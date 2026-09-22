#!/usr/bin/env python3
"""
compartment_robustness.py — stress-test the TE-compartment result four ways.

    python src/compartment_robustness.py --counts results/counts_matrix.tsv \
        --manifest data/manifests/manifest_core.csv --out results/compartment_robustness.csv

WHY THIS EXISTS
---------------
The project's primary TE readout is

    delta_TE = median(log2FC over TE subfamilies) - median(log2FC over protein-coding genes)

computed within one contrast, with a Mann-Whitney p-value. The effect size is defensible:
size factors are per-sample multiplicative, so a normalisation error shifts both sets by the
same additive amount on the log scale and cancels in the difference.

**The p-value is not defensible as stated**, and an external reviewer was right to attack it.
Mann-Whitney treats the ~350 TE features as independent observations. They are not: TE
subfamilies covary through shared regulatory machinery, shared sequence ancestry, and shared
mapping ambiguity. Competitive gene-set tests are ANTI-CONSERVATIVE under exactly this
condition, which is why CAMERA (Wu & Smyth 2012, 10.1093/nar/gks461) exists at all. A
p-value of 1.6e-08 computed this way overstates the evidence by an unknown factor, and the
job of this script is to find out roughly how large that factor is.

Nothing here is a fix for the p-value. The point is to replace one number with several, so
the reader can see which parts of the claim survive which challenge:

  A  leave-one-library-out    does the effect depend on a single library?
  B  sample-label permutation the only test whose unit of inference is the SAMPLE
  C  correlation-aware        how many independent features do we actually have?
  D  feature-set sensitivity  does direction survive alternative definitions of "the TE set"?

A result that fails these is a result that should be retracted, and that outcome is
explicitly allowed: the script reports what it finds.
"""
from __future__ import annotations
import argparse, itertools, json, os, sys
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_de import _patch_sysconf, is_te, classify          # identical conventions


def fit_delta(counts: pd.DataFrame, meta: pd.DataFrame, kd: str, ctrl: str,
              min_count: int = 10):
    """One DESeq2 fit -> (delta, medians, per-feature log2FC, normalised counts).

    Size factors from protein-coding genes only, exactly as run_de.py does, so every number
    here is comparable to the headline result rather than approximately comparable.
    """
    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats
    from pydeseq2.default_inference import DefaultInference
    inf = DefaultInference(n_cpus=2)
    c = counts.T.loc[meta.index]
    c = c.loc[:, (c.sum(0) >= min_count) & ((c > 0).sum(0) >= 2)]
    bg = list(c.columns[classify(c.columns) == "gene"])
    dds = DeseqDataSet(counts=c, metadata=meta[["target"]], design="~target",
                       control_genes=bg, inference=inf, quiet=True)
    dds.deseq2()
    st = DeseqStats(dds, contrast=["target", kd, ctrl], inference=inf, quiet=True)
    st.summary()
    r = st.results_df.dropna(subset=["log2FoldChange"])
    cls = classify(r.index)
    te, gene = r.log2FoldChange[cls == "TE"], r.log2FoldChange[cls == "gene"]
    norm = pd.DataFrame(dds.layers["normed_counts"], index=c.index, columns=c.columns)
    return dict(delta=float(te.median() - gene.median()),
                med_te=float(te.median()), med_gene=float(gene.median()),
                n_te=int(len(te)), n_gene=int(len(gene)),
                frac_te_up=float((te > 0).mean()),
                mw_p=float(stats.mannwhitneyu(te, gene, alternative="two-sided").pvalue),
                te_lfc=te, gene_lfc=gene, norm=norm)


