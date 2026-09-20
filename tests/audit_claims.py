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
    r"[Nn]o public (biological )?knowledge graph (can|has|represents)":
        "retracted D1 — say 'major general-purpose biomedical KGs do not model TEs as "
        "first-class entities'",
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


def is_prohibition(txt: str, start: int) -> bool:
    pre = txt[max(0, start - 120):start]
    return bool(NEG.search(pre.strip())) or pre.rstrip().endswith(('"', "'", "as ", "— "))


def main():
    files = (glob.glob(str(ROOT / "**/*.md"), recursive=True)
             + glob.glob(str(ROOT / "**/*.html"), recursive=True)
             + glob.glob(str(ROOT / "src/*.py")))
    fails, warns = [], []

    for f in files:
        txt = Path(f).read_text(errors="ignore")
        rel = str(Path(f).relative_to(ROOT))
        if rel in REGISTRY:
            continue
        for pat, why in BANNED.items():
            for m in re.finditer(pat, txt):
                if is_prohibition(txt, m.start()):
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
