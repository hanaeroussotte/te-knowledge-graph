# The panel-augmented reference

**The problem.** The TE arm of this project was measurable and the inflammation arm was
not. On a chr1+chr19 reference only **16.8%** of the GO type-I interferon set is present,
and every canonical sensor and effector except `IRF3`, `ISG15` and `ADAR` lives on another
chromosome — `CGAS` chr6, `STING1` chr5, `IFIH1` chr2, `MAVS` chr20, `TBK1` chr12, `STAT1`
chr2, `STAT2` chr12, `IRF7` chr11, `MX1` chr21, `OAS1` chr12, `IFIT1` chr10. Any interferon
result computed on that scope describes the chromosome selection, not the biology.
`score_signatures.py` therefore refused to interpret it.

Naming a limit is better than reporting past it. Removing the limit is better still.

**The idea.** The two arms have different reference requirements, and we had been paying
the more expensive one for both. Transposable elements are dispersed, so the TE arm needs
a large reference — you cannot count a subfamily you did not index. The inflammation arm
needs roughly a thousand specific gene bodies. So rather than index 3.1 Gb to rescue 60 Mb
of signal, splice the missing loci into the existing reference as extra contigs, carrying
their real GENCODE exon structure across so that counting stays exonic and comparable.

```
   before:   [ chr1 ][ chr19 ]                                310 Mb,  17% ISG coverage
   after:    [ chr1 ][ chr19 ][ 921 panel contigs ]           372 Mb,  77% ISG coverage
```

---

## 1. What the builder does

`src/build_panel_reference.py`, two subcommands.

```bash
python src/build_panel_reference.py spec  --gtf refs/gencode.v44.gtf \
    --in-scope chr1,chr19 --outdir data/graph
python src/build_panel_reference.py build --gtf refs/gencode.v44.gtf \
    --spec data/graph/panel_spec.csv --outdir refs
```

`spec` pulls the six GO signature sets plus an explicit canonical sensing/effector/SASP
list, resolves each symbol to GENCODE coordinates, and partitions into in-scope,
off-scope and unresolvable. **990 genes** needed panelling.

`build` fetches each padded gene body (±5 kb) from Ensembl REST, writes the contigs, and
translates each gene's exon structure into contig-local coordinates preserving strand.

Four decisions in the builder that are not cosmetic:

**Overlapping windows are merged.** Padded windows around clustered gene families overlap —
`IFIT1`/`IFIT1B`/`IFIT3`/`IFIT5` on chr10, `OAS1`/`OAS2`/`OAS3` on chr12,
`IFITM1`/`IFITM2`/`IFITM3` on chr11, `CASP1`/`CASP5`, the APOBEC3 and IFNA clusters. Emitted
as separate contigs they would put **0.69 Mb of identical sequence in the reference twice**
and turn uniquely-mapping reads into artificial multi-mappers, at precisely the genes the
panel exists to measure. The first index build was discarded when this was found. After
merging: 990 genes → **921 contigs, 61.7 Mb, zero duplicated genomic span** (asserted).

**Neighbouring genes inside a window are annotated too**, tagged
`feature_source "panel_neighbour"`, so their reads are attributed to them rather than
leaking into the panel target they sit beside.

**TEs are deliberately not annotated on panel contigs.** The TE feature set stays exactly
what it was on chr1+chr19. That is what makes the perturbation control in §3 a clean
comparison.

**The coordinate systems were verified, not assumed.** The panel splices Ensembl GRCh38
sequence into a UCSC hg38 reference. A one-base disagreement would put every spliced exon
out of register and quietly corrupt the whole arm. A 301 bp window on chr1 was fetched from
both and compared byte for byte: identical.

---

## 2. What it cost and what it bought

| | chr1+chr19 | panel-augmented |
|---|---|---|
| Reference size | 310 Mb | 372 Mb (+20%) |
| Sequences | 2 | 923 |
| Index build | ~20 min | ~25 min |
| Mean alignment rate | 18.9% | 23.3% |
| Type-I IFN coverage | 0.168 | **0.768** |
| Defense-response-to-virus | 0.174 | **0.708** |
| Senescence | 0.096 | **0.783** |
| NF-κB | 0.124 | **0.686** |
| Inflammatory response | 0.179 | 0.535 — **still refused** |

