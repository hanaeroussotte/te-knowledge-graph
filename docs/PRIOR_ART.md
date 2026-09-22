# Prior art

**Purpose.** This was not a literature review. It was an attempt to kill every novelty
claim the project makes. Each claim was treated as false until a search failed to find a
sufficiently close precedent; what survived is in `CLAIMS.md`, and the machine-readable
table is `data/graph/prior_art.csv`.

## Search method

| | |
|---|---|
| **Date** | 2026-09-20 |
| **Sources** | PubMed (E-utilities via connector); Europe PMC REST body-text search (open-access subset); one web search for a preprint-only tool |
| **Screened** | 279 abstracts across 23 queries, LLM-screened against a per-claim question, then manually reviewed |
| **Full text** | 198 open-access full texts retrieved and grepped at **sentence level** for the specific methodological claim |
| **Bias** | Primary papers preferred over reviews. Where only a review surfaced, the claim is marked as unresolved rather than novel |

**A methodological failure worth recording.** The first full-text pass used Europe PMC's
`FULL_TEXT:` field and returned zero hits for all five queries. `FULL_TEXT:` is not a valid
field name — it fails silently rather than erroring. The correct field is `BODY:`, which
returned 593 hits for the first query. Five "no precedent found" results were an artefact
of a typo in a field name. This is exactly the failure mode the adversarial rule exists to
catch: **a novelty claim is cheapest to "prove" with a broken search.** Any future search
should validate its syntax against a query expected to return many hits before trusting a
zero.

---

## 1. What we must credit, not claim

