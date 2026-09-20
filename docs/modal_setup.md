# Connecting Modal, and what to run when you get there

You do not need this before the hackathon. Your Modal credits land on the day; the pipeline is
already debugged against real ENCODE data, so connecting is a credential step, not a build step.

## Connect (5 minutes)

1. Sign up at modal.com. The free tier is enough to smoke-test the connection.
2. In a terminal: `pip install modal` then `modal token new`. This opens a browser, and on
   return prints a **token ID** and **token secret**.
3. In Claude Science, left sidebar → **Customize → Compute → Add**. Paste both values.
4. Ask me to re-check; the target appears immediately and I can dispatch to it.

## What the genome-scale run costs

Estimates, not measurements — nothing at genome scale has been run yet.

| Step | Resource | Wall time | Notes |
|---|---|---|---|
| Download GRCh38 + GENCODE | 1 CPU, 20 GB disk | ~10 min | once, into a Modal Volume |
| STAR index, full GRCh38 | 16 CPU, 64 GB RAM | 45–70 min | once; **cache it in the Volume or you pay it every run** |
| Per sample: fetch + align + TEcount | 8 CPU, 32 GB RAM | 15–25 min at full depth | embarrassingly parallel |
| 100 samples, 50 containers | | ~40–60 min wall | this is the fan-out worth demoing |

The index build is the only serial step. Start it the moment you arrive, then do graph work
while it runs — that is the same ordering that worked in this build.

## Order of operations on the day

1. Launch the index build first, in the background.
2. While it builds: extend `manifest_core.csv`. `encode_kd_inventory.csv` has all 1,060
   experiments with FASTQ; filter to the targets you want and pair each with its control
   (the `controls` column carries the matched control accession).
3. When the index is ready, fan out with `--ref-scope genome --aligner star --subsample reservoir`.
4. Re-run `deseq2` and `te_reason.py`; the graph layers rebuild from the new `edges_measured.csv`
   automatically.

## Two things that will bite

- **Use `--subsample reservoir` for the real run.** The default `stream_head` takes the first
  N reads off the wire, which is ~10× cheaper but is not a random draw. Fine for validation,
  wrong for a headline number.
- **`--aligner star` needs a working STAR.** On Linux x86-64 it is fine. The macOS arm64 conda
  build silently reads zero reads while reporting success — check `Log.final.out` says
  `Number of input reads | <nonzero>` on your first container before launching 50 of them.
