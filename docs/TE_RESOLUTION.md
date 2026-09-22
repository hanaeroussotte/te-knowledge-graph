# TE resolution: the ontology this should grow into

## 1. Two orthogonal axes

The mistake to avoid is collapsing these into one. **Resolution** is how finely a claim
localises in the repeat hierarchy. **Context** is the experimental circumstances it was
established in. They vary independently: a claim can be subfamily-level in K562 or
locus-level in primary cells, and neither implies the other.

### Axis 1 — evidence resolution

```
    TEClass            LINE, SINE, LTR, DNA, Retroposon, RC
       │
    TEFamily           Alu, L1, ERV1, ERVK, SVA
       │
    TESubfamily        AluY, AluYa5, L1HS, HERVK-int      ← where we currently attach
       │
    TELocus            chr1:1,234,567-1,234,867 (AluY)
       │
    TETranscript       a specific transcript from that locus
```

**Family and subfamily are separate levels, not one hybrid level.** They are neither
biologically nor computationally interchangeable, and this project demonstrates the
distinction itself: `AluY` is significant at padj 0.0005 while the `Alu` family it belongs
to is not significant at all. Writing them as "family/subfamily" would erase the finding
that motivates the whole resolution discussion.

### Axis 2 — experimental context

```
    species | cell_type | cell_state | perturbation | perturbation_modality
            | assay | timepoint | dose | reference_genome | reference_scope | quantifier
```

Both axes are carried as columns on every edge (`migrate_edge_context.py`,
`nesy_rules.CONTEXT_KEYS`), and inferred edges **inherit** context from their premises
rather than silently generalising — see §7.

**Evidence should attach at whichever resolution the experiment actually supports** — not
at whichever level the pipeline happens to output. That is the design rule, and the current
build does not meet it: everything attaches at subfamily because the quantifier we run
(`TEcount`) reports at subfamily, and the reasoning layer operates there.

## 2. Why subfamily, for now

The prototype uses a mature, validated method at the resolution its inference layer works
at. Two empirical reasons, not a preference:

- **Aggregating upward loses power at this depth.** Class/family aggregation dropped
  SETDB1 from 2 hits to 0 and TRIM28 from 4 to 1; `AluY` alone is padj 0.0005 but pooled
  into `Alu:SINE` it is +0.616 and not significant (`aggregation_level_comparison.csv`).
- **Going downward is not supported by 1.5 M reads.** Locus-level quantification on ~104,000
  AluY copies at this depth would be almost entirely prior, not data.

Both reasons are about **depth**, so both expire. At full depth, aggregation should become
the better choice for common subfamilies and locus resolution should become feasible for
the expressed minority. The resolution should then be chosen per-question rather than
fixed.

## 3. What each resolution buys, and what it costs

| Resolution | Buys | Costs | Tool |
|---|---|---|---|
| Class | Robust, interpretable, low multiple-testing burden | Dilutes a responding subfamily among non-responding relatives | any |
| Family | Middle ground | Same dilution, weaker | any |
| **Subfamily** | Age/activity-coherent groups; survives low depth | Aggregates ~10⁵ loci that differ enormously in whether they are transcribed | TEcount, SalmonTE |
| Locus | The biologically real unit; distinguishes an expressed insertion from a silent one | Needs depth; multi-mapping is hardest here; exon overlap contaminates | Telescope, SQuIRE, MAJEC, TElocal |
| Transcript | Distinguishes autonomous TE transcription from read-through and exonisation | Needs long reads or careful TSS evidence | long-read, TSS profiling |

The gap between subfamily and locus is where most of the criticism of TE analysis lives,
and it is legitimate: "AluY goes up" aggregates roughly 104,000 loci, most of which are
certainly silent.

## 4. The specific failure mode we do not currently address

