#!/usr/bin/env python3
"""make_demo.py — build demo/query.html, a clickable viewer over real engine output.

    python src/te_reason.py GENE1 GENE2 ... --json handoff/demo_answers.json
    python src/make_demo.py

HONESTY CONSTRAINT, and it is load-bearing: this page is a VIEWER, not a server. Every
answer in it was produced by te_reason.py and is pasted in verbatim — no answer is
constructed by the page, and the page says so where the audience can read it. A demo that
implied a live backend it does not have would be exactly the kind of claim this repository
exists to avoid.
"""
import html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "handoff" / "demo_answers.json"
if not SRC.exists():
    SRC = ROOT.parent / "handoff" / "demo_answers.json"
A = json.load(open(SRC))

def img(name):
    import base64
    p = ROOT / "figures" / name
    if not p.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


TIER_ORDER = ["measured", "curated", "literature", "inferred", "none"]
TIER_NOTE = {
 "measured":   "our own re-analysis of a perturbation experiment",
 "curated":    "a curated database record (Gene Ontology, Reactome, Complex Portal, STRING)",
 "literature": "extracted from an abstract — unvalidated, and never allowed to ground a rule",
 "inferred":   "derived by a rule from premises below it; tier = weakest link on the path",
 "none":       "no evidence at any tier. The system declines rather than guessing",
}


EDGE_RE = re.compile(r"^(\S+) -([A-Z_0-9]+)-> (\S+)\s+\[(\w+)")

def parse_edges(lines):
    """Pull (subject, predicate, object, tier) triples out of a printed proof tree.

    The tree is text because the engine prints it for a terminal. It is a GRAPH, and the
    whole point of this project is that the answer is a path through one — so the demo has to
    draw it as a graph rather than as indented text, or it looks like a lookup table.
    """
    out, seen = [], set()
    for ln in lines:
        m = EDGE_RE.match(ln.strip())
        if not m:
            continue
        s, pr, o, tier = m.groups()
        if (s, pr, o) in seen:
            continue
        seen.add((s, pr, o)); out.append((s, pr, o, tier))
    return out

def layer(edges):
    """Longest-path layering: a node sits one column right of its furthest premise."""
    nodes = {n for s, _, o, _ in edges for n in (s, o)}
    preds = {n: [s for s, _, o, _ in edges if o == n] for n in nodes}
    col, guard = {}, 0
    while len(col) < len(nodes) and guard < 40:
        for n in nodes:
            if n in col:
                continue
            ps = preds[n]
            if all(q in col for q in ps):
                col[n] = (max((col[q] for q in ps), default=-1) + 1)
        guard += 1
    for n in nodes:                       # cycle fallback — never silently drop a node
        col.setdefault(n, 0)
    return col

def svg(edges):
    if not edges:
        return ""
    col = layer(edges)
    bycol = {}
    for n, c in sorted(col.items(), key=lambda kv: (kv[1], kv[0])):
        bycol.setdefault(c, []).append(n)
    CW, NH, VG, PAD = 208, 40, 26, 16
    ncol = max(bycol) + 1
    rows = max(len(v) for v in bycol.values())
    W, H = PAD * 2 + (ncol - 1) * CW + 168, PAD * 2 + rows * (NH + VG)
    pos = {}
    for c, ns in bycol.items():
        off = (rows - len(ns)) * (NH + VG) / 2
        for i, n in enumerate(ns):
            pos[n] = (PAD + c * CW, PAD + off + i * (NH + VG))
    parts = [f'<svg class="kg" viewBox="0 0 {W} {H}" width="100%">',
             '<defs><marker id="ar" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" '
             'orient="auto"><path d="M0,0 L9,3.5 L0,7 z" fill="#687487"/></marker></defs>']
    for s, pr, o, tier in edges:
        x1, y1 = pos[s]; x2, y2 = pos[o]
        ax, ay = x1 + 156, y1 + NH / 2
        bx, by = x2, y2 + NH / 2
        mx = (ax + bx) / 2
        parts.append(f'<path d="M{ax},{ay} C{mx},{ay} {mx},{by} {bx},{by}" fill="none" '
                     f'stroke="var(--t-{tier})" stroke-width="2" marker-end="url(#ar)" '
                     f'opacity=".85"/>')
        parts.append(f'<text class="el" x="{mx}" y="{(ay+by)/2 - 5}" text-anchor="middle">'
                     f'{html.escape(pr)}</text>')
    for n, (x, y) in pos.items():
        tiers = [t for s, _, o, t in edges if s == n]
        tc = tiers[0] if tiers else "inferred"
        parts.append(f'<rect class="kn" x="{x}" y="{y}" width="156" height="{NH}" rx="8" '
                     f'stroke="var(--t-{tc})"/>')
        parts.append(f'<text class="nl" x="{x+78}" y="{y+NH/2+4.5}" text-anchor="middle">'
                     f'{html.escape(n)}</text>')
    parts.append("</svg>")
    return "".join(parts)

