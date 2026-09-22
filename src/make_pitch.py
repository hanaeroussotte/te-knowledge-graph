#!/usr/bin/env python3
"""make_pitch.py — build demo/pitch.html, a self-contained 10-slide deck.

    python src/make_pitch.py

Figures are base64-embedded so the file works offline on any machine with no server and no
network. Every number here is quoted from a table in results/ — if you change an analysis,
re-run this rather than editing the HTML.

Keys: arrows navigate, f fullscreen, s toggles speaker notes, o slide overview.
"""
import base64, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

def img(name):
    p = ROOT / "figures" / name
    if not p.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()

S = []
def slide(kicker, title, body, notes):
    S.append((kicker, title, body, notes))

# ------------------------------------------------------------------ 1
slide("", "Evidence-Traceable Neurosymbolic Reasoning<br>for Transposable-Element Regulation",
"""<p class="lede">Half of your genome is repeated DNA that cells work constantly to keep
switched off. When that machinery fails, those elements switch back on — and that has been
tied to inflammation and ageing.</p>
<p class="lede"><b>This system re-analyses public perturbation experiments for what they did
to the repetitive genome, turns each result into a relationship that carries its own
evidence, reasons over the result, and tells you when the evidence is not enough.</b></p>
<p class="meta">Hanae Roussotte · biology knowledge-graph track</p>""",
"""Say the first paragraph slowly — it is the only biology anyone needs. Then the claim
sentence verbatim. Do not say 'atlas'; an atlas is the long-term object, this is an
architecture with three worked experiments.""")

# ------------------------------------------------------------------ 2
slide("The gap", "Transposable elements are excluded twice over",
"""<div class="two">
<div class="card"><h3>Out of the knowledge graphs</h3>
<p>The major general-purpose biomedical graphs do not model transposable elements as
first-class entities. PrimeKG has 10 principal node types; Hetionet has 11. None is a
transposable element.</p>
<p class="small">Nearest precedents: TEKRABber builds TE–KRAB-ZFP networks, PlaNC-TE is a
plant TE knowledgebase. Neither is perturbational.</p></div>
<div class="card"><h3>Out of the experiments</h3>
<p>ENCODE holds <b>1,114 knockdown experiments across 570 genes</b>. The reads are public.
Almost nobody re-counts them against the repeat annotation, because the standard pipeline
discards multi-mapping reads — which is most of the repetitive genome.</p>
<p class="small">The measurement exists in data already paid for. It was never made.</p></div>
</div>
<p class="punch">So the question &ldquo;what does this gene do to transposable elements?&rdquo;
has no substrate to be asked against. That is what we built.</p>""",
"""Both halves are defensible and both are narrowed claims — 'do not model TEs as
first-class entities', not 'no graph has TEs'. If challenged on novelty, concede
immediately and cite TEKRABber; the positioning survived two adversarial prior-art passes.""")

# ------------------------------------------------------------------ 3
slide("Architecture", "Four evidence layers, six rules, and permission to refuse",
"""<div class="layers">
<div class="L c"><b>curated</b><span>9,263 edges</span><em>GO · STRING v12 · Reactome · Complex Portal</em></div>
<div class="L m"><b>mechanism</b><span>44 edges</span><em>who writes and erases which chromatin mark</em></div>
<div class="L e"><b>measured</b><span>27 edges</span><em>our own re-analysis, signed and dated</em></div>
<div class="L l"><b>literature</b><span>tiered lowest</span><em>extracted, unvalidated, never grounds a rule</em></div>
</div>
<p class="punch">Every edge carries a source, a retrieval date, a stable id and a tier. Rules
chain forward to a fixpoint; a claim's tier is <b>the weakest link on its path</b>, and every
answer prints the derivation that produced it.</p>
<div class="two">
<div class="card"><h3>Structural audit — <span class="mono">make validate</span></h3>
<p class="small">42 metrics. <b>0</b> schema violations over 9,366 typed edges · <b>0</b>
self-loops · <b>0</b> duplicate triples · <b>100%</b> provenance · 97.6% one component.</p></div>
<div class="card"><h3>It found its own defect</h3>
<p class="small">One gene–TE pair asserted in <i>both</i> directions — both edges from the
<i>same abstract</i>. Kept, not deleted: it is the literature layer's unmeasured error rate
made visible, and the reason that layer is tiered below measurement.</p></div>
</div>""",
"""The audit slide is where technical credibility is won. Lead with the defect, not the
passes — volunteering a real flaw buys more trust than five clean metrics. If asked whether
structural cleanliness means the edges are true: no, and say so flatly.""")

