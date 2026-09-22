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
"""<p class="lede">Roughly half the human genome is repeated, mobile DNA. Cells spend real
energy keeping it switched off; when that machinery fails it switches back on, and that is
tied to inflammation and ageing.</p>
<p class="lede"><b>Ask that question of any gene today and five separate things are in your
way.</b> This is which of them already have answers, which do not, and what we built for the
ones that do not.</p>
<p class="meta">Hanae Roussotte &middot; biology knowledge-graph track</p>""",
"""Two sentences of biology, then promise the structure: problems, what exists, what is left.
Saying 'five things are in your way' sets up the next slide and stops you sounding like you
are claiming the whole field is empty.""")

slide("The problems", "Five obstacles, and they are not the same kind of problem",
"""<table class="t">
<tr><th>#</th><th>Problem</th><th>Why it blocks the question</th></tr>
<tr><td><b>1</b></td><td>Repeats are thrown away by default</td><td>Standard RNA-seq pipelines discard multi-mapping reads. Most of the repetitive genome <i>is</i> multi-mapping, so it is invisible unless you deliberately handle it</td></tr>
<tr><td><b>2</b></td><td>Transposable elements are not entities in biomedical knowledge graphs</td><td>You cannot query a relationship whose object does not exist in the schema</td></tr>
<tr><td><b>3</b></td><td>Perturbation data was never read out on repeats</td><td>ENCODE holds <b>1,114 knockdowns across 570 genes</b>, reads public. The measurement was paid for and never made</td></tr>
<tr><td><b>4</b></td><td>Predictions rarely say where they came from</td><td>If a tool tells you gene X silences element Y, you usually cannot tell whether that is a measurement, a curation, a sentence in an abstract, or a model's guess</td></tr>
<tr><td><b>5</b></td><td>Nothing says &ldquo;not enough evidence&rdquo;</td><td>Systems that always answer cannot tell you which answers to distrust</td></tr>
</table>
<p class="punch">1 and 3 are <b>engineering</b>. 2 is a <b>schema</b> problem. 4 and 5 are
<b>epistemic</b> — and they are the ones that do not go away with more data.</p>""",
"""Say the last line deliberately. It is the slide's whole purpose: separating the problems
that compute solves from the problems that design solves. Judges who build tools will
recognise 4 and 5 as the hard ones.""")

slide("What already exists", "Most of this is solved, and by people who are not us",
"""<table class="t">
<tr><th>Problem</th><th>Already solved by</th><th>Status</th></tr>
<tr><td><b>1</b> handling repeats</td><td><b>TEtranscripts / TEcount</b> (Jin 2015, 10.1093/bioinformatics/btv422) — <i>we use it</i>. Alternatives at locus level: Telescope (10.1371/journal.pcbi.1006453), SQuIRE (10.1093/nar/gky1301), MAJEC (2026). <b>16 tools have been benchmarked</b> (10.1093/gpbjnl/qzag044)</td><td class="ok">solved</td></tr>
<tr><td><b>1&prime;</b> where repeats are active</td><td><b>Atlases exist and dwarf us</b> — TE-SCALE, 1.3 M cells / 20 cancer types (10.1093/nar/gkaf1235) · TEITbase, 33 cancer types (10.1093/database/baag025) · REdiscoverTE across TCGA (10.1038/s41467-019-13035-2)</td><td class="ok">solved</td></tr>
<tr><td><b>3</b> screening for regulators</td><td><b>Done repeatedly</b> — <i>C. elegans</i> RNAi 2003, <i>Drosophila</i> 2013, human L1 screens (<i>Nature</i> 2018, 10.1038/nature25179), CRISPR L1 regulators 2025</td><td class="ok">solved</td></tr>
<tr><td><b>2</b> graphs and TE networks</td><td>PrimeKG (10.1038/s41597-023-01960-3), Hetionet (10.7554/elife.26726) — 10 and 11 node types, none a TE. TE-specific networks do exist: TEKRABber (10.7554/elife.103608), PlaNC-TE in plants (10.1093/database/bay078)</td><td class="bad">partial</td></tr>
<tr><td>predicting perturbation response</td><td><b>GEARS</b> (10.1038/s41587-023-01905-6), <b>TxPert</b> (10.1038/s41587-026-03113-4), scPerturb (10.1038/s41592-023-02144-y)</td><td class="bad">not for TEs</td></tr>
<tr><td>set-level statistics</td><td><b>GSEA</b> (10.1073/pnas.0506580102), <b>CAMERA</b> (10.1093/nar/gks461) — our compartment test is a variant of an established idea, not a new one</td><td class="ok">solved</td></tr>
</table>
<p class="punch">Industry too: <b>ROME Therapeutics</b> built a company on the repeat genome and
solved the LINE-1 ORF2p structure. Ahead of us on biology. <span class="small">(Their published
science is verified; their platform description I could not check from this environment, and
I say so rather than guess.)</span></p>""",
"""This is the slide that wins trust, and the instinct to skip it is exactly wrong. Say
'solved' out loud six times. Five of our own novelty claims were retracted after two
adversarial prior-art passes — 279 abstracts, 198 full texts — and naming that before anyone
asks removes the entire attack surface.""")

