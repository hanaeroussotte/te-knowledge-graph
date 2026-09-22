# Evidence-Traceable Neurosymbolic Reasoning for Transposable-Element Regulation

*What does this gene do to transposable-element activation — and how would you know?*

A transposable-element-aware biological knowledge graph with a rule-based reasoning layer,
where every claim carries an evidence tier and a proof back to primary sources.

```
$ python src/te_reason.py SUV39H1 --proofs

=== SUV39H1  [best tier: inferred]  measured=0 curated=0 literature=0 inferred=3
Losing SUV39H1 is predicted to raise HERV9NC-int, derived by R2_WRITER_TRANSFER ...

  SUV39H1 -SILENCES-> HERV9NC-int          [inferred via R2_WRITER_TRANSFER]
    H3K9me3 -MARK_AT-> HERV9NC-int         [inferred via R1_MARK_GROUNDING]
      SETDB1 -SILENCES-> HERV9NC-int       [measured: ENCODE ENCSR819PCU]
      SETDB1 -DEPOSITS_MARK-> H3K9me3      [curated: GO:0140949]
    SUV39H1 -DEPOSITS_MARK-> H3K9me3       [curated: GO:0140949]
```

Nobody measured SUV39H1. The prediction is signed, specific, and every step is a database
record or a measurement you can open.

## Why this exists

Transposable elements are excluded from graph-based target discovery twice over, and both
exclusions are structural rather than accidental.

**From the data.** Standard RNA-seq pipelines discard multi-mapping reads. TEs are repeated by
definition, so the reads that report on them are exactly the reads thrown away. TE signal is
absent from most public expression matrices.

**From the graph.** Hetionet, PrimeKG and Open Targets do not model TEs as first-class
entities. A TE cannot be a
target, cannot lie on a returned path, and cannot be predicted — the schema has nowhere to put
it. The evidence exists in the literature; the data model does not admit it.

This repository fixes both: a pipeline that keeps multi-mapping reads and redistributes them
by EM, and a graph with `TEFamily` / `TELocus` / `TEClass` as first-class node types.

## What is here

| | |
|---|---|
| `src/te_pipeline.py` | FASTQ → aligner (multi-mapping kept) → TEcount → count matrix |
| `src/build_te_annotation.py` | RepeatMasker → TE GTF + subfamily vocabulary |
| `src/build_graph.py` | curated + chromatin-mark edge layers from GO, STRING, Reactome, Complex Portal |
| `src/run_de.py` | PyDESeq2 → per-feature **and** set-level measured edges |
| `src/nesy_rules.py` | 5 forward-chaining rules, proof trees, path-admissibility grammar |
| `src/te_reason.py` | `explain(gene)` + the citation gate |
| `src/annotate_tractability.py` | Open Targets + ChEMBL → five druggability classes |
| `src/score_signatures.py` | interferon / senescence set-level tests, with a coverage guard |
| `src/build_panel_reference.py` | splices signature gene loci into the reference as extra contigs so a gene set becomes measurable without a genome-wide index |
| `src/extract_lit.py` | rule-based literature extractor — **kept but not used**, see below |

### What this is, stated precisely

> **An evidence-traceable perturbational reasoning system for transposable-element
> regulation.** It re-analyses perturbation experiments for effects on the repetitive
> genome, converts those measurements into signed and provenance-tracked biological
> relationships, connects them to known mechanisms, and generates testable hypotheses whose
> evidence paths can be inspected and falsified.

