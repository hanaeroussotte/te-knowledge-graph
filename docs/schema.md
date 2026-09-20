# TE-aware biological knowledge graph — schema

## The gap this schema closes

Every major biomedical knowledge graph models genes, proteins, pathways, drugs, diseases,
phenotypes and anatomical structures. None of them models a transposable element.

- **Hetionet** (Himmelstein et al. 2017) — 11 node types: Gene, Compound, Disease, Anatomy,
  Pathway, Biological Process, Molecular Function, Cellular Component, Symptom, Side Effect,
  Pharmacologic Class. No repeat or TE entity.
- **PrimeKG** (Chandak et al. 2023) — 10 node types spanning gene/protein, drug, disease,
  phenotype, exposure, pathway, anatomy. No repeat or TE entity.
- **Open Targets** — target / disease / drug / evidence. Targets are protein-coding genes.

The consequence is structural, not incidental. A transposable element cannot be a *target*,
cannot be a *node on a path*, and cannot be *predicted* — because there is no slot for it.
Any question of the form "which genes control which repeat families, and what does that do
downstream?" is unanswerable in these graphs, not because the evidence is missing from the
literature but because the data model has no place to put it.

The same exclusion happens one layer down, in the data. Standard RNA-seq pipelines discard
multi-mapping reads. TEs are, by definition, repeated — so the reads that report on them are
exactly the reads that get thrown away. TE signal is therefore absent from most public
expression matrices *and* absent from every graph built on top of them.

This schema introduces `TEFamily` and `TELocus` as first-class node types, and defines the
edge types that connect host genes to them and them to downstream immune consequence.

---

## Node types

| Type | Key | Description | Primary source |
|---|---|---|---|
| `Gene` | Ensembl gene ID | Protein-coding or ncRNA gene | MyGene / Ensembl |
| `Complex` | Complex Portal CPX | Curated stable macromolecular complex | Complex Portal |
| `TEFamily` | Dfam / RepeatMasker family name | Repeat family or subfamily (e.g. `L1HS`, `HERVK-int`, `AluY`) | Dfam, Telescope annotation |
| `TELocus` | Telescope locus ID | One annotated insertion (e.g. `HERVK_1q22`) | Telescope `retro.hg38` annotation |
| `TEClass` | class/superfamily label | `LINE`, `LTR/ERV1`, `LTR/ERVL`, `SINE/Alu`, `SVA`, `DNA` | RepeatMasker taxonomy |
| `ChromatinMark` | SO / GO term | e.g. H3K9me3, 5mC, H3K27me3 | GO, Sequence Ontology |
| `Sensor` | Ensembl gene ID | Nucleic-acid sensing receptor (subtype of `Gene`, tagged) | GO, Reactome |
| `Pathway` | Reactome stId | Curated pathway | Reactome |
| `GOTerm` | GO ID | Gene Ontology biological process / cellular component | GO |
| `Drug` | ChEMBL ID | Compound or biologic | ChEMBL |
| `Disease` | EFO / MONDO | Disease or trait | Open Targets |

`Sensor` is modelled as a *role tag* on a `Gene` rather than a separate node, so that a gene
that both silences TEs and senses their products (there are several) does not get duplicated.

## Edge types

| Edge | Domain → Range | Meaning | Directed |
|---|---|---|---|
| `SILENCES` | Gene / Complex → TEFamily / TELocus | Loss of this entity increases TE expression | yes |
| `DEREPRESSES` | Gene / Complex → TEFamily / TELocus | Loss of this entity decreases TE expression (i.e. it is required for expression) | yes |
| `MEMBER_OF` | Gene → Complex | Curated subunit membership | yes |
| `DEPOSITS_MARK` | Gene / Complex → ChromatinMark | Writes or maintains the mark | yes |
| `MARK_AT` | ChromatinMark → TEFamily | Mark is enriched at this repeat family | yes |
| `BELONGS_TO` | TELocus → TEFamily → TEClass | Repeat taxonomy | yes |
| `SENSED_BY` | TEFamily → Gene(Sensor) | TE-derived nucleic acid is a ligand for this sensor | yes |
| `SIGNALS_TO` | Gene → Gene | Signal transduction step | yes |
| `PARTICIPATES_IN` | Gene → Pathway | Reactome membership | yes |
| `ANNOTATED_TO` | Gene → GOTerm | GO annotation | yes |
| `INTERACTS_WITH` | Gene → Gene | STRING physical/functional interaction | no |
| `TARGETED_BY` | Gene → Drug | ChEMBL mechanism of action | yes |
| `ASSOCIATED_WITH` | Gene → Disease | Open Targets association | yes |