**TE quantification with multi-mapping reads is solved prior art, and we use it.**
`TEcount` from **TEtranscripts** (Jin et al., *Bioinformatics* 2015,
[10.1093/bioinformatics/btv422](https://doi.org/10.1093/bioinformatics/btv422)) apportions
ambiguously mapped reads between genes and TEs by expectation-maximisation. Every TE number
in this project comes out of that tool. It is not our method and must never be presented as
one.

Alternatives we do **not** use and have **not** benchmarked against:

| Tool | Reference | What it does differently |
|---|---|---|
| Telescope | *PLoS Comput Biol* 2019, [10.1371/journal.pcbi.1006453](https://doi.org/10.1371/journal.pcbi.1006453) | Bayesian reassignment to specific **loci** |
| SQuIRE | *Nucleic Acids Res* 2019, [10.1093/nar/gky1301](https://doi.org/10.1093/nar/gky1301) | Locus-specific interspersed repeat expression |
| SalmonTE | *Pac Symp Biocomput* 2018, PMID 29218879 | Fast quantification pipeline |
| TEspeX, MATES, IRescue | various | Exonised-fragment bias; single-cell resolution |
| **MAJEC** | bioRxiv 2026, [10.64898/2026.04.10.717472](https://doi.org/10.64898/2026.04.10.717472) | Unified gene/isoform/locus-level quantification; targets **gene-overlap contamination** |

MAJEC deserves specific treatment because it addresses a failure mode we do not: reads in
TE fragments that overlap gene exons. Its own benchmark reports reducing exon-overlap
contamination of locus-level estimates from roughly 43% to 5%. Critically for us, the same
benchmark reports **subfamily-level differential-expression concordance of r = 0.987 with
TEtranscripts** — so our subfamily-level conclusions are not invalidated by it, and the
right response is the robustness experiment in `QUANTIFIER_ROBUSTNESS.md`, which we have
written and **not run**.

## 2. What we wrongly claimed, and the correction

**"Nobody has systematically perturbed genes to find TE regulators."** False, and not
marginally. Genome-wide RNAi screens for transposon silencers date to *C. elegans* in 2003
([10.1016/s0960-9822(03)00539-6](https://doi.org/10.1016/s0960-9822(03)00539-6)) and
*Drosophila* in 2013 ([10.1016/j.molcel.2013.04.006](https://doi.org/10.1016/j.molcel.2013.04.006)).
In human cells, genome-wide CRISPR screens for L1 regulators were published in *Nature* in
2018 ([10.1038/nature25179](https://doi.org/10.1038/nature25179)), and the approach is still
active ([10.1186/s13100-025-00386-5](https://doi.org/10.1186/s13100-025-00386-5), 2025).

What survives is narrower and different in kind. Those screens are **prospective**: designed
around a TE readout, usually a reporter, usually focused on L1. Our question is:

> What can be recovered by re-mining generic perturbational transcriptomic datasets for TE
> phenotypes that the original investigators did not measure?

We did not locate a precedent for that at scale (`D4`). It is a scoped negative, not a
proof of absence.

**"No public knowledge graph has TEs."** Replaced with the defensible version: *major
general-purpose human biomedical knowledge graphs — PrimeKG, Hetionet, Open Targets — do
not model TE families or loci as first-class entities.* The nearest structural precedent
found is **ICEO** ([10.1038/s41597-021-01112-5](https://doi.org/10.1038/s41597-021-01112-5)),
an ontology making bacterial integrative and conjugative elements queryable first-class
entities — the right idea, a different domain, and not perturbational.

**The set-level statistic is not new.** Comparing a focal feature set's fold-change
distribution against all other features is **competitive gene-set testing**: CAMERA
([10.1093/nar/gks461](https://doi.org/10.1093/nar/gks461)) and GSEA
([10.1073/pnas.0506580102](https://doi.org/10.1073/pnas.0506580102)). Aggregate and global
TE readouts also exist, including in neurodegeneration: ALS cortex stratifies into subtypes
one of which is defined by retrotransposon activation
([10.1016/j.celrep.2019.09.066](https://doi.org/10.1016/j.celrep.2019.09.066)), and aggregate
intact-L1 expression has been quantified in the same tissue
([10.1186/s13041-022-00914-x](https://doi.org/10.1186/s13041-022-00914-x)). TE-category
enrichment testing has a dedicated web server
([10.1093/nar/gkae411](https://doi.org/10.1093/nar/gkae411)).

**A correction to the brief that prompted this search.** The suggested wording was that
"global TE shifts *relative to genes* have appeared in neurodegeneration analyses." The
first half is right; the second half we could not confirm. The neurodegeneration work uses
aggregate TE quantities and subtype signatures — it does not use the protein-coding
fold-change distribution from the same contrast as an internal reference. That distinction
is the whole content of what survives below.

## 3. What survived

**D8 — the normalisation-invariance framing.** Across 198 open-access full texts retrieved
from targeted body-text queries, we did not locate a paper that uses the protein-coding
log₂ fold-change distribution *within the same contrast* as the reference against which TE
fold changes are tested, on the explicit grounds that per-sample size factors cancel in the
difference of the two medians. The two nearest sentence-level hits use protein-coding genes
only to *define* intergenic TEs, and to describe structural-variant distributions.

To be precise about what this does and does not mean:

- The **statistic** is standard (§2). We are not claiming a new test.
- The **argument for why it is the right primary readout for TEs** — that it is immune to
  the normalisation error which is the field's main objection to TE quantification — is
  what we did not find stated.
- It is a **scoped negative**: Europe PMC's open-access subset, four body-text queries,
  one date. A closed-access methods section could contain it.

**D12 — the assembly.** Each component has precedent: TE quantification (TEtranscripts),
perturbational screening (CRISPR/RNAi screens), knowledge graphs over biology (PrimeKG,
Hetionet), KG-driven perturbation prediction (TxPert), rule-based reasoning, druggability
annotation (Open Targets). What did not surface is the combination, which is the honest
form of the claim:

> An evidence-traceable perturbational reasoning system for transposable-element
> regulation: it re-analyses perturbation experiments for effects on the repetitive genome,
> converts those measurements into signed, provenance-tracked relationships, connects them
> to known mechanisms, and generates testable hypotheses whose evidence paths can be
> inspected and falsified.

## 4. The nearest competitor, stated fairly

**TxPert** (*Nat Biotechnol* 2026,
[10.1038/s41587-026-03113-4](https://doi.org/10.1038/s41587-026-03113-4)) uses multiple
knowledge graphs of gene-product relationships to predict transcriptomic responses to
genetic perturbations, and reports approaching split-half experimental reproducibility for
unseen single perturbations. It is the closest thing to a competitor in the space, and at
least three other KG-based perturbation predictors exist.

The distinction to draw — carefully, because it is narrow — is that TxPert's published
output space is conventional transcriptomic response. It does not model transposable
elements as an output. **TxPert plus a TE-aware expression matrix would be a strong
competitor, and that is a closable gap, not a closed one.** Anyone with a TE quantification
pipeline and TxPert could build it. That is a reason to state the claim precisely now, not
a reason to pretend the risk is absent.

It is also the right long-term direction rather than a threat to argue against. Once the
measured matrix is large enough to hold out a validation set, a TE-specific
TxPert/GEARS-style model becomes feasible, and the rule engine is best understood as a
**bootstrap**: what generates testable hypotheses *before* the atlas is large enough for
learned prediction. Rules and a learned model can coexist; claiming symbolic reasoning will
permanently outperform learning would be a weaker and less interesting position.

## 5. A finding that complicates our own graph

cGAS-deficient mice show premature ageing with LINE-1 derepression and inflammation
([10.1038/s43587-026-01206-y](https://doi.org/10.1038/s43587-026-01206-y), *Nat Aging* 2026),
implicating cGAS in maintaining H3K9me3 rather than only sensing cytoplasmic DNA.

This matters structurally, not just as a citation. Our graph draws cGAS as **downstream** of
TE derepression. If cGAS also acts upstream in chromatin control, then the TE → sensor →
inflammation path contains feedback, and a directed acyclic reading of it is wrong. The
`EPISTEMOLOGY.md` ladder and the R6 rule are written so this is expressible rather than
assumed away, and it is listed as an open structural issue in `CRITIQUE.md`.

---

# Second pass: external review, 2026-09-22

The first pass (above) was run by the same agent that built the project, which is a
structural conflict of interest no amount of adversarial phrasing removes. On 2026-09-22 the
completed walkthrough was given to a **separate deep-research system** and it was asked to
attack the positioning. It found prior art this pass had missed, in two areas that were not
searched at all the first time.

The full landscape write-up is `LANDSCAPE.md`. The machine-readable rows are in
`data/graph/prior_art.csv` (claim ids `N1b`–`N15c`, `S1`, `S2`, `X1`). What follows is what
changed.

## Search method for the second pass

| | |
|---|---|
| **Date** | 2026-09-22 |
| **Sources** | PubMed E-utilities (via connector); Europe PMC REST |
| **Method** | Every factual assertion in the review was re-searched from scratch. The review's own citations were **not visible** — it named papers, years and numbers with no resolvable identifiers — so nothing in it was accepted without an independent hit |
| **Outcome** | **29 verified, 1 not found, 6 unverifiable from this environment** |

## What the first pass missed, and why

**Two entire categories were never searched.**

1. **TE expression atlases.** The first pass searched for TE *knowledge graphs* and TE
   *quantification methods*, and never asked whether TE *atlases* exist. They do, and they
   are large: TE-SCALE (1.3 M cells, 330 samples, 20 cancer types,
   [10.1093/nar/gkaf1235](https://doi.org/10.1093/nar/gkaf1235)); TEITbase (TE-initiated
   transcripts across 33 cancer types,
   [10.1093/database/baag025](https://doi.org/10.1093/database/baag025)); REdiscoverTE across
   TCGA with over 400 altered TE subfamilies
   ([10.1038/s41467-019-13035-2](https://doi.org/10.1038/s41467-019-13035-2)); ERVmap
   ([10.1073/pnas.1814589115](https://doi.org/10.1073/pnas.1814589115)).
   **Consequence:** the phrase the audit already bans is now banned for a documented reason,
   and the surviving distinction is axis-based — those atlases answer *where* TEs are active,
   this project asks *what perturbation changed them*.

2. **The commercial landscape.** Not searched at all. **ROME Therapeutics** built a company
   on the repeat genome with published science that is verifiable and ahead of this project
   on biology: LINE-1 ORF2p structures
   ([10.1038/s41586-023-06947-z](https://doi.org/10.1038/s41586-023-06947-z), *Nature* 2024),
   a pan-cancer LINE-1 activity model with locus heterogeneity
   ([10.1038/s41467-025-57271-1](https://doi.org/10.1038/s41467-025-57271-1)), and the
   genome-wide L1 regulator screen already cited above. Several other companies were named;
   none of the corporate claims can be checked from this environment, and they are tagged
   accordingly in `LANDSCAPE.md` §6.

**Two claims narrowed further.**

- **D1 (knowledge graphs).** Already narrowed once. Two closer precedents now exist in the
  record: **TEKRABber** ([10.7554/elife.103608](https://doi.org/10.7554/elife.103608)), which
  builds TE–KRAB-ZFP networks in human brain evolution, and **PlaNC-TE**
  ([10.1093/database/bay078](https://doi.org/10.1093/database/bay078)), an ncRNA–TE
  knowledgebase in plants. TEKRABber is closer in subject matter than ICEO was. The narrowed
  wording survives — PrimeKG ([10.1038/s41597-023-01960-3](https://doi.org/10.1038/s41597-023-01960-3))
  and Hetionet ([10.7554/elife.26726](https://doi.org/10.7554/elife.26726)) genuinely have no
  TE node type — but "nobody builds TE networks" would now be false twice over.
- **Subfamily resolution.** Defended upward (aggregating loses signal, measured). The review
  established that it must be defended **downward** too: locus-resolution measurement is
  established (CELLO-seq, [10.1038/s41587-021-01093-1](https://doi.org/10.1038/s41587-021-01093-1)),
  locus-level annotation exists at scale (2,596 long-read datasets, 21 organs, 71 cell lines,
  [10.1186/s44342-025-00048-1](https://doi.org/10.1186/s44342-025-00048-1)), and two 2026
  preprints push further. The ontology roadmap in `LANDSCAPE.md` §1.1 is the response.

**One new hazard.** There is now a published benchmark of **16** TE RNA quantification tools
(She J, Wang J, Yang E., [10.1093/gpbjnl/qzag044](https://doi.org/10.1093/gpbjnl/qzag044)).
"Which quantifier and why" is no longer an open question in the field; it has an answer sheet.

## One claim did not survive verification

The review asserted that a **September 2026 *GeroScience* article** compares retroelement
deregulation between DNMT3A- and TET2-mutant clonal haematopoiesis — direct recent support
for the project's own hypothesis.

**It was not found.** Five searches (PubMed `GeroScience retroelement`,
`GeroScience transposable element`, `DNMT3A TET2 retroelement`,
`retroelement deregulation clonal hematopoiesis`; Europe PMC `DNMT3A AND TET2 AND
(retroelement OR retrotransposon) AND PUB_YEAR:2026`) returned no matching paper. The
*GeroScience* TE papers that do exist concern canine LINE-1 methylation with age,
Alzheimer's/cognitive impairment, and Alu overexpression in fibroblasts. Recorded as `X1`
with verdict `NOT_FOUND_IN_PRIOR_ART_SEARCH`.

**The single claim most favourable to this project's hypothesis is the one that did not
resolve.** That is worth stating in exactly those terms, because it is the argument for the
citation gate in one sentence.

**What was found instead is better than what was claimed.** Two verified papers, neither in
the first pass:

- **Scheller et al., *Nature Cancer* 2021**
  ([10.1038/s43018-021-00213-9](https://doi.org/10.1038/s43018-021-00213-9), PMID 35122024) —
  hotspot **DNMT3A** mutations in clonal haematopoiesis and AML sensitise cells to azacytidine
  **via a viral mimicry response**. Peer-reviewed, CH-specific, and direct support for the
  DNMT3A arm of `HYPOTHESIS_DNMT3A_TET2.md`. It says nothing about the TET2 contrast, and it
  is not a measurement made here.
- **Mutant ASXL1-BAP1-EHMT complex**, *PNAS* 2025
  ([10.1073/pnas.2413302121](https://doi.org/10.1073/pnas.2413302121), PMID 39752521) — a
  different CH driver converging on heterochromatin dysfunction. ASXL1 is already in the CH
  gene set; this is a second mechanistic entry point and a natural next perturbation target.

## What the second pass did not change

The differentiation that survived the first attack survived the second one, and the wording
in `CLAIMS.md` D8/D12 stands: signed perturbation edges, four evidence layers in one graph,
inspectable mechanistic reasoning with proof trees, re-mining public perturbation data for
TE phenotypes, and refusing when the evidence is insufficient. The review's independent
conclusion was that it did not find a public system combining those pieces — which is a
second `NOT_FOUND`, from a different searcher, and still not proof of absence.
