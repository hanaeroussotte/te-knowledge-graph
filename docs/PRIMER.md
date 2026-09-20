# Primer — this project explained from zero

For someone with no background in genomics, no background in knowledge graphs, and no
intention of running the code. By the end you should be able to explain to somebody else what
this project does, why it is built the way it is, and what every step in it produces.

`MANUAL.md` is the operator's guide — install, commands, flags. **This document is the
explanation.** Part V is the complete numbered procedure.

---

# Part I — The biology, from nothing

## I.1 Genes, in four sentences

Your DNA is a long string in a four-letter alphabet (A, C, G, T), about 3.1 billion letters,
split across 23 chromosome pairs. Some stretches are **genes**: instructions for building
proteins. To use a gene, the cell copies it into **RNA** (this is *transcription*), and the RNA
is then read to build a protein.

Measuring which genes are switched on, and how strongly, means measuring **how much RNA of each
kind is present**. That is what RNA sequencing does.

## I.2 What a transposable element is

Here is the surprise: **only about 2% of your genome is protein-coding genes. Roughly half of
it is transposable elements.**

A transposable element (TE) is a sequence that, at some point in evolutionary history, made
copies of itself and inserted them elsewhere in the genome. Most are "retroelements": they are
transcribed into RNA, reverse-transcribed back into DNA, and the new DNA copy inserts somewhere
new. Do that for a hundred million years and you get a genome that is mostly repeats.

The real hg38 numbers, counted in this project from RepeatMasker:

| Class | What it is | Subfamilies | Copies | Genome covered |
|---|---|---|---|---|
| **SINE** | short, non-autonomous — borrows LINE machinery | 60 | 1,570,678 | 378.6 Mb |
| **LINE** | long, autonomous — carries its own copying enzymes | 171 | 1,214,702 | 621.9 Mb |
| **LTR** | endogenous retroviruses — ancient viral integrations | 578 | 617,410 | 260.5 Mb |
| **DNA** | cut-and-paste transposons — all fossil in humans | 233 | 353,782 | 93.3 Mb |
| **Retroposon** | SVA — the youngest human family | 6 | 3,735 | 4.1 Mb |
| **RC** | rolling-circle | 3 | 1,371 | 0.3 Mb |

**Total: 3,761,678 individual TE copies across 1,057 subfamilies.**

### The vocabulary: class → family → subfamily → locus

This nesting matters, because the whole analysis turns on picking the right level.

```
class        LTR                      SINE
              └── family   ERVK        └── family   Alu
                    └── subfamily  HERVK-int             └── subfamily  AluY
                          └── locus  (233 individual copies)   └── locus  (104,272 copies)
```

A **subfamily** is a set of near-identical copies that entered the genome around the same time.
This is the useful unit: copies in one subfamily behave similarly, and subfamilies differ in
**age**, which determines whether they still work.

- `AluY` — 104,272 copies, young, still mobile in humans
- `L1HS` — 1,531 copies, the only human element still fully autonomous
- `HERVK-int` — 233 copies, the youngest endogenous retrovirus
- `HERVE-int` — 248 copies; `HERV9NC-int` — 228 copies (both appear in our results)

Older subfamilies are decayed and mostly inert. **This turns out to matter enormously — see
Part V, step 14.**

## I.3 Why the cell keeps them switched off

A TE copying itself can land inside a gene and break it. So cells suppress them, mainly by
making the DNA physically inaccessible:

- **H3K9me3** — a chemical tag on the histone proteins DNA is wound around. Marked regions
  pack into dense, closed chromatin. This is the main mark over TEs.
- **DNA methylation (5mC)** — a methyl group added directly to cytosine bases.

Proteins that add a mark are **writers**; proteins that remove one are **erasers**.

| | H3K9me3 | 5mC |
|---|---|---|
| **writers** | SETDB1, SUV39H1, SUV39H2, SETDB2, EHMT1 | DNMT1, DNMT3A, DNMT3B |
| **erasers** | KDM4A–F, KDM3A/B, KDM1A, PHF8 | TET1, TET2, TET3 |

TRIM28 is a scaffold: it does not write the mark itself, it recruits SETDB1 to specific TEs.

**This table is the hinge of the entire project.** Both DNMT3A and TET2 — the genes from your
own research — are on it: DNMT3A writes 5mC, TET2 erases it. Neither has any direct annotation
linking it to transposable elements. The mark layer is how they get in.

