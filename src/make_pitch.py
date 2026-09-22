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

# ================================================================== ACT I — the method
slide("", "From simple rules to a real biological question",
"""<p class="lede">A cellular automaton is the simplest thing that can be called a model of a
living system: a row of cells, each one recolouring itself from its own colour and its two
neighbours', over and over.</p>
<p class="lede"><b>It produces rules you could not have guessed — and it cannot tell you
anything about a named gene.</b> This is about joining that to a graph of real, cited,
measured biology, and what happened when we did.</p>
<p class="meta">Hanae Roussotte &middot; with a cellular-automata collaborator &middot;
biology knowledge-graph track</p>""",
"""Do not start with transposable elements. Start with the automaton — everyone in the room
follows it, and it earns you the right to the specific biology later. The two-sentence shape
of the whole talk is: this method finds rules but has no nouns; a knowledge graph is nothing
but nouns with evidence.""")

slide("1 — The method", "Eight numbers decide everything",
f"""<img class="fig tall" src="{img('fig_ca_intro.png')}" alt="four elementary cellular automata">
<p class="punch">Each panel starts from <b>one black cell</b> and applies its own eight-case
rule. Nothing differs between them but those eight outputs — and you get uniform growth, an
exact fractal, chaos, and localised structures that collide and compute.</p>
<p>Wolfram's classification of these four behaviours
(<span class="mono">Rev. Mod. Phys.</span> 1983) is the founding result: <b>you cannot read
the behaviour off the rule.</b> You have to run it.</p>""",
"""Point at Rule 30 and Rule 90 and say: same architecture, one number changed. Rule 110 is
provably capable of universal computation — a rule you could write on your hand. This slide
is 40 seconds and it does all the conceptual work for the rest of the talk.""")

slide("2 — Why biology cares", "Local rules reproduce phenomena no equation was written for",
"""<div class="two">
<div class="card"><h3>The track record is real</h3>
<p class="small"><b>Turing, 1952</b> — local interaction alone generates stripes and spots,
before anything was known about the molecules.<br>
<b>Moe, 1964</b> — a cellular automaton of cardiac tissue reproducing atrial fibrillation.<br>
<b>Kauffman, 1969</b> — random Boolean networks settling into a small number of stable
states, proposed as cell types.<br>
<b>Li et al., 2004</b> — the yeast cell-cycle network is robust <i>as a network</i>.<br>
<b>Anderson et al., <i>Cell</i> 2006</b> — a hybrid automaton showing tumour morphology
driven by microenvironmental selection.<br>
<b>PhysiCell, 2018</b> — the modern multicellular simulator, in routine use.</p></div>
<div class="card"><h3>What the method actually buys</h3>
<p class="small"><b>You can enumerate.</b> Every possible perturbation, every possible
intervention — impossible in any real organism.</p>
<p class="small"><b>You get generic phenomena.</b> Bistability, travelling waves, spontaneous
recovery, threshold effects — these emerge from the <i>structure</i> of local interaction, not
from the biochemistry, so they should appear in any system with that structure.</p>
<p class="small"><b>You find rules, not parameters.</b> The output is a statement of the form
&ldquo;systems like this recover in this way&rdquo;.</p></div>
</div>
<p class="punch ok-b">That is a genuinely different kind of knowledge from a measurement, and
the field has been extracting it for seventy years.</p>""",
"""Six references, all resolvable, all checked by our citation gate. The point to land is
the middle card: enumeration and generic phenomena. If a modeller is in the room this is
where they relax, because you are not overselling.""")

slide("3 — The frontier", "The metamodel of medicine, run end to end",
f"""<img class="fig tall" src="{img('ca_worked_example.png')}" alt="disease and treatment enumerated">
<p>Following Wolfram's <i>Foundations of Medicine</i> framing: the <b>organism</b> is a
pattern that grows and dies (ours at step 117), a <b>disease</b> is changing one cell, a
<b>treatment</b> is changing a second. Now enumerate.</p>
<div class="two">
<div class="card"><h3>All 3,447 possible diseases</h3>
<p class="small"><b>8% heal themselves</b> with no treatment · 10% shorten life · 50% extend
it · <b>32% grow without bound</b>.</p>
<p class="small">Wolfram's own organism self-heals at 8.7%; ours, found independently, at
8.2%. A property of the class, not of one lucky rule.</p></div>
<div class="card"><h3>All 1,479 possible treatments</h3>
<p class="small"><b>6 cure</b> (0.4%) · <b>195 (13%) cause unbounded, tumour-like growth</b> ·
79 are worse than the disease.</p>
<p class="small">And <b>every cure leaves 1,622 cells changed</b>. The lifetime is restored
exactly; the life is not the same life.</p></div>
</div>""",
"""These four facts are the reason to care: cures are rare, intervening is not free, nearby
treatments behave completely differently, and side effects are unavoidable. All four fall out
of arithmetic on a toy — no biology assumed. Say that explicitly.""")

