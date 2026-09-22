# Presentation guide: every slide, explained

**Purpose.** So that by tomorrow morning you can stand up without notes and defend every
number on the screen. For each of the 12 slides: what it shows, **what to say**, *why it is
there*, and **the number you must be able to defend**.

Open `demo/presentation.html` in any browser. Arrow keys navigate, `f` for fullscreen, `s`
hides the speaker notes. The notes are already in the file — this document is the deeper
version.

**The one rule for the whole talk:** every number on screen is either measured by us or
flagged as inferred. If you are asked something you have not measured, *say so and name the
experiment that would settle it.* That is the demo, not a failure of it.

---

## Slide 1 — Title

> Evidence-Traceable Neurosymbolic Reasoning for Transposable-Element Regulation

**Say:** "What does this gene do to transposable-element activation — and how would you
know?"

**Why the second half matters.** The first half is a lookup question. The second half is
the project. Lead with the epistemics because that is what is unusual here.

---

## Slide 2 — Transposable elements are excluded twice over

**Shows:** two boxes. From the data: standard pipelines discard multi-mapping reads. From
the graph: the major biomedical knowledge graphs do not model TEs as first-class entities.

**Say:** "Half your genome is repeat-derived — 3.8 million transposable element copies. TEs
are repeated *by definition*, so the reads that report on them are exactly the reads a
standard pipeline throws away. And separately, the graphs where you would record what you
learn have nowhere to put a TE."

**Defend this number:** *3,761,678 copies across 1,057 subfamilies.* Ours, computed from
hg38 RepeatMasker after three filters — TE classes only, ≥100 bp, main chromosomes.
`data/graph/te_subfamilies_hg38.csv`.

**The phrasing trap.** Say **"do not model TEs as first-class entities"**. Do **not** say
"no knowledge graph has TEs" — an ontology for *bacterial* mobile elements exists (ICEO),
and the slide names it so the scoping is visible. Someone in that room may know it.

---

## Slide 3 — The tool

**Shows:** the five evidence layers and what feeds each.

**Say:** "One graph, five layers, and each edge carries an evidence tier saying how much you
should believe it. The layer that is ours is `measured` — our own re-analysis of
perturbation experiments whose authors never counted transposable elements."

**Why tiers, in one line:** *a conclusion inherits the weakest tier on its path.* Not the
average — a chain is as strong as its weakest link.

---

## Slide 4 — Built on data nobody had re-quantified

**Shows:** the ENCODE inventory.

**Say:** "ENCODE has 1,114 human knockdown RNA-seq experiments across 570 genes. Almost
none were designed to study transposable elements. The reads have been public for years;
the TE signal in them was never counted."

**Defend:** *1,114 experiments, 570 target genes, 1,060 with paired-end FASTQ.* Ours, from
the ENCODE API. `data/graph/encode_kd_inventory.csv`.

**Credit, on this slide:** the quantifier is **TEcount, from TEtranscripts** (Jin *et al.*
2015). Say it out loud. Telescope, SQuIRE and MAJEC are alternatives we have not
benchmarked — and MAJEC's own paper reports **r = 0.987** subfamily-level agreement with
TEtranscripts, which is your answer if someone says your quantifier is out of date.

**The flag that makes it work:** `-k 100`. Keep up to 100 candidate locations per read
instead of one. Without it there is no TE signal at all.

---

## Slide 5 — The positive control fired

**Shows:** TRIM28 and SETDB1 results.

**Say:** "TRIM28 knockdown: AluY up 0.79 log₂, adjusted p 0.0005. TRIM28 is known to
recruit SETDB1 to young Alu elements, so this is the positive control — we recovered known
biology we did not hard-code."

**Defend:** *log₂FC +0.79 means 2^0.79 = 1.73-fold up.* Sign convention is **knockdown
versus control**, so a positive value after removing a silencer means the element went up —
which is what a silencer is supposed to do.

---

## Slide 6 — One measurement propagates to eight unassayed genes

**Say:** "One measured mark-grounding propagates through the rule layer to genes nobody has
knocked down."

**The honest caveat, volunteered:** this is also the fragility — see slide 11.

---

## Slide 7 — The neurosymbolic part is a citation gate

**Say:** "The language model does exactly one job: read 3,120 abstracts and turn English
into structured triples. All the reasoning is explicit rules. And at the boundary, every
sentence the system displays must carry a resolvable edge id — sentences without one are
*discarded before display*, not flagged."

**Defend:** *19 sentences kept, 2 rejected across eight worked genes.*

**Why this is the answer to "how do you know the LLM isn't making it up":** it never
asserts anything. It proposes structure; anything that cannot point at an edge id does not
reach the user.

---

## Slide 8 — Ask it about TET2, and it refuses

**Shows:** the TET2 proof tree.

