#!/usr/bin/env python3
"""
build_te_annotation.py — turn the UCSC RepeatMasker table into the project's TE vocabulary.

Produces the TE GTF that TEcount quantifies against, and the subfamily table that becomes the
TEFamily / TEClass nodes in the knowledge graph.

    python src/build_te_annotation.py --rmsk refs/rmsk.hg38.txt.gz --outdir refs \
        --subset chr1 chr19

Decisions encoded here, and why:
  * keep LINE / SINE / LTR / DNA / Retroposon / RC — these are transposable elements.
    Simple_repeat, Low_complexity, Satellite and the small-RNA classes are repeats but not
    TEs, and including them would dilute every set-level statistic downstream.
  * drop loci shorter than 100 bp. A 40 bp fragment cannot be assigned a 100 bp read, so it
    contributes noise to the EM step and nothing else.
  * main chromosomes only (chr1-22, X, Y). Alt contigs and patches duplicate sequence and
    would double-count reads.
  * gene_id = subfamily. TEcount aggregates on gene_id, so this single choice sets the
    resolution of the entire analysis to subfamily level.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

RMSK_COLS = ["bin", "swScore", "milliDiv", "milliDel", "milliIns", "chrom", "start", "end",
             "genoLeft", "strand", "repName", "repClass", "repFamily", "repStart", "repEnd",
             "repLeft", "id"]
TE_CLASSES = {"LINE", "SINE", "LTR", "DNA", "Retroposon", "RC"}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rmsk", default="refs/rmsk.hg38.txt.gz")
    p.add_argument("--outdir", default="refs")
    p.add_argument("--prefix", default="hg38_rmsk_TE")
    p.add_argument("--min-length", type=int, default=100)
    p.add_argument("--subset", nargs="*", default=["chr1", "chr19"],
                   help="also emit a GTF restricted to these chromosomes (for local testing)")
    a = p.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)

    rm = pd.read_csv(a.rmsk, sep="\t", header=None, names=RMSK_COLS,
                     usecols=["swScore", "milliDiv", "chrom", "start", "end", "strand",
                              "repName", "repClass", "repFamily"])
    te = rm[rm.repClass.isin(TE_CLASSES) & rm.chrom.str.match(r"^chr([0-9]+|X|Y)$")].copy()
    te["length"] = te.end - te.start
    te = te[te.length >= a.min_length]

    g = te.sort_values(["chrom", "start"]).reset_index(drop=True)
    g["dup"] = g.groupby("repName").cumcount() + 1
    attrs = ('gene_id "' + g.repName + '"; transcript_id "' + g.repName + "_dup"
             + g.dup.astype(str) + '"; family_id "' + g.repFamily
             + '"; class_id "' + g.repClass + '";')
    gtf = pd.DataFrame({"seqname": g.chrom, "source": "rmsk", "feature": "exon",
                        "start": g.start + 1, "end": g.end, "score": ".",
                        "strand": g.strand.replace({"C": "-"}), "frame": ".", "attribute": attrs})
    gtf.to_csv(out / f"{a.prefix}.gtf", sep="\t", header=False, index=False, quoting=3)
    sub = None
    if a.subset:
        sub = gtf[gtf.seqname.isin(a.subset)]
        sub.to_csv(out / f"{a.prefix}.{'_'.join(a.subset)}.gtf", sep="\t",
                   header=False, index=False, quoting=3)

    fam = (te.groupby(["repClass", "repFamily", "repName"])
             .agg(n_loci=("length", "size"), total_bp=("length", "sum"),
                  median_bp=("length", "median"), median_milliDiv=("milliDiv", "median"))
             .reset_index().sort_values("total_bp", ascending=False))
    fam.to_csv(out / "te_subfamilies.csv", index=False)

    print(f"rmsk rows read   : {len(rm):,}")
    print(f"TE loci retained : {len(te):,}")
    print(f"subfamilies      : {fam.repName.nunique():,}")
    print(f"wrote            : {out / (a.prefix + '.gtf')}")
    if sub is not None:
        print(f"wrote subset     : {len(sub):,} lines for {', '.join(a.subset)}")


if __name__ == "__main__":
    main()
