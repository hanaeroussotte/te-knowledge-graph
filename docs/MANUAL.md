# Manual — from zero to running the TE reasoning engine

Written for someone who has never touched this project. No prior knowledge of transposable
elements, RNA-seq pipelines, or knowledge graphs is assumed. If you already know the biology,
skip to §3.

---

## 1. What problem is this solving?

### 1.1 What is a transposable element?

Roughly half of the human genome is made of **transposable elements** (TEs) — sequences that
copied themselves around the genome over evolutionary time. The big classes:

| Class | What it is | Examples | Copies in hg38 |
|---|---|---|---|
| **LINE** | Long autonomous retroelements; L1 is the only one still active in humans | L1HS, L1PA2 | ~1.2 M |
| **SINE** | Short non-autonomous elements that hitchhike on LINE machinery | AluY, AluYa5 | ~1.6 M |
| **LTR / ERV** | Endogenous retroviruses — ancient viral integrations | HERV-K, HERV-E | ~617 k |
| **SVA** | Composite, youngest human element family | SVA_D, SVA_F | ~3.7 k |
| **DNA** | Cut-and-paste transposons, all fossil in humans | Tigger, MER | ~354 k |

Cells keep these switched off. The silencing machinery is largely chromatin-based: proteins
write repressive marks (H3K9me3, DNA methylation) over TE sequences, and the TEs stay quiet.

**Why anyone cares:** when that silencing fails, TE transcripts accumulate. Double-stranded RNA
and reverse-transcribed DNA from TEs look like a viral infection to the cell's innate immune
sensors, which fires interferon and inflammatory signalling. This links epigenetic regulators
to inflammation — relevant to ageing, cancer, autoimmunity, and clonal haematopoiesis.

### 1.2 The two reasons TEs are invisible to standard analysis

**Reason one — the reads get thrown away.** When you sequence RNA, you get millions of short
reads and align them to the genome. A read from a TE will match hundreds of near-identical
copies. Standard pipelines call that a *multi-mapping* read and discard it, because they cannot
tell which copy it came from. TEs are repetitive by definition, so this discards exactly the
evidence about TEs. Most public expression matrices therefore contain no usable TE signal.

**Reason two — there is no slot for them in the graph.** Biology knowledge graphs
(Hetionet, PrimeKG, Open Targets) model genes, proteins, drugs, diseases, pathways. **None of
them has a transposable-element node type.** So a TE cannot be a drug target, cannot appear on
a returned path, and cannot be predicted — not because the evidence is missing from the
literature, but because the data model has nowhere to put it.

This project fixes both: a pipeline that keeps multi-mapping reads, and a graph that has TE
nodes.

### 1.3 What the tool does, in one sentence

**You give it a human gene symbol. It tells you what losing that gene does to TE activation —
measured where data exists, derived by logical rule where it does not — and every statement
comes with the evidence it rests on.**

---

## 2. Key concepts you need

### 2.1 The "loss frame"

Every edge in the graph is phrased as *what happens when you remove the gene*. This matches how
the experiments work (you knock a gene down and see what changes).

- `SILENCES` — losing the gene **raises** the TE. The gene was holding it down.
- `DEREPRESSES` — losing the gene **lowers** the TE. The gene was needed for it to be expressed.

Keeping one frame everywhere is what lets curated, measured, and inferred edges be compared
without sign errors.

### 2.2 Evidence tiers

Every edge carries a tier. Tier describes **where the claim came from**, not how confident
anyone is. A high-scoring prediction is still a prediction.

| Tier | Meaning | Source here |
|---|---|---|
| `curated` | A human curator asserted it in a reference database | GO, Reactome, Complex Portal, STRING |
| `measured` | Computed in this project from primary data | ENCODE knockdown RNA-seq, re-quantified |
| `literature` | Extracted from published abstracts, PMID attached | PubMed |
| `inferred` | Derived by a rule from edges already present | the rule engine |
| `predicted` | Proposed with no direct evidence | (not used in this build — see CRITIQUE.md) |

**A path is only as strong as its weakest edge.** That is enforced in code, so one inferred hop
cannot make a chain look established.

### 2.3 "Neurosymbolic" — what it actually means here

The word covers a lot of vague things. Here it is concrete and has two halves.

**Symbolic half.** A small set of hand-written if-then rules over the graph. They run forward
to a fixpoint and every derived edge keeps a **proof tree** — the list of ground edges it rests
on. You can always ask "why do you say that?" and get a finite, checkable answer.

**Neural half.** Language models do two jobs: extracting relations from paper abstracts, and
writing the natural-language explanation. Neither is trusted.

