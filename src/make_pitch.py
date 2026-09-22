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

slide("", "What does this gene do to the repetitive genome?",
"""<p class="lede">Half the human genome is repeated, mobile DNA. Cells spend real energy
keeping it switched off; when that machinery fails it switches back on, and that is tied to
inflammation and ageing.</p>
<p class="lede"><b>Ask that question of any gene and there is nothing to ask it against.</b>
Transposable elements are missing from the knowledge graphs, and missing from the experiments
that could have answered it.</p>
<div class="two">
<div class="card"><h3>Absent from the graphs</h3>
<p class="small">The major biomedical knowledge graphs do not model transposable elements as
first-class entities. PrimeKG has 10 principal node types, Hetionet 11. None is a
transposable element.</p></div>
<div class="card"><h3>Absent from the experiments</h3>
<p class="small">ENCODE holds <b>1,114 knockdowns across 570 genes</b>, reads public. Standard
pipelines discard multi-mapping reads — which is most of the repetitive genome. The
measurement was paid for and never made.</p></div>
</div>
<p class="meta">Hanae Roussotte &middot; biology knowledge-graph track</p>""",
"""Two sentences of biology, then the gap, then move. Both gap claims are narrowed on purpose
— 'not as first-class entities', not 'no graph has TEs'. The positioning survived two
adversarial prior-art passes; if pushed, concede and cite TEKRABber immediately.""")

slide("The tool", "Ask it about TET2 — a gene with no annotation and no experiment",
"""<pre class="term">$ python src/te_reason.py TET2 --proofs

=== TET2  [best tier: inferred]  measured=0 curated=0 literature=0 inferred=1
Losing TET2 is predicted to <b>lower</b> TE:global, derived by R3_ERASER_INVERSION from:
5mC-MARK_AT-&gt;TE:global, TET2-ERASES_MARK-&gt;5mC  [e0eab062a2cf49c, e62dbe0821f074b]
  citation gate: 1 sentences kept, 0 rejected

  TET2 -DEREPRESSES-&gt; TE:global            [inferred via R3_ERASER_INVERSION]
    <span class="warn">! grounded in context_cell_type=K562; perturbation_modality=CRISPR
      — asserting it elsewhere is a further inference</span>
    5mC -MARK_AT-&gt; TE:global                [inferred via R1_MARK_GROUNDING]
      DNMT1 -SILENCES-&gt; TE:global           <span class="meas">[measured: ENCODE ENCSR600OWF,
        median log2FC of 503 TE subfamilies minus 3120 protein-coding genes]</span>
      DNMT1 -DEPOSITS_MARK-&gt; 5mC            [curated: GO:0003886]
    TET2 -ERASES_MARK-&gt; 5mC                 [curated: GO:0070579]</pre>
<p class="punch">TET2 has <b>no</b> transposon annotation in the Gene Ontology and <b>no</b>
knockdown in ENCODE. The answer is nevertheless specific, signed, and <b>traceable to one
real measurement</b> — and it is labelled <span class="mono">inferred</span>, not measured.</p>""",
"""Run this live if you can; it takes under a second. Trace the tree bottom-up with a finger:
one measurement, two ontology records, a directional prediction. Then point at the warning
line — the system flags that its own conclusion is bound to K562.""")

slide("Under it", "Four evidence layers, and a tier that is the weakest link",
"""<div class="layers">
<div class="L c"><b>curated</b><span>9,263 edges</span><em>Gene Ontology &middot; STRING v12 &middot; Reactome &middot; Complex Portal</em></div>
<div class="L m"><b>mechanism</b><span>44 edges</span><em>which enzyme writes or erases which chromatin mark</em></div>
<div class="L e"><b>measured</b><span>27 edges</span><em>our own re-analysis &mdash; signed, dated, reproducible</em></div>
<div class="L l"><b>literature</b><span>tiered lowest</span><em>extracted, unvalidated, never permitted to ground a rule</em></div>
</div>
<p class="punch">Every edge carries a source, a retrieval date, a stable id and a tier. Six
rules chain forward to a fixpoint; a conclusion's tier is the <b>weakest link on its path</b>,
and every answer prints the derivation — which is what you just saw.</p>
<div class="two">
<div class="card"><h3>Structural audit — <span class="mono">make validate</span></h3>
<p class="small">42 metrics. <b>0</b> schema violations over 9,366 typed edges &middot;
<b>0</b> duplicate triples &middot; <b>100%</b> provenance &middot; 97.6% one component.</p></div>
<div class="card"><h3>It found its own defect</h3>
<p class="small">One gene&ndash;TE pair asserted in <i>both</i> directions — both edges from the
<i>same abstract</i>. Kept, not deleted: it is the literature layer's unmeasured error rate
made visible, and the reason that layer can never ground a rule.</p></div>
</div>""",
"""Lead the audit with the defect, not the passes — volunteering a real flaw buys more than
five clean metrics. If asked whether clean structure means the edges are true: no, flatly.""")

