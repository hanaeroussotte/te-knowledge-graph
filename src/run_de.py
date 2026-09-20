#!/usr/bin/env python3
"""
run_de.py — differential expression on the gene+TE matrix, and conversion to graph edges.

    python src/run_de.py --counts results/counts_matrix.tsv \
        --manifest data/manifests/manifest_core.csv --outdir results

Emits:
    deseq2_results.csv        per-feature log2FC / p / padj for every contrast
    edges_measured.csv        graph edges, per-feature AND set-level
    setlevel_tests.csv        the TE-set vs gene-set comparison per contrast

Two statistics are computed, and you want both.

  Per-feature FDR  — which individual TE subfamilies moved. Conservative; at shallow depth
                     it can return nothing at all.
  Set-level shift  — did the TE compartment move relative to the protein-coding compartment,
                     tested with Mann-Whitney on the two log2FC distributions from the SAME
                     contrast. Size-factor normalisation scales genes and TEs together, so it
                     cannot manufacture a difference between the two sets: the test is
                     normalisation-invariant. It also needs no replicates.

In the reference run this mattered: DNMT1 knockdown had ZERO subfamilies at FDR < 0.1 and a
set-level shift at p = 1.4e-07. Reading only the padj column would have called it a null.
"""
from __future__ import annotations
import argparse, datetime, hashlib, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

TODAY = datetime.date.today().isoformat()
COLS = ["edge_id", "subject", "subject_type", "predicate", "object", "object_type",
        "evidence_tier", "source", "source_detail", "native_score", "native_score_type",
        "statistic", "retrieved"]


def _patch_sysconf():
    """pydeseq2 hard-codes inner_max_num_threads=1, which only joblib's loky backend
    accepts, and loky aborts in restricted sandboxes on os.sysconf('SC_SEM_NSEMS_MAX').
    Shim that one key rather than switching backend (the other backends reject the arg)."""
    real = os.sysconf
    def sysconf(name):
        if name in ("SC_SEM_NSEMS_MAX", 274):
            return 256
        return real(name)
    try:
        real("SC_SEM_NSEMS_MAX")
    except (ValueError, OSError):
        os.sysconf = sysconf


def is_te(index) -> np.ndarray:
    """TEcount writes TE features as subfamily:family:class; genes keep their IDs."""
    return np.array([str(i).count(":") == 2 for i in index])


