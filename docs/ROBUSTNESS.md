# Robustness: how much does the reasoning layer actually rest on?

**Run, not planned.** `results/holdout_robustness.csv`, `figures/fig_holdout_robustness.png`.

## 1. The question

The engine turns 3 measured knockdowns into 89 derived predictions. That ratio invites an
obvious attack: *is this a reasoning system, or one experiment with 89 restatements of it?*

The test is leave-one-anchor-out. Drop every **measured** edge belonging to one gene,
re-run forward chaining to fixpoint, and see what survives. Nothing else changes — same
curated layer, same rules, same grammar.

## 2. Result

| Anchor removed | measured edges dropped | derived edges | R1 | R2 | R3 | R4 | genes answered |
|---|---|---|---|---|---|---|---|
| — (full graph) | 0 | **89** | 4 | 38 | 45 | 2 | 10/10 |
| TRIM28 | 13 | **89** | 4 | 38 | 45 | 2 | 9/10 |
| DNMT1 | 6 | **83** | 3 | 36 | 42 | 2 | 7/10 |
| SETDB1 | 8 | **8** | 1 | 2 | 3 | 2 | 8/10 |

Three findings, and the first two are uncomfortable.

### 2.1 The inference layer rests on a single knockdown

Removing SETDB1's 8 measured edges takes the derived layer from **89 edges to 8** — a 91%
collapse. R2 goes from 38 firings to 2, R3 from 45 to 3.

The reason is visible in R1. Only **four** mark-grounding edges exist in the whole graph,
and each mark is grounded by exactly one gene:

```
H3K9me3 MARK_AT HERV9NC-int   <- SETDB1   (measured)
H3K9me3 MARK_AT LTR/ERV1      <- SETDB1   (measured)
H3K9me3 MARK_AT HERVE-int     <- SETDB1   (measured)
5mC     MARK_AT TE:global     <- DNMT1    (measured)
```

R1 is the only rule that creates `MARK_AT` edges, and R2/R3 consume them. So the entire
H3K9me3 arm — every SUV39H1, SETDB2, EHMT1, KDM4A–E prediction — traces to **one CRISPRi
experiment**, and the entire 5mC arm — DNMT3A, DNMT3B, TET1/2/3 — traces to **one CRISPR
experiment**. That is the project's central structural fragility and it should be said
before anyone finds it.

### 2.2 The largest measured effect contributes nothing to the reasoning

Removing **TRIM28** drops 13 measured edges — more than either other anchor — and changes
the derived layer **not at all** (89 → 89). TRIM28 has the biggest measured effect in the
project (compartment shift +0.41, p = 3.5 × 10⁻¹⁵) and the inference layer does not use it.

Why: TRIM28 is a scaffold, not a mark writer. It has no `DEPOSITS_MARK` edge, so it can
never satisfy R1, so it can never ground a mark. Its measured edges are terminal — they
answer questions about TRIM28 and propagate nowhere.

This is not a bug, but it is a real limitation: **measured evidence only enters the
reasoning layer through genes with a curated enzymatic role.** A scaffold, an RNA-binding
protein or an uncharacterised hit contributes zero inferential value however large its
effect. Fixing that needs either a rule that propagates through `RECRUITS` (R5 exists and
fires 0 times) or complex-membership evidence strong enough for R4.

### 2.3 Where it holds up: the graph never silently substitutes an answer

In no hold-out did any surviving claim change **direction**. Genes either kept their
prediction or lost it entirely and returned `best_tier: none`:

| | full graph | SETDB1 held out |
|---|---|---|
| SUV39H1 | inferred, 3 claims | **none** |
| KDM4A | inferred, 3 claims | **none** |
| TET2 | inferred, 1 claim | inferred, 1 claim, same sign |
| DNMT3A | curated + inferred | unchanged |
| DNMT3B | inferred | unchanged |

That is the behaviour you want: when the evidence goes away the system **refuses** rather
than falling back on a weaker source and presenting it at the same confidence. The 5mC arm
is independent of the H3K9me3 arm, exactly as the mark structure implies, which is a small
piece of evidence that the rule layer is doing what it claims rather than laundering one
number.

## 3. What this changes

**For the claims.** `CLAIMS.md` B-series predictions stand, but the derived C-series now
carries a quantified dependency: 87 of 89 derived edges require SETDB1 or DNMT1 to remain
true. That belongs on the slide, not in a footnote.

**For what to compute next.** This is now the strongest argument for the fan-out, and it
is a specific one rather than "more data would be nice": the useful next experiments are
**additional writers and erasers of the same two marks**, because those are what add
independent R1 groundings. A second H3K9me3 writer (SUV39H1, SETDB2, EHMT1) measured
directly would make the H3K9me3 arm survive the loss of SETDB1. A fourth TRIM28-like
scaffold would add nothing to the inference layer.

**For the demo.** Lead with it. "Our reasoning layer collapses 91% if you remove one
experiment, we measured that, and here is the experiment that fixes it" is a much stronger
position than waiting to be asked whether 3 knockdowns can support 89 predictions.

## 4. Reproducing

```bash
python - <<'PY'
import sys; sys.path.insert(0,"src")
import te_reason as T, nesy_rules as N
full,_,_,_ = T.load_graph()
for a in ["none","SETDB1","TRIM28","DNMT1"]:
    e = full if a=="none" else [x for x in full if not (x.subject==a and x.tier=="measured")]
    d,_ = N.forward_chain(e)
    print(f"{a:8} dropped={len(full)-len(e):3} derived={len(d)}")
PY
```
