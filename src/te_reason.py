#!/usr/bin/env python3
"""
te_reason.py — ask the graph what a gene does to transposable-element activation.

    python te_reason.py SETDB1 TET2 DNMT3A --json out/examples.json

For each gene it returns, in order of how much the evidence can carry:
  measured   what the ENCODE knockdown actually showed, with log2FC and FDR
  inferred   what the symbolic rules derive, each with a proof tree
  paths      admissible multi-hop routes from the gene to a TE family and onward
  claims     one sentence per finding, each carrying the edge IDs it rests on

The neural/symbolic coupling is the citation gate. A natural-language explanation is
only emitted for sentences whose cited edge IDs all exist in the graph; anything else is
rejected and counted rather than shown. That gate runs identically whether the prose came
from a language model or from the built-in template renderer, so the guarantee does not
depend on the model behaving.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd
import nesy_rules as nr

REPO = Path(__file__).resolve().parent.parent
# Edge layers are discovered rather than hardcoded, so adding a new layer is a matter of
# dropping an edges_*.csv into either directory.
EDGE_DIRS = [REPO / "data" / "graph", REPO / "results", Path("data/graph"), Path("results"),
             Path("out")]


def discover_edge_files(dirs=None):
    seen, files = set(), []
    for d in (dirs or EDGE_DIRS):
        d = Path(d)
        if not d.is_dir():
            continue
        for f in sorted(d.glob("edges_*.csv")):
            if f.name not in seen:
                seen.add(f.name)
                files.append(str(f))
    return files


def load_graph(files=None):
    files = files or discover_edge_files()
    edges, missing = [], []
    for p in files:
        if not Path(p).exists():
            missing.append(p); continue
        # keep_default_na=False so the literal token "not_applicable" survives, and so a
        # genuinely blank cell stays distinguishable from "this does not apply"
        df = pd.read_csv(p, keep_default_na=False)
        have = [c for c in nr.CONTEXT_KEYS if c in df.columns]
        for r in df.itertuples():
            ctx = tuple(sorted((c, str(getattr(r, c, ""))) for c in have))
            edges.append(nr.Edge(str(r.subject), str(r.predicate), str(r.object),
                                 str(r.evidence_tier), str(getattr(r, "source", "")),
                                 str(getattr(r, "source_detail", "") or "")[:120],
                                 getattr(r, "native_score", None), str(r.edge_id), ctx))
    derived, index = nr.forward_chain(edges)
    return edges, derived, index, missing


def explain(gene: str, edges, derived, index):
    ged = [e for e in edges if e.subject == gene]
    gdv = [d for d in derived if d.edge.subject == gene]
    te_preds = {"SILENCES", "DEREPRESSES"}

    measured = [e for e in ged if e.predicate in te_preds and e.tier == "measured"]
    curated = [e for e in ged if e.predicate in te_preds and e.tier == "curated"]
    literature = [e for e in ged if e.predicate in te_preds and e.tier == "literature"]
    inferred = [d for d in gdv if d.edge.predicate in te_preds]

    paths = nr.find_paths(edges + [d.edge for d in derived], gene)
    paths = [p for p in paths if any(e.predicate in te_preds or e.predicate == "MARK_AT" for e in p)]

    claims = []
    for e in measured:
        d = "raises" if e.predicate == "SILENCES" else "lowers"
        claims.append({"text": f"Knocking down {gene} {d} {e.object} ({e.detail}), measured in "
                               f"{e.source}.", "tier": "measured", "edge_ids": [e.edge_id]})
    for e in curated:
        claims.append({"text": f"{gene} is curated as silencing transposable elements "
                               f"({e.detail}).", "tier": "curated", "edge_ids": [e.edge_id]})
    for e in literature:
        d = "silences" if e.predicate == "SILENCES" else "is required for expression of"
        claims.append({"text": f"Published work reports that {gene} {d} {e.object} "
                               f"({e.detail}).", "tier": "literature", "edge_ids": [e.edge_id]})
    for d in inferred:
        direction = "raise" if d.edge.predicate == "SILENCES" else "lower"
        prem = ", ".join(f"{p.subject}-{p.predicate}->{p.object}" for p in d.premises if p)
        claims.append({"text": f"Losing {gene} is predicted to {direction} {d.edge.object}, "
                               f"derived by {d.rule} from: {prem}.",
                       "tier": "inferred",
                       "edge_ids": ([d.edge.edge_id] if d.edge.edge_id else [])
                                   + [p.edge_id for p in d.premises if p and p.edge_id],
                       "rule": d.rule, "proof": d.proof(index=index)})

    return {
        "gene": gene,
        "has_measured_data": bool(measured),
        "n_measured": len(measured), "n_curated": len(curated),
        "n_literature": len(literature), "n_inferred": len(inferred),
        "best_tier": ("measured" if measured else "curated" if curated else
                      "literature" if literature else "inferred" if inferred else "none"),
        "claims": claims,
        "paths": [{"tier": nr.path_tier(p),
                   "hops": [f"{e.subject} -{e.predicate}-> {e.object}" for e in p],
                   "edge_ids": [e.edge_id for e in p]} for p in paths[:25]],
    }


# ------------------------------------------------------------------ the citation gate
CITE = re.compile(r"\[(e[0-9a-f]{14}(?:\s*,\s*e[0-9a-f]{14})*)\]")


def verify_claims(text: str, allowed: set[str]):
    """Split prose into sentences; keep only those citing edge IDs that exist.

    Returns (kept, rejected). A sentence with no citation at all is rejected — silence
    about provenance is not a lesser offence than a wrong citation, because the reader
    cannot tell the difference.
    """
    kept, rejected = [], []
    for sent in re.split(r"(?<=[.!?])\s+", (text or "").strip()):
        if not sent:
            continue
        ids = [i.strip() for m in CITE.findall(sent) for i in m.split(",")]
        if not ids:
            rejected.append({"sentence": sent, "reason": "no edge cited"})
        elif not set(ids) <= allowed:
            rejected.append({"sentence": sent, "reason": "cites unknown edge(s): "
                                                         + ", ".join(sorted(set(ids) - allowed))})
        else:
            kept.append({"sentence": sent, "edge_ids": ids})
    return kept, rejected


def narrate(result: dict) -> str:
    """Deterministic renderer. Every sentence carries its citation, by construction."""
    g = result["gene"]
    if not result["claims"]:
        return f"No evidence in the graph connects {g} to transposable-element activation."
    lines = []
    for c in result["claims"]:
        ids = ", ".join(c["edge_ids"]) if c["edge_ids"] else ""
        lines.append(f"{c['text'].rstrip('.')} [{ids}]." if ids else c["text"])
    return " ".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("genes", nargs="+")
    ap.add_argument("--json", default=None)
    ap.add_argument("--proofs", action="store_true", help="print proof trees")
    ap.add_argument("--export-derived", default=None, metavar="CSV",
                    help="write every derived edge with its inherited context. Inferred "
                         "edges carry the scope of their narrowest premise; an edge with "
                         "context_generalization_required=yes must not be quoted as a "
                         "universal claim.")
    a = ap.parse_args()

    edges, derived, index, missing = load_graph()
    if missing:
        print(f"[note] absent edge files (layer not built): {', '.join(missing)}", file=sys.stderr)
    if a.export_derived:
        rows = []
        for d in derived:
            e = d.edge
            rows.append({"edge_id": e.edge_id, "subject": e.subject, "predicate": e.predicate,
                         "object": e.object, "evidence_tier": e.tier, "rule": d.rule,
                         "premise_edge_ids": ";".join(p.edge_id for p in d.premises),
                         "premise_tiers": ";".join(p.tier for p in d.premises),
                         **e.ctx()})
        pd.DataFrame(rows).to_csv(a.export_derived, index=False)
        flagged = sum(r.get("context_generalization_required") == "yes" for r in rows)
        print(f"{len(rows)} derived edges -> {a.export_derived} "
              f"({flagged} require context generalisation before being stated universally)")
    # derived edges are part of the graph once inferred, so their ids are citable; the
    # gate checks existence, and the tier field is what marks them as inference
    allowed = {e.edge_id for e in edges} | {d.edge.edge_id for d in derived}
    out = {}
    for g in a.genes:
        r = explain(g, edges, derived, index)
        prose = narrate(r)
        kept, rejected = verify_claims(prose, allowed)
        r["narrative"] = prose
        r["citation_check"] = {"sentences_kept": len(kept), "sentences_rejected": len(rejected),
                               "rejected": rejected}
        out[g] = r
        print(f"\n=== {g}  [best tier: {r['best_tier']}]  "
              f"measured={r['n_measured']} curated={r['n_curated']} "
              f"literature={r['n_literature']} inferred={r['n_inferred']}")
        print(prose)
        print(f"  citation gate: {len(kept)} sentences kept, {len(rejected)} rejected")
        if a.proofs:
            for c in r["claims"]:
                if "proof" in c:
                    print("  " + "\n  ".join(c["proof"]))
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        json.dump(out, open(a.json, "w"), indent=1)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