## I.4 Why anyone should care

When silencing fails, TE RNA accumulates. TE transcripts form double-stranded RNA, and
reverse-transcription produces cytoplasmic DNA. The cell's innate immune sensors — **MDA5**
(gene `IFIH1`) for double-stranded RNA, **cGAS** for cytoplasmic DNA — cannot distinguish that
from a viral infection. They fire, and interferon and inflammatory signalling follow.

So: *epigenetic regulator fails → TEs wake up → cell thinks it is infected → inflammation.*
This chain is implicated in ageing, cancer, autoimmunity and clonal haematopoiesis.

Two honest notes. The chain above is established in the literature in general terms, but **this
project did not measure the sensing arm** — no interferon response was tested here. Where it
appears in the figures it is drawn as a dashed "consequence arm, not measured here."

---

# Part II — What a knowledge graph is

## II.1 Nodes and edges

A knowledge graph stores facts as a network. Two ingredients:

- **Node** — a thing. A gene, a drug, a disease, a chemical mark.
- **Edge** — a directed, labelled relationship between two things.

An edge is read as a sentence: `SETDB1 —DEPOSITS_MARK→ H3K9me3` means "SETDB1 deposits the
H3K9me3 mark." Subject, predicate, object.

Why bother, rather than a spreadsheet? Because you can **follow chains**. If you have
`SETDB1 —DEPOSITS_MARK→ H3K9me3` and `H3K9me3 —MARK_AT→ HERV9NC-int`, then you can walk from
SETDB1 to a transposable element in two hops, even though no single record ever mentioned both.
That is **multi-hop reasoning**, and it is the point of the structure.

## II.2 Node types and edge types — the schema

A graph without rules about what may connect to what becomes unusable. The **schema** declares
the allowed vocabulary. Ours:

**Node types:** `Gene`, `Complex` (a stable multi-protein machine), `TEFamily`, `TELocus`,
`TEClass`, `ChromatinMark`, `Pathway`, `GOTerm`, `Drug`, `Disease`.

**Edge types:** `SILENCES`, `DEREPRESSES`, `MEMBER_OF`, `DEPOSITS_MARK`, `ERASES_MARK`,
`MARK_AT`, `SENSED_BY`, `INTERACTS_WITH`, `PARTICIPATES_IN`, `ANNOTATED_TO`, `TARGETED_BY`.

The actual graph as built:

| Predicate | Count | Reads as |
|---|---|---|
| `PARTICIPATES_IN` | 1,082 | gene is in this Reactome pathway |
| `MEMBER_OF` | 952 | gene is a subunit of this complex |
| `INTERACTS_WITH` | 582 | STRING says these two proteins interact |
| `ANNOTATED_TO` | 144 | gene carries this GO annotation |
| `SILENCES` | 59 | losing this gene **raises** this TE |
| `DEPOSITS_MARK` | 20 | gene writes this chromatin mark |
| `ERASES_MARK` | 20 | gene removes this chromatin mark |
| `DEREPRESSES` | 15 | losing this gene **lowers** this TE |

**Total 2,874 edges over 1,350 distinct nodes.**

## II.3 Direction and sign — the "loss frame"

Edges are directed, but direction alone is not enough for biology: you also need to know
whether the relationship is positive or negative. We fix this with one convention used
everywhere:

> **Every gene→TE edge states what happens when the gene is *removed*.**

- `SILENCES` — remove the gene, the TE goes **up**. (The gene was holding it down.)
- `DEREPRESSES` — remove the gene, the TE goes **down**. (The gene was needed for it.)

Why the loss frame? Because that is what the experiments do — you knock a gene out and see what
changes. Keeping one frame everywhere means a curated database fact, a measurement, and a
rule-derived prediction can all be compared without sign errors. Sign errors in this area are
easy and embarrassing: removing an *eraser* of a repressive mark leaves *more* mark and so
*less* TE, which is the opposite of the intuitive direction.

## II.4 The gap: no public graph has a TE node

| Graph | Node types | TE node? |
|---|---|---|
| Hetionet | 11 (gene, compound, disease, anatomy, pathway, …) | **no** |
| PrimeKG | 10 (gene/protein, drug, disease, phenotype, exposure, …) | **no** |
| Open Targets | target / disease / drug | **no** |