slide("4 — The limitation", "Now name a gene",
"""<p class="punch bad-b">Everything on the previous slide is true of <b>a pattern of
coloured squares</b>. The four colours are not molecules. Cell 60 is not a locus. There is no
gene, no protein, no citation, and nothing that could be looked up or falsified by an
experiment.</p>
<div class="two">
<div class="card"><h3>What it cannot do</h3>
<p class="small">&bull; Say which <i>real</i> perturbation corresponds to its disease<br>
&bull; Say which <i>real</i> molecule could be its treatment<br>
&bull; Be checked against a measurement<br>
&bull; Carry provenance — nothing in it has a source<br>
&bull; Be wrong in a way anyone could detect</p></div>
<div class="card"><h3>And the honest version of its strength</h3>
<p class="small">A model with many free parameters, fitted to nothing, will reproduce
<i>some</i> qualitative phenomenon whatever the biology. That is why &ldquo;our simulation
looks like the disease&rdquo; is the weakest sentence in computational biology.</p>
<p class="small ok-b">The way out is not a better simulation. It is to make the model's
statements <b>point at named entities that carry evidence</b>.</p></div>
</div>
<p class="punch">The method has <b>rules without nouns</b>. So: find something that is
nothing but nouns, each with a citation.</p""",
"""This is the pivot and it must be said without defensiveness — the collaborator's method
is strong AND it cannot reach a gene. Landing the limitation yourself is what makes the next
slide land. 'Rules without nouns' is the phrase to remember.""")

# ================================================================== ACT II — the complement
slide("5 — The complement", "A knowledge graph is nouns with evidence attached",
"""<div class="layers">
<div class="L c"><b>curated</b><span>9,263 edges</span><em>Gene Ontology &middot; STRING v12 &middot; Reactome &middot; Complex Portal</em></div>
<div class="L m"><b>mechanism</b><span>44 edges</span><em>which enzyme writes or erases which chromatin mark</em></div>
<div class="L e"><b>measured</b><span>27 edges</span><em>our own re-analysis &mdash; signed, dated, and reproducible</em></div>
<div class="L l"><b>literature</b><span>tiered lowest</span><em>extracted, unvalidated, and never permitted to ground a rule</em></div>
</div>
<p class="punch">Every edge carries a source, a retrieval date, a stable id and an evidence
tier. Rules chain forward to a fixpoint; a conclusion's tier is <b>the weakest link on its
path</b>, and every answer prints the derivation that produced it.</p>
<p class="punch ok-b">So the two halves are complementary in a precise way, not a rhetorical
one: <b>the automaton supplies structure with no referents; the graph supplies referents with
evidence and no dynamics.</b> The graph can name what a perturbation is, what a candidate
treatment would be, and refuse when it cannot.</p>
<p class="small">Structural audit, <span class="mono">make validate</span>: 42 metrics.
<b>0</b> schema violations across 9,366 typed edges, <b>0</b> duplicate triples, <b>100%</b>
provenance, 97.6% in one connected component. It also found a real defect — one gene&ndash;TE
pair asserted in <i>both</i> directions, both edges from the <i>same abstract</i>. Kept, not
deleted: that is the literature layer's error rate becoming visible.</p>""",
"""Say 'referents' once and then say 'nouns'. Lead the audit with the defect it found, not
the metrics it passed — volunteering a flaw buys more credibility than five clean numbers.
If asked whether a clean structure means the edges are true: no, and say it flatly.""")

# ================================================================== ACT III — the instance
slide("6 — The example", "Transposable elements: the case where the nouns were missing",
"""<div class="two">
<div class="card"><h3>The biology</h3>
<p class="small">Roughly half the human genome is repeated, mobile DNA. Cells spend real
energy keeping it switched off, using chemical marks. When that machinery fails the elements
switch back on — and that is tied to inflammation and ageing.</p></div>
<div class="card"><h3>Excluded twice over</h3>
<p class="small"><b>Out of the graphs.</b> The major biomedical knowledge graphs do not model
transposable elements as first-class entities — PrimeKG has 10 principal node types, Hetionet
11, and none is a transposable element.</p>
<p class="small"><b>Out of the experiments.</b> ENCODE holds <b>1,114 knockdowns across 570
genes</b>, public reads. Standard pipelines discard multi-mapping reads — which is most of the
repetitive genome. The measurement was paid for and never made.</p></div>
</div>
<p class="punch">This is why it is the right test case. The automaton has no nouns; for
transposable elements, <b>biology had no nouns either.</b> We had to build them before either
method could say anything.</p>""",
"""Both claims are narrowed on purpose — 'not as first-class entities', not 'no graph has
TEs'. The positioning survived two adversarial prior-art passes, and if pushed, concede and
cite TEKRABber immediately.""")

