# Evidence-tiered knowledge representation for transposable-element regulation, with inspectable inference and a quantified account of what the inference rests on

**Hanae Roussotte**¹

¹ *Affiliation to be completed.* Correspondence: *to be completed.*

**Preprint draft.** Prepared for a methods/resource venue. All numbers below are produced by
the accompanying repository and reproducible from a single command; the provenance of each is
given in *Availability*.

---

## Abstract

**Background.** Transposable elements (TEs) occupy roughly half the human genome and are
silenced by chromatin machinery whose failure is linked to inflammation and ageing. They are
nonetheless absent from graph-based target discovery in two independent ways: standard RNA-seq
pipelines discard the multi-mapping reads that report on repeats, and general-purpose
biomedical knowledge graphs do not model TEs as first-class entities. Large TE expression
atlases exist, but they describe *where* elements are active rather than *what perturbation
changes them*.

**Results.** We describe a knowledge representation in which TEs are first-class nodes and
every edge carries a source, a retrieval date, a stable identifier and an evidence tier, and a
forward-chaining rule layer whose conclusions inherit the weakest tier on their derivation path
and print that derivation. As a pilot we re-analysed three public CRISPR/CRISPRi knockdown
experiments (SETDB1, TRIM28, DNMT1 in K562) against the repeat annotation, yielding 27 measured
edges within a graph of 9,366 typed edges over 1,910 nodes. A structural audit of 42 metrics
reports zero schema violations and complete provenance, and surfaces one genuine defect: a
single gene–TE pair asserted in both directions by the same source. The rule layer produces 89
derived edges and answers queries for genes with no measurement and no ontology annotation.

We report three methodological results that generalise beyond this domain. First, a
*compartment* statistic comparing TE against protein-coding log₂ fold changes within one
contrast is invariant to sample-level size-factor error, but its naive significance test is
strongly anti-conservative: measured mean pairwise correlation among TE features ranges 0.006
to 0.48, implying variance inflation of 4× to 155×, and we retract our own p-values
accordingly. Second, a *leave-one-anchor-out* analysis quantifies how much of the inferred
layer depends on each measured input; here 78 of 83 derived edges rest on a single chromatin
mark grounded by one experiment, and removing the largest measured effect changes nothing
because a scaffold protein cannot satisfy the grounding rule. Third, this dependency structure
converts directly into an experiment ranking.

**Conclusions.** Evidence tiers, printed derivations and an explicit refusal state make an
inference layer auditable, and dependency analysis turns a knowledge graph into an
experimental-design instrument. The pilot is three experiments and is presented as such.

**Keywords:** transposable elements; knowledge graph; provenance; neurosymbolic reasoning;
perturbation transcriptomics; experimental design

---

## 1 Background

Transposable elements make up approximately half the human genome. Their transcriptional
silencing is maintained by DNA methylation and repressive histone modification, and loss of
that silencing has been associated with interferon signalling, inflammation and senescence
[10.1038/s41586-018-0784-9]. A current conceptual review of the field is given by Ho, Douse
and Marazzi [10.1016/j.cell.2026.05.003].

Two structural exclusions make it difficult to ask what an arbitrary gene does to the
repetitive genome.

**From the data.** Reads originating in repeats map to many genomic locations. Standard RNA-seq
quantification discards multi-mapping reads, so TE signal is largely absent from public
expression matrices. Dedicated quantifiers exist and are mature: TEtranscripts/TEcount
redistributes multi-mapping reads by expectation–maximisation at subfamily level
[10.1093/bioinformatics/btv422]; Telescope [10.1371/journal.pcbi.1006453] and SQuIRE
[10.1093/nar/gky1301] resolve individual loci; single-cell methods and long-read locus
annotation now exist [10.1038/s41587-021-01093-1]; and at least sixteen tools have been
formally benchmarked with usage guidance [10.1093/gpbjnl/qzag044]. The limitation is therefore
not method availability but that public perturbation experiments were, with few exceptions,
never re-quantified this way.

