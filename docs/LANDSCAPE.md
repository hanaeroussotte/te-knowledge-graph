# The landscape: what already exists, and where this project sits in it

**Why this document exists.** On 2026-09-22 the project was given an external review by a
separate deep-research system, which was asked to attack the project's positioning using
the literature and the commercial landscape. It found substantially more prior art than
`PRIOR_ART.md` had, particularly in two areas the first prior-art pass had missed
completely: **TE expression atlases that already exist**, and **companies that have built
repeat-genome analytics platforms**. It also proposed wording changes, most of which were
adopted.

**Why this document is not just that review pasted in.** The review arrived with citation
markers whose targets were not visible — it named papers, years and numbers without
resolvable identifiers. This repository has a citation gate (`make gate` → `tests/check_citations.py`)
that resolves every DOI against Crossref and every PMID against NCBI, and a rule
(`CLAIMS.md`) that a claim without a resolvable identifier is not a claim. So every factual
assertion in the review was re-searched from scratch against PubMed and Europe PMC before
being allowed into this document. The results of that verification are in §9, and they
matter: **30 claims verified and six unverifiable from here.** One was initially recorded as
not found, wrongly — §10 is the correction, and it is the most instructive section in this
document.

That is the whole method, and it is worth stating plainly: an external review is evidence,
not authority. It gets checked like anything else.

---

## 0. How to read the verification tags

Every claim in this document carries one:

| Tag | Meaning |
|---|---|
| **[V]** | Verified here — the paper exists, the identifier resolves, and the specific number quoted was found in the abstract |
| **[V-ref]** | The paper is verified but a number attributed to it was not checked against its abstract |
| **[NF]** | Searched for and **not found**. Not "false" — not located by PubMed + Europe PMC on 2026-09-22. **§10 is a worked example of an `[NF]` that was simply a bad search, so treat every tag in this column as a statement about the search, not about the world** |
| **[U]** | Unverifiable from this environment (corporate facts, press releases, company websites — the sandbox reaches literature databases, not news) |

`[U]` is not a euphemism for "probably true". It means the claim is reported as
second-hand and should be spoken as second-hand.

---

## 1. The resolution frontier: the field is moving below the subfamily

The single most useful correction in the review. The TE hierarchy is:

```
class  →  family  →  subfamily  →  locus  →  transcript
(SINE)    (Alu)      (AluY)       (one of 104,272 AluY copies)
```

**This project operates at subfamily level.** That was a deliberate choice, defended in
`TE_RESOLUTION.md` and measured: aggregating *upward* to family/class demonstrably destroys
signal (AluY padj 0.0005 versus pooled `Alu:SINE` +0.616, not significant; SETDB1 2 hits → 0,
TRIM28 4 → 1). What the review adds is the observation that the field is moving *downward*,
and that our choice needs to be defended in that direction too.

The evidence that locus resolution matters:

