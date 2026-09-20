.DEFAULT_GOAL := help
SHELL := /bin/bash
REFS   := refs
OUT    := results
GRAPH  := data/graph
THREADS ?= 8
READS  ?= 1500000
SCOPE  ?= chr_subset
ALIGNER ?= hisat2
GENE   ?= SETDB1

.PHONY: help refs annotation graph index smoke de tractability signatures query clean-results

help:  ## show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	 | awk 'BEGIN{FS=":.*?## "}{printf "  \033[1m%-14s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  variables: THREADS=$(THREADS) READS=$(READS) SCOPE=$(SCOPE) ALIGNER=$(ALIGNER)"

refs:  ## download RepeatMasker, GENCODE and chr1+chr19 (~290 MB)
	@mkdir -p $(REFS)
	cd $(REFS) && \
	[ -s rmsk.hg38.txt.gz ]   || curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/rmsk.txt.gz && mv -n rmsk.txt.gz rmsk.hg38.txt.gz 2>/dev/null || true ; \
	cd $(REFS) && \
	[ -s chr1.fa.gz ]  || curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr1.fa.gz ; \
	[ -s chr19.fa.gz ] || curl -sSLO https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr19.fa.gz ; \
	[ -s gencode.v44.gtf.gz ] || curl -sSL -o gencode.v44.gtf.gz https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz
	@cd $(REFS) && [ -s gencode.v44.gtf ] || gunzip -c gencode.v44.gtf.gz > gencode.v44.gtf
	@cd $(REFS) && awk -F'\t' '$$1=="chr1" || $$1=="chr19" || /^#/' gencode.v44.gtf > gencode.v44.chr1_chr19.gtf
	@ls -la $(REFS)

annotation:  ## RepeatMasker -> TE GTF + subfamily vocabulary
	python src/build_te_annotation.py --rmsk $(REFS)/rmsk.hg38.txt.gz --outdir $(REFS) \
	  --subset chr1 chr19

graph:  ## curated + chromatin-mark edge layers (network, ~10 min)
	python src/build_graph.py --outdir $(GRAPH)

index:  ## build the aligner index
	python src/te_pipeline.py index --ref-scope $(SCOPE) --threads $(THREADS)

smoke:  ## quantify the 2-sample smoke manifest end to end
	python src/te_pipeline.py run --manifest data/manifests/manifest_smoke.csv \
	  --ref-scope $(SCOPE) --aligner $(ALIGNER) --reads $(READS) --threads $(THREADS) \
	  --outdir $(OUT)
	python src/te_pipeline.py merge --outdir $(OUT)

de:  ## differential expression -> measured edges (per-feature AND set-level)
	python src/run_de.py --counts $(OUT)/counts_matrix.tsv \
	  --manifest data/manifests/manifest_core.csv --outdir $(OUT)

tractability:  ## annotate graph genes with Open Targets + ChEMBL druggability
	python src/annotate_tractability.py --graph $(GRAPH) --results $(OUT) \
	  --out $(OUT)/targets_tractability.csv

signatures:  ## interferon / senescence set-level tests (with coverage guard)
	python src/score_signatures.py --counts $(OUT)/counts_matrix.tsv \
	  --de $(OUT)/deseq2_results.csv --gtf $(REFS)/gencode.v44.gtf \
	  --outdir $(OUT) --scope-chroms chr1 chr19

query:  ## ask the engine about a gene:  make query GENE=TET2
	python src/te_reason.py $(GENE) --proofs

clean-results:  ## remove generated results, keep references and graph
	rm -rf $(OUT)/align $(OUT)/fastq $(OUT)/counts