**From the graph.** General-purpose biomedical knowledge graphs do not model TEs as
first-class entities: PrimeKG defines ten principal node types [10.1038/s41597-023-01960-3] and
Hetionet eleven [10.7554/elife.26726], none of which is a transposable element. TE-specific
relationship resources do exist — TEKRABber builds TE–KRAB-zinc-finger networks
[10.7554/elife.103608], PlaNC-TE catalogues ncRNA–TE relationships in plants
[10.1093/database/bay078], and ICEO provides an ontology for bacterial mobile elements
[10.1038/s41597-021-01112-5] — but none supplies human TE regulatory edges with perturbational
evidence. Consequently a TE cannot lie on a returned path in the graphs most target-discovery
work is built on.

**What already answers part of this.** Large TE expression atlases exist and are substantially
larger than the pilot reported here: TE-SCALE [10.1093/nar/gkaf1235], TEITbase
[10.1093/database/baag025], REdiscoverTE [10.1038/s41467-019-13035-2] and ERVmap
[10.1073/pnas.1814589115]. Genome-wide screens for TE regulators have been performed
repeatedly, including human LINE-1 screens [10.1038/nature25179, 10.1186/s13100-025-00386-5].
Knowledge-graph-driven prediction of perturbation response is an active area — GEARS
[10.1038/s41587-023-01905-6], TxPert [10.1038/s41587-026-03113-4] — with standardised
perturbation resources [10.1038/s41592-023-02144-y]. We claim none of this.

The distinction we do draw is axial. Atlases answer *where* TEs are active — which tissue,
which tumour, which cell. They do not answer *what perturbation changed them, through what
mechanism, and what to measure next*. The perturbational axis is comparatively empty, and
answering on it requires representing evidence of different strengths in one structure without
allowing the weakest to be reported as the strongest.

---

## 2 Implementation

### 2.1 Schema

Nodes are typed: `Gene`, `Complex`, `Pathway`, `GOTerm`, `ChromatinMark`, and TE entities.
Predicates carry a type contract enforced at build time — for example `SILENCES` and
`DEREPRESSES` may relate a `Gene` only to a TE entity, `DEPOSITS_MARK` and `ERASES_MARK` relate
a `Gene` to a `ChromatinMark`, and `MARK_AT` relates a `ChromatinMark` to a TE entity.

TE entities are represented at class, family and subfamily granularity. `TELocus` and
`TETranscript` are deliberately **not** implemented: the field is moving to locus resolution
and this schema does not reach it. Subfamily is used because aggregating upward measurably
loses signal at the depth sampled here — AluY is significant after TRIM28 knockdown at
padj = 0.0005 while the pooled Alu/SINE family is not — and the aggregation comparison is
reported rather than assumed.

### 2.2 Evidence tiers and provenance

Every edge carries `source`, `source_detail`, a retrieval date, a stable 15-character
identifier, and one of four tiers:

| tier | meaning |
|---|---|
| `measured` | produced by our own re-analysis of a perturbation experiment |
| `curated` | a record in a curated database |
| `literature` | extracted from published text; unvalidated |
| `inferred` | produced by a rule from premises |

Edges additionally carry twelve context qualifiers — cell type, species, perturbation modality,
assay, timepoint, dose, TE resolution, quantifier, reference scope and others — with the
literal value `not_applicable` where a qualifier does not apply, distinguished from *not
recorded*.

### 2.3 Rule layer

Six rules chain forward to a fixpoint with a maximum of four hops. `R1_MARK_GROUNDING` converts
a measured gene–TE effect plus a curated enzymatic annotation into a `MARK_AT` edge;
`R2_WRITER_TRANSFER` and `R3_ERASER_INVERSION` transfer that grounding to other writers and
invert it for erasers; `R4_COMPLEX_CONSENSUS` operates over complexes of no more than eight
members; `R5_RECRUITMENT_CHAIN` and `R6_TE_MEDIATED_INFLAMMATION` are implemented and do not
fire (§3.5).

Three properties matter more than the specific rules.

1. **Tier propagation.** A derived conclusion inherits the *weakest* tier on its path. A chain
   containing one `literature` edge can never be reported as `measured`.
2. **Context inheritance.** Where premises agree on a context value the conclusion inherits it;
   where they disagree the conclusion records `mixed(a|b)`; and any specific experimental
   context sets `context_generalization_required=yes` with the grounding context named. A
   prediction derived from a K562 experiment is labelled as bound to K562.