- **[V]** The current conceptual review of the field — Ho JSY, Douse CH, Marazzi I,
  *Cell* 2026, [10.1016/j.cell.2026.05.003](https://doi.org/10.1016/j.cell.2026.05.003)
  (PMID 42276034) — frames TE DNA and RNA as drivers of gene expression, evolution and
  disease, and the locus-level direction as where the field is going. **This is the single
  paper to read before presenting.**
- **[V]** Copies within one subfamily behave differently enough that single-cell
  locus-specific measurement was worth building: CELLO-seq, *Nat Biotechnol* 2021,
  [10.1038/s41587-021-01093-1](https://doi.org/10.1038/s41587-021-01093-1) (PMID 34782740),
  with a protocol paper in *Nat Protoc* 2025,
  [10.1038/s41596-025-01203-2](https://doi.org/10.1038/s41596-025-01203-2) (PMID 40670609).
- **[V]** Locus-level annotation at scale now exists: a long-read analysis across
  **2,596 datasets, 21 organs and 71 cell lines**,
  [10.1186/s44342-025-00048-1](https://doi.org/10.1186/s44342-025-00048-1) (PMID 40770674).
  All three numbers were confirmed in the abstract.
- **[V]** Context-dependence is now quantified: Hyacinthe J & Bourque G, *Nat Commun* 2026,
  [10.1038/s41467-026-74920-1](https://doi.org/10.1038/s41467-026-74920-1) (PMID 42386716),
  report **456 cell-type–histone–TE triplets** with strong cell-type-specific enrichment.
  Note the precise unit: *triplets*, not "associations".
- **[V]** Two 2026 preprints push further: TEsingle
  ([10.64898/2026.03.19.712984](https://doi.org/10.64898/2026.03.19.712984), locus-specific
  single-cell) and TEscape
  ([10.64898/2026.07.08.737305](https://doi.org/10.64898/2026.07.08.737305), multiplatform
  long-read TE transcriptome). Preprints — cite as such.

### 1.1 What this changes in the ontology

`TE_RESOLUTION.md` already separates `TEFamily` from `TESubfamily` as distinct ontology
levels, for the measured reason above. The review's proposal — and it is adopted as a
**roadmap item, not a built feature** — is that the ontology should extend downward:

```
TEClass → TEFamily → TESubfamily → TELocus → TETranscript
```

with **evidence attaching at whichever level the experiment actually supports**. That is
the right design and it is genuinely more sophisticated than forcing one resolution, but it
is not implemented. `TELocus` and `TETranscript` do not exist as node types today. Saying
otherwise would be the exact failure this repository is built to avoid.

The honest position: *we chose subfamily because we measured that aggregating up loses
signal, and because the biological inference layer operates at that level. The field is
moving to loci. The schema should follow it, and the ontology is already split in a way
that permits it.*

---

## 2. The quantifier ecosystem, and the question we will be asked

We use `TEcount` from **TEtranscripts** (Jin et al., *Bioinformatics* 2015,
[10.1093/bioinformatics/btv422](https://doi.org/10.1093/bioinformatics/btv422)). This is
established prior art we credit and do not claim. `PRIOR_ART.md` §1 already says so. The
review adds four tools that pass had missed:

| Tool | Resolution | Idea | Reference | Status |
|---|---|---|---|---|
| TEtranscripts / TEcount | subfamily | EM allocation of ambiguous reads, genes + TEs jointly | [10.1093/bioinformatics/btv422](https://doi.org/10.1093/bioinformatics/btv422) | **what we use** |
| SalmonTE | family/subfamily | quasi-mapping, fast | PMID 29218879 | not benchmarked |
| SQuIRE | locus | genome alignment + locus quantification | [10.1093/nar/gky1301](https://doi.org/10.1093/nar/gky1301) | not benchmarked |
| Telescope | locus | Bayesian reassignment of ambiguous reads | [10.1371/journal.pcbi.1006453](https://doi.org/10.1371/journal.pcbi.1006453) | not benchmarked |
| **REdiscoverTE** | subfamily + genomic context | joint repeat/gene representation, applied across TCGA | **[V]** [10.1038/s41467-019-13035-2](https://doi.org/10.1038/s41467-019-13035-2) (PMID 31745090) | **new to us** |
| **ERVmap** | locus, ERVs | curated ERV locus set | **[V]** [10.1073/pnas.1814589115](https://doi.org/10.1073/pnas.1814589115) (PMID 30455304) | **new to us** |
| TElocal | locus | TEtranscripts-derived locus counting | no primary methods paper located **[NF]** | **new to us** |
| MAJEC | locus + gene + isoform | joint probabilistic model | [10.64898/2026.04.10.717472](https://doi.org/10.64898/2026.04.10.717472) | specified, not run |
| CELLO-seq | locus/transcript | long reads resolve ambiguity directly | **[V]** [10.1038/s41587-021-01093-1](https://doi.org/10.1038/s41587-021-01093-1) | **new to us** |

**[V] And there is now a benchmark.** She J, Wang J, Yang E., *Genomics Proteomics
Bioinformatics* 2026, [10.1093/gpbjnl/qzag044](https://doi.org/10.1093/gpbjnl/qzag044)
(PMID 42308529) — "Comprehensive Benchmarking with Guidelines for Analyzing Transposable
Element-derived RNA Expression". The abstract states **16 representative tools**. This is
the most immediately dangerous paper in the list, because it means "which tool did you pick
and why" is now a question with a published answer sheet. Read it.

### 2.1 The answer to "why TEcount and not MAJEC / Telescope / SQuIRE?"

Do not defend TEcount as superior. It is not the claim. The answer:

> The inference layer operates at subfamily resolution, so the quantifier is a mature,
> validated subfamily-level method. MAJEC addresses a different failure mode — gene-overlap
> contamination and locus assignment — and reports reducing exon-overlap contamination from
> over 40% to roughly 5%, while still reporting **r = 0.987 subfamily-level concordance with
> TEtranscripts**. That concordance is why the subfamily conclusions here are not expected
> to be quantifier-dependent, and the experiment that would confirm it is specified in
> `QUANTIFIER_ROBUSTNESS.md`, pre-registered, and deliberately not yet run.

The pre-registration includes a retract-if-sign-flips row. That is the strongest available
answer, and it is stronger than a benchmark we could have rushed.

---

## 3. TE atlases already exist — this is the correction that matters most

The first prior-art pass did not look for TE expression atlases, and it should have. They
exist and they are large:

- **[V]** **TE-SCALE** — [10.1093/nar/gkaf1235](https://doi.org/10.1093/nar/gkaf1235)
  (PMID 41296555, *NAR* 2026). Abstract confirms **1.3 million cells, 330 samples,
  20 cancer types**, with TE–gene co-expression functionality.
- **[V]** **TEITbase** — [10.1093/database/baag025](https://doi.org/10.1093/database/baag025)
  (PMID 42153345, *Database* 2026). TE-**initiated** transcripts across **33 cancer types**.
  (Note: same group as the 16-tool benchmark — Zhang Y, She J, … Yang E.)
- **[V]** **REdiscoverTE** across TCGA — [10.1038/s41467-019-13035-2](https://doi.org/10.1038/s41467-019-13035-2).
  Abstract confirms **over 400 TE subfamilies** altered in tumours, linked to immune
  infiltration and antigenicity.
- **[V]** **ERVmap** — locus-level human ERV expression,
  [10.1073/pnas.1814589115](https://doi.org/10.1073/pnas.1814589115).
- **[V]** **Pan-cancer LINE-1 activity model** with explicit locus heterogeneity —
  [10.1038/s41467-025-57271-1](https://doi.org/10.1038/s41467-025-57271-1) (PMID 40021663).

**Consequence for positioning.** The project must not be described as *the* TE atlas — the
audit (`tests/audit_claims.py`) bans that phrasing, and this is now the reason why. The
distinction that survives is about the **question the atlas answers**:

| | Question answered | Axis |
|---|---|---|
| TE-SCALE, TEITbase, REdiscoverTE, ERVmap | **Where** are TEs active — which tissue, tumour, cell | descriptive, observational |
| this project | **What perturbation changed them**, through what mechanism, and what to test next | perturbational, interventional |

That is a real distinction and it is defensible. An observational atlas of TE expression
across tumours and a perturbational map of which host genes control TEs are different
objects; neither substitutes for the other. But the sentence must be *"a perturbational map,
which existing TE atlases are not"* — not *"the first TE atlas"*.

---

## 4. TE networks and graphs also exist

`PRIOR_ART.md` had narrowed the original claim to "major general-purpose biomedical
knowledge graphs do not model TEs as first-class entities", with **ICEO** (bacterial mobile
elements, [10.1038/s41597-021-01112-5](https://doi.org/10.1038/s41597-021-01112-5)) as the
nearest structural precedent. The review supplies two more precedents, both closer in
subject matter than ICEO:

- **[V]** **PlaNC-TE** — [10.1093/database/bay078](https://doi.org/10.1093/database/bay078)
  (PMID 30101318). A knowledgebase of relationships between non-coding RNAs and TEs **in
  plants**. Explicitly a TE-relationship knowledgebase; different kingdom, no perturbational
  or mechanistic reasoning layer.
- **[V]** **TEKRABber** — [10.7554/elife.103608](https://doi.org/10.7554/elife.103608)
  (PMID 40928843, *eLife* 2025). Builds **TE–KRAB-ZFP interaction networks** across human
  brain evolution. This is the closest thing to a TE regulatory network found to date: it is
  a network, of TEs, with host regulators. It is correlation-derived across species rather
  than perturbation-derived, and it has no evidence-tier or proof layer — but anyone claiming
  "nobody builds TE networks" should be shown this paper.

The general-purpose graphs the narrowed claim refers to, now with identifiers:

| Graph | Reference | Node types |
|---|---|---|
| PrimeKG | **[V]** [10.1038/s41597-023-01960-3](https://doi.org/10.1038/s41597-023-01960-3) (PMID 36732524) | 10 principal types; gene/protein, disease, drug, pathway, anatomy, GO, phenotype, exposure |
| Hetionet | **[V]** [10.7554/elife.26726](https://doi.org/10.7554/elife.26726) (PMID 28936969) | 11 metanode types |
| DRKG | **[NF]** as a primary paper | genes, compounds, diseases, pathways, symptoms, side effects |

None of the three has a TE family or TE locus node type. That statement is checkable from
their published schemas and it is the version of the claim that is safe to make. The
banned phrasing and the approved phrasing are both recorded in `CLAIMS.md` D1.

---

## 5. Perturbation prediction: GEARS, TxPert, scPerturb

`PRIOR_ART.md` already treats **TxPert** (*Nat Biotechnol* 2026,
[10.1038/s41587-026-03113-4](https://doi.org/10.1038/s41587-026-03113-4), PMID 42067667) as
the nearest competitor. The review adds its predecessor and the data resource:

- **[V]** **GEARS** — Roohani et al., *Nat Biotechnol* 2023,
  [10.1038/s41587-023-01905-6](https://doi.org/10.1038/s41587-023-01905-6) (PMID 37592036),
  "Predicting transcriptional outcomes of novel multigene perturbations with GEARS". A
  gene–gene knowledge graph plus a graph neural network, predicting responses to unseen
  single and combinatorial perturbations. **This is the paper a machine-learning judge is
  most likely to know.**
- **[V]** **scPerturb** — *Nat Methods* 2024,
  [10.1038/s41592-023-02144-y](https://doi.org/10.1038/s41592-023-02144-y) (PMID 38279009),
  harmonised single-cell perturbation datasets. Relevant because it is the obvious substrate
  for scaling this project beyond ENCODE.

**Why these are not this project, stated carefully.** Their output space is conventional
gene expression. Neither models TE families or loci as the predicted variable, and neither
emits an inspectable derivation. But the gap is **closable, not closed**: TxPert or GEARS
trained on a TE-aware count matrix would be a strong competitor, and the honest framing —
already adopted in `CLAIMS.md` — is that the rule engine is a **bootstrap** for the low-data
regime, not a permanent claim that symbolic reasoning beats learning. At 3 measured
perturbations, rules with proofs are the defensible choice; at 500, a learned model becomes
possible and the two should coexist.

One point of independent validation worth knowing: the review reports that TxPert also
emphasises batch-matched controls. This project found the same thing empirically and
painfully — the non-targeting control and the CRISPR control in ENCODE K562 split on ISG
score (+0.71 versus −0.84), which is why every comparison here is contrast-internal.
Arriving at a published design principle from a bug is a good sign about the engineering,
and it is worth saying out loud.

---

## 6. Commercial precedent: ROME Therapeutics and the others

The first prior-art pass searched the literature and **not the commercial landscape**. That
was a real gap, and it is the kind of gap that produces an embarrassing question from a
judge who happens to know the field.

### 6.1 ROME Therapeutics — the closest industrial precedent

ROME built a company around the repeat genome, under the name **repeatomics**. Its published
science is verifiable and substantial:

- **[V]** Structures of the human LINE-1 ORF2 protein — *Nature* 2024,
  [10.1038/s41586-023-06947-z](https://doi.org/10.1038/s41586-023-06947-z) (PMID 38096902).
  Reverse transcriptase structure, the basis for pharmacological inhibition.
- **[V]** Pan-cancer multi-omic model of LINE-1 activity with locus heterogeneity of
  retrotransposition efficiency — *Nat Commun* 2025,
  [10.1038/s41467-025-57271-1](https://doi.org/10.1038/s41467-025-57271-1) (PMID 40021663).
- **[V]** Genome-wide CRISPR screening for LINE-1 regulators —
  [10.1186/s13100-025-00386-5](https://doi.org/10.1186/s13100-025-00386-5), already in
  `PRIOR_ART.md` as the retraction of the "nobody has systematically perturbed" claim.

**[U]** The rest of the ROME picture — a proprietary annotated repeat reference, a
machine-learning repeat-expression quantification tool, LINE-1 reverse-transcriptase
inhibitors in autoimmune and neurodegenerative programmes, and the corporate outcome
(standalone operations wound down; reported as continuing as a wholly owned subsidiary of
Pretzel Therapeutics) — comes from company and press material that cannot be reached from
this environment. Report it as second-hand.

**How to speak about ROME.** With respect, and without a comparison that invites ridicule:

> ROME Therapeutics is the closest industrial precedent. They had more proprietary
> experimental biology and far more drug-development depth than this project — they solved
> the ORF2p structure and built inhibitors. What I have not found in their public work is
> this specific architecture: arbitrary public perturbation datasets re-analysed against the
> repeat genome, converted into signed provenance-bearing edges in a common evidence schema,
> reasoned over with inspectable rules that separate measurement from inference.

And if asked why they wound down: **a company closing does not establish that the science
failed.** That is the only correct answer, and it is also true.

### 6.2 The others

**[U] — all of the following are reported from the review and not independently verified
here.** The sandbox reaches literature databases, not company websites. Treat as a map of
who to search for, not as facts.

| Company | Reported activity | Competitive distance |
|---|---|---|
| **ROME** | repeatome analytics + LINE-1 biology + therapeutics | closest |
| **Nexco / TEnex** | TE family/subfamily/locus quantification, TE–gene annotation, ML biomarkers | computationally closest |
| **HERVolution** | HERV-targeted immune therapeutics | biologically adjacent |
| **Enara Bio** | dark-genome-derived tumour antigens, proteomics + computation | adjacent |
| **HAYA** | causal regulatory-genome atlas, RNA medicines | platform analogue, not TE-specific |
| **Repeat Therapeutics** | C9orf72 repeat-expansion ALS | **not a TE competitor** despite the name |

If a judge names one of these, the correct response is "I know of them, I have not
independently verified what their platform does" — not a confident comparison.

---

## 7. Disease evidence, by strength

Useful for answering "so what?" without overclaiming.

**Cancer — strongest.** TE deregulation through hypomethylation and chromatin change;
TE-derived regulatory elements, dsRNA, antigens. **[V]** REdiscoverTE: over 400 TE
subfamilies altered across tumours with immune-infiltration and antigenicity associations
([10.1038/s41467-019-13035-2](https://doi.org/10.1038/s41467-019-13035-2)). **[V]** Griffin
et al., *Nature* 2021, [10.1038/s41586-021-03520-4](https://doi.org/10.1038/s41586-021-03520-4)
(PMID 33953401): SETDB1 silencing suppresses tumour intrinsic immunogenicity — causal
evidence linking epigenetic TE repression to immune escape, and directly relevant because
SETDB1 is one of our three measured knockdowns.

**Viral mimicry — strong, and the reason our caveat chain exists.** **[V]** Two 2015 *Cell*
papers established that DNA-demethylating agents induce ERV/dsRNA expression and antiviral
signalling: Roulois et al., [10.1016/j.cell.2015.07.056](https://doi.org/10.1016/j.cell.2015.07.056)
(PMID 26317465) and Chiappinelli et al.,
[10.1016/j.cell.2015.07.011](https://doi.org/10.1016/j.cell.2015.07.011) (PMID 26317466).
**[V]** HUSH-mediated silencing of intronless mobile elements: Seczynska et al., *Nature*
2022, [10.1038/s41586-021-04228-1](https://doi.org/10.1038/s41586-021-04228-1)
(PMID 34794168).

**Ageing — strong and increasingly causal.** De Cecco et al.,
[10.1038/s41586-018-0784-9](https://doi.org/10.1038/s41586-018-0784-9) (L1 → interferon in
senescence). And the complication already logged in `CRITIQUE.md`: cGAS has a nuclear role
maintaining H3K9me3 (*Nature Aging* 2026,
[10.1038/s43587-026-01206-y](https://doi.org/10.1038/s43587-026-01206-y), PMID 42642519), so
cGAS is not only a downstream sensor and the TE → sensor → inflammation path **is not
guaranteed to be acyclic**. This is an open structural issue in the schema, not a patched one.

**Haematopoietic — directly relevant to the worked example.** **[V]** Silencing of LINE-1
retrotransposons is a selective dependency of myeloid leukaemia (MPP8/HUSH), *Nat Genet*
2021, [10.1038/s41588-021-00829-8](https://doi.org/10.1038/s41588-021-00829-8)
(PMID 33833453). **[V]** A locus-specific TE preprint in VEXAS claims CRISPRi against two L1
loci reverses disease-associated HSC phenotypes
([10.64898/2026.07.31.742092](https://doi.org/10.64898/2026.07.31.742092)) — preprint, cite
as such, but it is the clearest illustration of why locus resolution may eventually matter
here.

**Autoimmune, neurodegeneration.** Association and mechanism both present, heterogeneous
across conditions; ERVmap identified disease-associated ERV loci in SLE
([10.1073/pnas.1814589115](https://doi.org/10.1073/pnas.1814589115)). Locus-specific tools
should help. No claim made here.

---

## 8. What survives, after both attacks

Two independent adversarial passes have now been run against the positioning: the internal
prior-art gate (2026-09-20, `PRIOR_ART.md`) and this external review (2026-09-22). The
combined verdict:

| Area | Novelty | Why |
|---|---|---|
| TE biology | none | mature field; SETDB1 and TRIM28 are positive controls, not discoveries |
| TE quantification | none | TEtranscripts, and 15 other tools benchmarked |
| subfamily differential expression | none | standard capability |
| set-level compartment test | some | related ideas exist (CAMERA, GSEA, aggregate TE readouts); the normalisation-invariance framing survived scoped |
| TE nodes in a graph | some | unusual in general-purpose biomedical KGs; TE networks exist (TEKRABber, PlaNC-TE) |
| provenance schema | some | not conceptually new; unusually central here |
| **signed perturbation edges** | **strong** | directly usable for mechanistic reasoning |
| **measured + curated + literature + inferred in one graph** | **strong** | pieces found, no close integrated precedent |
| **inspectable TE mechanism reasoning** | **strong** | comparable systems predict with ML instead |
| **proof trees** | **strong** | scientifically the most valuable part |
| **re-mining public perturbation data for TE phenotypes** | **strong** | potentially the largest scalable contribution |
| **refusing when evidence is insufficient** | **strong** | and it is the part that matches Claude Science's design goals |
| perturbational TE atlas at scale | **potentially very strong** | if actually built; today it is 3 genes |

The positioning sentence that survives both attacks is the one already in `CLAIMS.md`:

> An evidence-traceable perturbational reasoning system for transposable-element regulation.

And the longer object, which is the one worth being ambitious about:

> **The perturbational map of the repetitive genome.** Rows = gene perturbations.
> Columns = TE subfamilies, eventually loci. Layers = cell type, modality, time point,
> chromatin context. Today: 3 rows.

---

## 9. Verification ledger

Every checkable assertion in the external review, searched on **2026-09-22** against PubMed
(E-utilities) and Europe PMC REST.

**Verified — 29.** Ho *Cell* 2026 review · CELLO-seq + protocol · long-read locus annotation
(2,596 / 21 / 71 all confirmed) · TEsingle · TEscape · 16-tool benchmark (She et al.,
"16 representative tools" confirmed) · REdiscoverTE (over 400 subfamilies confirmed) ·
ERVmap · TE-SCALE (1.3 M cells / 330 samples / 20 cancer types confirmed) · TEITbase
(33 cancer types) · PlaNC-TE · TEKRABber · PrimeKG · Hetionet · GEARS · scPerturb ·
456 cell-type–histone–TE triplets · Seczynska HUSH · MPP8 myeloid dependency · Griffin
SETDB1 · Roulois · Chiappinelli · ORF2p structures · pan-cancer L1 locus heterogeneity ·
VEXAS L1 preprint · Scheller DNMT3A/azacitidine · ASXL1-BAP1-EHMT · TxPert · MAJEC ·
Hasan et al. *GeroScience* 2026 (verified late — see §10).

**Initially recorded as not found — 1, wrongly.** The *GeroScience* DNMT3A/TET2 paper was
found after the correction: [10.1007/s11357-026-02510-6](https://doi.org/10.1007/s11357-026-02510-6),
PMID 42744964. The searches failed on vocabulary, not on the index. **§10 is the full
correction and the lesson is not the one §9 originally implied.**

**Unverifiable here — 6.** All corporate: ROME's platform description and corporate
outcome, Nexco/TEnex, HERVolution, Enara Bio, HAYA, Repeat Therapeutics.

**Also not located:** a primary methods paper for **TElocal** (the tool exists; no separate
publication found), and **DRKG** as a primary citation (referenced in many downstream papers).

---

## 10. The claim I got wrong, and what it cost

**Read this section before quoting §9 at anyone.** The first version of it was confidently
wrong, and the correction is more instructive than the original point.

### 10.1 What I wrote, and what was actually true

The external review stated that the DNMT3A/TET2 interest "has just received direct support
from a September 16, 2026 *GeroScience* article comparing retroelement deregulation in those
two CH genotypes." I searched five ways, found nothing, recorded it as `[NF]`, and wrote a
section observing that the one claim most favourable to the project was the one that did not
resolve — with the implication that a generative system had produced a flattering citation.

**The paper exists.** The author of this project supplied the PDF.

> **Hasan M, Durandeau S, Thompson IR, Roussotte H, Tsai Y-T, Seymen N, Gerlevik S,
> Bianchini N, Alishah K, Albuquerque MM, Lewis J, Bonganay L, Jakobsen NA, Zeisig B,
> Irshad S, Vyas P, So ECW, Iacoangeli A, Zheng X, Mackie S, Mok KY, Uksaite V,
> Handfield L-F, Napolitani G, Carmichael J, Mufti GJ, Gandhi AK, Suragani RNVS, Quek L,
> Karimi MM.** "Retrotransposable element derepression distinguishes DNMT3A-mutant from
> TET2-mutant clonal haematopoiesis." *GeroScience*, published **16 September 2026**.
> [10.1007/s11357-026-02510-6](https://doi.org/10.1007/s11357-026-02510-6) ·
> **PMID 42744964** · CC-BY.

The review's date was exact. The journal was exact. The subject was exact. Crossref resolves
the DOI, and **PubMed had already indexed it** — a search on the DOI returns PMID 42744964.
Nothing was lagging. The index had it and I did not find it.

### 10.2 Why the search failed, precisely

Not indexing latency. **Vocabulary.** The paper's title says *retrotransposable element*;
every query I ran said `retroelement` or `retrotransposon`. And the paper uses the British
*haematopoiesis*; one of my queries used the American *hematopoiesis*, which returned zero.

Run afterwards against the same PubMed:

| Query | Hits |
|---|---|
| `GeroScience retroelement` | 4 — none of them this paper |
| `DNMT3A TET2 retroelement` | 2 — unrelated |
| `retroelement deregulation clonal hematopoiesis` | **0** |
| `retrotransposable element clonal haematopoiesis` | **1 — PMID 42744964** |
| `retrotransposable DNMT3A TET2` | **1 — PMID 42744964** |
| `(retroelement OR retrotransposon OR retrotransposable) AND DNMT3A AND TET2` | **4, including it** |

Any one of the last three would have found it in a single call. The searches that failed
failed on a synonym and a vowel.

### 10.3 This is the same failure already recorded at the top of `PRIOR_ART.md`

That document opens with a methodological confession: a full-text pass used Europe PMC's
`FULL_TEXT:` field, which is not a valid field name and fails **silently**, returning zero
for five queries. Five "no precedent found" verdicts were an artefact of a typo. The lesson
recorded there was:

> A novelty claim is cheapest to "prove" with a broken search. Any future search should
> validate its syntax against a query expected to return many hits before trusting a zero.

**I then made the same class of error in the opposite direction** — and this time the broken
search did not manufacture novelty, it manufactured a *retraction* and an accusation. A
search returning zero because of the words you chose is not evidence about the world. It was
already written down. I did not apply it.

### 10.4 The corrected lesson, which is not the one I drew

The original section drew a satisfying moral: verify flattering citations, because
plausible-and-flattering is the dangerous combination. That is still true and it is still
why the citation gate exists. But it was the wrong lesson to draw *from this episode*,
because the flattering citation was **correct** and my verification was what failed.

Three things are true at once, and the order matters:

1. **Checking was right.** A claim with no resolvable identifier cannot go into a document
   that carries a citation gate. Nothing about this episode argues for accepting unsourced
   citations.
2. **Recording it as `[NF]` was right.** The verdict vocabulary exists precisely for
   "we did not locate this", and `NOT_FOUND_IN_PRIOR_ART_SEARCH` is defined in `CLAIMS.md`
   as *not located by this search*, never *does not exist*.
3. **The narrative built on top of it was wrong.** I treated a null from three
   badly-worded queries as strong enough to support a story about the reviewer's
   reliability. A null that weak supports no story at all. The failure was not the
   verification, it was the **confidence attached to a negative result** — which is the
   single most common way a literature search misleads, and the thing this repository
   claims to be careful about.

And a fourth, which is the practical one: **the cheapest way to resolve a citation about
your own field is to ask the person who works in it.** The author was in the conversation
the entire time. One question would have cost a sentence and saved a wrong section.

### 10.5 What the paper actually reports

Details in `HYPOTHESIS_DNMT3A_TET2.md` §8; in brief, and note that it is **not**
independent of this project — the project's author is the fourth of thirty authors, so this
is the *source* of the hypothesis, not confirmation of it:

- **Cohort.** 68 PBMC samples from a healthy-ageing cohort: DNMT3A high-VAF (>10%) n = 10,
  DNMT3A low-VAF n = 30, DNMT3A/TET2 double-mutant n = 9, TET2-mutant n = 7, non-CH control
  n = 12. Total RNA-seq, mean 65.1 M reads per sample.
- **DNMT3A high-VAF:** widespread RTE derepression, dominated by **LINE:L1 and
  LTR:ERV1/ERVL**, with TNF-α/NF-κB, interferon and senescence enrichment in the RTE-high
  subgroup — and marked heterogeneity, including the R882H hotspot clustering with *low*
  RTE expression while PWWP-domain mutations were exclusively RTE-high.
- **TET2-mutant:** a **non-significant trend toward reduced** RTE expression versus controls,
  no RTE-associated inflammatory signature, and enrichment of oxidative phosphorylation, ROS
  and mTORC1 instead — inflammation by a metabolic/redox route rather than a retroelement one.
- Reproduced in TARGET-seq across haematopoietic lineages and in an independent cohort
  (GSE263013).

**One finding deserves attention here rather than in the hypothesis document:** the
RTE-high DNMT3A high-VAF clones were enriched for **HUSH-mediated silencing** and SIRT1
pathways, read as a compensatory response. HUSH (MPHOSPH8/TASOR/PPHLN1) is already a
complex in this graph, and R4_COMPLEX_CONSENSUS operates over it. That is a concrete,
testable point of contact between the paper and the graph, and it was not in either document
before.

### 10.6 The methodological contrast, which is genuinely useful

The paper and this project measure the same biology with almost no shared machinery:

| | Hasan et al. 2026 | this project |
|---|---|---|
| System | primary human PBMCs, 68 donors | K562, 3 knockdowns |
| Perturbation | naturally occurring somatic mutation | CRISPR/CRISPRi knockdown |
| Quantifier | **featureCounts** over RepeatMasker regions | **TEcount** (TEtranscripts EM) |
| Resolution | class and family (9 families) | **subfamily** (1,057) |
| Statistics | DESeq2, ~Batch+Sex+Age+Group, raw *p* | DESeq2 + a set-level compartment test |

Different quantifier, different resolution, different perturbation modality, different
tissue. Where the two agree on a direction, that agreement is not methodological
coincidence — and where this project chose subfamily resolution over family, the paper is a
concrete example of the family-level analysis whose power cost was measured in
`aggregation_level_comparison.csv`.
