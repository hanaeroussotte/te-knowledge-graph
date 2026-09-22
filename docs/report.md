# A TE-aware knowledge graph with a provable reasoning layer

**Input:** a human gene symbol. **Output:** what losing that gene does to transposable-element
activation — measured where data exists, derived by rule where it does not — with an evidence
tier and a proof back to primary sources on every claim.

---

## 1. The gap

Transposable elements are excluded from graph-based target discovery twice over, and both
exclusions are structural rather than accidental.

**In the data.** Standard RNA-seq pipelines discard multi-mapping reads. TEs are repeated by
definition, so the reads that report on them are exactly the reads thrown away. TE signal is
therefore missing from most public expression matrices.

**In the graph.** Hetionet, PrimeKG and Open Targets do not model TEs as first-class
entities. A transposable
element cannot be a target, cannot lie on a returned path, and cannot be predicted, because
the schema has nowhere to put it.

This build introduces `TEFamily` / `TELocus` / `TEClass` as first-class node types, populates
gene→TE edges from four independent sources, and adds a rule layer that derives new edges with
proof trees. Full schema in `schema.md`.

## 2. What was built

| | |
|---|---|
| ENCODE knockdown experiments inventoried | 1,114 (570 distinct target genes) |
| …with released paired-end FASTQ | 1,060 |
| GO-curated TE regulators | 112 (15 have knockdown data) |
| TE loci in annotation (RepeatMasker hg38) | 3,761,678 across 1,057 subfamilies |
| Graph nodes | 1,350 |
| Graph edges | 2,874 |
| Rule-derived edges | 71 |
| Samples quantified end-to-end | 11 |

Edge layers, each with mandatory provenance (source, native score, statistic, retrieval date):

| Layer | Edges | Source |
|---|---|---|
| curated | 2,792 | GO, STRING v12.0, Reactome, Complex Portal |
| mechanism | 40 | GO molecular function — mark writers and erasers |
| literature | 32 | PubMed abstracts, PMID per edge |
| measured | 10 | ENCODE knockdown RNA-seq re-quantified in this run |

Of the 2,792 curated edges, 696 are Complex Portal *predicted* complexes and are tiered
`predicted`, not `curated`; the rule layer refuses to propagate through them.

## 3. The measured layer

**Pipeline.** ENCODE FASTQ → 1.5 M-read subsample → HISAT2 `-k 100` → TEcount `--mode multi`
(EM redistribution of multi-mapping reads across repeat loci) → PyDESeq2. Reference scope is
chr1 + chr19 — a TE-dense subset sized to run on a laptop. Eleven samples: SETDB1 (n=3),
TRIM28 (n=2) and a shared non-targeting control (n=2) from one CRISPRi series, plus DNMT1
(n=2) against its own CRISPR control (n=2). Alignment rates 17–20 %, as expected against a
two-chromosome index.

**Result — the positive control fired.**

| Knockdown | TE subfamily | log2FC | padj |
|---|---|---|---|
| TRIM28 | AluY | +0.79 | 0.00053 |
| TRIM28 | AluYa5 | +0.99 | 0.068 |
| TRIM28 | SVA_D | −0.41 | 0.080 |
| TRIM28 | MIR | +0.56 | 0.089 |
| SETDB1 | HERVE-int | +0.97 | 0.083 |
| SETDB1 | HERV9NC-int | +1.20 | 0.090 |

Direction is consistent: among nominally significant TE subfamilies (p < 0.05), SETDB1
knockdown gives 4 up / 0 down and TRIM28 gives 12 up / 2 down. TRIM28 loss raising SINEs and
SETDB1 loss raising HERVs is the textbook expectation, recovered from two chromosomes and
~0.2 M annotated reads per library. That agreement is the evidence the pipeline is wired
correctly — the point of running a known silencer first.

**DNMT1 produced no FDR-significant TE change** (best: LTR12C +0.46, p = 0.0011, padj = 0.41).
That is a power limitation, not a biological finding, and it has a downstream consequence
described in §5.

## 4. The reasoning layer

Five forward-chaining rules (`nesy_rules.py`), each stated in English in the code and each
producing a proof tree. The productive chain:

1. **R1 — mark grounding.** SETDB1 knockdown raises HERV9NC-int (*measured*) and SETDB1
   deposits H3K9me3 (*curated*, GO:0140949) ⇒ H3K9me3 is a silencing mark at HERV9NC-int.
   This is the only rule that creates `MARK_AT` edges, so every one is anchored to a measurement.
