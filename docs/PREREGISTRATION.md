# Pre-registration: one prospective, independently testable prediction

> **Written before the data was touched.** Commit this file, then run the experiment. The
> point of pre-registering is that the interpretation cannot be renegotiated after the
> numbers appear.

## 1. The prediction

The engine predicts, from a rule stated in advance:

```
DNMT3B -SILENCES-> TE:global          [inferred, R2_WRITER_TRANSFER]
  edge_id   e5ef09fb31a4343 (premises e62dbe0821f074b, e5ef09fb31a4343)
  meaning   losing DNMT3B RAISES the TE compartment
  grounded  context_cell_type=K562, perturbation_modality=CRISPR
  flag      context_generalization_required = yes
```

The proof:

```
DNMT3B -SILENCES-> TE:global                       [inferred, R2]
├── DNMT3B writes 5mC                              [curated: GO:0003886]
└── 5mC represses TEs                              [inferred, R1]
    ├── DNMT1 writes 5mC                           [curated: GO:0003886]
    └── DNMT1 loss raised the TE compartment       [MEASURED, K562, p = 1.6e-08]
```

**Why this is the right prediction to test.** R2_WRITER_TRANSFER is the rule most likely
to be wrong in the whole engine — it transfers a measured effect from one writer of a mark
to another on the strength of the shared mark alone, and `DNMT1` is the *maintenance*
methyltransferase while `DNMT3B` is a *de novo* one. If writer-transfer is unsound, this is
where it breaks.

## 2. The test

Data that exists and **has never been processed in this project**:

| | |
|---|---|
| Knockdown | ENCODE **ENCSR290GUQ** — DNMT3B, CRISPR, HepG2, paired-end, 258.5 M reads |
| Control | ENCODE **ENCSR306EWE** — CRISPR control, HepG2, paired-end |
| Manifest | `data/manifests/manifest_prospective.csv` (4 libraries, 2 per arm) |
| Pipeline | unchanged: HISAT2 `-k 100` → `TEcount --mode multi` → PyDESeq2 → set-level test |

**Primary endpoint:** the sign of the set-level statistic — median log₂FC over TE
subfamilies minus median log₂FC over protein-coding genes, in the DNMT3B-vs-control
contrast, with a Mann–Whitney test. This is the normalisation-invariant readout
(`COMPLETE_WALKTHROUGH.md` §8.7); it is the primary endpoint precisely because per-feature
FDR at this depth already failed to detect the real DNMT1 effect.

**Secondary:** per-subfamily results at FDR < 0.1, reported but not the test.

## 3. A confound that must be stated, not discovered later

**The prediction is grounded in K562. The only available test data is HepG2.** So this
tests two things at once and cannot separate them:

1. R2 — does a measured effect transfer between two writers of the same mark?
2. Cell-type generalisation — does the 5mC→TE relationship hold outside K562?

A failure does not tell you which one broke. A clean test of R2 alone would need a DNMT3B
knockdown in K562, and **ENCODE does not contain one**. This is exactly the situation the
`context_generalization_required` flag exists to flag, and it is flagged.

The engine is therefore making a *two-step* inference here, and the pre-registered
interpretation below treats it as such.

## 4. Pre-registered interpretation

Decided now, before the data is seen.

| Outcome | Interpretation |
|---|---|
| TE compartment shifts **up**, p < 0.01 | R2 survives a cross-cell-type test — a stronger result than a within-K562 confirmation would have been. Convert the DNMT3B edge from `inferred` to `measured` |
| TE compartment shifts up, 0.01 ≤ p < 0.1 | Direction consistent, underpowered at this depth. Report as weak support; re-test at full depth before claiming it |
| **No shift** (p ≥ 0.1, delta within ±0.05) | R2 or cell-type transfer fails here. **Do not quietly drop the prediction** — record it in `CLAIMS.md` as `REFUTED_IN_THIS_CONTEXT` and add the negative edge to the graph |
| TE compartment shifts **down** | R2's sign logic is wrong, not merely weak. This would be the most informative outcome: it would mean writer-transfer inverts across DNMT family members, and R2 should be restricted to within-subfamily transfer or removed |
| Knockdown efficiency poor (DNMT3B not reduced in the KD arm) | Test is void, not negative. Check `DNMT3B` counts in the contrast **first**, before reading any TE result |

**The last row is a gate, not a caveat.** The first thing to look at is whether DNMT3B
itself went down. A CRISPR knockdown that did not work produces a perfect null and would
otherwise look like a refutation.

## 5. What this does not test

- Nothing about inflammation. HepG2 sensor expression is unknown here and the
  `score_signatures.py` coverage guard applies as usual.
- Nothing about DNMT3A, which is the gene the user's hypothesis concerns. DNMT3A has no
  ENCODE knockdown at all; DNMT3B is the nearest testable member of the same family, and
  a result here constrains R2 rather than confirming the DNMT3A prediction.
- Nothing about locus-level TE behaviour — this is subfamily resolution
  (`TE_RESOLUTION.md`).

## 6. How to run it

```bash
python src/modal_app.py --dry-run --manifest data/manifests/manifest_prospective.csv
modal run src/modal_app.py --manifest data/manifests/manifest_prospective.csv --reads 0
python src/te_pipeline.py merge --outdir results_prospective
python src/run_de.py --counts results_prospective/counts_matrix.tsv \
    --manifest data/manifests/manifest_prospective.csv --outdir results_prospective
```

Then read `results_prospective/setlevel_tests.csv`, apply §4, and update `CLAIMS.md`.

## 7. Status

`NOT_RUN` as of commit `d60ac4b`. The manifest is built and validated; the prediction,
the endpoint and the interpretation are fixed above.