slide("7 — What we measured", "Three knockdowns, re-counted against the repeat genome",
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
<p class="punch bad-b">We pointed that efficiency check at our own data <b>today</b>, and it
cost us: SETDB1 — the sole anchor for one of our two chromatin marks — cannot be confirmed to
have worked. <i>Not confirmed</i>, not <i>failed</i>: it is CRISPRi read as a shallow
snapshot, and it did produce the ERV results.</p>""",
"""Credit TEtranscripts out loud — it is the single thing most likely to be mistaken for our
contribution. Then give the SETDB1 row flatly. Nobody else will show you a failed control on
their own data, and that is exactly why it works.""")

slide("8 — Attacked", "The one result that had to survive, and what it cost",
"""<p>Our primary readout is normalisation-invariant by construction:
<span class="mono">&Delta; = median log&#8322;FC over TE subfamilies &minus; median over
protein-coding genes</span>, within one contrast. Size factors are per-sample and
multiplicative, so they shift both sets equally on the log scale and cancel in the difference.</p>
<p class="punch bad-b">An external reviewer found the real flaw: our p-value treated ~350
correlated TE families as independent evidence. We measured the inflation rather than arguing
about it. <b>Mean pairwise correlation 0.006 to 0.48 &rarr; variance inflation 4&times; to
155&times;</b> — in two of three contrasts, 322 families carry about <b>two families' worth</b>
of independent information. Those p-values are <b>retracted</b>.</p>
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
statistic and stands.</p>""",
"""The line to have ready: with two replicates per arm there are three possible label
shufflings, so no p below 0.333 is reachable — a limit of the experiment, not the analysis.
Anyone quoting a tiny p from a two-replicate design is quoting an artefact.""")

slide("9 — Reasoning", "One measurement reaches genes nobody assayed",
"""<div class="two">
<div class="card"><h3>The rules</h3>
<p class="small"><b>R1</b> grounds a mark on a TE from a measured writer effect ·
<b>R2</b> transfers to other writers of that mark · <b>R3</b> inverts the sign for erasers ·
<b>R4</b> needs complex consensus · <b>R6</b> demands TE derepression <i>and</i> inflammation
in the same contrast — and has <b>never fired</b>.</p>
<p class="small">89 derived edges from 27 measured ones, each printing its proof.</p></div>
<div class="card"><h3>The worked case</h3>
<p class="small">From the DNMT1 measurement plus two Gene Ontology records, the engine derives
<b>DNMT3A loss raises TEs</b> and <b>TET2 loss lowers them</b> — opposite signs on one axis,
having seen data for neither gene.</p>
<p class="small bad-b">That hypothesis is published and <b>I am a co-author</b>
(<i>GeroScience</i> 2026). This instruments my own prior finding; it does not confirm it.</p></div>
</div>
<p class="punch">What is not trivial: the rule commits to a <b>direction</b> the paper's own
hypothesis does not state — TEs go <i>down</i> when TET2 is lost — and the measured cohort
trends that way, across a different quantifier, resolution, perturbation type and tissue.</p>""",
"""Disclose the co-authorship in the same breath as the citation, every time. 'An independent
paper confirms our prediction' is falsifiable in ten seconds from the author list.""")

slide("10 — Robustness", "How much of the reasoning rests on how little",
f"""<img class="fig" src="{img('fig_holdout_robustness.png')}" alt="anchor-dependence analysis">
<p class="punch">Remove <b>SETDB1</b> and the derived layer collapses from <b>89 edges to
8</b>. Remove <b>TRIM28</b> — the largest measured effect in the dataset — and <b>nothing
changes</b>, because a scaffold has no writer annotation and cannot satisfy R1. Only
<b>four</b> edges ground the entire inference layer.</p>
<p class="punch ok-b">This is where the graph stops being a database and becomes an
experimental-design tool: it converts &ldquo;we need more data&rdquo; into <b>more writers and
erasers of these two marks</b>. We then checked — of 40 such enzymes in the graph, ENCODE has
knockdowns for <b>three</b>, and we have used two. The public well is nearly dry, which is
itself the result.</p>""",
"""The TRIM28-contributes-nothing result is counter-intuitive and worth a pause. It is also
the honest answer to 'what would you do with more compute' — a named experiment, not a wish.""")

slide("11 — Refusal", "Four things we built, measured, and did not ship",
"""<table class="t">
<tr><th>Built</th><th>Measured</th><th>Decision</th></tr>
<tr><td>rule-based literature extractor</td><td>precision <b>0.109</b></td><td class="bad">rejected</td></tr>
<tr><td>link prediction on the graph</td><td>no held-out set constructible from 3 knockdowns</td><td class="bad">not built</td></tr>
<tr><td>an interferon conclusion</td><td>reference contained 17% of the signature</td><td class="bad">refused, then fixed</td></tr>
<tr><td>compartment Mann&ndash;Whitney p-values</td><td>variance inflation to 155&times;</td><td class="bad">retracted today</td></tr>
</table>
<p class="punch">The interferon arm is the instructive one. We built a panel reference and took
type-I interferon coverage from <b>0.17 to 0.77</b> — and the answer was <i>still</i> a null,
now with a mechanism: in K562 the cytosolic sensors are barely expressed. CGAS 0.21, ZBP1
0.26, TLR3 0.00 CPM, while the transducers run at 270&ndash;800.</p>
<p><b>The wiring and the sprinklers are installed; the smoke detectors are not.</b> So the
claim is not &ldquo;TE derepression does not cause interferon&rdquo; — it is <i>this dataset
cannot decisively test it, and here is the cell type that could</i>.</p>""",
"""If you get one slide past the title, make it this one. 'best_tier: none' as a supported
output rather than an error path is the thing nobody else in the room will have.""")

slide("12 — The join", "Why the two halves need each other, stated precisely",
"""<div class="two">
<div class="card"><h3>What the automaton gives the graph</h3>
<p class="small">A question the graph cannot pose: <b>what would a treatment even look
like?</b> Rare, side-effect-laden, 13% actively harmful, and not reachable by interpolation.
It also names phenomena to go looking for — bistability being the sharpest, because our data
already contains an unexplained split.</p></div>
<div class="card"><h3>What the graph gives the automaton</h3>
<p class="small">Nouns with evidence. A candidate rescue is not &ldquo;dimension 3&rdquo; but
<i>a named enzyme with a Gene Ontology annotation, a measured effect, and a tier</i>. And a
refusal when there is nothing to say.</p></div>
</div>
<p class="punch ok-b"><b>Both halves inherit the same limit:</b> computational irreducibility
— the only way to know what a rule does is to run it. But irreducible processes contain
<b>pockets of reducibility</b>, and a provenance-bearing graph is precisely a map of them.
<b>The refusals mark where the map ends.</b></p>
<p class="punch">Which also explains the bistability match. In the metamodel, rule cases never
used while the organism is healthy make variants <i>indistinguishable</i> until a perturbation
arrives. In our own cohort, DNMT3A carriers split <b>RTE-high versus RTE-low by which
mutation they carry</b> — same gene, same diagnosis, opposite behaviour. Generic in the model;
real in the patients.</p>""",
"""The thesis sentence, verbatim. It reframes every refusal in the talk from timidity into
the correct response to irreducibility — and it is the most defensible thing either half says
alone.""")

slide("13 — Honestly", "What is weak, and exactly what fixes each thing",
"""<table class="t">
<tr><th>Limitation</th><th>What settles it</th></tr>
<tr><td>the whole 5mC arm rests on <b>one</b> contrast, 1.5 M reads across chr1+chr19 — and chr19 is the most gene-dense, Alu-rich chromosome and carries the KRAB-ZFP clusters</td><td>genome-wide, full depth</td></tr>
<tr><td>SETDB1's knockdown efficiency <b>not confirmed</b>, and it anchors 3 of the 4 grounding edges</td><td>the same run</td></tr>
<tr><td>only <b>9 of 55</b> silencing-machinery genes are measurable at current reference scope</td><td>the same run</td></tr>
<tr><td>subfamily resolution, not individual loci — and the field is moving to loci</td><td>Telescope / SQuIRE</td></tr>
<tr><td><b>no rescue experiment exists in ENCODE</b> — every public experiment is a single perturbation</td><td>control vs disease vs disease + candidate rescue</td></tr>
<tr><td>two replicates per arm caps any sample-level p at 0.333</td><td>more replicates, not a better test</td></tr>
<tr><td>the abstract side's &ldquo;principles&rdquo; are so far descriptions of one model</td><td>a null model, then held-out disturbances</td></tr>
</table>
<p class="punch">Two adversarial prior-art passes, 279 abstracts, 198 full texts, five novelty
claims retracted — including one we liked. <b>And one search returned a clean zero that we
believed: the paper existed, and its fourth author was in the room.</b> Logged as the fifth
time a check in this project was caught lying.</p>
<p class="punch ok-b">The ask is specific. <b>Writers and erasers of these two marks from
outside ENCODE</b>, and <b>one rescue experiment</b>. Everything else here is computed, in the
repository, and reproducible from a single command.</p>""",
"""Close on the ask. If you are cut to three minutes: slides 1, 3, 4, 5, 8, 12 — method,
enumeration, limitation, complement, the surviving result, the join. That is the whole
argument.""")

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
