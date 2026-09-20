#!/usr/bin/env python3
"""
build_panel_reference.py — make a gene set measurable without indexing the whole genome.

The problem this solves
-----------------------
The TE arm of this project needs a big reference, because transposable elements are
dispersed and you cannot count a subfamily you did not index. The inflammation arm does
not: it needs ~1000 specific gene bodies. On a chr1+chr19 reference only ~17% of the GO
type-I interferon set is present and every canonical sensor except IRF3 is missing, so
any "no interferon response" result describes the chromosome selection, not the biology.

Rather than index 3.1 Gb to rescue 60 Mb of signal, this script splices the missing gene
loci into the existing reference as extra contigs, carrying their real GENCODE exon
structure across so counting stays exonic and comparable to the chromosomes already there.

    # 1. which genes are missing, and how big is the panel?
    python src/build_panel_reference.py spec  --gtf refs/gencode.v44.gtf \
        --in-scope chr1,chr19 --outdir data/graph

    # 2. fetch them and write the contigs
    python src/build_panel_reference.py build --gtf refs/gencode.v44.gtf \
        --spec data/graph/panel_spec.csv --outdir refs

What it is honest about
-----------------------
* A panel measures the genes you name. It cannot discover a pathway you did not
  anticipate — unlike a genome-wide run, which can.
* Isolated contigs are a decoy surface: a read whose true origin is still absent from the
  reference may now land on a panel gene. Two things contain this. First, paralogue
  families are panelled together (OAS1/2/3, IFIT1/2/3/5, MX1/2, APOBEC3*), so within-family
  reads compete rather than collapsing onto one member. Second, and mainly, every
  comparison is contrast-internal: knockdown and control are aligned to the identical
  reference, so a constant mismapping bias cancels in the log2 fold change. Run
  `check_reference_perturbation` before believing any of it.
* TEs are deliberately NOT annotated inside panel contigs. The TE feature set stays exactly
  what it was on chr1+chr19, which is what makes the perturbation control interpretable.
* Neighbouring genes that fall inside a padded window ARE annotated, so their reads are
  attributed to them instead of leaking into the panel gene they sit next to.
"""
from __future__ import annotations
import argparse, re, sys, time
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

ATTR = re.compile(r'(\S+) "([^"]*)"')
ENSEMBL = "https://rest.ensembl.org/sequence/region/human"
QUICKGO = "https://www.ebi.ac.uk/QuickGO/services/annotation/search"

DEFAULT_SETS = {
    "IFN_typeI": "GO:0034340", "IFN_typeII": "GO:0034341",
    "defense_virus": "GO:0051607", "inflammatory": "GO:0006954",
    "senescence": "GO:0090398", "NFkB": "GO:0038061",
}
# Canonical sensing / effector / SASP axis, listed explicitly so a GO curation gap cannot
# silently drop cGAS or STING from the panel.
CORE_AXIS = """CGAS STING1 IFIH1 RIGI MAVS TBK1 IKBKE IRF3 IRF7 IRF9 STAT1 STAT2 JAK1 TYK2
ISG15 IFI6 IFI27 IFI44 IFI44L IFIT1 IFIT2 IFIT3 IFIT5 OAS1 OAS2 OAS3 OASL MX1 MX2 ZBP1
EIF2AK2 DDX60 RSAD2 USP18 BST2 XAF1 HERC5 HERC6 CMPK2 EPSTI1 SIGLEC1 LY6E PARP9 DTX3L ADAR
TREX1 SAMHD1 IFNB1 IFNA1 IFNAR1 IFNAR2 IFNL1 TNF IL6 IL1A IL1B CXCL8 CXCL10 CXCL9 CXCL11
CCL5 NFKB1 NFKB2 RELA RELB TLR3 TLR7 TLR9 TICAM1 MYD88 NLRP3 CASP1 GSDMD AIM2 PYCARD CDKN1A
CDKN2A TP53 LMNB1 SERPINE1 GLB1 IGFBP7 MMP3 TNFRSF1A""".split()


# --------------------------------------------------------------------------- annotation
def read_gencode_genes(gtf: Path) -> dict:
    """symbol -> locus. GENCODE attribute order is gene_id, gene_type, gene_name; a regex
    that assumes id/name/type matches nothing and yields an empty map."""
    out = {}
    with open(gtf) as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.split("\t", 9)
            if len(f) < 9 or f[2] != "gene":
                continue
            d = dict(ATTR.findall(f[8]))
            nm = d.get("gene_name")
            if not nm:
                continue
            span = int(f[4]) - int(f[3])
            prev = out.get(nm)
            if prev is None or span > prev["end"] - prev["start"]:
                out[nm] = dict(symbol=nm, gene_id=d["gene_id"], chrom=f[0],
                               start=int(f[3]), end=int(f[4]), strand=f[6],
                               gene_type=d.get("gene_type", ""))
    return out