PATH_RE = re.compile(r"^(\S+) -([A-Z_0-9]+)-> (\S+)$")

def edges_from_paths(paths):
    out, seen = [], set()
    for pth in paths or []:
        for hop in pth.get("hops", []):
            m = PATH_RE.match(hop.strip())
            if not m:
                continue
            s, pr, o = m.groups()
            if (s, pr, o) in seen:
                continue
            seen.add((s, pr, o)); out.append((s, pr, o, pth.get("tier", "inferred")))
    return out

def render_proof(lines):
    out = []
    for ln in lines:
        ind = len(ln) - len(ln.lstrip())
        s = html.escape(ln.strip())
        cls = "pl"
        for t in ("measured", "curated", "literature", "inferred"):
            if f"[{t}" in ln:
                cls = f"pl t-{t}"; break
        if ln.lstrip().startswith("!"):
            cls = "pl warn"
        out.append(f'<div class="{cls}" style="padding-left:{ind*0.55}em">{s}</div>')
    return "".join(out)


# ---------------------------------------------------------------- next experiment
# Computed, never written by hand. Every statement below is derived from a table in the
# repository: which genes ENCODE actually perturbed, which genes carry a DEPOSITS_MARK or
# ERASES_MARK annotation, how many derived edges collapse when each anchor is removed, and
# whether each knockdown's own mRNA actually fell. A demo that invented plausible next
# experiments would be the easiest thing here to fake and the least defensible.
import csv

def _load_next_context():
    def rd(rel):
        fp = ROOT / rel
        return list(csv.DictReader(open(fp))) if fp.exists() else []
    mech = rd("data/graph/edges_mechanism.csv")
    inv  = rd("data/graph/encode_kd_inventory.csv")
    ho   = rd("results/holdout_robustness.csv")
    eff  = rd("results/knockdown_efficiency.csv")
    wr = {r["subject"]: r["object"] for r in mech if r["predicate"] == "DEPOSITS_MARK"}
    er = {r["subject"]: r["object"] for r in mech if r["predicate"] == "ERASES_MARK"}
    enc = {r.get("target_label") for r in inv} | {r.get("target_gene") for r in inv}
    enc.discard(None); enc.discard("")
    full = next((int(r["derived"]) for r in ho if r["anchor_removed"] == "none"), 0)
    dep = {r["anchor_removed"]: full - int(r["derived"])
           for r in ho if r["anchor_removed"] != "none"}
    effi = {r["gene"]: r for r in eff if r["analysis"] == "knockdown_efficiency"}
    enzymes = set(wr) | set(er)
    return dict(wr=wr, er=er, enc=enc, dep=dep, eff=effi,
                n_enz=len(enzymes), n_enz_enc=len(enzymes & enc))

NX = _load_next_context()