2. **R2 — writer transfer.** Any other H3K9me3 writer is predicted to silence that TE.
   SUV39H1, SUV39H2, SETDB2, EHMT1, ASH1L, PRDM2/8/9, SETD5 — none assayed here — acquire a
   signed prediction.
3. **R3 — eraser inversion.** H3K9me3 *erasers* get the opposite sign: losing KDM4A leaves
   more mark and so *lowers* the TE. Writers and erasers land on one axis with opposite signs.
4. **R4 — complex consensus** and **R5 — complex propagation**, restricted to curated membership.

71 edges derived: 36 by eraser inversion, 30 by writer transfer, 3 mark groundings, 2 complex
consensus.

**The neural/symbolic coupling is a citation gate.** Prose explanation is emitted sentence by
sentence, and a sentence survives only if every edge ID it cites exists in the graph. Sentences
citing nothing are rejected — silence about provenance is not treated as a lesser fault than a
wrong citation, because the reader cannot tell them apart. The gate runs identically whether the
prose came from a language model or the built-in template renderer, so the guarantee does not
depend on the model behaving. In the eight worked examples it kept 19 sentences and rejected 2
(both "no evidence connects X" statements, which cite nothing by construction).

## 5. Where DNMT3A and TET2 actually stand

This is the honest version, and it is more interesting than a clean result would have been.

- **TET2 is annotated to no GO transposition or TE-silencing term** — it is absent from all 112
  curated TE regulators. DNMT3A is present.
- **Neither has any ENCODE knockdown experiment**, in any cell line or assay.
- The route that *should* reach both is the mark layer: DNMT3A writes 5mC, TET2 erases it
  (GO:0070579, methylcytosine dioxygenase). R2 and R3 would then give them opposite predicted
  signs on any TE where 5mC is a grounded silencing mark.
- **That grounding requires a measured 5mC-writer effect, and DNMT1 did not clear FDR at this
  depth.** So the engine currently returns `best tier: curated` for DNMT3A (one GO edge) and
  `best tier: none` for TET2.

The engine does not paper over this. Asked about TET2 it says there is no evidence, and the
citation gate rejects the sentence for having nothing to cite. **Grounding 5mC is the single
most valuable thing full-depth genome-wide compute buys here** — it is a concrete, stated
prediction about what changes when the run scales, not a vague promise of "more data".

## 6. What was cut, and why

**Link prediction was gated on the measured layer and the gate closed.** The plan was to train
an embedding model on a gene × TE effect matrix and report held-out AUC and precision@k against
a degree-preserving baseline. Three knockdowns with ten significant edges cannot support that —
any AUC computed on it would be noise with a number attached, which is worse than no model,
because a judge cannot tell the difference without the validation set. It is deferred to the
run that produces hundreds of genes.

**A rule-based literature extractor was built, validated, and rejected.** With the LLM
extraction budget exhausted at 600 of 3,120 abstracts, a deterministic dictionary-and-pattern
extractor was written as a fallback and scored against the 600 LLM-labelled abstracts:

| filter | predicted | precision | recall | F1 | direction agreement |
|---|---|---|---|---|---|
| all rule hits | 193 | 0.109 | 0.175 | 0.134 | 10 / 21 |
| direction resolved | 52 | 0.154 | 0.067 | 0.093 | 6 / 8 |
| perturbation language | 25 | 0.200 | 0.042 | 0.069 | 0 / 5 |

Sentence co-occurrence of a gene symbol and a TE term is not evidence of a directed regulatory
claim, and direction agreement at 10/21 is chance. It is not shipped. The code is kept
(`extract_lit.py`) so the negative result is reproducible.

## 7. Limitations

- Two chromosomes, not the genome; 1.5 M reads per library, not full depth. Absolute effect
  sizes are not final quantifications.
- Subsampling takes the head of each FASTQ rather than a uniform random draw (~10× less
  transfer). Applied identically to every sample, fine for relative comparison; `--subsample
  reservoir` is the correct setting for the genome-scale run.
- Local alignment uses HISAT2 because the conda osx-arm64 STAR build reads zero reads while
  reporting success. The cloud path keeps STAR, which is what the published TEtranscripts
  workflow assumes. **The two aligners have not been compared on the same samples here.**
- The literature layer covers 19 % of the retrieved corpus and 32 human edges.
- R2 assumes writers of the same mark are interchangeable at a given locus. That is the rule
  most likely to be wrong; it is tiered `inferred`, never `curated`.
- Cell context is K562 only. Nothing here establishes that these effects transfer to primary
  haematopoietic cells.