**The coupling is a citation gate.** The explanation is split into sentences, and a sentence is
kept only if every edge ID it cites exists in the graph. Sentences citing nothing are rejected
too — silence about provenance is not treated as better than a wrong citation, because a reader
cannot tell the difference. The gate runs identically on model-written and template-written
prose, so the guarantee **does not depend on the model behaving well**. That is the design
point: the trust comes from the checker, not from the generator.

---

## 3. The files

### Code
| File | What it does |
|---|---|
| `te_pipeline.py` | FASTQ → aligner → TEcount → count matrix. Subcommands `index`, `run`, `merge`. |
| `nesy_rules.py` | The rule engine: 5 rules, proof trees, path-admissibility grammar. |
| `te_reason.py` | The query engine: `explain(gene)`, plus the citation gate. |
| `extract_lit.py` | Rule-based literature extractor. **Kept but not used** — it failed validation; see CRITIQUE.md. |

### Graph data
| File | Rows | What it is |
|---|---|---|
| `nodes.csv` | 1,350 | every node with its type |
| `edges_curated.csv` | 2,792 | GO, STRING, Reactome, Complex Portal |
| `edges_mechanism.csv` | 40 | which genes write/erase which chromatin marks |
| `edges_literature.csv` | 32 | PubMed-extracted, PMID per edge |
| `edges_measured.csv` | 10 | from this project's own RNA-seq run |
| `te_subfamilies_hg38.csv` | 1,057 | the TE vocabulary from RepeatMasker |
| `encode_kd_inventory.csv` | 1,114 | every ENCODE knockdown experiment available to run |

### Outputs
| File | What it is |
|---|---|
| `demo.html` | open in a browser — the query surface, 8 genes |
| `deseq2_results.csv` | full differential-expression table |
| `examples.json` | machine-readable engine output for the worked genes |
| `fig_measured_volcano.png` | the measured result |
| `fig_inference_chain.png` | how one measurement propagates to eight genes |

### Documents
`schema.md` (the data model and the argument), `report.md` (results), `CRITIQUE.md` (honest
assessment), `RUNBOOK.md` (commands + demo path), `modal_setup.md` (cloud scale-up), this manual.

---

## 4. Running it

### 4.1 Setup

Two environments. The pipeline needs bioinformatics tools; the analysis needs Python science
packages.

```bash
conda create -n te-pipeline -c conda-forge -c bioconda \
    python=3.10 star samtools seqtk sra-tools hisat2 pysam pandas numpy scipy
conda activate te-pipeline && pip install TEtranscripts

conda create -n te-analysis python=3.11 pandas numpy scipy matplotlib networkx
conda activate te-analysis && pip install pydeseq2 gseapy
```

### 4.2 Get reference data (~290 MB)

```bash
mkdir -p refs && cd refs
curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz
curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr1.fa.gz
curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr19.fa.gz
curl -sSLO https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz
cd ..
```

`rmsk.txt.gz` is RepeatMasker's annotation of every repeat in the genome — this is where the TE
nodes come from. It is converted to a GTF keeping LINE/SINE/LTR/DNA/Retroposon/RC classes and
dropping loci under 100 bp (too short to assign reads to).

### 4.3 Build the index, then quantify

```bash
python te_pipeline.py index --ref-scope chr_subset --threads 9        # ~4 min
python te_pipeline.py run  --manifest manifest_core.csv \
       --ref-scope chr_subset --aligner hisat2 --reads 1500000 \
       --threads 9 --outdir results                                    # ~30 min for 11 samples
python te_pipeline.py merge --outdir results
```

**What the flags mean:**

- `--ref-scope chr_subset` — align to chr1 + chr19 only. A laptop cannot hold a full-genome
  index (needs ~32 GB RAM); these two chromosomes are TE-dense and enough to prove the method.
  Use `genome` in the cloud.
- `--aligner hisat2` — see §6.
- `--reads 1500000` — take 1.5 M reads per file instead of ~35 M. Makes a run take minutes.
- **The critical setting is inside the script, not on the command line:** `-k 100` (HISAT2) or
  `--outFilterMultimapNmax 100` (STAR) tells the aligner to report a read that matches up to
  100 places instead of discarding it. Without this, everything else is pointless.

TEcount then uses an **EM algorithm** to distribute each multi-mapping read across the repeat
copies it could have come from, in proportion to how much unique evidence each copy already
has. That is how you get per-subfamily counts from ambiguous reads.

### 4.4 Ask the engine something

```bash
python te_reason.py SETDB1 TET2 --proofs
```

Reading the output:

```
=== SETDB1  [best tier: measured]  measured=3 curated=1 literature=0 inferred=0
```
`best tier` is the strongest evidence available for this gene. `measured` beats `curated` here
because a measurement in the relevant cell type outranks a general database annotation.

