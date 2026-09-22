# Technical summary for external review

**Purpose.** A self-contained description of what this project measured, inferred and
refused, written to be handed to a reviewer with no access to the repository. Numbers are
quoted from saved result tables. Where something is unmeasured it says so.

**What I want checked** is listed in §12. Please attack those specifically rather than the
positioning — the positioning has already been through two adversarial passes.

---

## 1. One-sentence description

An evidence-traceable perturbational reasoning system for transposable-element (TE)
regulation: it re-analyses public perturbation RNA-seq for effects on the repetitive genome,
converts those measurements into signed, provenance-tracked graph edges, connects them to
curated mechanism, derives testable hypotheses with inspectable proofs, and reports when the
evidence is insufficient.

**Status: architecture with a worked example, not an atlas.** Three genes measured, not 570.

---

## 2. What was measured

**Data.** Three ENCODE knockdown RNA-seq experiments in K562, 11 libraries total:

| Target | Accession | Method | Control |
|---|---|---|---|
| SETDB1 | ENCSR819PCU | CRISPRi | ENCSR095PIC (non-targeting) |
| TRIM28 | ENCSR591QYK | CRISPRi | ENCSR095PIC (non-targeting) |
| DNMT1 | ENCSR600OWF | CRISPR | ENCSR712CQC (CRISPR control) |

**Pipeline.** FASTQ → subsample to 1.5 M reads/library → HISAT2 `-k 100` against a
**chr1+chr19-only** index → name-ordered BAM → `TEcount --mode multi` (TEtranscripts, Jin et
al. 2015) against an hg38 RepeatMasker-derived TE GTF → PyDESeq2.

**TE vocabulary.** UCSC RepeatMasker, filtered to LINE/SINE/LTR/DNA/Retroposon/RC and loci
≥100 bp: **3,761,678 loci across 1,057 subfamilies**. Analysis is at **subfamily** level.

**Normalisation.** DESeq2 size factors estimated on **protein-coding genes only**
(PyDESeq2 `control_genes`), deliberately excluding TEs so that a global TE shift cannot
partly normalise itself away.

**Two statistics per contrast, always:**
1. Per-feature Wald test with Benjamini–Hochberg FDR.
2. A **set-level** test: Mann–Whitney on the TE-subfamily log₂FC distribution versus the
   protein-coding-gene log₂FC distribution *from the same contrast*.

### 2.1 Per-feature results (FDR < 0.1)

| Knockdown | TE subfamily | log₂FC | padj |
|---|---|---|---|
| TRIM28 | AluY | +0.790 | 0.0005 |
| TRIM28 | AluYa5 | +0.990 | 0.068 |
| TRIM28 | SVA_D | −0.408 | 0.080 |
| SETDB1 | HERVE-int | +0.966 | 0.083 |
| TRIM28 | MIR | +0.559 | 0.090 |
| SETDB1 | HERV9NC-int | +1.198 | 0.090 |
| DNMT1 | **none** | — | best padj 0.41 |

### 2.2 Set-level results

| Knockdown | Δ (TE − gene median log₂FC) | frac TE up | Mann–Whitney p | **correlation-aware p** | leave-one-library-out | permutation |
|---|---|---|---|---|---|---|
| SETDB1 | +0.023 | 0.53 | 0.41 | 0.89 | −0.40..+0.70, sign flips | p = 1.00 (floor 0.10) |
| TRIM28 | +0.421 | 0.73 | ~~2.3 × 10⁻²¹~~ | **0.44** | −0.02..+1.12, **sign flips** | p = 0.67, null beat observed |
| **DNMT1** | **+0.130** | **0.63** | ~~1.4 × 10⁻⁷~~ | **0.045** | **+0.10..+0.19, sign held 4/4** | most extreme of 3, 3.7× null |

**The Mann–Whitney values are struck through because they are retracted as evidence.** They
treat 322–503 TE features as independent observations; measured mean pairwise correlation ρ̄
is 0.006 (DNMT1) to 0.48 (TRIM28), giving variance-inflation factors of 4.1 to 155 — i.e. the
two CRISPRi contrasts carry roughly **two** features' worth of independent information, not
300. Full analysis and method in `COMPARTMENT_STATISTICS.md`.

**The DNMT1 result is the one that matters, and it is the one that survived being attacked.**
No individual subfamily clears FDR 0.1, yet Δ = +0.13 with 63% of 503 features up, the same
sign in **all six** alternative feature-set definitions (LINE +0.19, SINE +0.10, LTR +0.11,
DNA +0.10, expression-filtered +0.13, trimmed +0.13), stable under leave-one-library-out
(+0.10 to +0.19, sign preserved in all four drops), the most extreme of the three admissible
sample labellings by a factor of 3.7, and a correlation-aware p of 0.045. A per-feature-only
analysis would report "no effect". **This grounds 5mC, which is the only route by which the
reasoning layer reaches DNMT3A and TET2 — so it matters that it is the arm that held.**