**Say:** "TET2 has no TE annotation in Gene Ontology and no knockdown in ENCODE. The engine
still answers — and prints its work. TET2 erases 5mC, that's curated. 5mC represses TEs,
that's inferred from *our* DNMT1 measurement. Therefore TET2 loss is *predicted* to lower
TE expression. Three facts, one of them ours, and you can attack any line."

**Two things to say without being asked:**

1. **The flag.** "This prediction is grounded in K562 CRISPR data. Asserting it elsewhere
   is a further inference — 87 of our 89 predictions carry that flag." An inferred edge
   inherits the scope of its narrowest evidence.
2. **The weakest link.** "R2 transfers between DNMT1, a *maintenance* methyltransferase,
   and other 5mC writers. That is the rule most likely to be wrong, and the proof tree is
   what lets you see the argument depends on it."

**Word discipline:** say **predicts**, **mechanistic hypothesis**. Never *proves*,
*derives causally*, or *causal pathway*.

---

## Slide 9 — So what is actually druggable?

**Say:** "A graph that ends at 'these things are connected' is an interesting object. We
sorted all 83 graph genes into five druggability classes using Open Targets and ChEMBL.
The interesting one is class 3: **28 proteins with a solved structure and a real binding
pocket, on a causal path to inflammation, with nobody running a clinical programme.**"

**Two entries you will be asked about:**

- **TRIM28 is class 5 — no tractability evidence.** Our largest measured effect is the one
  with no pocket, because it is a scaffold. Biggest effect ≠ best target. Say this
  yourself; it reads as honesty, not weakness.
- **ERVW-1 (syncytin-1) is class 2 — clinical-stage.** A human endogenous retrovirus
  protein already has an antibody against it (temelimab). The precedent that TE-derived
  proteins are druggable already exists.

**Caveat to state:** tractability is **imported**, not computed by us.

---

## Slide 10 — Two things we built, measured, and threw away

**Say:** "A rule-based literature extractor — we measured it at **precision 0.109**, with
direction agreement no better than chance, and did not wire it in. And link prediction —
which we did not build, because with three knockdowns you cannot hold out a validation set,
and an unvalidated AUC would have been the most impressive and least meaningful number in
the project. The code and the measurements that condemned them are both in the repo."

**Why this slide exists.** It is the credibility slide. Anyone can show what worked.

---

## Slide 11 — We asked how much our own reasoning rests on

**Shows:** the leave-one-anchor-out figure.

**Say:** "Three measured knockdowns, 89 derived predictions. That ratio invites an obvious
attack, so we measured it. Drop every measured edge from one gene and re-derive. **Remove
SETDB1 and the inference layer collapses from 89 edges to 8.** Only four mark-grounding
edges exist in the whole graph, and each chromatin mark is grounded by exactly one
knockdown."

**Then the surprise:** "Remove **TRIM28** — our *largest* measured effect, 13 edges — and
the derived layer doesn't change at all. It's a scaffold, not an enzyme, so it can never
ground a mark. Measured evidence only enters the reasoning layer through genes with a
curated enzymatic role."

**And where it holds up:** "No hold-out ever flipped a direction. Genes either keep the
prediction or return *none*. When the evidence goes away the system refuses rather than
quietly falling back on something weaker."

**Why this is the most important slide.** Volunteering *"91% of our inference layer depends
on one experiment"* before being asked converts the project's biggest weakness into its
strongest demonstration of rigour. It also makes the ask specific: not "more data" but
**more writers and erasers of the same two marks**.

**Defend:** 89 → 8; TRIM28 89 → 89; four `MARK_AT` edges.
`results/holdout_robustness.csv`.

---

## Slide 12 — Is the evidence sufficient? Per claim, not in general

**Shows:** five questions, two answered, three not. Then the DNMT3B pre-registration.

**Say:** "Two of our five headline questions are answered and three are not, and the system
knows which is which. So we pre-registered one: **DNMT3B**. The engine predicts its loss
raises the TE compartment, via the rule most likely to be wrong — transferring from a
maintenance methyltransferase to a *de novo* one. ENCODE has a 258-million-read knockdown we
have never opened. The prediction, the endpoint, and the interpretation of *every* outcome
are committed to the repo before we look."

**State the confound yourself:** "The prediction is grounded in K562; the only knockdown is
HepG2. So it tests the rule *and* cross-cell-type transfer, confounded. That is exactly
what the context flag is for."

**Close:** "The interesting question in AI for science isn't whether a model can produce a
hypothesis — that's easy now, and the bottleneck was never a shortage of plausible
hypotheses. It's whether a system can tell you when the evidence isn't enough, and then
name the experiment. That's what this does."

**Do not** end on an agentic flourish. Let sufficiency drive it: what is answered, what is
not, *then* the computation. That ordering is the scientific logic.

---

## The four questions you will definitely get

**"Isn't this just a lookup table?"**
> TET2 has no annotation anywhere and no experiment, and it still gets a signed answer
> through a rule chain you can inspect. And we measured the dependency — slide 11.