slide("The gap", "What is left once you credit all of that",
"""<p class="punch bad-b">Every atlas above answers <b>where</b> transposable elements are
active — which tissue, which tumour, which cell. None of them answers <b>what perturbation
changed them, through what mechanism, and what to test next.</b> Observational versus
interventional. That axis is comparatively empty.</p>
<p>And the two epistemic problems, 4 and 5, are untouched by any of it. So the residual gap is
narrow and specific:</p>
<table class="t">
<tr><th>Gap</th><th>What we built for it</th></tr>
<tr><td>a perturbation read out on the repeat genome becomes a <b>signed, sourced relationship</b></td><td>27 measured edges from re-analysed ENCODE knockdowns, each carrying accession, statistic, date and a stable id</td></tr>
<tr><td>those relationships sit in <b>one schema</b> with curated mechanism, so they can be reasoned over</td><td>9,366 typed edges across four evidence layers; transposable elements are first-class nodes</td></tr>
<tr><td>a conclusion's <b>trust level is computed, not asserted</b></td><td>tier = the weakest link on the derivation path, and the path is printed</td></tr>
<tr><td>the system can <b>decline</b></td><td><span class="mono">best_tier: none</span> is a supported output, not an error</td></tr>
</table>
<p class="punch ok-b">Stated honestly: <b>every component here has precedent. The assembly did
not surface in two independent searches</b> — which is a `NOT_FOUND`, and still not proof of
absence.</p>""",
"""The axis sentence — observational versus interventional — is the one to memorise. And end
on the NOT_FOUND caveat yourself; a claim of novelty that names its own limit is much harder
to attack than one that does not.""")

slide("Result 1 — real data", "The TE compartment moves as a whole",
f"""<img class="fig tall" src="{img('fig_ev1_data.png')}" alt="TE versus gene log2FC distributions">
<p class="punch">Look at <b>DNMT1</b>. <b>Zero</b> individual TE families clear FDR — best padj
0.41 — yet the whole compartment is displaced. A per-feature search finds nothing here; the
compartment statistic finds a coherent shift. <b>&Delta; = +0.13</b>, same sign in <b>6/6</b>
feature-set variants, stable to dropping any library, correlation-aware <b>p = 0.045</b>.</p>
<table class="t">
<tr><th>Knockdown</th><th>target's own mRNA</th><th>did it work?</th></tr>
<tr><td>DNMT1</td><td>&minus;1.87 (27% remaining)</td><td class="ok">confirmed</td></tr>
<tr><td>TRIM28</td><td>&minus;1.12 (46% remaining)</td><td class="ok">confirmed</td></tr>
<tr><td>SETDB1</td><td>&minus;0.35, ns (78% remaining)</td><td class="bad">not confirmed</td></tr>
</table>
<p class="small">TRIM28's &Delta; = +0.42 is shown as an <b>effect size</b>: a permuted labelling
beat the real one, so its compartment p-value is retracted. Its per-feature AluY result
(padj 0.0005) is a different statistic and stands. Counted with <b>TEtranscripts, Jin et al.
2015 — not ours.</b></p>""",
"""Point at the DNMT1 panel and say the sentence: zero significant families, clear compartment
shift. Then the efficiency table without flinching — SETDB1 is our own failed control and
nobody else will show you one.""")

slide("Result 2 — the proof", "Not a lookup: the answer is a chain you can audit",
f"""<img class="fig tall" src="{img('fig_ev2_proof.png')}" alt="TET2 proof tree with evidence tiers">
<p class="punch">TET2 has <b>no</b> transposon annotation in the Gene Ontology and <b>no</b>
knockdown in ENCODE. The prediction is nevertheless specific, directional, and traceable to
<b>one real measurement</b> — and every edge is labelled with the kind of evidence it is.</p>
<p>A conclusion's tier is the <b>weakest link on its path</b>, so this answer is
<span class="mono">inferred</span>, never <span class="mono">measured</span>. Run it yourself:
<span class="mono">python src/te_reason.py TET2 --proofs</span></p>""",
"""Trace it with a finger: one measurement, two ontology records, a directional claim. That is
problem 4 answered. If you have a laptop, run the command instead — under a second, and it
prints the same tree with its citation ids.""")

