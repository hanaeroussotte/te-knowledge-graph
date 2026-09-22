#!/usr/bin/env python3
"""
ca_principles.py — turn cellular-automaton recovery trajectories into measured statistics.

    python src/ca_principles.py --selftest
    python src/ca_principles.py --runs ca_runs.csv --steps ca_steps.csv --out results/ca_principles.csv

WHY THIS EXISTS
---------------
The collaboration design (docs/CELLULAR_AUTOMATA.md) says: the abstract model discovers
general principles of recovery, the knowledge graph looks for biological analogies, real
perturbation data tests them. That ordering hides a dependency, and the dependency is the
bottleneck.

**The CA side does not emit principles. It emits trajectories.** "Recovery uses only a few
dimensions" is not an output of a search; it is a claim about a set of searches, and it needs
a statistic, a null model, and a held-out test before it is anything more than an impression.
Until that is done there is nothing for the biological layer to translate, and any analogy
found would be an analogy to an unvalidated pattern.

So this script does three things, in order:

  1. EXTRACT   compute one number per question, from the trajectory table
  2. NULL      compare each to a randomised control, because most of these questions have a
               generic answer. Optimisation in 8 dimensions often concentrates in a few
               directions whatever the landscape is; convergence can be an artefact of a
               bounded space. A statistic without its null is not evidence
  3. GENERALISE hold out whole disturbances, derive the principle on the rest, and test it on
               the held-out ones. THIS is the step that makes a principle a principle: it has
               to predict recovery for disturbances it was not derived from

Only statistics that beat their null AND survive the held-out test should be handed to the
biological layer. The rest are descriptions of one run of one model.

SELF-TEST COVERAGE — read this before trusting any number here
--------------------------------------------------------------
`--selftest` generates trajectories with a known answer. Measured on 2026-09-22:

    concentrated (truth: recovery only moves 2 of 8 dimensions)
        effective_dimensions_used  1.96  (null 7.08, p = 0.000)   <- recovers the truth
        held_out_accuracy          1.00  (baseline 0.50)          <- principle transfers
    diffuse (truth: recovery moves all 8 equally)
        effective_dimensions_used  7.66  (null 7.40, p = 0.984)   <- correctly NOT significant
        held_out_accuracy          0.50  (baseline 0.50)          <- correctly NO principle

Both directions pass, and the second matters more: on data with no structure the script
reports no structure instead of manufacturing one.

**But only 2 of the 5 statistics are exercised by that test.** The synthetic generator
produces independent per-dimension steps and no disturbance-specific structure, so it
contains no joint change, no convergence and no multi-basin geometry to find — which is why
q2, q4 and q6 sit at their null values above. Their implementations are argued from first
principles and are UNVALIDATED. Before relying on one, extend `synth()` to generate the
phenomenon it claims to detect and confirm it is detected.

INPUT SCHEMA (two CSVs — this is the handoff contract)
------------------------------------------------------
`--runs` one row per (disturbance, search run):
    disturbance_id   str    which perturbed rule / disturbed system
    run_id           str    independent search replicate
    recovered        0/1    did this run reach the desired behaviour
    n_steps          int    steps taken
    x0_0 .. x0_{d-1} float  starting coordinates (the disturbed system)
    xf_0 .. xf_{d-1} float  final coordinates
    behaviour_final  float  achieved behaviour score (higher = closer to desired)

`--steps` one row per (disturbance, run, step) — optional, needed only for Q3 and Q5:
    disturbance_id, run_id, step (int)
    x_0 .. x_{d-1}   float  coordinates at this step
    behaviour        float  behaviour score at this step

Dimensionality d is inferred. Nothing here assumes d == 8.
"""
from __future__ import annotations
import argparse, itertools, os, sys
import numpy as np
import pandas as pd

RNG = np.random.default_rng(0)


# ---------------------------------------------------------------- helpers
def _coord_cols(df, prefix):
    cols = sorted([c for c in df.columns if c.startswith(prefix)],
                  key=lambda c: int(c.rsplit("_", 1)[1]))
    if not cols:
        raise SystemExit(f"no columns with prefix {prefix!r} in the runs table")
    return cols


def participation_ratio(v: np.ndarray) -> float:
    """Effective number of dimensions used, from the eigenvalues of the displacement
    covariance. PR = (sum λ)^2 / sum λ^2 — d if variance is spread evenly over d
    dimensions, 1 if it all sits in one. Preferred over 'variance explained by PC1'
    because it needs no arbitrary threshold."""
    if v.shape[0] < 2:
        return float("nan")
    lam = np.linalg.eigvalsh(np.cov(v, rowvar=False))
    lam = np.clip(lam, 0, None)
    return float(lam.sum() ** 2 / (lam ** 2).sum()) if (lam ** 2).sum() > 0 else float("nan")


