# Quantifier-robustness experiment

> **STATUS: NOT RUN.** This is a protocol, not a result. No number in this document is a
> measurement from this project. It is written out so that (a) the experiment is
> specified before anyone has an interest in its outcome, and (b) the reader can see
> exactly what would falsify our conclusions.

## 1. The question

Every TE result in this project comes from one quantifier: `TEcount` (TEtranscripts),
`--mode multi`, at subfamily resolution. The field now has at least six alternatives that
make different choices about multi-mapping reads, locus resolution and gene-overlap
contamination. A reviewer is entitled to ask whether our biology is a property of the
biology or a property of the tool.

**Hypothesis under test:** the three conclusions below are invariant to the choice of
quantifier.

| # | Conclusion | Where |
|---|---|---|
| Q1 | TRIM28 knockdown shifts the whole TE compartment (+0.41 median log₂FC vs genes) | `global_directional_shift.csv` |
| Q2 | DNMT1 knockdown shifts the TE compartment with no single subfamily at FDR < 0.1 | same |
| Q3 | SETDB1 is a targeted ERV silencer, not a global one | same |

## 2. Design

Same three contrasts, same 11 libraries, same subsampled FASTQs, same reference. **Only
the quantifier varies.** Everything downstream — DESeq2 model, size-factor gene set,
set-level test — is held fixed.

| Arm | Tool | Resolution | Multi-mapper handling |
|---|---|---|---|
| A (current) | TEcount / TEtranscripts | subfamily | EM, fractional assignment |
| B | featureCounts `--countMultiMappingReads` | subfamily | full count at every locus |
| C | Telescope | locus → aggregated to subfamily | Bayesian reassignment |
| D | SQuIRE | locus → aggregated to subfamily | EM with unique-read anchoring |
| E | MAJEC | locus + subfamily | unified gene/isoform/TE model |

Arm B is the user's published `TE_CHIP` pipeline and is the most important comparison,
because the two are currently treated as interchangeable in discussion and are not.

## 3. Pre-registered outcomes

Report all four, per contrast:

1. **Subfamily effect-size correlation** — Pearson and Spearman of log₂FC between each arm
   and arm A, over subfamilies present in both.
2. **Sign concordance** — fraction of subfamilies with the same sign; and separately for
   the subset at padj < 0.1 in either arm.
3. **Set-level shift concordance** — does the TE-vs-gene median difference keep its sign
   and rough magnitude? This is the primary endpoint, because it is the statistic our
   conclusions rest on.
4. **Which effects disappear under locus- or gene-aware modelling** — specifically, do any
   of the six headline subfamilies lose their effect under arm E, which removes
   exon-overlap contamination? Name them individually.

## 4. Pre-registered interpretation

Decide now, not after seeing the numbers.

| Result | Conclusion |
|---|---|
| Set-level sign and significance hold in ≥4 of 5 arms | Q1–Q3 are quantifier-independent; report as robust |
| Set-level holds in arms A, C, D, E but not B | The disagreement is with full-multi-counting, whose totals are not on a gene-comparable scale; explain rather than average |
| A headline subfamily disappears only under E | That subfamily's signal was exon-overlap contamination. **Retract it**, keep the compartment result |
| Set-level sign flips in any arm | Q1–Q3 are tool artefacts. Retract them and say so publicly |

The fourth row is the one that matters. It is written down here so that it cannot be
renegotiated later.

## 5. Cost

Roughly 11 libraries × 4 additional quantifiers. Telescope and SQuIRE need locus-level
annotation and more memory than a laptop has; MAJEC needs its own reference build. This is
a natural Modal fan-out — one container per (library × quantifier) pair, shared reference
Volume, results collected into one table. See `docs/COMPUTE.md`.

Estimated: ~44 CPU jobs, none GPU, a few hours wall-clock on parallel containers.

## 6. Why it has not been run

Honestly: time, and the fact that arms C–E each need a reference build we do not have.
It is the single clearest next test of this project's correctness, it is listed as such in
`CRITIQUE.md`, and it is the first thing that should be done with cloud credits.
