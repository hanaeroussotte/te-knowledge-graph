# Critique — what this answers, what it is good at, and where it breaks

Written to be read by someone deciding whether to trust the tool, including by the person who
built it. Nothing here is softened for a pitch.

---

## 1. What demand does this answer?

### 1.1 The concrete user

A researcher studying epigenetic regulators — chromatin writers/erasers, silencing complexes,
innate-immune coupling — who wants to know **which of their genes control transposable
elements, and whether anything downstream is druggable.**

Today that person does one of three things:

| What they do now | What it costs | What it misses |
|---|---|---|
| Read the TE literature by hand | days per gene | anything not yet published |
| Query a knowledge graph (Hetionet, Open Targets, PrimeKG) | minutes | **everything** — TEs are not first-class entities there |
| Re-analyse RNA-seq with a TE-aware pipeline | weeks of setup | genes with no available perturbation data |

The middle row is the point. It is not that the existing graphs give a poor answer; it is that
they cannot represent the question. A transposable element has no node type, so it cannot be a
target, cannot appear on a path, and cannot be scored.

### 1.2 What changes

The question "what does gene X do to TE activation, and is X or anything downstream druggable"
goes from a multi-day literature exercise to a single query that returns a signed answer, the
evidence tier behind it, and a proof you can audit.

### 1.3 Who this is *not* for

- Anyone needing a clinical or diagnostic answer. Nothing here is validated for that.
- Anyone working outside human K562/HepG2-like contexts — the measured layer is one cell line.
- Anyone wanting locus-level TE calls. This resolves to subfamily, not individual insertion.

---

## 2. Advantages

**It represents something no public graph can.** TE families and subfamilies are first-class
nodes with a defined taxonomy (1,057 subfamilies from RepeatMasker). This is not a
re-weighting of an existing graph; it is a node type that did not exist.

**Provenance is structural, not documentation.** Every edge carries source, native score,
statistic and retrieval date as mandatory fields. An edge that cannot fill them is dropped
rather than downgraded. Five tiers (`curated` / `measured` / `literature` / `inferred` /
`predicted`) are enforced in code, and a path takes the tier of its weakest edge — so a single
inferred hop cannot make a chain look established.

**Predictions come with proofs, not scores.** An inferred edge carries the tree of ground edges
it rests on. "Losing SUV39H1 raises HERV9NC-int" resolves to one measurement plus two GO
annotations, each inspectable. A reviewer can disagree with a specific step rather than with an
opaque number.

**The trust mechanism does not depend on the language model.** Prose is split into sentences
and a sentence survives only if every edge ID it cites exists in the graph. Uncited sentences
are rejected too. The checker is deterministic and runs identically on model-written and
template-written text. Most "LLM + knowledge graph" systems ask you to trust the model; this
one only asks you to trust a string comparison.

**It recovers known biology without being told it.** SETDB1 knockdown derepressing HERVs and
TRIM28 knockdown derepressing Alu were not coded in — they came out of the pipeline. That is
the only reason to believe the multi-mapping read assignment is working.

**It says "I don't know."** Asked about TET2 it returns no evidence and the citation gate
rejects the sentence. That is rarer than it should be in this class of tool.

---

## 3. Limitations

### 3.1 Statistical — the most serious ones

**The measured layer rests on three knockdowns.** SETDB1, TRIM28, DNMT1. Ten significant edges.
Every claim about the tool being a general "any gene" atlas is currently an argument about
architecture, not a demonstration of coverage.

**Two chromosomes, 1.5 M reads per library.** Absolute effect sizes are not final
quantifications. Libraries ended up at ~0.2–0.34 M annotated reads — low enough that only
strong effects clear FDR, and DNMT1's did not (best padj 0.41).

**Subsampling is not random.** `stream_head` takes the first N reads off the wire. Applied
identically across samples so relative comparison holds, but early reads cluster by flowcell
tile, so per-sample quality and duplication can skew.

**No multiple-testing correction across the three contrasts.** FDR is controlled within each
knockdown separately. With three contrasts the family-wise error is higher than the per-contrast
padj implies.

**n = 2–3 per arm.** Dispersion estimates at that n are unstable, and DESeq2's shrinkage is
doing a lot of work. Effect *signs* are more trustworthy than effect *sizes*.

### 3.2 Methodological