def classify(index) -> np.ndarray:
    """Three feature classes, and the distinction matters for two separate reasons.

    TE              subfamily:family:class, from the RepeatMasker GTF.
    gene            an ENSG id, i.e. a gene on a chromosome that is fully in the reference.
    panel_gene      a symbol id, from a spliced-in signature contig (build_panel_reference.py).

    Panel genes are an immune-biased, deliberately chosen subset. They must never enter the
    protein-coding background of the set-level TE test — that test works because size
    factors scale both sets together, which only means something if the background is an
    unselected sample of the transcriptome. They are also excluded from size-factor
    estimation, so normalisation stays identical to a run without a panel.
    """
    out = []
    for i in index:
        s = str(i)
        out.append("TE" if s.count(":") == 2 else "gene" if s.startswith("ENSG") else "panel_gene")
    return np.array(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--counts", default="results/counts_matrix.tsv")
    ap.add_argument("--manifest", default="data/manifests/manifest_core.csv")
    ap.add_argument("--outdir", default="results")
    ap.add_argument("--fdr", type=float, default=0.1)
    ap.add_argument("--min-count", type=int, default=10)
    ap.add_argument("--setlevel-alpha", type=float, default=1e-3)
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)

    _patch_sysconf()
    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats
    from pydeseq2.default_inference import DefaultInference
    inf = DefaultInference(n_cpus=2, joblib_verbosity=0)

    m = pd.read_csv(a.counts, sep="\t", index_col=0)
    m.index = [str(i).strip('"') for i in m.index]
    # `merge` writes a trailing feature_type annotation column; counts only from here on
    m = m.drop(columns=[c for c in m.columns if m[c].dtype == object], errors="ignore")
    m = m.round().astype(int)
    man = pd.read_csv(a.manifest)

    meta = man.drop_duplicates("sample").set_index("sample")
    meta = meta.loc[[s for s in m.columns if s in meta.index]]
    meta["target"] = meta.get("target_gene", pd.Series(index=meta.index)).fillna("NA")
    meta["target"] = [t.replace("-", "_") for t in meta["target"]]

    controls = sorted(meta[meta.condition == "control"].target.unique())
    kds = sorted(meta[meta.condition == "kd"].target.unique())
    if not kds or not controls:
        sys.exit("manifest needs at least one `kd` and one `control` row")
    # pair each knockdown with the control sharing its experiment batch where possible
    pairs = []
    for kd in kds:
        batch = meta[meta.target == kd].get("assay", pd.Series(["NA"])).iloc[0]
        cand = [c for c in controls
                if str(meta[meta.target == c].get("assay", pd.Series(["NA"])).iloc[0]) == str(batch)]
        pairs.append((kd, cand[0] if cand else controls[0]))
    print("contrasts:", pairs, file=sys.stderr)

    teflag = is_te(m.index)
    all_res, edges, setrows = [], [], []
    for kd, ctrl in pairs:
        sub = meta[meta.target.isin([kd, ctrl])]
        c = m.T.loc[sub.index]
        c = c.loc[:, (c.sum(0) >= a.min_count) & ((c > 0).sum(0) >= 2)]
        cls = classify(c.columns)
        bg = list(c.columns[cls == "gene"])
        dds = DeseqDataSet(counts=c, metadata=sub[["target"]], design="~target",
                           control_genes=bg, inference=inf, quiet=True)
        dds.deseq2()
        st = DeseqStats(dds, contrast=["target", kd, ctrl], inference=inf, quiet=True)
        st.summary()
        r = st.results_df.copy()
        r["feature"] = r.index
        r["is_TE"] = is_te(r.index)
        r["feature_class"] = classify(r.index)
        r["knockdown"], r["control"] = kd, ctrl
        all_res.append(r)

        # ---- per-feature edges
        sig = r[r.is_TE].dropna(subset=["padj"])
        sig = sig[sig.padj < a.fdr]
        for row in sig.itertuples():
            parts = str(row.Index).split(":")
            pred = "SILENCES" if row.log2FoldChange > 0 else "DEREPRESSES"
            for obj, otype in [(parts[0], "TEFamily"), (f"{parts[2]}/{parts[1]}", "TEClass")]:
                edges.append(dict(zip(COLS, [
                    "e" + hashlib.sha1(f"{kd}|{pred}|{obj}|measured".encode()).hexdigest()[:14],
                    kd, "Gene", pred, obj, otype, "measured", f"{kd} vs {ctrl} (this run)",
                    "per-feature DESeq2", round(float(row.log2FoldChange), 4),
                    "DESeq2 log2 fold change (knockdown vs control)",
                    f"padj={row.padj:.4g}", TODAY])))

        # ---- set-level edge
        t = r[r.feature_class == "TE"].log2FoldChange.dropna()
        g = r[r.feature_class == "gene"].log2FoldChange.dropna()
        mw = stats.mannwhitneyu(t, g, alternative="two-sided")
        delta = float(t.median() - g.median())
        setrows.append({"knockdown": kd, "control": ctrl, "n_TE": len(t), "n_gene": len(g),
                        "median_log2FC_TE": round(float(t.median()), 4),
                        "median_log2FC_gene": round(float(g.median()), 4),
                        "delta": round(delta, 4), "mannwhitney_p": float(f"{mw.pvalue:.4g}")})
        if mw.pvalue < a.setlevel_alpha:
            pred = "SILENCES" if delta > 0 else "DEREPRESSES"
            edges.append(dict(zip(COLS, [
                "e" + hashlib.sha1(f"{kd}|{pred}|TE:global|measured".encode()).hexdigest()[:14],
                kd, "Gene", pred, "TE:global", "TEClass", "measured",
                f"{kd} vs {ctrl} (this run, set-level)",
                f"median log2FC of {len(t)} TE features minus {len(g)} protein-coding genes; "
                f"normalisation-invariant", round(delta, 4),
                "median log2FC difference, TE set vs protein-coding set",
                f"Mann-Whitney p={mw.pvalue:.4g}", TODAY])))

    de = pd.concat(all_res)
    de.to_csv(out / "deseq2_results.csv")
    ed = pd.DataFrame(edges, columns=COLS).drop_duplicates("edge_id")
    ed.to_csv(out / "edges_measured.csv", index=False)
    sl = pd.DataFrame(setrows)
    sl.to_csv(out / "setlevel_tests.csv", index=False)

    print("\nset-level TE shift (the artefact-resistant test):")
    print(sl.to_string(index=False))
    print(f"\nmeasured edges written: {len(ed)} -> {out / 'edges_measured.csv'}")
    if ed.empty:
        print("NOTE: no edges passed. Check depth, replication, and that TE rows carry counts.")


if __name__ == "__main__":
    main()