3. **Refusal.** Where no path exists the system returns `best_tier: none`. This is a supported
   output, not an error.

Every answer prints its derivation, and a citation gate rejects any generated sentence whose
claim is not backed by a resolvable edge identifier.

### 2.4 Measurement pipeline

Public FASTQ files are subsampled, aligned with HISAT2 reporting up to 100 alignments per read
[10.1038/s41587-019-0201-4] (STAR is supported as an alternative [10.1093/bioinformatics/bts635]
but the two have not been compared head to head on identical samples — an open falsifier), and
quantified with TEcount in multi mode [10.1093/bioinformatics/btv422] against a RepeatMasker
annotation for hg38 filtered to 1,057 subfamilies over 3,761,678 loci, together with GENCODE
gene annotation [10.1093/nar/gkaa1087]. Differential expression uses DESeq2
[10.1186/s13059-014-0550-8] via PyDESeq2 [10.1093/bioinformatics/btad547], with size factors
estimated on protein-coding genes only so that a global shift in the TE compartment cannot
partially normalise itself away. Multiple testing is controlled within each contrast by the
Benjamini–Hochberg procedure [10.1111/j.2517-6161.1995.tb02031.x].

### 2.5 The compartment statistic

For a contrast *c*, let *T* be the set of quantified TE subfamilies and *G* the set of
quantified protein-coding genes. We define

> Δ_c = median{ log₂FC(t) : t ∈ T } − median{ log₂FC(g) : g ∈ G }

Because DESeq2 size factors are per-sample and multiplicative, an error in normalisation shifts
both medians by the same additive amount on the log scale and cancels in the difference. Δ is
therefore invariant to *sample-level multiplicative* normalisation error specifically. It is
**not** protected against differential mappability, annotation overlap between TEs and gene
exons, composition effects, or a genuine global transcriptional shift, and we state this rather
than the stronger claim.

Δ is a competitive set comparison and belongs to an established family — GSEA
[10.1073/pnas.0506580102] and CAMERA [10.1093/nar/gks461]; the latter exists precisely because
such tests are anti-conservative under inter-feature correlation. §3.3 measures that inflation
in our own data.

---

## 3 Results

### 3.1 The graph

The assembled graph contains **9,366 typed edges over 1,910 nodes**. The curated layer draws
from Reactome (4,900 edges) [10.1093/nar/gkab1028], Complex Portal (2,321)
[10.1093/nar/gkab991], STRING v12 at confidence ≥ 700 (1,724) [10.1093/nar/gkac1000] and the
Gene Ontology (318, plus 44 mechanism edges) [10.1093/genetics/iyad031]. The literature layer
contributes 32 edges and the measured layer 27, from ENCODE [10.1093/nar/gkz1062].

Sources are queried directly rather than through an aggregating knowledge graph. This is partly
a provenance decision — an aggregator's merge decisions would be inherited without being
auditable — and partly forced: no aggregator contains TE nodes, so none can contribute to the
half of the graph that is sparse.

A structural audit (`make validate`, 42 metrics) reports **0 schema violations** across 9,366
typed edges, **0** self-loops, **0** duplicate triples, complete source and retrieval-date
provenance, and 97.6% of nodes in one connected component. Two findings are unfavourable and
are reported as such. **TE vocabulary coverage is 0.0199**: only 21 of 1,057 subfamilies carry
any edge. And the audit surfaces **one sign contradiction within a single layer** — one gene–TE
pair asserted as both silencing and derepressing, both edges extracted from the *same* abstract.
It is retained rather than deleted: it is a visible instance of the literature layer's unmeasured
error rate, and the reason that layer is barred from grounding a rule.

### 3.2 Measured effects, and a failed control

Three ENCODE knockdown experiments in K562 were re-quantified (11 libraries). Before any TE
result, we checked whether each perturbation reduced its own target transcript.

| knockdown | target log₂FC | transcript remaining | padj | verdict |
|---|---|---|---|---|
| DNMT1 | −1.87 | 27% | 1.0 × 10⁻¹⁸ | confirmed |
| TRIM28 | −1.12 | 46% | 8.6 × 10⁻¹² | confirmed |
| SETDB1 | −0.35 | 78% | 0.77 | **not confirmed** |

