# Interpreting the results — what the numbers mean and the maths behind them

Covers: how counts become fold changes, what log2FC and padj actually are, how to read a
volcano plot, what we expected versus what we got, and the traps specific to TE data.

---

## 1. The starting point: a count matrix

After alignment and counting you have a table — features (genes and TE subfamilies) down the
side, samples across the top, integer read counts inside.

|  | SETDB1_rep1 | SETDB1_rep2 | non_targeting_rep1 |
|---|---|---|---|
| ENSG00000000457 | 11 | 8 | 14 |
| AluY:Alu:SINE | 412 | 388 | 265 |
| HERVE-int:ERV1:LTR | 37 | 41 | 19 |

You cannot compare these numbers directly. Two reasons: libraries differ in total reads, and
count data has variance that grows with the mean.

## 2. Normalisation — the median-of-ratios size factor

If sample A was sequenced twice as deeply as sample B, everything in A looks twice as big.
DESeq2 corrects this per sample with a single scaling number, the **size factor**.

For feature *i* in sample *j* with count *K<sub>ij</sub>*, over *m* samples:

$$
s_j \;=\; \underset{i}{\mathrm{median}}\;
\frac{K_{ij}}{\left(\prod_{v=1}^{m} K_{iv}\right)^{1/m}}
$$

In words: compute each feature's geometric mean across all samples; for each sample take the
ratio of its count to that mean; the **median** of those ratios is the size factor. The median
makes it robust — a handful of wildly changing features cannot drag it.

**Why this matters specifically for TEs.** The size factor is estimated on the **joint gene +
TE matrix**. If you normalised TEs against TE-only totals, a genuine global rise in TE
expression would be divided straight back out and become invisible. Pooling is not a
convenience; it is what makes a global TE shift detectable at all. (§6 is a result that only
exists because of this.)

## 3. The model — negative binomial

Read counts are discrete and over-dispersed: repeat the same experiment and the variance
exceeds the mean, because biological replicates genuinely differ. The Poisson distribution
(variance = mean) is too narrow. DESeq2 uses the **negative binomial**:

$$
K_{ij} \sim \mathrm{NB}(\mu_{ij},\ \alpha_i), \qquad
\mu_{ij} = s_j\, q_{ij}, \qquad
\log_2 q_{ij} = \sum_r x_{jr}\,\beta_{ir}
$$

with variance

$$
\mathrm{Var}(K_{ij}) \;=\; \mu_{ij} \;+\; \alpha_i \mu_{ij}^{2}
$$

- *α<sub>i</sub>* is the **dispersion** — the extra biological variability of feature *i*. At
  α = 0 this collapses to Poisson.
- *x<sub>jr</sub>* is the design matrix (here: is this sample knockdown or control?).
- *β<sub>ir</sub>* is what we want: **the log2 fold change**.

**Dispersion estimation** is the delicate part at low replication. DESeq2 does it in three
stages: a per-feature maximum-likelihood estimate; a smooth trend fitted across all features
as a function of mean expression; then empirical-Bayes shrinkage of each feature's estimate
toward that trend. With n = 2–3 per arm — as here — the per-feature estimate is nearly
worthless on its own and the shrinkage is doing most of the work. **This is the single biggest
statistical caveat in this project.**

## 4. log2 fold change

$$
\log_2 \mathrm{FC} \;=\; \log_2\!\frac{q_{\text{knockdown}}}{q_{\text{control}}}
$$

| log2FC | meaning |
|---|---|
| +1.0 | doubled |
| +0.79 (our AluY hit) | ×1.73 |
| 0 | no change |
| −1.0 | halved |

**Sign convention used everywhere in this project:** the contrast is always *knockdown vs
control*, so **positive means the feature went UP when the gene was removed** — i.e. the gene
was holding it down. That is why a positive log2FC becomes a `SILENCES` edge in the graph.

**These are unshrunken (MLE) estimates.** `lfc_shrink` was not applied. Consequence:
low-count features can show large fold changes that are mostly noise. Always read log2FC
alongside `baseMean`. (Shrinkage would pull those toward zero and is worth adding for the
full-depth run.)

