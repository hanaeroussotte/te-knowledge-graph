#!/usr/bin/env python3
"""
annotate_tractability.py — is anything in the graph druggable?

Takes every gene carrying a TE edge (any tier) plus the innate-sensing axis, and annotates it
with Open Targets tractability buckets and ChEMBL mechanisms of action.

    python src/annotate_tractability.py --graph data/graph --results results \
        --out results/targets_tractability.csv

Five classes, most to least actionable:
    1  approved drug exists
    2  clinical-stage
    3  structurally tractable, no clinical programme   <- the interesting bucket
    4  druggable family / antibody-accessible only
    5  no tractability evidence

Read class 3 carefully. "No clinical programme" frequently means a programme was attempted and
abandoned, not that an opportunity is sitting unclaimed. The class is a prompt to go and check,
not a conclusion.
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
import pandas as pd
import requests

S = requests.Session()
S.headers.update({"Accept": "application/json", "User-Agent": "te-knowledge-graph/1.0"})
OT = "https://api.platform.opentargets.org/api/v4/graphql"
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"

# NB: the Open Targets Tractability type exposes label/modality/value. There is no `id`
# field — querying one returns HTTP 400 with no partial data.
Q = """query($ids:[String!]!){ targets(ensemblIds:$ids){
  id approvedSymbol
  tractability{ label modality value }
  drugAndClinicalCandidates{ count }
} }"""
SENSING = ["CGAS", "STING1", "IFIH1", "DDX58", "MAVS", "TBK1", "IRF3", "EIF2AK2", "ADAR", "TREX1"]
TE_PREDICATES = {"SILENCES", "DEREPRESSES"}


def ensembl_ids(symbols):
    out = {}
    for i in range(0, len(symbols), 200):
        r = S.post("https://mygene.info/v3/query",
                   data={"q": ",".join(symbols[i:i + 200]), "scopes": "symbol",
                         "species": "human", "fields": "symbol,ensembl.gene"}, timeout=120)
        if not r.ok:
            continue
        for h in r.json():
            e = h.get("ensembl")
            if isinstance(e, list):
                e = e[0].get("gene") if e else None
            elif isinstance(e, dict):
                e = e.get("gene")
            if h.get("symbol") and e:
                out.setdefault(h["symbol"], e)
    return out


def chembl_mechanisms(symbol):
    r = S.get(f"{CHEMBL}/target/search", params={"q": symbol, "format": "json", "limit": 5},
              timeout=90)
    if not r.ok:
        return {"target_chembl_id": None, "n_mechanisms": 0, "example_moa": ""}
    hits = [t for t in r.json().get("targets", [])
            if t.get("organism") == "Homo sapiens" and t.get("target_type") == "SINGLE PROTEIN"]
    if not hits:
        return {"target_chembl_id": None, "n_mechanisms": 0, "example_moa": ""}
    tid = hits[0]["target_chembl_id"]
    rm = S.get(f"{CHEMBL}/mechanism", params={"target_chembl_id": tid, "format": "json",
                                              "limit": 50}, timeout=90)
    mechs = rm.json().get("mechanisms", []) if rm.ok else []
    moa = sorted({f'{x.get("mechanism_of_action")} ({x.get("action_type")})' for x in mechs})[:2]
    return {"target_chembl_id": tid, "n_mechanisms": len(mechs), "example_moa": "; ".join(moa)}


def classify(tr, chem):
    sm_appr = tr.get("SM|Approved Drug", False)
    ab_appr = tr.get("AB|Approved Drug", False)
    clinical = any(tr.get(k, False) for k in
                   ["SM|Advanced Clinical", "SM|Phase 1 Clinical",
                    "AB|Advanced Clinical", "AB|Phase 1 Clinical"])
    structural = any(tr.get(k, False) for k in
                     ["SM|Structure with Ligand", "SM|High-Quality Ligand", "SM|High-Quality Pocket"])
    family = tr.get("SM|Druggable Family", False)
    ab_acc = tr.get("AB|UniProt loc high conf", False) or tr.get("AB|GO CC high conf", False)
    if sm_appr or ab_appr:
        return "1. approved drug exists"
    if clinical:
        return "2. clinical-stage"
    if structural:
        return "3. structurally tractable, no clinical programme"
    if family or ab_acc:
        return "4. druggable family / antibody-accessible only"
    return "5. no tractability evidence"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--graph", default="data/graph")
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="results/targets_tractability.csv")
    ap.add_argument("--skip-chembl", action="store_true")
    a = ap.parse_args()

    roles = {}
    for d in [Path(a.graph), Path(a.results)]:
        for f in sorted(d.glob("edges_*.csv")):
            df = pd.read_csv(f)
            for r in df[df.predicate.isin(TE_PREDICATES)].itertuples():
                roles.setdefault(str(r.subject), set()).add(str(r.evidence_tier))
    for s in SENSING:
        roles.setdefault(s, set()).add("sensing_axis")
    genes = sorted(g for g in roles if not g.startswith("CPX-"))
    if not genes:
        sys.exit("no genes with TE edges found — run build_graph.py and run_de.py first")
    print(f"annotating {len(genes)} targets", file=sys.stderr)

    ens = ensembl_ids(genes)
    r = S.post(OT, json={"query": Q, "variables": {"ids": sorted(set(ens.values()))}}, timeout=180)
    rows_ot = ((r.json().get("data") or {}).get("targets") or []) if r.ok else []
    if not rows_ot:
        sys.exit(f"Open Targets returned nothing: {r.text[:300] if r is not None else 'no response'}")

    rows = []
    for t in rows_ot:
        sym = t["approvedSymbol"]
        tr = {f'{x["modality"]}|{x["label"]}': x["value"] for x in (t.get("tractability") or [])}
        chem = ({"target_chembl_id": None, "n_mechanisms": 0, "example_moa": ""}
                if a.skip_chembl else chembl_mechanisms(sym))
        rows.append({"gene": sym, "ensembl": t["id"],
                     "graph_role": ";".join(sorted(roles.get(sym, []))),
                     "druggability_class": classify(tr, chem),
                     "sm_approved_drug": tr.get("SM|Approved Drug", False),
                     "sm_advanced_clinical": tr.get("SM|Advanced Clinical", False),
                     "sm_structure_with_ligand": tr.get("SM|Structure with Ligand", False),
                     "sm_high_quality_pocket": tr.get("SM|High-Quality Pocket", False),
                     "sm_druggable_family": tr.get("SM|Druggable Family", False),
                     "ab_approved_drug": tr.get("AB|Approved Drug", False),
                     "ot_known_drugs": (t.get("drugAndClinicalCandidates") or {}).get("count", 0),
                     **chem})
        time.sleep(0.05)
    df = pd.DataFrame(rows).sort_values(["druggability_class", "gene"])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.out, index=False)
    print(df.druggability_class.value_counts().sort_index().to_string())
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
