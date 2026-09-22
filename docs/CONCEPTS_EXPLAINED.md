# Everything explained: sources, statistics, and the honest uncertainties

Answers to the questions that come up when you actually read the pipeline. Written to be
read in any order — each section stands alone.

| | |
|---|---|
| §1 | The four curated databases: GO, STRING, Reactome, Complex Portal |
| §2 | The three ways to count a TE read — and where your own pipeline sits |
| §3 | What was taken from TE_CHIP |
| §4 | The EM assumption, and what would genuinely be better |
| §5 | Bayesian statistics here, and the model I would actually build |
| §6 | Competitive gene-set testing, in plain words |
| §7 | What a proof tree is |
| §8 | Is DNMT1 similar to DNMT3A? |
| §9 | Bootstrap confidence intervals |
| §10 | How to read the reference-control table |
| §11 | The cytosolic sensing arm, and how to fix it |
| §12 | The panel's remaining limit, and how to fix that |
| §13 | Where this analysis could be wrong |
| §14 | Scaling to many genes, and what a company would be |
| §15 | What to set up for Modal right now |
| §16 | Where the demo is |

---

## 1. The four curated databases

These supply the `curated` layer — 9,263 edges. All four are public, free, and standard;
none of them knows anything about transposable elements. That is the gap the project exists
to bridge.

### 1.1 Gene Ontology (GO)

**What it is.** A controlled vocabulary of biological concepts, plus a huge set of
*annotations* linking genes to those concepts. Three independent branches:

- **Molecular Function** — what the protein *does* biochemically ("H3K9 methyltransferase
  activity", GO:0140949)
- **Biological Process** — the larger process it takes part in ("transposable element
  silencing", GO:0010526)
- **Cellular Component** — where it is ("nucleolus")

The terms form a hierarchy (a DAG): `GO:0031507 heterochromatin formation` is a child of
broader chromatin terms, so querying a parent with `goUsage=descendants` pulls everything
beneath it.

**The critical detail most people miss: evidence codes.** Every annotation carries one.
`EXP`, `IDA`, `IMP` mean somebody did an experiment. **`IEA` means a computer inferred it by
sequence similarity and no human ever checked.** A large share of GO is IEA. An
unfiltered GO query therefore returns a mix of measured biology and automated guesswork
under one label.

**What we use it for.** Two things, and the second is load-bearing:
- 318 `ANNOTATED_TO` edges (gene → GO term) defining the seed gene set.
- **All 44 `DEPOSITS_MARK` / `ERASES_MARK` edges** — from Molecular Function only, because
  "has H3K9 methyltransferase activity" is a biochemical statement, not a pathway guess.
  This is the layer R1/R2/R3 reason over, so the whole inference layer inherits GO's
  accuracy on those specific terms.

**What it cannot tell you.** Direction, magnitude, cell type, or condition. "DNMT3A is a
5mC methyltransferase" says nothing about which loci, in which cell, or how much.

### 1.2 STRING v12.0

**What it is.** A protein–protein *association* network — around 20,000 human proteins with
scored links. Each link is built from seven independent evidence channels: genomic
neighbourhood, gene fusion, phylogenetic co-occurrence, co-expression, experiments,
curated databases, and **text-mining**. They combine into a score from 0 to 999.

**We filter at `required_score=700`** ("high confidence"), giving 1,724 `INTERACTS_WITH`
edges.

**The trap.** STRING's "interaction" means *functional association*, **not physical
binding**. Two proteins can score 900 because they are always mentioned in the same
sentences. The text-mining channel in particular means STRING partly encodes *what has been
written about* genes, which makes it circular if you then use it as evidence about the
literature. Well-studied genes have more and higher-scoring edges regardless of biology.

**Why we use it anyway.** It is the best available answer to "which proteins work with this
one", and the rule layer never treats an `INTERACTS_WITH` edge as a mechanism — it cannot
satisfy R1, R2 or R3. It is there to make the graph navigable, not to prove anything.

### 1.3 Reactome

**What it is.** A hand-curated, peer-reviewed database of human *reactions* and pathways.
Unlike GO, it is explicitly mechanistic and ordered: a pathway is a sequence of reactions
with inputs, outputs, catalysts and compartments, organised hierarchically ("Chromatin
organization" → "HDACs deacetylate histones" → individual reactions).

**We use** `PARTICIPATES_IN` edges (gene → pathway): **4,900 of them, 52% of the whole
graph.**

**The trap, and it is a big one.** Pathway *co-membership* is very weak evidence of any
specific relationship. Two genes both in "Chromatin organization" may do unrelated things
in different complexes at different times. These edges inflate the headline edge count far
more than the graph's actual reasoning power — which is exactly what §4.5 of
`GRAPH_VALIDATION.md` reports, and why "9,455 edges" is a number to state carefully rather
than proudly.

### 1.4 Complex Portal

**What it is.** An EBI/IntAct-curated catalogue of *macromolecular complexes* — stable
physical assemblies with identifiers (`CPX-` numbers), defined membership and often
stoichiometry. This is the one that says "HUSH consists of MPHOSPH8, TASOR and PPHLN1",
which GO and STRING only imply.

**We use** `MEMBER_OF` edges (gene → complex): 2,321, over 1,199 complex nodes.

**The important handling detail.** Complex Portal includes entries that are *predicted* or
inferred by orthology rather than directly observed in human. Those edges are tiered
**`predicted`** — 1,316 of them — and **the rule layer refuses to propagate through a
predicted complex.** R4_COMPLEX_CONSENSUS only fires over curated membership, which is why
it produces just 2 edges. That refusal is deliberate: a complex that might not exist cannot
be allowed to launder a guess into a mechanism.

### 1.5 One-line comparison

| | Says what | Mechanistic? | Trap |
|---|---|---|---|
| **GO** | this gene has this function / is in this process | Molecular Function: yes | `IEA` evidence is computer-inferred |
| **STRING** | these two proteins are associated | no | includes text-mining; favours famous genes |
| **Reactome** | this gene participates in this pathway | yes, but coarse per-gene | co-membership ≠ relationship |
| **Complex Portal** | these proteins form this complex | yes, physically | some entries predicted, not observed |

---

## 2. The three ways to count a TE read

A read from a repeat often maps equally well to hundreds of places. There are three things
you can do about it.

**Route 1 — discard it.** What standard gene-centric pipelines do by default
(`featureCounts` with no multi-mapping flag, `HTSeq` default). Unambiguous, and it throws
away most of the repeat signal. Young, active subfamilies — the interesting ones — are the
most ambiguous and so are hit hardest. This is *why* the repetitive genome is missing from
most public analyses: not conspiracy, just a default setting.

**Route 2 — count it everywhere.** `featureCounts --countMultiMappingReads=TRUE` (`-M`)
assigns the read *in full* to every locus it hits. One read can contribute 100 counts. It
recovers the signal at the cost of inflating abundance in proportion to how repetitive the
subfamily is — a systematic bias that correlates with exactly the thing you are measuring.
It is defensible for *relative comparisons within one subfamily across samples*, since the
inflation factor is roughly constant per subfamily, which is why it is widely used.

**Route 3 — apportion it statistically.** `TEcount` from **TEtranscripts** (Jin et al.,
*Bioinformatics* 2015, [10.1093/bioinformatics/btv422](https://doi.org/10.1093/bioinformatics/btv422))
runs expectation–maximisation: start from the uniquely-mapping reads, estimate each
subfamily's abundance, distribute the ambiguous reads in proportion to those estimates,
re-estimate, repeat to convergence. One read contributes a total of 1.0, split fractionally.

**This project takes route 3. Every TE number here comes out of TEcount, and it is not our
method.** Nor is it the only option: Telescope and SQuIRE resolve individual loci, SalmonTE
is much faster, TEspeX handles exonised fragments, MATES and IRescue work single-cell, and
MAJEC targets a failure mode we do not address at all — TE reads overlapping gene exons,
which it reports cutting from ~43% to ~5% of locus-level signal. **There is now a published
benchmark of 16 such tools** (She, Wang & Yang, *Genomics Proteomics Bioinformatics* 2026,
[10.1093/gpbjnl/qzag044](https://doi.org/10.1093/gpbjnl/qzag044)).

### 2.1 Where your own published pipeline sits

**TE_CHIP takes route 2, and so does the *GeroScience* paper.**

| | TE_CHIP / Hasan et al. 2026 | this project |
|---|---|---|
| Alignment | STAR via **nf-core/rnavar** | HISAT2 `-k 100` (STAR on Modal) |
| TE counting | **featureCounts** over a RepeatMasker SAF, `countMultiMappingReads=TRUE` | **TEcount**, EM apportionment |
| A multi-mapping read | counted **in full at every locus** | split **fractionally**, totalling 1.0 |
| Resolution reported | class, family **and** subfamily | subfamily |
| Normalisation | TPM (genes), RPM/TPM/VST or rlog (TEs) | DESeq2 size factors from protein-coding genes only |
| Differential test | DESeq2, `~Batch+Sex+Age+Group` | DESeq2 (PyDESeq2) + a set-level compartment test |
| Perturbation | naturally occurring somatic mutation, 68 donors | CRISPR/CRISPRi knockdown, 11 libraries |

**They are not interchangeable and they have never been compared on the same data.** Route 2
inflates repetitive subfamilies by a roughly constant factor; route 3 does not, but it
*estimates* where ambiguous reads belong. A number from one is not comparable to a number
from the other in absolute terms — only the fold-changes are roughly comparable, and even
that is an assumption rather than a demonstration.

`CRITIQUE.md` lists that head-to-head as the clearest next test, and
`QUANTIFIER_ROBUSTNESS.md` pre-registers it — including a row committing to retract if signs
flip. **The single cheapest version:** run the three existing ENCODE contrasts through the
TE_CHIP featureCounts path and correlate the log₂ fold-changes. Same FASTQs, same
annotation, two counting philosophies. A day's work, and it would answer the question for
your own data rather than borrowing MAJEC's r = 0.987.

---

## 3. What was taken from TE_CHIP

Concretely, so you can say it accurately:

1. **The aggregation-level question.** TE_CHIP's `Normalise.R` aggregates to class, family
   *and* subfamily. That prompted testing whether aggregation helps here — and it measurably
   does not at this depth: AluY is significant at padj 0.0005 while pooled `Alu:SINE` gives
   +0.616 and loses significance; SETDB1 drops from 2 hits to 0, TRIM28 from 4 to 1
   (`aggregation_level_comparison.csv`). **The honest framing is that aggregation is a power
   trade-off, not a correctness choice** — and it becomes the right choice once per-subfamily
   counts stop being sparse, which is precisely the regime your PBMC data is in at 65 M
   reads and ours is not at 1.5 M.
2. **Joint gene + TE library normalisation.** TE_CHIP normalises genes and TEs together.
   This project deliberately does the opposite — size factors are estimated on
   protein-coding genes only (PyDESeq2 `control_genes`) — because if TEs contribute to the
   size factors, a global TE shift partly normalises itself away. That decision was made *by
   contrast with* TE_CHIP.
3. **The route-2 quantification path**, which is now the named comparator in the
   pre-registered benchmark rather than an abstract alternative.
4. **The VAF stratification scheme** (five groups, 10% threshold) from the poster and paper,
   which is what makes `HYPOTHESIS_DNMT3A_TET2.md` able to state the hypothesis precisely
   rather than vaguely.
5. **The Jakobsen et al. variant-filtering lineage** (VEP → ClinVar/COSMIC → MAF), noted as
   the provenance of the mutation calls the hypothesis rests on. Not reimplemented here —
   this project perturbs genes, it does not call variants.

**What was *not* taken:** the alignment stack, the counting method, the normalisation, or
any code. The pipelines are independent implementations of different choices, which is why a
head-to-head is informative rather than circular.

---

## 4. The EM assumption, and what would genuinely be better

**The problem, stated precisely.** EM distributes ambiguous reads *in proportion to
unambiguous evidence*. If a subfamily has no distinguishing positions anywhere — every copy
ambiguous with every other — then there is no unambiguous evidence to anchor it, and the
number EM returns is essentially the prior propagated to convergence. It will look like a
measurement. It is not one.

And the cruelty of it: **ambiguity correlates with youth, and youth correlates with
interest.** AluY and L1HS are the least diverged, therefore the least distinguishable,
therefore the most prior-driven — and they are exactly the subfamilies that are still
mobilising and still immunogenic.

**The key insight: this is not an algorithm problem, it is an *identifiability* problem.**
No estimator can recover information the reads do not contain. EM is the maximum-likelihood
answer; the likelihood surface is simply flat in those directions. Swapping EM for something
cleverer does not add information. So the useful approaches are the ones that either *measure
how much information exists*, *propagate the resulting uncertainty*, or *go and get more
information*.

### 4.1 Six approaches, in increasing cost

**(a) Quantify identifiability per subfamily, and report it alongside abundance.**
For each subfamily, compute the fraction of its positions that can distinguish it from every
other subfamily — a mappability or unique-k-mer fraction. Then every abundance comes with a
label: *how much of this estimate is data and how much is prior?* This is cheap (one pass
over the annotation and the genome), requires no new tool, and converts an invisible
assumption into a reported number.

**This is the analysis I would actually run first**, and it has a natural falsification
test: recompute the set-level statistic using **only** subfamilies above an identifiability
threshold. If TRIM28's +0.410 and DNMT1's +0.117 survive on identifiable subfamilies alone,
the conclusion does not depend on the prior-driven ones. If they vanish, we have been
reading EM's prior. Either answer is worth having, and neither requires new sequencing.

**(b) Report posterior intervals instead of point estimates.** Salmon and kallisto already
do this for transcripts — Gibbs sampling or bootstrap over the read-assignment step, giving
each feature a distribution rather than a number. An unidentifiable subfamily then gets a
*wide* interval, which is the correct representation of ignorance, and that uncertainty can
be propagated into the differential-expression model instead of being discarded at the
boundary. Telescope's Bayesian reassignment is the TE-specific version of this idea.

**(c) Collapse to identifiable equivalence classes rather than forcing subfamily labels.**
Borrowed from transcript quantification: instead of insisting every read be assigned to
*AluY* or *AluSx*, group features that the data cannot separate and report the group. You
lose the pretty label and gain an estimate that is actually supported. This connects directly
to the ontology roadmap in `TE_RESOLUTION.md` §8 — report at the resolution the experiment
supports, and no finer.

**(d) Use within-element variation as an anchor.** Young elements are not *identical*, just
very similar. Their few diagnostic positions — SNVs, indels, the poly-A junction — are
information EM ignores when it works off whole-read multi-mapping. Variant-aware assignment
uses them. This is close to what locus-level methods (Telescope, SQuIRE) are exploiting.

**(e) Model read assignment and differential expression jointly.** Currently there is a hard
boundary: TEcount produces counts, DESeq2 treats them as observed data. A joint model would
let the DE step know which counts are uncertain. MAJEC is the closest thing to this in the
TE world — genes, isoforms and TE loci in one probabilistic model.

**(f) Long reads, which dissolve the problem instead of modelling it.** A read spanning a
whole element is usually unambiguous. CELLO-seq
([10.1038/s41587-021-01093-1](https://doi.org/10.1038/s41587-021-01093-1)) does this at
single-cell resolution. Expensive, lower throughput, and the honest long-term answer.

### 4.2 The sentence to say

> EM's assumption is that ambiguous reads distribute like unambiguous ones. For the youngest
> subfamilies there is barely any unambiguous evidence, so the estimate is closer to a prior
> than a measurement — and those are the interesting ones. That isn't fixable by a better
> optimiser, because the information isn't in short reads. What *is* fixable is reporting it:
> compute per-subfamily identifiability, re-test the headline results on identifiable
> subfamilies only, and carry posterior intervals instead of point estimates. Long reads are
> the real answer.

---

## 5. Bayesian statistics here — and the model I would actually build

### 5.1 You are already doing Bayesian statistics

DESeq2 is **empirical Bayes**, which is why it works with three replicates. Two places:

**Dispersion shrinkage.** With 2–3 replicates you cannot estimate a feature's dispersion
α_i reliably. A feature that happens to look consistent gets a near-zero dispersion, and then
any difference looks significant — this is the single biggest source of false positives in
small RNA-seq experiments. DESeq2 fits a smooth trend α_trend(μ̄) across all features and
pulls each noisy per-feature estimate toward it, in proportion to how uncertain that estimate
is. A feature with genuinely high dispersion keeps it; a feature that merely *looks* quiet
gets pulled up to what features at its expression level typically look like.

That is a prior — estimated from the data itself, hence *empirical* Bayes. The "prior" is
"features like this one usually have this much noise", and the posterior is a compromise
between that and the feature's own three points.

**Log fold-change shrinkage** (`apeglm`, which the *GeroScience* paper uses for its
TARGET-seq pseudobulk) does the same for effect sizes: a low-count feature showing an
enormous fold-change gets pulled toward zero, because with that little data an enormous
fold-change is more likely noise than signal.

### 5.2 What a fully Bayesian treatment would add — and the elegant part

Three things, the third being genuinely exciting for this project specifically:

**(a) Posterior intervals instead of p-values.** "There is a 95% probability the TE
compartment shifted between +0.08 and +0.15" is a more useful statement than "p = 1.6 × 10⁻⁸",
and much harder to misread. It also handles the DNMT1 situation gracefully — no subfamily
individually credible, the compartment clearly shifted — without needing two separate tests.

**(b) Propagating quantification uncertainty.** §4 above. The EM assignment uncertainty and
the differential-expression model become one joint model, so unidentifiable subfamilies
automatically get wide posteriors and stop driving conclusions.

**(c) Partial pooling across the TE hierarchy — this is the one I would build.**

The TE vocabulary is *natively hierarchical*: class → family → subfamily. That is a textbook
multilevel model:

```
log2FC[subfamily]  ~  Normal( μ[family],  σ_subfamily )
μ[family]          ~  Normal( μ[class],   σ_family )
μ[class]           ~  Normal( 0,          σ_class )
```

Why this matters here: **it dissolves the aggregation dilemma.** Right now there is a forced
choice — subfamily resolution (more power at our depth, measured) versus family aggregation
(what TE_CHIP and your *GeroScience* paper use, and what loses signal here). Partial pooling
gives both at once. AluY borrows strength from the Alu family *without being collapsed into
it*: if AluY's own data is strong it keeps its own estimate, and if AluY is sparse it shrinks
toward the family mean. The amount of borrowing is estimated from the data, not chosen by you.

It would also give a principled family-level and class-level estimate as a *by-product*, with
honest uncertainty — rather than the current situation where aggregating is a separate
analysis that throws power away.

**Practically:** `brms` or `rstan` in R, or `PyMC`/`numpyro` in Python, on the counts with a
negative-binomial likelihood and the hierarchy above as a random-effects structure. For your
own PBMC data, the model extends naturally: `~ Batch + Sex + Age + Group + (1|family/subfamily)`.
`limma`/`edgeR` can approximate the random-effects part more cheaply if a full Stan fit is
too slow.

**The honest caveat:** this is not done, is not in the repository, and would need its own
validation. Do not describe it as implemented. Describe it as the next statistical step, and
say *why* — it resolves a trade-off the project currently has to choose sides on.

---

## 6. Competitive gene-set testing, in plain words

You have measured 12,660 features. Some belong to a set you care about (TE subfamilies,
interferon genes). Two very different questions:

**Self-contained:** *did my set change?* Compare the set against zero. Problem: if the whole
library shifted — sequencing depth, normalisation, a global stress response — your set
"changed" along with everything else, and you learn nothing specific.

**Competitive:** *did my set change **more than everything else**?* Compare the set against
the other features in the same experiment. This is the useful question, and it is what we do.

**GSEA** (Subramanian et al., [10.1073/pnas.0506580102](https://doi.org/10.1073/pnas.0506580102))
is the famous implementation. Rank all features by fold-change, walk down the list from most
up-regulated to most down-regulated, and keep a running score: step **up** when you hit a set
member, **down** when you don't. If set members are scattered randomly the score wanders
around zero. If they are bunched at the top it climbs high before falling. The maximum
deviation is the enrichment score, and significance comes from permutation.

The intuition worth keeping: *are my genes clustered at one end of the ranked list, or spread
through it?*

**CAMERA** (Wu & Smyth, [10.1093/nar/gks461](https://doi.org/10.1093/nar/gks461)) is
essentially a t-test between set and non-set fold-changes, with one crucial correction: genes
in a set are **correlated** with each other (same pathway, co-regulated). Standard tests
assume independence, so correlation makes 100 correlated genes behave statistically like a
much smaller number and *p*-values come out far too small. CAMERA estimates the inter-gene
correlation and inflates the variance accordingly. It is the reason a set of 500 co-regulated
genes doesn't automatically look overwhelmingly significant.

**What we do, and how it relates.** We take the TE subfamily log₂ fold-changes and the
protein-coding gene log₂ fold-changes *from the same contrast* and run a Mann–Whitney test on
the two distributions. That is a competitive test with the TE compartment as the set and
protein-coding genes as the reference.

**The one thing about it that survived the prior-art attack** is not the statistic — that is
standard, and `CLAIMS.md` D6 retracts any claim otherwise. It is the *reason* for using it as
the **primary** TE readout: size factors are per-sample multiplicative, so a normalisation
error shifts TE and gene fold-changes by the *same amount*, and cancels in the difference
between their medians. **A normalisation artefact cannot manufacture a gap between two
feature sets measured in the same libraries.** For a compartment as normalisation-sensitive
as the repeat genome, that property is worth more than per-feature FDR.

And the honest caveat, which §13.2 develops: normalisation-invariance is not *biological*
invariance. If a knockdown broadly activates transcription, TEs and genes could diverge for
reasons that have nothing to do with TE-specific silencing.

---

## 7. What a proof tree is

A record of *how* a conclusion was reached, with every step and every piece of evidence
named, in a form you can attack.

Ordinary output: **"DNMT3A silences transposable elements."** You cannot tell whether that
came from a measurement, an annotation, a guess, or a language model's recollection.

A proof tree instead:

```
CONCLUSION  Losing DNMT3A is predicted to RAISE TE:global        [tier: inferred]
│
└── R2_WRITER_TRANSFER
    ├── premise 1  DNMT1 —SILENCES→ TE:global                    [tier: measured]
    │              e3f9a1c04b2e77 · set-level p=1.6e-8 · K562 · CRISPR
    ├── premise 2  DNMT1 —DEPOSITS_MARK→ 5mC                     [tier: curated]
    │              GO:0003886
    └── premise 3  DNMT3A —DEPOSITS_MARK→ 5mC                    [tier: curated]
                   GO:0003886
    !  context_generalization_required = yes  (grounded in K562)
```

Four properties matter:

1. **Every leaf is a real edge id** you can look up in the CSV. Nothing is asserted without a
   traceable source.
2. **The tier of the conclusion is the weakest tier on the path.** One inferred step makes
   the whole conclusion inferred, no matter how much curated evidence surrounds it.
3. **The attack surface is explicit.** You can see that the whole thing rests on one DNMT1
   measurement, and that the load-bearing assumption is "two writers of the same mark are
   interchangeable" — which is *false in general*, since SETDB1 recruited via TRIM28 and
   another H3K9 writer elsewhere are not equivalent. A reviewer can reject R2 specifically
   rather than disbelieving the output vaguely.
4. **It carries its own generalisation warning.** The `!` line says the evidence came from
   K562, so asserting it elsewhere is a *second* inference.

The contrast that matters: a language model's explanation is generated *after* the answer and
may or may not describe how the answer arose. A proof tree **is** the derivation — the answer
exists because the tree does.

---

## 8. Is DNMT1 similar to DNMT3A?

**Similar enough to share a mark; different enough that the transfer is a hypothesis.** They
are the same enzyme class and both are annotated to GO:0003886 — which is exactly what lets
R2 connect them, and exactly why R2 is the weakest step in the whole graph.

| | DNMT1 | DNMT3A |
|---|---|---|
| Role | **maintenance** | ***de novo*** |
| Substrate preference | hemimethylated CpG — a site already methylated on one strand | unmethylated CpG |
| When | at the replication fork, copying the parental pattern to the new strand | establishing patterns where none existed |
| Recruitment | UHRF1 reads hemimethylated DNA, PCNA ties it to replication | PWWP domain reads H3K36me2/3; DNMT3L stimulates |
| Knockout effect | rapid, near-global loss of methylation as cells divide | gradual, milder hypomethylation |

**Why the transfer is defensible:** they deposit the identical chemical mark at the identical
kind of site. If 5mC is what keeps a TE silent, then losing *any* enzyme that maintains 5mC
at that TE should derepress it.

**Why it may fail:** targeting is not shared. DNMT1 loss removes methylation everywhere
replication goes; DNMT3A loss removes it where DNMT3A was recruited, which its PWWP domain
determines. A TE silenced by DNMT1-maintained methylation need not be a TE that DNMT3A ever
methylated.

**And your own paper makes this sharper than I could.** It reports that DNMT3A mutations
yield *mild* hypomethylation, and — more pointedly — that **DNMT3A-mutant is not one
phenotype**: PWWP-domain mutations were exclusively RTE-high, while the R882H hotspot
clustered with *low* RTE expression and R882C with high. If different DNMT3A mutations don't
behave alike, then "DNMT3A behaves like DNMT1" is obviously a coarse approximation.

**How to say it:** *DNMT1 is the maintenance methyltransferase and DNMT3A the de novo one.
They share the mark, which is what the rule uses, and they don't share the targeting, which
is why the conclusion is tiered `inferred` and why a direct DNMT3A knockdown is the named
next experiment.*

---

## 9. Bootstrap confidence intervals

**The problem.** You have a statistic — the median TE log₂FC minus the median gene log₂FC —
and you want to know how precise it is. Its sampling distribution has no clean formula.

**The bootstrap.** Instead of deriving the distribution, simulate it from your own data:

1. Draw a resample of your features **with replacement**, the same size as the original. Some
   features appear twice, some not at all.
2. Recompute the statistic on the resample.
3. Repeat a few thousand times.
4. The middle 95% of those values is your confidence interval.

That's it. No normality assumption, no formula — the variability *within* your data is used to
estimate how much the statistic would wobble if you could repeat the experiment.

**What it bought here.** The two-arm figure reports, per knockdown:

| Knockdown | TE arm | interferon arm |
|---|---|---|
| SETDB1 | +0.024 [−0.062, +0.115] | +0.023 [−0.056, +0.060] |
| TRIM28 | **+0.408 [+0.311, +0.467]** | −0.023 [−0.126, +0.061] |
| DNMT1 | **+0.136 [+0.095, +0.178]** | −0.011 [−0.059, +0.042] |

The TE intervals for TRIM28 and DNMT1 exclude zero comfortably. The interferon intervals all
contain zero — and, more importantly, they **exclude effects of TE-arm magnitude**. That is
the difference between "we found nothing" and "if an effect of the size we saw on the TE side
existed here, we would have seen it". The first is a shrug; the second is a measurement.

**The caveat.** Resampling features assumes features are exchangeable, and they aren't quite
— genes in a pathway are correlated, TE subfamilies share sequence. That makes these
intervals mildly optimistic. It is the same correlation problem CAMERA corrects for in §6, and
it is not corrected here.

---

## 10. How to read the reference-control table

| Knockdown | Pearson (all) | Pearson (TE only) | median \|Δlog₂FC\| |
|---|---|---|---|
| SETDB1 | 0.995 | 0.993 | 0.007 |
| TRIM28 | 0.996 | 0.993 | 0.027 |
| DNMT1 | 0.992 | 0.992 | 0.013 |

**What was being tested.** 62 Mb of interferon-signature gene loci were spliced into the
chr1+chr19 reference to close a coverage gap. The obvious worry: did changing the reference
change the answers we had already reported? The same FASTQs were re-quantified against both
references, so every difference is attributable to the reference alone.

**Read the third column, not the first two.** Pearson *r* across thousands of features is
close to 1 almost automatically, because most features don't change in either run and a few
large values dominate the correlation. `r = 0.992` is reassuring but weak evidence.

**Median |Δlog₂FC| is the number that matters:** the typical feature's fold-change moved by
**0.007 to 0.027 log₂ units** — under 2% in fold-change terms. Put that against the effects
being claimed: the TRIM28 TE compartment shift is **+0.408**, roughly **15× larger** than the
biggest perturbation the reference change caused. And no sign flipped among the six headline
TE hits.

**Why TRIM28 has the largest Δ (0.027).** It has the largest true effects, so more features
are genuinely moving, and features that are moving are more sensitive to a change in the
denominator. Expected, not alarming.

**The cost that the table doesn't show, and you should volunteer.** Adding ~1,100 features
enlarges the multiple-testing set, so per-feature FDR loses 1–2 hits per contrast. That is
why the TE arm is quoted from the original reference and the inflammation arm from the panel
run — stated in `PANEL_REFERENCE.md` rather than buried.

**The sentence:** *Same reads, two references. Typical fold-change moved by 0.007–0.027
log₂ — fifteen to sixty times smaller than the effects we report, and no sign flipped. The
measurements are a property of the data, not of the reference we happened to build.*

---

## 11. The cytosolic sensing arm — and how to fix it

First, a correction of terms: there is no "non-sensing arm". The phrase is **cytosolic
sensing arm**, and it means the *first* step of the innate immune pathway — the proteins whose
job is to notice nucleic acid sitting somewhere it shouldn't be.

**The pathway has three stages:**

1. **Sensors** — detect the ligand. cGAS (cytoplasmic DNA), RIG-I/`RIGI` and MDA5/`IFIH1`
   (cytoplasmic double-stranded RNA), ZBP1, TLR3, NLRP3. **These are the entry points.**
2. **Transducers** — relay the alarm. STING1, MAVS, TBK1, IRF3, JAK1, STAT1/2, TYK2.
3. **Effectors** — the response itself. The interferon-stimulated genes: ISG15, IFIT1/3, MX1,
   OAS1.

**What K562 actually looks like** (`sensor_expression_k562.csv`):

| Stage | Gene | CPM |
|---|---|---|
| **sensor** | TLR3 | **0.00** |
| **sensor** | NLRP3 | **0.20** |
| **sensor** | CGAS | **0.21** — non-zero in 1 of 11 samples |
| **sensor** | ZBP1 | **0.26** |
| **sensor** | RIGI | 5.4 |
| **sensor** | IFIH1 | 8.5 |
| transducer | STING1 | 270 |
| transducer | IRF3 | 317 |
| transducer | MAVS | 586 |
| transducer | TYK2 | **799** |

**The wiring and the sprinklers are installed. The smoke detectors are not.** ADAR is at
823 CPM — it edits double-stranded RNA and suppresses MDA5 activation, so even the dsRNA
route is actively damped. IFNB1 and OASL sit at exactly zero.

**Why this makes the null a real result rather than a failure.** TE derepression definitely
happened — TRIM28's compartment shift is +0.408 with a tight bootstrap interval. No
interferon signature moved, under either background, with intervals excluding TE-arm-magnitude
effects. If you stop there you might conclude *TE derepression does not cause interferon*.
The sensor expression shows that conclusion is unavailable: **in this cell line there is
nothing present to detect the ligand.** So the correct claim is *this dataset cannot test
viral mimicry* — a statement about the experiment, not about the biology.

That distinction is the single most defensible thing in the project. It is also the one most
likely to be mangled under pressure, so the wording is fixed in `CLAIMS.md` W6.

### 11.1 Four ways to fix it, cheapest first

**(a) Add the positive control that is currently missing — and do this regardless.** Transfect
poly(I:C) (a dsRNA mimic) or 2′3′-cGAMP (a direct STING agonist) into K562 and score the same
signature. If the ISGs move, the sensing axis *can* respond and the null is about the ligand.
If they don't, the axis is non-functional and the null is about the cell line. **Right now
that has not been done, so "the sensors aren't expressed" is inferred from mRNA abundance
rather than demonstrated by a failure to respond.** One plate, and it converts an inference
into a measurement.

**(b) Use a sensing-competent cell type — and you already have one.** Primary PBMCs are
sensing-competent, and your own *GeroScience* cohort is PBMCs with matched genotypes and
65 M reads per sample. Its TE compartment was quantified but the *joint* question — does
TE derepression co-occur with interferon induction **within the same donors** — is exactly
what the R6 rule is built to answer and has never had data. The paper reports interferon
enrichment in DNMT3A RTE-high clones, which is that association at signature level. Running
it through this framework would put both arms in one contrast with a proof tree attached.

Other options: THP-1 or U937 (myeloid, sensing-competent, and closer to CH biology than
K562), primary HSPCs, or BJ fibroblasts if senescence is the interest.

**(c) Reconstitute the sensor in K562.** Express cGAS and/or STING1 and repeat the knockdowns.
This isolates the sensing step cleanly — same cells, same perturbation, one variable added —
and is the standard trick in the viral-mimicry literature for exactly this reason.

**(d) Accept the scope.** K562 is a legitimate system for asking *which genes silence TEs*. It
is simply not a system for asking *what TE derepression does immunologically*. Splitting the
two questions across two cell types is better experimental design than forcing one line to
answer both.

---

## 12. The panel's remaining limit, and how to fix it

The panel-augmented reference took type-I interferon coverage from 0.168 to 0.768 — but
**inflammatory response (GO:0006954, 725 members) is still only 0.535** and the 0.6 coverage
guard still refuses it.

**Why a panel cannot solve this in general:** a panel measures the genes you *name*. It
cannot discover a pathway you did not anticipate. It is the right tool for a pre-specified
question and the wrong tool for discovery.

**Four fixes:**

1. **Go genome-wide.** The actual fix, and the reason Modal is in the architecture at all.
   Every coverage guard disappears the moment the reference is the whole genome. GO:0006954's
   725 members are then all present by construction. This is the single highest-value run
   available and it needs cloud compute, not cleverness.
2. **Expand the panel to the full set.** ~725 genes instead of the current 990 mixed-signature
   selection — mechanical, and it would clear the guard for this one set. But it just moves
   the boundary: the *next* signature someone asks about is again uncovered. Treating the
   symptom.
3. **Two-stage design.** Genome-wide at low depth to discover *which* pathways move, then a
   panel at high depth on those. Efficient if sequencing is the constraint, and it uses each
   tool for what it is good at.
4. **Keep the guard, which is the point.** 0.535 coverage means a "result" for inflammatory
   response would be describing *which of its genes happen to live on chr1, chr19 and the
   panel* rather than the biology. That the guard still refuses after a substantial
   engineering effort is evidence it is calibrated to the question and not to the effort
   already spent — which is exactly what you want from a guard, and worth saying out loud.

---

## 13. Where this analysis could be wrong

Ordered by how much would collapse if it were.

### 13.1 The entire 5mC arm rests on one contrast at reduced depth

DNMT1 is the *only* grounding for 5mC — a single `MARK_AT` edge. Every claim about DNMT3A and
TET2 flows through it. If that set-level shift (+0.117, p = 1.6 × 10⁻⁸) is an artefact of
chr1/chr19 composition or of 1.5 M reads, then R1 → R2 → R3 collapses and with it the entire
DNMT3A/TET2 story. **This is the most consequential single point of failure in the project**,
and the genome-wide full-depth DNMT1 re-run is the named test.

### 13.2 Normalisation-invariance is not biological invariance

The set-level test is immune to *per-sample normalisation error* — that argument is sound and
it is the one claim of ours that survived the prior-art attack. But it does **not** protect
against a knockdown that broadly changes transcription. If losing DNMT1 globally activates
transcription of previously silent regions, TEs and protein-coding genes would diverge for
reasons that have nothing to do with TE-specific silencing, and the test cannot distinguish
that from TE-specific derepression. I have asserted invariance carefully in the narrow
technical sense and it could still be over-read. **Not tested.**

### 13.3 chr1 + chr19 is a biased pair

Chosen for gene density and size, not neutrality. **chr19 is the most gene-dense human
chromosome, unusually Alu-rich, and carries the large KRAB-zinc-finger clusters** — the very
proteins that recruit TRIM28 to TEs. A TE compartment defined largely by chr19 may behave
differently from the genome's. Whether this inflates or deflates the effects is unknown
because the genome-wide run has not happened.

### 13.4 Alignment and quantification choices, never benchmarked

`HISAT2 -k 100` truncates at 100 alignments, so the most repetitive reads are
under-represented. HISAT2 and STAR have never been compared head-to-head here — forced by a
broken arm64 STAR build, not chosen. And the quantifier comparison (§2.1) is pre-registered
and unrun. Any of these could shift numbers; the MAJEC r = 0.987 figure is *someone else's*
evidence that subfamily conclusions are robust, not ours.

### 13.5 The literature layer's error rate is unmeasured, and visibly non-zero

The LLM extractions were used as the reference standard for scoring the rule-based extractor
and were **never themselves validated against human annotation**. `GRAPH_VALIDATION.md` found
a concrete instance: PPARG asserted as both silencing and derepressing Alu, both edges from
the same abstract. That is an error rate becoming visible. Nothing quantifies it.

### 13.6 The interferon null is explained by inference, not by experiment

§11.1(a): the sensor-absence explanation rests on mRNA abundance. No stimulation control was
run. It is a strong and coherent explanation — transducers abundant, sensors at the floor,
ADAR high, IFNB1 zero — but a cell can express a sensor's mRNA and still not respond, and
vice versa. **I stated a mechanism where I measured a correlate.**

### 13.7 Batch structure could reach further than acknowledged

The two control arms differ sharply on ISG score (non-targeting +0.71 versus CRISPR control
−0.84), which is why every comparison is contrast-internal. That protects against the ISG
confound specifically. If the batches differ in *other* systematic ways — library prep, depth,
date — contrast-internal comparison does not fix that, and it has not been characterised.

### 13.8 R2's core assumption is false in general

"Two writers of the same mark are interchangeable at a locus" generates the largest share of
derived edges and is **known to be wrong** as a general statement: targeting differs, and
SETDB1 recruited via TRIM28 is not equivalent to another H3K9 writer elsewhere. It is tiered
`inferred` and the proof tree exposes it, which is honest — but honest is not the same as
correct, and a reviewer is entitled to reject every R2 edge.

### 13.9 The statistical power is small, and n = 11

Three knockdowns, 2–3 replicates, 11 libraries. Dispersion shrinkage (§5.1) makes this
*workable*, not *strong*. One outlier library could move a set-level median more than is
comfortable, and leave-one-library-out has not been run.

### 13.10 I got a literature search wrong today, demonstrably

The *GeroScience* paper was recorded as not found when it was indexed the whole time —
the queries used *retroelement* where the title says *retrotransposable*, and one used the
American spelling of *haematopoiesis*. Every `NOT_FOUND` verdict in `PRIOR_ART.md` rests on
searches by the same author, with the same blind spots. **Treat the surviving novelty claims
as provisional in exactly that way**, and expect a specialist to close one of them in
conversation.

### 13.11 Numbers imported rather than computed

The tractability classes (83 targets, 28 structurally tractable with no clinical programme)
are Open Targets/ChEMBL buckets, re-labelled here, not derived. If their bucketing is wrong,
ours is wrong identically. Flagged in `CLAIMS.md` C4 but easy to present as if it were an
analysis.

---

## 14. Scaling to many genes, and what a company would be

### 14.1 The immediate extension is already sitting in ENCODE

**1,114 knockdown RNA-seq experiments across 570 target genes, 1,060 of them with released
paired-end FASTQ**, median 32.4 M reads per file (`encode_kd_inventory.csv`). Three have been
processed. The pipeline is identical for the rest — it is the same `te_pipeline.py` call with
a longer manifest.

That produces a matrix of **570 genes × 1,057 TE subfamilies**, which is the object worth
building: the *perturbational map of the repetitive genome*. Rows = perturbations, columns =
TE subfamilies, layers = cell type and modality.

**Rough compute estimate, stated as an estimate:** genome-wide alignment with `-k 100` plus
TEcount runs on the order of an hour of CPU per library at full depth. ~1,060 libraries is
therefore ~1,000 CPU-hours — which is 10 hours of wall-clock on 100 parallel containers, and
the reference index is built **once** into a shared read-only volume. That shape — embarrassingly
parallel, CPU-bound, large reusable reference, no GPU — is why Modal is in the architecture.

**What the matrix unlocks that three genes cannot:** which host genes control HERV-K;
which regulators produce global versus subfamily-specific derepression; which silencing
systems are cell-type-invariant; which perturbations cluster mechanistically; and eventually
the learned model — predict the TE response to a perturbation never measured. At 3
perturbations, rules with proofs are the defensible choice. At 500, a TE-specific
GEARS/TxPert-style model becomes trainable, and rules and learning should coexist rather than
compete.

### 14.2 If this were a YC pitch

Be careful here — a strong scientific project is not automatically a company, and the fastest
way to lose a technical audience is to pitch a dataset as a business. Four framings, with what
is wrong with each:

**(a) The dataset as the asset.** "The perturbational TE atlas nobody has built." Honest, and
the moat is thin: the input data is *public*. Anyone with the pipeline and the compute can
rebuild it. The defensible version is processing depth plus the evidence layer, not the data.

**(b) Companion diagnostic for hypomethylating agents — the strongest hook, and it comes
from your own paper.** Scheller et al. (*Nat Cancer* 2021,
[10.1038/s43018-021-00213-9](https://doi.org/10.1038/s43018-021-00213-9)) show hotspot
DNMT3A mutations sensitise cells to **azacitidine via viral mimicry**. Your *GeroScience*
paper shows DNMT3A-mutant CH splits into RTE-high and RTE-low subgroups **by mutation
position** — PWWP exclusively RTE-high, R882H clustering RTE-low. Put those together and there
is a real clinical hypothesis: **a TE-derepression state predicts response to azacitidine**,
and it may be readable from mutation position plus an RNA signature. Azacitidine is approved
and widely used; a test that picks responders has an obvious buyer. The risk is equally
obvious — it needs a retrospective cohort with outcomes, which you do not have, and the
n = 10 high-VAF subgroup is nowhere near enough.

**(c) TE-aware target discovery for immuno-oncology.** The SETDB1 story — silencing TEs
suppresses tumour immunogenicity ([10.1038/s41586-021-03520-4](https://doi.org/10.1038/s41586-021-03520-4))
— plus 28 structurally tractable targets with no clinical programme. This is close to ROME
Therapeutics' thesis, and ROME wound down standalone operations. **Do not present that as
ROME having failed** — a closure does not establish that the science did — but an investor
who knows the space will raise it, and the answer needs to be about what is different now
(better locus-level tools, a perturbational rather than observational map) rather than
defensive.

**(d) Reanalysis as a service.** Every pharma RNA-seq archive has an unmeasured TE layer. Run
their existing data through a TE-aware pipeline and return the second phenotype layer. Lowest
technical risk, most credible near-term revenue, least venture-scale.

**What actually travels to that audience,** in one sentence: *there are thousands of
perturbational sequencing experiments in public repositories, nearly all analysed only through
the protein-coding genome; we re-analyse them for what happened to the other half, turn the
result into structured evidence, and can say which experiment to run next.* That is a data
asset, a method, and a wedge — and it is honest.

**And the thing to keep from the science:** the refusal behaviour is a *feature* in this
context. An investor who has been shown three confident AI-biology demos will remember the
one that said "this dataset cannot answer that, and here is the experiment that would".

---

## 15. What to set up for Modal right now

`list_compute` still returns empty, so nothing is connected yet. Everything below can be done
before any credits exist.

**(a) Validate the plan with no account at all.** This works today:

```bash
python src/modal_app.py --dry-run --manifest data/manifests/manifest_prospective.csv
```

It checks the manifest parses, the accessions resolve, the job plan is coherent and the
resource requests are sane — without contacting Modal. If this fails, fix it now rather than
on the day.

**(b) Create the account and the CLI token.** Sign up at modal.com, then:

```bash
pip install modal
modal token new          # opens a browser, writes ~/.modal.toml
modal profile current    # confirms which workspace you are in
```

**(c) Connect it to Claude Science:** Customize → Compute → add Modal. Then `list_compute`
returns it and jobs can be dispatched from a conversation.

**(d) Smoke-test with something trivial before the real run.** A container that prints its
CPU count and exits costs almost nothing and proves auth, image build and networking all work.
Do this *before* spending credits on a 258 M-read library.

**(e) Pre-build the reference volume if credits allow it early.** `build_reference` (8 CPU,
32 GB) downloads the genome, builds the index and writes it to a **shared read-only volume**
once. Every later job mounts it. If that is already warm when the day starts, the first
quantification job begins immediately instead of waiting on an index build.

**(f) Know the two flags.** `--reads 0` means full depth; `--reads 5000000` is the fast,
noisy version that still shows a compartment-level shift. Start with the second.

**The honest note:** no GPU is requested anywhere in `modal_app.py`, and that is deliberate.
Alignment and counting are CPU- and RAM-bound. Requesting a GPU to look impressive would be
theatre, and a Modal engineer would spot it instantly.

---

## 16. Where the demo is

Two HTML files in `demo/`, both self-contained — no server, no build step, no network. Open
either by double-clicking, or:

```bash
open demo/presentation.html      # macOS
xdg-open demo/presentation.html  # Linux
```

**`demo/presentation.html` — the 12-slide deck. This is what you present.** Figures are
base64-embedded so it works offline on any machine. Controls: **arrow keys** navigate,
**`f`** fullscreen, **`s`** hides the speaker notes. Every slide carries its own notes, and
`docs/PRESENTATION_GUIDE.md` explains what to say on each one and which number to defend.

**`demo/demo.html` — the query-engine walkthrough.** Type a gene, see the answer with its
proof tree and evidence tiers. **Caveat: this one was never reframed** after the positioning
changed. It passes the claim audit and makes no prohibited claims, but it is still the
original query demo and its framing predates the current wording. Use the deck for the pitch;
use this one if someone asks to see the tool respond to a gene.

**The live version is the command line**, and it is more convincing than either file because
it is obviously not pre-rendered:

```bash
make query GENE=TET2     # a gene with no annotation and no experiment — and it still answers
make query GENE=SETDB1   # the measured case, for contrast
```