Alignment rate rose for every library, consistently (`DNMT1_rep1` 23.44→29.20%,
`TRIM28_rep2` 12.75→16.08%) — reads that previously had no home now have one.

The inflammatory-response set still fails the 0.6 guard, because GO:0006954 has 725
members and many are tissue-specific genes not expressed in K562 at all. **The guard is
still doing its job after the fix**, which is the point of having it in code rather than
in prose.

---

## 3. The control: does adding 62 Mb change what we already measured?

This is the step that decides whether the approach is usable. The risk is that isolated
contigs act as a decoy surface — a read whose true origin is still absent from the
reference may now land on a panel gene. All 11 libraries were re-aligned from the
**identical** subsampled FASTQ files, so any difference is attributable to the reference
alone.

| Knockdown | features | Pearson | Spearman | median &#124;Δlog₂FC&#124; |
|---|---|---|---|---|
| SETDB1 | all 3,367 | 0.995 | 0.995 | 0.007 |
| SETDB1 | TE only 349 | 0.993 | 0.988 | 0.010 |
| TRIM28 | all 3,179 | 0.996 | 0.997 | 0.027 |
| TRIM28 | TE only 319 | 0.993 | 0.990 | 0.025 |
| DNMT1 | all 3,581 | 0.992 | 0.991 | 0.013 |
| DNMT1 | TE only 499 | 0.992 | 0.987 | 0.014 |

None of the six headline TE results changes sign, and effect sizes move by at most 0.09
log₂ units. The median shift is the **same for the TE and gene sets** in every contrast, so
the set-level delta — which is a difference between those two medians — is unchanged:

| Knockdown | delta, original | delta, panel | p, panel |
|---|---|---|---|
| SETDB1 | +0.024 | +0.024 | 0.47 |
| TRIM28 | +0.408 | +0.408 | 2.3 × 10⁻¹⁹ |
| DNMT1 | +0.130 | +0.136 | 7.9 × 10⁻⁸ |

**Multi-mapping on panel contigs.** Panel contigs take 4.4–6.8% of primary alignments, of
which 2.5–3.4% are multi-mapping, against 0.3–0.8% on chr1/chr19. Higher, and expected:
paralogue families are deliberately panelled together, so within-family ambiguity is real
sequence similarity rather than decoy capture. In absolute terms it is ~0.2% of all
alignments.

**One real cost.** Per-feature FDR loses one to two hits per contrast (SETDB1 2→1,
TRIM28 4→2). This is not mismapping — effect sizes are unchanged — it is that ~1,100 more
features enter the multiple-testing set. Applying BH within the TE features only is *more*
conservative still, because DESeq2's independent filtering already handles the burden
better than a naive within-family correction. **Conclusion: quote the TE arm from the
original reference and the inflammation arm from the panel run.** They are the same reads
and the same effect sizes; only the FDR denominator differs.

---

## 4. Two backgrounds, because a panel introduces one specific confound

Signature genes now mostly sit on spliced-in contigs; ordinary genes mostly do not. If the
two groups differ *technically* — mappability, contig edges, GC — that alone would look
like a signature shift. So `score_signatures.py` reports every test against two
backgrounds:

- `all_other_genes` — the conventional comparison.
- `other_panel_genes` — every gene on both sides is then on a panel contig, so
  panel-ness cannot explain a difference.

A shift that appears only against the first background is a reference artefact. In this
run the two agree throughout, which is itself the check passing.

Size factors are estimated on chr1/chr19 protein-coding genes only (PyDESeq2
`control_genes`), and panel genes are excluded from the set-level TE background. Both for
the same reason: the panel is a deliberately chosen immune-biased subset, and letting it
into normalisation would mean a genuine interferon response partly normalises itself away.

---

## 5. The result

