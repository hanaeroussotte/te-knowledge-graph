# Claim registry

Every externally presentable scientific claim this project makes, with a status, the
approved public wording, and the wording that is **not** to be used. Nothing goes on a
slide, in an abstract, into a README or out of anyone's mouth in a demo unless it appears
here. This is the single source of truth for what can safely be said.

> **Adversarial novelty rule.** Assume every novelty claim is false until the strongest
> available prior art has been identified and compared against it. The purpose of the
> search is to narrow or eliminate our claims, not to defend them.

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

---

## A. Claims about what exists in the world

| # | Claim | Status | Evidence |
|---|---|---|---|
| A1 | Roughly half the human genome is repeat-derived; hg38 RepeatMasker yields 3,761,678 filtered TE copies across 1,057 subfamilies after our filters | `SUPPORTED_BY_THIS_BUILD` | `te_subfamilies_hg38.csv`; filters in `build_te_annotation.py` |
| A2 | L1 activation drives an interferon response in senescent cells and age-associated inflammation | `ESTABLISHED` | De Cecco et al., Nature, 10.1038/s41586-018-0784-9 |
| A3 | cGAS has a role upstream of TE control, not only downstream as a sensor: cGAS-deficient mice show LINE-1 derepression and inflammatory ageing | `ESTABLISHED` | Nat Aging 2026, 10.1038/s43587-026-01206-y |
| A4 | Neither DNMT3A nor TET2 has a knockdown RNA-seq experiment in ENCODE | `SUPPORTED_BY_THIS_BUILD` | `encode_kd_inventory.csv`, 1,114 experiments / 570 targets |
| A5 | TET2 is not annotated to any GO transposition or TE-silencing term | `SUPPORTED_BY_THIS_BUILD` | QuickGO query in `build_graph.py` |

## B. Claims about our measurements

| # | Claim | Status | Evidence |
|---|---|---|---|
| B1 | TRIM28 knockdown shifts the whole TE compartment (median log₂FC +0.41 vs −0.02 for genes) | `SUPPORTED_BY_THIS_BUILD` | `global_directional_shift.csv`, p = 3.5 × 10⁻¹⁵ |
| B2 | DNMT1 knockdown derepresses the TE compartment with **no** single subfamily at FDR < 0.1 | `SUPPORTED_BY_THIS_BUILD` | p = 1.6 × 10⁻⁸; best per-feature padj 0.41 |
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
| C2 | TET2 loss *lowers* TE expression | `INFERRED` | R3_ERASER_INVERSION; sharper than the source hypothesis and falsifiable |
| C3 | In DNMT3A-mutant CH, TE reactivation is on the causal path to inflammation; in TET2-mutant CH inflammation is not TE-mediated | `HYPOTHESIS` | The user's published hypothesis. This project instruments it; it does not test it |
| C4 | The 28 structurally tractable targets with no clinical programme are actionable | `INFERRED` | Imported Open Targets/ChEMBL buckets, not computed here |

## D. Novelty and positioning claims

| # | Claim | Status | Notes |
|---|---|---|---|
| D1 | "No public knowledge graph has TEs" | `RETRACTED_BY_US` | Replaced by D2 |
| D2 | Major general-purpose human biomedical knowledge graphs (PrimeKG, Hetionet, Open Targets) do not model TE families or loci as first-class entities, making TE-specific perturbational reasoning hard to express directly | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | Nearest precedent is ICEO, an ontology for *bacterial* mobile elements (10.1038/s41597-021-01112-5) |
| D3 | "Nobody has systematically perturbed genes to find TE regulators" | `RETRACTED_BY_US` | Flatly false — C. elegans 2003, Drosophila 2013, human L1 CRISPR screens Nature 2018, LINE-1 CRISPR 2025 |
| D4 | Re-mining perturbation experiments *run for other purposes* for TE phenotypes their authors did not measure | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | Narrow. Existing screens are prospective and TE-designed, usually reporter-based and L1-focused |
| D5 | TE quantification handling multi-mapping reads is our contribution | `RETRACTED_BY_US` | It is TEtranscripts/TEcount (10.1093/bioinformatics/btv422). Alternatives: Telescope, SQuIRE, SalmonTE, TEspeX, MATES, IRescue, MAJEC |
| D6 | Comparing a focal feature set's fold-change distribution against all other features is a new statistic | `RETRACTED_BY_US` | It is competitive gene-set testing — CAMERA (10.1093/nar/gks461), GSEA (10.1073/pnas.0506580102) |
| D7 | Aggregate/global TE expression readouts are new | `RETRACTED_BY_US` | ALS cortex subtypes with retrotransposon activation (10.1016/j.celrep.2019.09.066); aggregate intact-L1 quantification (10.1186/s13041-022-00914-x) |
| D8 | Framing the TE-vs-protein-coding set comparison as *immune to per-sample normalisation error*, and using it as the primary TE readout for that reason | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | 198 OA full texts read at sentence level; nearest hits used protein-coding genes only to *define* intergenic TEs |
| D9 | Knowledge-graph-driven prediction of perturbation responses is unexplored | `RETRACTED_BY_US` | TxPert (10.1038/s41587-026-03113-4) and at least three other KG-based perturbation predictors |
| D10 | TxPert plus a TE-aware expression matrix would be a strong competitor | `HYPOTHESIS` | TxPert's published output space is conventional transcriptomic response; it does not model TEs. The gap is closable, not closed |
| D11 | A reduced/targeted reference set is a novel idea | `RETRACTED_BY_US` | Targeted panels are routine. Our contribution is the coverage guard and the reference-perturbation control around one |
| D12 | The surviving positioning: **an evidence-traceable perturbational reasoning system for transposable-element regulation** | `NOT_FOUND_IN_PRIOR_ART_SEARCH` | Combination claim: re-analysis of perturbation data for TE effects + signed provenance-tracked edges + mechanism rules + inspectable proof trees + explicit refusal. Each component has precedent; the assembly did not surface |

## E. Claims about the system's behaviour

| # | Claim | Status | Evidence |
|---|---|---|---|
| E1 | Every displayed sentence carries a resolvable edge id or is discarded | `SUPPORTED_BY_THIS_BUILD` | Citation gate in `te_reason.py`; 19 kept / 2 rejected on 8 worked genes |
| E2 | The system refuses to interpret a signature below a coverage threshold | `SUPPORTED_BY_THIS_BUILD` | `score_signatures.py --min-coverage`; still refuses GO:0006954 at 0.535 after the panel fix |
| E3 | Three components were built, measured and deliberately not shipped | `SUPPORTED_BY_THIS_BUILD` | Rule-based literature extractor (precision 0.109), link prediction (no held-out set possible), the uninterpretable interferon result |
| E4 | Rules generate mechanistic hypotheses, not causal conclusions | `SUPPORTED_BY_THIS_BUILD` | Vocabulary corrected throughout; see `EPISTEMOLOGY.md` |