Sign convention: `SILENCES` and `DEREPRESSES` are stated as **effects of loss of function**,
because that is what the measured layer observes (knockdown / knockout RNA-seq). A
measured edge with a positive log2FC on the TE after knockdown of gene *G* is `G SILENCES T`.
A negative log2FC is `G DEREPRESSES T`. This keeps the measured and curated layers sign-compatible.

---

## Provenance block — mandatory on every edge

No edge enters the graph without all of these fields populated. This is the trust mechanism;
an edge that cannot fill them is dropped, not downgraded.

```
edge_id            stable hash of (subject, predicate, object, source)
subject, predicate, object
evidence_tier      one of: curated | measured | literature | inferred | predicted
source             database name, PMID, or run identifier
source_detail      GO term ID, CPX accession, STRING channel, ENCODE accession, ...
native_score       the source's own score, unmodified (STRING combined score,
                   DESeq2 log2FC, link-prediction probability, ...)
native_score_type  what native_score means, so scores are never silently compared
statistic          FDR / p-value / confidence where the source provides one
retrieved          ISO date the edge was pulled
```

## Evidence tiers

Ordered by how much weight a claim built on the edge can carry. Tier is a property of
*provenance*, not of confidence — a high-scoring predicted edge is still `predicted`.

1. **`curated`** — a human curator asserted it in a reference database (GO with experimental
   evidence codes, Complex Portal, Reactome). Highest trust, lowest coverage.
2. **`measured`** — computed in this project from primary data (ENCODE knockdown RNA-seq
   re-quantified with Telescope, then PyDESeq2). Carries an effect size and an FDR.
   Trustworthy for the cell type assayed; generalisation beyond it is not implied.
3. **`literature`** — extracted from published abstracts/full text, with PMIDs attached.
   Coverage is broad, precision is bounded by the extraction step and must be reported.
4. **`inferred`** — derived by a symbolic rule from edges already in the graph. Carries a
   proof tree naming every ground edge it rests on. No new evidence; new *composition* of
   existing evidence.
5. **`predicted`** — proposed by the link-prediction model for a pair with no direct evidence.
   A hypothesis. Must always be reported with the model's held-out validation metrics
   alongside, and must never be rendered in the same visual style as the tiers above.

A path's tier is the *weakest* tier on it. This is enforced in the path grammar rather than
left to the reader, so a single predicted hop cannot launder a path into looking established.

---

## What this buys that the existing graphs cannot express

Three query classes become expressible:

1. **"What does knocking down gene X do to TE activation?"** — answered from `measured` edges
   where ENCODE assayed X, and from `predicted` edges where it did not.
2. **"Which host factors restrain family F, and through which complex and which mark?"** —
   a multi-hop path `Gene -MEMBER_OF-> Complex -DEPOSITS_MARK-> ChromatinMark -MARK_AT-> TEFamily`,
   which no graph without a TE node can return.
3. **"Which druggable node sits upstream of TE-driven interferon signalling?"** — a path from
   `Drug -TARGETED_BY-> Gene -SILENCES-> TEFamily -SENSED_BY-> Sensor -SIGNALS_TO-> ISG`,
   crossing the TE node that is currently missing.

The third is the target-discovery case, and it is the reason the missing node type is a
practical problem rather than an ontological complaint.
