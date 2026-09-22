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
import html, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "handoff" / "demo_answers.json"
if not SRC.exists():
    SRC = ROOT.parent / "handoff" / "demo_answers.json"
A = json.load(open(SRC))

TIER_ORDER = ["measured", "curated", "literature", "inferred", "none"]
TIER_NOTE = {
 "measured":   "our own re-analysis of a perturbation experiment",
 "curated":    "a curated database record (Gene Ontology, Reactome, Complex Portal, STRING)",
 "literature": "extracted from an abstract — unvalidated, and never allowed to ground a rule",
 "inferred":   "derived by a rule from premises below it; tier = weakest link on the path",
 "none":       "no evidence at any tier. The system declines rather than guessing",
}

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
            blocks.append(
                f'<div class="claim"><div class="ctop"><span class="badge b-{c["tier"]}">'
                f'{c["tier"]}</span>{rule}</div><p class="ctext">{html.escape(c["text"])}</p>'
                f'<div class="proof">{render_proof(c.get("proof", []))}</div>'
                f'<div class="cites">evidence ids: {cites or "&mdash;"}</div></div>')
        body = "".join(blocks)
    cards[g] = (f'<div class="hdr"><h2>{g}</h2><span class="badge big b-{t}">best tier: {t}'
                f'</span></div><p class="tnote">{TIER_NOTE[t]}</p>'
                f'<div class="counts">{counts}</div>{body}')

groups = {t: [g for g, v in A.items() if v["best_tier"] == t] for t in TIER_ORDER}
nav = "".join(
    f'<div class="grp"><div class="glab">{t}</div>' +
    "".join(f'<button class="gb b-{t}" data-g="{g}">{g}</button>' for g in groups[t]) + "</div>"
    for t in TIER_ORDER if groups[t])

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',
Inter,system-ui,sans-serif;color:#1b2430;background:#f4f6f9}
.wrap{display:flex;min-height:100vh}
aside{width:270px;flex:0 0 270px;background:#111823;color:#dbe4ee;padding:1.4rem 1.1rem;overflow:auto}
aside h1{font-size:1.02rem;margin:0 0 .25rem;color:#fff;letter-spacing:-.01em}
aside .sub{font-size:.78rem;color:#8fa0b4;margin:0 0 1.1rem;line-height:1.5}
.grp{margin-bottom:1rem}.glab{font-size:.68rem;text-transform:uppercase;letter-spacing:.09em;
color:#7d8fa5;margin-bottom:.38rem}
.gb{display:block;width:100%;text-align:left;margin:.16rem 0;padding:.4rem .6rem;border-radius:6px;
border:1px solid #2c3a4b;background:#1b2531;color:#e6edf5;font:600 13.4px/1.3 inherit;cursor:pointer;
transition:.12s}
.gb:hover{background:#26344a}
.gb.on{background:#2f4666;border-color:#5b7fa8}
main{flex:1;padding:2.1rem 2.4rem;overflow:auto;max-width:1000px}
.hdr{display:flex;align-items:center;gap:.9rem;flex-wrap:wrap}
h2{font-size:1.82rem;margin:0;letter-spacing:-.02em}
.tnote{color:#5a6879;font-size:.92rem;margin:.45rem 0 .9rem}
.badge{display:inline-block;padding:.2rem .6rem;border-radius:999px;font:700 11.6px/1.5 inherit;
text-transform:uppercase;letter-spacing:.05em;color:#fff}
.badge.big{font-size:12.6px;padding:.3rem .8rem}
.b-measured{background:#0a7c4a}.b-curated{background:#2c6fa8}.b-literature{background:#8a6d3b}
.b-inferred{background:#b8791f}.b-none{background:#7a8391}
.counts{margin:.2rem 0 1.2rem}.cnt{display:inline-block;margin-right:.45rem;padding:.16rem .55rem;
border-radius:5px;font:600 12px/1.5 inherit;background:#e6ecf3;color:#405063}
.claim{background:#fff;border:1px solid #dde4ec;border-radius:10px;padding:1rem 1.15rem;margin-bottom:1rem}
.ctop{display:flex;align-items:center;gap:.6rem;margin-bottom:.5rem}
.rule{font:600 11.6px/1.5 ui-monospace,Menlo,monospace;color:#6b7886}
.ctext{margin:.1rem 0 .8rem;font-size:1.02rem}
.proof{background:#0d1219;border-radius:7px;padding:.75rem .9rem;overflow-x:auto}
.pl{font:12.6px/1.62 ui-monospace,SFMono-Regular,Menlo,monospace;color:#c6d5e6;white-space:pre-wrap}
.t-measured{color:#7fd6a8}.t-curated{color:#8fc4ec}.t-inferred{color:#e8c07a}
.t-literature{color:#d9bd8a}.warn{color:#e89a5a}
.cites{margin-top:.6rem;font-size:.8rem;color:#6b7886}
.cites code{background:#eef2f7;padding:.08rem .3rem;border-radius:4px;font-size:.92em}
.refuse{background:#fff;border:1px solid #dde4ec;border-left:4px solid #7a8391;border-radius:10px;
padding:1.1rem 1.25rem}
.rbig{font:700 1.15rem/1.4 ui-monospace,Menlo,monospace;color:#5a6879;margin-bottom:.5rem}
.sm{font-size:.88rem;color:#5a6879}
footer{margin-top:2rem;padding-top:1rem;border-top:1px solid #dde4ec;font-size:.83rem;color:#6b7886}
footer code{background:#eef2f7;padding:.1rem .34rem;border-radius:4px}
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
 f"<style>{CSS}</style><div class='wrap'><aside><h1>What does this gene do to the "
 "repetitive genome?</h1><p class='sub'>Click a gene. Every answer shows its evidence tier "
 "and the derivation that produced it — including the genes where the answer is "
 "<b>nothing</b>.</p>" + nav + "</aside><main><div id='out'></div>"
 "<footer>Answers produced by <code>python src/te_reason.py &lt;gene&gt; --proofs</code> and "
 "pasted in verbatim. <b>This page is a viewer, not a server</b> — it computes nothing. "
 "A conclusion's tier is the weakest link on its derivation path, so a chain containing one "
 "literature edge can never be reported as measured.</footer></main></div>"
 f"<script>{JS}</script>")
print(f"wrote {out.relative_to(ROOT)} — {len(A)} genes, {out.stat().st_size/1024:.0f} KB")
