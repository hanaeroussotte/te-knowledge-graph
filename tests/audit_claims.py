#!/usr/bin/env python3
"""
audit_claims.py — refuse to ship a retracted claim.

    python tests/audit_claims.py

Checks, against every .md, .html and src/*.py in the repo:

    1. no retracted novelty claim appears as an assertion (see docs/CLAIMS.md section D)
    2. no cross-reference to a document that does not exist
    3. every DOI in data/graph/prior_art.csv is cited in PRIOR_ART.md or CLAIMS.md
    4. CLAIMS.md still defines the whole status vocabulary

On (1) the audit distinguishes *asserting* a banned phrase from *prohibiting* it — the
documents that retract these claims necessarily contain them. A match preceded by a
negation, or appearing inside quotation marks, is a prohibition and is allowed. That
distinction is the interesting part of this script: a naive grep would force you to
whitelist the very files that do the retracting, which is how a banned claim eventually
creeps back in through one of them.
"""
from __future__ import annotations
import glob, re, sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

BANNED = {
    # The first version of this pattern required the literal words "public knowledge
    # graph", and the slide deck said "No major biology knowledge graph has a TE node
    # type" — the same retracted claim, straight past the audit. Match the CLAIM, not one
    # phrasing of it: a negation, any qualifier, "knowledge graph", and a has/contains verb.
    r"[Nn]o (public|major|existing|current)?\s*(biological|biomedical|biology)?\s*"
    r"knowledge graph\s+(can|has|have|contains?|includes?|models?|represents?)":
        "retracted D1 — say 'major general-purpose biomedical KGs do not model TEs as "
        "first-class entities'",
    r"(has|have) (a )?(no|zero) TE node type|no TE node type":
        "retracted D1 variant — 'does not model TEs as first-class entities'",
    r"[Nn]obody has systematically perturbed":
        "retracted D3 — genome-wide screens for TE regulators exist since 2003",
    r"causal deduction":
        "use 'mechanistic hypothesis' (see docs/EPISTEMOLOGY.md)",
    r"\bthe TE atlas\b":
        "do not position the project as THE atlas",
    r"we invented|our novel quantifier|our TE quantification method":
        "retracted D5 — quantification is TEtranscripts, credit it",
}
# documents whose job is to record the retractions
REGISTRY = {"docs/CLAIMS.md", "docs/PRIOR_ART.md"}
NEG = re.compile(r"(not|never|avoid|instead of|rather than|replaced|retract|banned|"
                 r"do not|don't|attackable|say it that way)\W*$", re.I)


def in_quoted_span(txt: str, start: int, end: int) -> bool:
    """Is the match inside a pair of double quotes on its own line?

    A 'never say X / say Y instead' table quotes the banned phrase by design, and the
    quoted phrase may sit mid-string — `| "This is the TE atlas" |` — so checking only the
    character immediately before the match misses it. Quoting a claim is not asserting it.
    """
    ls = txt.rfind("\n", 0, start) + 1
    le = txt.find("\n", end)
    line = txt[ls:le if le != -1 else len(txt)]
    a, b = start - ls, end - ls
    # count quote marks before the match on this line; odd = we are inside a quoted span
    return line[:a].count('"') % 2 == 1 and '"' in line[b:]


def is_prohibition(txt: str, start: int, end: int | None = None) -> bool:
    pre = txt[max(0, start - 120):start]
    if NEG.search(pre.strip()) or pre.rstrip().endswith(('"', "'", "as ", "— ")):
        return True
    return in_quoted_span(txt, start, end if end is not None else start)