def read_exons(gtf: Path, want_chroms: set) -> dict:
    """chrom -> list of (start, end, strand, gene_id, gene_name, transcript_id)."""
    ex = defaultdict(list)
    with open(gtf) as fh:
        for line in fh:
            if line[0] == "#":
                continue
            f = line.split("\t", 9)
            if len(f) < 9 or f[2] != "exon" or f[0] not in want_chroms:
                continue
            d = dict(ATTR.findall(f[8]))
            ex[f[0]].append((int(f[3]), int(f[4]), f[6], d.get("gene_id", ""),
                             d.get("gene_name", ""), d.get("transcript_id", "")))
    for c in ex:
        ex[c].sort()
    return ex


# ------------------------------------------------------------------------------ QuickGO
def quickgo_symbols(go_id: str, max_pages: int = 25) -> set:
    s, syms, page = requests.Session(), set(), 1
    s.headers.update({"Accept": "application/json"})
    while page <= max_pages:
        r = s.get(QUICKGO, params={"goId": go_id, "goUsage": "descendants",
                                   "goUsageRelationships": "is_a,part_of,regulates",
                                   "taxonId": 9606, "limit": 200, "page": page,
                                   "geneProductType": "protein"}, timeout=90)
        if not r.ok:
            break
        j = r.json()
        syms.update(a["symbol"] for a in j.get("results", []) if a.get("symbol"))
        if page >= (j.get("pageInfo") or {}).get("total", 1):
            break
        page += 1
    return syms


def resolve_aliases(symbols, known) -> dict:
    """QuickGO returns UniProt accessions for isoform-level annotations. Map what we can
    back onto GENCODE symbols; the rest are not genes and are dropped."""
    symbols = [s for s in symbols if s not in known]
    if not symbols:
        return {}
    out = {}
    for i in range(0, len(symbols), 500):
        chunk = symbols[i:i + 500]
        r = requests.post("https://mygene.info/v3/query",
                          data={"q": ",".join(chunk), "scopes": "symbol,alias,uniprot,ensemblgene",
                                "fields": "symbol", "species": "human"}, timeout=120)
        if not r.ok:
            continue
        for h in r.json():
            q, s = h.get("query"), h.get("symbol")
            if s and s in known:
                out[q] = s
    return out


# --------------------------------------------------------------------------------- spec
def cmd_spec(a):
    gtf = Path(a.gtf)
    in_scope = set(a.in_scope.split(","))
    genes = read_gencode_genes(gtf)
    sets = {k: quickgo_symbols(v) for k, v in DEFAULT_SETS.items()}
    sets["core_axis"] = set(CORE_AXIS)
    alias = resolve_aliases(sorted(set().union(*sets.values())), genes)
    sets = {k: {alias.get(s, s) for s in v} for k, v in sets.items()}

    rows = []
    for s in sorted(set().union(*sets.values())):
        memb = ";".join(k for k, v in sets.items() if s in v)
        g = genes.get(s)
        if g is None:
            rows.append(dict(symbol=s, gene_id="", chrom="", start=0, end=0, strand="",
                             gene_type="", sets=memb, status="unresolved_accession"))
            continue
        st = ("in_scope" if g["chrom"] in in_scope else
              "off_scope" if re.fullmatch(r"chr[0-9XY]+", g["chrom"]) else "nonprimary")
        rows.append(dict(**g, sets=memb, status=st))
    spec = pd.DataFrame(rows)
    spec["span_kb"] = (spec.end - spec.start) / 1e3

    cov = pd.DataFrame([dict(
        gene_set=k, n_total=len(v),
        n_in_scope=int(spec[spec.symbol.isin(v)].status.eq("in_scope").sum()),
        n_off_scope=int(spec[spec.symbol.isin(v)].status.eq("off_scope").sum()),
        n_unresolved=int(spec[spec.symbol.isin(v)].status
                         .isin(["unresolved_accession", "nonprimary"]).sum()))
        for k, v in sets.items()])
    cov["coverage_before"] = (cov.n_in_scope / (cov.n_in_scope + cov.n_off_scope)).round(3)

    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    spec.to_csv(out / "panel_spec.csv", index=False)
    cov.to_csv(out / "panel_coverage_before.csv", index=False)
    off = spec[spec.status == "off_scope"]
    print(cov.to_string(index=False))
    print(f"\npanel: {len(off)} genes, {(off.span_kb.sum() + len(off) * 2 * a.pad / 1e3) / 1e3:.1f} Mb padded")


# -------------------------------------------------------------------------------- build
def fetch_regions(regions, batch_bp=4_000_000, batch_n=50, retries=4):
    """POST to Ensembl in batches. Returns {region_string: sequence}."""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
    seqs, batch, bp = {}, [], 0
    def flush(b):
        if not b:
            return
        for attempt in range(retries):
            r = s.post(ENSEMBL, json={"regions": b}, timeout=300)
            if r.ok:
                for obj in r.json():
                    key = obj.get("query") or obj.get("id")
                    seqs[key] = obj["seq"]
                return
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Ensembl {r.status_code}: {r.text[:300]}")
        raise RuntimeError("Ensembl retries exhausted")
    for reg in regions:
        c, rest = reg.split(":", 1)
        lo, hi = rest.split(":")[0].split("..")
        size = int(hi) - int(lo)
        if batch and (len(batch) >= batch_n or bp + size > batch_bp):
            flush(batch); batch, bp = [], 0
        batch.append(reg); bp += size
    flush(batch)
    return seqs