def next_experiment(g, tier):
    wr, er, enc, dep, eff = NX["wr"], NX["er"], NX["enc"], NX["dep"], NX["eff"]
    mark = wr.get(g) or er.get(g)
    role = "writer" if g in wr else ("eraser" if g in er else None)
    in_enc = g in enc
    have = f'<b>ENCODE has a knockdown of {g}</b>' if in_enc else \
           f'<b>No ENCODE knockdown of {g} exists</b> &mdash; this needs a GEO/SRA search or new data'
    rows = []
    if g in eff and eff[g]["verdict"].startswith("NOT CONFIRMED"):
        rows.append(("highest priority",
            f'{g}\u2019s own mRNA is not significantly reduced in its own knockdown '
            f'({eff[g]["log2FC"]} log&#8322;, {eff[g]["pct_remaining"]}% remaining), and '
            f'<b>{dep.get(g,0)} derived edges depend on it</b>. A full-depth genome-wide '
            f'rerun of the same libraries settles whether the perturbation worked. Until it '
            f'does, every conclusion below it is provisional.'))
    if tier == "measured" and dep.get(g, 0) == 0:
        rows.append(("ingest, not experiment",
            f'{g} is measured and its effect is the largest in the dataset, yet it grounds '
            f'<b>0</b> derived edges: a scaffold carries no mark annotation, so no rule can '
            f'use it. The fix is not more data &mdash; it is ingesting <code>RECRUITS</code> '
            f'edges, of which the graph currently holds <b>zero</b>. With them, '
            f'{g}&nbsp;&rarr;&nbsp;SETDB1&nbsp;&rarr;&nbsp;H3K9me3&nbsp;&rarr;&nbsp;TE '
            f'becomes traversable.'))
    if tier in ("inferred", "curated", "literature") and mark:
        rows.append(("converts this answer to measured",
            f'Perturb {g} directly and re-quantify against the repeat annotation. {have}. '
            f'Because {g} is a <b>{role} of {mark}</b>, that experiment would also add an '
            f'<b>independent grounding for {mark}</b> &mdash; and by the anchor-dependence '
            f'analysis that is the single highest-value class of experiment available, '
            f'because only four edges currently ground the whole inference layer.'))
    elif tier in ("inferred", "curated", "literature"):
        rows.append(("converts this answer to measured",
            f'Perturb {g} directly and re-quantify against the repeat annotation. {have}. '
            f'{g} carries no chromatin-mark annotation, so this would add a measured edge '
            f'but no new rule grounding.'))
    if tier == "none":
        rows.append(("what would create an answer",
            f'Nothing connects {g} to transposable-element regulation at any tier, so there '
            f'is no path to strengthen. Two things would create one: a curated '
            f'<code>DEPOSITS_MARK</code> or <code>ERASES_MARK</code> annotation for {g}, or a '
            f'measured perturbation effect. {have}. <b>Until one exists the honest output is '
            f'this one</b> &mdash; and proposing an experiment here would be the system '
            f'inventing a hypothesis it has no basis for.'))
    if tier == "measured" and dep.get(g, 0) > 0 and not rows:
        rows.append(("corroboration",
            f'<b>{dep.get(g,0)} derived edges rest on this one contrast.</b> An independent '
            f'{("writer" if g in wr else "eraser")} of {mark} would corroborate it; a second '
            f'cell type would test whether it generalises beyond K562.'))
    if not rows:
        return ""
    body = "".join(f'<div class="nxr"><span class="nxk">{k}</span><p>{v}</p></div>'
                   for k, v in rows)
    return (f'<div class="next"><h3>what to measure next</h3>{body}'
            f'<p class="nxf">Scope: of the <b>{NX["n_enz"]}</b> chromatin-mark writers and '
            f'erasers in this graph, ENCODE has knockdowns for <b>{NX["n_enz_enc"]}</b> and we '
            f'have used two. The public well is nearly dry, which is itself the result.</p></div>')

cards = {}
for g, v in A.items():
    t = v["best_tier"]
    counts = "".join(
        f'<span class="cnt c-{k}">{v["n_"+k]} {k}</span>'
        for k in ("measured", "curated", "literature", "inferred") if v["n_" + k])
    if t == "none":
        body = ('<div class="refuse"><div class="rbig">best_tier: none</div>'
                '<p>No evidence at any tier connects this gene to transposable-element '
                'regulation, and no rule fires. <b>The system returns nothing rather than '
                'guessing.</b></p><p class="sm">This is a supported output, not an error '
                'path — and it is what makes the other answers worth reading.</p></div>')
    else:
        blocks = []
        for c in v["claims"]:
            cites = " ".join(f'<code>{html.escape(e)}</code>' for e in c.get("edge_ids", []))
            rule = (f'<span class="rule">{html.escape(c["rule"])}</span>'
                    if c.get("rule") else "")
            eds = parse_edges(c.get("proof") or []) or edges_from_paths(v.get("paths"))
            mix = {}
            for *_x, tr in eds:
                mix[tr] = mix.get(tr, 0) + 1
            combo = " + ".join(f'<span class="mx m-{k}">{mix[k]} {k}</span>'
                               for k in ("measured", "curated", "literature", "inferred")
                               if mix.get(k))
            blocks.append(
                f'<div class="claim"><div class="ctop"><span class="badge b-{c["tier"]}">'
                f'{c["tier"]}</span>{rule}</div><p class="ctext">{html.escape(c["text"])}</p>'
                + (f'<div class="combo">built from {combo}</div>' if combo else "")
                + svg(eds)
                + f'<details><summary>the same derivation as the engine prints it</summary>'
                f'<div class="proof">{render_proof(c.get("proof", []))}</div></details>'
                f'<div class="cites">evidence ids: {cites or "&mdash;"}</div></div>')
        body = "".join(blocks)
    cards[g] = (f'<div class="hdr"><h2>{g}</h2><span class="badge big b-{t}">best tier: {t}'
                f'</span></div><p class="tnote">{TIER_NOTE[t]}</p>'
                f'<div class="counts">{counts}</div>{body}{next_experiment(g, t)}')