It is **not** a new TE quantification method (that is
[TEtranscripts](https://doi.org/10.1093/bioinformatics/btv422), which we run), not the first
systematic search for TE regulators (genome-wide screens date to 2003), and not a new
statistical test (competitive gene-set testing). Every novelty claim was put through a
deliberate attempt to kill it — see `PRIOR_ART.md` and the claim registry `CLAIMS.md`.

### Documentation

| Read this | For |
|---|---|
| `COMPLETE_WALKTHROUGH.md` | the whole project from zero — biology, architecture, every script, the mathematics, how to read every output |
| `WHY_THIS_IS_DIFFERENT.md` | what already existed and which part is actually new |
| `PRIOR_ART.md` / `CLAIMS.md` | the evidence behind every claim, and its status |
| `EPISTEMOLOGY.md` | what the system is entitled to conclude, and the inference ladder |
| `DEMO_SCRIPT.md` | the seven-question demo |
| **`TOMORROW.md`** | **start here on the day — hour by hour, for a first-timer** |
| `KNOWLEDGE_GRAPHS_101.md` | what a knowledge graph is, technically, from zero |
| `PRESENTATION_GUIDE.md` | every slide explained, with the number to defend |
| `DEMO_5MIN.md` | **the timed 5-minute pitch** |
| `PREREGISTRATION.md` | the one prospective prediction, committed before the data was opened |
| `ROBUSTNESS.md` | leave-one-anchor-out: what the reasoning layer actually rests on |
| `EXECUTION_BRIEF.md` | plan, status and verification commands |
| `PRIMER.md` / `MANUAL.md` | shorter explainer / operator's guide |
| `CRITIQUE.md` | read before believing any of it |
| `PANEL_REFERENCE.md` | how the interferon coverage gap was closed |
| `TE_RESOLUTION.md` / `QUANTIFIER_ROBUSTNESS.md` | where the resolution should go; the robustness test, specified and **not run** |
| `COMPUTE.md` / `modal_setup.md` | what belongs in the cloud and what does not |

Run `make test` before any push: it audits for retracted claims and regression-tests the
proof trees.

## Quickstart

```bash
conda env create -f environment.yml && conda activate te-pipeline
pip install -r requirements.txt

make refs          # download RepeatMasker, GENCODE, chr1+chr19 (~290 MB)
make annotation    # build the TE GTF and subfamily table
make graph         # curated + mechanism edge layers (network, ~10 min)
make index         # STAR/HISAT2 index over the chromosome subset (~4 min)
make smoke         # quantify 2 samples end to end (~15 min)
make de            # differential expression -> measured edges
make query GENE=TET2
```

`make` with no target lists everything.

## Evidence tiers

Every edge carries `evidence_tier`, describing **where the claim came from** — not how
confident anyone feels. A high-scoring prediction is still a prediction.

| tier | meaning |
|---|---|
| `curated` | a human curator asserted it in a reference database |
| `measured` | computed here from primary data, with effect size and FDR |
| `literature` | extracted from abstracts, PMID attached |
| `inferred` | derived by a rule, with a proof tree |
| `predicted` | proposed with no direct evidence |

**A path takes the tier of its weakest edge**, enforced in code. One inferred hop cannot make
a chain look established.

## Two design decisions worth knowing before you use it

**Compute two statistics, not one.** Per-feature FDR answers "which subfamilies moved". The
set-level test asks whether the TE compartment shifted relative to the protein-coding
compartment in the same contrast — which is normalisation-invariant, because size factors
scale both sets together and cannot manufacture a difference between them. In the reference
run, DNMT1 knockdown had **zero** subfamilies at FDR < 0.1 and a set-level shift at
**p = 1.4 × 10⁻⁷**. Reading only the padj column would have called it a null result.

**The neurosymbolic coupling is a citation gate, not a prompt.** Explanations are split into
sentences; a sentence survives only if every edge ID it cites exists in the graph. Sentences
citing nothing are rejected too. The gate is a string comparison and behaves identically on
model-written and template-written text, so the guarantee does not depend on the model
behaving well.

## Reported honestly

Two components were built, validated, and **not shipped**:

- **Rule-based literature extraction** — precision 0.109, recall 0.175, direction agreement
  10/21 (chance) against an LLM-labelled reference. Code kept in `src/extract_lit.py` so the
  negative result is reproducible; not wired into the graph.
- **Link prediction** — gated at design time on having a gene × TE matrix large enough to hold
  out a validation set. Three knockdowns is not. An unvalidated AUC is worse than no model.

The interferon analysis in `results/` is also a negative: at a chr1+chr19 reference only ~17%
of the type-I IFN gene set is present and every canonical sensor except IRF3 is off-scope, so
the result describes the chromosome selection rather than the biology. `score_signatures.py`
refuses to interpret a signature below `--min-coverage` for that reason.

`docs/CRITIQUE.md` has the full limitation list and five concrete falsifiers.
`docs/LANDSCAPE.md` places the project against the existing TE atlases, the 16 benchmarked
quantifiers, the perturbation-prediction models and the companies in this space, with a
verification ledger for every claim in it. `docs/JURY_QUESTIONS.md` answers 41 likely
questions.

## A note on the shipped graph vs the figures

`data/graph/` was regenerated by `src/build_graph.py` and is **larger** than the graph behind
the figures in `docs/` and `figures/`: 219 seed genes and 9,263 curated edges, versus 112 and
2,792. The original run went through an API wrapper that silently capped gene lookups at 10
results per GO term. The scripts here query mygene.info directly with `size=1000` and get the
full set. The measured, mechanism and rule layers are unaffected; re-run `make query` to
regenerate outputs against the larger graph.

## Data sources

RepeatMasker (UCSC), GENCODE v44, ENCODE knockdown RNA-seq, Gene Ontology / QuickGO,
STRING v12.0, Reactome, Complex Portal, PubMed, Open Targets Platform, ChEMBL.
All public; no credentials required.

## Status and scope

A working demonstration, not a validated atlas. The schema, pipeline, rule layer and citation
gate all run on real data; **three genes have been measured, not 570**. The "any gene" claim
is architectural. What stands between this and an actual atlas is compute, not design —
`docs/modal_setup.md` and `docs/ADAPTING_TO_NEW_DATA.md` cover scaling up.

## Licence

**MIT** — see [`LICENSE`](LICENSE). Anyone may use, modify and redistribute the code,
including commercially, provided the copyright notice is kept. No warranty is given.

The licence covers the *code*. The *data* in `data/` and `results/` derives from sources with
their own terms (ENCODE, Open Targets and ChEMBL are permissive; check Complex Portal and
COSMIC-derived material if you add any). Nothing here relicenses those.