**TRIM28's compartment claim is downgraded to an effect size.** Large (+0.42) and
directionally very consistent (73% up, same sign in 6/6 variants), but a permuted labelling
produced a *larger* Δ than the real one, the sign does not survive leave-one-library-out, and
the correlation-aware p is 0.44. Its **per-feature** results are unaffected — AluY at
padj 0.0005 is a DESeq2 Wald test with BH correction, a different statistic that does not
depend on the compartment comparison.

At this depth and reference scope, SETDB1 shows several stronger individual HERV effects
without evidence of a global compartment shift, whereas TRIM28 and DNMT1 show broader
positive shifts in the TE distribution. That is what was observed; it is consistent with
SETDB1 acting as a targeted ERV silencer and does not establish specificity.

**The binding constraint is the design.** With two replicates per arm there are three
admissible label permutations, so **no sample-level p below 0.333 is attainable regardless of
effect size.** More replicates, not a better test, is what would settle these.

### 2.3 The normalisation-invariance argument

Size factors are **per-sample multiplicative**, so a size-factor error shifts the log₂FC of
TEs and of genes by the same additive amount and **cancels in the difference between their
medians**. A normalisation artefact therefore cannot manufacture a gap between two feature
sets measured in the same libraries.

The test itself is standard competitive gene-set testing (cf. CAMERA, GSEA) and is not
claimed as novel. What a literature search did not locate was this *argument* for using it
as the **primary** TE readout.

**Known limitation:** this is invariance to normalisation error, **not** biological
invariance. If a knockdown broadly activates transcription, TEs and protein-coding genes
could diverge for reasons unrelated to TE-specific silencing. Untested.

---

## 3. The interferon arm: a measured null with a mechanism

**Motivation.** The viral-mimicry hypothesis — TE derepression → cytoplasmic nucleic acid →
innate sensing → interferon.

**First attempt refused.** The chr1+chr19 reference contained only **16.8%** of the GO
type-I interferon gene set, so any result would describe chromosome membership rather than
biology. A coverage guard (`--min-coverage 0.6`) blocked it.

**Fix.** 990 off-scope signature genes were spliced into the reference as **921 merged
contigs (61.7 Mb)**, carrying GENCODE exon structure into contig coordinates. Overlapping
padded windows around clustered families (IFIT1/1B/3/5, OAS1/2/3, IFITM1/2/3, CASP1/5,
APOBEC3, IFNA) were merged first; emitting them separately would have duplicated 0.69 Mb of
sequence and converted unique reads into artificial multi-mappers at precisely the genes of
interest. Zero duplicated span is asserted in code.

Coverage: type-I IFN **0.168 → 0.768**; defense-response-to-virus 0.174 → 0.708; senescence
0.096 → 0.783. Inflammatory response (GO:0006954) reached only **0.535 and is still
refused**.

**Control for the reference change** (same FASTQs, both references):

| Knockdown | Pearson r (all) | r (TE only) | median \|Δlog₂FC\| |
|---|---|---|---|
| SETDB1 | 0.995 | 0.993 | 0.007 |
| TRIM28 | 0.996 | 0.993 | 0.027 |
| DNMT1 | 0.992 | 0.992 | 0.013 |

No sign flips among the six headline hits; set-level deltas unchanged. Cost: ~1,100 extra
features enlarge the multiple-testing set, losing 1–2 per-feature hits per contrast — so the
TE arm is quoted from the original reference and the inflammation arm from the panel run.

**Result: no detectable type-I interferon transcriptional signature moves in any contrast**, under Bonferroni across 15 tests,
under either background (all-other-genes and panel-only). Bootstrap 95% CIs:

| Knockdown | TE arm | interferon arm |
|---|---|---|
| SETDB1 | +0.024 [−0.062, +0.115] | +0.023 [−0.056, +0.060] |
| TRIM28 | +0.408 [+0.311, +0.467] | −0.023 [−0.126, +0.061] |
| DNMT1 | +0.136 [+0.095, +0.178] | −0.011 [−0.059, +0.042] |

The interferon intervals exclude effects of TE-arm magnitude.

