# The Complete Walkthrough

**What this document is.** Everything in this project, explained from zero, in the order
that makes it understandable rather than the order it was built. If you read only one
file, read this one. It assumes no molecular biology, no statistics and no bioinformatics.
Where a piece of mathematics is doing real work, the formula is written out and explained
term by term, because the correctness of the whole project rests on three or four specific
equations and you should be able to defend each of them.

**How it relates to the other documents.**

| Document | Answers |
|---|---|
| `COMPLETE_WALKTHROUGH.md` (this one) | What is all of this, and why is each piece here? |
| `PRIMER.md` | A shorter from-zero explainer plus the 20-step procedure |
| `MANUAL.md` | I want to run it — which command, which flag? |
| `INTERPRETING_RESULTS.md` | What does this number in the output mean? |
| `CRITIQUE.md` | What is wrong with it, and what is it good for? |
| `HYPOTHESIS_DNMT3A_TET2.md` | How does it connect to the DNMT3A/TET2 work? |
| `ADAPTING_TO_NEW_DATA.md` | Someone handed me a dataset — now what? |
| `PANEL_REFERENCE.md` | How the interferon coverage gap was closed |
| `RUNBOOK.md`, `modal_setup.md` | Operational: reruns, cloud |

---

## 1. The one-paragraph version

About half of the human genome is made of **transposable elements** — ancient viral and
parasitic DNA sequences that copied themselves into our ancestors' chromosomes. Cells keep
them switched off using chemical marks on DNA and on the proteins DNA is wound around. When
that silencing machinery is damaged, transposable elements switch back on, and the cell's
antiviral alarm system mistakes their RNA for a real infection and starts an inflammatory
response. That chain — *broken silencer → element reactivation → inflammation* — is
suspected to matter in ageing, in blood cancers and in autoimmunity. **No public biological
knowledge graph can represent it**, because none of them has a node type for transposable
elements. This project builds one that does, fills it from five independent evidence
sources including our own measurements from raw sequencing data, adds a small symbolic
reasoning engine that derives new links and shows its work as a proof tree, and ends by
asking which of the genes involved could actually be hit with a drug.

---

## 2. The biology, from zero

### 2.1 What a transposable element is

DNA is a long text written in four letters. Most of what people mean by "the genome" is
genes — about 20,000 stretches of text that encode proteins. Genes are roughly **2% of
human DNA**.

A large part of the rest is repeated sequence that arrived by copying itself. A
**transposable element** (TE, also "transposon", "repeat element", "mobile element") is a
stretch of DNA that carries, or once carried, the instructions for making copies of itself
and inserting them elsewhere in the genome. Most are broken by mutation and can no longer
move; a handful of families in humans still can.

They are not a footnote. In the reference human genome used here (hg38), counting
RepeatMasker annotations, this project inventoried:

| Class | What it is | Subfamilies | Copies in the genome | Total DNA |
|---|---|---|---|---|
| SINE | Short elements; includes *Alu*, ~300 bp, over a million copies | 60 | 1,570,678 | 378.6 Mb |
| LINE | Long elements; includes *L1*, up to 6 kb, can still move | 171 | 1,214,702 | 621.9 Mb |
| LTR | Endogenous retroviruses — fossilised viral genomes | 578 | 617,410 | 260.5 Mb |
| DNA | Cut-and-paste transposons, all inactive in humans | 233 | 353,782 | 93.3 Mb |
| Retroposon | The SVA family, evolutionarily young and still active | 6 | 3,735 | 4.1 Mb |
| RC | Rolling-circle (Helitron) elements | 3 | 1,371 | 0.3 Mb |
| **Total** | | **1,057** | **3,761,678** | **~1.36 Gb** |

Three words you need, because they are the hierarchy the whole project counts on:

- **Class** — the broad mechanism (LINE, SINE, LTR, DNA).
- **Family** — a lineage within a class (Alu, L1, ERV1).
- **Subfamily** — a specific version, usually of a specific age (AluY, AluYa5, L1HS,
  HERVK-int). **This is the level at which we count.** Section 8.8 explains why that choice
  is load-bearing and not cosmetic.

An important consequence of "over a million near-identical copies": when you sequence RNA
from a cell and try to work out where each fragment came from, a fragment from an Alu
element matches a million places about equally well. This is the **multi-mapping problem**,
and it is the single biggest technical reason TE biology is hard. Section 8.1 and 8.2 deal
with it.

### 2.2 How the cell keeps them quiet

If a million parasites could copy themselves freely, the genome would not survive. Cells
therefore silence TEs, using two chemical systems that both work by making DNA physically
inaccessible rather than by editing it.

**System one: DNA methylation (5mC).** A methyl group (`-CH3`) is attached to cytosine, one
of the four DNA letters, where it is followed by a guanine ("CpG"). Methylated DNA is
read as "do not transcribe".

- **Writers** add it: `DNMT1` (maintains the pattern when DNA is copied), `DNMT3A` and
  `DNMT3B` (establish new marks).
- **Erasers** remove it: `TET1`, `TET2`, `TET3` — these are dioxygenase enzymes that
  chemically oxidise the methyl group so it can be replaced.

**System two: histone H3 lysine 9 tri-methylation (H3K9me3).** DNA is wound around histone
proteins. Adding three methyl groups to the 9th amino acid (a lysine) of histone H3 makes
that region of chromosome condense into an inaccessible state called heterochromatin.

- **Writers**: `SETDB1`, `SUV39H1`, `SUV39H2`, `SETDB2`, `EHMT1`.
- **Erasers**: the `KDM4` family (`KDM4A`–`KDM4E`), `KDM3A`, `KDM3B`, `PHF8`.
- **Scaffolds** that aim the writers at the right places: `TRIM28` (also called KAP1) — it
  does not have enzyme activity itself, it recruits `SETDB1` to specific TE sequences. The
  **HUSH complex** (`MPHOSPH8`, `TASOR`, `PPHLN1`) does something similar.

This writer/eraser/scaffold structure is not just background. It is *the logic the
reasoning engine in section 9 runs on.*

### 2.3 What happens when silencing fails

When a TE is de-silenced, it is transcribed into RNA. Some of that RNA is
double-stranded, and some TEs reverse-transcribe themselves into DNA in the cytoplasm.

The cell has sensors whose job is to detect exactly those molecular shapes, because that is
what a viral infection looks like:

- `CGAS` detects DNA in the cytoplasm, and signals through `STING1`.
- `IFIH1` (MDA5) and `RIGI` (DDX58) detect double-stranded RNA, and signal through `MAVS`.
- Both routes converge on the kinase `TBK1`, which activates the transcription factors
  `IRF3` and `IRF7`, which switch on **type I interferon** (`IFNB1`).
- Interferon then acts on the cell through `STAT1`/`STAT2`/`IRF9`, switching on hundreds of
  **interferon-stimulated genes** (ISGs): `ISG15`, `IFIT1`, `IFIT3`, `MX1`, `OAS1`, `OASL`.

The cell cannot tell "our own ancient retrovirus woke up" from "we are infected". This is
called **viral mimicry**, and it is the mechanistic heart of the project: it is the reason a
chromatin gene can cause inflammation without any pathogen.

### 2.4 The named user: clonal haematopoiesis

Blood is continuously remade by stem cells in bone marrow. With age, a stem cell can acquire
a mutation that gives it a slight growth advantage, and its descendants come to make up a
measurable share of the blood. This is **clonal haematopoiesis (CH)**. It is common over
60, mostly symptomless, and it raises the risk of blood cancer and — surprisingly — of
cardiovascular disease, which is thought to be driven by chronic inflammation.

The two most frequently mutated genes in CH are `DNMT3A` (~40–50% of cases) and `TET2`
(~10–20%). Look back at section 2.2: **`DNMT3A` is a 5mC writer and `TET2` is a 5mC
eraser.** They are opposite halves of the same chemical switch.

That sets up the question this project's user actually cares about, and it is a question
about *causal structure*, not about whether two things correlate:

> Both DNMT3A-mutant and TET2-mutant clones are inflammatory. Is the inflammation caused by
> the same thing in both? The hypothesis is no: in DNMT3A-mutant CH, TE reactivation lies
> **on the causal path** to inflammation; in TET2-mutant CH there is inflammation, but it
> **does not go through** TE reactivation.

A knowledge graph that cannot represent a TE cannot express that hypothesis, let alone test
it. That is the gap this project fills.

---

## 3. What existing knowledge graphs do not model