With coverage at 0.768 instead of 0.168, the interferon question is finally askable. The
answer is a clean, interpretable **null**:

| Knockdown | TE arm (Δ median log₂FC) | 95% CI | Interferon arm | 95% CI |
|---|---|---|---|---|
| SETDB1 | +0.024 | −0.062 … +0.115 | +0.023 | −0.056 … +0.060 |
| TRIM28 | **+0.408** | +0.311 … +0.467 | −0.023 | −0.126 … +0.061 |
| DNMT1 | **+0.136** | +0.095 … +0.178 | −0.011 | −0.059 … +0.042 |

No signature moves in any contrast under Bonferroni correction across the 15 tests. The
bootstrap intervals matter here: the interferon confidence intervals **exclude effects of
the magnitude seen on the TE arm**, so this is a measured absence rather than a shrug.

**Why — and this is in the same data.** Expression of the pathway in K562:

| Entry points (sensors) | CPM | | Transducers | CPM | | Effectors | CPM |
|---|---|---|---|---|---|---|---|
| `CGAS` | **0.21** | | `TYK2` | 799 | | `IFNB1` | **0.00** |
| `ZBP1` | **0.26** | | `MAVS` | 586 | | `OASL` | **0.00** |
| `NLRP3` | **0.20** | | `IRF3` | 317 | | `OAS1` | 1.06 |
| `TLR3` | **0.00** | | `JAK1` | 317 | | `IFIT1` | 1.29 |
| `RIGI` | 5.4 | | `STAT2` | 286 | | `MX1` | 2.21 |
| `IFIH1` | 8.5 | | `STING1` | 270 | | `IFIT3` | 9.14 |

**The transduction machinery is abundant and the entry points are at the floor.** `CGAS` is
effectively not expressed — 0.1 mean raw count, non-zero in 1 of 11 samples. The RNA
sensors sit under 10 CPM. `ADAR`, whose editing of double-stranded RNA is the principal
brake on MDA5 sensing of endogenous transcripts, is at **823 CPM**. There is no tonic ISG
tone to raise: `IFNB1` and `OASL` are at zero.

So the correct statement is not "TE derepression does not cause interferon". It is:

> In K562, TE derepression is not accompanied by a type-I interferon response, and the
> cytosolic sensing arm that would be required to produce one is not expressed. This
> dataset cannot test viral mimicry; a cell type with an intact sensing axis is required.

That is a far stronger and more useful result than the uninterpretable version, and it
converts "we could not measure the inflammation arm" into a specific experimental
requirement.

---

## 6. Consequences for the reasoning engine

`nesy_rules.py` gains **R6_TE_MEDIATED_INFLAMMATION**: if, in the *same contrast*, losing
gene *g* raised the TE compartment (measured) **and** raised an inflammation signature
(measured), conclude *g* drives that signature through TE derepression. Requiring the same
contrast is the point — a TE effect in one experiment and an interferon effect in another
is a coincidence, not a pathway.

R6 **fires zero times**, because all 15 inflammation edges are `NO_DETECTED_EFFECT_ON`.
That is reported the same way R5's zero is reported. The rule is implemented and its
premises are unmet; when someone runs this in a sensing-competent cell line, it will fire
without a code change.

Engine totals: 89 derived edges from 9,366 inputs — R3 45, R2 38, R1 4, R4 2, R5 0, R6 0.

---

## 7. What a panel cannot do

**It measures the genes you name.** A genome-wide run can surface a pathway nobody
anticipated; a panel cannot. If the real consequence of TE derepression in this system were
something outside the six GO sets, this design would miss it entirely.

It is the right tool when you have a specific, pre-specified question and the wrong tool
for discovery. Here the question was specific — *does the interferon arm respond* — and the
genome-wide run remains the listed next step for everything else.

---

## 8. Reproducing it

```bash
make panel          # spec + fetch + contigs + index
make de-panel       # align 11 libraries, quantify, DE, signatures
```

Roughly 25 min for the index and 70 min for the 11 libraries on 8 cores. Outputs land in
`results_panel/`.