def main():
    files = (glob.glob(str(ROOT / "**/*.md"), recursive=True)
             + glob.glob(str(ROOT / "**/*.html"), recursive=True)
             + glob.glob(str(ROOT / "src/*.py")))
    fails, warns = [], []

    # ---------------------------------------------------------------- retracted STATISTICS
    # Added 2026-09-22, immediately after it failed to catch one. The compartment
    # Mann-Whitney p-values were retracted (docs/COMPARTMENT_STATISTICS.md) because they
    # treat correlated TE features as independent; the deck still asserted two of them on
    # its final slide, and this audit passed, because BANNED only ever matched POSITIONING
    # language. A retracted number is as damaging as a retracted phrase and this script had
    # no concept of one.
    #
    # It also has to see through HTML entities. The deck wrote `1.6&times;10&minus;8`, so a
    # pattern looking for '×' or 'x' matched nothing at all — the encoding hid it from three
    # separate greps. Normalise entities before matching, never after.
    RETRACTED_STATS = {
        r"1\.6\s*(?:&times;|[x×*])\s*10\s*(?:&minus;|[-−])?\s*⁻?8":
            "retracted: DNMT1 compartment Mann-Whitney p. Use delta = +0.13, "
            "correlation-aware p = 0.045 (docs/COMPARTMENT_STATISTICS.md)",
        r"3\.5\s*(?:&times;|[x×*])\s*10\s*(?:&minus;|[-−])?\s*⁻?15":
            "retracted: TRIM28 compartment Mann-Whitney p. The compartment claim is "
            "effect-size only; quote the per-feature AluY result instead",
        r"1\.41?e-0?7|2\.3\d*e-?2?1":
            "retracted compartment Mann-Whitney p-value",
        r"p\s*=\s*(?:&minus;|-)?\s*0?\.0+1?6?\s*(?:&times;|[x×])\s*10\s*⁻?2[01]":
            "retracted compartment Mann-Whitney p-value",
    }

    def normalise(s: str) -> str:
        """Entities first, THEN tags. The deck wrote `1.6&times;10<sup>&minus;8</sup>`:
        unescaping alone leaves `1.6×10<sup>−8</sup>` and the markup still splits the
        number, so the first version of this check reported a clean pass on the very file
        it was written to catch."""
        import html
        return re.sub(r"<[^>]+>", "", html.unescape(s))

    for f in files:
        raw = Path(f).read_text(errors="ignore")
        rel = str(Path(f).relative_to(ROOT))
        if rel in REGISTRY or rel in {"docs/COMPARTMENT_STATISTICS.md"}:
            continue
        for pat, why in RETRACTED_STATS.items():
            for src in (raw, normalise(raw)):
                for m in re.finditer(pat, src):
                    if is_prohibition(src, m.start(), m.end()):
                        continue
                    fails.append(f"{rel} — {why}\n      …{m.group(0)!r}…")
                    break

    for f in files:
        txt = Path(f).read_text(errors="ignore")
        rel = str(Path(f).relative_to(ROOT))
        if rel in REGISTRY:
            continue
        for pat, why in BANNED.items():
            for m in re.finditer(pat, txt):
                if is_prohibition(txt, m.start(), m.end()):
                    continue
                line = txt[:m.start()].count("\n") + 1
                fails.append(f"{rel}:{line} — {why}\n      …{m.group(0)!r}…")

    for f in glob.glob(str(ROOT / "docs/*.md")) + [str(ROOT / "README.md")]:
        txt = Path(f).read_text(errors="ignore")
        for m in re.finditer(r"`(?:docs/)?([A-Z_]+\.md)`", txt):
            if not (ROOT / "docs" / m.group(1)).exists() and not (ROOT / m.group(1)).exists():
                fails.append(f"{Path(f).name}: dangling reference to {m.group(1)}")

    pa_path = ROOT / "data/graph/prior_art.csv"
    if pa_path.exists():
        pa = pd.read_csv(pa_path, keep_default_na=False)
        cited = (ROOT / "docs/PRIOR_ART.md").read_text() + (ROOT / "docs/CLAIMS.md").read_text()
        for d in sorted({x for x in pa.doi.unique() if x}):
            if d not in cited:
                warns.append(f"DOI in prior_art.csv not cited in docs: {d}")
    else:
        fails.append("data/graph/prior_art.csv is missing — the prior-art gate has no record")

    claims = (ROOT / "docs/CLAIMS.md").read_text()
    for tok in ["NOT_FOUND_IN_PRIOR_ART_SEARCH", "RETRACTED_BY_US", "SUPPORTED_BY_THIS_BUILD",
                "INFERRED", "HYPOTHESIS", "NOT_TESTED", "ESTABLISHED"]:
        if tok not in claims:
            fails.append(f"CLAIMS.md is missing status vocabulary: {tok}")

    # the registry must carry approved/prohibited wording, or it is a status list rather
    # than a source of truth for what can be said
    for tok in ["Say this", "Do **not** say", "Adversarial novelty rule",
                "weak evidence of absence"]:
        if tok not in claims:
            fails.append(f"CLAIMS.md is missing required section/rule: {tok!r}")

    # no blank context fields anywhere an edge claims a context
    ctx_cols = ["context_cell_type", "context_species", "perturbation_modality", "assay",
                "timepoint", "te_resolution", "quantifier", "reference_scope"]
    for f in (glob.glob(str(ROOT / "data/graph/edges_*.csv"))
              + glob.glob(str(ROOT / "results/edges_*.csv"))):
        d = pd.read_csv(f, keep_default_na=False)
        for c in ctx_cols:
            if c not in d.columns:
                fails.append(f"{Path(f).name}: missing context column {c}")
            elif (d[c].astype(str).str.strip() == "").any():
                n = int((d[c].astype(str).str.strip() == "").sum())
                fails.append(f"{Path(f).name}: {n} blank cells in {c} "
                             f"(use 'not_applicable', never blank and never 'NA')")

    # inferred edges must not be presented as universal without a flag
    derived = ROOT / "results/derived_edges.csv"
    if derived.exists():
        d = pd.read_csv(derived, keep_default_na=False)
        if "context_generalization_required" not in d.columns:
            fails.append("derived_edges.csv has no context_generalization_required column")
        else:
            grounded = d[(d.context_cell_type != "not_applicable")
                         & (d.context_generalization_required != "yes")]
            if len(grounded):
                fails.append(f"{len(grounded)} derived edges carry a specific cell type but "
                             f"are not flagged for context generalisation")

    # demo and deck must not assert anything absent from the registry's approved wording
    for name in ("docs/DEMO_SCRIPT.md", "demo/presentation.html"):
        p = ROOT / name
        if not p.exists():
            warns.append(f"{name} missing — cannot audit its claims")

    for w in warns:
        print("  ! ", w)
    if fails:
        print("AUDIT FAIL")
        for x in fails:
            print("  x ", x)
        sys.exit(1)
    print(f"AUDIT PASS — {len(files)} files checked, 0 retracted claims asserted, "
          f"0 dangling references, {len(warns)} warning(s)")


if __name__ == "__main__":
    main()