**Mechanism, from the same data.** Mean CPM in K562: **sensors** TLR3 0.00, NLRP3 0.20,
CGAS 0.21 (non-zero in 1 of 11 samples), ZBP1 0.26, RIGI 5.4, IFIH1 8.5 — versus
**transducers** STING1 270, IRF3 317, JAK1 317, STAT2 286, MAVS 586, TYK2 799. ADAR 823;
IFNB1 and OASL 0.00.

**Conclusion as stated:** *TE derepression occurred without a detectable type-I interferon
transcriptional signature under these conditions. Several candidate upstream sensing
components are absent or expressed at very low levels, making K562 a weak context in which
to test viral mimicry. Without a positive stimulation control, functional competence of the
sensing pathway cannot be established, so this dataset cannot provide a decisive test.*

Note the deliberate narrowing: **not** "the sensing entry points are not expressed" (RIGI at
5.4 and IFIH1 at 8.5 CPM are expressed), **not** "no interferon response" (only a
transcriptional signature was measured — no secreted protein, phosphorylation or functional
signalling), and **not** "TE derepression does not cause interferon".

**Weakness (acknowledged):** no stimulation control (poly(I:C) or cGAMP) was run, so sensor
non-responsiveness is **inferred from mRNA abundance rather than demonstrated**.

---

## 4. The knowledge graph

**Scale.** 9,366 input edges over 1,910 declared nodes, assembled directly from REST APIs.

| Layer | Edges | Source |
|---|---|---|
| curated | 9,263 | Reactome 4,900 · Complex Portal 2,321 · STRING v12.0 (score ≥700) 1,724 · GO 318 |
| mechanism | 44 | GO **Molecular Function** only — `DEPOSITS_MARK` / `ERASES_MARK` |
| literature | 32 | LLM extraction from PubMed abstracts |
| measured | 12 | the contrasts in §2 |
| measured (inflammation) | 15 | all `NO_DETECTED_EFFECT_ON` |

Every edge carries provenance (source, native score, statistic, retrieval date) and one of
five evidence tiers: `curated | measured | literature | inferred | predicted`. Complex Portal
entries flagged as predicted complexes are tiered `predicted` (1,316 edges) and **the rule
layer refuses to traverse them**.

Every edge also carries 8 context columns (cell type, species, perturbation modality, assay,
timepoint, TE resolution, quantifier, reference scope), written as explicit
`not_applicable` rather than empty.

**Sign convention:** predicates describe the effect of **losing** the subject.
`SILENCES(G,T)` ⇒ knocking down G raises T.

### 4.1 Structural audit (42 metrics, script in repo)

**Passes:** 0 schema violations across 9,366 typed edges · 0 self-loops · 0 duplicate
triples · 0 blank context cells · 100% of edges carry source + retrieval date · 97.6% in one
connected component · median degree 2, max 188, top 1% of entities hold only 15.9% of edge
endpoints.

**One defect found:** `PPARG → Alu` asserted as **both** `SILENCES` and `DEREPRESSES`, both
literature-tier, **both extracted from the same abstract** (PMID 14668325). Not deleted — it
is a visible instance of an unmeasured error rate in that layer.

**Quantified weaknesses:**
- **21 of 1,057 TE subfamilies have any edge at all** (coverage 0.0199).
- **4 `MARK_AT` edges** ground the entire inference layer, covering 2 marks.
- Reactome alone is 52% of edges (pathway co-membership — weak evidence).
- `native_score` present on 19.8% of edges; a `statistic` on 1.2%.

---

## 5. The reasoning layer

Six forward-chaining rules, run to fixpoint, `MAX_HOPS = 4`. From 9,366 input edges they
derive **89** edges:

| Rule | Fires | What it does |
|---|---|---|
| R1_MARK_GROUNDING | 4 | measured gene effect + curated mark role ⇒ `MARK_AT(mark, TE)` |
| R2_WRITER_TRANSFER | 38 | another writer of the same mark ⇒ same-sign prediction |
| R3_ERASER_INVERSION | 45 | an eraser of that mark ⇒ opposite-sign prediction |
| R4_COMPLEX_CONSENSUS | 2 | curated complex membership, ≤8 members |
| R5_RECRUITMENT_CHAIN | **0** | **no `RECRUITS` edges exist in the graph** |
| R6_TE_MEDIATED_INFLAMMATION | **0** | requires TE derepression **and** inflammation induction in the *same* contrast |

A derived conclusion's tier is the **weakest tier on its path**. Derived edges **inherit
context** from premises: agreement inherits the value, disagreement becomes `mixed(a|b)`
(nested `mixed()` flattened), absence becomes `not_applicable`, and any specific experimental
context sets `context_generalization_required = yes`. 87 of 89 derived edges are so flagged.