slide("Result 3 — refusal", "It recognises missing evidence, fixes it, and still accepts a null",
f"""<img class="fig" src="{img('fig_ev3_refusal.png')}" alt="refusal, rebuild, null">
<p class="punch">The interferon question came back <b>refused</b>, not answered: the reference
held 17% of the signature, below the coverage guard. So we built a targeted 62 Mb reference,
took coverage to <b>77%</b>, and re-ran — and the answer was <i>still</i> a null.</p>
<p class="punch ok-b">The null then got a mechanism: in K562 the cytosolic sensors are barely
expressed. <b>The wiring and the sprinklers are installed; the smoke detectors are not.</b> So
the claim is not &ldquo;TE derepression does not cause interferon&rdquo; — it is <i>this dataset
cannot decisively test it, and here is the cell type that could</i>.</p>
<p class="small">Three more things were built, measured and not shipped: a literature extractor
at precision 0.109, link prediction with no constructible held-out set, and the p-values
retracted on the previous slide. <span class="mono">best_tier: none</span> is a supported
output, not an error path.</p>""",
"""Problem 5, and the slide nobody else will have. The beat that lands is 'refused, fixed the
computation, and the answer was still no'.""")

slide("Result 4 — what it is for", "It tells you which experiment to run next",
f"""<img class="fig" src="{img('fig_ev5_priority.png')}" alt="experiment priority by mark">
<p class="punch"><b>78 of 83 derived edges rest on H3K9me3</b> — a mark grounded by SETDB1
alone, the one knockdown whose efficiency we could <i>not</i> confirm. 5mC carries 5 and is
grounded by DNMT1 alone. H3K27me3 has <b>zero</b> groundings, so nothing about it can be
derived at all. Remove TRIM28, the largest measured effect, and the reasoning is
<b>unchanged</b>: a scaffold cannot ground a mark.</p>
<p class="punch ok-b">So the ranking is computed, not asserted: the <b>26 H3K9me3 writers and
erasers</b> in the graph would each corroborate 78 edges — and <b>not one has a public
knockdown</b>. The only ENCODE option left is DNMT3B, which corroborates the arm worth 5.
<b>That gap is the ask</b>, and it is an experimental-design output rather than a wish list.</p>
<p class="small">Value proxy = derived edges that would gain a second independent grounding. A
count of exposure, not an expected-information calculation, and the figure says so.</p>""",
"""More interesting than 'we have 9,366 edges'. A system that shows where its own reasoning is
fragile, rather than hiding it, is the thing worth having.""")

slide("Honestly", "What is weak, what compute would buy, and the ask",
"""<div class="two">
<div class="card"><h3>The binding limitations</h3>
<p class="small">&bull; the whole 5mC arm rests on <b>one</b> contrast, 1.5 M reads across
chr1+chr19 — and chr19 is the most gene-dense, Alu-rich chromosome<br>
&bull; SETDB1's efficiency <b>not confirmed</b>, and it anchors 3 of 4 grounding edges<br>
&bull; only <b>9 of 55</b> silencing-machinery genes measurable at this reference scope<br>
&bull; subfamily resolution, not loci — the field is moving to loci<br>
&bull; two replicates per arm caps any sample-level p at <b>0.333</b><br>
&bull; no time, position, dose or feedback — those context columns read
<span class="mono">not_applicable</span> throughout</p></div>
<div class="card"><h3>What compute buys, costed</h3>
<p class="small">A genome-wide re-run at 30 M reads fixes the <b>first four at once</b>:
retires the two-chromosome bias, lifts machinery coverage, settles the SETDB1 question, and
retires the interferon coverage guard because its 725 genes become present by construction.</p>
<p class="small ok-b">The pipeline is written, containerised and <b>dry-run validated</b>
(<span class="mono">src/modal_app.py</span>). Pre-flight found three defects that would each
have wasted the run — including a setup step that reported success while never building the
annotation the counter needs.</p>
<p class="small bad-b"><b>Not launched today, deliberately.</b> The shared reference build is
a 1&ndash;2.5 h critical path and there are 90 minutes. Spending credits on a run that cannot
finish would be theatre.</p></div>
</div>
<p class="punch">Two adversarial prior-art passes, 279 abstracts, 198 full texts, five novelty
claims retracted — including one we liked. <b>And one search returned a clean zero we believed:
the paper existed, and its fourth author was in the room.</b></p>
<p class="punch ok-b">The ask is specific: <b>writers and erasers of H3K9me3 and 5mC from
outside ENCODE</b>. Everything else is computed, in the repository, and reproducible from one
command.</p>""",
"""If asked why you did not run it: because the critical path is longer than the time, and
naming that is better than a half-finished job. The pre-registration is the artefact proving
the interpretation was fixed before the data was opened. Three-minute cut: slides 2, 3, 4, 5.""")