```
Knocking down SETDB1 raises HERV9NC-int (...), measured in ENCODE ENCSR819PCU [e934902523d7fc8].
  citation gate: 4 sentences kept, 0 rejected
```
The bracketed string is an edge ID. Look it up in the edge CSVs to see the full provenance.
"0 rejected" means every sentence was backed.

For TET2 you get `best tier: none` and **1 sentence rejected** — the engine says there is no
evidence, and the gate throws that sentence out for citing nothing. That is correct behaviour,
not a bug.

---

## 5. How to read a proof tree

```
SUV39H1 -SILENCES-> HERV9NC-int            [inferred via R2_WRITER_TRANSFER]
  H3K9me3 -MARK_AT-> HERV9NC-int           [inferred via R1_MARK_GROUNDING]
    SETDB1 -SILENCES-> HERV9NC-int         [measured: ENCODE ENCSR819PCU]
    SETDB1 -DEPOSITS_MARK-> H3K9me3        [curated: GO:0140949]
  SUV39H1 -DEPOSITS_MARK-> H3K9me3         [curated: GO:0140949]
```

Read it bottom-up. We measured that removing SETDB1 raises HERV9NC-int. GO says SETDB1 writes
H3K9me3. Therefore H3K9me3 is probably what keeps that TE quiet (**R1**). GO also says SUV39H1
writes H3K9me3. Therefore removing SUV39H1 should also raise that TE (**R2**).

Nobody measured SUV39H1. The prediction is signed, specific, testable, and every step is a
database record or a measurement you can inspect.

The rules, in plain terms:

| Rule | Says |
|---|---|
| **R1** mark grounding | a measured writer effect makes its mark a silencing mark at that TE |
| **R2** writer transfer | other writers of that mark should silence that TE too |
| **R3** eraser inversion | *erasers* of that mark get the **opposite** sign — removing an eraser leaves more mark, so less TE |
| **R4** complex consensus | if ≥2 subunits of a complex silence a TE, attribute it to the complex |
| **R5** complex propagation | then extend it to the complex's other subunits |

R3 is why DNMT3A (writes 5mC) and TET2 (erases 5mC) end up on the same axis with opposite
predicted signs — without anyone having annotated TET2 as a TE regulator.

---

## 6. Traps that will cost you an afternoon

- **The macOS arm64 conda build of STAR is broken for alignment.** Index building works;
  mapping reports `Number of input reads | 0` and **exits successfully**. Always check
  `Log.final.out` for a nonzero read count. HISAT2 is the local substitute.
- **STAR's `--readFilesCommand` fails in restricted sandboxes** ("Failed spawning
  readFilesCommand"). Feed it uncompressed FASTQ.
- **ENCODE download URLs redirect to S3.** `www.encodeproject.org/@@download/...` 307-redirects
  to `encode-public.s3.amazonaws.com`; both hosts need network access.
- **pydeseq2 + joblib in a sandbox.** pydeseq2 hard-codes `inner_max_num_threads=1`, which only
  joblib's `loky` backend accepts, and loky fails on `os.sysconf("SC_SEM_NSEMS_MAX")`. Shim that
  one key rather than switching backend.
- **Don't feed a two-chromosome index the whole GENCODE annotation.** STAR logs every record;
  you get an 800 MB log file for nothing.
- **`--subsample stream_head` is not a random sample.** It takes the first N reads off the wire
  — 10× cheaper, fine for validation, wrong for a final number. Use `reservoir` at scale.

---

## 7. Glossary

**FASTQ** — raw sequencing reads plus per-base quality scores.
**Alignment** — finding where each read came from in the genome.
**Multi-mapping read** — a read matching several genome locations equally well.
**BAM** — compressed binary alignment file.
**GTF** — annotation file saying which genome intervals are which features.
**RepeatMasker / rmsk** — the standard annotation of every repeat in a genome.
**Subfamily** — a named group of near-identical TE copies (AluY, L1HS, HERV-K).
**log2 fold change** — doubling = +1, halving = −1.
**padj / FDR** — p-value corrected for testing thousands of features. `padj < 0.1` means ~10%
of calls at that threshold are expected to be false.
**Knockdown / knockout** — experimentally removing a gene's function (shRNA, CRISPR, CRISPRi).
**H3K9me3** — a repressive histone mark, the main one over TEs.
**5mC** — DNA methylation; also repressive.
**Writer / eraser** — enzymes that add / remove a chromatin mark.
**Tractability** — how amenable a protein is to being drugged.
**Forward chaining** — applying if-then rules repeatedly until nothing new is derived.
