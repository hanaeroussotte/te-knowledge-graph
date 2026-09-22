# Does the engine reproduce the DNMT3A / TET2 hypothesis?

**The hypothesis under test** — now published, with this project's author as a co-author:

> Hasan M, Durandeau S, Thompson IR, **Roussotte H**, et al. "Retrotransposable element
> derepression distinguishes DNMT3A-mutant from TET2-mutant clonal haematopoiesis."
> *GeroScience*, 16 September 2026.
> [10.1007/s11357-026-02510-6](https://doi.org/10.1007/s11357-026-02510-6) · PMID 42744964

In DNMT3A-mutant clonal haematopoiesis, TE reactivation lies on the path to inflammation. In
TET2-mutant CH, inflammation occurs but **not** through TE reactivation. **Section 8 records
what the paper actually measured**, and why the fact that the author is on it changes how
this document may be cited.

**Short answer: yes — and the engine derives the asymmetry rather than being told it.**
It also makes a sharper claim than the hypothesis states, which is good, because sharper means
easier to falsify.

---

## 1. What the engine now returns

```
=== DNMT3A  [best tier: curated]   curated=1  inferred=1
Losing DNMT3A is predicted to RAISE TE:global
  derived by R2_WRITER_TRANSFER

=== TET2    [best tier: inferred]  inferred=1
Losing TET2 is predicted to LOWER TE:global
  derived by R3_ERASER_INVERSION
```

Opposite signs. Neither gene was given any TE annotation.

## 2. How it got there

Both proofs rest on one measurement and two ontology records:

```
DNMT3A -SILENCES-> TE:global              [inferred, R2_WRITER_TRANSFER]
  5mC -MARK_AT-> TE:global                [inferred, R1_MARK_GROUNDING]
    DNMT1 -SILENCES-> TE:global           [MEASURED: ENCODE ENCSR600OWF, this run]
    DNMT1 -DEPOSITS_MARK-> 5mC            [curated: GO:0003886]
  DNMT3A -DEPOSITS_MARK-> 5mC             [curated: GO:0003886]

TET2 -DEREPRESSES-> TE:global             [inferred, R3_ERASER_INVERSION]
  5mC -MARK_AT-> TE:global                [inferred, R1_MARK_GROUNDING]
    DNMT1 -SILENCES-> TE:global           [MEASURED: ENCODE ENCSR600OWF, this run]
    DNMT1 -DEPOSITS_MARK-> 5mC            [curated: GO:0003886]
  TET2 -ERASES_MARK-> 5mC                 [curated: GO:0070579]
```

The chain in words: knocking down **DNMT1** raised TE expression relative to protein-coding
genes (median log2FC difference **+0.130**, Mann-Whitney **p = 1.4 × 10⁻⁷**). GO says DNMT1
writes 5mC. Therefore 5mC is a silencing mark over TEs. GO says **DNMT3A also writes 5mC** —
so losing it should raise TEs. GO says **TET2 erases 5mC** — so losing it leaves *more* mark
and should *lower* TEs.

## 3. Why this is a stronger result than "consistent with"

Three things make it more than a restatement of the hypothesis.

**It is derived, not encoded.** Nothing in the graph says "DNMT3A affects TEs" beyond one
generic GO annotation, and **nothing at all** connects TET2 to transposable elements — TET2 is
absent from all 112 GO-curated TE regulators and did not survive the literature filter. The
only inputs are a DNMT1 measurement and two molecular-function annotations. The asymmetry falls
out of the writer/eraser sign logic.

**It is sharper than the hypothesis.** Your model says TET2-driven inflammation is *not* via TE
reactivation. The engine says something stronger and more testable: **TET2 loss should
actively reduce TE expression.** If that holds, TE reactivation cannot be the TET2 inflammation
route — it points the wrong way, not merely a different way. That is a cleaner experimental
prediction than "not involved".

**The measured anchor would have been missed by standard analysis.** DNMT1 has **zero** TE
subfamilies at FDR < 0.1. Reading only the padj column calls it a null result. The effect is
visible only as a set-level shift of the TE compartment against the protein-coding compartment
— a comparison that is internally controlled, because size-factor normalisation moves both sets
together and so cannot manufacture a difference between them.

## 4. The specificity result, which also fits your model

Three knockdowns, three different behaviours:

| Knockdown | Mark | Set-level TE shift | Strongest individual hits |
|---|---|---|---|
| SETDB1 | H3K9me3 | **none** (p = 0.16) | HERVE-int, HERV9NC-int (ERVs only) |
| TRIM28 | recruits SETDB1 | **+0.410** (p = 1.9 × 10⁻²²) | AluY, AluYa5, MIR |
| DNMT1 | 5mC | **+0.117** (p = 7.2 × 10⁻⁸) | none individually |

SETDB1 is a targeted ERV silencer. TRIM28 and DNMT1 move the whole TE compartment. This
matters for your framing: **the 5mC axis — where DNMT3A and TET2 live — is the global one.**
A DNMT3A-mutant clone would be predicted to raise TE expression broadly rather than at a few
specific loci, which is the profile more likely to trip a nucleic-acid sensor.

## 5. What this does NOT establish

Stated plainly, because the gap between what was measured and what the hypothesis claims is
large.

1. **DNMT3A was not measured. DNMT1 was.** The DNMT3A prediction is a transfer across two
   enzymes that share a catalytic product but differ in targeting: DNMT1 is the maintenance
   methyltransferase, DNMT3A is *de novo*. Rule R2 assumes writers of the same mark are
   interchangeable, which is the weakest assumption in the rule set. **This is the first thing
   a knowledgeable reviewer will attack, and they are right to.**
2. **TET2 was not measured either.** Its prediction is R3 applied to the same grounding.
3. **The inflammation arm was not measured at all.** No interferon or ISG readout was tested.
   Everything downstream of `TE:global` in the figure is drawn as an explicitly unmeasured
   consequence arm.
4. **K562, not clonal haematopoiesis.** An immortalised erythroleukaemia line with an abnormal
   epigenome. Nothing here shows transfer to HSPCs or to a mutant clone in a patient.
5. **Knockdown ≠ the CH mutation.** DNMT3A R882H is a dominant-negative missense with
   hypomorphic and possibly neomorphic behaviour; TET2 CH mutations are typically
   loss-of-function. A CRISPR knockdown models the latter far better than the former.
6. **Set-level, not locus-level.** `TE:global` is a summary over ~500 subfamilies. It says the
   compartment moved; it does not identify which elements.

## 5b. The interferon arm: attempted, and NOT testable at this reference scope

The obvious next step was to score an interferon-stimulated-gene signature per sample from the
gene counts already in the matrix, and ask whether TE derepression and ISG induction co-move.
It was run. **The result is not interpretable, and the reason is the chromosome subset.**

| Signature (GO, via QuickGO) | genes in set | on chr1/chr19 | coverage |
|---|---|---|---|
| Type I interferon response (GO:0034340) | 125 | 21 | **16.8%** |
| Type II interferon response (GO:0034341) | 107 | 24 | 22.4% |
| Defense response to virus (GO:0051607) | 264 | 46 | 17.4% |
| Inflammatory response (GO:0006954) | 725 | 130 | 17.9% |
| Cellular senescence (GO:0090398) | 83 | 8 | 9.6% |

Every canonical sensor and effector except IRF3 is on a chromosome that was not indexed:
**CGAS (chr6), STING1 (chr5), IFIH1 (chr2), MAVS (chr20), TBK1 (chr12), STAT1 (chr2), STAT2
(chr12), IRF7 (chr11), MX1 (chr21), OAS1 (chr12), IFIT1 (chr10).** Of the machinery, only
IRF3 (chr19), ISG15 (chr1) and ADAR (chr1) were quantified at all.

The set-level test on the 17% that *was* measured returns no interferon induction — and in
SETDB1 the inflammatory set is significantly *down* (Δmedian log2FC −0.43, p = 5.8 × 10⁻⁹).
**That must not be reported as a biological finding.** It is a statement about a biased
one-sixth of a gene set, scored on a reference that excludes the pathway's core.

This adds a second concrete thing the genome-wide run buys, alongside grounding 5mC:
**it makes the TE → sensing → inflammation link testable at all.** Right now the project can
measure the TE arm and cannot measure the inflammation arm, which is precisely the junction
the hypothesis turns on.

### 5c. RESOLVED — the arm was made measurable, and the answer is a null with a reason

*(Added after §5b; full write-up in `docs/PANEL_REFERENCE.md`.)*

Rather than wait for a genome-wide run, the missing loci were spliced into the existing
reference as 921 extra contigs covering 990 signature genes (`src/build_panel_reference.py`).
Coverage of the type-I interferon set went **0.168 → 0.768**; defense-response-to-virus
0.174 → 0.708; senescence 0.096 → 0.783. The inflammatory-response set reached only 0.535
and is **still refused** by the coverage guard.

A reference-perturbation control on the identical FASTQs confirms nothing already measured
moved: Pearson 0.992–0.996 against the original log₂FCs, median |Δ| ≤ 0.027, no sign flips,
and the set-level TE deltas unchanged (TRIM28 +0.408, DNMT1 +0.136, SETDB1 +0.024).

**The measured answer, at real coverage:**

| Knockdown | TE arm Δ | 95% CI | Interferon arm Δ | 95% CI |
|---|---|---|---|---|
| SETDB1 | +0.024 | −0.062 … +0.115 | +0.023 | −0.056 … +0.060 |
| TRIM28 | **+0.408** | +0.311 … +0.467 | −0.023 | −0.126 … +0.061 |
| DNMT1 | **+0.136** | +0.095 … +0.178 | −0.011 | −0.059 … +0.042 |

No signature moves under Bonferroni across the 15 tests, under either background
(`all_other_genes` and the panel-only control background agree). The interferon intervals
exclude effects of TE-arm magnitude, so this is a measured absence.

**Why, from the same data.** In K562 the transducers are abundant — `TYK2` 799 CPM, `MAVS`
586, `IRF3` 317, `JAK1` 317, `STAT2` 286, `STING1` 270 — and the **pathway's entry points
are at the floor**: `CGAS` 0.21 CPM (non-zero in 1 of 11 samples), `ZBP1` 0.26, `NLRP3`
0.20, `TLR3` 0.00, `RIGI` 5.4, `IFIH1` 8.5. `ADAR`, the principal brake on MDA5 sensing of
endogenous double-stranded RNA, is at 823 CPM, and there is no tonic interferon tone to
raise (`IFNB1` 0.00, `OASL` 0.00).

**What this means for the hypothesis.** It does not test it. K562 cannot mount the response
the hypothesis requires, so the DNMT3A-arm prediction — TE reactivation → viral mimicry →
inflammation — is neither supported nor refuted here. What the project now has is a
*validated instrument* for the junction: the TE arm and the inflammation arm are measured
in the same libraries, on the same reference, with a control showing the reference change is
inert, and a rule (`R6_TE_MEDIATED_INFLAMMATION`) that fires only when both move in the same
contrast. It currently fires zero times, correctly.

**The experiment this specifies.** Repeat in a sensing-competent cell type — one expressing
cGAS/STING and MDA5, e.g. primary or immortalised haematopoietic progenitors, or K562
reconstituted with cGAS — and ideally with a DNMT3A or TET2 perturbation rather than DNMT1.
That is now a concrete protocol rather than an aspiration, and it is the single most
informative next experiment for the hypothesis.

Tables: `signature_coverage_panel.csv`, `signature_setlevel_tests_panel.csv`,
`two_arm_effects.csv`, `sensor_expression_k562.csv`, `reference_perturbation.csv`.
Figure: `fig_two_arm.png`.

Tables: `signature_coverage_chr_subset.csv`, `signature_setlevel_tests.csv`,
`signature_scores.csv` — all retained so the attempt and its failure mode are reproducible.

*A further caution for when this is re-run at genome scale:* the two control groups differ
sharply on the ISG score (non-targeting +0.71 vs CRISPR control −0.84, mean z). That is a
batch split between the CRISPRi and CRISPR series, not biology, and it will swamp any
cross-sample correlation. The comparison must stay contrast-internal.

## 6. What would settle it — in cost order

1. **Genome-wide, full-depth re-run of DNMT1** (already staged). If the set-level shift
   strengthens and individual subfamilies clear FDR, the anchor becomes much harder to argue
   with. *This is the single highest-value next run.*
2. **Find or generate DNMT3A and TET2 knockdown RNA-seq.** Neither exists in ENCODE. This
   converts both predictions from `inferred` to `measured` and directly tests R2 and R3. If
   TET2 loss does **not** lower TEs, R3 is wrong and should be removed.
3. **Add an ISG readout.** The gene-level counts are already in the matrix — scoring an
   interferon-stimulated-gene signature per sample costs nothing and would test whether TE
   derepression and ISG induction co-move across the three existing knockdowns. **This is
   cheap and was not done; it is the obvious next analysis.**
4. **Primary HSPCs with genotyped CH.** What the hypothesis is actually about, and the only
   thing that would make it a statement about patients.

## 7. The honest sentence for the pitch

> The engine independently derives the DNMT3A/TET2 asymmetry from one DNMT1 measurement and two
> GO annotations, with a proof tree for each. It predicts that DNMT3A loss raises TE expression
> and TET2 loss lowers it — opposite signs on the same axis. That is a falsifiable prediction
> consistent with the published CH hypothesis, generated rather than assumed. It is not
> evidence for the hypothesis: DNMT3A and TET2 were not themselves measured, and the
> inflammation arm was not measured at all.

The value on offer is a hypothesis-generation engine that reconstructs a real, non-obvious
model from public data and states exactly which experiment would break it. That is worth more
than a confirmation would be.

---

## 8. The hypothesis is now published — what that does and does not give us

Added 2026-09-22, when the author supplied the paper. It changes three things and must not
be allowed to change a fourth.

### 8.1 What the paper measured

| | |
|---|---|
| **Cohort** | 68 PBMC samples from a healthy-ageing cohort (hip-replacement surgery, n = 738 population study) |
| **Groups** | DNMT3A high-VAF (>10%) n = 10 · DNMT3A low-VAF (≤10%) n = 30 · DNMT3A/TET2 double-mutant n = 9 · TET2-mutant n = 7 · non-CH control n = 12 |
| **Sequencing** | total RNA (no poly(A) selection), 150 bp paired-end, mean **65.1 M reads/sample**, nf-core/rnavar v1.0, hg38 |
| **Gene + RTE quantification** | **featureCounts v2.0** — genes against GENCODE, RTEs against RepeatMasker regions, rlog-normalised at **class and family** level |
| **Families examined** | nine: CR1, L1, L2 (LINE); Alu, MIR (SINE); ERV1, ERVL, ERVL–MaLR, ERVK (LTR) |
| **Statistics** | DESeq2 v1.42.0, `~Batch+Sex+Age+Group`; log₂FC > 0.5 and **raw** *p* < 0.05, with adjusted values supplied separately |
| **Validation** | TARGET-seq single-cell (5 DNMT3A, 3 TET2; EGAS00001007358) pseudobulked per lineage, plus an independent bulk cohort (GSE263013, 92 PBMC donors → 7 DNMT3A high-VAF, 6 TET2-mutant) |

**Findings:**

- **DNMT3A high-VAF → widespread RTE derepression**, dominated by **LINE:L1** and
  **LTR:ERV1/ERVL**. The RTE-high subgroup is enriched for **TNF-α/NF-κB signalling,
  inflammatory response, interferon regulatory genes** (higher TNF and S100A9) and
  senescence signatures.
- **Heterogeneity within high-VAF, which is the paper's subtlest result.** Two distinct
  subgroups: one with markedly elevated RTE expression, one indistinguishable from controls.
  **PWWP-domain** mutations were exclusively RTE-high; the recurrent **R882H** hotspot
  clustered with *low* RTE expression while **R882C** was RTE-high. Interpret with care at
  n = 10, as the paper does — but it means *DNMT3A-mutant* is not one phenotype.
- **TET2-mutant → a non-significant trend toward *reduced* RTE expression** versus controls,
  with subfamily-level downregulation across all three comparisons and **CR1, L2, ERVL, MIR
  significantly lower than DNMT3A high-VAF**. No RTE-associated inflammatory signature;
  instead **oxidative phosphorylation, ROS and mTORC1** enrichment. Inflammation by a
  metabolic/redox route, not a retroelement one.
- **Double mutants sit in between**, trending above TET2 and clearly below DNMT3A high-VAF,
  with TNF–NF-κB and interferon programmes attenuated.
- **TARGET-seq:** DNMT3A-mutant cells carry more upregulated RTE subfamilies than
  TET2-mutant across lineages, strongest in **erythroid and megakaryocyte** compartments,
  with ERV1, ERVL, ERVL–MaLR and L1 contributing most.
- **A finding that touches this graph directly:** RTE-high DNMT3A clones were enriched for
  **HUSH-mediated silencing** and SIRT1-mediated rRNA regulation, read as a compensatory
  response to lost DNMT3A methylation. HUSH (MPHOSPH8/TASOR/PPHLN1) is already a complex in
  this graph and R4_COMPLEX_CONSENSUS operates over it.

### 8.2 The engine's derived direction agrees

Section 1 shows the engine predicting, from a DNMT1 knockdown plus two GO annotations:

```
DNMT3A loss  →  RAISE TE:global      (R2_WRITER_TRANSFER)
TET2   loss  →  LOWER TE:global      (R3_ERASER_INVERSION)
```

Section 3 called the TET2 arm "sharper than the hypothesis states, which is good, because
sharper means easier to falsify" — the published hypothesis says inflammation is *not
TE-mediated* in TET2 CH, which is a statement about the mechanism, whereas the rule commits
to a **direction**: TEs go *down*.

**The paper measures them going down.** Non-significantly versus controls, significantly
versus DNMT3A high-VAF, and consistently at subfamily level across all three comparisons.

What makes that worth more than a coincidence of pipelines is how little the two analyses
share:

| | Hasan et al. 2026 | this project |
|---|---|---|
| System | primary human PBMCs, 68 donors | K562 cell line, 3 knockdowns |
| Perturbation | naturally occurring somatic mutation | CRISPR / CRISPRi knockdown |
| Gene perturbed | DNMT3A, TET2 themselves | **DNMT1** — neither of them |
| Quantifier | featureCounts over RepeatMasker | TEcount, EM allocation |
| Resolution | class and family | **subfamily** |
| Route to the claim | measured directly | derived through two GO annotations |

Different quantifier, different resolution, different modality, different tissue, and the
engine never saw DNMT3A or TET2 data at all.

### 8.3 The four caveats, and the fourth is the one that matters

1. **The TET2 result is a non-significant trend** versus controls at n = 7. It is
   significant against DNMT3A high-VAF, which is a different comparison. Say "trend", not
   "shown".
2. **The engine's anchor is DNMT1, not DNMT3A.** R2 transfers a measured DNMT1 effect to
   DNMT3A via a shared curated enzymatic role; R3 inverts it for an eraser. Both remain
   `inferred`. Neither DNMT3A nor TET2 has been perturbed in this project, and §19 of the
   walkthrough shows that 5mC is grounded by exactly **one** edge.
3. **Resolution and quantifier differ**, so this is directional agreement, not replication.
   The paper's family-level analysis is also a live example of the aggregation whose power
   cost this project measured (`aggregation_level_comparison.csv`) — the paper's own TET2
   signal being non-significant at family level is consistent with that.
4. **This is not a blind prospective validation, and must never be presented as one.** The
   hypothesis was known to this project from the start — it is in the first line of this
   document — and the author is the paper's fourth author. The *rule firing* is mechanical
   and its premises are curated annotations rather than that paper, so the derivation is
   genuinely blind to it. But the choice to ask about DNMT3A and TET2 was not. What is fair
   to claim: **the engine reconstructs the published asymmetry from unrelated public data
   and commits to a sharper, directional version of it that the measurement then agrees
   with.** What is not fair: "independent confirmation", "we predicted this", or any framing
   that hides the co-authorship.

### 8.4 The honest sentence, updated

> The hypothesis is published — Hasan et al., *GeroScience* 2026 — and I'm a co-author, so
> this project instruments my own prior finding rather than confirming it. What is not
> trivial is that the engine reconstructs the asymmetry from a DNMT1 knockdown and two GO
> annotations, having never seen DNMT3A or TET2 data, and commits to a *directional* claim
> the paper's own hypothesis does not make: TEs go down in TET2. The paper measures a trend
> in that direction, by a different quantifier at a different resolution in a different
> tissue. That is what a hypothesis-generation engine is supposed to do, and the experiment
> that would break it is still the obvious one — perturb DNMT3A and TET2 directly.

### 8.5 What it changes in the next-experiment list

Section 6 item 2 — *find or generate DNMT3A and TET2 knockdown RNA-seq* — is unchanged and
still the test that converts both predictions from `inferred` to `measured`.

Two additions come from the paper:

- **The HUSH enrichment is a testable point of contact.** If HUSH silencing is compensatory
  in RTE-high DNMT3A clones, then perturbing HUSH components should interact with DNMT3A
  status. MPHOSPH8, TASOR and PPHLN1 are already in the graph and ENCODE knockdown data
  exists for parts of the complex — this is a concrete, cheap next contrast.
- **`DNMT3A-mutant` should not be one node.** PWWP-domain versus R882H versus R882C behave
  differently, and the graph currently has a single DNMT3A gene node. Mutation-level
  resolution is the same class of problem as locus-level TE resolution
  (`TE_RESOLUTION.md` §8): the schema forces a coarser entity than the biology supports.
  Logged, not built.
