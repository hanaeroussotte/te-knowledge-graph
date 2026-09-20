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