def merge_windows(off: pd.DataFrame, pad: int) -> pd.DataFrame:
    """Padded windows around clustered gene families overlap — IFIT1/3/5, OAS1/2/3,
    IFITM1/2/3, the APOBEC3 and IFNA clusters. Emitting them as separate contigs would put
    the same genomic sequence in the reference twice and turn uniquely-mapping reads into
    artificial multi-mappers, right at the genes the panel exists to measure. Merge any
    overlapping windows into one contig instead."""
    recs = []
    for chrom, g in off.groupby("chrom"):
        iv = sorted(zip((g.start - pad).clip(lower=1), g.end + pad, g.symbol))
        cur_s, cur_e, members = iv[0][0], iv[0][1], [iv[0][2]]
        for s, e, sym in iv[1:]:
            if s <= cur_e:
                cur_e = max(cur_e, e); members.append(sym)
            else:
                recs.append((chrom, cur_s, cur_e, members)); cur_s, cur_e, members = s, e, [sym]
        recs.append((chrom, cur_s, cur_e, members))
    return pd.DataFrame([dict(chrom=c, win_start=int(s), win_end=int(e),
                              contig=f"panel_{c}_{int(s)}_{int(e)}",
                              members=";".join(sorted(m)), n_members=len(m),
                              region=f"{c[3:]}:{int(s)}..{int(e)}:1")
                         for c, s, e, m in recs])


def cmd_build(a):
    spec = pd.read_csv(a.spec)
    off = spec[spec.status == "off_scope"].copy().sort_values(["chrom", "start"])
    win = merge_windows(off, a.pad)
    n_merged = int((win.n_members > 1).sum())
    print(f"{len(off)} panel genes -> {len(win)} contigs "
          f"({n_merged} contigs hold a merged gene cluster)", flush=True)

    print(f"fetching {len(win)} regions from Ensembl ...", flush=True)
    seqs = fetch_regions(win.region.tolist())
    missing = [r for r in win.region if r not in seqs]
    if missing:
        raise SystemExit(f"Ensembl returned no sequence for {len(missing)} regions, e.g. {missing[:3]}")

    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    fa, n_bp = out / "panel.fa", 0
    with open(fa, "w") as fh:
        for _, r in win.iterrows():
            s = seqs[r.region]
            want = r.win_end - r.win_start + 1
            assert len(s) == want, f"{r.contig}: got {len(s)} bp, expected {want}"
            n_bp += len(s)
            fh.write(f">{r.contig}\n")
            for i in range(0, len(s), 60):
                fh.write(s[i:i + 60] + "\n")

    # Exon structure shifted into contig coordinates. Neighbours that fall inside a window
    # are annotated too, so their reads are attributed to them rather than leaking into the
    # panel target they sit beside.
    targets = set(off.symbol)
    exons = read_exons(Path(a.gtf), set(win.chrom))
    rows, with_exons = [], set()
    for _, r in win.iterrows():
        shift = r.win_start - 1
        for (es, ee, strand, gid, gname, tid) in exons[r.chrom]:
            if ee < r.win_start or es > r.win_end:
                continue
            cs, ce = max(es, r.win_start) - shift, min(ee, r.win_end) - shift
            if ce < cs:
                continue
            own = gname in targets
            if own:
                with_exons.add(gname)
            rows.append((r.contig, "panel", "exon", cs, ce, ".", strand, ".",
                         f'gene_id "{gname or gid}"; transcript_id "{tid or gid}"; '
                         f'gene_name "{gname}"; source_locus "{r.chrom}:{es}-{ee}"; '
                         f'feature_source "{"panel_target" if own else "panel_neighbour"}";'))
    gtf_out = out / "panel.gtf"
    with open(gtf_out, "w") as fh:
        for t in rows:
            fh.write("\t".join(map(str, t)) + "\n")

    win.drop(columns=["region"]).to_csv(out / "panel_contigs.csv", index=False)
    no_exon = sorted(targets - with_exons)
    print(f"{fa}: {len(win)} contigs, {n_bp/1e6:.1f} Mb")
    print(f"{gtf_out}: {len(rows)} exon rows, {len(with_exons)}/{len(targets)} targets with exons")
    if no_exon:
        print(f"WARNING {len(no_exon)} panel genes have no exon in window: {no_exon[:10]}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("spec", help="which signature genes are outside the reference scope")
    s.add_argument("--gtf", default="refs/gencode.v44.gtf")
    s.add_argument("--in-scope", default="chr1,chr19")
    s.add_argument("--outdir", default="data/graph")
    s.add_argument("--pad", type=int, default=5000)
    s.set_defaults(func=cmd_spec)
    b = sub.add_parser("build", help="fetch panel sequence and write contigs + GTF")
    b.add_argument("--gtf", default="refs/gencode.v44.gtf")
    b.add_argument("--spec", default="data/graph/panel_spec.csv")
    b.add_argument("--outdir", default="refs")
    b.add_argument("--pad", type=int, default=5000)
    b.set_defaults(func=cmd_build)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