This is worth being precise about, because it is the project's central claim. The problem is
not that these graphs give a *poor* answer about TEs. It is that **the question cannot be
expressed**. If there is no TE node type, a TE cannot be the object of an edge, cannot appear
in a returned path, and cannot be scored by a prediction model. The evidence exists in the
literature; the data model has nowhere to put it.

## II.5 Provenance and evidence tiers

Anyone can assert an edge. The graph is only useful if you can tell where each one came from.
Every edge here carries mandatory fields:

```
edge_id            stable hash of subject + predicate + object + source
evidence_tier      curated | measured | literature | inferred | predicted
source             database name, PMID, or run identifier
source_detail      the GO term, complex accession, experiment accession...
native_score       the source's own number, unmodified
native_score_type  what that number means (so scores are never silently compared)
statistic          FDR / p-value where one exists
retrieved          the date
```

An edge that cannot fill these is **dropped**, not downgraded.

**The five tiers** describe *where a claim came from*, not how confident anyone feels:

| Tier | Means | In this build |
|---|---|---|
| `curated` | a human curator asserted it in a reference database | 2,832 edges |
| `measured` | computed here from primary data | 10 edges |
| `literature` | extracted from abstracts, PMID attached | 32 edges |
| `inferred` | derived by a rule from edges already present | 71 derived |
| `predicted` | proposed with no direct evidence | not used in this build |

**A path takes the tier of its weakest edge.** Enforced in code, not left to the reader — so a
single inferred hop cannot make a chain look established.

---

# Part III — How the data is treated

## III.1 What RNA sequencing gives you

A machine reads short fragments of the RNA in a sample — typically 100 letters each, tens of
millions of them. Each fragment is a **read**. A file of reads is a **FASTQ** file. Reads carry
no label saying where they came from; you have to work that out.

## III.2 Alignment

**Alignment** means finding, for each read, where in the genome it matches. Software (STAR,
HISAT2) indexes the 3.1-billion-letter genome so this can be done tens of millions of times.

Count how many reads land on each gene, and you have measured expression.

## III.3 The multi-mapping problem — the crux of the whole project

A read from a unique gene matches one place. **A read from a TE matches hundreds of places**,
because the TE has hundreds of near-identical copies.

```
read:  ...GGCTCACGCCTGTAATCCCAGCACTTTGGGAGG...

matches AluY copy on chr1  at 1,204,552   equally well
matches AluY copy on chr7  at 88,301,447  equally well
matches AluY copy on chr19 at 4,112,908   equally well
...and 104,269 other AluY copies
```

Standard pipelines call these **multi-mapping reads** and throw them away, because they cannot
be placed confidently. This is a reasonable default for gene expression. **For TEs it is fatal:
the discarded reads are precisely the TE evidence.** This is why TE signal is absent from most
public expression data, and why "just query the existing data" does not work.

### What we do instead

Two changes.

**1. Tell the aligner to keep them.** `-k 100` in HISAT2, `--outFilterMultimapNmax 100` in
STAR: report a read matching up to 100 locations instead of discarding it. Without this flag
nothing else in the project has any input.

**2. Distribute them sensibly with EM.** A read that could be from 300 AluY copies should not
count as 300 reads, nor be dropped. **TEcount** uses expectation-maximisation:

- *Start:* spread each ambiguous read evenly across its candidate copies.
- *Estimate:* compute how much each copy appears to be expressed, using unambiguous reads as
  anchors.
- *Re-assign:* redistribute the ambiguous reads in proportion to those estimates — a copy with
  strong unique evidence claims a larger share.
- *Repeat* until the numbers stop moving.

The result is a fractional, evidence-weighted assignment rather than a guess or a deletion.

> **A methodological note, because it matters for comparing to other work.** TEcount's EM is
> one valid approach. `featureCounts --countMultiMappingReads` — used in the TE_CHIP paper
> pipeline — instead counts a multi-mapping read *fully at every location*. That inflates
> high-copy families relative to EM. Neither is wrong; numbers from the two are **not
> interchangeable**, and they have not been benchmarked against each other here.

## III.4 From counts to a result

**Counting.** After alignment, count reads per feature. TEcount produces genes and TEs in one
table, which matters for the next step.

**Normalisation.** Libraries differ in total reads, so raw counts are not comparable. DESeq2
uses a median-of-ratios size factor. Critically, this is estimated on the **joint gene + TE
matrix** — if you normalised TEs against TE-only totals, a genuine global TE increase would be
divided straight back out.