# ------------------------------------------------------------------ 4
slide("The measurement", "Three knockdowns, re-counted against the repeat genome",
"""<p>ENCODE RNA-seq, K562, 11 libraries. HISAT2 reporting up to 100 alignments per read,
then TEcount's expectation-maximisation to apportion multi-mapping reads across subfamilies
(<b>TEtranscripts, Jin et al. 2015 — not ours</b>), then DESeq2 with size factors estimated
on protein-coding genes only.</p>
<table class="t">
<tr><th>Knockdown</th><th>target's own mRNA</th><th>remaining</th><th>efficiency</th><th>TE result</th></tr>
<tr><td>DNMT1</td><td>&minus;1.87</td><td>27%</td><td class="ok">confirmed</td><td>whole-compartment shift</td></tr>
<tr><td>TRIM28</td><td>&minus;1.12</td><td>46%</td><td class="ok">confirmed</td><td>AluY +0.79, padj 0.0005</td></tr>
<tr><td>SETDB1</td><td>&minus;0.35 <span class="small">(ns)</span></td><td>78%</td><td class="bad">not confirmed</td><td>two ERV families up</td></tr>
</table>
<p class="punch">We ran that efficiency check on ourselves <b>today</b>, and it cost us:
SETDB1 — the sole anchor for H3K9me3 — cannot be confirmed to have worked. Verdict is
<i>not confirmed</i>, not <i>failed</i>: CRISPRi acts on transcription, we read a shallow
snapshot, and the knockdown did produce the ERV results.</p>""",
"""Credit TEtranscripts out loud and early; it is the single most likely thing to be
mistaken for our contribution. Then give the SETDB1 row without flinching. The reason this
slide works is that nobody else will show you a failed control on their own data.""")

# ------------------------------------------------------------------ 5
slide("The headline, attacked", "One result had to survive, and it did — weaker than it started",
"""<p>Our primary readout is normalisation-invariant by construction:
<span class="mono">&Delta; = median log&#8322;FC over TE subfamilies &minus; median over
protein-coding genes</span>, within one contrast. Size factors are per-sample and
multiplicative, so they shift both sets equally on the log scale and cancel in the difference.</p>
<p class="punch bad-b">An external reviewer found the real flaw: our p-value treated ~350
correlated TE families as independent evidence. We measured the inflation instead of arguing.
<b>Mean pairwise correlation 0.006–0.48 → variance inflation 4× to 155×.</b> In the two
CRISPRi contrasts, 322 families carry about <b>two families' worth</b> of independent
information. Those p-values are retracted.</p>
<table class="t">
<tr><th>Test</th><th>DNMT1 — the 5mC anchor</th></tr>
<tr><td>effect size</td><td><b>&Delta; = +0.13</b>, 63% of 503 families up</td></tr>
<tr><td>six ways of defining the TE set</td><td class="ok">same sign in <b>6 of 6</b> — LINE +0.19, SINE +0.10, LTR +0.11, DNA +0.10</td></tr>
<tr><td>drop any one library</td><td class="ok">+0.10 … +0.19, <b>sign never flips</b></td></tr>
<tr><td>permute the sample labels</td><td class="ok">most extreme of the 3 admissible labellings, by 3.7&times;</td></tr>
<tr><td>correlation-aware p</td><td><b>0.045</b></td></tr>
</table>
<p class="small">TRIM28's <i>whole-compartment</i> claim did not survive — a permuted
labelling beat the real one — and is now reported as an effect size only. Its per-feature
AluY result is a different statistic and stands.</p>""",
"""This is the slide a statistician will respect. The line to have ready: with two
replicates per arm there are three possible label shufflings, so no p below 0.333 is
reachable — that is a limit of the experiment, not the analysis. Anyone quoting a tiny
p-value from a two-replicate design is quoting an artefact.""")

