# Execution brief

**Project:** Evidence-Traceable Neurosymbolic Reasoning for Transposable-Element Regulation

**Why this document exists.** The brief was reviewed three times and the same four gaps
were flagged each round — not because they had not been fixed, but because the reviewer was
reading a *plan document that never changed* while the fixes landed in the repository. This
file is the plan and the status in one place, so that a reviewer can see what was asked and
check the claim that it is done. Every row has a file to open.

Status at commit `2c43fa8`. The verification column is what to run, not what to trust.

---

## Standing rules

These govern everything below and are reproduced in `CLAIMS.md`.

> **Adversarial novelty rule:** treat every novelty claim as unproven until the strongest
> available prior art has been identified and compared against it. The objective is to
> narrow or remove claims where necessary, not to preserve the existing positioning.
> "Not found" claims must always state the databases searched, the search strategy and the
> search date; absence from a literature search must never be converted into "nobody has
> done this."

> **Absence of evidence from a literature search is weak evidence of absence.**

> **No claim gets rewritten until the prior-art table exists.** The gate runs before the
> repositioning, not after it, so the wording cannot be chosen first and justified second.

---

## The four flagged items, and where each one landed

### 1. Title

**Asked:** change the title; "Mutation Pathways" points at the wrong scientific object.

**Done.** `Evidence-Traceable Neurosymbolic Reasoning for Transposable-Element Regulation`
— `README.md` line 1 and the `<title>` of `demo/presentation.html`. The rejected original
described mutation biology rather than perturbation → TE regulation.

```bash
head -1 README.md
grep -o '<title>[^<]*</title>' demo/presentation.html
```

### 2. Ontology

**Asked:** `TEClass → TEFamily → TESubfamily → TELocus → TETranscript`, not a combined
family/subfamily level.

**Done.** `docs/TE_RESOLUTION.md` §1, five separate levels. The argument for separating
them is the project's own result: `AluY` is significant at padj 0.0005 while the `Alu`
family it belongs to is not significant at all, so collapsing the two levels would erase
the finding that motivates the resolution discussion.

A second axis is documented alongside it, because resolution and context are independent:

```
evidence resolution   class | family | subfamily | locus | transcript
experimental context  species | cell_type | cell_state | perturbation
                      | perturbation_modality | assay | timepoint | dose
                      | reference_genome | reference_scope | quantifier
```

```bash
grep -n "TESubfamily" docs/TE_RESOLUTION.md
grep -c "TEFamily/Subfamily" docs/TE_RESOLUTION.md   # expect 0
```

### 3. Context propagation and regression testing

Inserted verbatim as asked, and implemented:

> **Context propagation and regression testing**
>
> Inferred edges must inherit relevant experimental context from their premises. If an
> inference generalises beyond the measured context, mark it explicitly as
> `context_generalization_required` rather than silently presenting it as universal.
>
> After regenerating the graph, run regression tests across all existing worked examples.
> Compare returned edges, direction/sign, evidence tiers, proof-tree topology, rule
> provenance and citation IDs. Any changed biological conclusion must be surfaced for
> review rather than silently altered to preserve the old output.

**Context propagation — done.** `nesy_rules.inherit_context()`, applied centrally in
`forward_chain` so a rule added later cannot forget it. Agreement inherits; disagreement
becomes `mixed(a|b)` with nesting flattened so it does not compound across chaining
rounds; absence is `not_applicable`; any premise carrying specific experimental context
sets `context_generalization_required=yes`. **87 of 89 derived edges are flagged**; the two
that are not rest only on curated complex membership and genuinely have no experimental
context. Proof trees print it inline:

```
TET2 -DEREPRESSES-> TE:global   [inferred via R3_ERASER_INVERSION]
  ! prediction is grounded in context_cell_type=K562; perturbation_modality=CRISPR
    — asserting it elsewhere is a further inference
```

**Regression — done.** `tests/test_regression.py` pins, for **10** worked examples:
per-claim `direction` (the biological conclusion), `cites` (citation IDs), `tier`, `rule`
(provenance), `proof_depth` (topology), the traversed `paths`, and `inference_context`
including the generalisation flag. The header states the rule the reviewer asked for: a
changed conclusion is surfaced, never silenced by editing code until the old answer
returns. Two things worth recording from building it — it caught a tuple/JSON round-trip
bug in its own baseline, and it was checked by deliberately flipping a `direction` field
to confirm it reports the flip rather than passing.

```bash
python src/te_reason.py TET2 --export-derived results/derived_edges.csv
python tests/test_regression.py
python -c "import pandas as pd; d=pd.read_csv('results/derived_edges.csv',keep_default_na=False); \
print(d.context_generalization_required.value_counts().to_dict()); \
print('grounded but unflagged:', int(((d.context_cell_type!='not_applicable') & \
(d.context_generalization_required!='yes')).sum()))"
```

### 4. Pre-push scientific gate

Inserted verbatim as asked:

> **Pre-push scientific gate**
>
> Do not commit or push until the prior-art table is complete, graph regeneration
> succeeds, context fields are explicit, proof-tree regression tests pass, old
> causal-overclaim wording is removed, novelty claims are traceable to prior-art evidence,
> citations resolve, artifacts regenerate, and the git diff contains no unrelated changes.

**Implemented as `make gate`**, seven steps:

| # | Step | Checks |
|---|---|---|
| 1 | regenerate derived edges | the graph re-derives; `results/derived_edges.csv` rewritten |
| 2 | `tests/audit_claims.py` | retracted wording asserted anywhere; dangling doc references; **blank context cells**; grounded-but-unflagged inferences; registry sections present; prior-art table exists |
| 3 | `tests/check_citations.py` | **every DOI resolves against Crossref and every PMID against NCBI**, printing the title each resolves to |
| 4 | `tests/test_regression.py` | proof trees, rule firing, layer counts, structured conclusions |
| 5 | `src/make_figures.py` | **both figures rebuild from `results/*.csv`** with no kernel state |
| 6 | syntax | every file in `src/` and `tests/` parses |
| 7 | `git status` | the diff is printed for a human to read; the gate does not commit |

Two of these were existence checks in an earlier round — `ls figures/*.png` and a
file-present test — which assert a property rather than verify it. They were replaced:
citations are now resolved against live registries (17 DOIs, 17 PMIDs), and the committed
PNGs are exactly the output of `make_figures.py`.

**Two defects found in the gate itself, by testing it.** Recorded because a gate nobody
attacks is decoration:

1. **The gate reported `GATE PASSED` while step 3 printed `AUDIT FAIL`.** The recipe was
   `python tests/check_citations.py | tail -3`, and a shell pipeline reports the exit
   status of the *last* command — `tail` — not of python. A check whose failure cannot fail
   the gate is worse than no check. The pipe is gone, with a comment on the line so it is
   not reintroduced for tidier output.
2. **The citation checker called a transient NCBI response a definitive failure.** NCBI
   intermittently returns HTTP 200 with an empty record under load; PMID 29218879 failed
   once and resolved on retry. That is dangerous in both directions — it blocks a push on a
   network hiccup, and it invites someone to "fix" the gate by deleting a citation that was
   real. `resolve_pmid` now retries with backoff and only declares failure when the record
   is absent every time; transient states are reported as inconclusive, not as failure.

Both were verified by injecting a fake DOI and PMID into `CLAIMS.md` and confirming the
gate exits non-zero, then removing them and confirming it exits zero:

```
injected bad citations  -> gate exit status: 2
                           AUDIT FAIL — 2 citation(s) do not resolve
clean tree              -> gate exit status: 0
                           CITATIONS PASS — 17 DOIs, 17 PMIDs all resolve
```

**One box is deliberately unticked.** *Graph regeneration succeeds from source* is not in
the automated gate: `build_graph.py` needs ~10 minutes of live calls to GO, STRING,
Reactome and Complex Portal, so gating on it would fail on a network blip rather than on a
defect. Run `make graph` manually before a release. Flagged rather than quietly passed.

```bash
make gate
```

---

## Workstreams, unchanged

The scientific direction was not redesigned. For reference, the phases as executed:

| Phase | Output |
|---|---|
| 1. Establish the scientific record | `data/graph/prior_art.csv`, `docs/PRIOR_ART.md`, `docs/CLAIMS.md` — **run before any wording changed** |
| 2. Reposition | `docs/WHY_THIS_IS_DIFFERENT.md`; only claims surviving phase 1 rewritten |
| 3. Make the epistemology explicit | `docs/EPISTEMOLOGY.md` — the TE RNA → dsRNA → cytoplasmic cDNA → sensor activation → interferon → phenotype ladder; rules relabelled mechanism-guided candidate generation |
| 4. Make evidence contextual | `src/migrate_edge_context.py`; context on all 9,366 edges; inheritance on inferred edges |
| 5. Define the next resolution | `docs/TE_RESOLUTION.md`, `docs/QUANTIFIER_ROBUSTNESS.md` — specified, **not run** |
| 6. Rebuild the scientific story | `docs/DEMO_SCRIPT.md` — seven questions, TRIM28-centred |
| 7. Make the compute story credible | `docs/COMPUTE.md` — no GPU step claimed; honest Nextflow/Snakemake/HPC comparison |
| 8. Audit before push | `make gate` |

## What the prior-art gate cost

Four claims retracted, two survived in narrowed form. Full record in `PRIOR_ART.md`;
statuses and approved wording in `CLAIMS.md` §0.

| Retracted | Because |
|---|---|
| "No public knowledge graph has TEs" | Narrowed to PrimeKG/Hetionet/Open Targets not modelling TEs as first-class entities. ICEO does this for *bacterial* mobile elements |
| "Nobody has systematically perturbed genes to find TE regulators" | Genome-wide screens: *C. elegans* 2003, *Drosophila* 2013, human L1 CRISPR screens *Nature* 2018 |
| TE multi-mapping quantification as ours | It is TEtranscripts |
| The set-level statistic as new | Competitive gene-set testing — CAMERA, GSEA |

| Survived, scoped | |
|---|---|
| The normalisation-invariance *framing* | Not the test — the argument for making it the primary TE readout. Not located in 198 open-access full texts |
| The assembly | "An evidence-traceable perturbational reasoning system for transposable-element regulation" |

A method note is recorded in `PRIOR_ART.md` because it nearly produced a false novelty
claim: the first full-text pass used Europe PMC's `FULL_TEXT:` field, which does not exist
and fails silently, returning five false "no precedent" results. The correct field is
`BODY:` — same query, 593 hits. A novelty claim is cheapest to "prove" with a broken
search, which is the whole reason for the adversarial rule.