**Differential expression.** For each feature, compare knockdown against control with a
negative-binomial model (PyDESeq2). Two outputs per feature:

- **log2 fold change** — the size and direction. +1 = doubled, −1 = halved, 0 = no change.
- **padj (FDR)** — the p-value adjusted for testing thousands of features at once. `padj < 0.1`
  means roughly 10% of calls at that cut-off are expected to be wrong.

A result worth reporting needs **both**: a fold change big enough to matter and an FDR small
enough to believe.

---

# Part IV — How the reasoning works

## IV.1 The five rules

Plain if-then statements applied to the graph, repeatedly, until nothing new appears
(**forward chaining**).

| Rule | Plain English | Derived here |
|---|---|---|
| **R1** mark grounding | If removing a *writer* of mark M raises TE T (measured), then M is a silencing mark at T. | 3 |
| **R2** writer transfer | If M silences T, every other writer of M is predicted to silence T. | 30 |
| **R3** eraser inversion | If M silences T, every *eraser* of M gets the **opposite** sign. | 36 |
| **R4** complex consensus | If ≥2 curated subunits of a complex silence T, attribute it to the complex. | 2 |
| **R5** complex propagation | Then extend that to the complex's other curated subunits. | 0 |

**71 derived edges.** R1 is the only rule that creates `MARK_AT` edges, so every mark-to-TE link
in the graph is anchored to a measurement rather than assumed.

## IV.2 Proof trees

Every derived edge keeps the list of edges it was built from. Read bottom-up:

```
SUV39H1 -SILENCES-> HERV9NC-int          [inferred via R2_WRITER_TRANSFER]
  H3K9me3 -MARK_AT-> HERV9NC-int         [inferred via R1_MARK_GROUNDING]
    SETDB1 -SILENCES-> HERV9NC-int       [measured: ENCODE ENCSR819PCU]
    SETDB1 -DEPOSITS_MARK-> H3K9me3      [curated: GO:0140949]
  SUV39H1 -DEPOSITS_MARK-> H3K9me3       [curated: GO:0140949]
```

We measured that removing SETDB1 raises HERV9NC-int. GO says SETDB1 writes H3K9me3. So H3K9me3
is probably what keeps that TE quiet. GO also says SUV39H1 writes H3K9me3. So removing SUV39H1
should raise it too.

**Nobody measured SUV39H1.** The prediction is signed, specific, testable, and every step is a
database record or a measurement you can open.

## IV.3 "Neurosymbolic" — what it means here

Two halves and a contract between them.

- **Symbolic:** the rules above. Deterministic, readable, auditable.
- **Neural:** language models extract relations from paper abstracts and write the
  explanations. **Neither output is trusted.**
- **The contract — a citation gate:** the explanation is split into sentences, and a sentence
  survives only if every edge ID it cites exists in the graph. Sentences citing nothing are
  rejected too, because a reader cannot distinguish an unsupported claim from a supported one
  that forgot to say so.

The gate is a string comparison. It behaves identically on model-written and template-written
text, so **the guarantee does not depend on the model behaving well.** On the eight worked
genes it kept 19 sentences and rejected 2 — both "no evidence connects X" statements, which
cite nothing by construction.

What the gate does **not** do: it checks that a cited edge *exists*, not that the sentence
*describes it correctly*. It catches fabrication, not misinterpretation.

---

# Part V — Everything we do, step by step

Each step: what it does, why, what goes in, what comes out.

### Phase A — Find out what data exists

**1. Inventory the perturbation data.**
*Why:* to measure what a gene does to TEs you need samples where that gene was removed.
*How:* query the ENCODE portal for knockdown RNA-seq experiments (shRNA, CRISPR, CRISPRi,
siRNA), recording target gene, cell line, matched control, and whether raw FASTQ exists.
*Out:* `encode_kd_inventory.csv` — **1,114 experiments, 570 distinct target genes, 1,060 with
paired-end FASTQ, 986 naming a control.** This is the ceiling on how many genes the atlas could
ever cover from this source.

**2. Assemble the curated TE-regulator seed.**
*Why:* a starting set of genes already known to control TEs.
*How:* find the Gene Ontology terms for transposition and TE silencing, walk down to every
descendant term, and pull the human genes annotated to each.
*Out:* **43 GO terms → 112 genes** (`te_regulator_seed.csv`) — including SETDB1, TRIM28, the
HUSH complex (MPHOSPH8/TASOR/PPHLN1), DNMTs, PIWIs and APOBEC3s.
*Finding:* **TET2 is not among them.** It has no GO annotation linking it to transposition.

