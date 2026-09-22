# Claim registry

Every externally presentable scientific claim this project makes, with a status, the
approved public wording, and the wording that is **not** to be used. Nothing goes on a
slide, in an abstract, into a README or out of anyone's mouth in a demo unless it appears
here. This is the single source of truth for what can safely be said.

> **Adversarial novelty rule.** Treat every novelty claim as unproven until the strongest
> available prior art has been identified and compared against it. The objective is not to
> preserve the project's existing positioning. Narrow, qualify or remove claims whenever
> the literature requires it. "Not found" claims must always state the databases searched,
> the search strategy and the search date; absence from a literature search must never be
> converted into "nobody has done this."

> **Absence of evidence from a literature search is weak evidence of absence.** Every
> `NOT_FOUND_IN_PRIOR_ART_SEARCH` below is scoped to the databases, queries and date used
> — see `PRIOR_ART.md` and `data/graph/prior_art.csv`. It means *we did not locate a
> precedent*, never *no precedent exists*.

**Claim types.** `field fact` (established biology or methodology, we cite it) ·
`project result` (measured in this build) · `inference` (derived by a rule) ·
`novelty claim` (an assertion about what is new).

**Search scope for all `NOT_FOUND` verdicts:** PubMed (connector) and Europe PMC REST
body-text search over the open-access subset, plus one web search for a preprint tool;
searched **2026-09-20**; 279 abstracts screened and 198 open-access full texts read at
sentence level. A negative here means *not located by this search*, never *does not exist*.

**Second, independent pass — 2026-09-22.** The completed project was reviewed by a separate
deep-research system asked to attack the positioning, and every factual assertion it made
was then re-searched from scratch against PubMed and Europe PMC because its own citations
carried no resolvable identifiers: **29 verified, 1 not found, 6 unverifiable from this
environment.** It found two categories the first pass never searched — existing TE atlases
and the commercial landscape — which produced D13–D17. See `LANDSCAPE.md` and
`PRIOR_ART.md` § "Second pass".

## Status vocabulary

| Status | Meaning |
|---|---|
| `ESTABLISHED` | Published and accepted; we cite it, we did not find it |
| `SUPPORTED_BY_THIS_BUILD` | We measured it in this project from raw data |
| `INFERRED` | Derived by a rule from other edges; a prediction, not a result |
| `HYPOTHESIS` | Proposed, not tested here |
| `NOT_TESTED` | Within scope but deliberately not attempted, or attempted and refused |
| `NOT_FOUND_IN_PRIOR_ART_SEARCH` | We looked for a precedent and did not locate one |
| `RETRACTED_BY_US` | We previously stated this and it is wrong |

---

---

## 0. Approved wording — the table to read before speaking

For the claims that are easy to overstate. Left column is sayable; right column is not.

