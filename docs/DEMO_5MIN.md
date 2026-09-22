# The 5-minute demo

Timed, four beats. `DEMO_SCRIPT.md` is the long version with all seven questions; this is
what you actually say on the day. Total 4:40, leaving 20 s of slack.

**Rule for the whole thing:** every number on screen is either measured here or flagged as
inferred. If asked something you have not measured, say so and name the experiment — that
is the demo, not a failure of it.

---

## 0:00 – 0:45 · The gap

> Half your genome is domesticated viruses — 3.8 million transposable element copies.
> Cells switch them off with chemical marks. When that machinery breaks they switch back
> on, and the cell's antiviral alarm fires: inflammation with no infection. That's
> implicated in ageing and blood cancer.
>
> Two things already exist. Tools that measure TE expression — TEtranscripts and its
> successors. And biological knowledge graphs — PrimeKG, Hetionet, Open Targets. **They
> have never been connected, and the graphs don't model a transposable element as a
> first-class entity, so you can't even write down "SETDB1 silences HERVK".**
>
> Meanwhile ENCODE has 1,114 human knockdown experiments across 570 genes. Almost none
> measured transposable elements. The reads are sitting there.

*Say "don't model TEs as first-class entities" — not "no knowledge graph has TEs". The
strong version is false and someone will know ICEO.*

## 0:45 – 2:00 · The measurement, and the statistic that matters

Run it live:

```bash
make query GENE=TRIM28
```

> TRIM28 knockdown, re-quantified from ENCODE data whose authors never counted TEs: AluY
> up 0.79 log₂, padj 0.0005. And the whole TE compartment shifts — median +0.41 against
> −0.02 for protein-coding genes, p = 3.5 × 10⁻¹⁵.
>
> Now the one that matters. **DNMT1: not a single TE subfamily clears FDR. Best padj
> 0.41.** Read only that and you'd conclude DNMT1 doesn't touch transposable elements —
> and you'd have deleted the DNA-methylation arm of the project.
>
> The compartment test says p = 1.6 × 10⁻⁸. Size factors are per-sample, so a
> normalisation error shifts TE and gene fold changes by the *same* amount and cancels in
> the difference of their medians. **A normalisation artefact cannot manufacture a gap
> between two feature sets measured in the same libraries** — which is the field's main
> objection to TE quantification, and this readout is immune to it.
>
> The test itself is standard competitive gene-set testing. What we didn't find in the
> literature is anyone using it as the *primary* TE readout for that reason.

## 2:00 – 3:00 · A prediction for a gene nobody has tested, and its proof

```bash
make query GENE=TET2
```

> TET2 has no TE annotation in Gene Ontology and no knockdown in ENCODE. The engine still
> answers — and prints its work:
>
> TET2 erases 5mC (curated) → 5mC represses TEs (inferred from *our* DNMT1 measurement)
> → **TET2 loss is predicted to lower TE expression.**
>
> Three facts, one of them ours, and you can attack any line. It also flags itself: this
> prediction is grounded in K562 CRISPR data, so asserting it elsewhere is a further
> inference. **An inferred edge inherits the scope of its narrowest evidence** — 87 of our
> 89 predictions carry that flag.
>
> And note the sign. Our collaborator's hypothesis is that TET2 inflammation isn't
> TE-mediated. The engine says something sharper: TET2 loss should actively *lower* TEs.
> That's falsifiable by one experiment.

*Say "predicts" and "mechanistic hypothesis". Never "proves" or "causal".*

## 3:00 – 4:00 · What we don't know — measured, not hedged

Two slides, both negative results, both deliberate.

> **One.** Does TE derepression trigger interferon? First attempt: only 17% of the
> interferon gene set was in our reference, so the code **refused to report it** — a
> coverage threshold, in software. We then fixed it properly: 921 spliced-in gene loci
> took coverage to 77%, with a control showing existing measurements unchanged, r = 0.99.
>
> Answer: no interferon response. And rather than publish that, we checked whether the
> cell line *can* respond. cGAS: 0.21 counts per million. The machinery downstream of it
> is a thousandfold higher. **The pathway has no entry point.** So the finding isn't "TEs
> don't cause inflammation" — it's "this dataset cannot test it, and here's the cell type
> that could."
>
> **Two.** We asked how much our own reasoning rests on. Remove one experiment — SETDB1 —
> and the inference layer collapses from 89 predictions to 8, because each chromatin mark
> is grounded by exactly one knockdown. We also found that TRIM28, our *largest* measured
> effect, contributes nothing to the reasoning at all: it's a scaffold, not an enzyme, so
> it can't ground a mark.

*Show `fig_holdout_robustness.png`. This is the slide that makes the rest credible.*

## 4:00 – 4:40 · What to compute, and why that

> So: two of our five headline questions are answered and three are not, and the system
> knows which is which.
>
> That tells us exactly what to compute. Not "more data" — **more writers and erasers of
> the same two marks**, because those are what add independent groundings. A second
> H3K9me3 writer makes that whole arm survive the loss of SETDB1. A fourth scaffold adds
> nothing.
>
> So we pre-registered one: DNMT3B. The engine predicts its loss raises TEs, via the rule
> most likely to be wrong — transferring from a maintenance methyltransferase to a *de
> novo* one. ENCODE has a 258-million-read knockdown we have never opened. The prediction,
> the endpoint and the interpretation of every outcome are committed to the repo **before**
> we look.

```bash
python src/modal_app.py --dry-run --manifest data/manifests/manifest_prospective.csv
```

> Four libraries, fan-out, shared reference volume, no GPU — alignment is CPU-bound and
> we don't claim otherwise. The graph reasoning stays local; it reaches a fixpoint in
> under a second and putting it in the cloud would be theatre.
>
> The interesting question in AI for science isn't whether a model can produce a
> hypothesis. It's whether it can tell you when the evidence isn't enough — and then name
> the experiment. That's what this does.

---

## If you have 3 minutes, not 5

Cut §2:00–3:00 to the TET2 proof tree only (30 s), and drop the panel-reference detail from
§3:00. Keep: the gap, DNMT1's hidden effect, the proof tree, cGAS at 0.21 CPM, the
hold-out collapse, DNMT3B pre-registered.

## The three questions you will get

**"Isn't this a lookup table?"** TET2 has no annotation and no experiment; it still gets a
signed answer through a stated rule chain. And we measured the dependency — hold-out in
§3:00.

**"Three knockdowns can't support 89 predictions."** Correct, and we quantified it rather
than waiting to be asked: 91% of the inference layer depends on one experiment. That's why
the pre-registered next experiment is a second writer of the same mark.

**"Multi-mapping makes TE quantification meaningless."** Which is why there are two
statistics, and the primary one compares TEs against genes *in the same libraries*.

## Do not say

Check `CLAIMS.md` §0 before the pitch. The four most tempting errors: "no knowledge graph
has TEs", "nobody has looked for TE regulators systematically", "our quantification
method", and "the TE atlas".
