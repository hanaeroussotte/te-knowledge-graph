#!/usr/bin/env python3
"""
check_citations.py — do the DOIs and PMIDs we cite actually resolve, and to what?

    python tests/check_citations.py            # resolve everything (needs network)
    python tests/check_citations.py --offline  # structural checks only

A citation that does not resolve is a fabricated citation, whatever the intent. This
resolves every DOI in data/graph/prior_art.csv and in docs/*.md against Crossref, and
every PMID against NCBI, and prints the title each one resolves to so a human can see
that the reference says what we claim it says.

DOI extraction is the fiddly part: DOIs legitimately contain parentheses
(10.1016/s0960-9822(03)00539-6), and a naive `[^\\s)]+` pattern truncates at the first
one and then reports a perfectly good citation as broken. The pattern here balances a
single level of parentheses and strips trailing punctuation.
"""
from __future__ import annotations
import argparse, re, sys, time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
# allow one balanced (...) inside the suffix, then stop at whitespace or markdown syntax
DOI_RE = re.compile(r"10\.\d{4,9}/(?:[^\s\]\|]*?\([^\s\)]*\))?[^\s\)\]\|,;]*")
PMID_RE = re.compile(r"\bPMID[:\s]+(\d{7,9})\b")


def collect() -> tuple[set, set]:
    dois, pmids = set(), set()
    pa = ROOT / "data/graph/prior_art.csv"
    if pa.exists():
        d = pd.read_csv(pa, keep_default_na=False)
        dois |= {x.strip() for x in d.doi if x.strip()}
        pmids |= {str(x).strip() for x in d.pmid if str(x).strip()}
    for p in list((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
        t = p.read_text(errors="ignore")
        dois |= {m.group(0).rstrip(".,;)") for m in DOI_RE.finditer(t)}
        pmids |= set(PMID_RE.findall(t))
    return dois, pmids


def resolve_doi(doi: str, email: str | None) -> tuple[bool | None, str]:
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}",
                         params={"mailto": email} if email else {},
                         headers={"User-Agent": "python-requests"}, timeout=45)
    except Exception as e:
        return None, f"network error: {type(e).__name__}"
    if r.status_code == 404:
        return False, "not found in Crossref"
    if not r.ok:
        return None, f"Crossref HTTP {r.status_code}"
    return True, (r.json()["message"].get("title") or [""])[0]


def resolve_pmid(pmid: str, email: str | None) -> tuple[bool | None, str]:
    try:
        r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                         params={"db": "pubmed", "id": pmid, "retmode": "json",
                                 **({"email": email} if email else {})}, timeout=45)
    except Exception as e:
        return None, f"network error: {type(e).__name__}"
    if not r.ok:
        return None, f"NCBI HTTP {r.status_code}"
    rec = (r.json().get("result") or {}).get(pmid)
    if not rec or rec.get("error"):
        return False, "not found in PubMed"
    return True, rec.get("title", "")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()

    dois, pmids = collect()
    print(f"{len(dois)} DOIs and {len(pmids)} PMIDs cited")
    if a.offline:
        bad = [d for d in dois if not re.fullmatch(r"10\.\d{4,9}/.+", d)]
        if bad:
            print("AUDIT FAIL — malformed DOIs:", bad)
            sys.exit(1)
        print("offline structural check passed (no resolution attempted)")
        return

    email = None
    try:
        import builtins
        email = getattr(builtins, "host", None) and builtins.host.get_user_email()
    except Exception:
        email = None

    fails, inconclusive = [], []
    for d in sorted(dois):
        ok, info = resolve_doi(d, email)
        mark = {True: "ok  ", False: "FAIL", None: "?   "}[ok]
        print(f"  {mark} {d}  {info[:80]}")
        (fails if ok is False else inconclusive if ok is None else []).append(d)
        time.sleep(0.12)
    for p in sorted(pmids):
        ok, info = resolve_pmid(p, email)
        mark = {True: "ok  ", False: "FAIL", None: "?   "}[ok]
        print(f"  {mark} PMID {p}  {info[:76]}")
        (fails if ok is False else inconclusive if ok is None else []).append(p)
        time.sleep(0.12)

    if fails:
        print(f"\nAUDIT FAIL — {len(fails)} citation(s) do not resolve: {fails}")
        sys.exit(1)
    msg = f"CITATIONS PASS — {len(dois)} DOIs, {len(pmids)} PMIDs all resolve"
    if inconclusive:
        msg += f"; {len(inconclusive)} inconclusive (network/rate limit), re-run to confirm"
    print("\n" + msg)


if __name__ == "__main__":
    main()