| # | Say this | Do **not** say |
|---|---|---|
| W1 | "Major general-purpose biomedical knowledge graphs — PrimeKG, Hetionet, Open Targets — don't model TE families or loci as first-class entities." | "No public knowledge graph has TEs." |
| W2 | "We re-analyse perturbation experiments for TE effects their authors didn't measure." | "Nobody has systematically perturbed genes to find TE regulators." |
| W3 | "We use TEcount from TEtranscripts; Telescope, SQuIRE and MAJEC are alternatives we haven't benchmarked." | "We built a TE quantification method." / "our quantifier" |
| W4 | "The set-level test is standard competitive gene-set testing; what we did not find in the literature is the normalisation-invariance argument for using it as the primary TE readout." | "We invented a normalisation-invariant statistic." |
| W5 | "The engine **predicts** TET2 loss lowers TEs — a mechanistic hypothesis, here is the proof tree." | "The engine shows / proves / derives causally that TET2 derepresses TEs." |
| W6 | "In K562, TE derepression is not accompanied by an interferon response, and the sensors aren't expressed — this dataset can't test viral mimicry." | "TE derepression does not cause interferon." |
| W7 | "Predicted from a DNMT1 knockdown in K562; asserting it in another cell type is a further inference." | "DNMT3A silences transposable elements." (unqualified) |
| W8 | "A perturbational TE atlas is the long-term object; this is an architecture with a worked example." | "This is the TE atlas." |
| W9 | "TxPert plus a TE-aware expression matrix would be a strong competitor — a closable gap." | "Nothing else can do this." |
| W10 | "cGAS also acts upstream in chromatin control, so this path has feedback and our drawing is a simplification." | "TE derepression → cGAS → interferon" as a settled directed pathway. |
| W11 | "Three components were built, measured and not shipped." | Any mention of link prediction as a feature. |
| W12 | "TE atlases exist and are large — TE-SCALE, TEITbase, REdiscoverTE. They answer *where* TEs are active; we ask *what perturbation changed them*." | "There's no TE atlas." / "the first TE atlas" |
| W13 | "ROME Therapeutics is the closest industrial precedent and was ahead of us on biology — they solved the ORF2p structure. What I haven't found in their public work is this architecture." | Any comparison implying we have more depth than ROME, or that its closure means the science failed. |
| W14 | "We work at subfamily level because aggregating upward measurably loses signal; the field is moving to loci and the ontology is split to permit it." | "Subfamily is the right level." / any implication `TELocus` exists as a node type. |
| W16 | "The compartment effect size is Δ = +0.13 for DNMT1, consistent across every feature class and stable to dropping any library. The correlation-aware p is 0.045 — our original Mann–Whitney p was anti-conservative because TE features aren't independent, and we measured the inflation at 4×." | Any Mann–Whitney p-value for a compartment effect: 1.6 × 10⁻⁸, 3.5 × 10⁻¹⁵, 2.3 × 10⁻²¹. All retracted as evidence. |
| W17 | "With two replicates per arm the permutation floor is p = 0.333, so no sample-level test can reach significance in this design. That's a limitation of the experiment, not of the analysis." | Any small sample-level p-value from an n = 2 design. |
| W15 | "The hypothesis is published — Hasan et al., *GeroScience* 2026, 10.1007/s11357-026-02510-6, and I'm a co-author, so this project instruments my own prior finding rather than confirming it." | "An independent paper confirms our prediction." (You are the 4th of 30 authors. It is the source, not confirmation.) |

---

## A. Claims about what exists in the world

| # | Claim | Status | Evidence |
|---|---|---|---|
| A1 | Roughly half the human genome is repeat-derived; hg38 RepeatMasker yields 3,761,678 filtered TE copies across 1,057 subfamilies after our filters | `SUPPORTED_BY_THIS_BUILD` | `te_subfamilies_hg38.csv`; filters in `build_te_annotation.py` |
| A2 | L1 activation drives an interferon response in senescent cells and age-associated inflammation | `ESTABLISHED` | De Cecco et al., Nature, 10.1038/s41586-018-0784-9 |
| A3 | cGAS has a role upstream of TE control, not only downstream as a sensor: cGAS-deficient mice show LINE-1 derepression and inflammatory ageing | `ESTABLISHED` | Nat Aging 2026, 10.1038/s43587-026-01206-y |
| A4 | Neither DNMT3A nor TET2 has a knockdown RNA-seq experiment in ENCODE | `SUPPORTED_BY_THIS_BUILD` | `encode_kd_inventory.csv`, 1,114 experiments / 570 targets |
| A5 | TET2 is not annotated to any GO transposition or TE-silencing term | `SUPPORTED_BY_THIS_BUILD` | QuickGO query in `build_graph.py` |
| A6 | Hotspot DNMT3A mutations in clonal haematopoiesis and AML sensitise cells to azacytidine via a viral mimicry response | `ESTABLISHED` | Scheller et al., Nat Cancer 2021, 10.1038/s43018-021-00213-9 (PMID 35122024). The closest real support for the DNMT3A arm of C3; says nothing about the TET2 contrast |
| A7 | TE regulation is strongly cell-type-specific: 456 cell-type–histone–TE triplets show strong cell-type-specific enrichment | `ESTABLISHED` | Hyacinthe & Bourque, Nat Commun 2026, 10.1038/s41467-026-74920-1. Note the unit is *triplets* |
| A8 | Silencing of LINE-1 is a selective dependency of myeloid leukaemia (MPP8/HUSH) | `ESTABLISHED` | Nat Genet 2021, 10.1038/s41588-021-00829-8 |
| B3 | SETDB1 knockdown efficiency is confirmed in this data | `NOT_CONFIRMED` | SETDB1's own mRNA change in its knockdown is −0.35 log₂ (78% remaining), padj 0.77 — **not significant**, while TRIM28 (−1.12, 46% remaining, padj 8.6e-12) and DNMT1 (−1.87, 27% remaining, padj 1.0e-18) are both confirmed in the same data. Counter-evidence that the perturbation did something: the two HERV results. Correct reading is *not confirmed*, not *failed*. SETDB1 is the sole H3K9me3 anchor (3 of 4 `MARK_AT` edges), so this is the highest-consequence unconfirmed item in the project. `results/knockdown_efficiency.csv` |
| A9 | In human CH, DNMT3A high-VAF clones show widespread RTE derepression (LINE:L1, LTR:ERV1/ERVL) with TNF-α/NF-κB, interferon and senescence enrichment, whereas TET2-mutant clones trend toward *reduced* RTE expression and show inflammation via oxidative phosphorylation/ROS/mTORC1 instead | `ESTABLISHED (AUTHOR CONFLICT)` | **Hasan et al., GeroScience 2026, 10.1007/s11357-026-02510-6, PMID 42744964.** 68 PBMC samples; featureCounts over RepeatMasker at class/family level; reproduced by TARGET-seq and in GSE263013. **This project's author is the 4th of 30 authors — this is the source of C3, not independent confirmation of it.** The TET2 trend is non-significant vs controls (n=7) |