# ---------------------------------------------------------------- Q1..Q7
def q1_dimensionality(disp, d):
    """Do successful recoveries use a small subset of dimensions?

    Null: the same displacement magnitudes, but with each row's components randomly
    reassigned across dimensions. That destroys any dimension preference while preserving
    step sizes — so a low PR that survives is about WHICH dimensions, not how far."""
    obs = participation_ratio(disp)
    null = []
    for _ in range(500):
        p = np.array([RNG.permutation(r) for r in disp])
        null.append(participation_ratio(p))
    null = np.array(null)
    return dict(statistic="effective_dimensions_used", value=round(obs, 3),
                null_mean=round(float(np.nanmean(null)), 3),
                p_value=round(float((null <= obs).mean()), 4),
                n=len(disp), note=f"of {d} available dimensions; lower = more concentrated")


def q2_convergence(disp, labels):
    """Do different disturbances converge on common regions?

    Statistic: mean within-disturbance distance between endpoints divided by mean
    between-disturbance distance. < 1 means endpoints cluster BY DISTURBANCE (each
    disturbance has its own solution); ≈ 1 means disturbance identity does not predict where
    you end up, which is the interesting 'common region' case.

    Null: shuffle the disturbance labels."""
    def ratio(lab):
        w, b = [], []
        for i, j in itertools.combinations(range(len(disp)), 2):
            dist = float(np.linalg.norm(disp[i] - disp[j]))
            (w if lab[i] == lab[j] else b).append(dist)
        if not w or not b:
            return float("nan")
        return float(np.mean(w) / np.mean(b))
    obs = ratio(labels)
    null = np.array([ratio(RNG.permutation(labels)) for _ in range(300)])
    return dict(statistic="within_over_between_disturbance_distance", value=round(obs, 3),
                null_mean=round(float(np.nanmean(null)), 3),
                p_value=round(float((null <= obs).mean()), 4),
                n=len(disp),
                note="<1 = disturbance-specific solutions; ~1 = shared region")


def q4_joint_change(disp, d):
    """Must two dimensions change together?

    Statistic: the largest absolute pairwise correlation between dimension displacements
    across successful runs, with the pair named. Null: independently permute each column,
    which breaks pairing while keeping each dimension's marginal distribution."""
    if disp.shape[0] < 4:
        return dict(statistic="max_abs_pairwise_dimension_correlation", value=float("nan"),
                    null_mean=float("nan"), p_value=float("nan"), n=len(disp),
                    note="too few successful runs")
    def maxcorr(m):
        c = np.corrcoef(m, rowvar=False)
        np.fill_diagonal(c, 0)
        c = np.nan_to_num(c)
        k = int(np.argmax(np.abs(c)))
        return float(np.abs(c).max()), divmod(k, c.shape[0])
    obs, pair = maxcorr(disp)
    null = np.array([maxcorr(np.column_stack([RNG.permutation(disp[:, k])
                                              for k in range(d)]))[0] for _ in range(300)])
    return dict(statistic="max_abs_pairwise_dimension_correlation", value=round(obs, 3),
                null_mean=round(float(null.mean()), 3),
                p_value=round(float((null >= obs).mean()), 4), n=len(disp),
                note=f"strongest pair: dims {pair[0]} and {pair[1]}")


def q6_multiple_routes(disp, beh, labels):
    """Multiple distinct routes to equivalent recovered behaviour?

    The interesting pattern is endpoints that are FAR APART in coordinates while achieving
    the SAME behaviour. Statistic: correlation between pairwise coordinate distance and
    pairwise behaviour difference. Near zero with large coordinate spread = several routes to
    the same outcome; strongly positive = one basin and distance from it costs you."""
    cd, bd = [], []
    for i, j in itertools.combinations(range(len(disp)), 2):
        cd.append(float(np.linalg.norm(disp[i] - disp[j])))
        bd.append(abs(float(beh[i] - beh[j])))
    if len(cd) < 6 or np.std(bd) == 0:
        return dict(statistic="coord_distance_vs_behaviour_difference", value=float("nan"),
                    null_mean=float("nan"), p_value=float("nan"), n=len(disp),
                    note="insufficient spread")
    r = float(np.corrcoef(cd, bd)[0, 1])
    return dict(statistic="coord_distance_vs_behaviour_difference", value=round(r, 3),
                null_mean=0.0, p_value=float("nan"), n=len(disp),
                note="~0 with wide coordinate spread = multiple equivalent routes; "
                     "high = single basin")