**Aggregating to family/class level made results worse — observation solid, explanation not.**
Following the TE_CHIP pipeline's class/family aggregation, subfamily-level significance was
lost: SETDB1 goes from 2 hits at padj < 0.1 to 0, TRIM28 from 4 to 1, and the aggregated
`Alu:SINE` family (+0.616) is no longer significant even though `AluY` alone is at padj
0.00053. **That observation is robust** (`aggregation_level_comparison.csv`), and it means
subfamily resolution is load-bearing at this depth.

*A correction to an earlier draft of this document.* I initially explained it as "only young,
still-active subfamilies respond, so pooling averages them against inert old copies." **That
explanation is not supported.** Tested directly against RepeatMasker divergence (`milliDiv`,
low = young):

| contrast | Spearman rho (milliDiv vs log2FC), baseMean ≥ 20 | p |
|---|---|---|
| SETDB1 | +0.098 | 0.39 |
| TRIM28 | +0.056 | 0.61 |
| DNMT1 | +0.166 | 0.027 |

Genome-wide there is **no age effect**, and the one nominal p is the wrong sign and does not
survive being one of six tests. Within Alu specifically the pattern does appear (AluY* median
log2FC +0.914 vs +0.555 for older Alu, Mann-Whitney p < 0.0001), but age and expression level
are confounded there (rho(milliDiv, baseMean) = +0.713); after partial correlation the age
association drops to rho = −0.346, and fold-change magnitude is inversely related to count
depth for protein-coding genes too (rho = −0.233, n = 2,890), i.e. part of the effect is a
generic estimation artefact pushing the same direction. With n = 39 Alu subfamilies this cannot
be resolved.

So: aggregation loses signal here, the reason is not established, and a plausible and duller
explanation — pooling high-variance low-count features with high-count ones — has not been
excluded. Aggregation remains the right choice when per-subfamily counts are sparse, which at
full depth they will not be.

**The quantifier differs from the reference pipeline.** TEcount distributes a multi-mapping
read probabilistically across candidate loci by EM; `featureCounts --countMultiMappingReads`
counts it fully at every location. The EM approach is more conservative; the featureCounts
approach inflates counts for high-copy families. Neither is wrong, but numbers from the two are
not interchangeable, and **nothing here has been benchmarked against the TE_CHIP outputs.**

**Local alignment uses HISAT2, the cloud path uses STAR.** Forced by a broken conda osx-arm64
STAR build. The two have not been compared on the same samples. This is an untested seam
running straight through the middle of the project.

**No batch or covariate modelling.** The design is `~target`. CRISPRi and CRISPR arms were run
as separate contrasts rather than modelled jointly, which is correct but means the two arms
cannot be compared to each other.

### 3.3 The knowledge layer

**The literature tier covers 19% of the retrieved corpus** — 600 of 3,120 abstracts, 32 human
edges after filtering. Coverage is not representative of the field.

**A cheaper literature extractor was built and failed.** Rule-based dictionary matching scored
precision 0.109, recall 0.175, direction agreement 10/21 (chance) against LLM-labelled
abstracts. It is not shipped. But note what that implies: the LLM extractions themselves were
used as the reference standard and were never validated against human annotation, so the
literature tier's true precision is unknown, not measured.

**696 of the 2,792 "curated" edges are Complex Portal *predicted* complexes**, correctly tiered
`predicted` and excluded from rule propagation — but they inflate the headline edge count.

### 3.4 The reasoning layer

**R2 is the weak rule and it generates most of the output.** "Writers of the same mark are
interchangeable at a locus" produces 30 of 71 derived edges. It is demonstrably false in
general — SETDB1 and SUV39H1 have distinct genomic preferences. It is tiered `inferred`, never
`curated`, but a reader skimming the graph will see many edges resting on one contestable
assumption.

**The rules encode a specific causal model and do not know when it fails.** Mark-mediated
silencing is one mechanism among several (small RNA, RNA destabilisation, sequestration). Genes
acting through those routes will be invisible to R1–R3, and the engine will report "no evidence"
rather than "wrong mechanism model."

**The citation gate verifies existence, not correctness.** A sentence citing a real edge passes
even if it misdescribes that edge. The gate catches fabrication, not misinterpretation.

**Five rules is a small rule set.** Calling it a symbolic reasoning engine is generous; it is a
small forward-chainer. The architecture would support more; the content is thin.