The SETDB1 result is consequential because SETDB1 grounds three of the four `MARK_AT` edges in
the graph. We report it as *not confirmed* rather than *failed*: CRISPRi acts on transcription
and a steady-state snapshot at reduced depth is a weak readout, and the same libraries did
produce two ERV-family effects. It is nonetheless the least-confirmed perturbation carrying the
largest share of the inference layer, and §3.4 quantifies exactly how large.

This check had been written into a pre-registration for a *future* experiment and had never
been applied retrospectively to the three contrasts already in hand. Applying it there is how
the problem surfaced.

### 3.3 Retraction of our own significance test

Compartment effects and their corrected evaluation:

| contrast | Δ | fraction of TE features up | naive Mann–Whitney p | mean pairwise ρ̄ | variance inflation | correlation-aware p |
|---|---|---|---|---|---|---|
| SETDB1 | +0.023 | 0.53 | 0.41 | 0.399 | 141× | 0.89 |
| TRIM28 | +0.421 | 0.73 | ~~2.3 × 10⁻²¹~~ | 0.479 | 155× | 0.44 |
| DNMT1 | **+0.130** | **0.63** | ~~1.4 × 10⁻⁷~~ | **0.006** | **4.1×** | **0.045** |

The naive test treats 322–503 TE subfamilies as independent observations. They are not:
subfamilies covary through shared regulatory machinery, shared sequence ancestry and shared
mapping ambiguity. With ρ̄ estimated from residuals in the manner of CAMERA
[10.1093/nar/gks461], the two CRISPRi contrasts carry approximately **two features' worth** of
independent information rather than three hundred. **We retract those p-values.**

The DNMT1 effect survives in a weaker and better-supported form: same sign in **6 of 6**
alternative definitions of the TE set (LINE +0.19, SINE +0.10, LTR +0.11, DNA +0.10, an
expression-filtered variant, a trimmed variant); leave-one-library-out range +0.10 to +0.19
with the sign preserved in 4 of 4; the most extreme of the three admissible sample labellings by
a factor of 3.7; and correlation-aware p = 0.045. TRIM28's *compartment* claim does not survive
— a permuted labelling produced a larger Δ than the true labelling — and is demoted to an effect
size. Its per-feature result (AluY, padj = 0.0005) is a different statistic and is unaffected.

**A design limit worth stating plainly.** With two replicates per arm there are three admissible
label permutations, so no sample-level p below 0.333 is attainable regardless of effect size.
More replicates, not a better test, is what would settle these claims.

### 3.4 What the inference rests on, measured

The rule layer produces **89 derived edges** (R1: 4, R2: 38, R3: 45, R4: 2). Removing each
measured anchor and re-running to fixpoint:

| anchor removed | derived edges surviving | genes answered |
|---|---|---|
| none | 89 | 10/10 |
| TRIM28 | **89** | 9/10 |
| DNMT1 | 83 | 7/10 |
| SETDB1 | **8** | 8/10 |

Two results follow, and the counter-intuitive one is more useful.

**Measured evidence enters the inference layer only through curated enzymatic roles.** TRIM28
produces the largest measured effect in the dataset and contributes **zero** derived edges,
because a scaffold protein carries no `DEPOSITS_MARK` annotation and therefore cannot satisfy
`R1_MARK_GROUNDING`. More measurement of scaffolds would not increase inferential capacity;
ingesting `RECRUITS` edges would, and the graph currently holds none.

**The inference layer rests on very little.** Tracing each derived edge to the grounding it
consumed: **78 of 83** rest on H3K9me3, grounded by three edges all originating in the SETDB1
experiment; **5** rest on 5mC, grounded by one edge from DNMT1; and H3K27me3 has **zero**
groundings, so nothing about it can be derived at all. No hold-out ever reversed a direction —
genes either keep their prediction or return `best_tier: none`.

### 3.5 From dependency to experiment ranking

Because each derived edge is attributable to a grounding, the value of a candidate experiment
can be stated as the number of derived edges that would gain a second, independent grounding.
This is a count of exposure, not an expected-information calculation, and we label it as such.