`MAJEC` (bioRxiv 2026, [10.64898/2026.04.10.717472](https://doi.org/10.64898/2026.04.10.717472))
reports that a substantial share of locus-level TE signal in existing tools comes from TE
fragments that overlap gene exons — so a change in *gene* expression can register as a
change in *TE* expression. It reports reducing that contamination from roughly 43% to 5%.

Two honest observations:

1. This is a **different failure mode** from the one our set-level test defends against.
   Ours is per-sample normalisation error; MAJEC's is per-feature annotation contamination.
   Neither defends against the other.
2. MAJEC's own benchmark reports **subfamily-level differential-expression concordance of
   r = 0.987 with TEtranscripts**. So it does not invalidate subfamily-level conclusions —
   it improves locus-level ones. That is the accurate response to "your quantifier is out
   of date", and it is a reason to run the experiment in §5 rather than a reason to
   dismiss the concern.

## 5. Schema changes this implies

The edge schema already carries `te_resolution` as a column (see `EPISTEMOLOGY.md` §5), so
locus-level edges can enter without a migration. What would be needed:

- Node types `TELocus` and `TETranscript`, with `PART_OF` edges up the hierarchy.
- A `quantifier` value per edge (already present) so two resolutions produced by two tools
  are never silently pooled.
- A rule guard: no rule may combine premises at different resolutions without an explicit
  `PART_OF` traversal, or `AluY` evidence will leak onto a specific insertion.

## 6. Context inheritance on inferred edges

This is implemented, and it is one of the more useful properties of the reasoning layer.

The problem is easy to miss. R2 takes

```
SETDB1 loss raises HERV9NC-int     [measured: K562, CRISPRi, RNA-seq, subfamily, TEcount]
SUV39H1 writes H3K9me3             [curated: no cell type]
```

and concludes something about `SUV39H1`. Written down bare, that conclusion reads as a
universal claim about SUV39H1 and HERV9NC-int — when the only experiment underneath it is
one knockdown in one leukaemia line.

`nesy_rules.inherit_context()` therefore carries premise context onto every derived edge,
centrally in `forward_chain` rather than inside each rule, so a newly added rule cannot
forget to do it:

- a key the informative premises agree on is **inherited**;
- a key they disagree on becomes `mixed(a|b)`, with nested `mixed()` flattened so repeated
  chaining does not compound;
- a key no premise speaks to is `not_applicable`;
- if any premise carried a specific experimental context, the conclusion is flagged
  **`context_generalization_required=yes`**.

87 of 89 derived edges carry that flag. The two that do not are R4 complex-consensus edges
resting only on curated membership, which genuinely have no experimental context. Proof
trees print the flag inline:

```
TET2 -DEREPRESSES-> TE:global   [inferred via R3_ERASER_INVERSION]
  ! prediction is grounded in context_cell_type=K562; perturbation_modality=CRISPR
    — asserting it elsewhere is a further inference
```

Export the whole set with `python src/te_reason.py <gene> --export-derived results/derived_edges.csv`.

**Why this matters beyond bookkeeping:** generalising a prediction outside the context that
grounds it is a *second inference*, and it should have to be made explicitly rather than
inherited by silence. The flag is what forces that.

## 7. Status

`NOT_TESTED`. Nothing in this document has been run. It is the design the next build should
target, recorded so the current subfamily choice reads as a scoped decision with an expiry
condition rather than an oversight.

---

## 8. The direction this document originally missed

Sections 1–7 defend subfamily resolution **upward** — against aggregating to family and
class, which was measured and demonstrably loses signal. The external review of 2026-09-22
pointed out that the more dangerous direction is **downward**, and it was right: the field
is moving to loci, and a defence that only faces one way is not a defence.

The evidence, all verified (`LANDSCAPE.md` §1 carries the full citations):

- Locus-specific single-cell measurement is established — CELLO-seq, *Nat Biotechnol* 2021,
  [10.1038/s41587-021-01093-1](https://doi.org/10.1038/s41587-021-01093-1).
- Locus-level annotation exists at scale — 2,596 long-read datasets, 21 organs, 71 cell
  lines, [10.1186/s44342-025-00048-1](https://doi.org/10.1186/s44342-025-00048-1).
- Two 2026 preprints go further still: TEsingle
  ([10.64898/2026.03.19.712984](https://doi.org/10.64898/2026.03.19.712984)) and TEscape
  ([10.64898/2026.07.08.737305](https://doi.org/10.64898/2026.07.08.737305)).
- And the reason it matters biologically: copies within one subfamily do not behave alike.
  A VEXAS preprint reports CRISPRi against **two individual L1 loci** reversing
  disease-associated HSC phenotypes
  ([10.64898/2026.07.31.742092](https://doi.org/10.64898/2026.07.31.742092)) — which, if it
  holds, is a phenotype no subfamily-level measurement could ever have located.

### 8.1 The full ontology

```
TEClass  →  TEFamily  →  TESubfamily  →  TELocus  →  TETranscript
 SINE        Alu           AluY          one of      a specific
                                      104,272 copies  TE-initiated
                                                       transcript
```

**Evidence attaches at whichever level the experiment supports**, and only there. A TEcount
measurement supports a `TESubfamily` node; a Telescope or CELLO-seq measurement supports a
`TELocus` node; a long-read transcript assembly supports `TETranscript`. Nothing propagates
downward — a subfamily-level effect is not evidence about any individual copy, which is
precisely the inferential error locus-level work exists to prevent.

`TEFamily` and `TESubfamily` are already separate node types in the built schema, for the
measured reason in §2. **`TELocus` and `TETranscript` do not exist.** They are roadmap. The
schema is split in a way that permits adding them without migration of the existing levels,
which is the most that can honestly be claimed today.

### 8.2 The sentence to say out loud

> We work at subfamily level because we measured that aggregating upward loses signal, and
> because the inference layer consumes that resolution. The field is moving to loci, the
> tools for it exist, and the ontology is split so the schema can follow. It has not
> followed yet.

Not: *subfamily is the right level*. It is the right level **here, at this depth, for this
inference layer** — and that qualifier is the whole content of the claim.