# ------------------------------------------------------------------ 6
slide("The reasoning layer", "One measurement propagates to genes nobody assayed",
"""<div class="two">
<div class="card"><h3>What fires</h3>
<p class="small"><b>R1</b> grounds a mark on a TE from a measured writer effect ·
<b>R2</b> transfers to other writers of the same mark · <b>R3</b> inverts the sign for
erasers · <b>R4</b> requires complex consensus · <b>R6</b> demands TE derepression <i>and</i>
inflammation in the same contrast — and has <b>never fired</b>.</p>
<p class="small">89 derived edges from 27 measured ones. Each prints its proof tree.</p></div>
<div class="card"><h3>The worked example</h3>
<p class="small">From the DNMT1 measurement plus two Gene Ontology records, the engine
derives <b>DNMT3A loss raises TEs</b> and <b>TET2 loss lowers them</b> — opposite signs on
one axis, having never seen data for either gene.</p>
<p class="small bad-b">The hypothesis is published, and <b>I am a co-author</b>
(<i>GeroScience</i> 2026). So this instruments my own prior finding; it does not confirm it.</p></div>
</div>
<p class="punch">What is <i>not</i> trivial: the rule commits to a <b>direction</b> the
paper's own hypothesis does not state — TEs go <i>down</i> in TET2 — and the measured data
trends that way, across a different quantifier, resolution, perturbation type and tissue.</p>""",
"""Disclose the co-authorship in the same breath as the citation, every time. 'An
independent paper confirms our prediction' is falsifiable in ten seconds from the author
list, and if they check after hearing it they will discount everything else.""")

# ------------------------------------------------------------------ 7
slide("Robustness", "We asked how much of our own reasoning rests on how little",
f"""<img class="fig" src="{img('fig_holdout_robustness.png')}" alt="anchor-dependence analysis">
<p class="punch">Remove <b>SETDB1</b> and the derived layer collapses from <b>89 edges to
8</b>. Remove <b>TRIM28</b> — the largest measured effect in the whole dataset — and
<b>nothing changes at all</b>, because a scaffold has no writer annotation and cannot satisfy
R1.</p>
<p>Only <b>four</b> edges ground the entire inference layer. No hold-out ever flipped a
direction; genes either keep their prediction or return <span class="mono">best_tier:
none</span>.</p>
<p class="punch ok-b">That converts &ldquo;we need more data&rdquo; into a specific
experimental request: <b>more writers and erasers of the same two marks</b> — not more
scaffolds. And we checked: of 40 mark enzymes in the graph, ENCODE has knockdowns for
<b>three</b>, and we have used two. The public well is nearly dry, which is itself the
finding.</p>""",
"""The strongest 40 seconds in the deck, and the one that shows the graph is an
experimental-design tool rather than a database. The TRIM28-contributes-nothing result is
counter-intuitive and worth pausing on.""")

# ------------------------------------------------------------------ 8
slide("Refusal", "Four things we built, measured, and did not ship",
"""<table class="t">
<tr><th>Built</th><th>Measured</th><th>Decision</th></tr>
<tr><td>rule-based literature extractor</td><td>precision <b>0.109</b></td><td class="bad">rejected</td></tr>
<tr><td>link prediction on the graph</td><td>no held-out set is constructible from 3 knockdowns</td><td class="bad">not built</td></tr>
<tr><td>an interferon conclusion</td><td>reference contained 17% of the signature</td><td class="bad">refused, then fixed</td></tr>
<tr><td>compartment Mann-Whitney p-values</td><td>variance inflation up to 155&times;</td><td class="bad">retracted today</td></tr>
</table>
<p class="punch">The interferon arm is the instructive one. We built a panel reference,
took type-I interferon coverage from <b>0.17 to 0.77</b> — and the answer was <i>still</i> a
null, now with a mechanism: in K562 the cytosolic sensors are barely expressed. CGAS 0.21,
ZBP1 0.26, TLR3 0.00 CPM, while the transducers run at 270–800.</p>
<p><b>The wiring and the sprinklers are installed; the smoke detectors are not.</b> So the
honest claim is not &ldquo;TE derepression does not cause interferon&rdquo; — it is
<i>this dataset cannot decisively test it, and here is the cell type that could</i>.</p>
<p class="small">The inflammatory-response set still fails the 0.6 coverage guard at 0.535.
The guard is still refusing, after the fix.</p>""",
"""If you only get one slide past the title, make it this one. 'best_tier: none' being a
supported output rather than an error path is the thing nobody else in the room will have.""")