## 5. p-value and padj

**The Wald test.** For each feature, divide the estimated coefficient by its standard error:

$$
z_i = \frac{\hat{\beta}_i}{\mathrm{SE}(\hat{\beta}_i)}, \qquad
p_i = 2\left(1 - \Phi(|z_i|)\right)
$$

*p* answers only: *if this gene truly did not change, how often would I see an effect at least
this large by chance?* It says nothing about effect size or importance.

**Why raw p is not enough.** We test ~3,000 features at once. At p < 0.05, pure chance gives
~150 false positives. So we control the **false discovery rate** with Benjamini–Hochberg: sort
the *m* p-values ascending, then

$$
\mathrm{padj}_{(k)} \;=\; \min_{j \ge k}\ \min\!\left(1,\ \frac{m\, p_{(j)}}{j}\right)
$$

**Reading padj:** `padj < 0.1` means that among all features called at that threshold, about
10% are expected to be false. It is a property of the *list*, not of any single feature.

**Why so many padj are `NaN`.** DESeq2 applies **independent filtering** — it removes
low-count features (which have almost no power) before correction, because doing so increases
the number of true discoveries. Filtered features get `padj = NA`. In our data: 286 of 353 TE
subfamilies for SETDB1, 275 of 322 for TRIM28. A `NaN` means "not tested", not "not
significant". Cook's-distance outlier removal also produces `NA`, and with n = 2 no
replacement is possible.

## 6. How to read a volcano plot

A volcano plot puts **log2FC on x** and **−log10(p) on y**. Higher = more statistically
confident; further from centre = bigger effect.

```
        ^  -log10(p)
        |
   (A)  |  (B)        A  strong, confident DOWN
        |             B  strong, confident UP   <- what a silencer knockdown should produce
  - - - + - - -  p=0.05
        |
   (C)  |  (D)        C,D  changed a lot but not confidently — usually low counts
--------+-------->  log2FC
        0
```

The dense cloud near the centre is the majority: unchanged. Points climb the y-axis only when
the effect is large *relative to its variability*.

**What to check before believing a point:** its `baseMean`. A log2FC of +3.8 on a subfamily
with 12 reads (our `Tigger15a`) is noise wearing a big number. A log2FC of +0.79 on AluY with
thousands of reads is real.

In our figure the points are coloured by TE class, and only points at padj < 0.1 are labelled —
deliberately, so the eye is not drawn to large-but-unsupported values.

## 7. What we expected, and what we got

**The prior.** SETDB1 and TRIM28 are textbook TE silencers. Removing them should raise TEs:
positive log2FC, with TRIM28 hitting SINEs/LINEs and SETDB1 hitting endogenous retroviruses.
**If that had not happened, the pipeline would be broken** — that is the entire reason for
running known genes first rather than interesting ones.

**What we got, per feature:**

| Knockdown | Subfamily | log2FC | padj |
|---|---|---|---|
| TRIM28 | AluY | +0.79 | 0.00053 |
| TRIM28 | AluYa5 | +0.99 | 0.068 |
| SETDB1 | HERVE-int | +0.97 | 0.083 |
| SETDB1 | HERV9NC-int | +1.20 | 0.090 |

Right genes, right TE classes, right direction.

### The more informative statistic at this depth: directional consistency

With 0.2–0.34 M annotated reads per library, per-feature FDR is brutal. But if a knockdown
truly derepresses TEs, then *most* TE subfamilies should move up even where individually
non-significant. A sign test over all tested subfamilies (binomial, H₀: up and down equally
likely):

| Knockdown | TE subfamilies up / down | binomial p |
|---|---|---|
| SETDB1 | 188 / 165 | 0.12 |
| TRIM28 | **231 / 91** | **1.7 × 10⁻¹⁵** |
| DNMT1 | **315 / 188** | **8.2 × 10⁻⁹** |

**The control that makes this interpretable.** A global shift could be a normalisation
artefact. But size factors move genes and TEs together, so they cannot create a *difference
between the two sets*. Comparing the TE log2FC distribution against the protein-coding gene
distribution in the same contrast:

