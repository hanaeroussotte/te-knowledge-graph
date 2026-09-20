# Demo script: seven questions

**The centre of the demo is TRIM28, not DNMT3A/TET2.** TRIM28 is where the measurement is
strongest, and starting from a measurement rather than a hypothesis keeps the whole
sequence grounded. DNMT3A/TET2 appears at question 4 as *one worked example* of prediction
— not as the thesis.

The arc: **measurement → is it specific → what mechanism → what should follow → why believe
it → what did NOT happen → what to compute next.** The last transition is the one to land.

---

## Q1. "Which transposable elements respond when I perturb TRIM28?"

```
make query GENE=TRIM28
```

Show measured edges. AluY **+0.79 log₂FC, padj 0.0005**, from ENCODE ENCSR591QYK, K562,
CRISPRi, re-quantified here — the original experiment did not measure transposable
elements at all.

> The point to make: this number did not exist before. The reads did.

## Q2. "Is that a specific effect, or has everything moved?"

Two statistics, always.

| | AluY alone | TE compartment |
|---|---|---|
| effect | +0.79 | median +0.41 vs −0.02 for genes |
| p | padj 0.0005 | 3.5 × 10⁻¹⁵ |

TRIM28 moves **both** — a specific young Alu and the whole compartment. Contrast with
SETDB1, which moves two ERV subfamilies and leaves the compartment alone (p = 0.24): a
targeted silencer versus a global one, distinguishable only because both statistics are
computed.

Then the methodological point, which is the strongest thing to say in the room:

> Size factors are per-sample, so a normalisation error shifts TE and gene log₂ fold
> changes by the same amount and cancels in the difference between their medians. A
> normalisation artefact cannot manufacture a gap between two feature sets measured in the
> same libraries. The test itself is standard competitive gene-set testing — what's ours is
> using it as the *primary* TE readout for that reason.

## Q3. "What mechanism could explain it?"

Traverse: `TRIM28 —RECRUITS→ SETDB1 —DEPOSITS_MARK→ H3K9me3 —MARK_AT→ TE`.

TRIM28 has no catalytic activity; it recruits SETDB1 to specific TE sequences. That the
graph holds the chromatin mark as its own node is what makes this traversable rather than
a sentence in a review.

## Q4. "Which untested regulators should show a related phenotype?"

This is where prediction enters, and where DNMT3A/TET2 appears as **an example**.

Neither has a knockdown anywhere in ENCODE; TET2 is not annotated to any GO transposition
term. The engine still answers, with opposite signs derived from the same grounding:

| Gene | Role | Rule | Prediction |
|---|---|---|---|
| DNMT3A | 5mC writer | R2_WRITER_TRANSFER | loss **raises** TEs |
| TET2 | 5mC eraser | R3_ERASER_INVERSION | loss **lowers** TEs |

Say "predicted" and "mechanistic hypothesis", never "causal". And note that the prediction
is *sharper* than the source hypothesis: not merely "TET2 inflammation is not TE-mediated"
but "TET2 loss should actively lower TE expression" — which is falsifiable by one
experiment.

## Q5. "Why should I believe that?"

Print the tree.

```
TET2 → DEREPRESSES → TE:global                    [inferred, R3]
├── TET2 erases 5mC                               [curated: GO:0070579]
└── 5mC represses TEs                             [inferred, R1]
    ├── DNMT1 writes 5mC                          [curated: GO:0003886]
    └── DNMT1 loss raised the TE compartment      [MEASURED, p = 1.6e-08]
```

Three facts, one of them ours. Then volunteer the weakest link before anyone finds it:
**R2 transfers between DNMT1 (maintenance) and DNMT3A (*de novo*) on the strength of a
shared mark.** That is the rule most likely to be wrong, it is tiered accordingly, and the
tree is what lets you see that the argument depends on it.

## Q6. "Did this TE activation trigger interferon?"

**No detected response in this context — and here is why the question could not be answered
as posed.**

The first attempt was refused by the software: only 17% of the type-I interferon gene set
was inside the reference. We fixed that properly — 921 spliced-in contigs took coverage to
77%, with a control showing existing measurements were unchanged (Pearson 0.992–0.996).

