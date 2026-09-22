# The TE-compartment statistic, attacked properly

**Run it:** `python src/compartment_robustness.py` → `results/compartment_robustness.csv`

**Summary: the Mann–Whitney p-values this project has been quoting are retracted as
evidence.** They are anti-conservative by a factor between ~4 and ~155, depending on the
contrast. The DNMT1 effect — the anchor the whole 5mC arm depends on — **survives** in a
weaker but better-supported form. The TRIM28 *compartment* claim does not, though its
per-feature hits are unaffected.

---

## 1. Why the original p-value was wrong

The primary readout is

```
Δ_TE = median(log₂FC over TE subfamilies) − median(log₂FC over protein-coding genes)
```

within one contrast. The **effect size** argument is sound and unchanged: size factors are
per-sample multiplicative, so a normalisation error shifts both sets by the same additive
amount on the log scale and cancels in the difference.

The **p-value** was computed with Mann–Whitney over ~350–500 TE features. That treats the
features as independent observations. They are not — TE subfamilies covary through shared
regulatory machinery, shared sequence ancestry, and shared mapping ambiguity. Competitive
gene-set tests are anti-conservative under exactly this condition, which is the reason
CAMERA exists (Wu & Smyth, *NAR* 2012,
[10.1093/nar/gks461](https://doi.org/10.1093/nar/gks461)).

An external reviewer identified this as the project's largest statistical vulnerability.
They were right.

## 2. How large is the inflation? Measured, not assumed

Mean pairwise correlation among TE features, estimated from residuals after removing group
means (CAMERA's estimator), with the variance-inflation factor
`VIF = 1 + (m−1)·ρ̄` and effective feature count `m/VIF`:

| Contrast | ρ̄ | VIF | effective independent TE features | Mann–Whitney p | correlation-aware p |
|---|---|---|---|---|---|
| **DNMT1** | **0.006** | **4.1** | **122 of 503** | 1.41 × 10⁻⁷ | **0.045** |
| SETDB1 | 0.399 | 141 | 2.5 of 353 | 0.411 | 0.886 |
| TRIM28 | 0.479 | 155 | 2.1 of 322 | 2.31 × 10⁻²¹ | **0.441** |

Read the third column. In the two CRISPRi contrasts, 322–353 TE features carry roughly
**two features' worth of independent information**. A p-value built on 322 independent
observations is meaningless there.

**Why DNMT1 is different, and it matters:** its residual correlation is ~80× lower. DNMT1 is
the CRISPR batch; SETDB1 and TRIM28 share the CRISPRi batch and the same non-targeting
control libraries. A large shared latent factor in those libraries is consistent with the
control-arm heterogeneity already documented (the two control arms split on ISG score,
+0.71 versus −0.84). The correlation is picking up a library effect, not only TE biology.

**Caveat on ρ̄ itself:** residual dimension is 2–3. These estimates are noisy. The direction
of the bias is not in doubt — positive correlation always inflates significance — but the
exact VIF should be read as an order of magnitude.

## 3. The test whose unit of inference is the sample

Permuting knockdown/control labels *within* a contrast (never across batches — those samples
are not exchangeable):

| Contrast | admissible labellings | attainable p floor | observed Δ vs permutation null |
|---|---|---|---|
| DNMT1 | 3 | **0.333** | observed **+0.130**, null max \|Δ\| **0.035** — observed is 3.7× the largest null |
| TRIM28 | 3 | 0.333 | observed +0.421, null max \|Δ\| **0.679 — a permuted labelling beat the real one** |
| SETDB1 | 10 | 0.100 | observed +0.023, null max \|Δ\| 0.785 |

**The binding constraint is the design, not the analysis.** With 2 replicates per arm there
are 3 admissible labellings, so **no p below 0.333 is attainable regardless of effect
size**. Anyone quoting a small sample-level p-value from an n=2 design is quoting an
artefact. That is worth saying plainly.

Within that limit, DNMT1 is the most extreme of its labellings by a wide margin, and TRIM28
is not.

## 4. Leave-one-library-out

| Contrast | Δ range | sign preserved | max shift |
|---|---|---|---|
| **DNMT1** | **+0.100 .. +0.187** | **yes, 4/4** | 0.058 |
| TRIM28 | −0.025 .. +1.116 | **no** | 0.695 |
| SETDB1 | −0.400 .. +0.695 | no | 0.673 |

**Caveat that cuts both ways:** dropping one library from a 2-versus-2 design leaves 1
versus 2, where dispersion is barely estimable. So instability here is partly a property of
the leave-one-out procedure, not only of the data. That makes DNMT1's stability *more*
impressive — it holds under the same handicap that destabilises the other two.

## 5. Feature-set sensitivity

Δ_TE recomputed under alternative definitions of "the TE set":

| Variant | DNMT1 | TRIM28 | SETDB1 |
|---|---|---|---|
| all TE features | +0.130 | +0.421 | +0.023 |
| LINE only | +0.193 | +0.448 | +0.018 |
| SINE only | +0.102 | +0.626 | +0.184 |
| LTR only | +0.109 | +0.125 | **−0.127** |
| DNA only | +0.104 | +0.436 | +0.237 |
| expressed (mean norm count ≥ 10) | +0.129 | +0.436 | +0.075 |
| trimmed (5% most extreme dropped) | +0.130 | +0.421 | +0.023 |

DNMT1 is positive in **all six** variants, in a tight band (+0.10 to +0.19), with 63–74% of
features moving up. TRIM28 is positive in all six but with a 5-fold spread. SETDB1 changes
sign on LTRs.

## 6. What each claim is now

### DNMT1 — survives, restated

> **DNMT1 knockdown produces a coherent positive shift of the TE compartment relative to
> protein-coding genes: Δ = +0.13 log₂, 63% of 503 TE features moving up, the same sign in
> all six feature-set variants, stable under leave-one-library-out (+0.10 to +0.19, sign
> preserved in all four drops), the most extreme of the three admissible sample labellings
> by a factor of 3.7, and a correlation-aware p of 0.045 after a measured variance inflation
> of 4.1×. No individual subfamily reaches FDR 0.1.**

That is a weaker claim than "p = 1.6 × 10⁻⁸" and a much better supported one. **The 5mC
anchor holds**, so R1 → R2 → R3 and the DNMT3A/TET2 derivation stand — on this evidence,
with this uncertainty.

### TRIM28 — compartment claim downgraded

> **TRIM28 knockdown shows a large and directionally very consistent TE-compartment effect
> (Δ = +0.42, 73% of features up, same sign in all six variants), but the sample-level
> evidence does not support it: a permuted labelling produced a larger effect than the real
> one, the sign does not survive leave-one-library-out, and the correlation-aware p is 0.44.
> Treated as a strong effect size with weak inferential support, pending replicates.**

**TRIM28's per-feature results are unaffected** — AluY at padj 0.0005 comes from the
per-feature DESeq2 Wald test with BH correction, which is a different statistic and does not
depend on the compartment comparison. That result stands.

And a convenient consequence of the anchor-dependence analysis: TRIM28 contributes **zero**
derived edges, so downgrading its compartment edge changes no inference.

### SETDB1 — unchanged

Already reported as having no compartment shift (p = 0.41). The corrected analysis agrees
more strongly (p = 0.89) and adds that LTRs move the other way. Consistent with a targeted
ERV silencer rather than a global one — stated as consistency, not demonstration.

## 7. What changed in the repository

- `results/edges_measured.csv` — the two `TE:global` set-level edges now carry the full
  corrected evidence in their `statistic` field, naming the retracted Mann–Whitney value
  explicitly rather than deleting it.
- `CLAIMS.md` — B1 and B2 restated; a new approved-wording row.
- The Mann–Whitney p-value is no longer quoted as primary evidence anywhere.

## 8. What would actually settle it

**More replicates.** Not a better test. With 2 per arm the permutation floor is 0.333 and no
statistical method recovers information the design does not contain. ENCODE has more
libraries for some targets; a genome-wide run at 3–4 replicates per arm would put the
sample-level test within reach of significance for the first time.

Second: the quantifier comparison (`QUANTIFIER_ROBUSTNESS.md`), still pre-registered and
unrun — ρ̄ of 0.4–0.5 could partly reflect shared multi-mapping, which a different
quantifier would redistribute differently.
