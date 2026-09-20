# TE resolution: the ontology this should grow into

## 1. The target hierarchy

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

## 6. Status

`NOT_TESTED`. Nothing in this document has been run. It is the design the next build should
target, recorded so the current subfamily choice reads as a scoped decision with an expiry
condition rather than an oversight.
