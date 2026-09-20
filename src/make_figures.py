#!/usr/bin/env python3
"""
make_figures.py — regenerate the panel-reference figures from saved tables.

    python src/make_figures.py --outdir figures

Exists so that "the figures regenerate" is a check the gate can actually run rather than
an assertion. Both figures are rebuilt from CSVs in results/, with no kernel state:

    fig_reference_control.png  per-feature log2FC, original vs panel-augmented reference
    fig_two_arm.png            TE arm vs interferon arm, plus why the interferon arm is null

Inputs: results/deseq2_results.csv, results/deseq2_results_panel.csv,
        results/reference_perturbation.csv, results/two_arm_effects.csv,
        results/sensor_expression_k562.csv
"""
from __future__ import annotations
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

META_GREY = "#7d8896"
COL = {"gene": "#b9c0c9", "TE": "#c4462d"}
CKD = {"SETDB1": "#4c72b0", "TRIM28": "#c4462d", "DNMT1": "#2f8f5b"}


def style():
    plt.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 300,
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#3b4252", "axes.linewidth": .8,
        "axes.titlelocation": "left", "axes.titlepad": 6,
    })


def fig_reference_control(res: Path, out: Path) -> Path:
    old = pd.read_csv(res / "deseq2_results.csv", index_col=0)
    new = pd.read_csv(res / "deseq2_results_panel.csv", index_col=0)
    pert = pd.read_csv(res / "reference_perturbation.csv")
    old["feat"], new["feat"] = old.index, new.index

    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.5), sharex=True, sharey=True)
    for ax, kd in zip(axes, ["SETDB1", "TRIM28", "DNMT1"]):
        a = old[old.knockdown == kd].set_index("feat")
        b = new[new.knockdown == kd].set_index("feat")
        common = a.index.intersection(b.index)
        m = pd.DataFrame({"old": a.loc[common, "log2FoldChange"],
                          "new": b.loc[common, "log2FoldChange"],
                          "cls": b.loc[common, "feature_class"]}).dropna()
        m = m[m.cls != "panel_gene"]
        for cl in ["gene", "TE"]:
            d = m[m.cls == cl]
            ax.scatter(d.old, d.new, s=7 if cl == "gene" else 11, c=COL[cl],
                       alpha=.45 if cl == "gene" else .85, lw=0,
                       label="protein-coding genes" if cl == "gene" else "TE subfamilies",
                       zorder=2 if cl == "gene" else 3)
        lim = (-3.2, 3.2)
        ax.plot(lim, lim, color="#3b4252", lw=.7, ls=(0, (4, 3)), zorder=1)
        r = pert[(pert.knockdown == kd) & (pert.feature_set == "all")].iloc[0]
        rte = pert[(pert.knockdown == kd) & (pert.feature_set == "TE")].iloc[0]
        ax.set_title(f"{kd} knockdown")
        ax.text(.04, .955, f"r = {r.pearson:.3f}  (TE only {rte.pearson:.3f})\n"
                           f"median |Δ| = {r.median_abs_diff:.3f} log₂",
                transform=ax.transAxes, va="top", ha="left", fontsize=6.6, color="#3b4252")
        ax.set_xlim(*lim); ax.set_ylim(*lim); ax.set_aspect("equal")
        ax.set_xlabel("log₂FC, chr1+chr19 reference")
    axes[0].set_ylabel("log₂FC, panel-augmented\nreference")
    axes[0].legend(loc="lower right", frameon=False, fontsize=6.4,
                   handletextpad=.3, borderpad=.2)
    fig.suptitle("Splicing in 62 Mb of signature gene loci leaves the existing "
                 "measurements unchanged", x=.5, y=1.005, ha="center", fontsize=8.6)
    fig.tight_layout()
    p = out / "fig_reference_control.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    return p