| mark | derived edges at stake | current groundings | candidate enzymes in graph | of those, with a public knockdown |
|---|---|---|---|---|
| H3K9me3 | 78 | 3 (all SETDB1) | 26 | **0** |
| 5mC | 5 | 1 (DNMT1) | 5 | 1 |
| H3K27me3 | 0 | 0 | 7 | 0 |

The ranking is unambiguous and inconvenient: the highest-value class of experiment is any of
the 26 H3K9me3 writers or erasers, **none of which has a public knockdown**. Across the whole
graph, of 40 chromatin-mark writers and erasers, ENCODE contains knockdowns for three, two of
which are already used. The public resource is close to exhausted for this purpose, which is
itself a result about the field rather than about this project.

`R5_RECRUITMENT_CHAIN` fires zero times for a structural reason the audit identifies: there are
no `RECRUITS` edges in the graph, so the rule has no possible input. The underlying biology is
well established, so this is a missing ingest rather than a missing mechanism.
`R6_TE_MEDIATED_INFLAMMATION` requires TE derepression and inflammatory induction measured in
the same contrast, which §3.6 explains did not occur.

### 3.6 A refusal, a repair, and a null with a mechanism

An initial attempt to test whether TE derepression was accompanied by a type-I interferon
response was **refused** by the pipeline: at the reduced reference scope only **16.8%** of the
type-I interferon gene set was quantified, below the coverage guard. Rather than report the
result with a caveat, we constructed a 62 Mb targeted reference containing the signature genes,
raising type-I interferon coverage to **76.8%**.

The re-run answer was still a null: no interferon signature moved in any contrast under
Bonferroni correction, under either background, with bootstrap intervals excluding effects of
the magnitude seen in the TE arm. A control confirmed the reference change did not perturb the
existing measurements (Pearson 0.992–0.996; median |Δlog₂FC| 0.006–0.027; no sign flips).

The null has an explanation in the data. In K562 the cytosolic sensing entry points are barely
expressed — CGAS 0.21, ZBP1 0.26, NLRP3 0.20, TLR3 0.00 CPM — while downstream transducers are
abundant (TYK2 799, MAVS 586, IRF3 317, STING1 270 CPM), and ADAR, which suppresses dsRNA
sensing, is at 823 CPM. RIG-I and MDA5 are expressed but low (5.4 and 8.5 CPM). The defensible
claim is therefore not that TE derepression fails to induce interferon, but that **this dataset
cannot decisively test viral mimicry** and a sensing-competent context is required. We note that
no positive stimulation control was performed, so functional incompetence is inferred from
transcript abundance rather than demonstrated.

### 3.7 Results withheld

Three further components were built, evaluated and not shipped. A rule-based literature
extractor reached precision 0.109 with direction agreement at chance (10/21) against an
LLM-labelled reference and was rejected; its code is retained so the negative result is
reproducible. Link prediction was gated at design time on the existence of a held-out
validation set, which three knockdowns cannot provide. And the p-values of §3.3 were retracted
after evaluation. In the demonstration interface, 4 of 14 queried genes return `best_tier:
none`.

---

## 4 Discussion

The contribution here is a representation and an analysis, not a data resource. Three elements
appear to us to generalise beyond transposable elements.

**Tier propagation by weakest link, with printed derivations.** Systems that mix curated,
textual and experimental evidence routinely report a single confidence score. Taking the
minimum along a path is more conservative and, more importantly, inspectable: a reader can see
which link is weak. Combined with a refusal state, this makes "we do not know" a first-class
output rather than a failure of the query.

**Anchor-dependence analysis.** Knowledge graphs are typically characterised by size. Size is
close to irrelevant to inferential capacity: this graph has 9,263 curated edges and four
grounding edges, and only the latter matter. Reporting how much of the derived layer collapses
when each measured input is removed is cheap, generalises to any graph with a rule layer, and
in our case produced the finding that the largest measured effect contributes nothing. We are
not aware of this being reported routinely and suggest it should be.

**Dependency as experimental design.** Because the dependency is attributable, it ranks
experiments. This is the sense in which a knowledge graph can be an instrument rather than a
database: it answered "what should we measure next?" with a specific class of enzyme and,
uncomfortably, with the observation that the public data for that class does not exist.

