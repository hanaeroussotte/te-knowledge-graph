# Using this on a dataset you are handed at the hackathon

You arrive, someone gives you data and Modal credits. This is the decision tree and the exact
commands. Read §1 first — it takes two minutes and decides everything else.

---

## 1. Triage the dataset in two minutes

Ask three questions, in this order.

**Q1 — Is it raw reads (FASTQ) or a count matrix?**

| | What you can do |
|---|---|
| **FASTQ / BAM** | Everything. This is the good case — you can re-quantify TEs. |
| **Count matrix, genes only** | **You cannot recover TE signal.** The multi-mapping reads are already gone. Do not pretend otherwise. |
| **Count matrix including TE rows** | Skip to §4 — plug it straight into the graph layer. |

This is the single most important question and the answer is often "gene counts only", because
that is what most pipelines emit. If so, say plainly: *"this dataset has already discarded the
reads my method depends on"* — which is itself a demonstration of the problem the project
exists to solve.

**Q2 — Is there a perturbation with a control?**
The measured layer needs a contrast: knockdown/knockout/treatment versus a matched control,
ideally ≥2 replicates per arm. Without a contrast you can still quantify TE expression per
sample, but you cannot produce `SILENCES` / `DEREPRESSES` edges.

**Q3 — Which genome?** Human hg38/GRCh38 works out of the box. Mouse needs a different
RepeatMasker table and GENCODE (§6). Anything else is a longer job than a hackathon allows.

---

## 2. If it is FASTQ — the full path

### 2.1 Write a manifest

One CSV, six columns. This is the only file you need to create.

```csv
sample,experiment,target_gene,condition,fastq_url_1,fastq_url_2
KD_rep1,EXP01,SETDB1,kd,/data/kd1_R1.fq.gz,/data/kd1_R2.fq.gz
KD_rep2,EXP01,SETDB1,kd,/data/kd2_R1.fq.gz,/data/kd2_R2.fq.gz
CTL_rep1,EXP02,control,control,/data/c1_R1.fq.gz,/data/c1_R2.fq.gz
CTL_rep2,EXP02,control,control,/data/c2_R1.fq.gz,/data/c2_R2.fq.gz
```

- `fastq_url_*` accepts a URL **or** a local path — the fetch step handles both.
- Single-end data: leave `fastq_url_2` empty.
- `condition` must be `kd` or `control`; `target_gene` is what the edge will be named after.

### 2.2 Smoke-test before you spend credits

```bash
head -4 manifest.csv > manifest_smoke.csv        # one KD, one control
python te_pipeline.py index --ref-scope chr_subset --threads 8
python te_pipeline.py run --manifest manifest_smoke.csv --ref-scope chr_subset \
       --aligner hisat2 --reads 1000000 --threads 8 --outdir results_smoke
python te_pipeline.py merge --outdir results_smoke
```

~15 minutes. **Check three things before going further:**
1. Alignment rate in `results/align/*.summary` — expect 15–25% on the two-chromosome index
   (low is normal here; it means ~90% of the genome is absent, not that the data is bad).
2. `counts_matrix.tsv` has TE rows — grep for `:` in the feature names.
3. TE features carry non-trivial counts, not all zeros.

If any of those fail, the problem is the data or the reference, not Modal. Fix it locally
where iteration is free.

### 2.3 Scale up on Modal

```bash
python te_pipeline.py index --ref-scope genome --threads 16     # 45-70 min, cache in a Volume
python te_pipeline.py run --manifest manifest.csv --ref-scope genome \
       --aligner star --subsample reservoir --reads 20000000 \
       --threads 8 --outdir results_full
python te_pipeline.py merge --outdir results_full
```

**Three flags that must change from the local run, and why:**

| flag | local | Modal | why |
|---|---|---|---|
| `--ref-scope` | `chr_subset` | `genome` | two chromosomes miss ~83% of the interferon machinery (see §5) |
| `--aligner` | `hisat2` | `star` | the conda osx-arm64 STAR build is broken; on Linux use STAR |
| `--subsample` | `stream_head` | `reservoir` | head-of-file is not a random draw — fine for validation, not for a reported number |

**Verify on ONE container before fanning out to fifty:** `Log.final.out` must report a nonzero
`Number of input reads`. The broken STAR build reports success with zero reads.

---

## 3. If it is already a count matrix

Format it as TSV with features down the side, samples across. TE rows must be named
`subfamily:family:class` (e.g. `AluY:Alu:SINE`) — that is how the downstream code tells TEs
from genes. Genes can be Ensembl IDs or symbols.

Then run the DE and edge-building steps directly; skip `te_pipeline.py` entirely.

---