def fig_two_arm(res: Path, out: Path) -> Path:
    arm = pd.read_csv(res / "two_arm_effects.csv")
    tab = pd.read_csv(res / "sensor_expression_k562.csv", index_col=0)

    fig = plt.figure(figsize=(9.4, 4.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.25], wspace=0.34)
    ax = fig.add_subplot(gs[0, 0])
    for _, r in arm.iterrows():
        c = CKD[r.knockdown]
        ax.plot([r.te_lo, r.te_hi], [r.ifn_delta] * 2, color=c, lw=1.2, alpha=.8, zorder=2)
        ax.plot([r.te_delta] * 2, [r.ifn_lo, r.ifn_hi], color=c, lw=1.2, alpha=.8, zorder=2)
        ax.scatter(r.te_delta, r.ifn_delta, s=46, c=c, zorder=3, lw=0)
        ax.annotate(r.knockdown, (r.te_delta, r.ifn_delta), textcoords="offset points",
                    xytext=(7, 8), fontsize=7.2, color=c, fontweight="bold")
    ax.axhline(0, color=META_GREY, lw=.7, zorder=1)
    ax.axvline(0, color=META_GREY, lw=.7, zorder=1)
    ax.set_xlabel("TE arm\nmedian log₂FC, TE subfamilies − genes")
    ax.set_ylabel("inflammation arm\nmedian log₂FC, type-I IFN set − other genes")
    ax.set_title("The TE arm moves; the interferon arm does not")
    ax.set_xlim(-0.12, 0.55); ax.set_ylim(-0.19, 0.12)
    ax.text(.975, .04, "bars: 95% bootstrap CI", transform=ax.transAxes, ha="right",
            fontsize=6.3, color=META_GREY)

    ax2 = fig.add_subplot(gs[0, 1])
    grp = {"sensor (pathway entry)": ["CGAS", "IFIH1", "RIGI", "ZBP1", "TLR3", "NLRP3"],
           "transducer": ["STING1", "MAVS", "TBK1", "IRF3", "IRF7", "STAT1", "STAT2",
                          "JAK1", "TYK2", "IFNAR1"],
           "effector (ISG)": ["IFNB1", "ISG15", "IFIT1", "IFIT3", "MX1", "OAS1", "OASL"]}
    GC = {"sensor (pathway entry)": "#c4462d", "transducer": "#7d8896",
          "effector (ISG)": "#4c72b0"}
    ylab, yv, yc = [], [], []
    for g, mem in grp.items():
        for s in sorted(mem, key=lambda x: tab.loc[x, "mean_CPM"]):
            ylab.append(s); yv.append(max(tab.loc[s, "mean_CPM"], 0.05)); yc.append(GC[g])
    ypos = np.arange(len(ylab))
    ax2.hlines(ypos, 0.05, yv, color=yc, lw=1.0, alpha=.55)
    ax2.scatter(yv, ypos, c=yc, s=22, zorder=3, lw=0)
    ax2.set_yticks(ypos); ax2.set_yticklabels(ylab, fontsize=6.2)
    ax2.set_xscale("log"); ax2.set_xlim(0.05, 3000)
    ax2.set_xticks([0.1, 1, 10, 100, 1000])
    ax2.set_xticklabels(["0.1", "1", "10", "100", "1k"])
    ax2.axvline(1, color=META_GREY, lw=.7, ls=(0, (3, 3)), zorder=1)
    ax2.set_xlabel("mean expression in K562 (CPM, log scale)")
    ax2.set_title("Why: the pathway's entry points are not expressed")
    for g, c in GC.items():
        ax2.scatter([], [], c=c, s=22, label=g, lw=0)
    ax2.legend(loc="lower right", frameon=False, fontsize=6.3,
               handletextpad=.3, borderpad=.2)
    ax2.set_ylim(-0.8, len(ylab) - 0.2)
    p = out / "fig_two_arm.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results")
    ap.add_argument("--outdir", default="figures")
    a = ap.parse_args()
    res, out = Path(a.results), Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    style()
    for fn in (fig_reference_control, fig_two_arm):
        p = fn(res, out)
        print(f"{p}  ({p.stat().st_size/1e3:.0f} kB)")


if __name__ == "__main__":
    main()
