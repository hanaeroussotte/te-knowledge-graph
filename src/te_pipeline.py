#!/usr/bin/env python3
"""
te_pipeline.py — TE-aware RNA-seq quantification.

FASTQ -> subsample -> STAR (multi-mapping permissive) -> TEcount -> gene+TE count matrix.

The point of this pipeline is the part standard RNA-seq throws away. Default aligner
settings report one alignment per read and discard reads that map to many places; TEs
are repeated by definition, so those are exactly the reads that carry TE signal. STAR is
therefore run with --outFilterMultimapNmax 100 / --winAnchorMultimapNmax 100 so that
multi-mapping reads survive into the BAM, and TEcount redistributes them across repeat
loci with an EM procedure (Jin et al. 2015, Bioinformatics 31:3593).

Identical invocation locally and on Modal — only --ref-scope and --threads change.

  # one-time index build
  python te_pipeline.py index --ref-scope chr_subset --threads 8

  # quantify a manifest
  python te_pipeline.py run --manifest manifest.csv --ref-scope chr_subset \
      --reads 2000000 --threads 8 --outdir results/

Manifest columns: sample, experiment, target_gene, condition (kd|control), fastq_url_1,
fastq_url_2 (blank for single-end). `python te_pipeline.py manifest --help` builds one
from the ENCODE inventory.
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

REFS = Path("refs")
SCOPES = {
    # scope -> (fasta list, TE gtf, gene gtf, star index dir, genomeSAindexNbases)
    # The gene GTF is scoped too: feeding STAR the whole of GENCODE when the index holds
    # two chromosomes makes it log and process ~93% irrelevant records (an 800 MB Log.out).
    "chr_subset": ([REFS / "chr1.fa", REFS / "chr19.fa"],
                   REFS / "hg38_rmsk_TE.chr1_chr19.gtf",
                   REFS / "gencode.v44.chr1_chr19.gtf",
                   REFS / "star_chr1_chr19", 13),
    "genome":     ([REFS / "GRCh38.primary_assembly.genome.fa"],
                   REFS / "hg38_rmsk_TE.gtf",
                   REFS / "gencode.v44.gtf",
                   REFS / "star_GRCh38", 14),
}


def sh(cmd, **kw):
    print("+", " ".join(map(str, cmd)), flush=True)
    t0 = time.time()
    subprocess.run(list(map(str, cmd)), check=True, **kw)
    print(f"  [{time.time() - t0:.1f}s]", flush=True)


def gunzip_if_needed(p: Path) -> Path:
    """refs ship gzipped; STAR and TEcount want plain text."""
    if p.exists():
        return p
    gz = Path(str(p) + ".gz")
    if not gz.exists():
        sys.exit(f"missing reference: {p} (and {gz})")
    sh(["bash", "-c", f"gunzip -c {gz} > {p}"])
    return p


# --------------------------------------------------------------------------- index
def cmd_index(a):
    fastas, _, gencode, idx, sa_n = SCOPES[a.ref_scope]
    fastas = [gunzip_if_needed(f) for f in fastas]
    gencode = gunzip_if_needed(gencode)
    idx.mkdir(parents=True, exist_ok=True)
    sh(["STAR", "--runMode", "genomeGenerate", "--runThreadN", a.threads,
        "--genomeDir", idx, "--genomeFastaFiles", *fastas,
        "--sjdbGTFfile", gencode, "--sjdbOverhang", a.sjdb_overhang,
        "--genomeSAindexNbases", sa_n,
        "--outFileNamePrefix", str(idx) + "/_"])
    print(f"index ready: {idx}")


# ------------------------------------------------------------------------- fetch/sub
def fetch_and_subsample(url: str, dest: Path, n_reads: int | None,
                        mode: str = "stream_head", seed: int = 42) -> Path:
    """Get a FASTQ, optionally subsampled.

    Subsampling is what makes the pipeline debuggable: a 1-2M read subset runs in minutes
    and exercises every step. It is NOT a substitute for full depth in the final result —
    TE loci are individually low-expressed, and depth drives how many clear FDR.

    mode="reservoir": download the whole file, then `seqtk sample` a uniform random subset.
        Statistically clean, but pulls the full ~2 GB per file.
    mode="stream_head": take the first n_reads straight off the wire and let curl stop
        there. ~10x less transfer. The cost is that the head of an Illumina FASTQ is not a
        random draw — early reads cluster by flowcell tile, so per-sample quality and
        duplication can skew slightly. Applied identically to every sample it is fine for
        pipeline validation and for relative comparisons; it is not what you would report
        as a final quantification. Use "reservoir" for the genome-scale run.
    """
    if n_reads is None:
        raw = dest.with_suffix(".raw.fastq.gz")
        if not raw.exists():
            sh(["curl", "-sSL", "--retry", "3", "-o", raw, url])
        return raw
    if mode == "stream_head" and str(dest).endswith(".gz"):
        dest = Path(str(dest)[:-3])      # written uncompressed; STAR reads it directly
    if dest.exists():
        return dest
    if mode == "stream_head":
        # `head` closing the pipe kills curl with SIGPIPE — that is the intended early
        # stop, not an error, so pipefail cannot be used here. Validate the output
        # instead: a truncated or 403'd download otherwise produces an empty .gz that
        # STAR only complains about ten confusing lines later.
        tmp = dest.with_suffix(".part")
        sh(["bash", "-c",
            f"curl -sSL --retry 3 '{url}' | gunzip -c | head -n {n_reads * 4} > {tmp}"])
        n = int(subprocess.run(["bash", "-c", f"wc -l < {tmp}"],
                               capture_output=True, text=True, check=True).stdout.strip())
        if n == 0:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"empty download for {url} — blocked, expired or moved")
        if n % 4:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"truncated FASTQ for {url}: {n} lines is not a multiple of 4")
        print(f"  fetched {n // 4:,} reads", flush=True)
        tmp.rename(dest)
    else:
        raw = dest.with_suffix(".raw.fastq.gz")
        if not raw.exists():
            sh(["curl", "-sSL", "--retry", "3", "-o", raw, url])
        sh(["bash", "-c", f"seqtk sample -s{seed} {raw} {n_reads} | gzip > {dest}"])
    return dest


# ----------------------------------------------------------------------------- align
def star_align(idx: Path, fq1: Path, fq2: Path | None, prefix: Path, threads: int) -> Path:
    bam = Path(str(prefix) + "Aligned.out.bam")
    if bam.exists():
        return bam
    reads = [fq1] + ([fq2] if fq2 else [])
    # No --readFilesCommand: STAR spawns it through a shell + fifo, which fails in
    # restricted execution sandboxes ("Failed spawning readFilesCommand"). Handing STAR
    # plain uncompressed FASTQ costs disk but removes the failure mode entirely.
    if any(str(r).endswith(".gz") for r in reads):
        plain = []
        for r in reads:
            p = Path(str(r)[:-3]) if str(r).endswith(".gz") else Path(r)
            if not p.exists():
                sh(["bash", "-c", f"gunzip -c {r} > {p}"])
            plain.append(p)
        reads = plain
    sh(["STAR", "--runThreadN", threads, "--genomeDir", idx,
        "--readFilesIn", *reads,
        "--outFileNamePrefix", prefix,
        "--outSAMtype", "BAM", "Unsorted",
        # --- the TE-critical settings -------------------------------------------
        "--outFilterMultimapNmax", 100,      # keep reads mapping to <=100 places
        "--winAnchorMultimapNmax", 100,      # allow those loci to seed alignment
        "--outSAMattributes", "NH", "HI", "AS", "nM",   # TEcount needs NH/HI
        # ------------------------------------------------------------------------
        "--outFilterMismatchNoverLmax", 0.04,
        "--alignIntronMax", 1000000, "--alignMatesGapMax", 1000000,
        "--outSAMunmapped", "None"])
    return bam


def hisat2_align(idx_prefix: Path, fq1: Path, fq2: Path | None, prefix: Path, threads: int) -> Path:
    """HISAT2 alternative to STAR.

    Present because the conda osx-arm64 STAR build silently reads zero reads — the genome
    loads, the run reports success, and Log.final.out says "Number of input reads | 0".
    Rather than debug someone else's binary, the local validation runs HISAT2 and the
    cloud path keeps STAR, which is what the published TEtranscripts workflow assumes.
    Both are run with -k 100 / --outFilterMultimapNmax 100 so the multi-mapping reads that
    carry TE signal survive into the BAM either way.
    """
    bam = Path(str(prefix) + "Aligned.out.bam")
    if bam.exists():
        return bam
    sam = Path(str(prefix) + "tmp.sam")
    reads = ["-1", fq1, "-2", fq2] if fq2 else ["-U", fq1]
    sh(["bash", "-c",
        "hisat2 -p {t} -x {x} {r} -k 100 --summary-file {s} -S {sam}".format(
            t=threads, x=idx_prefix, r=" ".join(map(str, reads)),
            s=str(prefix) + "hisat2.summary", sam=sam)])
    sh(["bash", "-c", f"samtools view -@ {threads} -b -o {bam} {sam} && rm -f {sam}"])
    return bam


def tecount(bam: Path, te_gtf: Path, gencode: Path, project: Path, stranded: str, mode: str):
    out = Path(str(project) + ".cntTable")
    if out.exists():
        return out
    # No --sortByPos: STAR writes BAM Unsorted, i.e. grouped by read name, which is what
    # TEcount's paired-end handling needs. Declaring position-sorted input on a name-ordered
    # BAM makes it silently mispair mates.
    sh(["TEcount", "-b", bam, "--GTF", gencode, "--TE", te_gtf,
        "--mode", mode, "--stranded", stranded, "--project", project, "--verbose", "2"])
    return out


# ------------------------------------------------------------------------------- run
def cmd_run(a):
    import csv
    fastas, te_gtf, gencode, idx, _ = SCOPES[a.ref_scope]
    gencode = gunzip_if_needed(gencode)
    if not (idx / "SA").exists():
        sys.exit(f"no STAR index at {idx} — run `te_pipeline.py index --ref-scope {a.ref_scope}` first")
    out = Path(a.outdir); (out / "fastq").mkdir(parents=True, exist_ok=True)
    (out / "align").mkdir(exist_ok=True); (out / "counts").mkdir(exist_ok=True)

    rows = list(csv.DictReader(open(a.manifest)))
    manifest_out = []
    for i, r in enumerate(rows, 1):
        s = r["sample"]
        print(f"\n=== [{i}/{len(rows)}] {s}  ({r.get('target_gene')} / {r.get('condition')})", flush=True)
        try:
            fq1 = fetch_and_subsample(r["fastq_url_1"], out / "fastq" / f"{s}_1.fastq.gz",
                                      a.reads, a.subsample)
            fq2 = (fetch_and_subsample(r["fastq_url_2"], out / "fastq" / f"{s}_2.fastq.gz",
                                       a.reads, a.subsample)
                   if r.get("fastq_url_2") else None)
            if a.aligner == "hisat2":
                bam = hisat2_align(REFS / "hisat2" / idx.name.replace("star_", ""),
                                   fq1, fq2, out / "align" / f"{s}.", a.threads)
            else:
                bam = star_align(idx, fq1, fq2, out / "align" / f"{s}.", a.threads)
            cnt = tecount(bam, te_gtf, gencode, out / "counts" / s, a.stranded, a.mode)
            manifest_out.append({**r, "bam": str(bam), "counts": str(cnt), "status": "ok"})
            if a.cleanup_fastq:
                for f in (out / "fastq").glob(f"{s}_*"):
                    f.unlink()
        except (subprocess.CalledProcessError, RuntimeError) as e:
            print(f"  FAILED: {e}", flush=True)
            manifest_out.append({**r, "status": f"failed: {e}"})
    json.dump(manifest_out, open(out / "run_manifest.json", "w"), indent=1)
    ok = sum(m["status"] == "ok" for m in manifest_out)
    print(f"\n{ok}/{len(rows)} samples quantified -> {out}")


# ----------------------------------------------------------------------------- merge
def cmd_merge(a):
    import pandas as pd
    out = Path(a.outdir)
    frames = {}
    for f in sorted((out / "counts").glob("*.cntTable")):
        s = f.name.replace(".cntTable", "")
        frames[s] = pd.read_csv(f, sep="\t", index_col=0).iloc[:, 0]
    if not frames:
        sys.exit(f"no .cntTable files under {out/'counts'}")
    m = pd.DataFrame(frames).fillna(0).astype(int)
    m.index.name = "feature"
    # TEcount emits TE features as "subfamily:family:class"; genes keep ENSG ids
    m["feature_type"] = ["TE" if str(i).count(":") == 2 else "gene" for i in m.index]
    m.to_csv(out / "counts_matrix.tsv", sep="\t")
    print(m.feature_type.value_counts().to_string())
    print(f"matrix: {m.shape[0]} features x {m.shape[1]-1} samples -> {out/'counts_matrix.tsv'}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("index", help="build the STAR index")
    pi.add_argument("--ref-scope", choices=SCOPES, default="chr_subset")
    pi.add_argument("--threads", type=int, default=os.cpu_count())
    pi.add_argument("--sjdb-overhang", type=int, default=100)
    pi.set_defaults(func=cmd_index)

    pr = sub.add_parser("run", help="quantify every sample in a manifest")
    pr.add_argument("--manifest", required=True)
    pr.add_argument("--ref-scope", choices=SCOPES, default="chr_subset")
    pr.add_argument("--outdir", default="results")
    pr.add_argument("--reads", type=int, default=2_000_000,
                    help="subsample to N reads per file; 0 = full depth")
    pr.add_argument("--threads", type=int, default=os.cpu_count())
    pr.add_argument("--aligner", choices=["star", "hisat2"], default="star",
                    help="star for the cloud run; hisat2 for local validation on macOS "
                         "where the conda STAR build reads zero reads")
    pr.add_argument("--subsample", choices=["stream_head", "reservoir"], default="stream_head",
                    help="stream_head is ~10x less transfer but not a random draw; "
                         "reservoir downloads in full and samples uniformly")
    pr.add_argument("--stranded", choices=["yes", "no", "reverse"], default="no")
    pr.add_argument("--mode", choices=["multi", "uniq"], default="multi")
    pr.add_argument("--cleanup-fastq", action="store_true")
    pr.set_defaults(func=cmd_run)

    pm = sub.add_parser("merge", help="merge per-sample count tables")
    pm.add_argument("--outdir", default="results")
    pm.set_defaults(func=cmd_merge)

    a = p.parse_args()
    if getattr(a, "reads", None) == 0:
        a.reads = None
    a.func(a)


if __name__ == "__main__":
    main()
