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

slide("Result 1 — the tool", "Ask it about TET2: no annotation, no experiment, still an answer",
"""<pre class="term">$ python src/te_reason.py TET2 --proofs

=== TET2  [best tier: inferred]  measured=0 curated=0 literature=0 inferred=1
Losing TET2 is predicted to <b>lower</b> TE:global, derived by R3_ERASER_INVERSION from:
5mC-MARK_AT-&gt;TE:global, TET2-ERASES_MARK-&gt;5mC   [e0eab062a2cf49c, e62dbe0821f074b]
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
knockdown in ENCODE. The answer is specific, signed, traceable to one real measurement — and
labelled <span class="mono">inferred</span>, not measured. That is problems 4 and 5, answered
in one screen.</p>""",
"""Run it live if you can — under a second. Trace the tree bottom-up with a finger, then
point at the warning line: the system flags that its own conclusion is bound to one cell
type.""")

slide("Result 2 — the measurement", "Three knockdowns, re-counted against the repeat annotation",
"""<p>ENCODE RNA-seq in K562, 11 libraries. HISAT2 reporting up to 100 alignments per read,
TEcount's expectation-maximisation for multi-mapping reads (<b>TEtranscripts — not ours</b>),
DESeq2 with size factors estimated on protein-coding genes only.</p>
<table class="t">
<tr><th>Knockdown</th><th>target's own mRNA</th><th>remaining</th><th>did it work?</th><th>effect on TEs</th></tr>
<tr><td>DNMT1</td><td>&minus;1.87</td><td>27%</td><td class="ok">confirmed</td><td>whole-compartment shift</td></tr>
<tr><td>TRIM28</td><td>&minus;1.12</td><td>46%</td><td class="ok">confirmed</td><td>AluY +0.79, padj 0.0005</td></tr>
<tr><td>SETDB1</td><td>&minus;0.35 <span class="small">(ns)</span></td><td>78%</td><td class="bad">not confirmed</td><td>two ERV families up</td></tr>
</table>
<p class="punch bad-b">We pointed that check at our own data and it cost us: SETDB1 — the sole
anchor for one of our two chromatin marks — cannot be confirmed to have worked. <i>Not
confirmed</i>, not <i>failed</i>: CRISPRi read as a shallow snapshot, and it did produce the
ERV results. It is in the limitations.</p>""",
"""Credit TEtranscripts out loud — the single thing most likely to be mistaken for our
contribution. Then give the SETDB1 row without flinching. Nobody else will show you a failed
control on their own data.""")

slide("Result 3 — attacked", "The one result that had to survive, and what it cost",
"""<p>The readout is normalisation-invariant by construction:
<span class="mono">&Delta; = median log&#8322;FC over TE subfamilies &minus; median over
protein-coding genes</span>, within one contrast — size factors are per-sample and
multiplicative, so they cancel in the difference.</p>
<p class="punch bad-b">A reviewer found the real flaw: our p-value treated ~350 correlated TE
families as independent evidence. We measured the inflation instead of arguing. <b>Mean
pairwise correlation 0.006 to 0.48 &rarr; variance inflation 4&times; to 155&times;</b> — in two
of three contrasts, 322 families carry about <b>two families' worth</b> of independent
information. Those p-values are <b>retracted</b>. This is exactly why CAMERA exists.</p>
<table class="t">
<tr><th>Challenge</th><th>DNMT1 — the anchor slide 5's answer rests on</th></tr>
<tr><td>effect size</td><td><b>&Delta; = +0.13</b>, 63% of 503 families up</td></tr>
<tr><td>six ways of defining the TE set</td><td class="ok">same sign <b>6 of 6</b> — LINE +0.19, SINE +0.10, LTR +0.11, DNA +0.10</td></tr>
<tr><td>drop any single library</td><td class="ok">+0.10 … +0.19, <b>sign never flips</b></td></tr>
<tr><td>permute the sample labels</td><td class="ok">most extreme of the 3 admissible labellings, by 3.7&times;</td></tr>
<tr><td>correlation-aware p</td><td><b>0.045</b></td></tr>
</table>
<p class="small">TRIM28's <i>whole-compartment</i> claim did not survive — a permuted labelling
beat the real one — and is now an effect size only. Its per-feature AluY result is a different
statistic and stands.</p>""",
"""Have this ready: with two replicates per arm there are three label shufflings, so no p
below 0.333 is reachable — a limit of the experiment, not the analysis. Anyone quoting a tiny
p from a two-replicate design is quoting an artefact.""")

slide("Result 4 — what it is for", "The graph tells you which experiment to run next",
f"""<img class="fig" src="{img('fig_holdout_robustness.png')}" alt="anchor-dependence analysis">
<p class="punch">Remove <b>SETDB1</b> and the derived layer collapses from <b>89 edges to
8</b>. Remove <b>TRIM28</b> — the largest measured effect in the dataset — and <b>nothing
changes</b>, because a scaffold has no writer annotation and cannot ground a mark. Only
<b>four</b> edges support the entire inference layer.</p>
<p class="punch ok-b">That turns &ldquo;we need more data&rdquo; into a named experiment:
<b>more writers and erasers of these two marks</b>. We then checked — of 40 such enzymes in
the graph, ENCODE has knockdowns for <b>three</b>, and we have used two. <b>The public well is
nearly dry, and that is the result.</b></p>
<p>Four things were also built, measured, and not shipped: a literature extractor at
precision <b>0.109</b>, link prediction with no constructible held-out set, an interferon
conclusion drawn from a reference holding 17% of the signature, and the p-values retracted on
the previous slide.</p>""",
"""The TRIM28-contributes-nothing result is counter-intuitive and worth a pause. It is also
the honest answer to 'what would you do with more compute' — a named experiment, not a wish.""")

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