slide("The measurement", "Three knockdowns, re-counted against the repeat annotation",
"""<p>ENCODE RNA-seq in K562, 11 libraries. HISAT2 reporting up to 100 alignments per read,
then TEcount's expectation-maximisation to apportion multi-mapping reads
(<b>TEtranscripts, Jin et al. 2015 &mdash; not ours</b>), then DESeq2 with size factors
estimated on protein-coding genes only.</p>
<table class="t">
<tr><th>Knockdown</th><th>target's own mRNA</th><th>remaining</th><th>did it work?</th><th>effect on TEs</th></tr>
<tr><td>DNMT1</td><td>&minus;1.87</td><td>27%</td><td class="ok">confirmed</td><td>whole-compartment shift</td></tr>
<tr><td>TRIM28</td><td>&minus;1.12</td><td>46%</td><td class="ok">confirmed</td><td>AluY +0.79, padj 0.0005</td></tr>
<tr><td>SETDB1</td><td>&minus;0.35 <span class="small">(ns)</span></td><td>78%</td><td class="bad">not confirmed</td><td>two ERV families up</td></tr>
</table>
<p class="punch bad-b">We pointed that check at our own data and it cost us: SETDB1 — the sole
anchor for one of our two chromatin marks — cannot be confirmed to have worked. <i>Not
confirmed</i>, not <i>failed</i>: it is CRISPRi read as a shallow snapshot, and it did produce
the ERV results. It is now in the limitations.</p>""",
"""Credit TEtranscripts out loud and early — the single thing most likely to be mistaken for
our contribution. Then give the SETDB1 row without flinching. Nobody else will show you a
failed control on their own data.""")

slide("Attacked", "The one result that had to survive, and what it cost",
"""<p>The primary readout is normalisation-invariant by construction:
<span class="mono">&Delta; = median log&#8322;FC over TE subfamilies &minus; median over
protein-coding genes</span>, within one contrast. Size factors are per-sample and
multiplicative, so they shift both sets equally on the log scale and cancel in the difference.</p>
<p class="punch bad-b">An external reviewer found the real flaw: our p-value treated ~350
correlated TE families as independent evidence. We measured the inflation instead of arguing.
<b>Mean pairwise correlation 0.006 to 0.48 &rarr; variance inflation 4&times; to 155&times;</b>
— in two of three contrasts, 322 families carry about <b>two families' worth</b> of
independent information. Those p-values are <b>retracted</b>.</p>
<table class="t">
<tr><th>Challenge</th><th>DNMT1 — the anchor that had to hold</th></tr>
<tr><td>effect size</td><td><b>&Delta; = +0.13</b>, 63% of 503 families up</td></tr>
<tr><td>six ways of defining the TE set</td><td class="ok">same sign <b>6 of 6</b> — LINE +0.19, SINE +0.10, LTR +0.11, DNA +0.10</td></tr>
<tr><td>drop any single library</td><td class="ok">+0.10 … +0.19, <b>sign never flips</b></td></tr>
<tr><td>permute the sample labels</td><td class="ok">most extreme of the 3 admissible labellings, by 3.7&times;</td></tr>
<tr><td>correlation-aware p</td><td><b>0.045</b></td></tr>
</table>
<p class="small">TRIM28's <i>whole-compartment</i> claim did not survive — a permuted labelling
beat the real one — and is now an effect size only. Its per-feature AluY result is a different
statistic and stands. DNMT1 is the anchor the TET2 answer on slide 2 rests on, which is why
this is the slide that mattered.</p>""",
"""Have this ready: with two replicates per arm there are three possible label shufflings, so
no p below 0.333 is reachable — a limit of the experiment, not the analysis. Anyone quoting a
tiny p from a two-replicate design is quoting an artefact.""")

