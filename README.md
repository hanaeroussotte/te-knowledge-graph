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

## Start here — five minutes

| | |
|---|---|
| **Open `demo/query.html`** | Click a gene. Every answer shows its evidence tier, the subgraph it was derived from, and what to measure next. Click **GAPDH** — the system returns nothing, deliberately. No server, no build step. |
| **Open `demo/pitch.html`** | The 11-slide deck: the problems, what already exists, the residual gap, the results, the limitations. Arrow keys; `s` toggles speaker notes. |
| **Run one command** | `python src/te_reason.py TET2 --proofs` — a gene with no transposon annotation and no knockdown, answered anyway, with the derivation printed. |
| **Check we are not lying** | `make gate` runs the claim audit, resolves all 46 DOIs and 44 PMIDs, and re-runs the regression pins. |

Reading order for the documents is in `docs/COMPLETE_WALKTHROUGH.md`; the short version is
`docs/WHERE_WE_ARE.md`, and the limitations are `docs/CRITIQUE.md`.

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

This repository addresses both: a pipeline that keeps multi-mapping reads and redistributes
them by EM, and a graph in which transposable elements are first-class entities — `TEClass`,
`TEFamily` and `TESubfamily` are node types a predicate can point at.

**`TELocus` and `TETranscript` are roadmap, not built.** The field is moving to locus
resolution and this schema does not reach it yet; `docs/TE_RESOLUTION.md` §8 says so in
detail, and the working resolution here is the subfamily.

## What is here

| | |
|---|---|
| `src/te_pipeline.py` | FASTQ → aligner (multi-mapping kept) → TEcount → count matrix |
| `src/build_te_annotation.py` | RepeatMasker → TE GTF + subfamily vocabulary |
| `src/build_graph.py` | curated + chromatin-mark edge layers from GO, STRING, Reactome, Complex Portal |
| `src/run_de.py` | PyDESeq2 → per-feature **and** set-level measured edges |
| `src/nesy_rules.py` | 6 forward-chaining rules, proof trees, path-admissibility grammar |
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

make validate      # 42 structural metrics on the graph -> results/graph_validation.csv
make demo          # rebuild demo/query.html from live engine output
make gate          # claim audit + DOI/PMID resolution + regression pins
make ship          # gate && stage  (the && is the point: see docs/COMPLETE_WALKTHROUGH.md 21)
```

`make` with no target lists everything. Nothing below `make graph` requires the pipeline to
have been run — the shipped `data/` and `results/` tables are enough to query, validate and
rebuild the demo.

### What is in `demo/`

| file | |
|---|---|
| `query.html` | the product: 14 genes, all five evidence tiers, four of them refusals. Self-contained; a viewer over real engine output, not a server |
| `pitch.html` | the 11-slide deck, figures embedded, works offline |
| `TE_Knowledge_Graph.pptx` | the slides as presented |
| `demo.html` | the earlier query walkthrough, kept for reference |

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

**Four things were built, measured, and not shipped.**

- **Rule-based literature extraction** — precision 0.109, direction agreement 10/21 (chance)
  against an LLM-labelled reference. Code kept in `src/extract_lit.py` so the negative result
  is reproducible; not wired into the graph.
- **Link prediction** — gated at design time on having a gene × TE matrix large enough to hold
  out a validation set. Three knockdowns is not. An unvalidated AUC is worse than no model.
- **An interferon conclusion**, first refused: at a chr1+chr19 reference only **16.8%** of the
  type-I IFN gene set was present, below the coverage guard in `score_signatures.py`. We then
  built a targeted 62 Mb panel reference, took coverage to **76.8%**, and re-ran — and the
  answer was *still* a null. It now carries a mechanism: in K562 the cytosolic sensors are
  barely expressed (CGAS 0.21, ZBP1 0.26, TLR3 0.00 CPM) while the transducers run at
  270–800. So the claim is not "TE derepression does not cause interferon" — it is that **this
  dataset cannot decisively test it**, and a sensing-competent cell type is required.
- **Our own set-level p-values, retracted.** The Mann–Whitney test treated ~350 TE subfamilies
  as independent observations. Measured mean pairwise correlation runs 0.006–0.48, i.e.
  **variance inflation 4× to 155×**. DNMT1 survives restated — Δ = +0.13, same sign in 6/6
  feature-set variants, stable to dropping any library, **correlation-aware p = 0.045**.
  TRIM28's whole-compartment claim does not and is now an effect size only.
  See `docs/COMPARTMENT_STATISTICS.md`.

**And one control we failed.** `SETDB1`'s own mRNA is not significantly reduced in its own
knockdown (−0.35 log₂, 78% remaining, padj 0.77), while TRIM28 and DNMT1 are both confirmed at
padj < 1e-11 in the same data. SETDB1 grounds 3 of the 4 `MARK_AT` edges, so **78 of 83 derived
edges rest on the mark supported by the least-confirmed perturbation** — see
`results/experiment_priority.csv` and `figures/fig_ev5_priority.png`. Read as *not confirmed*,
not *failed*: CRISPRi acts on transcription, we read a shallow steady-state snapshot, and the
knockdown did produce the two ERV results. Full-depth genome-wide would settle it.

`best_tier: none` is a supported output, not an error path. Four of the fourteen genes in the
demo return it.

`docs/CRITIQUE.md` has the full limitation list and five concrete falsifiers.
`docs/LANDSCAPE.md` places the project against the existing TE atlases, the 16 benchmarked
quantifiers, the perturbation-prediction models and the companies in this space, with a
verification ledger for every claim in it — including one claim we recorded as unfindable that
turned out to exist. `docs/JURY_QUESTIONS.md` answers 41 likely questions.

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
