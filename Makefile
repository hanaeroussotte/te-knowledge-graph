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

.PHONY: help validate refs annotation graph index smoke de tractability signatures query clean-results

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

test:  ## regression (proof trees, rule firing, edge context) + claim audit
	python tests/audit_claims.py
	python tests/test_regression.py

derived:  ## export inferred edges with their inherited context
	python src/te_reason.py TET2 --export-derived results/derived_edges.csv

gate:  ## FULL pre-push gate — nothing is committed until this passes
	@echo "--- 1/7 regenerate derived edges from the graph"
	@$(MAKE) --no-print-directory derived
	@echo "--- 2/7 claim audit (retracted wording, dangling refs, blank context, registry)"
	@python tests/audit_claims.py
	@echo "--- 3/7 every cited DOI and PMID resolves"
# NO PIPE HERE. `python ... | tail -3` reports tail's exit status, not python's, so a
# failing citation check printed AUDIT FAIL and the gate still said GATE PASSED. A check
# whose failure cannot fail the gate is worse than no check at all.
	@python tests/check_citations.py
	@echo "--- 4/7 proof-tree + structured conclusion regression"
	@python tests/test_regression.py
	@echo "--- 5/7 figures regenerate from saved tables"
	@python src/make_figures.py --outdir figures
	@echo "--- 6/7 every script parses"
	@for f in src/*.py tests/*.py; do python -c "import ast;ast.parse(open('$$f').read())" || exit 1; done
	@echo "--- 7/7 review the diff yourself before committing:"
	@git status --short
	@echo "GATE PASSED — now read the diff above, then commit."

ship:  ## gate, then stage — refuses to stage anything if the gate fails.  make ship M="msg"
# The gate is only a gate if something depends on its exit status. Running `make gate`
# and then `git commit` as two statements in one shell line does NOT gate anything:
# the commit runs regardless. That mistake was made, and the fix is this target, where
# `&&` makes staging conditional on the gate passing.
	@$(MAKE) --no-print-directory gate && git add -A && \
	  echo && echo "staged. now:  git commit -m \"...\"  &&  git push origin main"

figures:  ## regenerate both panel figures from results/*.csv
	python src/make_figures.py --outdir figures

migrate-context:  ## add cell type / modality / assay / resolution columns to every edge file
	python src/migrate_edge_context.py --apply

prior-art:  ## show the prior-art record behind every novelty claim
	@python -c "import pandas as pd; d=pd.read_csv('data/graph/prior_art.csv',keep_default_na=False); \
	print(d.groupby('verdict').size().to_string()); print(); \
	print(d[['claim_id','verdict','precedent','doi']].to_string(index=False))"

panel:  ## splice signature gene loci into the reference so the inflammation arm is measurable
	python src/build_panel_reference.py spec  --gtf $(REFS)/gencode.v44.gtf \
	  --in-scope chr1,chr19 --outdir data/graph
	python src/build_panel_reference.py build --gtf $(REFS)/gencode.v44.gtf \
	  --spec data/graph/panel_spec.csv --outdir $(REFS)
	cat $(REFS)/chr1.fa $(REFS)/chr19.fa $(REFS)/panel.fa > $(REFS)/chr1_chr19_panel_m.fa
	cat $(REFS)/gencode.v44.chr1_chr19.gtf $(REFS)/panel.gtf \
	  > $(REFS)/gencode.v44.chr1_chr19.panel.gtf
	hisat2-build -p 8 $(REFS)/chr1_chr19_panel_m.fa $(REFS)/hisat2/chr1_chr19_panel_m

de-panel:  ## re-quantify + DE + signatures on the panel-augmented reference
	python src/te_pipeline.py run --ref-scope chr_subset_panel --aligner hisat2 \
	  --manifest data/manifests/manifest_core.csv --outdir results_panel \
	  --reads 1500000 --threads 8 --stranded no --mode multi
	python src/te_pipeline.py merge --outdir results_panel
	python src/run_de.py --counts results_panel/counts_matrix.tsv \
	  --manifest data/manifests/manifest_core.csv --outdir results_panel
	python src/score_signatures.py --counts results_panel/counts_matrix.tsv \
	  --de results_panel/deseq2_results.csv --gtf $(REFS)/gencode.v44.gtf \
	  --outdir results_panel --scope-chroms chr1 chr19

query:  ## ask the engine about a gene:  make query GENE=TET2
	python src/te_reason.py $(GENE) --proofs

clean-results:  ## remove generated results, keep references and graph
	rm -rf $(OUT)/align $(OUT)/fastq $(OUT)/counts

validate:  ## structural audit of the graph: schema, hygiene, provenance, reasoning capacity
	python src/validate_graph.py