Output is a proof tree whose leaves are real edge ids. A separate **citation gate** splits
generated prose into sentences and drops any sentence citing an edge id that does not exist
— including sentences citing nothing.

### 5.1 Anchor-dependence analysis

| Anchor removed | measured edges dropped | derived edges | genes answered |
|---|---|---|---|
| none | 0 | **89** | 10/10 |
| TRIM28 | 13 | **89** | 9/10 |
| DNMT1 | 6 | 83 | 7/10 |
| SETDB1 | 8 | **8** | 8/10 |

**Removing TRIM28 — the largest measured effect in the dataset — changes nothing.** A
scaffold has no `DEPOSITS_MARK` edge, cannot satisfy R1, and therefore contributes zero
inferential value: measured evidence enters the reasoning layer only through genes with a
curated enzymatic role. **No hold-out ever flipped a direction**; genes either keep the
prediction or return `best_tier: none`.

Consequence: the highest-value next experiment is **another writer or eraser of the same two
marks**, not more scaffolds and not "more data".

---

## 6. The worked example, and a disclosure

The engine derives, from the DNMT1 measurement plus two GO Molecular Function records and
**no DNMT3A or TET2 data of any kind**:

- DNMT3A loss ⇒ **raises** TE expression (R2)
- TET2 loss ⇒ **lowers** TE expression (R3)

Opposite signs on the 5mC axis. TET2 is annotated to no GO transposition or TE-silencing
term, and neither gene has any ENCODE knockdown.

**Disclosure: this reproduces the hypothesis of a paper I co-authored** (Hasan et al.,
*GeroScience* 2026, 10.1007/s11357-026-02510-6, PMID 42744964; I am 4th of 30 authors).
That paper measured 68 PBMC samples with **featureCounts over RepeatMasker at class/family
level**: DNMT3A high-VAF clones show widespread RTE derepression (LINE:L1, LTR:ERV1/ERVL)
with TNF-α/NF-κB, interferon and senescence enrichment; TET2-mutant clones show a
**non-significant trend toward reduced** RTE expression and inflammation via oxidative
phosphorylation/ROS/mTORC1 instead.

So the engine's directional prediction agrees with the measurement, across a different
quantifier, resolution, perturbation modality and tissue. **This is not independent
confirmation and not a blind prospective test** — the hypothesis was known to the project
from the outset. The rule firing is mechanical and its premises are curated annotations, so
the derivation is blind to the paper; the choice of question was not.

---

## 7. What was built, measured, and deliberately not shipped

1. **Rule-based literature extractor** — measured precision 0.109, recall 0.175, direction
   agreement 10/21 (chance). Code retained, not wired into the graph.
2. **Link prediction** — refused at design time: three knockdowns cannot support a held-out
   validation set.
3. **The interferon result at the original reference scope** — refused by the coverage guard,
   then made measurable by the panel, and still reported as a null.

---

## 8. Things tested and rejected

- **Class/family aggregation instead of subfamily.** Reduces power at this depth: AluY
  padj 0.0005 versus pooled `Alu:SINE` +0.616 not significant; SETDB1 2 hits → 0, TRIM28
  4 → 1. Retained subfamily resolution.
- **"Only young subfamilies respond" as the explanation** for why aggregation loses power —
  tested genome-wide and **rejected**. The reason aggregation loses power is therefore
  *unexplained*, and recorded as unexplained.

---

## 9. Prospective test, pre-registered and not yet read

DNMT3B knockdown (ENCODE ENCSR290GUQ, CRISPR, **HepG2**, 258.5 M reads) versus control
ENCSR306EWE. The engine predicts DNMT3B loss **raises** the TE compartment via R2.

**Stated confound, fixed before the data was opened:** the prediction is grounded in K562 and
the only available DNMT3B knockdown is HepG2, so this tests writer-transfer **and**
cross-cell-type generalisation simultaneously; a failure cannot distinguish them.

A knockdown-efficiency gate is specified: verify DNMT3B's own counts dropped **before**
reading any TE result, because a failed CRISPR produces a perfect null indistinguishable
from a refutation. Interpretations for every outcome are fixed in advance, including a
commitment to retract if the sign flips.

**Newly computed constraint:** of the 40 chromatin-mark writers and erasers in the graph,
**exactly three have an ENCODE knockdown** — SETDB1, DNMT1 (both measured) and DNMT3B. No
SUV39H1/H2, KDM4A–E, EZH2, TET1/2/3 or DNMT3A. The §5.1 recommendation is therefore
**exhausted within ENCODE** after this run; extending it requires GEO/SRA.