## B. Claims about our measurements

| # | Claim | Status | Evidence |
|---|---|---|---|
| B1 | TRIM28 knockdown shifts the whole TE compartment | `DOWNGRADED — EFFECT SIZE ONLY` | Δ = +0.42, 73% of features up, same sign in 6/6 feature-set variants. **Sample-level evidence does not support it:** a permuted labelling produced a *larger* Δ (0.68) than observed, sign not preserved under leave-one-library-out (−0.02..+1.12), correlation-aware p = 0.44 (ρ̄ = 0.48, VIF = 155, ~2 effective independent features). The Mann–Whitney p = 3.5 × 10⁻¹⁵ is **retracted as evidence**. See `COMPARTMENT_STATISTICS.md`. TRIM28's *per-feature* hits (AluY padj 0.0005) are a different statistic and stand |
| B2 | DNMT1 knockdown derepresses the TE compartment with **no** single subfamily at FDR < 0.1 | `SUPPORTED_BY_THIS_BUILD (restated)` | Δ = +0.13, 63% of 503 features up, same sign in **6/6** feature-set variants (LINE +0.19, SINE +0.10, LTR +0.11, DNA +0.10), leave-one-library-out +0.10..+0.19 with sign preserved 4/4, most extreme of 3 admissible labellings by 3.7×, **correlation-aware p = 0.045** (ρ̄ = 0.006, VIF = 4.1). Mann–Whitney p = 1.6 × 10⁻⁸ retracted as anti-conservative. Best per-feature padj 0.41. **This is the 5mC anchor and it holds** |
| B3 | SETDB1 behaves as a targeted ERV silencer, not a global one | `SUPPORTED_BY_THIS_BUILD` | HERVE-int, HERV9NC-int move; compartment p = 0.24 |
| B4 | At 1.5 M reads on chr1+chr19, subfamily-level counting has more power than class/family aggregation | `SUPPORTED_BY_THIS_BUILD` | `aggregation_level_comparison.csv` |
| B5 | *Why* only some subfamilies respond | `NOT_TESTED` | Age explanation tested and **rejected**; see CRITIQUE §on aggregation |
| B6 | The panel-augmented reference raises type-I IFN coverage from 0.168 to 0.768 without changing existing measurements | `SUPPORTED_BY_THIS_BUILD` | `reference_perturbation.csv`, Pearson 0.992–0.996 |
| B7 | In K562, TE derepression is not accompanied by a type-I interferon response | `SUPPORTED_BY_THIS_BUILD` | 15 signature tests, none significant under Bonferroni; bootstrap CIs exclude TE-arm-magnitude effects |
| B8 | That null is explained by sensor absence, not by absence of ligand | `SUPPORTED_BY_THIS_BUILD` | `sensor_expression_k562.csv`: CGAS 0.21 CPM, ZBP1 0.26, TLR3 0.00, IFIH1 8.5, RIGI 5.4; transducers 270–800 CPM |
| B9 | Whether TE derepression causes interferon induction | `NOT_TESTED` | The cell line cannot mount the response; requires a sensing-competent system |
| B10 | Our subfamily-level results are robust to the choice of quantifier | `NOT_TESTED` | Protocol written (`QUANTIFIER_ROBUSTNESS.md`), **not run**. External support only: MAJEC reports r = 0.987 subfamily-level DE concordance with TEtranscripts |
| B11 | HISAT2 and STAR give equivalent results here | `NOT_TESTED` | Forced by a broken arm64 STAR build; open falsifier |