| Knockdown | TE median log2FC | gene median log2FC | Mann-Whitney (TE > gene) |
|---|---|---|---|
| SETDB1 | +0.060 | +0.018 | p = 0.16 — **no set-level shift** |
| TRIM28 | **+0.410** | −0.016 | p = 1.9 × 10⁻²² |
| DNMT1 | **+0.117** | −0.014 | p = 7.2 × 10⁻⁸ |

**Two conclusions that per-feature FDR alone would have missed:**

1. **DNMT1 loss does derepress TEs** — broadly, highly significantly — even though not one
   subfamily reaches FDR < 0.1. Reading only the padj column would have called this a null
   result. It is not.
2. **SETDB1 is specific, TRIM28 and DNMT1 are global.** SETDB1 shows no set-level shift but has
   the strongest individual HERV hits; it acts on particular retroviral families. TRIM28 and
   DNMT1 move the whole TE compartment. That distinction is biologically meaningful and is
   visible only because both statistics were computed.

**Caveat, stated plainly.** The sign test assumes subfamilies are independent. They are not —
related subfamilies share reads, and all share a library. The p-values are therefore
anticonservative and should be read as "this asymmetry is large", not as an exact probability.
The TE-versus-gene comparison is the more defensible of the two because it is internally
controlled.

### On TE age — tested, and it does not explain anything

A natural hypothesis is that only young, still-active subfamilies respond. Tested directly
against RepeatMasker divergence (`milliDiv`; low = young), restricted to baseMean ≥ 20:

| Contrast | Spearman ρ (milliDiv vs log2FC) | p |
|---|---|---|
| SETDB1 | +0.098 | 0.39 |
| TRIM28 | +0.056 | 0.61 |
| DNMT1 | +0.166 | 0.027 |

**No age effect genome-wide.** Within Alu the pattern does appear (AluY* median +0.914 vs
+0.555 for older Alu), but age and expression level are confounded there (ρ = +0.713), the
partial correlation drops to −0.35, and fold-change magnitude is inversely related to count
depth for protein-coding genes too. With n = 39 subfamilies it cannot be resolved, and it does
not currently improve the model. **Dropped.** It would only become useful as a prior in a
trained link-prediction model, which does not exist yet.

## 8. The EM step, since it is upstream of every number above

TEcount has to decide what to do with a read matching 300 AluY copies. Let *θ<sub>l</sub>* be
the expression of locus *l*, and *L(r)* the candidate loci for read *r*.

**E-step** — split each read across its candidates in proportion to current estimates:

$$
w_{rl} \;=\; \frac{\theta_l}{\sum_{l' \in L(r)} \theta_{l'}}
$$

**M-step** — re-estimate expression from those weights:

$$
\theta_l \;=\; \frac{\sum_r w_{rl}}{\sum_{l'} \sum_r w_{rl'}}
$$

Iterate to convergence. Loci with strong unique evidence claim a larger share of the ambiguous
reads. The output is fractional, which is why a count table can contain non-integers before
rounding.

**Compare to the alternative.** `featureCounts --countMultiMappingReads` (used in the TE_CHIP
paper pipeline) instead counts the read **fully at every location**, inflating high-copy
families. Neither is wrong; the numbers are **not interchangeable**, and they have not been
benchmarked against each other here.

## 9. Common misreadings

- **"padj = NaN means not significant."** It means not tested — filtered for low counts.
- **"Big log2FC = important."** Not without `baseMean`. Check the count level first.
- **"p = 0.04 means 96% chance it is real."** It does not. It is the probability of data this
  extreme *if nothing changed*.
- **"No individual hit = no effect."** Refuted above: DNMT1 has zero FDR-significant
  subfamilies and a p = 7 × 10⁻⁸ set-level shift.
- **"Aggregating to family level gives more power."** Here it gave less (see
  `aggregation_level_comparison.csv`). Why is not established.
- **"The fold changes are final."** They are from two chromosomes at 1.5 M reads, unshrunken,
  with n = 2–3. Directions are far more trustworthy than magnitudes.