A **knowledge graph** is a database shaped like a network: *nodes* are things (a gene, a
disease, a drug), *edges* are statements relating them (`DNMT3A —MUTATED_IN→ CH`). It is
useful because you can ask questions that traverse several edges at once — "what connects
this gene to that disease?" — which a table cannot answer.

The main public biomedical graphs are Hetionet, PrimeKG and Open Targets. Between them they
cover genes, proteins, diseases, drugs, pathways, phenotypes, anatomy and side effects.

**None of them models a transposable element as a first-class entity.** There is nowhere
to put `AluY`. So the statement "SETDB1 silences HERVK" is not a fact that can be false in
those graphs — it is a sentence they cannot write down directly.

Say it that way, not as "no public knowledge graph has TEs". The stronger version is
attackable: an ontology for *bacterial* integrative and conjugative elements exists
([ICEO](https://doi.org/10.1038/s41597-021-01112-5)), which is the same idea in a different
domain, and nothing stops someone building a TE-aware graph tomorrow. The claim is scoped
to the major general-purpose human biomedical graphs, and to a literature search on a
stated date — see `PRIOR_ART.md` and `CLAIMS.md` entry D2.

Two further gaps follow from that one:

1. **No mark-level vocabulary.** They record that SETDB1 is a methyltransferase; they do not
   record *which mark* it writes in a form you can compute on. Without `H3K9me3` as a node,
   you cannot reason "this gene writes the same mark as that gene, so it probably has the
   same effect".
2. **No place for your own measurement.** A curated graph is curated. If you run an
   experiment on Tuesday, there is no mechanism by which your result becomes an edge with a
   provenance tag saying it is yours.

So the project's contribution is not "another knowledge graph". It is: **a graph whose
schema admits TEs, chromatin marks and your own measurements, plus a reasoner that can
exploit the structure that schema exposes.**

---

## 4. The architecture

Five layers. Each produces edges; each edge carries an **evidence tier** saying how much you
should believe it; the reasoner treats tiers as first-class.

```
                    ┌─────────────────────────────────────────┐
     ASK            │  te_reason.py explain("TET2")           │
                    │  → answer + proof tree + citations      │
                    └────────────────┬────────────────────────┘
                                     │
                    ┌────────────────┴────────────────────────┐
     REASON         │  nesy_rules.py — 5 symbolic rules,      │  tier: inferred
                    │  forward-chained to fixpoint            │
                    └────────────────┬────────────────────────┘
                                     │
  ┌──────────────┬───────────────────┼──────────────┬──────────────────┐
  │              │                   │              │                  │
┌─┴──────────┐ ┌─┴───────────┐ ┌─────┴──────┐ ┌─────┴──────┐ ┌─────────┴────┐
│ curated    │ │ mechanism   │ │ measured   │ │ literature │ │ druggability │
│ 9,263 edges│ │ 44 edges    │ │ 12 edges   │ │ 32 edges   │ │ 83 targets   │
│ GO,STRING, │ │ hand-built  │ │ OUR OWN    │ │ LLM from   │ │ Open Targets │
│ Reactome,  │ │ writer/     │ │ analysis   │ │ 3,120      │ │ + ChEMBL     │
│ ComplexPtl │ │ eraser map  │ │ of ENCODE  │ │ abstracts  │ │              │
└────────────┘ └─────────────┘ └────────────┘ └────────────┘ └──────────────┘
  tier:curated   tier:mechanism   tier:measured  tier:literature
```

Evidence tiers, strongest first:

| Tier | Meaning | Source |
|---|---|---|
| `measured` | We computed it from raw reads in this project | `run_de.py` |
| `curated` | A human curator asserted it in a public database | GO, Reactome, STRING, Complex Portal |
| `mechanism` | A biochemical fact stated as a rule (SETDB1 writes H3K9me3) | hand-built, cited |
| `literature` | An LLM extracted it from a paper abstract | `extract_lit.py` |
| `inferred` | Derived by a rule from edges above | `nesy_rules.py` |

The word **neurosymbolic** describes the split: the *neural* part (an LLM) is used only
where language must be turned into structure — reading 3,120 abstracts. The *symbolic* part
(explicit logical rules over a graph) does all the reasoning. Neither is asked to do the
other's job, and the boundary between them is where the citation gate sits (section 9.4).

---

## 5. The platform: what runs where, and on what

### 5.1 The three kinds of work

1. **Network work** — asking public databases for facts (GO, STRING, Reactome, ENCODE,
   Ensembl, PubMed, Open Targets, ChEMBL). Small, fast, network-bound.
2. **Heavy sequence work** — turning gigabytes of raw sequencing reads into a table of
   counts. CPU- and memory-bound. This is the part that wants cloud compute.
3. **Statistics and reasoning** — small tables, seconds of CPU. Runs anywhere.

### 5.2 Reference files

"Reference" means the fixed background data every run needs. They live in `refs/`, which is
**deliberately excluded from the git repository** — they are hundreds of megabytes of
public data that anyone can re-download, and committing them would make the repo unusable.
A fresh clone must therefore run `make refs` first.

| File | What it is | Size |
|---|---|---|
| `chr1.fa`, `chr19.fa` | The DNA sequence of two chromosomes, as text | 314 MB |
| `gencode.v44.gtf` | Where every human gene and exon is | 1.6 GB |
| `hg38_rmsk_TE.gtf` | Where all 3.76 M transposable element copies are | 464 MB |
| `panel.fa`, `panel.gtf` | Spliced-in signature gene loci (section 10) | 62 MB |
| `hisat2/*.ht2` | The search index the aligner uses | ~1 GB |

**Why two chromosomes and not the whole genome?** Building a searchable index of all 3.1
gigabases and aligning against it is hours of compute and tens of gigabytes of memory. On
chr1 + chr19 — about 10% of the genome, chosen because chr19 is unusually gene-dense and
chr1 is the largest — an entire end-to-end run takes about two hours on a laptop. Every
number in this project is from that subset, which has consequences that section 13 is
explicit about. The genome-wide run is the same commands with `--ref-scope genome`.

### 5.3 Software environments

Two isolated environments, because the sequence tools and the statistics tools have
incompatible dependencies:

- **`te-pipeline`** — `hisat2`, `STAR`, `samtools`, `seqtk`, `sra-tools`, `TEtranscripts`.
- **`python`** — `pandas`, `numpy`, `scipy`, `pydeseq2`, `networkx`, `matplotlib`, `requests`.

`environment.yml` and `requirements.txt` in the repo reproduce both.

### 5.4 Two environment bugs you will hit, and their fixes

These are written down because they cost hours and will cost them again on another machine.

1. **STAR 2.7.11b from conda on Apple Silicon reads zero reads and exits 0.** No error, an
   empty BAM, a `Log.final.out` saying `Number of input reads: 0`. `genomeGenerate` works
   fine, which makes it look like your FASTQ is broken. It is not. *Fix:* use HISAT2
   locally and STAR in the cloud. Consequence: the two aligners have never been compared
   head-to-head on the same samples, which is listed as an open falsifier in `CRITIQUE.md`.
2. **STAR's `--readFilesCommand zcat` fails in a restricted sandbox** ("Failed spawning
   readFilesCommand") because STAR spawns it through a shell and a named pipe. *Fix:* the
   pipeline writes uncompressed FASTQ and hands STAR plain text.
3. **PyDESeq2 hard-codes `inner_max_num_threads=1`**, which routes through `loky`, which
   calls `os.sysconf("SC_SEM_NSEMS_MAX")`, which raises on macOS. *Fix:* `run_de.py`
   monkey-patches `os.sysconf` to return a sane value for that one key before importing
   pydeseq2. This is the `_patch_sysconf()` function at the top of the file.

### 5.5 Where Modal fits

Modal is a service that runs your container in the cloud with as many CPUs and as much
memory as you ask for. It matters here for exactly one step — section 6's `te_pipeline.py`
— and for one reason: **the genome-wide reference**. `docs/modal_setup.md` has the image
definition and the launch commands. The key parameter changes are `--ref-scope genome`,
`--aligner star`, `--subsample reservoir` and a real read depth instead of 1.5 M.

Nothing else needs the cloud. The graph build is network-bound, the statistics take
seconds, and the reasoner is instant.

---

## 6. Every script, and what it is for

Nine scripts in `src/`. Read this section as the table of contents of the codebase.

### 6.1 `build_te_annotation.py` — where are the transposable elements?

**Input:** the RepeatMasker table for hg38 (a list of every repeat copy found in the genome).
**Output:** `refs/hg38_rmsk_TE.gtf` and `data/graph/te_subfamilies_hg38.csv`.

RepeatMasker annotates everything repetitive, including things that are not transposable
elements at all — simple repeats like `CACACACA`, satellites, ribosomal RNA. Three filters:

1. Keep only classes `LINE`, `SINE`, `LTR`, `DNA`, `Retroposon`, `RC`.
2. Drop copies shorter than 100 bp — too short to quantify reliably.
3. Keep only main chromosomes, dropping unplaced scaffolds and alternative haplotypes,
   which would otherwise duplicate sequence and create fake multi-mapping.

It sets `gene_id` to the **subfamily** name, which is what makes the counting tool report
per-subfamily totals rather than per-copy totals. The output table is also the TE node
vocabulary for the graph: 1,057 subfamilies.

### 6.2 `build_graph.py` — the curated layer

**Input:** GO terms, public REST APIs. **Output:** `data/graph/nodes.csv`,
`edges_curated.csv`.

Starts from GO terms that define the domain — `GO:0010526` (TE silencing), `GO:0032196`
(transposition), `GO:0140949` (H3K9me3 methyltransferase), `GO:0003886` (DNA cytosine-5
methyltransferase), `GO:0070579` (methylcytosine dioxygenase), plus the interferon and
inflammation terms — collects the genes annotated to them, then expands:

- **STRING v12** for protein–protein interaction edges at confidence ≥ 700.
- **Reactome** for pathway membership.
- **Complex Portal** for protein complex membership.

Result: **1,910 nodes and 9,263 edges.**

| Node type | Count | | Predicate | Count |
|---|---|---|---|---|
| Complex | 1,199 | | `PARTICIPATES_IN` | 4,900 |
| Pathway | 400 | | `MEMBER_OF` | 2,321 |
| Gene | 280 | | `INTERACTS_WITH` | 1,724 |
| GOTerm | 27 | | `ANNOTATED_TO` | 275 |
| ChromatinMark | 3 | | `SILENCES` | 43 |
| TEFamily | 1 | | | |

**Why this script talks to REST APIs directly rather than through a convenience wrapper.**
An earlier version used a hosted connector, and the connector silently capped every gene
lookup at 10 results per GO term. The graph it produced had 112 seed genes and 2,792 edges
and looked entirely plausible. Rewriting against the raw APIs gave 219 seed genes and 9,263
edges — **the first version was missing half the domain and said nothing about it.** Three
concrete API traps, all found by testing rather than by reading documentation:

- `mygene.info` needs the **bare** query string `GO:0010526`. The field-qualified forms
  `go:GO\:0010526` and `go.BP.id:"GO:0010526"` return zero results without erroring, and
  you must pass `size=1000` or you silently get the first 10.
- Reactome's overrepresentation response has an `entities.found` field that is a **count,
  not a list**. To get actual pathway membership you need a second call to
  `/AnalysisService/token/{token}/found/all/{stId}`.
- Open Targets' GraphQL `Tractability` type exposes `label`, `modality` and `value`.
  Asking for `id` returns HTTP 400.

### 6.3 `te_pipeline.py` — raw reads to a count table

The heavy one. Three subcommands: `index`, `run`, `merge`.

```
FASTQ (raw reads)
   → subsample to a fixed depth
   → align to the reference, keeping up to 100 locations per read
   → TEcount: assign reads to genes and TE subfamilies
   → merge per-sample tables into one matrix
```

Each stage and why it is set the way it is:

**Subsampling.** Two modes. `reservoir` downloads the whole file and takes a uniform random
sample — statistically clean, pulls ~2 GB per file. `stream_head` takes the first *n* reads
straight off the wire and stops the download, which is ~10× less transfer. The head of an
Illumina file is *not* a random draw (early reads cluster by flowcell tile), so
`stream_head` is for pipeline validation and relative comparisons, not for a final
quantification. All numbers here use `stream_head` at 1.5 M reads per library, applied
identically to every sample.

**Alignment with `-k 100`.** This is the TE-critical flag. By default an aligner reports
one location per read and discards reads that match many places equally well — which
throws away essentially all TE-derived reads. `-k 100` (HISAT2) / `--outFilterMultimapNmax
100 --winAnchorMultimapNmax 100` (STAR) keeps up to 100 candidate locations per read and
passes the ambiguity downstream, where a tool that knows what to do with it is waiting.

**Counting with `TEcount --mode multi`.** See section 8.2 — this is where the ambiguity is
resolved, by expectation-maximisation rather than by a rule of thumb.

**Two non-obvious correctness details** that are comments in the code and belong here too:

- STAR is run with `--outSAMtype BAM Unsorted`, **not** sorted by position. Unsorted output
  is grouped by read name, which is what TEcount's paired-end handling requires. Telling
  TEcount that a name-ordered file is position-sorted makes it silently mis-pair mates.
- Downloads are validated, not assumed: an empty file, or a line count that is not a
  multiple of 4, raises immediately. A 403 from a data portal otherwise produces an empty
  `.gz` that the aligner complains about ten confusing lines later.

### 6.4 `run_de.py` — which features changed?

**Input:** the count matrix + a manifest saying which sample is knockdown and which is
control. **Output:** `deseq2_results.csv`, `edges_measured.csv`, `setlevel_tests.csv`.

Runs PyDESeq2 (section 8.3–8.6) and emits **two statistics for every contrast**, which is a
deliberate design decision, not belt-and-braces:

1. **Per-feature:** is *this specific TE subfamily* significantly changed?
2. **Set-level:** is the *whole TE compartment* shifted relative to protein-coding genes?

Section 8.7 explains why the second one exists and why it found something the first one
missed.

It also pairs each knockdown with the control from its own experimental batch rather than
pooling all controls, because CRISPRi and CRISPR controls in this dataset differ sharply
(section 13.3).

### 6.5 `score_signatures.py` — did inflammation follow?

**Input:** count matrix, DE results. **Output:** `signature_scores.csv`,
`signature_setlevel_tests.csv`, `signature_coverage.csv`.

Fetches gene sets from GO via QuickGO (type I interferon response, defense response to
virus, inflammatory response, senescence, NF-κB), scores each sample, and tests whether the
set is shifted within each contrast.

**Its most important feature is that it refuses to answer.** Before reporting anything it
computes what fraction of each gene set the reference scope can even see, and if that is
below `--min-coverage` (default 0.6) it declines to interpret the result. On chr1 + chr19
the coverage is:

| Gene set | Genes in set | Present on chr1+chr19 | Coverage |
|---|---|---|---|
| Type I interferon response | 125 | 21 | **16.8%** |
| Type II interferon response | 107 | 24 | 22.4% |
| Defense response to virus | 264 | 46 | 17.4% |
| Inflammatory response | 725 | 130 | 17.9% |
| Senescence | 83 | 8 | **9.6%** |
| NF-κB signalling | 121 | 15 | 12.4% |

`CGAS` is on chr6, `STING1` on chr5, `IFIH1` on chr2, `MAVS` on chr20, `TBK1` on chr12,
`STAT1` on chr2, `STAT2` on chr12, `IRF7` on chr11, `MX1` on chr21, `OAS1` on chr12,
`IFIT1` on chr10. **Every canonical sensor and effector except `IRF3` is outside the
reference.** A "no interferon response" result computed on that scope is a statement about
which chromosomes were indexed. Section 10 is how that was fixed.

### 6.6 `build_panel_reference.py` — make a gene set measurable

**Input:** gene sets + the full GENCODE annotation. **Output:** `refs/panel.fa`,
`refs/panel.gtf`, `data/graph/panel_spec.csv`.

New. Section 10 covers it in full.

### 6.7 `nesy_rules.py` — the symbolic reasoner

**Input:** all edge files. **Output:** derived edges with proof trees.

Five rules, forward-chained to a fixpoint. Section 9.

### 6.8 `te_reason.py` — the query interface

`python src/te_reason.py --gene TET2` returns what is known and what can be derived about a
gene's effect on TE activation, with a proof tree and citations.

Two implementation points worth knowing. It **discovers** its edge layers by globbing
`edges_*.csv` across `data/graph/`, `results/` and `out/`, so adding a new evidence layer
means dropping a file in a directory — no code change. And every sentence it emits must
carry an edge id matching `\[(e[0-9a-f]{14})\]`; sentences without one are **dropped**
rather than printed (section 9.4).

### 6.9 `annotate_tractability.py` — could you drug it?

**Input:** the gene list from the graph. **Output:** `results/targets_tractability.csv`.

Queries Open Targets and ChEMBL and sorts 83 targets into five classes. Section 11.

### 6.10 `extract_lit.py` — the literature layer

**Input:** PubMed abstracts. **Output:** `edges_literature.csv`.

Retrieves abstracts and uses an LLM to extract structured `gene → predicate → TE`
statements. It also contains a **rule-based extractor that was built, measured and
rejected** — kept in the repository because the measurement is the point (section 13.2).

---

## 7. The graph schema

`docs/schema.md` is the formal version; this is the shape.

**Node types:** `Gene`, `TEFamily`, `TEClass`, `ChromatinMark`, `GOTerm`, `Pathway`,
`Complex`, `Disease`, `Drug`.

**Edge columns** — every edge in every layer has the same 13 columns, which is what lets
the reasoner treat five heterogeneous sources uniformly:

| Column | Meaning |
|---|---|
| `edge_id` | `e` + first 14 hex chars of a SHA-1 of subject/predicate/object/tier — stable across reruns |
| `subject`, `subject_type` | where the edge starts |
| `predicate` | `SILENCES`, `DEREPRESSES`, `WRITES`, `ERASES`, `RECRUITS`, `INDUCES`, `MEMBER_OF`, `PARTICIPATES_IN`, `INTERACTS_WITH`, `ANNOTATED_TO` |
| `object`, `object_type` | where it ends |
| `evidence_tier` | `measured` / `curated` / `mechanism` / `literature` / `inferred` |
| `source` | the specific database, paper or contrast |
| `method` | how it was obtained |
| `effect_size`, `effect_size_units` | the number, and what it means |
| `statistic` | the p-value or confidence |
| `date` | when it entered the graph |

The stable hash id matters more than it looks: it is what makes a citation like
`[e3f9a1c04b2e77]` resolvable, and what lets a proof tree be checked by someone else.

---

## 8. The measurement layer and its mathematics

This is the section to understand properly. Everything else in the project is plumbing or
bookkeeping; this is where a claim about biology is actually made, and it is where the one
genuinely novel analytical move lives (8.7).

### 8.1 From a cell to a number

An RNA-seq experiment: take cells, extract RNA, chop it into fragments, read ~100 letters
from each end of a few tens of millions of fragments. The output is a **FASTQ** file — a
list of short strings. The question is how many fragments came from each gene and each TE
subfamily.

You answer it by finding where in the genome each read matches. For a gene this is usually
unambiguous. For an Alu element it is catastrophically ambiguous: one million near-identical
copies, and a 100-letter read matches thousands of them essentially equally well.

Three possible responses:

| Approach | What it does | Consequence |
|---|---|---|
| Discard multi-mappers | Keep only uniquely-mapping reads | Throws away most TE signal; biases towards old, decayed, divergent elements — exactly the ones that are *not* active |
| Count at every location | `featureCounts --countMultiMappingReads` | One read contributes 1 to each of 1,000 loci; totals are inflated and not comparable to gene counts |
| Distribute by likelihood | `TEcount --mode multi` | Each read contributes a *fraction* summing to 1; this is what we do |

The user's own published pipeline (`TE_CHIP`) takes the second route. The two are **not
interchangeable** and have never been benchmarked against each other on the same data;
`CRITIQUE.md` lists that benchmark as the clearest next test.

**Credit where it is due, because this is the part most likely to be mistaken for our
contribution.** The third route is `TEcount`, from **TEtranscripts** (Jin et al.,
*Bioinformatics* 2015, [10.1093/bioinformatics/btv422](https://doi.org/10.1093/bioinformatics/btv422)).
Every TE number in this project comes out of that tool. We did not invent it and must never
imply otherwise. Nor is it the only option — **Telescope**
([10.1371/journal.pcbi.1006453](https://doi.org/10.1371/journal.pcbi.1006453)) and **SQuIRE**
([10.1093/nar/gky1301](https://doi.org/10.1093/nar/gky1301)) resolve to individual loci
rather than subfamilies, SalmonTE is faster, TEspeX handles exonised fragments, MATES and
IRescue work at single-cell resolution, and **MAJEC** (bioRxiv 2026,
[10.64898/2026.04.10.717472](https://doi.org/10.64898/2026.04.10.717472)) targets a failure
mode we do not address at all: TE reads that overlap gene exons, which it reports cutting
from ~43% to ~5% of locus-level signal.

The reason our subfamily-level results are not simply obsolete is that MAJEC's own
benchmark reports **r = 0.987 concordance with TEtranscripts for subfamily-level
differential expression**. MAJEC's advantage is at locus level. That is a defence, not a
dismissal, and the experiment that would settle it for our data is written up — and
explicitly not run — in `QUANTIFIER_ROBUSTNESS.md`.

### 8.2 TEcount's expectation-maximisation

The idea: if you knew how strongly each subfamily was expressed, you could split an
ambiguous read between its candidate locations in proportion to those expressions. You do
not know the expressions — that is what you are trying to measure. So you guess, split,
re-estimate, and repeat until it stops changing.

Let `θ_t` be the (unknown) relative abundance of subfamily *t*, and let read *r* have a set
of candidate alignments `A(r)`, each to some subfamily `t(a)` with alignment score weight
`w_ra`.

**E-step** — given current abundances, how much of read *r* belongs to subfamily *t*?

```
                  Σ_{a ∈ A(r), t(a)=t}  w_ra · θ_t
    z_rt   =     ──────────────────────────────────
                  Σ_{a ∈ A(r)}          w_ra · θ_t(a)
```

**M-step** — given those fractional assignments, re-estimate abundance:

```
    θ_t   =   (1/N) · Σ_r  z_rt
```

Iterate to convergence. Each read contributes exactly 1.0 in total, split across
subfamilies, so **TE counts remain on the same scale as gene counts** — which is what makes
the comparison in 8.7 legitimate.

The assumption to be honest about: EM assigns ambiguous reads *in proportion to unambiguous
evidence*. A subfamily whose copies are all equally ambiguous, with no distinguishing
positions anywhere, gets an abundance that is essentially a prior. Young subfamilies (AluY,
L1HS) are the most ambiguous and also the most interesting.

### 8.3 Size factors: making libraries comparable

Two libraries never contain the same number of reads. Before comparing, you rescale. The
naive approach — divide by total reads — fails badly when a few features dominate, because
one enormous gene changes everyone else's apparent depth.

DESeq2 uses the **median-of-ratios** method. For feature *i* and sample *j* with raw count
`K_ij`, across *m* samples:

```
                        ⎛          K_ij            ⎞
    s_j   =   median_i  ⎜ ─────────────────────────⎟
                        ⎜  ( Π_{v=1..m} K_iv )^(1/m)⎟
                        ⎝                          ⎠
```

In words: for each feature, form a *reference* value as the geometric mean of its counts
across all samples. Divide the sample's count by that reference. You now have one ratio per
feature; **take the median.** That is the sample's size factor.

Why the median makes it robust: a size factor derived from a mean would be dragged by a
handful of extremely highly expressed features. The median asks "what does the *typical*
feature say about this library's depth?" and ignores outliers on both sides.

**One modification here.** In the panel-augmented run (section 10) size factors are
estimated on chr1/chr19 protein-coding genes only, via PyDESeq2's `control_genes` argument.
The panel genes are a deliberately chosen immune-biased subset; letting them influence
normalisation would mean that a genuine interferon response would partly normalise itself
away. Excluding them also makes the panel run's normalisation *identical* to the run
without a panel, which is what the control in section 10.4 requires.

### 8.4 The negative binomial, and why not Poisson

If sequencing were pure random sampling, counts would be Poisson: variance = mean. Real
RNA-seq is **overdispersed** — repeat the experiment on different plates of cells and you
see more variation than Poisson allows, because of real biological variability.

So counts are modelled as **negative binomial**:

```
    K_ij  ~  NB( mean = μ_ij ,  dispersion = α_i )

    Var(K_ij)  =  μ_ij  +  α_i · μ_ij²
                  └──┬──┘   └────┬────┘
              Poisson noise   biological
              (shot noise)    variability
```

and the mean is decomposed into library depth × true expression:

```
    μ_ij  =  s_j · q_ij ,      log₂( q_ij )  =  Σ_r  x_jr · β_ir
```

`x` is the design matrix (which group each sample is in) and `β` the coefficients. The
coefficient you care about *is* the log₂ fold change.

**Dispersion shrinkage** — the step that makes small experiments work at all. With 2–3
replicates per group you cannot estimate `α_i` reliably per feature; a feature that happens
to look consistent gets a near-zero dispersion and then any difference looks significant.
DESeq2 therefore fits a smooth trend `α_trend(μ̄)` across all features, and shrinks each
feature's own noisy estimate towards that trend, in proportion to how uncertain it is. A
feature with genuinely high dispersion keeps it; a feature that merely looks quiet gets
pulled up to what features of its expression level typically look like.

This is empirical Bayes: **borrowing strength across features.** It is the single largest
reason DESeq2 outperforms a per-feature t-test on 2-vs-2 designs, and it is why the results
here are not simply noise despite having two replicates.

### 8.5 The Wald test, and what log2FoldChange means

For each feature, test whether its coefficient differs from zero:

```
                β̂_i                                        1
    z_i  =  ───────────         log₂FC = 1  →  2× more     -1  →  ── as much
              SE(β̂_i)                                        2
```

`z` is compared to a standard normal to get a p-value.

Reading `log2FoldChange`:

| Value | Meaning |
|---|---|
| `0` | no change |
| `+1` | doubled in the knockdown |
| `+0.79` (our AluY/TRIM28 result) | ×2^0.79 = **1.73-fold up** |
| `−1` | halved |

The sign convention here is **knockdown versus control**. So a *positive* log2FC after
knocking down a silencer means the TE went **up** when the silencer was removed — which is
what a silencer is supposed to do. The graph edge for that is `SILENCES`, not
`DEREPRESSES`; the predicate describes the gene's normal function, not the direction of the
measured change.

### 8.6 Multiple testing: Benjamini–Hochberg

353 TE subfamilies tested at p < 0.05 gives ~18 false positives by chance alone; the full
matrix of ~8,700 features gives ~435. You must correct.

Benjamini–Hochberg controls the **false discovery rate** — the expected proportion of your
*declared* discoveries that are wrong. Sort the *m* p-values ascending; find the largest
*k* such that

```
    p_(k)   ≤   (k / m) · q
```

and reject all hypotheses up to *k*. With `q = 0.1`, roughly 1 in 10 of the features you
call significant is expected to be a false positive. That is the `padj` column.

BH is far less conservative than Bonferroni (`p < q/m`), which would control the
probability of *any* false positive and would find nothing here.

**The cost of correction is the subject of the next section.**

### 8.7 The set-level test — the analytical core of this project

**The problem.** Here is the per-feature result for three knockdowns, subfamilies passing
FDR < 0.1:

| Knockdown | TE subfamily | log2FC | padj | baseMean |
|---|---|---|---|---|
| TRIM28 | AluY | +0.790 | 0.0005 | 789 |
| TRIM28 | AluYa5 | +0.990 | 0.068 | 54 |
| TRIM28 | SVA_D | −0.408 | 0.080 | 516 |
| SETDB1 | HERVE-int | +0.966 | 0.083 | 54 |
| TRIM28 | MIR | +0.559 | 0.090 | 197 |
| SETDB1 | HERV9NC-int | +1.198 | 0.090 | 32 |
| **DNMT1** | — **nothing** — | | best padj **0.41** | |

Read only that table and you conclude: DNMT1 knockdown does not derepress transposable
elements. That conclusion would be wrong, and it would have removed the DNA-methylation
arm from the project — the arm the entire DNMT3A/TET2 question depends on.

**Why it is wrong.** FDR correction asks each subfamily to be individually convincing at
1.5 M reads of depth. A small coherent shift spread across 500 subfamilies satisfies no
individual test while being a large, real effect on the compartment.

**The fix.** Ask a different question: *is the TE compartment shifted relative to
protein-coding genes in the same contrast?*

```
    Δ  =  median( log₂FC over TE subfamilies )  −  median( log₂FC over protein-coding genes )
```

tested with a Mann–Whitney U test (a rank test, so it needs no distributional assumption).

**This statistic is not new, and claiming it is would be a mistake.** Comparing one feature
set's fold-change distribution against all other features is **competitive gene-set
testing** — CAMERA ([10.1093/nar/gks461](https://doi.org/10.1093/nar/gks461)) and GSEA
([10.1073/pnas.0506580102](https://doi.org/10.1073/pnas.0506580102)). Aggregate TE readouts
also already exist, including in neurodegeneration, where ALS cortex stratifies into
subtypes one of which is defined by retrotransposon activation
([10.1016/j.celrep.2019.09.066](https://doi.org/10.1016/j.celrep.2019.09.066)).

What a literature search did **not** find (198 open-access full texts, sentence level,
2026-09-20 — see `PRIOR_ART.md`) is the argument below: that using protein-coding genes
from the *same contrast* as the reference makes the readout immune to the normalisation
error which is the field's central objection to TE quantification. The test is borrowed;
the reason for making it the primary TE readout is the contribution.

**Why this is normalisation-invariant, which is the point.** Suppose the size factors are
wrong — say every knockdown-group size factor is off by a common multiplicative factor *c*.
Then for **every** feature *i*, from 8.3–8.4:

```
    log₂FC_i  =  log₂( q_i,KD / q_i,ctrl )   →   log₂FC_i − log₂(c)
```

The shift `−log₂(c)` is **identical for every feature**, TE and gene alike, because size
factors are per-sample, not per-feature. Therefore:

```
    Δ  =  median_TE − median_gene
       →  ( median_TE − log₂ c ) − ( median_gene − log₂ c )
       =  Δ                                        ← unchanged
```

**A normalisation artefact cannot produce a difference between two feature sets measured in
the same libraries.** That is what makes this test worth more than the per-feature test,
not less: it is immune to the failure mode people rightly worry about most in TE
quantification.

**What it found:**

| Knockdown | Feature set | n | fraction up | median log₂FC | binomial p |
|---|---|---|---|---|---|
| SETDB1 | TE subfamilies | 353 | 0.533 | +0.060 | 0.24 |
| SETDB1 | protein-coding | 3,048 | 0.515 | +0.018 | 0.092 |
| TRIM28 | TE subfamilies | 322 | **0.717** | **+0.410** | **3.5 × 10⁻¹⁵** |
| TRIM28 | protein-coding | 2,890 | 0.487 | −0.016 | 0.17 |
| DNMT1 | TE subfamilies | 503 | **0.626** | **+0.117** | **1.6 × 10⁻⁸** |
| DNMT1 | protein-coding | 3,120 | 0.484 | −0.014 | 0.071 |

**DNMT1 loss does derepress transposable elements** — 63% of 503 subfamilies move up,
against 48% of genes, p = 1.6 × 10⁻⁸ — and no single subfamily clears FDR. The per-feature
table hid a real effect; the set-level test found it; and the set-level test is the one that
cannot be faked by normalisation.

The three genes also turn out to behave differently, which is a result in itself:

- **SETDB1** — a *targeted* silencer. Two specific ERV subfamilies move; the compartment as
  a whole does not (p = 0.24). Consistent with SETDB1 being aimed at particular
  endogenous retroviruses by TRIM28 and HUSH.
- **TRIM28** — moves the *whole* compartment (median +0.41) and specific young Alus.
- **DNMT1** — moves the whole compartment weakly and coherently, with nothing individually
  significant.

**This is what grounds the DNA-methylation arm of the graph, and therefore the entire
DNMT3A/TET2 derivation in section 9.6.** Without it, 5mC would be an assumption.

### 8.8 Why counting at subfamily level, not class level

The user's published pipeline aggregates to class and family level. That was tested here on
the same data, and at this depth it **loses** information:

| Knockdown | Hits at subfamily level | Hits after aggregation |
|---|---|---|
| SETDB1 | 2 | 0 |
| TRIM28 | 4 | 1 |

`AluY` alone is padj = 0.0005; pooled into `Alu:SINE` it lands at +0.616 and is no longer
significant. Pooling a responding subfamily together with dozens of non-responding
relatives dilutes the signal.

**The honest part:** *why* only some subfamilies respond is not established here. The
obvious explanation — that only evolutionarily young, still-intact elements can be
reactivated — was tested and **rejected** genome-wide. Correlating each subfamily's
divergence from its consensus (`milliDiv`, a measure of evolutionary age) against its
log2FC gives Spearman ρ = +0.098 (p = 0.39) for SETDB1, +0.056 (p = 0.61) for TRIM28, and
+0.166 (p = 0.027) for DNMT1 — the last one significant but in the *wrong direction*.
Within the Alu family the age pattern does appear, but age and expression level are
confounded there (ρ = +0.713), and partialling expression out drops it to −0.346.
Separately, `|log2FC|` declines with expression for protein-coding genes too (ρ = −0.233),
so the effect is not TE-specific.

So the finding stands (subfamily resolution matters at this depth) and the explanation does
not (we do not know why). Both `CRITIQUE.md` and `PRIMER.md` say so. Aggregation is
expected to become the better choice once per-subfamily counts stop being sparse — i.e. at
full depth, where the trade-off reverses.

---

## 9. The integration layer: symbolic reasoning over the graph

### 9.1 What problem the reasoner solves

The measured layer covers three genes. The curated layer covers 280. There are ~1,500
chromatin-associated genes, and a user will ask about one that has never been knocked down
in any public dataset — `TET2`, for instance, which is not annotated to **any** GO
transposition or TE-silencing term and has no ENCODE knockdown.

A pure lookup returns nothing and is honest but useless. A language model asked directly
will produce a fluent paragraph that you cannot check. The third option is to **derive** an
answer from facts you do have, using rules stated in advance, and show the derivation.

### 9.2 The rules

Each rule is a Horn clause — if these premises are all in the graph, add this conclusion —
with an English statement attached, so a proof tree reads as prose.

**R1 — MARK_GROUNDING.** Establish that a chromatin mark represses TEs, from measurement.

```
    WRITES(g, mark)  ∧  SILENCES_measured(g, TE:global)
                     ⟹  REPRESSES(mark, TE:global)
```

*"`g` writes `mark`; removing `g` raised the TE compartment; therefore `mark` represses
TEs."* Fires 3 times — this is where H3K9me3 and 5mC get grounded in our own data.

**R2 — WRITER_TRANSFER.** Generalise from mark to other writers.

```
    WRITES(g₂, mark)  ∧  REPRESSES(mark, T)  ∧  g₂ ≠ g₁
                      ⟹  SILENCES_inferred(g₂, T)
```

*"`g₂` writes the same repressive mark, so `g₂` is predicted to silence `T` too."* Fires
30 times. **This is the rule that predicts `DNMT3A ⊣ TE`.**

**R3 — ERASER_INVERSION.** Invert for the opposite enzyme.

```
    ERASES(g, mark)  ∧  REPRESSES(mark, T)
                     ⟹  DEREPRESSES_inferred(g, T)
```

*"`g` removes a mark that represses `T`, so `g` is predicted to derepress `T`."* Fires 36
times. **This is the rule that predicts `TET2 → TE`,** with the opposite sign to DNMT3A —
derived, not assumed.

**R4 — COMPLEX_CONSENSUS.** Propagate along physical assemblies.

```
    MEMBER_OF(g₁, C)  ∧  MEMBER_OF(g₂, C)  ∧  SILENCES(g₁, T)  ∧  |members(C)| ≤ 8
                      ⟹  SILENCES_inferred(g₂, T)
```

*"`g₁` and `g₂` are in the same small complex and `g₁` silences `T`."* Fires twice. The
size cap exists because "member of the same 40-protein complex" carries almost no
information.

**R5 — RECRUITMENT_CHAIN.** Fires 0 times on the current graph — reported, not hidden.

Totals: **71 derived edges** — 36 R3, 30 R2, 3 R1, 2 R4, 0 R5.

### 9.3 Forward chaining, fixpoint and path admissibility

The engine applies all rules to all edges, adds whatever fires, and repeats until a pass
adds nothing new. That terminal state is the **fixpoint**. Because every rule only ever
adds edges and the vocabulary is finite, termination is guaranteed.

Derived edges get their own SHA-1 ids and are written to their own file, so an inferred
edge is never confused with a measured one.

Two guards keep derived answers meaningful:

- **`MAX_HOPS = 4`.** In a graph this dense, everything is connected to everything within
  five or six steps, so an unbounded path search returns garbage that is technically true.
- **`path_tier` = the weakest tier on the path.** A chain that is measured → curated →
  inferred is reported as `inferred`. Confidence is limited by the weakest link, not
  averaged over the links.

### 9.4 The citation gate

Every sentence the query interface emits must contain an edge id matching

```
    \[(e[0-9a-f]{14})\]
```

Sentences without one are **discarded before display**, not flagged. On 8 worked genes: 19
sentences kept, 2 rejected.

This is the structural answer to hallucination. The LLM is never the thing that decides
what is true — it converts language to structured edges, and anything downstream that
cannot point at an edge id does not reach the user.

### 9.5 A worked proof tree: `TET2`

`TET2` has no TE annotation in GO, no ENCODE knockdown, and no measured edge. Ask anyway:

```
QUERY: what does TET2 do to TE activation?

ANSWER: TET2 is predicted to DEREPRESS transposable elements globally.
        tier: inferred    rule: R3_ERASER_INVERSION

PROOF
└── DEREPRESSES(TET2, TE:global)                                [inferred, R3]
    ├── ERASES(TET2, 5mC)                                       [curated]
    │   └── GO:0070579 methylcytosine dioxygenase activity      [e7c1a4...]
    └── REPRESSES(5mC, TE:global)                               [inferred, R1]
        ├── WRITES(DNMT1, 5mC)                                  [curated]
        │   └── GO:0003886 DNA (cytosine-5-)MTase activity      [e2b9f0...]
        └── SILENCES(DNMT1, TE:global)                          [MEASURED]
            └── DNMT1 CRISPR KD vs control, K562
                503 TE subfamilies, median log2FC +0.117
                vs 3,120 genes at −0.014, p = 1.6×10⁻⁸         [e5d3c7...]
```

Three edges, one of them our own measurement, and the answer is checkable line by line.

### 9.6 How this reproduces the user's hypothesis — and sharpens it

Run the same query for `DNMT3A`:

| Gene | Role in 5mC | Rule | Derived edge |
|---|---|---|---|
| `DNMT3A` | writer | R2_WRITER_TRANSFER | `SILENCES(DNMT3A, TE:global)` |
| `TET2` | eraser | R3_ERASER_INVERSION | `DEREPRESSES(TET2, TE:global)` |

**Opposite signs, from the same grounding, derived rather than asserted.** Now translate
to the clinical situation, where the gene is *lost* (loss-of-function mutation in a CH
clone):

- **DNMT3A loss** → less 5mC → TEs go **up** → viral mimicry → interferon → inflammation.
  TE reactivation is *on* the causal path.
- **TET2 loss** → less demethylation → 5mC **maintained or increased** → TEs **not** up.
  Inflammation in TET2-mutant CH must arrive by another route.

That is the user's published hypothesis, reconstructed from a DNMT1 knockdown and two GO
annotations, with no input from the CH literature.

And the engine says something *stronger* than the hypothesis. The hypothesis is that
TET2-mutant inflammation is not TE-mediated — i.e. no TE effect. R3 predicts an active
effect in the opposite direction: **TET2 loss should lower TE expression**, not merely fail
to raise it. That is a sharper, more falsifiable claim, and it is the experiment to run:
knock down TET2, measure the TE compartment with the set-level test, and the prediction
either holds or the rule chain is wrong somewhere specific.

**The caveats, which must be said in the same breath.** This is a K562 leukaemia cell line,
not a haematopoietic stem cell. It is knockdown of the whole gene, not the specific
mutations found in CH (DNMT3A R882H is a dominant-negative; TET2 mutations are mostly
loss-of-function). And `DNMT1` is the maintenance methyltransferase while `DNMT3A` is a *de
novo* methyltransferase — R2 transfers between them on the strength of a shared mark, which
is exactly the kind of generalisation that a direct experiment should be allowed to break.
Being able to see that the argument depends on R2, and on which edge, is the point of
printing the proof tree.

---

## 10. Closing the interferon gap: the panel-augmented reference

`docs/PANEL_REFERENCE.md` is the full write-up. The short version, because the reasoning
generalises well beyond this project.

### 10.1 The insight

The two arms of the project have **different reference requirements**, and we had been
paying the more expensive one for both.

- The **TE arm** needs a big reference. TEs are dispersed across the genome; you cannot
  count a subfamily you did not index.
- The **inflammation arm** needs about a thousand specific gene bodies. Nothing more.

So instead of indexing 3.1 Gb of genome to rescue 60 Mb of signal, splice the missing
gene loci into the existing reference as extra contigs, carrying their real GENCODE exon
structure across so counting stays exonic and comparable.

```
   before:   [ chr1 ][ chr19 ]                            310 Mb,  17% ISG coverage
   after:    [ chr1 ][ chr19 ][ 921 panel contigs ]       372 Mb,  77% ISG coverage
```

990 genes, fetched from Ensembl, became 921 contigs and 61.7 Mb.

### 10.2 The bug that nearly made it wrong

Padded windows around clustered gene families overlap — `IFIT1`/`IFIT3`/`IFIT5` on chr10,
`OAS1`/`OAS2`/`OAS3` on chr12, `IFITM1`/`IFITM2`/`IFITM3` on chr11, the APOBEC3 and IFNA
clusters. Written as separate contigs, that puts **0.69 Mb of identical sequence into the
reference twice**, which converts uniquely-mapping reads into artificial multi-mappers at
exactly the genes the panel exists to measure. Found before the first index finished;
windows are now merged, and the builder asserts zero duplicated span.

This is worth remembering as a general lesson: **the failure mode of a clever shortcut is
usually silent.** Nothing would have errored.

### 10.3 The control that licenses it

All 11 libraries were re-aligned from the *identical* FASTQ files, so any difference is
the reference alone.

| Knockdown | Pearson (all) | Pearson (TE only) | median &#124;Δlog₂FC&#124; |
|---|---|---|---|
| SETDB1 | 0.995 | 0.993 | 0.007 |
| TRIM28 | 0.996 | 0.993 | 0.027 |
| DNMT1 | 0.992 | 0.992 | 0.013 |

No sign flips; the set-level deltas are unchanged. The one real cost is that ~1,100 extra
features enlarge the multiple-testing set and per-feature FDR loses 1–2 hits per contrast
— so the TE arm is quoted from the original reference and the inflammation arm from the
panel run. Same reads, same effect sizes, different FDR denominator.

### 10.4 What the fix revealed

Coverage went from 16.8% to 76.8% for the type-I interferon set. The result is a clean,
interpretable **null** — with bootstrap confidence intervals that *exclude* effects the
size of the TE arm, so it is a measured absence rather than a shrug:

| Knockdown | TE arm | 95% CI | Interferon arm | 95% CI |
|---|---|---|---|---|
| SETDB1 | +0.024 | −0.062 … +0.115 | +0.023 | −0.056 … +0.060 |
| TRIM28 | **+0.408** | +0.311 … +0.467 | −0.023 | −0.126 … +0.061 |
| DNMT1 | **+0.136** | +0.095 … +0.178 | −0.011 | −0.059 … +0.042 |

**And the same data explains why.** Expression of the pathway in K562: the transducers are
abundant (`TYK2` 799 CPM, `MAVS` 586, `IRF3` 317, `STAT2` 286, `STING1` 270) and the
**entry points are at the floor** — `CGAS` 0.21 CPM (non-zero in 1 of 11 samples), `ZBP1`
0.26, `TLR3` 0.00, `NLRP3` 0.20, with the RNA sensors `RIGI` and `IFIH1` under 10. `ADAR`,
the principal brake on sensing endogenous double-stranded RNA, sits at 823 CPM. There is
no tonic interferon tone to raise: `IFNB1` and `OASL` are at zero.

So the defensible statement is:

> In K562, TE derepression is not accompanied by a type-I interferon response, **and the
> cytosolic sensing arm required to produce one is not expressed.** This dataset cannot
> test viral mimicry; a cell type with an intact sensing axis is required.

That is the difference between "we saw nothing" and a result. It also converts a
limitation into a specific experimental requirement, which is the more useful output.

### 10.5 The rule it enables

`R6_TE_MEDIATED_INFLAMMATION` — if, in the **same contrast**, losing gene *g* raised the
TE compartment (measured) *and* raised an inflammation signature (measured), conclude *g*
drives that signature through TE derepression. The same-contrast requirement is the whole
content of the rule: a TE effect in one experiment and an interferon effect in another is
a coincidence, not a pathway.

It fires **zero times** here, because every inflammation edge is `NO_DETECTED_EFFECT_ON`.
Reported exactly like R5's zero. The rule is implemented and its premises are unmet; run
this in a sensing-competent line and it fires with no code change.

Engine totals after the panel work: **89 derived edges** from 9,366 inputs — R3 45, R2 38,
R1 4, R4 2, R5 0, R6 0.

### 10.6 The limit that remains

A panel measures the genes you name. It cannot discover an unanticipated pathway the way a
genome-wide run can. It is the right tool for a pre-specified question and the wrong tool
for discovery — and the inflammatory-response set (GO:0006954, 725 members) *still* fails
the 0.6 coverage guard at 0.535, so the guard is still doing its job after the fix.

---

## 11. The druggability layer: so what?

A knowledge graph that ends at "these genes are connected" is an interesting object. The
question a drug discovery group actually asks is *which of these could I do something
about*. `annotate_tractability.py` queries Open Targets and ChEMBL for every gene in the
graph and sorts 83 targets into five classes:

| Class | n | Examples |
|---|---|---|
| 1. Approved drug exists | 7 | `DNMT3A`, `EZH2`, `HDAC1`, `HDAC2`, `ESR1`, `PPARG`, `AHR` |
| 2. Clinical-stage | 6 | `KDM1A`, `TP53`, `TGFB1`, `TGFB3`, `ICOS`, `ERVW-1` |
| 3. Structurally tractable, no clinical programme | 28 | `SETDB1`, `SUV39H1`, `SUV39H2`, `SETDB2`, `EHMT1`, `KDM4A`–`KDM4E`, `CGAS`, `IFIH1`, `EIF2AK2`, `PHF8` |
| 4. Druggable family / antibody-accessible only | 4 | `MPHOSPH8` |
| 5. No tractability evidence | 38 | `TRIM28` |

**Class 3 is the interesting one, and it is the slide to put up.** 28 proteins with a
solved structure and a real binding pocket, sitting on a causal path to inflammation, with
nobody running a clinical programme against them. `SETDB1` in particular: the gene with our
own strongest targeted measurement, structurally tractable, and no clinical programme.

Two entries worth knowing because they will be asked about:

- **`TRIM28` is class 5** — the gene with the largest measured effect in the whole project
  is the one with no tractability evidence at all. It is a scaffold protein with no enzyme
  pocket. This is an honest and instructive result: biggest effect ≠ best target.
- **`ERVW-1` (syncytin-1) is class 2.** A human endogenous retrovirus protein already has a
  clinical-stage antibody against it (temelimab, in multiple sclerosis). The precedent that
  TE-derived proteins are druggable already exists.

`TET2` is absent from this table, because `TET2` never enters the graph through any curated
route — which is the whole reason the reasoner has to derive it.

---

## 12. How to read every output file

### 12.1 `deseq2_results.csv` — one row per feature per contrast

| Column | Meaning | How to read it |
|---|---|---|
| `baseMean` | average normalised count across samples | low values (<10) mean the estimate is fragile whatever the p-value |
| `log2FoldChange` | effect size, knockdown vs control | `+1` = doubled; see 8.5 |
| `lfcSE` | standard error of that estimate | large SE with large log2FC = don't believe it |
| `stat` | the Wald z | `log2FoldChange / lfcSE` |
| `pvalue` | uncorrected | **never read this column alone** |
| `padj` | BH-adjusted | the one that matters; `NaN` means the feature was filtered out |
| `is_TE` / `feature_class` | `TE`, `gene`, `panel_gene` | see 8.3 on why the three are kept apart |
| `knockdown`, `control` | which contrast | comparisons are only valid within a contrast |

### 12.2 Reading a volcano plot

x-axis `log2FoldChange`, y-axis `−log₁₀(padj)`. Up = more significant, right = up in
knockdown. The shape to expect is a "V" — large effects are easier to detect, so
significance rises at both edges.

What to look for, in order:

1. **Is the cloud centred on x = 0?** If it is shifted bodily left or right, that is a
   normalisation problem, not biology.
2. **Are the TE points displaced relative to the gene points?** This is the set-level
   question read by eye, and it is the robust one.
3. **Only then** look at which individual labelled points clear the significance line.

A volcano with nothing above the line does **not** mean nothing happened — DNMT1 is the
worked example of exactly that.

### 12.3 `setlevel_tests.csv` / `global_directional_shift.csv`

Read `median_log2FC` for the TE row **and** the gene row, and the difference between them.
The gene row is the control: it should sit near zero. `frac_up` is the same thing as a
proportion; `binom_p` tests it against 0.5.

### 12.4 `targets_tractability.csv`

`druggability_class` is the summary column. `sm_*` columns are small-molecule evidence
flags from Open Targets; `ab_*` are antibody; `chembl_*` name the actual mechanism if a drug
exists.

### 12.5 Nine ways to misread these results

1. Reading `pvalue` instead of `padj`.
2. Concluding "no effect" from an empty per-feature table (see 8.7).
3. Comparing log2FC across different contrasts — they have different size factors.
4. Trusting a large log2FC on a feature with `baseMean` of 5.
5. Reading a `SILENCES` predicate as the direction of the measured change (it is the
   gene's normal function; the measured change is the opposite).
6. Treating `inferred` edges as findings rather than predictions.
7. Comparing ISG scores between the CRISPRi and CRISPR control groups (section 13.3).
8. Comparing TEcount output to `featureCounts --countMultiMappingReads` output as if they
   were the same quantity (section 8.1).
9. Quoting any interferon result from a chr1+chr19 run (section 6.5).

---

## 13. What makes this correct: the controls and the refusals

This is the section to have ready for a hostile question, because the defensible parts of a
project are the places where it declined to produce a result.

### 13.1 Three components were built, measured, and not shipped

- **The rule-based literature extractor.** A regex/dependency extractor for gene → TE
  statements, validated against LLM-extracted edges: **precision 0.109, recall 0.175,
  direction agreement 10/21 — indistinguishable from chance.** Code kept in
  `src/extract_lit.py`, output not wired into the graph.
- **Link prediction.** Gated at design time on having a gene × TE matrix large enough to
  hold out a validation set. Three knockdowns is not that. An unvalidated AUC would have
  been the single most impressive-looking and least meaningful number in the project.
- **The interferon result.** Withheld at 17% coverage; the guard is in the code, not just
  in the prose. Section 10 is what it took to lift it.

### 13.2 A claimed explanation was tested and withdrawn

The "only young subfamilies respond" story for section 8.8 was stated, then tested
genome-wide, then **rejected** — no age effect, and where it appears it is confounded with
expression. It is now marked as unexplained in two documents. The result survived; the
explanation did not.

### 13.3 A batch structure was found and is respected

The two control groups differ sharply in interferon score: non-targeting (CRISPRi) at
+0.71, CRISPR control at −0.84. That is a technical split between two perturbation
platforms, not biology. Every comparison in this project is therefore **contrast-internal**
— knockdown against its own batch's control — and `run_de.py` pairs them automatically.
Correlating scores across all samples would have produced a large, meaningless correlation.

### 13.4 A silent data-truncation bug was caught by rebuilding

The graph behind the original figures had 112 seed genes. The same build against raw APIs
has 219 (section 6.2). Nothing errored. The lesson generalises: **a convenience wrapper
that returns fewer rows than you asked for is worse than one that fails.**

### 13.5 A coordinate system was verified rather than assumed

The panel reference (section 10) splices Ensembl-fetched sequence into a UCSC-derived
reference. If GRCh38 and hg38 coordinates disagreed by even one base, every spliced exon
annotation would be out of register and the whole inflammation arm would be quietly wrong.
A 301 bp window on chr1 was fetched from both and compared byte for byte: identical.

---

## 14. Limitations, stated plainly

1. **Depth and scope.** 1.5 M reads per library on 10% of the genome. This is a pipeline
   validation, not a final quantification. Every effect size should be treated as
   provisional.
2. **Three knockdowns.** SETDB1, TRIM28, DNMT1. Everything else in the graph is curated,
   mechanistic, literature-derived or inferred.
3. **No DNMT3A or TET2 measurement exists anywhere in ENCODE.** The two genes the user
   cares about most are exactly the two that cannot currently be measured from public
   knockdown data. Both predictions are `inferred`.
4. **One cell type.** K562, a chronic myelogenous leukaemia line. Not a stem cell, not
   primary tissue.
5. **Aligners never compared.** HISAT2 locally, STAR intended for cloud; forced by a broken
   arm64 STAR build. An untested seam.
6. **Literature extraction precision is unknown.** The LLM's output was used as its own
   reference standard when validating the rule-based extractor, which measures agreement,
   not accuracy. ~100 human-annotated abstracts would fix this.
7. **Literature cannot name TEs.** Across 3,120 abstracts the literature layer could name
   only 9 coarse TE terms — **0.85% of the 1,057-subfamily vocabulary** — and none of the
   six subfamilies we actually measured. This is not a bug in the extractor; it is how
   papers are written. It is also the strongest argument for the measured layer existing.
8. **`stream_head` subsampling is not a random draw.** Fine for relative comparisons
   applied identically across samples; not what you would report as a final number.
9. **A panel measures what you name.** Section 10's fix cannot discover an unanticipated
   pathway the way a genome-wide run can.

---

## 15. Explaining it out loud

### The 60-second version

> Half your genome is domesticated viruses. Cells keep them switched off with chemical
> marks; when the machinery that writes those marks breaks, the elements wake up and the
> cell's antiviral alarm fires — inflammation with no infection. That's implicated in
> ageing and in blood cancer. The major general-purpose biomedical knowledge graphs —
> PrimeKG, Hetionet, Open Targets — don't model transposable elements as first-class
> entities, so that chain is hard to express in them directly. Meanwhile there are over a
> thousand public perturbation experiments whose authors never counted the repetitive
> genome. We re-analyse them for TE effects, turn the measurements into signed,
> provenance-tracked relationships, and run mechanism rules that generate testable
> hypotheses about genes nobody has assayed — each one printed as a proof tree you can
> attack line by line. And when the evidence won't support an answer, it refuses and names
> the experiment that would.

### The three slides that matter

1. **The gap.** Hetionet, PrimeKG and Open Targets don't model TEs as first-class
   entities — 3.76 million elements across 1,057 subfamilies with nowhere to sit. The
   measurement tools (TEtranscripts and successors) and the reasoning tools have never
   been connected.
2. **The measurement.** DNMT1: nothing at FDR < 0.1, and a real effect at p = 1.6 × 10⁻⁸ on
   the set-level test. Explain why that test cannot be faked by normalisation (8.7). This
   is the slide that shows you know what you are doing.
3. **The proof tree for TET2.** A gene with no data at all, answered from three edges, one
   of them yours, with the derivation printed.

### Questions you will get, and the answers

**"Isn't this just a lookup table?"** No — `TET2` has no TE annotation anywhere, and the
system still answers it, by a stated rule chain you can inspect.

**"How do you know the LLM isn't making it up?"** It never asserts anything. It converts
abstracts to structured edges; every displayed sentence must carry a resolvable edge id or
it is discarded. 19 kept, 2 rejected on the worked examples.

**"Multi-mapping reads make TE quantification meaningless."** That is why there are two
statistics. The set-level test compares TE against protein-coding features *within the same
libraries*, so any per-sample normalisation error cancels exactly (8.7).

**"Two replicates is not enough."** Correct for per-feature claims, which is why the
headline result is a compartment-level shift across 503 features, and why dispersion
shrinkage exists (8.4).

**"Why should I believe a prediction with no experiment behind it?"** You shouldn't believe
it — you should test it. The system tells you exactly which experiment: knock down TET2 and
look at the TE compartment. It predicts a *decrease*, which is falsifiable.

---

## 16. Glossary

| Term | Meaning |
|---|---|
| **5mC** | methylated cytosine; a repressive DNA mark |
| **Alu** | the most abundant human SINE, ~300 bp, >1 M copies |
| **BH / FDR** | Benjamini–Hochberg; expected fraction of your discoveries that are false |
| **CH** | clonal haematopoiesis |
| **CRISPRi** | CRISPR interference — blocks transcription without cutting DNA |
| **dispersion** | how much more variable counts are than Poisson |
| **ERV** | endogenous retrovirus; a fossilised retrovirus in the genome |
| **FASTQ** | the raw output file of a sequencer |
| **fixpoint** | the state where applying the rules adds nothing new |
| **GTF** | a text format listing genomic feature coordinates |
| **H3K9me3** | tri-methylated lysine 9 of histone H3; a repressive chromatin mark |
| **HUSH** | a complex (MPHOSPH8/TASOR/PPHLN1) that silences young TEs |
| **ISG** | interferon-stimulated gene |
| **knockdown** | reducing a gene's expression experimentally |
| **LINE / SINE / LTR** | long / short interspersed elements; long terminal repeat (ERV) elements |
| **log2FC** | log base 2 of the fold change; `+1` = doubled |
| **multi-mapping** | a read that matches many genomic locations equally well |
| **padj** | p-value after multiple-testing correction |
| **RepeatMasker** | the tool/annotation identifying repeats in a genome |
| **size factor** | per-sample scaling constant correcting for sequencing depth |
| **subfamily** | the finest TE grouping, usually age-related (AluY, L1HS) |
| **viral mimicry** | own TE transcripts triggering an antiviral response |
| **Wald test** | coefficient divided by its standard error, compared to a normal |
