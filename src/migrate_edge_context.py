#!/usr/bin/env python3
"""
migrate_edge_context.py — give every edge its context, as columns rather than prose.

    python src/migrate_edge_context.py --apply

Why
---
`SETDB1 —SILENCES→ HERVE-int` read on its own is a universal claim about a gene and a
transposable element. It is not what was measured. What was measured was one cell line,
one perturbation modality, one assay, one time point, one TE resolution, one quantifier.
Those facts were previously buried inside free-text `source` and `method` strings, which
means a downstream consumer could lift the edge and drop the qualifiers without noticing.

This adds them as first-class columns so an edge cannot be reused without them:

    context_cell_type      K562 | not_applicable
    context_species        Homo sapiens
    perturbation_modality  CRISPRi | CRISPR | shRNA | siRNA | NA
    assay                  RNA-seq | curation | text-mining | inference
    timepoint              as reported, else NA
    te_resolution          subfamily | family | class | locus | global | NA
    quantifier             TEcount (TEtranscripts) --mode multi | NA
    reference_scope        chr1+chr19 | chr1+chr19+panel | genome | NA

Values are derived from what each layer actually is; nothing is invented. Where a layer
genuinely has no cell type (a GO annotation is not measured in a cell line) the field is
`not_applicable`, which is information, not a gap to be filled. The literal token matters:
"NA" round-trips through pandas as NaN, which silently converts "we know this does not
apply" into "we did not record this".
"""
from __future__ import annotations
import argparse, glob, sys
from pathlib import Path
import pandas as pd

CONTEXT_COLS = ["context_cell_type", "context_species", "perturbation_modality", "assay",
                "timepoint", "te_resolution", "quantifier", "reference_scope"]

# what each evidence layer is, as a matter of fact about how it was produced
LAYER_DEFAULTS = {
    "measured":   dict(context_cell_type="K562", context_species="Homo sapiens",
                       perturbation_modality="", assay="RNA-seq (polyA, paired-end)",
                       timepoint="not_reported (ENCODE does not report a harvest time for these)",
                       te_resolution="subfamily",
                       quantifier="TEcount (TEtranscripts) --mode multi",
                       reference_scope="chr1+chr19"),
    "curated":    dict(context_cell_type="not_applicable", context_species="Homo sapiens",
                       perturbation_modality="not_applicable", assay="curation",
                       timepoint="not_applicable", te_resolution="not_applicable", quantifier="not_applicable",
                       reference_scope="not_applicable"),
    "mechanism":  dict(context_cell_type="not_applicable", context_species="Homo sapiens",
                       perturbation_modality="not_applicable", assay="curation (biochemical)",
                       timepoint="not_applicable", te_resolution="not_applicable", quantifier="not_applicable",
                       reference_scope="not_applicable"),
    "literature": dict(context_cell_type="as reported in abstract (not parsed)",
                       context_species="as reported in abstract (not parsed)",
                       perturbation_modality="as reported in abstract (not parsed)",
                       assay="text-mining", timepoint="not_applicable",
                       te_resolution="coarse TE term", quantifier="not_applicable",
                       reference_scope="not_applicable"),
    "inferred":   dict(context_cell_type="inherited from premises",
                       context_species="Homo sapiens", perturbation_modality="not_applicable",
                       assay="inference", timepoint="not_applicable",
                       te_resolution="inherited from premises", quantifier="not_applicable",
                       reference_scope="not_applicable"),
}

# the three contrasts in this build, by knockdown gene
MODALITY = {"SETDB1": "CRISPRi", "TRIM28": "CRISPRi", "DNMT1": "CRISPR"}


def infer_modality(row) -> str:
    subj = str(row.get("subject", ""))
    if subj in MODALITY:
        return MODALITY[subj]
    src = str(row.get("source", ""))
    for k, v in MODALITY.items():
        if k in src:
            return v
    return "not_applicable"


def migrate(path: Path, apply: bool) -> dict:
    df = pd.read_csv(path)
    if "evidence_tier" not in df.columns:
        return {"file": path.name, "skipped": "no evidence_tier column"}
    before = list(df.columns)
    for c in CONTEXT_COLS:
        if c not in df.columns:
            df[c] = ""
    for i, row in df.iterrows():
        d = LAYER_DEFAULTS.get(str(row["evidence_tier"]), LAYER_DEFAULTS["curated"]).copy()
        if str(row["evidence_tier"]) == "measured":
            d["perturbation_modality"] = infer_modality(row)
            # the inflammation layer was measured on the panel-augmented reference and is
            # a gene-signature readout, not a TE readout
            if str(row.get("object", "")).startswith("Signature:"):
                d["te_resolution"] = "not_applicable (gene signature)"
                d["quantifier"] = "not_applicable (gene-level counts)"
                d["reference_scope"] = "chr1+chr19+panel"
        for c in CONTEXT_COLS:
            if not str(df.at[i, c]).strip() or str(df.at[i, c]) == "nan":
                df.at[i, c] = d[c]
    if apply:
        df.to_csv(path, index=False)
    return {"file": path.name, "rows": len(df),
            "added": [c for c in CONTEXT_COLS if c not in before]}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dirs", nargs="*", default=["data/graph", "results"])
    ap.add_argument("--apply", action="store_true", help="write files (default is dry run)")
    a = ap.parse_args()
    files = [Path(p) for d in a.dirs for p in sorted(glob.glob(f"{d}/edges_*.csv"))]
    if not files:
        sys.exit("no edges_*.csv found")
    for f in files:
        print(migrate(f, a.apply))
    print("DRY RUN — pass --apply to write" if not a.apply else "written")


if __name__ == "__main__":
    main()
