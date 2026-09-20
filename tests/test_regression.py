#!/usr/bin/env python3
"""
test_regression.py — do the engine's conclusions survive a change to the codebase?

    python tests/test_regression.py            # compare against the stored baseline
    python tests/test_regression.py --bless    # record the current output as the baseline

The rule this enforces: a schema migration, a refactor or a new evidence layer may change
*what the graph knows*, but it must never change an existing conclusion silently. If a
proof tree changes, this test fails and prints the diff. **Do not edit code until the diff
goes away — read the diff and decide whether the new answer is the correct one.** A
regression test you "fix" by making the output match the old value is worse than no test.

Checks:
    1. proof-tree text for a fixed panel of genes, byte-for-byte against baseline
    2. rule firing counts per rule
    3. edge counts per layer and per evidence tier
    4. every edge file carries the context columns, fully populated
"""
from __future__ import annotations
import argparse, glob, json, subprocess, sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "tests" / "baseline.json"
GENES = ["TET2", "DNMT3A", "SETDB1", "TRIM28", "DNMT1", "EZH2", "KDM4A",
         "MPHOSPH8", "SUV39H1", "TP53"]
CONTEXT_COLS = ["context_cell_type", "context_species", "perturbation_modality", "assay",
                "timepoint", "te_resolution", "quantifier", "reference_scope"]


def edge_files():
    return (sorted(glob.glob(str(ROOT / "data/graph/edges_*.csv")))
            + sorted(glob.glob(str(ROOT / "results/edges_*.csv"))))


