# Runbook

## Rebuild everything from scratch

```bash
# 1. references (~290 MB download, 5 min)
mkdir -p refs && cd refs
curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz
curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr1.fa.gz
curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr19.fa.gz
curl -sSLO https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz
cd ..

# 2. TE annotation from RepeatMasker -> hg38_rmsk_TE.gtf (+ chr subset)
#    see build_te_annotation in the saved lineage; keeps LINE/SINE/LTR/DNA/Retroposon/RC,
#    drops loci < 100 bp, emits TEtranscripts-style gene_id/transcript_id/family_id/class_id

# 3. index (chr subset ~4 min; full genome 45-70 min)
python te_pipeline.py index --ref-scope chr_subset --threads 9

# 4. quantify
python te_pipeline.py run --manifest manifest_core.csv --ref-scope chr_subset \
    --aligner hisat2 --reads 1500000 --threads 9 --outdir results_smoke
python te_pipeline.py merge --outdir results_smoke

# 5. query the engine
python te_reason.py SETDB1 TRIM28 SUV39H1 KDM4A DNMT3A TET2 --json out/examples.json --proofs
```

Network allowlist: `hgdownload.soe.ucsc.edu`, `www.encodeproject.org`,
`encode-public.s3.amazonaws.com` (ENCODE `/@@download/` 307-redirects there), `ftp.ebi.ac.uk`.

## Scale-up on Modal

One config change, once the target is connected (see `modal_setup.md`):

```bash
python te_pipeline.py index --ref-scope genome --threads 16          # cache in a Volume
python te_pipeline.py run --manifest manifest_full.csv \
    --ref-scope genome --aligner star --subsample reservoir \
    --reads 20000000 --threads 8 --outdir results_full
```

Build `manifest_full.csv` from `encode_kd_inventory.csv`: filter `has_fastq == True`, take the
targets you want, join each experiment to its `controls` accession.

**Verify before fanning out to 50 containers:** run one sample and confirm
`Log.final.out` reports a nonzero `Number of input reads`. The macOS arm64 STAR build reports
success with zero reads; check rather than assume.

## Demo path

Show the artifacts in this order. The argument builds; don't start with the pipeline.

1. **`schema.md` §1** — no public KG has a TE node type. State the gap before showing anything.
   Thirty seconds, and it frames everything after it.
2. **`fig_measured_volcano.png`** — real numbers. "TRIM28 knockdown, AluY up, padj 0.0005.
   That is the control I ran first, because if a known silencer doesn't derepress its target
   my pipeline is broken."
3. **`fig_inference_chain.png`** — the money slide. One measurement plus two GO annotations
   give eight unassayed genes a signed prediction, with writers and erasers getting opposite
   signs. Nobody measured SUV39H1 here.
4. **`te_reason.py TET2`** live — it says there is no evidence, and the citation gate rejects
   the sentence for citing nothing. Then explain *why* TET2 is hard: no GO annotation, no
   ENCODE knockdown, reachable only through 5mC, and 5mC needs a measured DNMT1 effect that
   this depth could not resolve. This is the strongest thirty seconds in the deck — it shows
   the tool refusing to make something up, and names exactly what compute buys.
5. **`lit_extractor_validation.csv`** if challenged on the literature layer: the cheap
   extractor was built, measured at P=0.11 with chance-level direction agreement, and dropped.

## Questions to expect

**"How do you know the multi-mapping reads are assigned correctly?"** TEcount's EM
redistribution, and the control: known silencers derepress their known targets, which would not
happen if assignment were arbitrary.

**"Isn't the inference layer just a heuristic?"** Yes, and it is tiered as one. R2 assumes
writers of a mark are interchangeable at a locus; that is stated in the rule text and the
output never calls it curated.

**"Where is the link prediction?"** Not built. It was gated on having a gene × TE matrix big
enough to hold out a validation set; three knockdowns is not. An unvalidated AUC is worse than
no model.

**"Does this generalise past K562?"** Not demonstrated. Everything measured here is one cell
line.
