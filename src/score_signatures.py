#!/usr/bin/env python3
"""
score_signatures.py — does TE derepression come with an interferon / inflammation response?

    python src/score_signatures.py --counts results/counts_matrix.tsv \
        --de results/deseq2_results.csv --gtf refs/gencode.v44.gtf --outdir results

Two outputs:
    signature_setlevel_tests.csv   per contrast, is the signature's log2FC distribution
                                   shifted against all other genes? (contrast-internal)
    signature_coverage.csv         how much of each gene set the reference scope can even see

READ THE COVERAGE TABLE FIRST. On a chr1+chr19 reference only ~17% of the type-I interferon
set is present, and CGAS, STING1, IFIH1, MAVS, TBK1, STAT1/2, MX1, OAS1 and IFIT1 are all
absent. Any "no interferon response" conclusion from that scope is a statement about which
chromosomes were indexed, not about biology. The script therefore refuses to interpret a
signature below --min-coverage and says so.

Also: score contrasts internally, never by correlating scores across all samples. Different
perturbation series carry large batch offsets in ISG expression that will dominate any
cross-sample correlation.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from scipy import stats

S = requests.Session(); S.headers.update({"Accept": "application/json"})
QG = "https://www.ebi.ac.uk/QuickGO/services/annotation/search"
SETS = {"IFN_typeI": "GO:0034340", "IFN_typeII": "GO:0034341",
        "defense_virus": "GO:0051607", "inflammatory": "GO:0006954",
        "senescence": "GO:0090398", "NFkB": "GO:0038061"}


def quickgo_symbols(go_id, max_pages=25):
    syms, page = set(), 1
    while page <= max_pages:
        r = S.get(QG, params={"goId": go_id, "goUsage": "descendants",
                              "goUsageRelationships": "is_a,part_of,regulates",
                              "taxonId": 9606, "limit": 200, "page": page,
                              "geneProductType": "protein"}, timeout=90)
        if not r.ok:
            break
        j = r.json()
        syms.update(a["symbol"] for a in j.get("results", []) if a.get("symbol"))
        if page >= (j.get("pageInfo") or {}).get("total", 1):
            break
        page += 1
    return syms


def parse_gtf(gtf):
    """gene_id -> symbol, plus the protein-coding symbol whitelist and chromosome map.
    NOTE the GENCODE attribute order is gene_id, gene_type, gene_name — a regex that
    assumes id/name/type silently matches nothing."""
    attr = re.compile(r'(\S+) "([^"]*)"')
    sym, valid, chrom = {}, set(), {}
    with open(gtf) as fh:
        for line in fh:
            if line.startswith("#") or "\tgene\t" not in line:
                continue
            f = line.split("\t")
            d = dict(attr.findall(f[8]))
            gid, name, typ = d.get("gene_id"), d.get("gene_name"), d.get("gene_type")
            if gid and name:
                sym[gid] = name
                chrom.setdefault(name, f[0])
                if typ == "protein_coding":
                    valid.add(name)
    return sym, valid, chrom


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--counts", default="results/counts_matrix.tsv")
    ap.add_argument("--de", default="results/deseq2_results.csv")
    ap.add_argument("--gtf", default="refs/gencode.v44.gtf")
    ap.add_argument("--outdir", default="results")
    ap.add_argument("--scope-chroms", nargs="*", default=None,
                    help="chromosomes the reference actually contained; omit for whole genome")
    ap.add_argument("--min-coverage", type=float, default=0.6)
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)

    sym, valid, chrom = parse_gtf(a.gtf)
    de = pd.read_csv(a.de, index_col=0)
    de["symbol"] = [sym.get(i, i) for i in de.index]
    de["is_TE"] = [str(i).count(":") == 2 for i in de.index]

    sets = {k: sorted(quickgo_symbols(go) & valid) for k, go in SETS.items()}

    cov_rows, usable = [], {}
    for k, members in sets.items():
        if a.scope_chroms:
            inscope = [g for g in members if chrom.get(g) in set(a.scope_chroms)]
        else:
            inscope = members
        frac = len(inscope) / max(len(members), 1)
        cov_rows.append({"signature": k, "go": SETS[k], "genes_in_set": len(members),
                         "in_reference_scope": len(inscope), "coverage": round(frac, 3),
                         "interpretable": frac >= a.min_coverage})
        if frac >= a.min_coverage:
            usable[k] = members
    cov = pd.DataFrame(cov_rows)
    cov.to_csv(out / "signature_coverage.csv", index=False)
    print(cov.to_string(index=False))

    if not usable:
        print(f"\nNo signature reaches --min-coverage {a.min_coverage:.0%} in this reference "
              f"scope. Refusing to report set-level tests: any result would describe the "
              f"chromosome selection, not the biology. Re-run with a whole-genome reference.",
              file=sys.stderr)
        return

    rows = []
    for kd in sorted(de.knockdown.dropna().unique()):
        d = de[de.knockdown == kd].dropna(subset=["log2FoldChange"])
        genes = d[~d.is_TE]
        for name, members in usable.items():
            inset = genes[genes.symbol.isin(members)].log2FoldChange
            rest = genes[~genes.symbol.isin(members)].log2FoldChange
            if len(inset) < 10:
                continue
            mw = stats.mannwhitneyu(inset, rest, alternative="two-sided")
            rows.append({"knockdown": kd, "signature": name, "n_in_set": len(inset),
                         "median_set": round(float(inset.median()), 4),
                         "median_rest": round(float(rest.median()), 4),
                         "delta": round(float(inset.median() - rest.median()), 4),
                         "mannwhitney_p": float(f"{mw.pvalue:.4g}")})
        te = d[d.is_TE].log2FoldChange
        if len(te) >= 10:
            mw = stats.mannwhitneyu(te, genes.log2FoldChange, alternative="two-sided")
            rows.append({"knockdown": kd, "signature": "TE_compartment", "n_in_set": len(te),
                         "median_set": round(float(te.median()), 4),
                         "median_rest": round(float(genes.log2FoldChange.median()), 4),
                         "delta": round(float(te.median() - genes.log2FoldChange.median()), 4),
                         "mannwhitney_p": float(f"{mw.pvalue:.4g}")})
    res = pd.DataFrame(rows)
    res.to_csv(out / "signature_setlevel_tests.csv", index=False)
    print("\n" + res.to_string(index=False))


if __name__ == "__main__":
    main()