---

## 10. Compute design (pending execution)

Alignment and TE quantification are CPU/RAM-bound, independent per library, and all read the
same large index — so: build the HISAT2 index once into a shared read-only Volume, fan out
one container per library (4 CPU / 16 GB, retries=2), return small count tables.
**No GPU is requested anywhere.** DESeq2 on the merged matrix takes seconds and the rule
engine reaches fixpoint in under a second, both locally.

Honest comparison: Nextflow/Snakemake on AWS Batch or Slurm would execute the same DAG
perfectly well and may be preferable for a production facility. The claimed advantage is
runtime dynamism — deciding *which* perturbation to compute from the state of the evidence
rather than from a DAG fixed in advance.

**Pre-flight found three real defects before any spend**, now fixed: (a) `build_reference`
never created the TE GTF that `TEcount --TE` requires, so every worker would have died after
the expensive index build; (b) the documented invocation was `modal run`, which cannot work
because the App is constructed inside a function rather than at module scope; (c) there was
no step to retrieve count tables from the results Volume, so a successful run would have
left nothing locally to analyse.

---

## 11. Known limitations, ordered by consequence

1. **The entire 5mC arm rests on one contrast** at 1.5 M reads across two chromosomes. If
   that set-level shift is an artefact, R1 → R2 → R3 collapses and the DNMT3A/TET2 result
   goes with it.
2. **chr1 + chr19 is a biased pair.** chr19 is the most gene-dense human chromosome,
   unusually Alu-rich, and carries the large KRAB-zinc-finger clusters — the proteins that
   recruit TRIM28 to TEs. Direction of bias unknown.
3. **Normalisation-invariance ≠ biological invariance** (§2.3).
4. **`-k 100` truncation**; HISAT2 versus STAR never compared (a broken arm64 STAR build
   forced the choice); quantifier comparison against featureCounts/MAJEC pre-registered and
   **not run**. External evidence only: MAJEC reports r = 0.987 subfamily-level concordance
   with TEtranscripts.
5. **EM identifiability.** TEcount apportions ambiguous reads in proportion to unambiguous
   evidence. Subfamilies with no distinguishing positions get an estimate closer to a prior
   than a measurement — and ambiguity correlates with youth (AluY, L1HS), which correlates
   with interest. No per-subfamily identifiability metric is computed.
6. **Literature-layer error rate unmeasured** (§4.1), with one visible contradiction.
7. **The interferon mechanism is inferred from expression, not demonstrated** (§3).
8. **R2's core assumption — writers of the same mark are interchangeable — is false in
   general.** Targeting differs. It generates the largest share of derived edges.
9. **n = 11 libraries, 2–3 replicates.** Leave-one-library-out not run.
10. **Tractability figures are imported** Open Targets/ChEMBL buckets, not computed here.
11. **A literature search in this project was demonstrably wrong**: a paper was recorded as
    not found because queries used "retroelement"/"retrotransposon" where the title said
    "retrotransposable", plus one American spelling of "haematopoiesis". Every "not located"
    verdict rests on searches with the same blind spots.

---

## 12. What I would most like a reviewer to attack

1. **Is the set-level statistic the right primary readout**, given limitation 3? What test
   would distinguish TE-specific derepression from a global transcriptional shift, using only
   these data?
2. **Is the normalisation-invariance argument actually correct** as stated, or does the
   median-of-log₂FC difference have a dependence on the size factors I have missed?
3. **EM identifiability (limitation 5).** The proposed check is to compute a per-subfamily
   identifiability score and re-test the set-level result on identifiable subfamilies only.
   Is that the right diagnostic, and is there a standard one I should use instead?
4. **Bootstrap over features assumes exchangeability**, which correlated features violate
   (the problem CAMERA corrects). How much should I discount the interval widths in §3?
5. **The hierarchical alternative.** Would partial pooling across class → family → subfamily
   (negative-binomial likelihood, random effects) be a better answer than choosing a single
   resolution? It would let AluY borrow strength from Alu without collapsing into it. Any
   reason this is a bad idea for TE data specifically?
6. **Is chr19's composition (limitation 2) likely to inflate or deflate** a TE-versus-gene
   compartment comparison?
7. **R2's writer-interchangeability.** Is there a principled way to weight the transfer by
   shared targeting (co-localisation, shared recruiters) rather than treating all writers of
   a mark as equivalent?
8. **Is the K562 sensor-absence conclusion safe** without a stimulation control, or should
   the claim be weakened further?
9. **Given three anchors and no more available in ENCODE**, what is the highest-value
   experiment obtainable from public data?