def proof_text() -> str:
    r = subprocess.run([sys.executable, "src/te_reason.py", *GENES, "--proofs"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"te_reason.py failed:\n{r.stderr[-2000:]}")
    return r.stdout


def rule_counts() -> dict:
    sys.path.insert(0, str(ROOT / "src"))
    import nesy_rules as N
    from collections import Counter
    edges = []
    for f in edge_files():
        d = pd.read_csv(f, keep_default_na=False)
        for r in d.itertuples():
            edges.append(N.Edge(str(r.subject), str(r.predicate), str(r.object),
                                str(r.evidence_tier), str(getattr(r, "source", "")),
                                str(getattr(r, "statistic", "")), None, str(r.edge_id)))
    derived, _ = N.forward_chain(edges)
    c = Counter(d.rule for d in derived)
    return {"n_input_edges": len(edges), "n_derived": len(derived),
            "by_rule": {name: c.get(name, 0) for name, _, _ in N.RULES}}


def layer_counts() -> dict:
    out = {}
    for f in edge_files():
        d = pd.read_csv(f, keep_default_na=False)
        out[Path(f).name] = {"rows": len(d),
                             "tiers": d.evidence_tier.value_counts().to_dict()}
    return out


def context_complete() -> dict:
    bad = {}
    for f in edge_files():
        d = pd.read_csv(f, keep_default_na=False)
        missing = [c for c in CONTEXT_COLS if c not in d.columns]
        empty = {c: int((d[c].astype(str).str.strip() == "").sum())
                 for c in CONTEXT_COLS if c in d.columns}
        empty = {k: v for k, v in empty.items() if v}
        if missing or empty:
            bad[Path(f).name] = {"missing_columns": missing, "empty_cells": empty}
    return bad


def worked_examples() -> dict:
    """Structured per-gene record. A text diff of the proof output catches everything,
    but it cannot tell you *what* changed — and the failure mode that matters is a
    changed biological conclusion hiding inside a cosmetic reformat. So compare the
    scientific content field by field: which edges came back, with what signs, at what
    tiers, through which rules, resting on which premises, and with what context."""
    sys.path.insert(0, str(ROOT / "src"))
    import te_reason as T
    edges, derived, index, _ = T.load_graph()
    out = {}
    for g in GENES:
        r = T.explain(g, edges, derived, index)
        prose = T.narrate(r)
        allowed = {e.edge_id for e in edges} | {d.edge.edge_id for d in derived}
        kept, rejected = T.verify_claims(prose, allowed)
        rec = {"best_tier": r.get("best_tier"),
               "counts": {k: r.get(f"n_{k}") for k in
                          ("measured", "curated", "literature", "inferred")},
               "sentences_kept": len(kept), "sentences_rejected": len(rejected),
               "claims": [], "paths": []}
        # one record per claim the engine is willing to state, with the provenance that
        # justifies it — citations, rule, and proof-tree shape
        for cl in r.get("claims", []):
            rec["claims"].append({
                "id": "|".join(sorted(cl.get("edge_ids", []))),
                "tier": cl.get("tier"), "rule": cl.get("rule"),
                "cites": sorted(cl.get("edge_ids", [])),
                "proof_depth": len(cl.get("proof", []) or []),
                # sign is the direction word, which is the biological conclusion
                "direction": ("raise" if " raise" in cl.get("text", "")
                              else "lower" if " lower" in cl.get("text", "")
                              else "none")})
        for p in r.get("paths", []):
            rec["paths"].append({"id": "|".join(p.get("edge_ids", [])),
                                 "tier": p.get("tier"), "hops": p.get("hops", [])})
        # inferred-edge context, which is what may silently turn a scoped prediction
        # into a universal claim
        # lists, not tuples: this record round-trips through JSON, and a tuple comes back
        # as a list, so a tuple here makes the test fail against its own fresh baseline
        rec["inference_context"] = [list(t) for t in sorted(
            {(d.edge.edge_id, d.rule,
              d.edge.ctx().get("context_generalization_required"),
              d.edge.ctx().get("context_cell_type"),
              d.edge.ctx().get("te_resolution"))
             for d in derived if d.edge.subject == g})]
        rec["claims"].sort(key=lambda x: x["id"])
        rec["paths"].sort(key=lambda x: x["id"])
        out[g] = rec
    return out


def collect() -> dict:
    return {"proofs": proof_text(), "rules": rule_counts(), "layers": layer_counts(),
            "examples": worked_examples()}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bless", action="store_true",
                    help="record current output as baseline (only after reading the diff)")
    a = ap.parse_args()

    cur, ctx, fails = collect(), context_complete(), []
    if ctx:
        fails.append(f"context columns incomplete: {json.dumps(ctx)}")

    if a.bless:
        BASELINE.parent.mkdir(exist_ok=True)
        json.dump(cur, open(BASELINE, "w"), indent=1)
        print(f"baseline written -> {BASELINE}")
        print(json.dumps(cur["rules"], indent=1))
        if fails:
            print("\nNOTE, blessed anyway:", *fails, sep="\n  ")
        return

    if not BASELINE.exists():
        raise SystemExit(f"no baseline at {BASELINE} — run with --bless first")
    old = json.load(open(BASELINE))

    if old["proofs"] != cur["proofs"]:
        import difflib
        d = list(difflib.unified_diff(old["proofs"].splitlines(), cur["proofs"].splitlines(),
                                      "baseline", "current", lineterm="", n=1))
        fails.append("PROOF TREES CHANGED — read this diff, do not silence it:\n"
                     + "\n".join(d[:80]))
    if old["rules"] != cur["rules"]:
        fails.append(f"rule firing changed:\n  was {old['rules']}\n  now {cur['rules']}")
    for k in set(old["layers"]) | set(cur["layers"]):
        if old["layers"].get(k) != cur["layers"].get(k):
            fails.append(f"layer {k}: was {old['layers'].get(k)} now {cur['layers'].get(k)}")

    # per-gene scientific content, field by field — this is the check that tells you WHICH
    # conclusion moved. A changed biological conclusion is surfaced for review; it is never
    # to be "fixed" by editing code until the old answer comes back.
    oe, ce = old.get("examples", {}), cur.get("examples", {})
    for g in sorted(set(oe) | set(ce)):
        o, c = oe.get(g), ce.get(g)
        if o is None or c is None:
            fails.append(f"{g}: gene {'added to' if o is None else 'removed from'} the panel")
            continue
        for field in ("best_tier", "counts", "sentences_kept", "sentences_rejected"):
            if o.get(field) != c.get(field):
                fails.append(f"{g}.{field}: was {o.get(field)} now {c.get(field)}")
        if o.get("inference_context") != c.get("inference_context"):
            fails.append(f"{g}.inference_context changed:\n     was {o.get('inference_context')}"
                         f"\n     now {c.get('inference_context')}")
        for field in ("claims", "paths"):
            ob = {x["id"]: x for x in o.get(field, [])}
            cb = {x["id"]: x for x in c.get(field, [])}
            for i in sorted(set(ob) - set(cb)):
                fails.append(f"{g}: {field[:-1]} DISAPPEARED {ob[i]}")
            for i in sorted(set(cb) - set(ob)):
                fails.append(f"{g}: {field[:-1]} APPEARED {cb[i]}")
            for i in sorted(set(ob) & set(cb)):
                for k2 in sorted(set(ob[i]) | set(cb[i])):
                    if ob[i].get(k2) != cb[i].get(k2):
                        fails.append(f"{g}: {i}.{k2} was {ob[i].get(k2)!r} "
                                     f"now {cb[i].get(k2)!r}")

    if fails:
        print("FAIL")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("PASS — proof trees, rule firing, layer counts and edge context all unchanged")
    print(json.dumps(cur["rules"], indent=1))


if __name__ == "__main__":
    main()