## 4. From counts to graph edges — the part that makes it *your* tool

This is the differentiator, and it is fast (minutes, no Modal needed).

1. **Differential expression** — PyDESeq2, each knockdown against its matched control, size
   factors estimated on the **joint gene + TE matrix** (never TE-only; see
   `INTERPRETING_RESULTS.md` §2).
2. **Per-feature edges** — every TE subfamily at FDR < 0.1 becomes an edge: positive log2FC →
   `SILENCES`, negative → `DEREPRESSES`, carrying log2FC, padj and the experiment accession.
3. **Set-level edge** — compare the TE log2FC distribution against the protein-coding
   distribution in the same contrast (Mann-Whitney). This is normalisation-invariant and
   catches effects per-feature FDR misses. *In our data this is the only thing that detected
   the DNMT1 effect at all.* **Do not skip it.**
4. **Re-run the rules** — `te_reason.py` reloads all edge CSVs and re-derives automatically.
   New measured edges immediately propagate to every writer and eraser of the relevant mark.
5. **Query it** — `python te_reason.py <GENE> --proofs`.

Step 4 is the demo moment: add one measurement, and genes nobody assayed acquire signed,
provable predictions.

---

## 5. Choose your reference scope deliberately

`chr_subset` was a laptop-memory compromise and it has a real analytical cost that only became
obvious when we tried to score interferon signatures:

| Gene set | On chr1+chr19 |
|---|---|
| Type I interferon response | 17% |
| Defense response to virus | 17% |
| Inflammatory response | 18% |

cGAS, STING1, IFIH1, MAVS, TBK1, STAT1/2, MX1, OAS1 and IFIT1 are all absent. **If the
question involves anything downstream of TE derepression, you need `--ref-scope genome`.**
The chromosome subset is for proving the pipeline runs, nothing else.

---

## 6. If the dataset is not human hg38

Two files to swap, both in `refs/`:

- **RepeatMasker table** — `https://hgdownload.soe.ucsc.edu/goldenPath/<db>/database/rmsk.txt.gz`
  (`mm39` for mouse). The GTF conversion is genome-agnostic: keep LINE/SINE/LTR/DNA/
  Retroposon/RC, drop loci < 100 bp.
- **Gene annotation** — matching GENCODE release. Chromosome naming must agree (`chr1`, not `1`).

Add a new entry to the `SCOPES` dict in `te_pipeline.py`. Nothing else changes.

**What does not transfer:** the curated and literature edge layers are human. GO and Complex
Portal have mouse annotations, so the curated layer can be rebuilt; the measured layer is
species-agnostic; the rule layer works unchanged.

---

## 7. Realistic timings

| Step | Where | Time |
|---|---|---|
| Triage + manifest | local | 10 min |
| Smoke test, 2 samples | local | 15 min |
| STAR index, full genome | Modal, 16 CPU / 64 GB | 45–70 min (once — cache it) |
| Per sample, full depth | Modal, 8 CPU / 32 GB | 15–25 min |
| 50 samples across 25 containers | Modal | ~45 min wall |
| DE + edges + rules + query | local | < 5 min |

**Start the index build first, then do everything else while it runs.** That ordering is what
made the difference in this build.

---

## 8. Failure modes, ranked by how likely they are to hit you

1. **Gene-only count matrix.** Unfixable — the reads are gone. Say so and pivot to the graph
   layer using their gene list.
2. **Wrong chromosome naming** (`1` vs `chr1`) between FASTA, GENCODE and rmsk. Silent: you
   get zero counts, not an error. Check `counts_matrix.tsv` is not all zeros.
3. **No matched control.** No contrast, no measured edges. You can still show TE quantification.
4. **Single-end reads.** Works — leave `fastq_url_2` blank. Alignment rate drops.
5. **STAR reporting zero input reads.** Check `Log.final.out`, switch to `--aligner hisat2`.
6. **Too few replicates (n=1).** DESeq2 cannot estimate dispersion. Fall back to the set-level
   Mann-Whitney test in §4.3, which needs no replicates — one more reason not to skip it.
7. **Running out of Modal credits mid-fan-out.** The pipeline skips samples whose outputs
   already exist, so re-running resumes rather than restarting.

---

## 9. The honest thing to say if the dataset does not fit

Some datasets cannot support this analysis, and the strongest move is to name that fast rather
than force it. *"This is a gene-level count matrix, so the multi-mapping reads that carry TE
signal were discarded upstream — which is exactly the structural exclusion this project is
about. Here is what I can still do with it: [graph layer, tractability, reasoning over their
gene list]."*

That is a better demo than a forced result, and it lands the core argument using their own data
as the example.