At real coverage: no signature moves, and the bootstrap intervals exclude effects of
TE-arm magnitude. Then the sensor table, which is the slide:

| entry points | CPM | | transducers | CPM |
|---|---|---|---|---|
| CGAS | **0.21** | | TYK2 | 799 |
| ZBP1 | 0.26 | | MAVS | 586 |
| TLR3 | 0.00 | | IRF3 | 317 |
| IFIH1 | 8.5 | | STING1 | 270 |

> K562 has the whole downstream machinery and no way to switch it on. This dataset cannot
> test viral mimicry. The rule that would connect the two arms, R6, is implemented and
> fires zero times — correctly.

And the ladder from `EPISTEMOLOGY.md`: TE RNA up does not give dsRNA up, does not give
cytoplasmic cDNA, does not give sensor activation, does not give interferon, does not give
disease. Rungs 1, 2 and 6 are measured here. Rungs 3, 4, 5 are not.

## Q7. "Is the evidence sufficient to answer the question we started with?"

**Ask this, not "what should we compute next".** The ending has to be driven by the
scientific logic, or it becomes theatre: an agent announcing a next experiment regardless
of whether one is needed reads as a script, and a reviewer will hear it as one.

So the system assesses sufficiency first, per claim, against the registry in `CLAIMS.md`:

| Question | Sufficient? | Why |
|---|---|---|
| Does TRIM28 loss raise TEs in K562? | **yes** | measured, two statistics, p = 3.5 × 10⁻¹⁵ |
| Is DNMT1 on the 5mC→TE axis? | **yes, at compartment level** | p = 1.6 × 10⁻⁸; no subfamily clears FDR |
| Does DNMT3A silence TEs? | **no** | inferred only; no DNMT3A knockdown exists in ENCODE |
| Does TE derepression drive interferon? | **no** | the sensing arm is not expressed in this cell line |
| Are the TE effects quantifier-independent? | **no** | not tested; protocol written, not run |

Only where the answer is *no* does it name the computation expected to reduce the most
decision-relevant uncertainty — and the ranking is by what it would settle, not by cost:

1. **Repeat in a sensing-competent cell type** — primary haematopoietic progenitors, or
   K562 reconstituted with cGAS. Converts rung 5 from impossible to testable.
2. **Perturb DNMT3A and TET2 directly** — converts two `inferred` edges to `measured` and
   tests R2 and R3 head-on. R3 predicts a *decrease*; nothing else does.
3. **Quantifier robustness** (`QUANTIFIER_ROBUSTNESS.md`) — five arms, pre-registered
   interpretation, written and not run.
4. **Genome-wide, full depth** — unblocks locus resolution and link prediction.

The closing line:

> Two of those five questions are answered and three are not, and the system knows which
> is which. Five H3K9 methyltransferases are predicted to regulate the same TE programme —
> you don't test all five, you test the one that best discriminates between the competing
> explanations. Deciding *that* is what turns a knowledge graph into an experimental-design
> engine, and it only works if the system can first tell you honestly which of its own
> answers are not yet answers.

---

## Things to say once, and not oversell

- Credit TEtranscripts by name when the quantification comes up. Someone in the room will
  know it.
- "Major general-purpose biomedical knowledge graphs do not model TEs as first-class
  entities" — not "no knowledge graph has TEs".
- If TxPert comes up: it is real, it is good, and **TxPert plus a TE-aware expression
  matrix would be a strong competitor**. The gap is closable and not yet closed. Saying
  this first is stronger than being told it.
- If cGAS comes up: the 2026 *Nature Aging* result puts cGAS upstream in chromatin control
  as well as downstream as a sensor, so the pathway has feedback and our directed drawing
  is a simplification. Logged as an open structural issue.

## Three questions you will get

**"Isn't this just a lookup table?"** TET2 has no TE annotation anywhere and no experiment;
the system still answers, by a stated rule chain you can inspect.

**"Multi-mapping makes TE quantification meaningless."** That is why there are two
statistics, and why the second one compares TEs against genes in the same libraries.

**"Two replicates is not enough."** Correct for per-feature claims — which is why the
headline is a compartment-level shift across 503 features, and why the three components we
could not validate were not shipped.