# ------------------------------------------------------------------ 9
slide("Collaboration", "An abstract theory of treatment, joined to a real measurement",
f"""<img class="fig tall" src="{img('ca_worked_example.png')}" alt="metamodel worked example">
<div class="two">
<div class="card"><h3>What enumeration shows</h3>
<p class="small">Organism = a pattern from a simple rule, dying at step 117. Disease = change
one cell → dies at 70. Treatment = change a second. Of <b>3,447 possible diseases, 8% heal
themselves</b>. Of <b>1,479 possible treatments, 6 cure and 195 (13%) cause unbounded,
tumour-like growth</b> — and every cure leaves <b>1,622 cells</b> changed.</p></div>
<div class="card"><h3>Why it belongs here</h3>
<p class="small">Both sides inherit <b>computational irreducibility</b>: the only way to know
what a rule does is run it. But irreducible processes contain <b>pockets of
reducibility</b> — and that is exactly what this graph maps.</p>
<p class="small ok-b"><b>The evidence graph is a map of the pockets of reducibility in TE
regulation. The refusals mark where the map ends.</b></p></div>
</div>""",
"""Say the organism/disease/treatment sentence and let the figure do the rest. Then the
thesis sentence verbatim — it reframes the refusals from timidity into the correct response
to irreducibility, which is the most defensible thing either half says alone.""")

