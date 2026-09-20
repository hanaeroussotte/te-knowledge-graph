#!/usr/bin/env python3
"""
build_graph.py — build the curated and mechanism edge layers of the TE knowledge graph.

Uses public REST APIs directly (no platform connectors), so the repository is self-contained
and reproducible anywhere with network access:

    mygene.info   GO term  -> human genes                 (the TE-regulator seed)
    QuickGO/OLS   GO term  -> descendant terms            (walk the TE-silencing branch)
    STRING v12    gene set -> protein interactions
    Reactome      gene set -> pathway membership
    ComplexPortal UniProt  -> curated complex membership  (optional; --no-complexportal skips)

    python src/build_graph.py --outdir data/graph

Output: nodes.csv, edges_curated.csv, edges_mechanism.csv, te_regulator_seed.csv.

Every edge carries the mandatory provenance block defined in docs/schema.md. An edge that
cannot fill it is dropped rather than downgraded.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, sys, time
from pathlib import Path
import pandas as pd
import requests

TODAY = datetime.date.today().isoformat()
S = requests.Session()
S.headers.update({"Accept": "application/json", "User-Agent": "te-knowledge-graph/1.0"})

# --- GO branches that define "this gene acts on transposable elements" -------------------
SEED_ROOTS = {
    "GO:0010526": "transposable element silencing",
    "GO:0032196": "transposition",
    "GO:0031507": "heterochromatin formation",
    "GO:0006346": "DNA methylation-dependent constitutive heterochromatin formation",
}
# --- chromatin marks, from GO *molecular function*. This layer is what lets genes with no
#     direct TE annotation (TET2, for one) enter the graph at all.
MARK_WRITERS = {
    "H3K9me3": ["GO:0046974", "GO:0140949"],
    "H3K27me3": ["GO:0046976", "GO:0140951"],
    "5mC": ["GO:0003886"],
}
MARK_ERASERS = {
    "H3K9me3": ["GO:0140684", "GO:0032454"],
    "H3K27me3": ["GO:0071558"],
    # GO:0070579 (methylcytosine dioxygenase) returns exactly TET1/2/3. The broader parent
    # term also captures ALKBH/FTO, which act on other substrates — do not use it here.
    "5mC": ["GO:0070579"],
}
SENSING_AXIS = ["CGAS", "STING1", "IFIH1", "DDX58", "MAVS", "TBK1", "IRF3", "IRF7", "IRF9",
                "STAT1", "STAT2", "ISG15", "IFIT1", "IFIT3", "OAS1", "OASL", "MX1", "ZBP1",
                "EIF2AK2", "ADAR", "TREX1", "SAMHD1", "IFNB1", "TNF", "NFKB1", "RELA",
                "IL6", "CXCL10"]
EXTRA_GENES = ["DNMT3A", "TET2", "ASXL1", "JAK2", "TP53", "PPM1D", "SF3B1", "SRSF2"]

COLS = ["edge_id", "subject", "subject_type", "predicate", "object", "object_type",
        "evidence_tier", "source", "source_detail", "native_score", "native_score_type",
        "statistic", "retrieved"]


def get(url, **kw):
    for attempt in range(4):
        try:
            r = S.get(url, timeout=120, **kw)
            if r.ok:
                return r
            if r.status_code in (429, 500, 502, 503):
                time.sleep(3 * (attempt + 1)); continue
            return None
        except requests.RequestException:
            time.sleep(3 * (attempt + 1))
    return None


# ----------------------------------------------------------------- ontology / gene lookup
def go_descendants(go_id: str) -> dict[str, str]:
    """All descendant terms of a GO term, via the EBI OLS4 / QuickGO ontology service."""
    out = {}
    r = get(f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_id}/descendants",
            params={"relations": "is_a,part_of,regulates"})
    if r:
        for res in r.json().get("results", []):
            for d in res.get("descendants", []) or []:
                out[d] = None
    lab = get(f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_id}")
    if lab:
        for res in lab.json().get("results", []):
            out[res["id"]] = res.get("name")
    # hydrate labels in one batch
    ids = [i for i, v in out.items() if v is None]
    for i in range(0, len(ids), 50):
        rr = get("https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/"
                 + ",".join(ids[i:i + 50]))
        if rr:
            for res in rr.json().get("results", []):
                out[res["id"]] = res.get("name")
    return {k: v for k, v in out.items() if v}


def genes_for_go(go_id: str) -> dict[str, str]:
    """Human genes annotated to a GO term. size=1000 — the API default of 10 silently
    truncates, which is easy to miss and quietly halves your seed set."""
    # A bare "GO:0010526" searches every GO field (BP/MF/CC). The field-qualified forms
    # (go:..., go.BP.id:"...") silently return zero — do not "improve" this.
    r = get("https://mygene.info/v3/query",
            params={"q": go_id, "species": "human",
                    "fields": "symbol,ensembl.gene", "size": 1000})
    if not r:
        return {}
    out = {}
    for h in r.json().get("hits", []):
        e = h.get("ensembl")
        if isinstance(e, list):
            e = e[0].get("gene") if e else None
        elif isinstance(e, dict):
            e = e.get("gene")
        if h.get("symbol"):
            out.setdefault(h["symbol"], e)
    return out


def uniprot_for(symbols: list[str]) -> dict[str, str]:
    out = {}
    for i in range(0, len(symbols), 200):
        r = S.post("https://mygene.info/v3/query",
                   data={"q": ",".join(symbols[i:i + 200]), "scopes": "symbol",
                         "species": "human", "fields": "symbol,uniprot.Swiss-Prot"}, timeout=120)
        if not r.ok:
            continue
        for h in r.json():
            up = (h.get("uniprot") or {}).get("Swiss-Prot")
            if isinstance(up, list):
                up = up[0]
            if h.get("symbol") and up:
                out.setdefault(h["symbol"], up)
    return out


# ------------------------------------------------------------------------ evidence sources
def string_network(symbols: list[str], required_score: int = 700) -> list[dict]:
    r = S.post("https://string-db.org/api/json/network",
               data={"identifiers": "\r".join(symbols), "species": 9606,
                     "required_score": required_score, "caller_identity": "te-kg"}, timeout=180)
    if not r.ok:
        return []
    seen, out = set(), []
    for e in r.json():
        a, b = e.get("preferredName_A"), e.get("preferredName_B")
        if not a or not b:
            continue
        k = tuple(sorted((a, b)))
        if k in seen:
            continue
        seen.add(k)
        out.append({"a": a, "b": b, "score": float(e.get("score", 0))})
    return out


def reactome_pathways(symbols: list[str], max_pathways: int = 400
                      ) -> dict[str, list[tuple[str, str]]]:
    """gene -> [(pathway stId, name)].

    Two calls are needed. The overrepresentation response lists pathways but reports
    `entities.found` as a COUNT, not a membership list; the per-pathway members come from
    the token endpoint.
    """
    r = S.post("https://reactome.org/AnalysisService/identifiers/projection",
               params={"interactors": "false", "pageSize": max_pathways, "page": 1},
               data="\n".join(symbols),
               headers={"Content-Type": "text/plain"}, timeout=180)
    if not r.ok:
        return {}
    j = r.json()
    token = (j.get("summary") or {}).get("token")
    pathways = [(p.get("stId"), p.get("name")) for p in j.get("pathways", []) if p.get("stId")]
    if not token:
        return {}
    res: dict[str, list[tuple[str, str]]] = {}
    for st, name in pathways:
        rr = get(f"https://reactome.org/AnalysisService/token/{token}/found/all/{st}",
                 params={"pageSize": 1000, "page": 1, "resource": "TOTAL"})
        if not rr:
            continue
        payload = rr.json()
        if isinstance(payload, list):
            payload = payload[0] if payload else {}
        for ent in payload.get("entities", []) or []:
            sym = ent.get("id")
            if sym:
                res.setdefault(sym, []).append((st, name))
    return res


def complexportal(uniprot: dict[str, str]) -> dict[str, list[dict]]:
    out = {}
    for sym, acc in uniprot.items():
        r = get(f"https://www.ebi.ac.uk/intact/complex-ws/search/{acc}",
                params={"format": "json"})
        if not r:
            continue
        try:
            elems = r.json().get("elements", []) or []
        except Exception:
            continue
        hits = [{"complex_ac": e.get("complexAC"), "name": e.get("complexName"),
                 "predicted": bool(e.get("predictedComplex"))}
                for e in elems if e.get("complexAC")]
        if hits:
            out[sym] = hits
    return out


# ------------------------------------------------------------------------------- assembly
class Graph:
    def __init__(self):
        self.nodes, self.edges = {}, []

    def node(self, nid, ntype, label=None):
        self.nodes.setdefault(nid, {"node_id": nid, "node_type": ntype, "label": label or nid})

    def edge(self, s, st, p, o, ot, tier, source, detail, score=None, stype=None, stat=None):
        self.node(s, st); self.node(o, ot)
        eid = "e" + hashlib.sha1(f"{s}|{p}|{o}|{source}".encode()).hexdigest()[:14]
        self.edges.append(dict(zip(COLS, [eid, s, st, p, o, ot, tier, source, detail,
                                          score, stype, stat, TODAY])))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default="data/graph")
    ap.add_argument("--string-score", type=int, default=700)
    ap.add_argument("--no-complexportal", action="store_true")
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    G = Graph()

    # 1. TE-regulator seed from the GO transposition / silencing branches
    terms = {}
    for root, lbl in SEED_ROOTS.items():
        terms.update(go_descendants(root) or {root: lbl})
    print(f"GO terms in seed branches: {len(terms)}", file=sys.stderr)

    seed_rows = []
    for go_id, lbl in terms.items():
        for sym, ens in genes_for_go(go_id).items():
            seed_rows.append({"symbol": sym, "ensembl": ens, "go_id": go_id, "go_label": lbl})
    seed = pd.DataFrame(seed_rows).drop_duplicates()
    if seed.empty:
        sys.exit("no seed genes returned — check network access to mygene.info")
    seed.to_csv(out / "te_regulator_seed.csv", index=False)
    seed_genes = sorted(seed.symbol.unique())
    print(f"seed genes: {len(seed_genes)}", file=sys.stderr)

    TE_SIL = {g for g, l in terms.items() if "transposable element silencing" in (l or "").lower()}
    G.node("TE:UNSPECIFIED", "TEFamily", "transposable elements (family unspecified)")
    for r in seed.itertuples():
        G.node(r.go_id, "GOTerm", r.go_label)
        G.edge(r.symbol, "Gene", "ANNOTATED_TO", r.go_id, "GOTerm", "curated",
               "GO (mygene.info)", r.go_label)
        if r.go_id in TE_SIL:
            G.edge(r.symbol, "Gene", "SILENCES", "TE:UNSPECIFIED", "TEFamily", "curated",
                   "GO (mygene.info)", f"{r.go_id} {r.go_label}")

    genes = sorted(set(seed_genes) | set(SENSING_AXIS) | set(EXTRA_GENES))

    # 2. STRING interactions
    for e in string_network(genes, a.string_score):
        G.edge(e["a"], "Gene", "INTERACTS_WITH", e["b"], "Gene", "curated", "STRING v12.0",
               f"required_score>={a.string_score}", e["score"], "STRING combined score (0-1)")

    # 3. Reactome pathway membership
    for sym, pws in (reactome_pathways(genes) or {}).items():
        for st, name in pws:
            G.node(st, "Pathway", name)
            G.edge(sym, "Gene", "PARTICIPATES_IN", st, "Pathway", "curated", "Reactome", name)

    # 4. Complex Portal membership — predicted complexes are tiered `predicted`, and the
    #    rule engine refuses to propagate through them.
    if not a.no_complexportal:
        up = uniprot_for(genes)
        for sym, hits in complexportal(up).items():
            for h in hits:
                G.node(h["complex_ac"], "Complex", h["name"])
                G.edge(sym, "Gene", "MEMBER_OF", h["complex_ac"], "Complex",
                       "predicted" if h["predicted"] else "curated", "Complex Portal", h["name"])

    curated = pd.DataFrame(G.edges, columns=COLS).drop_duplicates("edge_id")
    curated.to_csv(out / "edges_curated.csv", index=False)

    # 5. Chromatin-mark layer, from GO molecular function
    M = Graph()
    for mark, gos in MARK_WRITERS.items():
        for go_id in gos:
            for sym in genes_for_go(go_id):
                M.edge(sym, "Gene", "DEPOSITS_MARK", mark, "ChromatinMark", "curated",
                       "GO molecular function", go_id)
    for mark, gos in MARK_ERASERS.items():
        for go_id in gos:
            for sym in genes_for_go(go_id):
                M.edge(sym, "Gene", "ERASES_MARK", mark, "ChromatinMark", "curated",
                       "GO molecular function", go_id)
    mech = pd.DataFrame(M.edges, columns=COLS).drop_duplicates("edge_id")
    mech.to_csv(out / "edges_mechanism.csv", index=False)

    allnodes = {**G.nodes, **M.nodes}
    pd.DataFrame(allnodes.values()).to_csv(out / "nodes.csv", index=False)

    print(f"\nnodes            : {len(allnodes):,}")
    print(f"curated edges    : {len(curated):,}")
    print(f"mechanism edges  : {len(mech):,}")
    print(curated.groupby(['predicate', 'evidence_tier']).size().to_string())


if __name__ == "__main__":
    main()
