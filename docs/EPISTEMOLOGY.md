# What this system is entitled to conclude

The rules in `nesy_rules.py` are **mechanism-guided candidate-generation rules**. They
produce *mechanistic hypotheses*, not causal deductions. This document says why that word
choice is load-bearing, and where the argument actually breaks.

## 1. Vocabulary

| Do not write | Write |
|---|---|
| "the engine derives that TET2 derepresses TEs" | "the engine **predicts** … " / "generates the hypothesis that …" |
| "causal pathway" | "mechanistic hypothesis" or "candidate path" |
| "R3 proves" | "R3 fires, generating a testable prediction" |
| "shows that DNMT3A silences TEs" | "places DNMT3A on the 5mC axis with a predicted sign" |
| "the measured edge establishes" | "the measured edge supports, in this cell line and contrast" |

Printing the proof tree is what makes the weaker word safe: a reader can see every premise
and attack whichever one they like. A system that says "predicted" and shows its work is
more useful than one that says "causal" and does not.

## 2. The ladder

The project's headline biology is a chain, and **every rung is a separate empirical
claim.** Treating the chain as one step is the single most common error in this field,
including in our own early drafts.

```
  1. a silencing gene is lost                        [measured — CRISPRi/CRISPR knockdown]
        ↓  does NOT automatically give
  2. TE RNA increases                                [measured here — TEcount + DESeq2]
        ↓  does NOT automatically give
  3. double-stranded RNA accumulates                 [NOT measured — needs dsRNA IP / J2]
        ↓  does NOT automatically give
  4. reverse-transcribed cytoplasmic cDNA appears    [NOT measured — needs cytoplasmic DNA assay]
        ↓  does NOT automatically give
  5. MDA5 / cGAS are activated                       [NOT measurable in K562 — sensors absent]
        ↓  does NOT automatically give
  6. type I interferon is induced                    [measured here — null, and uninterpretable
                                                      as biology because rung 5 fails]
        ↓  does NOT automatically give
  7. an inflammatory disease phenotype               [out of scope entirely]
```

Where this project actually stands: **rungs 1, 2 and 6 are measured. Rungs 3, 4 and 5 are
not. Rung 7 is out of scope.** An increase at rung 2 with a null at rung 6 tells you
nothing about causation until you know whether rungs 3–5 are even possible in the system,
which is exactly why the sensor-expression table exists.

Two consequences we hold ourselves to:

- No edge in the graph may skip rungs. `R6_TE_MEDIATED_INFLAMMATION` requires rung 2 and
  rung 6 to be measured **in the same contrast**, and even then produces
  `DRIVES_VIA_TE` at tier `inferred`, never `measured`.
- A null at rung 6 is reported together with the rung-5 evidence. "No interferon response"
  and "no interferon response because the sensor is not expressed" are different claims,
  and only the second one is ours.

## 3. The chain is not acyclic

Our figures draw cGAS **downstream** of TE derepression. That is now known to be
incomplete: cGAS-deficient mice show LINE-1 derepression and inflammatory ageing, implying
cGAS also acts **upstream**, in maintaining H3K9me3 heterochromatin
([10.1038/s43587-026-01206-y](https://doi.org/10.1038/s43587-026-01206-y), *Nat Aging* 2026).

So the real topology contains feedback:

```
        ┌──────────────────────────────────────────┐
        │                                          ▼
   chromatin state  ──►  TE expression  ──►  sensing (cGAS)
        ▲                                          │
        └──────────────────────────────────────────┘
              cGAS maintains H3K9me3 (Nat Aging 2026)
```

This is an **open structural issue**, not something we have handled. The path grammar in
`nesy_rules.py` walks directed paths and would happily report a one-way story. Recorded in
`CRITIQUE.md`; the honest position for now is that any cGAS-containing path should be
presented as one direction of a loop, not as a mechanism.

## 4. What each tier entitles you to say

| Tier | Entitles you to say | Does not entitle you to say |
|---|---|---|
| `measured` | "in K562, CRISPRi against TRIM28, the TE compartment rose" | "TRIM28 silences TEs" (unqualified, in any cell) |
| `curated` | "GO annotates DNMT1 as a cytosine-5 methyltransferase" | "therefore DNMT1 silences TEs" |
| `mechanism` | "SETDB1 writes H3K9me3" | anything about a specific TE family |
| `literature` | "an abstract asserts this" | "this is established" |
| `inferred` | "the system predicts X, by rule R, from premises P" | "X is true" |

A multi-step path takes the **weakest** tier on it, not an average. Confidence is limited
by the worst link.

## 5. Context is part of the claim

`SETDB1 —SILENCES→ HERVE-int` read without qualifiers is a universal statement, and it is
not what we measured. What we measured was one cell line, one perturbation modality, one
time point, one assay, one resolution. The schema therefore carries those as columns rather
than leaving them in a provenance string — see `schema.md` §context. The mature form of the
edge is:

```
SETDB1 loss —INCREASES_EXPRESSION_OF→ HERVE-int
    context_cell_type   = K562
    perturbation        = CRISPRi
    assay               = RNA-seq (polyA, paired-end)
    te_resolution       = subfamily
    quantifier          = TEcount (TEtranscripts) --mode multi
    effect_size         = +0.97 log2FC
    statistic           = padj 0.083
    species             = Homo sapiens
```

Anyone reusing an edge without its context is making a claim we did not make.

## 6. The refusals, as a list

These are not caveats. They are places where the software declines to produce output, and
they cost us results:

1. **Coverage guard** — `score_signatures.py` refuses to interpret a gene set whose
   reference coverage is below threshold. It refused the interferon arm at 0.168, and after
   the panel fix it still refuses the inflammatory-response set at 0.535.
2. **Citation gate** — `te_reason.py` discards any sentence without a resolvable edge id
   rather than printing it unsourced.
3. **Link prediction** — not built, because three knockdowns cannot support a held-out
   validation set, and an unvalidated AUC would have been the most impressive and least
   meaningful number in the project.
4. **Rule-based literature extractor** — built, measured at precision 0.109 and direction
   agreement no better than chance, and not wired in.
5. **The age explanation** — asserted, then tested genome-wide, then withdrawn. The result
   survived; the explanation did not.
6. **The viral-mimicry question** — answered "this dataset cannot test it", with the
   sensor-expression evidence and a named alternative experiment.

## 7. The standard we are trying to meet

> Determine what evidence exists, distinguish measurement from inference, identify what is
> missing, run the computation that would settle it, inspect the result, and return a claim
> whose derivation someone else can audit — including, when it is the right answer, "not
> yet knowable, and here is the experiment."

A hypothesis generator that cannot refuse is a random-sentence generator with good grammar.
The refusals are the product.
