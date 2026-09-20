# Where the compute goes, and why

## 1. The shape of this workload

The pipeline is heterogeneous, and the honest version of the architecture puts each step
where it belongs rather than pushing everything to the cloud because cloud credits exist.

| Step | Resource | Where | Why |
|---|---|---|---|
| Build TE annotation from RepeatMasker | 1 CPU, minutes | local | one-off, small |
| Build the graph (GO, STRING, Reactome, Complex Portal) | network-bound | local | ~10 min of HTTP; no compute to speak of |
| Build a reference index | 8 CPU, ~25 min, ~16 GB | either | reusable artefact — build once, mount many times |
| **Align + quantify N perturbation experiments** | **CPU + RAM, embarrassingly parallel** | **cloud** | the only step that needs it |
| DESeq2 + set-level tests | 1 CPU, seconds | local | small tables |
| Rule engine, proof trees, queries | 1 CPU, instant | local | 9,366 edges; a laptop is overkill |
| Druggability annotation | network-bound | local | API calls |

**There is no GPU step, and we do not pretend otherwise.** Alignment and TE quantification
are CPU- and memory-bound. Claiming GPU usage to look impressive would be noticed
immediately by anyone who has run this kind of pipeline.

## 2. The architecture

```
  Claude Science  ──  scientific orchestration: what to run, on what, and why
        │
        ├──► Modal fan-out: N perturbation experiments, one container each
        │        CPU/RAM jobs — align (-k 100) → TEcount → per-sample counts
        │        shared Volume: reference index + annotation, built once
        │
        ├──► collect → one count matrix
        │
        ├──► local: DESeq2, per-feature + compartment tests
        │
        ├──► local: graph ingestion, rules, proof trees
        │
        └──► Claude Science: evidence-based explanation, refusal, next experiment
```

The parallel axis is **experiments**, and it is genuinely independent: each library aligns
and quantifies without reference to any other. 570 ENCODE target genes with paired-end
FASTQ is a fan-out of a few hundred short CPU jobs against one shared reference Volume.
That is close to the ideal shape for this kind of elastic compute.

The `QUANTIFIER_ROBUSTNESS.md` experiment has the same shape on a second axis: 11 libraries
× 4 additional quantifiers = 44 independent CPU jobs, no GPU, one shared reference.

## 3. Why not Nextflow, Snakemake or an HPC cluster?

Someone will ask, and the defensible answer is not that they cannot do this.

**They can.** Nextflow or Snakemake on AWS Batch, or a Slurm cluster, would execute this
pipeline perfectly well, and for a production genomics facility with a stable stack
already in place, that is likely the better choice. Reproducible workflow managers are
mature, the scheduler is already paid for, and the team already knows it.

The advantage here is **integration speed and dynamic execution**, which matters because
of what is driving the pipeline:

- The agent decides *which* computation to run next, from the state of the evidence — for
  instance, that DNMT1's set-level result needs confirming at full depth before R1 can be
  trusted. That decision is made mid-session, not written into a DAG in advance.
- Launching it should be a Python function call that acquires compute, fans out, reuses a
  shared reference Volume and shuts down — with no cluster allocation, no queue, and no
  scientist maintaining infrastructure.
- The reference index is a large reusable asset. Building it once into a Volume and
  mounting it across a few hundred containers is exactly the pattern this needs.

So: for a mature production facility with a working Slurm/Nextflow stack, a workflow
manager is probably better. For an **AI-native exploratory system that decides at runtime
which computation would most reduce its uncertainty**, dynamic elastic compute is markedly
more convenient. That is a real distinction and it is worth stating as a trade-off rather
than a win.

## 4. What is actually parallel, and what is not

Worth being precise, because "embarrassingly parallel" is often claimed loosely:

- **Parallel:** per-library download, subsample, align, quantify. No cross-talk.
- **Parallel:** per-quantifier arms of the robustness experiment.
- **Not parallel:** DESeq2 fits a model across all samples in a contrast, so the count
  matrix must be assembled first. It is also seconds of CPU, so this does not matter.
- **Not parallel, and should not be:** the rule engine. 9,366 edges reaching a fixpoint in
  under a second. Putting this in the cloud would be theatre.

## 5. Practical notes

Setup and image definition are in `modal_setup.md`. The flags that change between a local
validation run and a real cloud run:

| | local (what produced these numbers) | cloud |
|---|---|---|
| `--ref-scope` | `chr_subset` / `chr_subset_panel` | `genome` |
| `--aligner` | `hisat2` | `star` |
| `--subsample` | `stream_head` | `reservoir` |
| `--reads` | 1500000 | full depth |

The aligner change is forced: the conda `osx-arm64` STAR build reads zero reads while
exiting 0, so local runs use HISAT2 and cloud runs use STAR. **The two have never been
compared head-to-head**, which is listed as an open falsifier — and is itself a natural
first cloud job, since it is the same libraries twice.