**3. Build the TE vocabulary.**
*Why:* the graph needs TE nodes, and they must come from a standard reference, not be invented.
*How:* download RepeatMasker's hg38 annotation (5,683,690 rows), keep LINE/SINE/LTR/DNA/
Retroposon/RC, drop loci under 100 bp (too short to assign reads to), convert to GTF.
*Out:* **3,761,678 TE loci in 1,057 subfamilies** (`hg38_rmsk_TE.gtf`,
`te_subfamilies_hg38.csv`). These become the `TEFamily` and `TEClass` nodes.

### Phase B — Build the knowledge graph

**4. Define the schema.** Node types, edge types, the mandatory provenance block, the five
tiers, and the rule that a path takes its weakest tier. → `schema.md`.

**5. Harvest curated edges.**
*How:* for the seed genes plus the sensing axis, pull STRING interactions (confidence ≥ 0.7),
Reactome pathway membership, Complex Portal complexes, and GO annotations. Resolve every gene
identifier through MyGene to stable Ensembl IDs so layers merge cleanly.
*Out:* **2,792 edges** (`edges_curated.csv`).
*Care taken:* 696 of these are Complex Portal **predicted** complexes — tiered `predicted`, not
`curated`, and excluded from rule propagation.

**6. Build the chromatin-mark layer.**
*Why:* this is the bridge that reaches genes with no direct TE annotation.
*How:* query GO *molecular function* terms for methyltransferase and demethylase activities,
and map genes to the marks they write or erase.
*Out:* **40 edges** (`edges_mechanism.csv`) — the writer/eraser table in §I.3.
*Care taken:* the broad "methylcytosine dioxygenase" search also returns ALKBH/FTO, which act
on other substrates. Using the specific term **GO:0070579** returns exactly TET1/2/3.

**7. Mine the literature.**
*How:* search PubMed across TE vocabulary crossed with regulation verbs; retrieve abstracts;
run LLM extraction into structured tuples (gene, TE, direction, evidence type, species, PMID).
*Out:* 3,120 abstracts retrieved, **600 extracted** before the session's LLM budget ran out,
**32 human edges** after filtering (`edges_literature.csv`).
*Honest status:* 19% of the corpus. **A cheaper rule-based extractor was built as a fallback,
validated against the LLM-labelled subset, and rejected** — precision 0.109, recall 0.175,
direction agreement 10/21 (chance). It is not shipped.

### Phase C — Measure

**8. Choose samples.** Pick knockdowns of genes already known to silence TEs, so a **positive
control** exists: if a known silencer does not derepress its known target, the pipeline is
broken and no other result can be trusted. Chosen: **SETDB1** (n=3) and **TRIM28** (n=2), both
CRISPRi in K562 with a shared non-targeting control (n=2); plus **DNMT1** (n=2) against its own
CRISPR control (n=2) — DNMT1 specifically to ground the 5mC mark and so reach DNMT3A and TET2.

**9. Build the alignment index.** A searchable structure over the reference. Full GRCh38 needs
~32 GB RAM, so locally we index **chr1 + chr19** — TE-dense and enough to prove the method.

**10. Fetch and subsample reads.** Stream 1.5 M reads per file instead of ~35 M, so a run takes
minutes. *Trade-off stated:* taking the first N reads off the wire is ~10× cheaper but is not a
random draw. Applied identically to all samples, fine for comparison; not a final number.

**11. Align, keeping multi-mappers.** `-k 100`. Alignment rates 17–20%, as expected when the
index holds two chromosomes out of 24.

**12. Count genes and TEs together.** TEcount with EM redistribution against both the GENCODE
gene annotation and the RepeatMasker TE GTF, producing one table per sample.
*Out:* **11/11 samples quantified end to end.**

**13. Differential expression.** PyDESeq2, each knockdown against its matched control, size
factors from the joint gene+TE matrix.
*Result — the positive control fired:*

| Knockdown | TE subfamily | log2FC | padj |
|---|---|---|---|
| TRIM28 | AluY | +0.79 | 0.00053 |
| TRIM28 | AluYa5 | +0.99 | 0.068 |
| SETDB1 | HERVE-int | +0.97 | 0.083 |
| SETDB1 | HERV9NC-int | +1.20 | 0.090 |

