#!/usr/bin/env python3
"""
modal_app.py — fan out TE quantification across perturbation experiments on Modal.

    modal run src/modal_app.py --manifest data/manifests/manifest_prospective.csv
    modal run src/modal_app.py --manifest data/manifests/manifest_core.csv --reads 0

    # no Modal account needed — validates the plan and the manifest locally:
    python src/modal_app.py --dry-run --manifest data/manifests/manifest_prospective.csv

Why this is the right shape for elastic compute
-----------------------------------------------
Exactly one step of this project needs it: align + quantify, per library. Those jobs are
independent (no cross-talk), CPU/RAM-bound, and all read the same large reference index.
That is the pattern this kind of compute is for — fan out N containers over a shared
read-only Volume, collect small CSVs, shut down.

Everything else stays local and cheap: DESeq2 on the merged matrix takes seconds, and the
rule engine reaches a fixpoint over ~9,400 edges in under a second. Putting those in the
cloud would be theatre.

**There is no GPU step and this app does not request one.** Alignment and TE
quantification are CPU- and memory-bound. Claiming a GPU to look impressive would be
noticed by anyone who has run this pipeline.

Honest comparison: Nextflow or Snakemake on AWS Batch, or a Slurm cluster, would execute
the same DAG perfectly well, and for a production facility with a working stack that is
probably the better choice. The advantage here is that the *agent decides at runtime*
which perturbations are worth computing — from the state of the evidence, not from a DAG
written in advance — and can launch that as a Python call without anyone provisioning a
cluster. See docs/COMPUTE.md.

Cost control
------------
`--reads` subsamples each library (default 1.5M for a smoke run, `0` = full depth).
`--max-containers` caps fan-out. The reference Volume is built once by `build_reference`
and mounted read-only by every worker, so a 300 Mb index is not downloaded N times.
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path

# ---------------------------------------------------------------- Modal app definition
# Imported lazily so that --dry-run works with no modal package installed.
APP_NAME = "te-perturbation-atlas"
REF_VOLUME = "te-refs"
RESULTS_VOLUME = "te-results"

APT = ["curl", "gzip", "pigz"]
CONDA = ["hisat2", "star", "samtools", "seqtk"]          # bioconda
PIP = ["TEtranscripts", "pandas", "numpy", "scipy", "pydeseq2"]


def build_image(modal):
    """One image, built once, cached by Modal. Bioconda for the aligners because they are
    not on PyPI; pip for TEtranscripts, which is."""
    return (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install(*APT)
        .micromamba(python_version="3.11")
        .micromamba_install(*CONDA, channels=["bioconda", "conda-forge"])
        .pip_install(*PIP)
        # the pipeline module itself, so workers run the same code as local runs
        .add_local_python_source("te_pipeline")
    )


def make_app(modal):
    app = modal.App(APP_NAME)
    image = build_image(modal)
    refs = modal.Volume.from_name(REF_VOLUME, create_if_missing=True)
    out = modal.Volume.from_name(RESULTS_VOLUME, create_if_missing=True)

    @app.function(image=image, volumes={"/refs": refs}, cpu=8.0, memory=32768,
                  timeout=60 * 60 * 6)
    def build_reference(scope: str = "genome"):
        """Build the aligner index ONCE into the shared Volume. Every worker mounts it
        read-only, so this cost is paid a single time rather than N times."""
        import subprocess
        os.makedirs("/refs", exist_ok=True)
        if scope == "genome":
            urls = {
                "GRCh38.primary_assembly.genome.fa.gz":
                    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/"
                    "GRCh38.primary_assembly.genome.fa.gz",
                "gencode.v44.gtf.gz":
                    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/"
                    "gencode.v44.annotation.gtf.gz",
            }
            for name, url in urls.items():
                p = f"/refs/{name}"
                if not os.path.exists(p.replace(".gz", "")):
                    subprocess.run(["curl", "-sSL", "--retry", "3", "-o", p, url], check=True)
                    subprocess.run(["bash", "-c", f"pigz -d -f {p}"], check=True)
        idx = "/refs/hisat2/GRCh38"
        if not os.path.exists(idx + ".1.ht2"):
            os.makedirs("/refs/hisat2", exist_ok=True)
            subprocess.run(["hisat2-build", "-p", "8",
                            "/refs/GRCh38.primary_assembly.genome.fa", idx], check=True)
        refs.commit()
        return sorted(os.listdir("/refs"))

    @app.function(image=image, volumes={"/refs": refs, "/out": out},
                  cpu=4.0, memory=16384, timeout=60 * 60 * 4, retries=2)
    def quantify(row: dict, reads: int, te_gtf: str, gene_gtf: str) -> dict:
        """One library: fetch -> (subsample) -> align -k 100 -> TEcount -> counts CSV.

        Runs in its own container. `retries=2` because the failure mode here is a flaky
        download from a data portal, which is worth retrying; a genuine pipeline error
        will fail all three times and show up in the returned dict rather than silently
        producing an empty count table."""
        import subprocess, tempfile
        sample = row["sample"]
        wd = tempfile.mkdtemp(prefix=f"{sample}_")
        try:
            fqs = []
            for key in ("fastq_url_1", "fastq_url_2"):
                url = row.get(key)
                if not url:
                    continue
                dest = f"{wd}/{sample}_{key[-1]}.fastq"
                if reads:
                    # head-limited stream: curl is killed by SIGPIPE once head closes the
                    # pipe, which is the intended early stop, so pipefail cannot be used
                    subprocess.run(["bash", "-c",
                                    f"curl -sSL --retry 3 '{url}' | gzip -dc | "
                                    f"head -n {reads * 4} > {dest}"], check=True)
                else:
                    subprocess.run(["bash", "-c",
                                    f"curl -sSL --retry 3 '{url}' | gzip -dc > {dest}"],
                                   check=True)
                n = int(subprocess.run(["bash", "-c", f"wc -l < {dest}"], check=True,
                                       capture_output=True, text=True).stdout.strip())
                if n == 0 or n % 4:
                    raise RuntimeError(f"{sample}: bad FASTQ ({n} lines) from {key}")
                fqs.append(dest)

            sam = f"{wd}/{sample}.sam"
            rd = ["-1", fqs[0], "-2", fqs[1]] if len(fqs) == 2 else ["-U", fqs[0]]
            subprocess.run(["hisat2", "-p", "4", "-x", "/refs/hisat2/GRCh38", *rd,
                            "-k", "100", "--summary-file", f"{wd}/{sample}.summary",
                            "-S", sam], check=True)
            bam = f"{wd}/{sample}.bam"
            # name-ordered, NOT position-sorted: TEcount's paired-end handling needs reads
            # grouped by name, and telling it otherwise makes it silently mis-pair mates
            subprocess.run(["bash", "-c", f"samtools view -@4 -b {sam} > {bam}"], check=True)
            subprocess.run(["TEcount", "-b", bam, "--GTF", gene_gtf, "--TE", te_gtf,
                            "--mode", "multi", "--stranded", "no",
                            "--project", f"/out/{sample}"], check=True)
            out.commit()
            return {"sample": sample, "status": "ok",
                    "counts": f"/out/{sample}.cntTable"}
        except Exception as e:
            return {"sample": sample, "status": f"failed: {type(e).__name__}: {e}"}
        finally:
            subprocess.run(["rm", "-rf", wd], check=False)

    return app, build_reference, quantify


# ------------------------------------------------------------------------------ driver
def read_manifest(path: str) -> list[dict]:
    import csv
    rows = list(csv.DictReader(open(path)))
    need = {"sample", "fastq_url_1"}
    for r in rows:
        missing = need - {k for k, v in r.items() if v}
        if missing:
            raise SystemExit(f"manifest row {r.get('sample')!r} missing {missing}")
    return rows


def dry_run(rows: list[dict], reads: int, cap: int):
    """Validate the plan without Modal. Prints what would be dispatched, so a manifest
    error is caught before anyone spends credits on it."""
    print(f"app            {APP_NAME}")
    print(f"volumes        {REF_VOLUME} (ro, shared), {RESULTS_VOLUME} (rw)")
    print(f"image          debian_slim + {'/'.join(CONDA)} + {'/'.join(PIP[:2])}…")
    print(f"resources      build_reference: 8 CPU / 32 GB · quantify: 4 CPU / 16 GB · no GPU")
    print(f"fan-out        {len(rows)} libraries, max {cap} concurrent")
    print(f"depth          {'full' if not reads else f'{reads:,} reads/library'}")
    print()
    for r in rows:
        pe = "PE" if r.get("fastq_url_2") else "SE"
        print(f"  {r['sample']:<26} {r.get('target_gene',''):<10} "
              f"{r.get('condition',''):<8} {pe}  {r.get('experiment','')}")
    print(f"\nDRY RUN — nothing dispatched. Remove --dry-run and use "
          f"`modal run src/modal_app.py` to execute.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default="data/manifests/manifest_core.csv")
    ap.add_argument("--reads", type=int, default=1_500_000,
                    help="subsample depth per library; 0 = full depth")
    ap.add_argument("--max-containers", type=int, default=32)
    ap.add_argument("--ref-scope", default="genome", choices=["genome", "chr_subset"])
    ap.add_argument("--te-gtf", default="/refs/hg38_rmsk_TE.gtf")
    ap.add_argument("--gene-gtf", default="/refs/gencode.v44.gtf")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--build-reference-only", action="store_true")
    a = ap.parse_args()

    rows = read_manifest(a.manifest)
    if a.dry_run:
        return dry_run(rows, a.reads, a.max_containers)

    try:
        import modal
    except ImportError:
        raise SystemExit("modal is not installed. `pip install modal && modal token new`, "
                         "or use --dry-run to validate the plan without it.")

    app, build_reference, quantify = make_app(modal)
    with app.run():
        if a.build_reference_only:
            print(json.dumps(build_reference.remote(a.ref_scope), indent=1))
            return
        results = list(quantify.map(
            rows, kwargs={"reads": a.reads, "te_gtf": a.te_gtf, "gene_gtf": a.gene_gtf},
            order_outputs=False))
    ok = [r for r in results if r["status"] == "ok"]
    print(f"\n{len(ok)}/{len(results)} libraries quantified")
    for r in results:
        if r["status"] != "ok":
            print(f"  FAILED {r['sample']}: {r['status']}")
    Path("results").mkdir(exist_ok=True)
    json.dump(results, open("results/modal_run.json", "w"), indent=1)
    print("next: te_pipeline.py merge, then run_de.py, then te_reason.py")


if __name__ == "__main__":
    main()