**Relation to the worked example.** The rule layer derives that loss of a 5mC eraser should
*lower* TE expression, from a DNMT1 measurement and two Gene Ontology annotations, having seen
no data for that eraser. The direction agrees with a measurement in human clonal haematopoiesis
[10.1007/s11357-026-02510-6]. **The present author is a co-author of that study**, which was
known to this project from the outset; the agreement is therefore not a blind prospective
validation, and the measurement in question is a non-significant trend at n = 7. What can
fairly be said is that the derivation used no data from that study and crosses a different
quantifier, resolution, perturbation modality and tissue. Related mechanistic support for the
same axis is reported in [10.1038/s43018-021-00213-9] and [10.1073/pnas.2413302121].

**What this is not.** It is not an atlas; the atlases cited in §1 are orders of magnitude
larger. It is not a new quantification method; TEcount does that work and is credited
accordingly. It is not a perturbation-response prediction model; GEARS and TxPert are, and a
TE-aware output space added to such a model would be a strong competitor to this approach — a
closable gap rather than a closed one. The novelty claim we make is narrow: the *assembly* of
perturbational TE measurement, tiered provenance, inspectable inference and refusal did not
surface in two independent prior-art searches. That is a negative search result, not proof of
absence, and one claim we initially recorded as unfindable was later shown to exist.

---

## 5 Limitations

1. **Three knockdowns, one cell type.** All measured evidence derives from K562, a chronic
   myelogenous leukaemia line, and the derived layer is grounded by two of those experiments.
2. **Reduced reference scope and depth.** The pilot quantifies chr1 and chr19 at 1.5 M reads per
   library. chr19 is the most gene-dense and Alu-rich human chromosome and carries the KRAB-ZFP
   clusters, so it is not a neutral sample of the genome. Effect sizes should be treated as
   provisional.
3. **A failed control on the principal anchor** (§3.2), affecting the mark that supports 78 of
   83 derived edges.
4. **Two replicates per arm** cap any sample-level permutation p at 0.333 (§3.3).
5. **Subfamily resolution** where the field is moving to loci; `TELocus` is not implemented.
6. **Literature-tier accuracy is unmeasured.** The LLM extractions used to evaluate the rejected
   rule-based extractor were never themselves validated against human annotation.
7. **Aligners were never compared** head to head on identical samples.
8. **No time, position, dose or feedback.** The representation has no clock, a node is an
   identity rather than a coordinate, a signed edge has no magnitude axis, and forward chaining
   to a fixpoint cannot represent a cycle. The last is not hypothetical: cGAS has been reported
   to act upstream in chromatin maintenance as well as downstream as a sensor
   [10.1038/s43587-026-01206-y], so the TE→sensor→inflammation path contains a loop and its
   acyclic reading is wrong.
9. **Novelty rests on negative searches** by the same authors, with the demonstrated failure
   mode described in §4.

---

## 6 Conclusions

Transposable elements can be represented as first-class entities in a biological knowledge graph
with per-edge provenance and evidence tiers, and a rule layer over that graph can answer
questions about genes for which no relevant measurement exists while making the basis of each
answer inspectable and refusing where the basis is absent. Applied to a three-experiment pilot,
the same machinery quantified how little its own inference rests on and converted that into a
ranked experimental agenda. We suggest that reporting anchor dependence should be routine for
knowledge graphs carrying an inference layer, and that the honest unit of confidence for a
derived biological claim is the weakest link on its path.

---

## Availability

**Code, data and reproduction:** `https://github.com/hanaeroussotte/te-knowledge-graph`
(MIT licence; data derive from the cited sources under their own terms).

Every number in this manuscript is produced by the repository. `make gate` runs a claim audit,
resolves all cited DOIs and PMIDs against Crossref and NCBI, and re-runs regression pins on the
derivations. `make validate` regenerates the structural audit of §3.1; `src/run_de.py` and
`src/compartment_robustness.py` regenerate §3.2–3.3; `src/te_reason.py --export-derived`
regenerates §3.4; `results/experiment_priority.csv` is §3.5. Public data: ENCODE accessions
ENCSR819PCU, ENCSR591QYK, ENCSR600OWF with controls ENCSR095PIC and ENCSR712CQC.

**Competing interests.** The author is a co-author of [10.1007/s11357-026-02510-6], discussed
in §4.

**Funding.** To be completed.