def rho_bar(norm: pd.DataFrame, meta: pd.DataFrame, features: list[str]) -> tuple[float, int]:
    """Mean pairwise correlation among a feature set, CAMERA's estimator.

    Residuals from the group means (the design has one factor), then the identity
        sum(offdiag of ZZ') = ||Z'1||^2 - m
    for a row-standardised residual matrix Z, which avoids forming the m x m matrix.

    The residual dimension here is tiny (n_samples - 2), so this estimate is NOISY. That is
    a real limitation and not a reason to skip it: even a small positive rho collapses the
    effective number of independent features, and the direction of the bias is known.
    """
    x = np.log2(norm[features].T + 1)                       # features x samples
    g = meta["target"].values
    for lvl in np.unique(g):                                # remove group means
        cols = g == lvl
        x.loc[:, cols] = x.loc[:, cols].sub(x.loc[:, cols].mean(axis=1), axis=0)
    d = x.shape[1] - len(np.unique(g))                      # residual dimension
    z = x.values
    z = z - z.mean(axis=1, keepdims=True)
    nrm = np.linalg.norm(z, axis=1, keepdims=True)
    keep = (nrm > 0).ravel()
    z = z[keep] / nrm[keep]
    m = z.shape[0]
    if m < 2:
        return float("nan"), d
    s = float(np.linalg.norm(z.sum(axis=0)) ** 2)
    return (s - m) / (m * (m - 1)), d


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--counts", default="results/counts_matrix.tsv")
    ap.add_argument("--manifest", default="data/manifests/manifest_core.csv")
    ap.add_argument("--out", default="results/compartment_robustness.csv")
    ap.add_argument("--min-count", type=int, default=10)
    a = ap.parse_args()
    _patch_sysconf()

    m = pd.read_csv(a.counts, sep="\t", index_col=0)
    m.index = [str(i).strip('"') for i in m.index]
    m = m.drop(columns=[c for c in m.columns if m[c].dtype == object], errors="ignore")
    m = m.round().astype(int)
    man = pd.read_csv(a.manifest)
    meta = man.drop_duplicates("sample").set_index("sample")
    meta = meta.loc[[s for s in m.columns if s in meta.index]]
    meta["target"] = [str(t).replace("-", "_") for t in meta["target_gene"]]

    controls = sorted(meta[meta.condition == "control"].target.unique())
    kds = sorted(meta[meta.condition == "kd"].target.unique())
    pairs = []
    for kd in kds:
        batch = str(meta[meta.target == kd]["assay"].iloc[0])
        cand = [c for c in controls if str(meta[meta.target == c]["assay"].iloc[0]) == batch]
        pairs.append((kd, cand[0] if cand else controls[0]))

    rows = []
    for kd, ctrl in pairs:
        sub = meta[meta.target.isin([kd, ctrl])].copy()
        obs = fit_delta(m, sub, kd, ctrl, a.min_count)
        n_kd = int((sub.target == kd).sum()); n_ct = int((sub.target == ctrl).sum())
        print(f"\n=== {kd} vs {ctrl}  ({n_kd} kd / {n_ct} control) ===", file=sys.stderr)
        print(f"  observed delta {obs['delta']:+.4f}  mannwhitney p {obs['mw_p']:.3g}",
              file=sys.stderr)
        base = dict(knockdown=kd, control=ctrl, n_kd=n_kd, n_control=n_ct)
        rows.append({**base, "analysis": "observed", "variant": "all TE features",
                     "delta": round(obs["delta"], 4), "n_features": obs["n_te"],
                     "frac_TE_up": round(obs["frac_te_up"], 3),
                     "p_or_note": f"mannwhitney p={obs['mw_p']:.3g} (NOT correlation-aware)"})

        # ---- A. leave-one-library-out ------------------------------------------------
        loo = []
        for drop in sub.index:
            s2 = sub.drop(index=drop)
            if (s2.target == kd).sum() < 1 or (s2.target == ctrl).sum() < 1:
                continue
            try:
                d = fit_delta(m, s2, kd, ctrl, a.min_count)["delta"]
            except Exception as e:
                d = float("nan"); print(f"    LOO {drop}: {type(e).__name__}", file=sys.stderr)
            loo.append((drop, d))
            rows.append({**base, "analysis": "leave_one_library_out",
                         "variant": f"without {drop}", "delta": round(d, 4),
                         "n_features": obs["n_te"], "frac_TE_up": "",
                         "p_or_note": ""})
        vals = [d for _, d in loo if np.isfinite(d)]
        if vals:
            same = all(np.sign(v) == np.sign(obs["delta"]) for v in vals)
            rows.append({**base, "analysis": "leave_one_library_out", "variant": "SUMMARY",
                         "delta": f"{min(vals):+.4f}..{max(vals):+.4f}",
                         "n_features": len(vals), "frac_TE_up": "",
                         "p_or_note": f"sign preserved in all {len(vals)} drops: {same}; "
                                      f"max |shift| from observed "
                                      f"{max(abs(v - obs['delta']) for v in vals):.4f}"})
            print(f"  LOO delta range {min(vals):+.4f}..{max(vals):+.4f} "
                  f"(sign preserved: {same})", file=sys.stderr)

        # ---- B. sample-label permutation ---------------------------------------------
        # The only test whose unit of inference is the SAMPLE. Labels are permuted WITHIN
        # the contrast only: the two control arms differ sharply on ISG score, so permuting
        # across batches would be comparing non-exchangeable samples.
        names = list(sub.index)
        obs_kd = set(sub.index[sub.target == kd])
        parts = [set(c) for c in itertools.combinations(names, n_kd)]
        # a labelling and its complement give the same partition with delta negated; keep
        # one representative of each pair when the arms are the same size
        if n_kd == n_ct:
            seen, uniq = set(), []
            for p in parts:
                key = frozenset([frozenset(p), frozenset(set(names) - p)])
                if key not in seen:
                    seen.add(key); uniq.append(p)
            parts = uniq
        perm_deltas = []
        for p in parts:
            if p == obs_kd:
                continue
            s2 = sub.copy()
            s2["target"] = [kd if s in p else ctrl for s in s2.index]
            try:
                perm_deltas.append(fit_delta(m, s2, kd, ctrl, a.min_count)["delta"])
            except Exception:
                pass
        n_adm = len(perm_deltas) + 1
        if perm_deltas:
            more = sum(1 for d in perm_deltas if abs(d) >= abs(obs["delta"])) + 1
            p_perm = more / n_adm
            rows.append({**base, "analysis": "sample_label_permutation", "variant":
                         f"{n_adm} admissible labellings (incl. observed)",
                         "delta": f"null |delta| max {max(abs(d) for d in perm_deltas):.4f}",
                         "n_features": obs["n_te"], "frac_TE_up": "",
                         "p_or_note": f"p = {more}/{n_adm} = {p_perm:.3f}; "
                                      f"FLOOR on attainable p is 1/{n_adm} = "
                                      f"{1/n_adm:.3f} — this design cannot produce a "
                                      f"smaller value regardless of effect size"})
            print(f"  permutation p = {more}/{n_adm} = {p_perm:.3f} "
                  f"(floor {1/n_adm:.3f})", file=sys.stderr)

        # ---- C. correlation-aware ------------------------------------------------------
        te_feats = [f for f in obs["te_lfc"].index if f in obs["norm"].columns]
        rb, dof = rho_bar(obs["norm"], sub, te_feats)
        mset = len(te_feats)
        if np.isfinite(rb):
            vif = 1 + (mset - 1) * max(rb, 0.0)
            m_eff = mset / vif
            # two-sample t on the log2FCs with the set's variance inflated by VIF
            tl, gl = obs["te_lfc"], obs["gene_lfc"]
            sp = np.sqrt(((len(tl) - 1) * tl.var(ddof=1) +
                          (len(gl) - 1) * gl.var(ddof=1)) / (len(tl) + len(gl) - 2))
            se = sp * np.sqrt(vif / mset + 1 / len(gl))
            tstat = (tl.mean() - gl.mean()) / se
            p_adj = 2 * stats.t.sf(abs(tstat), df=max(len(gl) - 1, 1))
            rows.append({**base, "analysis": "correlation_aware",
                         "variant": f"CAMERA-style VIF, rho_bar={rb:.4f} (residual df={dof})",
                         "delta": round(obs["delta"], 4), "n_features": mset,
                         "frac_TE_up": "",
                         "p_or_note": f"VIF={vif:.1f}; effective independent TE features "
                                      f"{m_eff:.1f} of {mset}; variance-inflated p={p_adj:.3g} "
                                      f"(vs mannwhitney {obs['mw_p']:.3g})"})
            print(f"  rho_bar {rb:+.4f} -> VIF {vif:.1f} -> m_eff {m_eff:.1f}/{mset}; "
                  f"adjusted p {p_adj:.3g}", file=sys.stderr)

        # ---- D. feature-set sensitivity ------------------------------------------------
        tl = obs["te_lfc"]; gmed = obs["med_gene"]
        variants = {"LINE only":   [f for f in tl.index if f.endswith(":LINE")],
                    "SINE only":   [f for f in tl.index if f.endswith(":SINE")],
                    "LTR only":    [f for f in tl.index if f.endswith(":LTR")],
                    "DNA only":    [f for f in tl.index if f.endswith(":DNA")]}
        keep = obs["norm"][ [f for f in tl.index if f in obs["norm"].columns] ].mean(0)
        variants["expressed (mean norm count >= 10)"] = list(keep[keep >= 10].index)
        variants["trimmed (drop 5% most extreme log2FC)"] = list(
            tl[(tl >= tl.quantile(0.05)) & (tl <= tl.quantile(0.95))].index)
        for label, feats in variants.items():
            feats = [f for f in feats if f in tl.index]
            if len(feats) < 5:
                continue
            d = float(tl[feats].median() - gmed)
            rows.append({**base, "analysis": "feature_set_sensitivity", "variant": label,
                         "delta": round(d, 4), "n_features": len(feats),
                         "frac_TE_up": round(float((tl[feats] > 0).mean()), 3),
                         "p_or_note": "same sign" if np.sign(d) == np.sign(obs["delta"])
                                      else "SIGN DIFFERS from headline"})

    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    out.to_csv(a.out, index=False)
    print(f"\nwrote {a.out} ({len(out)} rows)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
