#!/usr/bin/env python
"""Structural audit of the knowledge graph.

Answers "how good is this graph?" with numbers instead of adjectives. Nothing here
validates the *biology* — an edge can be structurally perfect and still wrong. What this
measures is whether the graph is internally coherent, honestly provenanced, and whether its
reasoning capacity is spread across many anchors or resting on a few.

Usage:  python src/validate_graph.py [--out results/graph_validation.csv]
"""
import argparse, glob, json, os, sys
from collections import Counter, defaultdict
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# predicate -> (allowed subject types, allowed object types). The schema contract.
SCHEMA = {
    "SILENCES":              ({"Gene"}, {"TEFamily", "TESubfamily", "TEClass"}),
    "DEREPRESSES":           ({"Gene"}, {"TEFamily", "TESubfamily", "TEClass"}),
    "NO_DETECTED_EFFECT_ON": ({"Gene"}, {"GeneSet", "Signature"}),
    "DEPOSITS_MARK":         ({"Gene"}, {"ChromatinMark"}),
    "ERASES_MARK":           ({"Gene"}, {"ChromatinMark"}),
    "MARK_AT":               ({"ChromatinMark"}, {"TEFamily", "TESubfamily", "TEClass"}),
    "INTERACTS_WITH":        ({"Gene"}, {"Gene"}),
    "MEMBER_OF":             ({"Gene"}, {"Complex"}),
    "PARTICIPATES_IN":       ({"Gene"}, {"Pathway"}),
    "ANNOTATED_TO":          ({"Gene"}, {"GOTerm"}),
    "RECRUITS":              ({"Gene"}, {"Gene"}),
}
SIGNED = {"SILENCES": +1, "DEREPRESSES": -1}


