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
matter: **29 claims verified, one not found, and six unverifiable from here.** The one that
could not be found is the one most favourable to this project's hypothesis (§10).

That is the whole method, and it is worth stating plainly: an external review is evidence,
not authority. It gets checked like anything else.

---

## 0. How to read the verification tags

Every claim in this document carries one:

| Tag | Meaning |
|---|---|
| **[V]** | Verified here — the paper exists, the identifier resolves, and the specific number quoted was found in the abstract |
| **[V-ref]** | The paper is verified but a number attributed to it was not checked against its abstract |
| **[NF]** | Searched for and **not found**. Not "false" — not located by PubMed + Europe PMC on 2026-09-22 |
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
VEXAS L1 preprint · Scheller DNMT3A/azacitidine · ASXL1-BAP1-EHMT · TxPert · MAJEC.

**Not found — 1.** See §10.

**Unverifiable here — 6.** All corporate: ROME's platform description and corporate
outcome, Nexco/TEnex, HERVolution, Enara Bio, HAYA, Repeat Therapeutics.

**Also not located:** a primary methods paper for **TElocal** (the tool exists; no separate
publication found), and **DRKG** as a primary citation (referenced in many downstream papers).

---

## 10. The claim that did not survive verification

The review states that the DNMT3A/TET2 interest "has just received direct support from a
September 16, 2026 GeroScience article comparing retroelement deregulation in those two CH
genotypes."

**[NF] This paper was not found.** Searched on 2026-09-22:

| Search | Result |
|---|---|
| PubMed `GeroScience retroelement` | 4 hits — canine LINE-1 methylation with age (2026-07), Alu overexpression in fibroblasts (2025-12), 2 older |
| PubMed `GeroScience transposable element` | 3 hits — TE dysregulation in cognitive impairment/AD (2025-08), unrelated |
| PubMed `DNMT3A TET2 retroelement` | 2 hits — LINE-1 methylation in vapers/smokers; bovine placental ERV |
| PubMed `retroelement deregulation clonal hematopoiesis` | 0 hits |
| Europe PMC `DNMT3A AND TET2 AND (retroelement OR retrotransposon) AND 2026` | 33 hits, none matching |

**This is the claim in the entire review most favourable to this project's hypothesis, and
it is the one that does not resolve.** That ordering is not a coincidence worth ignoring —
it is exactly why the citation gate exists, and exactly why an external review gets checked
rather than believed. If the paper exists under a title these searches missed, it can be
added; until an identifier resolves, **it must not be cited, and the hypothesis must not be
described as having recent direct support.**

### 10.1 What was found instead, and it is genuinely useful

Two real papers, both verified, both relevant to the DNMT3A/TET2 worked example:

- **[V]** **Scheller et al., *Nature Cancer* 2021** —
  [10.1038/s43018-021-00213-9](https://doi.org/10.1038/s43018-021-00213-9) (PMID 35122024).
  "Hotspot DNMT3A mutations in clonal hematopoiesis and acute myeloid leukemia sensitize
  cells to azacytidine **via viral mimicry response**." This is direct, peer-reviewed,
  DNMT3A-mutant-CH-specific evidence that the DNMT3A lesion connects to viral mimicry. It
  supports the *DNMT3A* arm of the hypothesis in `HYPOTHESIS_DNMT3A_TET2.md` — not the
  contrast with TET2, and not via a measurement made here, but it is the closest real
  support that exists and it was not in the prior-art table.
- **[V]** **ASXL1-BAP1-EHMT complex → heterochromatin dysfunction in clonal haematopoiesis**
  — *PNAS* 2025, [10.1073/pnas.2413302121](https://doi.org/10.1073/pnas.2413302121)
  (PMID 39752521). A different CH driver converging on heterochromatin. ASXL1 is already in
  the CH gene set; this is a second mechanistic entry point into the same axis and a natural
  next perturbation target.

The net effect of the verification pass is therefore **better** than the review's own claim:
one unverifiable supporting paper was removed, and two verifiable ones were added — one of
which is specifically about DNMT3A-mutant clonal haematopoiesis and viral mimicry.
