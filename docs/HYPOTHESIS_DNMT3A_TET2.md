# Does the engine reproduce the DNMT3A / TET2 hypothesis?

**The hypothesis under test** (from the user's prior research): in DNMT3A-mutant clonal
haematopoiesis, TE reactivation lies on the causal path to inflammation. In TET2-mutant CH,
inflammation occurs but **not** through TE reactivation.

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