def load():
    files = sorted(glob.glob(os.path.join(ROOT, "data/graph/edges_*.csv"))
                   + glob.glob(os.path.join(ROOT, "results/edges_*.csv")))
    # derived edges are the OUTPUT of the rule layer, not an input layer. They are loaded
    # because MARK_AT exists only there (R1 creates it), and the point of several metrics
    # below is exactly how few of them there are.
    derived = os.path.join(ROOT, "results/derived_edges.csv")
    if os.path.exists(derived):
        files.append(derived)
    frames = []
    for f in files:
        d = pd.read_csv(f, keep_default_na=False)
        d["layer"] = os.path.basename(f).replace("edges_", "").replace(".csv", "")
        frames.append(d)
    edges = pd.concat(frames, ignore_index=True)
    nodes = pd.read_csv(os.path.join(ROOT, "data/graph/nodes.csv"), keep_default_na=False)
    return edges, nodes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/graph_validation.csv")
    ap.add_argument("--json", default="results/graph_validation.json")
    a = ap.parse_args()
    E, N = load()
    R = []                                        # (metric, value, verdict, note)
    def rec(m, v, verdict, note=""): R.append(dict(metric=m, value=v, verdict=verdict, note=note))

    # ---- 1. size and composition -------------------------------------------------
    rec("edges_total", len(E), "info")
    rec("nodes_declared", len(N), "info")
    for layer, n in E.layer.value_counts().items():
        rec(f"edges_layer::{layer}", int(n), "info")
    for tier, n in E.evidence_tier.value_counts().items():
        rec(f"edges_tier::{tier}", int(n), "info")
    # source concentration: is one database the whole graph?
    src = E.source.value_counts()
    top_src_frac = src.iloc[0] / len(E)
    rec("source_concentration", round(float(top_src_frac), 3),
        "WEAKNESS" if top_src_frac > 0.5 else "ok",
        f"largest source = {src.index[0]} ({src.iloc[0]} edges)")

    # ---- 2. schema conformance ---------------------------------------------------
    # Derived edges carry no subject_type/object_type — the rule layer emits entity names
    # whose types are implied by the rule that fired. Schema conformance is therefore a
    # statement about the INPUT layers only, and saying so is more honest than silently
    # counting 89 untyped rows as violations (the first run of this script did exactly that).
    viol = []
    typed = E[~E.layer.str.startswith("derived")]
    rec("schema_checked_edges", len(typed), "info", "derived edges are untyped by design")
    for _, r in typed.iterrows():
        allowed = SCHEMA.get(r.predicate)
        if allowed is None:
            viol.append((r.edge_id, r.predicate, "unknown predicate")); continue
        s_ok = r.subject_type in allowed[0]
        o_ok = r.object_type in allowed[1]
        if not (s_ok and o_ok):
            viol.append((r.edge_id, r.predicate, f"{r.subject_type}->{r.object_type}"))
    rec("schema_violations", len(viol), "PASS" if not viol else "FAIL",
        "; ".join(f"{v[1]} {v[2]}" for v in viol[:4]))
    # do the derived edges at least use predicates the schema knows?
    if E.layer.str.startswith("derived").any():
        dpred = set(E[E.layer.str.startswith("derived")].predicate) - set(SCHEMA)
        rec("derived_unknown_predicates", len(dpred), "PASS" if not dpred else "FAIL",
            ", ".join(sorted(dpred)))

    # ---- 3. hygiene: self-loops, duplicates, contradictions ----------------------
    self_loops = int((E.subject == E.object).sum())
    rec("self_loops", self_loops, "PASS" if self_loops == 0 else "FAIL")
    key = E.subject + "|" + E.predicate + "|" + E.object
    dups = int(len(key) - key.nunique())
    rec("duplicate_triples", dups, "PASS" if dups == 0 else "WARN",
        "same subject/predicate/object appearing more than once")
    # contradictions: one gene both SILENCES and DEREPRESSES the same TE
    signed = E[E.predicate.isin(SIGNED)]
    contra, detail = 0, []
    for (s, o), g in signed.groupby(["subject", "object"]):
        if g.predicate.nunique() > 1:
            contra += 1
            detail.append(f"{s}->{o} [{'/'.join(sorted(g.evidence_tier.unique()))}"
                          f" via {'/'.join(sorted(set(g.source_detail)))}]")
    rec("sign_contradictions", contra, "PASS" if contra == 0 else "REVIEW",
        "; ".join(detail) or "same gene-TE pair asserted in both directions")
    # a contradiction WITHIN one layer from one source is a different, worse problem than
    # two layers disagreeing: it means the extractor is self-inconsistent.
    intra = 0
    for (s, o, lay), g in signed.groupby(["subject", "object", "layer"]):
        if g.predicate.nunique() > 1:
            intra += 1
    rec("sign_contradictions_within_one_layer", intra,
        "PASS" if intra == 0 else "DEFECT",
        "a single source asserting both directions for one pair — extractor self-inconsistency")

    # ---- 4. provenance completeness ----------------------------------------------
    for col in ["source", "retrieved", "native_score", "statistic"]:
        filled = int((E[col].astype(str).str.strip().ne("") & E[col].astype(str).ne("not_applicable")).sum())
        rec(f"provenance_filled::{col}", round(filled / len(E), 3),
            "ok" if filled / len(E) > 0.5 else "info")
    ctx_cols = [c for c in E.columns if c.startswith("context_") or c in
                ("perturbation_modality", "assay", "timepoint", "te_resolution",
                 "quantifier", "reference_scope")]
    blank_ctx = int((E[ctx_cols].astype(str).apply(lambda c: c.str.strip().eq("")).any(axis=1)).sum())
    rec("edges_with_blank_context_cell", blank_ctx, "PASS" if blank_ctx == 0 else "FAIL",
        f"{len(ctx_cols)} context columns must never be empty (use not_applicable)")

    # ---- 5. degree structure -----------------------------------------------------
    deg = Counter()
    for s, o in zip(E.subject, E.object):
        deg[s] += 1; deg[o] += 1
    dser = pd.Series(deg).sort_values(ascending=False)
    rec("distinct_entities_touched", len(dser), "info")
    rec("degree_median", float(dser.median()), "info")
    rec("degree_max", int(dser.iloc[0]), "info", f"hub = {dser.index[0]}")
    top1pct = max(1, len(dser) // 100)
    frac_top = dser.iloc[:top1pct].sum() / (2 * len(E))
    rec("edge_share_of_top_1pct_entities", round(float(frac_top), 3),
        "WEAKNESS" if frac_top > 0.30 else "ok",
        "high value = a few hubs carry the graph")

    # ---- 6. the TE side: coverage and sparsity -----------------------------------
    te_types = {"TEFamily", "TESubfamily", "TEClass"}
    te_edges = E[E.object_type.isin(te_types)]
    te_nodes_with_edges = set(te_edges.object)
    try:
        vocab = pd.read_csv(os.path.join(ROOT, "data/graph/te_subfamilies_hg38.csv"))
        n_vocab = len(vocab)
    except Exception:
        n_vocab = None
    rec("te_entities_with_any_edge", len(te_nodes_with_edges), "info",
        ", ".join(sorted(te_nodes_with_edges)[:6]))
    if n_vocab:
        rec("te_vocabulary_coverage", round(len(te_nodes_with_edges) / n_vocab, 4),
            "WEAKNESS", f"{len(te_nodes_with_edges)} of {n_vocab} subfamilies in the vocabulary "
                        "have any edge at all — the graph is overwhelmingly empty on the TE side")
    rec("gene_TE_edges_total", len(te_edges), "info")
    rec("gene_TE_edges_measured", int((te_edges.evidence_tier == "measured").sum()), "info")

    # ---- 7. reasoning capacity: what grounds the inference layer? ----------------
    mark_at = E[E.predicate == "MARK_AT"]
    rec("MARK_AT_edges", len(mark_at), "WEAKNESS" if len(mark_at) < 10 else "ok",
        "every R2/R3 inference consumes one of these")
    dep = E[E.predicate.isin(["DEPOSITS_MARK", "ERASES_MARK"])]
    rec("mark_writer_eraser_edges", len(dep), "info")
    rec("distinct_marks_grounded", mark_at.subject.nunique(), "WEAKNESS",
        ", ".join(sorted(mark_at.subject.unique())))
    # which genes can supply a measured effect INTO the rule layer at all?
    enzymes = set(dep.subject)
    measured_genes = set(E[(E.evidence_tier == "measured") & E.object_type.isin(te_types)].subject)
    rec("measured_genes_that_are_enzymes", len(measured_genes & enzymes), "info",
        f"measured={sorted(measured_genes)}; of these, enzymes={sorted(measured_genes & enzymes)}")
    rec("measured_genes_wasted_on_rules", len(measured_genes - enzymes), "WEAKNESS",
        f"{sorted(measured_genes - enzymes)} have measured TE effects but no DEPOSITS_MARK/ERASES_MARK "
        "edge, so they cannot satisfy R1 and contribute nothing to inference")

    # ---- 8. R5 diagnosis ---------------------------------------------------------
    rec("RECRUITS_edges", int((E.predicate == "RECRUITS").sum()),
        "EXPLAINS_R5_ZERO" if (E.predicate == "RECRUITS").sum() == 0 else "info",
        "R5_RECRUITMENT_CHAIN requires RECRUITS edges; none exist, so it can never fire")

    # ---- 9. connectivity ---------------------------------------------------------
    adj = defaultdict(set)
    for s, o in zip(E.subject, E.object):
        adj[s].add(o); adj[o].add(s)
    seen, comps = set(), []
    for n0 in adj:
        if n0 in seen: continue
        stack, comp = [n0], []
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x); comp.append(x)
            stack.extend(adj[x] - seen)
        comps.append(len(comp))
    comps.sort(reverse=True)
    rec("connected_components", len(comps), "info", f"sizes: {comps[:5]}")
    rec("largest_component_fraction", round(comps[0] / len(adj), 3),
        "ok" if comps[0] / len(adj) > 0.9 else "WARN")

    out = pd.DataFrame(R)
    os.makedirs(os.path.dirname(os.path.join(ROOT, a.out)), exist_ok=True)
    out.to_csv(os.path.join(ROOT, a.out), index=False)
    with open(os.path.join(ROOT, a.json), "w") as f:
        json.dump(R, f, indent=1)
    w = out[out.verdict.isin(["FAIL", "WEAKNESS", "REVIEW", "WARN"])]
    for _, r in out.iterrows():
        print(f"{r.verdict:18s} {r.metric:42s} {r.value}")
    print(f"\n{len(out)} metrics · {len(w)} flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