## C. Claims that are predictions, not findings

| # | Claim | Status | Evidence |
|---|---|---|---|
| C1 | DNMT3A silences TEs globally | `INFERRED` | R2_WRITER_TRANSFER from the DNMT1 measurement + GO:0003886 |
| C2 | TET2 loss *lowers* TE expression | `INFERRED — DIRECTION AGREES WITH A9` | R3_ERASER_INVERSION from the DNMT1 measurement + GO:0070579. The direction matches what Hasan et al. measured in TET2-mutant CH (non-significant trend to reduced RTE; significant reduction vs DNMT3A high-VAF), across a different quantifier, resolution, modality and tissue. **Not a blind prospective validation** — the hypothesis was known to this project before the rule was run, and the rule's premises are curated annotations, not that paper |
| C3 | In DNMT3A-mutant CH, TE reactivation is on the path to inflammation; in TET2-mutant CH inflammation occurs but is not TE-mediated | `PUBLISHED BY THE AUTHOR — SEE A9` | Now citable: Hasan et al., GeroScience 2026, 10.1007/s11357-026-02510-6. This project instruments the hypothesis; it does not test it, and the author's co-authorship must be disclosed whenever it is cited as support |
| C4 | The 28 structurally tractable targets with no clinical programme are actionable | `INFERRED` | Imported Open Targets/ChEMBL buckets, not computed here |

## D. Novelty and positioning claims