slide("Robustness", "How much of the reasoning rests on how little",
f"""<img class="fig" src="{img('fig_holdout_robustness.png')}" alt="anchor-dependence analysis">
<p class="punch">Remove <b>SETDB1</b> and the derived layer collapses from <b>89 edges to
8</b>. Remove <b>TRIM28</b> — the largest measured effect in the dataset — and <b>nothing
changes</b>, because a scaffold has no writer annotation and cannot satisfy R1. Only
<b>four</b> edges ground the entire inference layer.</p>
<p class="punch ok-b">This is where the graph stops being a database and becomes an
experimental-design tool: it turns &ldquo;we need more data&rdquo; into <b>more writers and
erasers of these two marks</b>. We checked — of 40 such enzymes in the graph, ENCODE has
knockdowns for <b>three</b>, and we have used two. The public well is nearly dry, which is
itself the result.</p>""",
"""The TRIM28-contributes-nothing result is counter-intuitive and worth a pause. It is also
the honest answer to 'what would you do with more compute': a named experiment, not a wish.""")

slide("Refusal", "Four things we built, measured, and did not ship",
"""<table class="t">
<tr><th>Built</th><th>Measured</th><th>Decision</th></tr>
<tr><td>rule-based literature extractor</td><td>precision <b>0.109</b></td><td class="bad">rejected</td></tr>
<tr><td>link prediction on the graph</td><td>no held-out set constructible from 3 knockdowns</td><td class="bad">not built</td></tr>
<tr><td>an interferon conclusion</td><td>reference contained 17% of the signature</td><td class="bad">refused, then fixed</td></tr>
<tr><td>compartment Mann&ndash;Whitney p-values</td><td>variance inflation to 155&times;</td><td class="bad">retracted</td></tr>
</table>
<p class="punch">The interferon arm is the instructive one. We built a panel reference and took
type-I interferon coverage from <b>0.17 to 0.77</b> — and the answer was <i>still</i> a null,
now with a mechanism: in K562 the cytosolic sensors are barely expressed. CGAS 0.21, ZBP1 0.26,
TLR3 0.00 CPM, while the transducers run at 270&ndash;800.</p>
<p><b>The wiring and the sprinklers are installed; the smoke detectors are not.</b> So the
claim is not &ldquo;TE derepression does not cause interferon&rdquo; — it is <i>this dataset
cannot decisively test it, and here is the cell type that could</i>.</p>
<p class="punch ok-b"><span class="mono">best_tier: none</span> is a supported output, not an
error path. That is the whole design.</p>""",
"""If you get one slide past the title, make it this one. Then stop talking and let them
ask.""")

slide("Honestly", "What is weak, what fixes it, and what is next",
"""<table class="t">
<tr><th>Limitation</th><th>What settles it</th></tr>
<tr><td>the whole 5mC arm rests on <b>one</b> contrast, 1.5 M reads across chr1+chr19 — and chr19 is the most gene-dense, Alu-rich chromosome and carries the KRAB-ZFP clusters</td><td>genome-wide, full depth</td></tr>
<tr><td>SETDB1's knockdown efficiency <b>not confirmed</b>, and it anchors 3 of the 4 grounding edges</td><td>the same run</td></tr>
<tr><td>only <b>9 of 55</b> silencing-machinery genes are measurable at current reference scope</td><td>the same run</td></tr>
<tr><td>subfamily resolution, not individual loci — and the field is moving to loci</td><td>Telescope / SQuIRE</td></tr>
<tr><td>two replicates per arm caps any sample-level p at 0.333</td><td>more replicates, not a better test</td></tr>
<tr><td>no <b>time</b>, no position along the chromosome, no dose, and no feedback — every context column for those reads <span class="mono">not_applicable</span></td><td>a dynamical model; scoped, <b>not implemented</b></td></tr>
</table>
<p class="punch">Two adversarial prior-art passes, 279 abstracts, 198 full texts, five novelty
claims retracted — including one we liked. <b>And one search returned a clean zero that we
believed: the paper existed, and its fourth author was in the room.</b> Logged as the fifth
time a check here was caught lying.</p>
<p class="punch ok-b">The ask is specific: <b>writers and erasers of H3K9me3 and 5mC from
outside ENCODE</b>. Everything else is computed, in the repository, and reproducible from one
command.</p>""",
"""The last limitation row is the only place the cellular-automata collaboration appears, and
it is framed as a known representational gap with a scoped answer — say 'designed, not built'
and move on unless asked. If cut to three minutes: slides 1, 2, 5, 7 — the gap, the tool
answering a gene, the surviving result, the refusals.""")

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
.term{background:#0d1219;border:1px solid #27333f;border-radius:7px;padding:.85rem 1rem;
 font:12.4px/1.62 ui-monospace,SFMono-Regular,Menlo,monospace;color:#cfe0f2;overflow-x:auto;margin:.3rem 0 1rem}
.term b{color:#8fe0b6}.term .warn{color:#e8c07a}.term .meas{color:#7fd6a8}
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