### 3.5 Biological

**One cell line.** K562 is an immortalised erythroleukaemia line with an abnormal epigenome.
Extrapolating to primary haematopoietic cells — which is what the clonal-haematopoiesis framing
implies — is not supported by anything measured here.

**The TE → sensor → interferon arm is now measured, and it is a null — with a mechanistic
explanation.** *(Updated; see `docs/PANEL_REFERENCE.md`.)* The arm was previously
unmeasurable because only 16.8% of the type-I interferon gene set sits on chr1+chr19.
Splicing 921 contigs covering 990 signature gene loci into the reference raised that to
76.8%, at a cost of 62 Mb and a reference-perturbation control (Pearson 0.992–0.996 against
the original log2FCs, no sign flips, set-level deltas unchanged).

At real coverage, no signature moves in any of the three contrasts under Bonferroni
correction, and the bootstrap confidence intervals on the interferon arm exclude effects of
the magnitude seen on the TE arm — so this is a measured absence, not an underpowered one.
The same data explains it: in K562 the transduction machinery is abundant (`TYK2` 799 CPM,
`MAVS` 586, `IRF3` 317, `STING1` 270) while the **entry points are at the floor** — `CGAS`
0.21 CPM, `ZBP1` 0.26, `TLR3` 0.00, `NLRP3` 0.20, `RIGI` 5.4, `IFIH1` 8.5 — and `ADAR`, the
main brake on sensing endogenous dsRNA, is at 823 CPM. `IFNB1` and `OASL` are at zero.

So: **this dataset cannot test viral mimicry**, because the cell line lacks the sensors. The
claim "TE derepression causes interferon" remains untested here and requires a
sensing-competent cell type. Two residual weaknesses of the fix itself: a panel measures
only the genes you name, so it cannot surface an unanticipated pathway; and the
inflammatory-response set (725 members) still fails the coverage guard at 0.535.

**Subfamily-level, not locus-level.** Individual insertions differ enormously in whether they
are transcribed. "AluY goes up" aggregates ~104,000 loci.

### 3.6 Druggability

**Tractability is imported, not computed.** Classes come from Open Targets buckets and ChEMBL
mechanism counts. "Structurally tractable, no clinical programme" means *nobody has published a
programme*, which is often evidence a programme was tried and failed rather than evidence of
opportunity.

**83 of 89 targets were annotated.** TET2 is absent from the tractability table because it never
entered the graph; six others failed Ensembl resolution.

**Class 3 is the interesting bucket and also the least informative one.** 28 of 83 targets sit
there. It is where anything with a crystal structure and no drug lands — a large, weakly
selective category.

---

## 4. What would change my mind

Concrete falsifiers, in order of how cheaply they can be run:

1. **Genome-wide, full-depth re-run of the same three knockdowns.** If SETDB1→HERV and
   TRIM28→Alu do not strengthen, the subset result was noise.
2. **STAR vs HISAT2 on identical samples.** If the two disagree on sign for the top hits, the
   local validation does not transfer to the cloud path and the measured layer needs redoing.
3. **Test an R2 prediction.** SUV39H1 knockdown is predicted to raise HERV9NC-int. ENCODE has
   no SUV39H1 knockdown, but if one is found or run and the effect is absent, R2 should be
   demoted or removed.
4. **Hold out a known gene.** Remove SETDB1's measured edges, see whether the remaining layers
   still reach the right answer. This is the honest test of whether the graph adds anything
   beyond the measurement.
5. **Human-annotate 100 abstracts** and score the LLM extraction against them. Until that
   exists, the literature tier's precision is unknown.

---

## 5. Honest positioning

**What it is:** a working demonstration that TEs can be represented in a biological knowledge
graph, that gene→TE edges can be measured from public perturbation data, and that inference
over such a graph can be made auditable end to end.

**What it is not:** a validated atlas. The coverage claim ("any gene") is architectural. Three
genes have been measured.

**The strongest honest sentence available:** *the pipeline, the schema, the rule layer and the
citation gate all work on real data, and the thing standing between this and an actual atlas is
compute, not design.* That is a defensible claim and it is the one worth making.

**The sentence to avoid:** any version of "we built a TE knowledge graph for all human genes."
The graph has 1,350 nodes and ten measured edges.