| # | Claim | Status | Notes |
|---|---|---|---|
| D1 | "No public knowledge graph has TEs" | `RETRACTED_BY_US` | Replaced by D2 |
| D2 | Major general-purpose human biomedical knowledge graphs (PrimeKG, Hetionet, Open Targets) do not model TE families or loci as first-class entities, making TE-specific perturbational reasoning hard to express directly | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | Schemas checked: PrimeKG 10.1038/s41597-023-01960-3 (10 node types), Hetionet 10.7554/elife.26726 (11 metanodes). **Closer precedents than ICEO now in the record:** TEKRABber builds TE–KRAB-ZFP networks (10.7554/elife.103608) and PlaNC-TE is an ncRNA–TE knowledgebase in plants (10.1093/database/bay078). "Nobody builds TE networks" would be false twice over |
| D3 | "Nobody has systematically perturbed genes to find TE regulators" | `RETRACTED_BY_US` | Flatly false — C. elegans 2003, Drosophila 2013, human L1 CRISPR screens Nature 2018, LINE-1 CRISPR 2025 |
| D4 | Re-mining perturbation experiments *run for other purposes* for TE phenotypes their authors did not measure | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | Narrow. Existing screens are prospective and TE-designed, usually reporter-based and L1-focused |
| D5 | TE quantification handling multi-mapping reads is our contribution | `RETRACTED_BY_US` | It is TEtranscripts/TEcount (10.1093/bioinformatics/btv422). Alternatives: Telescope, SQuIRE, SalmonTE, TEspeX, MATES, IRescue, MAJEC |
| D6 | Comparing a focal feature set's fold-change distribution against all other features is a new statistic | `RETRACTED_BY_US` | It is competitive gene-set testing — CAMERA (10.1093/nar/gks461), GSEA (10.1073/pnas.0506580102) |
| D7 | Aggregate/global TE expression readouts are new | `RETRACTED_BY_US` | ALS cortex subtypes with retrotransposon activation (10.1016/j.celrep.2019.09.066); aggregate intact-L1 quantification (10.1186/s13041-022-00914-x) |
| D8 | Framing the TE-vs-protein-coding set comparison as *immune to per-sample normalisation error*, and using it as the primary TE readout for that reason | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | 198 OA full texts read at sentence level; nearest hits used protein-coding genes only to *define* intergenic TEs |
| D9 | Knowledge-graph-driven prediction of perturbation responses is unexplored | `RETRACTED_BY_US` | TxPert (10.1038/s41587-026-03113-4) and at least three other KG-based perturbation predictors |
| D10 | TxPert plus a TE-aware expression matrix would be a strong competitor | `HYPOTHESIS` | TxPert's published output space is conventional transcriptomic response; it does not model TEs. The gap is closable, not closed |
| D11 | A reduced/targeted reference set is a novel idea | `RETRACTED_BY_US` | Targeted panels are routine. Our contribution is the coverage guard and the reference-perturbation control around one |
| D12 | The surviving positioning: **an evidence-traceable perturbational reasoning system for transposable-element regulation** | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | Combination claim: re-analysis of perturbation data for TE effects + signed provenance-tracked edges + mechanism rules + inspectable proof trees + explicit refusal. Each component has precedent; the assembly did not surface. **Independently re-attacked 2026-09-22** by a separate deep-research system, which also did not locate a system combining these pieces — a second `NOT_FOUND` from a different searcher, still not proof of absence |
| D13 | "This is the TE atlas" / no TE atlas exists | `RETRACTED_BY_US` | TE-SCALE (1.3 M cells / 330 samples / 20 cancer types, 10.1093/nar/gkaf1235), TEITbase (33 cancer types, 10.1093/database/baag025), REdiscoverTE (>400 subfamilies across TCGA, 10.1038/s41467-019-13035-2), ERVmap (10.1073/pnas.1814589115). Banned by `tests/audit_claims.py` |
| D14 | Existing TE atlases answer a **different question** — *where* TEs are active, not *what perturbation changed them* | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | The distinction is axis-based and defensible. It is not a claim of superiority and neither object substitutes for the other |
| D15 | Locus-level TE measurement is out of reach, or subfamily is the field's working resolution | `RETRACTED_BY_US` | CELLO-seq (10.1038/s41587-021-01093-1), locus annotation across 2,596 long-read datasets (10.1186/s44342-025-00048-1), TEsingle and TEscape preprints 2026. Our subfamily choice is a power argument at our depth, not a claim about the field |
| D16 | The choice of TE quantifier is an open question in the field | `RETRACTED_BY_US` | 16 tools benchmarked with guidelines: She J, Wang J, Yang E., 10.1093/gpbjnl/qzag044 |
| D17 | No company has built repeat-genome analytics | `RETRACTED_BY_US` | ROME Therapeutics: ORF2p structures 10.1038/s41586-023-06947-z, pan-cancer L1 model 10.1038/s41467-025-57271-1, genome-wide L1 regulator screen 10.1186/s13100-025-00386-5. Corporate detail unverifiable from this environment — see `LANDSCAPE.md` §6 |
| D18 | A September 2026 *GeroScience* paper compares retroelement deregulation in DNMT3A- vs TET2-mutant CH | `VERIFIED_AFTER_SEARCH_FAILURE` | **It exists** — Hasan et al., 10.1007/s11357-026-02510-6, PMID 42744964, 16 Sep 2026. Initially recorded as `NOT_FOUND`; the searches used *retroelement*/*retrotransposon* and never *retrotransposable* (the title word), plus one American spelling of *haematopoiesis*. PubMed had it indexed the whole time. See `PRIOR_ART.md` § "One claim was recorded as not found" — the lesson is about over-trusting a negative, not about the reviewer |

## E. Claims about the system's behaviour

| # | Claim | Status | Evidence |
|---|---|---|---|
| E1 | Every displayed sentence carries a resolvable edge id or is discarded | `SUPPORTED_BY_THIS_BUILD` | Citation gate in `te_reason.py`; 19 kept / 2 rejected on 8 worked genes |
| E2 | The system refuses to interpret a signature below a coverage threshold | `SUPPORTED_BY_THIS_BUILD` | `score_signatures.py --min-coverage`; still refuses GO:0006954 at 0.535 after the panel fix |
| E3 | Three components were built, measured and deliberately not shipped | `SUPPORTED_BY_THIS_BUILD` | Rule-based literature extractor (precision 0.109), link prediction (no held-out set possible), the uninterpretable interferon result |
| E4 | Rules generate mechanistic hypotheses, not causal conclusions | `SUPPORTED_BY_THIS_BUILD` | Vocabulary corrected throughout; see `EPISTEMOLOGY.md` |