def q7_generalisation(runs, coord0, coordf, d):
    """THE ONE THAT MATTERS: does the principle transfer to unseen disturbances?

    Leave-one-disturbance-out. On the training disturbances, rank dimensions by mean absolute
    displacement among successful runs and keep the top half. Then ask, on the HELD-OUT
    disturbance, whether successful runs really did move more in those dimensions than in the
    others. Reported as accuracy across folds, against a 0.5 coin-flip baseline.

    If this does not beat 0.5, there is no transferable principle and nothing should be handed
    to the biological layer — whatever the other statistics say."""
    ds = sorted(runs.disturbance_id.unique())
    if len(ds) < 3:
        return dict(statistic="held_out_disturbance_accuracy", value=float("nan"),
                    null_mean=0.5, p_value=float("nan"), n=len(ds),
                    note="need >=3 disturbances to hold one out")
    hits = []
    for held in ds:
        tr = runs[(runs.disturbance_id != held) & (runs.recovered == 1)]
        te = runs[(runs.disturbance_id == held) & (runs.recovered == 1)]
        if len(tr) < 2 or len(te) < 1:
            continue
        dtr = np.abs(tr[coordf].values - tr[coord0].values).mean(0)
        top = set(np.argsort(dtr)[-(d // 2):])
        dte = np.abs(te[coordf].values - te[coord0].values).mean(0)
        hits.append(float(dte[list(top)].mean() > dte[[k for k in range(d)
                                                       if k not in top]].mean()))
    if not hits:
        return dict(statistic="held_out_disturbance_accuracy", value=float("nan"),
                    null_mean=0.5, p_value=float("nan"), n=0, note="no usable folds")
    acc = float(np.mean(hits))
    return dict(statistic="held_out_disturbance_accuracy", value=round(acc, 3),
                null_mean=0.5, p_value=float("nan"), n=len(hits),
                note="fraction of held-out disturbances whose successful runs moved most in "
                     "the dimensions learned from the others; 0.5 = no transfer")


def analyse(runs: pd.DataFrame) -> pd.DataFrame:
    c0, cf = _coord_cols(runs, "x0_"), _coord_cols(runs, "xf_")
    d = len(c0)
    ok = runs[runs.recovered == 1]
    if len(ok) < 3:
        raise SystemExit(f"only {len(ok)} recovered runs — nothing to characterise")
    disp = ok[cf].values - ok[c0].values
    rows = [q1_dimensionality(disp, d),
            q2_convergence(disp, list(ok.disturbance_id)),
            q4_joint_change(disp, d),
            q6_multiple_routes(disp, ok.behaviour_final.values, list(ok.disturbance_id)),
            q7_generalisation(runs, c0, cf, d)]
    out = pd.DataFrame(rows)
    out.insert(0, "dimensions", d)
    out.insert(0, "n_recovered_runs", len(ok))
    out.insert(0, "n_disturbances", runs.disturbance_id.nunique())
    return out


# ---------------------------------------------------------------- selftest
def synth(d=8, n_dist=6, n_run=25, concentrated=True, seed=1):
    """Generate trajectories with a KNOWN answer, so the statistics can be checked.

    concentrated=True  : recovery only ever moves dimensions 0 and 1  -> PR should be ~2
    concentrated=False : recovery moves all dimensions equally        -> PR should be ~d
    """
    g = np.random.default_rng(seed)
    rows = []
    for di in range(n_dist):
        for ri in range(n_run):
            x0 = g.normal(0, 1, d)
            step = np.zeros(d)
            if concentrated:
                step[[0, 1]] = g.normal(0, 1.5, 2)
            else:
                step = g.normal(0, 1.5, d)
            rec = 1 if g.random() < 0.7 else 0
            xf = x0 + step * rec
            r = {"disturbance_id": f"D{di}", "run_id": f"D{di}_r{ri}", "recovered": rec,
                 "n_steps": int(g.integers(5, 40)),
                 "behaviour_final": float(g.normal(0.9 if rec else 0.2, 0.05))}
            r.update({f"x0_{k}": x0[k] for k in range(d)})
            r.update({f"xf_{k}": xf[k] for k in range(d)})
            rows.append(r)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs")
    ap.add_argument("--steps", help="reserved for the order/bottleneck questions")
    ap.add_argument("--out", default="results/ca_principles.csv")
    ap.add_argument("--selftest", action="store_true",
                    help="run on synthetic data with a known answer")
    a = ap.parse_args()

    if a.selftest:
        for tag, conc in [("CONCENTRATED (truth: 2 of 8 dims)", True),
                          ("DIFFUSE (truth: all 8 dims)", False)]:
            print(f"\n=== {tag} ===")
            print(analyse(synth(concentrated=conc))
                  [["statistic", "value", "null_mean", "p_value", "note"]].to_string(index=False))
        return 0

    if not a.runs:
        ap.error("--runs required (or --selftest)")
    out = analyse(pd.read_csv(a.runs))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    out.to_csv(a.out, index=False)
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