**"Three knockdowns can't support 89 predictions."**
> Correct, and we quantified it rather than waiting to be asked: 91% of the inference layer
> depends on one experiment. That's precisely why the pre-registered next experiment is a
> second writer of the same mark.

**"Multi-mapping makes TE quantification meaningless."**
> Which is why there are two statistics. The primary one compares TEs against
> protein-coding genes *in the same libraries* — size factors are per-sample, so a
> normalisation error shifts both sets equally and cancels in the difference of their
> medians. A normalisation artefact cannot manufacture a gap between two feature sets
> measured in the same libraries. The test itself is standard competitive gene-set testing;
> what's ours is using it as the primary TE readout for that reason.

**"Why not just use TxPert / a machine-learning model?"**
> TxPert is real and good, and **TxPert plus a TE-aware expression matrix would be a strong
> competitor** — that gap is closable, not closed. But it predicts conventional
> transcriptomic response and doesn't model TEs as an output space. And with three measured
> knockdowns we can't train anything honestly. The rule engine is a bootstrap: it generates
> testable hypotheses until the atlas is big enough to learn from. Eventually both should
> coexist.

---

## Four more you are now likely to get

Added after the external review of 2026-09-22. `JURY_QUESTIONS.md` has 41 with answers;
these four are the ones that would have caught the deck as it stood.

**"There are already TE atlases — TE-SCALE, TEITbase, REdiscoverTE. How is this different?"**
> They're much larger than this and they answer a different question: **where** TEs are
> active — which tissue, which tumour, which cell. This asks **what perturbation changed
> them**, through what mechanism, and what to test next. Observational versus
> interventional. TE-SCALE has 1.3 million cells; I have three knockdowns. I'm not claiming
> scale, I'm claiming a different axis — and the perturbational one is emptier.

**"ROME Therapeutics did this. They raised real money and they shut down."**
> ROME is the closest industrial precedent and they were ahead of me on biology — they
> solved the LINE-1 ORF2p structure in *Nature* and built reverse-transcriptase inhibitors.
> I'm not claiming more depth than a drug company. What I haven't found in their public work
> is this architecture: public perturbation data re-analysed against the repeat genome into
> one evidence schema with inspectable reasoning. And a company winding down doesn't
> establish that the science failed.

**"There's a published benchmark of 16 TE quantification tools. Did you use the best one?"**
> I used a mature subfamily-level method because the inference layer consumes subfamily
> resolution, not because it won a benchmark. She et al. 2026 is the benchmark and it's on
> my reading list. The specific challenge is MAJEC, which reports exon-overlap contamination
> down from over 40% to about 5% — and **r = 0.987 subfamily-level concordance with
> TEtranscripts**, which is why I don't expect my subfamily conclusions to be
> quantifier-dependent. The head-to-head is pre-registered with a retract-if-sign-flips row
> and deliberately not yet run.

**"Why Modal rather than Nextflow on AWS or your institution's cluster?"**
> Nextflow or Snakemake could absolutely run this pipeline, and for a production genomics
> facility with a stable Slurm stack they might be the better answer. Modal's advantage here
> isn't capability — it's that an agent can decide at runtime what computation is needed,
> acquire the compute, fan out across libraries, reuse a shared reference volume and shut
> down, with nobody managing infrastructure. For an AI-native exploratory system that's a
> real difference. For a stable production pipeline it isn't. Say both halves — the answer
> is more credible than a sales pitch.

---

## Five things never to say

From `CLAIMS.md` §0, which is the authority. Check it before you go on.

| Never | Instead |
|---|---|
| "No knowledge graph has TEs" | "Major general-purpose biomedical KGs don't model TEs as first-class entities" |
| "Nobody has looked for TE regulators systematically" | "We re-analyse experiments for TE effects their authors didn't measure" |
| "Our TE quantification method" | "We use TEcount from TEtranscripts" |
| "The engine proves / derives causally" | "The engine predicts — here's the proof tree" |
| "This is the TE atlas" | "A perturbational TE atlas is the long-term object; this is an architecture with a worked example" |
| Citing a September 2026 *GeroScience* paper on DNMT3A vs TET2 retroelements | It could not be found in five searches. Cite Scheller et al., *Nat Cancer* 2021 (10.1038/s43018-021-00213-9) for the DNMT3A arm instead |

---

## If you have 3 minutes instead of 5

Keep: slide 2 (the gap), slide 5 + the DNMT1 hidden-effect story, slide 8 (proof tree),
slide 11 (hold-out), slide 12 (sufficiency + DNMT3B). Cut slides 3, 6, 7, 9, 10 and
mention the refusals in one sentence on slide 12.

The single most impressive 30 seconds you have: **DNMT1 shows nothing at FDR < 0.1, and a
real effect at p = 1.6 × 10⁻⁸ on the compartment test — and here is why that test cannot be
faked by normalisation.** If you land only one thing, land that.