slide("Appendix", "What a dynamical layer could add to knowledge-graph research",
"""<p class="lede">Not specific to this project. Four things <b>no</b> knowledge graph can
represent, in any domain — consequences of the representation, not gaps in the data.</p>
<table class="t">
<tr><th>What a graph cannot hold</th><th>Why</th><th>What it costs you</th></tr>
<tr><td><b>time</b></td><td>forward chaining reaches a fixpoint, and a fixpoint has no clock</td><td>&ldquo;X silences Y&rdquo; cannot distinguish an immediate effect from one taking ten cell divisions</td></tr>
<tr><td><b>position</b></td><td>a node is an identity, not a coordinate</td><td>one node here stands for up to 104,272 scattered loci with no spatial relation to each other</td></tr>
<tr><td><b>dose</b></td><td>a signed edge has no magnitude axis</td><td>partial and complete loss of function are the same edge</td></tr>
<tr><td><b>feedback</b></td><td>chaining to a fixpoint does not model a cycle — it <i>ignores</i> one</td><td>our cGAS path <b>is</b> a cycle, so its acyclic reading is known to be wrong</td></tr>
</table>
<p class="punch">A cellular automaton is local rules applied over time on a lattice. It is
<b>natively</b> temporal, spatial, quantitative and cyclic — exactly the four axes a graph gives
up in exchange for provenance.</p>
<p class="small">The track record is not speculative: Turing 1952 (local rules generate pattern),
Moe 1964 (a cardiac automaton reproducing fibrillation), Kauffman 1969 (random Boolean networks
settling into few stable states), Li 2004 (yeast cell cycle), Anderson <i>Cell</i> 2006 (tumour
morphology under microenvironmental selection), PhysiCell 2018.</p>""",
"""Only open the appendix if asked. The framing: these are not missing data, they are the price
of a representation that carries provenance. Naming the trade is stronger than pretending it is
not there.""")

slide("Appendix", "How the two would compose — and the conditions for believing it",
"""<div class="two">
<div class="card"><h3>The asymmetry, stated precisely</h3>
<p class="small">The automaton supplies <b>structure with no referents</b>: its cells are not
loci, its states are not molecules, nothing in it has a source, and nothing in it could be
falsified by an experiment.</p>
<p class="small">The graph supplies <b>referents with evidence and no dynamics</b>: every node is
a named entity, every edge carries a citation and a tier, and none of it moves.</p>
<p class="small ok-b">Complements, not competitors — the useful direction is the automaton
proposing <i>phenomena to look for</i> and the graph naming <i>which entities could instantiate
them</i>.</p></div>
<div class="card"><h3>One case where it would earn its place</h3>
<p class="small">A deterministic rule engine gives one direction per gene for all targets. It
<b>cannot produce a split</b> — and our own cohort splits: DNMT3A-mutant carriers divide into
RTE-high and RTE-low by <i>which</i> mutation they carry.</p>
<p class="small">Bimodality from identical parameters is a generic property of bistable
stochastic local-rule models. So it is a candidate <b>explanation</b> for a pattern the current
model cannot generate at all.</p></div>
</div>
<p class="punch bad-b"><b>Three conditions, or it is decoration.</b> (1) Pre-commit the
biological prediction <i>before</i> looking at the graph — in 9,366 relationships you will
always find something analogous to any principle you bring. (2) The abstract side needs its own
null model: &ldquo;recovery uses few dimensions&rdquo; may just be what search in low dimensions
always looks like. (3) Simulated output carries a tier <b>below</b>
<span class="mono">inferred</span> and can never ground a rule — using it to fill edges would be
the link prediction we already refused, and a simulation does not create validation data.</p>
<p class="punch ok-b">And a falsifier fixed in advance: the first buildable version predicts
per-locus derepression depends on <b>distance to the nearest nucleation site and local
density</b>, not on subfamily identity — refutable with a locus-level quantifier. <b>If it
fails, the model is dropped, not tuned.</b> Design in
<span class="mono">docs/CELLULAR_AUTOMATA.md</span>; nothing from it is implemented, and nothing
from it is in any number on the previous slides.</p>""",
"""If pressed on why it is not built: because the three conditions are not met, and a dynamical
model that has not met them adds free parameters rather than knowledge. Saying that is the
answer.""")

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