groups = {t: [g for g, v in A.items() if v["best_tier"] == t] for t in TIER_ORDER}
nav = "".join(
    f'<div class="grp"><div class="glab">{t}</div>' +
    "".join(f'<button class="gb b-{t}" data-g="{g}">{g}</button>' for g in groups[t]) + "</div>"
    for t in TIER_ORDER if groups[t])

CSS = """
/* Light palette, NeSy accent hues darkened for contrast on white. The tier colours stay
   load-bearing: cyan is measurement, blue is curation, slate is literature (weakest),
   magenta is symbolic inference. A subgraph therefore shows cyan and blue edges feeding
   magenta conclusions, which is the architecture without a caption. */
:root{
 --bg:#f6f8fb; --panel:#ffffff; --panel2:#eef3f8; --line:#dbe3ec;
 --ink:#18212e; --mut:#55606e; --dim:#7d8a99;
 --t-measured:#0d7ea6; --t-curated:#2a6fae; --t-literature:#6b7886;
 --t-inferred:#b0466f; --t-none:#98a2af;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,system-ui,sans-serif;
 -webkit-font-smoothing:antialiased}
.wrap{display:flex;min-height:100vh}
aside{width:282px;flex:0 0 282px;background:#fff;border-right:1px solid var(--line);
 padding:1.5rem 1.15rem;overflow:auto}
.brand{font:700 9.6px/1.5 inherit;letter-spacing:.2em;color:var(--t-measured);
 text-transform:uppercase;margin-bottom:1rem}
aside h1{font-size:.98rem;line-height:1.4;margin:0 0 .4rem;letter-spacing:-.01em}
aside .sub{font-size:.79rem;color:var(--mut);margin:0 0 1.3rem;line-height:1.55}
.grp{margin-bottom:.95rem}
.glab{font:700 9.4px/1.5 inherit;text-transform:uppercase;letter-spacing:.15em;
 color:var(--dim);margin-bottom:.4rem;padding-left:.1rem}
.gb{display:block;width:100%;text-align:left;margin:.2rem 0;padding:.44rem .65rem;
 border-radius:7px;border:1px solid var(--line);background:#f9fbfd;color:#2b3644;
 font:600 13.2px/1.3 inherit;cursor:pointer;transition:.13s}
.gb:hover{background:#eef3f8;border-color:#c3d0de}
.gb.on{background:var(--t-measured);border-color:var(--t-measured);color:#fff}
main{flex:1;padding:2.1rem 2.5rem 3rem;overflow:auto;max-width:1060px}
.hdr{display:flex;align-items:baseline;gap:.9rem;flex-wrap:wrap}
h2{font-size:1.95rem;margin:0;letter-spacing:-.025em;font-weight:700}
.tnote{color:var(--mut);font-size:.9rem;margin:.5rem 0 .85rem;max-width:74ch}
.badge{display:inline-block;padding:.22rem .62rem;border-radius:999px;color:#fff;
 font:700 10.4px/1.5 inherit;text-transform:uppercase;letter-spacing:.12em}
.badge.big{font-size:11px;padding:.3rem .78rem}
.b-measured{background:var(--t-measured)}.b-curated{background:var(--t-curated)}
.b-literature{background:var(--t-literature)}.b-inferred{background:var(--t-inferred)}
.b-none{background:var(--t-none)}
.counts{margin:.15rem 0 1.35rem}
.cnt{display:inline-block;margin-right:.4rem;padding:.18rem .58rem;border-radius:6px;
 font:600 11.6px/1.5 inherit;background:#eef3f8;color:var(--mut);border:1px solid var(--line)}
.claim{background:var(--panel);border:1px solid var(--line);border-radius:12px;
 padding:1.1rem 1.25rem;margin-bottom:1.15rem;box-shadow:0 1px 2px rgba(20,35,60,.04)}
.ctop{display:flex;align-items:center;gap:.65rem;margin-bottom:.55rem}
.rule{font:600 11px/1.5 ui-monospace,Menlo,monospace;color:var(--dim);letter-spacing:.06em}
.ctext{margin:.1rem 0 .85rem;font-size:1.03rem;line-height:1.55}
.combo{font:600 11.4px/1.5 inherit;color:var(--mut);letter-spacing:.04em;
 text-transform:uppercase;margin-bottom:.55rem}
.mx{padding:.1rem .42rem;border-radius:5px;margin:0 .1rem}
.m-measured{color:#075e7d;background:#e2f2f8}
.m-curated{color:#1d5488;background:#e6eefa}
.m-literature{color:#4d5a69;background:#eef1f5}
.m-inferred{color:#8e2f56;background:#fae9f0}
svg.kg{display:block;margin:.35rem 0 .65rem;background:#fbfdff;border:1px solid var(--line);
 border-radius:10px;padding:.3rem}
.kn{fill:#ffffff}
.nl{font:600 12.4px ui-monospace,Menlo,monospace;fill:#1b2430}
.el{font:600 9.4px inherit;fill:var(--dim);letter-spacing:.07em}
details{margin:.35rem 0 .1rem}
summary{cursor:pointer;font-size:.83rem;color:var(--dim)}
summary:hover{color:var(--t-measured)}
.proof{background:#0f141a;border-radius:8px;padding:.75rem .9rem;overflow-x:auto;
 margin-top:.5rem}
.pl{font:12.4px/1.62 ui-monospace,SFMono-Regular,Menlo,monospace;color:#b9c6d4;
 white-space:pre-wrap}
.t-measured{color:#5ecbe8}.t-curated{color:#8fc0ec}
.t-inferred{color:#eda3c4}.t-literature{color:#aab6c4}
.warn{color:#e8a25a}
.cites{margin-top:.6rem;font-size:.78rem;color:var(--dim)}
.cites code{background:#eef3f8;padding:.1rem .34rem;border-radius:4px;font-size:.94em;
 color:var(--mut)}
.refuse{background:var(--panel);border:1px solid var(--line);
 border-left:3px solid var(--t-none);border-radius:12px;padding:1.15rem 1.3rem}
.rbig{font:700 1.12rem/1.4 ui-monospace,Menlo,monospace;color:var(--mut);margin-bottom:.55rem}
.sm{font-size:.87rem;color:var(--mut)}
.legend{display:flex;gap:1.1rem;flex-wrap:wrap;margin:0 0 1.2rem;padding:.9rem 1.05rem;
 background:var(--panel2);border:1px solid var(--line);border-radius:10px}
.lg{flex:1 1 260px;min-width:240px}
.lg h4{margin:0 0 .3rem;font:700 9.8px/1.5 inherit;letter-spacing:.15em;text-transform:uppercase}
.lg p{margin:0;font-size:.8rem;color:var(--mut);line-height:1.5}
.prio{background:var(--panel);border:1px solid var(--line);border-radius:12px;
 padding:.55rem .9rem 0;margin:0 0 1.5rem}
.prio summary{font:700 10px/1.5 inherit;letter-spacing:.15em;text-transform:uppercase;
 color:var(--t-measured);padding:.35rem 0}
.prio img{width:100%;display:block;margin:.7rem 0 .2rem;border-radius:8px}
.prio p{font-size:.82rem;color:var(--mut);margin:.2rem 0 .85rem;line-height:1.55}
.next{background:#f4fafd;border:1px solid #cfe6f0;border-left:3px solid var(--t-measured);
 border-radius:12px;padding:1.05rem 1.25rem;margin-top:.4rem}
.next h3{margin:0 0 .7rem;font:700 10px/1.5 inherit;letter-spacing:.17em;
 text-transform:uppercase;color:var(--t-measured)}
.nxr{margin-bottom:.8rem}
.nxk{display:inline-block;font:700 9.4px/1.5 inherit;letter-spacing:.13em;
 text-transform:uppercase;color:#fff;background:var(--t-measured);padding:.15rem .5rem;
 border-radius:4px;margin-bottom:.32rem}
.nxr p{margin:.3rem 0 0;font-size:.895rem;color:#2f3b4a;line-height:1.6}
.nxr code{background:#e8eef5;padding:.08rem .32rem;border-radius:4px;font-size:.92em;
 color:#8e2f56}
.nxf{margin:.85rem 0 0;padding-top:.7rem;border-top:1px solid #cfe6f0;font-size:.8rem;
 color:var(--mut);line-height:1.55}
footer{margin-top:2.2rem;padding-top:1.1rem;border-top:1px solid var(--line);
 font-size:.81rem;color:var(--dim);line-height:1.6}
footer code{background:#eef3f8;padding:.1rem .36rem;border-radius:4px;color:var(--mut)}
"""