Among nominally significant TE subfamilies: SETDB1 **4 up / 0 down**, TRIM28 **12 up / 2 down**.
TRIM28 restraining SINEs and SETDB1 restraining HERVs is the textbook expectation, recovered
from two chromosomes. **DNMT1 produced nothing at FDR < 0.1** (best padj 0.41).

**14. Test whether aggregating helps.** Following the TE_CHIP paper pipeline, TE counts were
also summed to family and class level before testing.
*Result: it made things worse.* SETDB1 drops from 2 hits at padj < 0.1 to 0; TRIM28 from 4 to
1. `AluY` alone is significant at padj 0.00053, but the whole `Alu:SINE` family (+0.616) is not.
*Conclusion:* **subfamily resolution is load-bearing at this depth.** Aggregation is the right
choice when per-subfamily counts are too sparse, which at full depth they will not be.
→ `aggregation_level_comparison.csv`.

*Why it happens is NOT established, and an earlier draft of this document got it wrong.* The
tempting explanation is "only young, still-active subfamilies respond, so pooling averages them
against inert old ones." Tested against RepeatMasker divergence, that fails genome-wide:
Spearman rho between `milliDiv` and log2FC is +0.098 (SETDB1, p = 0.39) and +0.056 (TRIM28,
p = 0.61). Within Alu the pattern does appear, but age and expression level are confounded
(rho = +0.713), and lowly-expressed features show larger fold changes for protein-coding genes
too — so part of it is a generic estimation artefact. A duller explanation (pooling
high-variance low-count features with high-count ones) has not been excluded. See
`INTERPRETING_RESULTS.md` §6.

**15. Convert results into edges.** Every TE hit at FDR < 0.1 becomes an edge: positive log2FC →
`SILENCES`, negative → `DEREPRESSES`, carrying the fold change, the FDR, and the ENCODE
accession. *Out:* **10 measured edges**.

### Phase D — Reason

**16. Run the rules to a fixpoint.** → **71 derived edges**, each with a proof tree.

**17. Answer queries.** `explain(gene)` returns measured effects, curated annotations,
literature edges, rule-derived predictions with proofs, and admissible multi-hop paths.

**18. Gate the prose.** Split into sentences, keep only those citing edges that exist.
19 kept, 2 rejected across the worked genes.

### Phase E — Ask what is druggable

**19. Annotate tractability.** For every gene in the graph with a TE edge of any tier, plus the
sensing axis, pull Open Targets tractability buckets and ChEMBL mechanisms of action; collapse
into five classes.

**20. The result:**

| Class | n | Contains |
|---|---|---|
| 1 · approved drug exists | 7 | DNMT3A, EZH2, HDAC1/2, ESR1, PPARG, AHR |
| 2 · clinical-stage | 6 | KDM1A, TP53, TGFB1/3, ICOS, ERVW-1 |
| **3 · structurally tractable, no clinical programme** | **28** | **SETDB1, SUV39H1/2, SETDB2, EHMT1, KDM4A–E, cGAS, TBK1, IFIH1** |
| 4 · druggable family / antibody-accessible only | 4 | MPHOSPH8 |
| 5 · no tractability evidence | 38 | TRIM28 |

Class 3 is the interesting bucket: a protein structure exists and chemistry is feasible, but no
clinical programme has been run. **Every gene the engine implicates in HERV control sits
there.**
*Caveat, stated plainly:* "no clinical programme" often means one was tried and failed rather
than that an opportunity is waiting.

---

# Part VI — How to check any of this yourself

| Claim | Where to verify |
|---|---|
| The TE counts are real | `counts_matrix.tsv` — 11 sample columns of integers |
| The statistics are real | `deseq2_results.csv` — every feature, fold change and FDR |
| An edge says what I claim | `edges_*.csv`, look up the `edge_id` |
| A prediction is honest | `examples.json` — proof trees for every inferred claim |
| Aggregation hurt | `aggregation_level_comparison.csv` |
| The rejected extractor really failed | `lit_extractor_validation.csv` |
| The limitations are not hidden | `CRITIQUE.md` |

And the one-line summary to keep hold of:

> The schema, pipeline, rule layer and citation gate all work on real data. **Three genes have
> been measured, not 570.** The "any gene" claim is architectural, and what stands between this
> and an actual atlas is compute, not design.