# ------------------------------------------------------------------ 10
slide("Honestly", "What is weak, and exactly what fixes it",
"""<table class="t">
<tr><th>Limitation</th><th>What would settle it</th></tr>
<tr><td>the entire 5mC arm rests on <b>one</b> DNMT1 contrast, at 1.5 M reads across chr1+chr19 — and chr19 is the most gene-dense, Alu-rich chromosome and carries the KRAB-ZFP clusters</td><td>genome-wide at full depth</td></tr>
<tr><td>SETDB1's knockdown efficiency is <b>not confirmed</b>, and it anchors 3 of the 4 grounding edges</td><td>the same run</td></tr>
<tr><td>only <b>9 of 55</b> silencing-machinery genes are measurable at current reference scope</td><td>the same run</td></tr>
<tr><td>subfamily resolution, not loci — and the field is moving to loci</td><td>Telescope / SQuIRE</td></tr>
<tr><td><b>no rescue experiment exists in ENCODE</b> — every public experiment is a single perturbation</td><td>control vs disease vs disease + candidate rescue</td></tr>
<tr><td>two replicates per arm caps any sample-level p at 0.333</td><td>more replicates, not a better test</td></tr>
</table>
<p class="punch">Two adversarial prior-art passes, 279 abstracts, 198 full texts. Five
novelty claims retracted, including one we had liked. <b>One search returned a clean zero and
we believed it — the paper existed and its fourth author was in the room.</b> That is logged
as the fifth time a check in this project was found to be lying.</p>
<p class="punch ok-b">The ask is specific: <b>writers and erasers of H3K9me3 and 5mC outside
ENCODE</b>, and <b>one rescue experiment</b>. Everything else here is already computed and
in the repository.</p>""",
"""Close on the ask, not on the limitations. If time is short cut slides 2 and 6 — the
architecture, the attacked headline, the robustness result and this one carry the whole
argument in three minutes.""")

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#12161c;color:#e8edf4;font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Helvetica,Arial,sans-serif}
.slide{display:none;min-height:100vh;padding:4.2vh 5.5vw 9vh;max-width:1220px;margin:0 auto;animation:f .18s ease}
.slide.on{display:block}
@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.kicker{text-transform:uppercase;letter-spacing:.16em;font-size:11.5px;font-weight:700;color:#7aa7d9;margin:0 0 .7rem}
h1{font-size:2.6rem;line-height:1.16;margin:.1rem 0 1.3rem;font-weight:800;letter-spacing:-.02em}
h2{font-size:1.92rem;line-height:1.2;margin:.1rem 0 1.15rem;font-weight:750;letter-spacing:-.015em}
h3{font-size:1.02rem;margin:0 0 .5rem;color:#a9c8ea;font-weight:700}
p{margin:0 0 .85rem}
.lede{font-size:1.16rem;color:#dbe6f2;max-width:56em}
.meta{margin-top:2.2rem;color:#7f8fa3;font-size:.95rem}
.small{font-size:.9rem;color:#b9c6d6}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.93em;background:#1c2431;padding:.08em .38em;border-radius:4px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:.6rem 0 1rem}
.card{background:#19212c;border:1px solid #27333f;border-left:3px solid #4d7fb3;border-radius:7px;padding:.9rem 1.05rem}
.punch{background:#19212c;border-left:3px solid #7aa7d9;padding:.75rem 1.05rem;border-radius:0 7px 7px 0;font-size:1.03rem}
.punch.ok-b{border-left-color:#3fae7a}.punch.bad-b{border-left-color:#d1695c}
.ok-b{color:#8fe0b6}.bad-b{color:#f0a79c}
.t{width:100%;border-collapse:collapse;margin:.5rem 0 1rem;font-size:.95rem}
.t th{text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.09em;color:#8fa3ba;border-bottom:1px solid #33404f;padding:.42rem .6rem}
.t td{border-bottom:1px solid #212b36;padding:.48rem .6rem;vertical-align:top}
.t td.ok{color:#7fd6a8;font-weight:650}.t td.bad{color:#eb8b7d;font-weight:650}
.layers{display:grid;gap:.5rem;margin:.4rem 0 1rem}
.L{display:grid;grid-template-columns:130px 110px 1fr;align-items:center;gap:.9rem;background:#19212c;border-radius:6px;padding:.55rem .9rem;border-left:3px solid #4d7fb3}
.L.m{border-left-color:#c9903f}.L.e{border-left-color:#3fae7a}.L.l{border-left-color:#7a6fa8}
.L b{font-size:1rem}.L span{color:#9fb2c6;font-size:.9rem}.L em{color:#aebfd2;font-style:normal;font-size:.9rem}
.fig{width:100%;border-radius:7px;background:#fff;padding:.5rem;margin:.2rem 0 .9rem;max-height:40vh;object-fit:contain}
.fig.tall{max-height:46vh}
.notes{position:fixed;left:0;right:0;bottom:0;background:#0b0e13;border-top:1px solid #2a3542;color:#c5d2e2;font-size:.9rem;padding:.7rem 5.5vw;max-height:26vh;overflow:auto}
.notes b{color:#7aa7d9}
.bar{position:fixed;top:0;left:0;height:2px;background:#4d7fb3;transition:width .18s}
.num{position:fixed;right:1.1rem;bottom:.5rem;color:#5d6b7d;font-size:12px;font-variant-numeric:tabular-nums}
.help{position:fixed;left:1.1rem;bottom:.5rem;color:#4b5766;font-size:11.5px}
"""

JS = """
let i=0,notes=true;const s=[...document.querySelectorAll('.slide')];
function go(n){i=Math.max(0,Math.min(s.length-1,n));s.forEach((e,k)=>e.classList.toggle('on',k===i));
document.querySelector('.bar').style.width=((i+1)/s.length*100)+'%';
document.querySelector('.num').textContent=(i+1)+' / '+s.length;
const nb=document.querySelector('.notes');nb.innerHTML='<b>say:</b> '+(s[i].dataset.notes||'');
nb.style.display=notes?'block':'none';}
document.addEventListener('keydown',e=>{
 if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown')go(i+1);
 else if(e.key==='ArrowLeft'||e.key==='PageUp')go(i-1);
 else if(e.key==='Home')go(0); else if(e.key==='End')go(s.length-1);
 else if(e.key==='s'){notes=!notes;go(i);}
 else if(e.key==='f'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}});
document.addEventListener('click',e=>{if(!e.target.closest('.notes'))go(i+1)});
go(0);
"""

parts = [f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Evidence-Traceable Neurosymbolic Reasoning for Transposable-Element Regulation</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style></head><body><div class="bar"></div>"""]
for k, t, b, n in S:
    esc = n.replace('"', "&quot;").replace("\n", " ")
    kick = f'<p class="kicker">{k}</p>' if k else ""
    head = "h1" if not k else "h2"
    parts.append(f'<section class="slide" data-notes="{esc}">{kick}'
                 f'<{head}>{t}</{head}>{b}</section>')
parts.append('<div class="notes"></div><div class="num"></div>'
             '<div class="help">&larr; &rarr; move &middot; s notes &middot; f fullscreen</div>'
             f'<script>{JS}</script></body></html>')
out = ROOT / "demo" / "pitch.html"
out.write_text("".join(parts))
print(f"wrote {out.relative_to(ROOT)} — {len(S)} slides, {out.stat().st_size/1e6:.2f} MB")