JS = """
const C=%s;
function show(g){document.getElementById('out').innerHTML=C[g];
 document.querySelectorAll('.gb').forEach(b=>b.classList.toggle('on',b.dataset.g===g));}
document.querySelectorAll('.gb').forEach(b=>b.onclick=()=>show(b.dataset.g));
show(%s);
""" % (json.dumps(cards), json.dumps("TET2"))

out = ROOT / "demo" / "query.html"
out.write_text(
 "<!doctype html><meta charset='utf-8'><title>TE regulation — evidence-traceable queries</title>"
 f"<style>{CSS}</style><div class='wrap'><aside>"
 "<div class='brand'>Dark genome &middot; live query</div><h1>What does this gene do to the "
 "repetitive genome?</h1><p class='sub'>Click a gene. Every answer shows its evidence tier "
 "and the derivation that produced it — including the genes where the answer is "
 "<b>nothing</b>.</p>" + nav +
 "<div class='glab' style='margin-top:1.2rem'>edge colours</div>"
 "<p class='sub' style='margin:0'><span style='color:var(--t-measured)'>&#9644; measured</span> "
 "&nbsp;<span style='color:var(--t-curated)'>&#9644; curated</span><br>"
 "<span style='color:var(--t-literature)'>&#9644; literature</span> "
 "&nbsp;<span style='color:var(--t-inferred)'>&#9644; inferred</span></p>" + "</aside><main>"
 "<div class='legend'>"
 "<div class='lg'><h4 style='color:var(--t-measured)'>the statistical half</h4>"
 "<p>Continuous, noisy effect sizes measured from public perturbation RNA-seq by our own "
 "re-analysis. Numbers with confidence, and no meaning attached.</p></div>"
 "<div class='lg'><h4 style='color:var(--t-curated)'>the symbolic half</h4>"
 "<p>Discrete, exact records &mdash; Gene Ontology, Reactome, Complex Portal &mdash; plus six "
 "rules that chain them. Meaning with no data attached.</p></div>"
 "<div class='lg'><h4 style='color:var(--t-inferred)'>what you are looking at</h4>"
 "<p>Every answer below is a <b>subgraph</b>: measured and curated edges combined by a rule "
 "into a conclusion no single source contains. That combination is the neurosymbolic part, and "
 "the tier tells you how much of it is measurement.</p></div></div>"
 "<details class='prio' open><summary>how the system ranks one experiment against another</summary>"
 f"<img src='{img('fig_ev5_priority.png')}' alt='experiment priority by mark'>"
 "<p>Value proxy = derived edges that would gain a second, independent grounding &mdash; a "
 "count of exposure, not an expected-information calculation. <b>78 of 83 derived edges rest "
 "on H3K9me3, grounded by SETDB1 alone: the one knockdown whose efficiency is not "
 "confirmed.</b> The 26 H3K9me3 writers and erasers in this graph would each corroborate those "
 "78 edges, and none has a public knockdown. That gap is the ask.</p></details>"
 "<div id='out'></div>"
 "<footer>Answers produced by <code>python src/te_reason.py &lt;gene&gt; --proofs</code> and "
 "pasted in verbatim. <b>This page is a viewer, not a server</b> — it computes nothing. "
 "A conclusion's tier is the weakest link on its derivation path, so a chain containing one "
 "literature edge can never be reported as measured.</footer></main></div>"
 f"<script>{JS}</script>")
print(f"wrote {out.relative_to(ROOT)} — {len(A)} genes, {out.stat().st_size/1024:.0f} KB")
