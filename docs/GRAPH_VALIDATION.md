# How good is this knowledge graph? — 42 measured answers

**Run it yourself:** `python src/validate_graph.py` → `results/graph_validation.csv`.

**What this measures and what it cannot.** Every number here is about whether the graph is
*internally coherent and honestly provenanced*. **None of it validates the biology.** An
edge can be structurally perfect and biologically wrong, and 1,316 of these edges are
`predicted` complex memberships that no experiment supports. A graph audit tells you the
plumbing is sound; it says nothing about whether water is the right thing to put in it.

That distinction is the first thing to say if anyone asks "is your graph any good?"

---

## 1. The honest summary

| | |
|---|---|
| **Structurally sound** | 0 schema violations across 9,366 typed edges · 0 self-loops · 0 duplicate triples · 0 blank context cells · 97.6% in one connected component |
| **Fully provenanced** | 100% of edges carry a source and a retrieval date |
| **One real defect found** | a single sign contradiction — and it is *within one layer from one abstract* |
| **Five structural weaknesses** | all of them already known, now quantified |
| **Not measured at all** | whether the edges are biologically true |

**The one-sentence version:** it is a small, well-formed, heavily provenanced graph whose
reasoning capacity rests on four edges and whose TE side is 98% empty — and it knows all of
that about itself.

---

## 2. What passes, and why each check exists

| Check | Result | Why it matters |
|---|---|---|
| Schema violations | **0** / 9,366 | Every edge's subject and object types match what the predicate permits. A graph where `SILENCES` can point at a Pathway is not a graph, it is a spreadsheet with arrows |
| Unknown predicates in derived edges | **0** | The rule layer cannot invent relationship types the schema has never heard of |
| Self-loops | **0** | No gene silences itself — a classic artefact of naïve interaction imports |
| Duplicate triples | **0** | The same claim is never counted twice, which would fake independent support |
| Blank context cells | **0** | All 8 context columns are populated on all edges; `not_applicable` is written explicitly, never left empty. (This matters more than it sounds — pandas reads an empty `NA` back as NaN, silently converting "does not apply" into "not recorded") |
| Provenance: source | **100%** | Every edge names where it came from |
| Provenance: retrieval date | **100%** | Databases change; an undated edge is unreproducible |
| Largest connected component | **97.6%** | The graph is one object, not a pile of fragments. 7 components exist; 6 are tiny |

Degree structure is also healthy: **median degree 2, maximum 188**, and the top 1% of
entities carry only **15.9%** of all edge endpoints. That last number is the useful one —
in a graph assembled carelessly from interaction databases, a handful of hubs (TP53, EGFR)
absorb most of the edges and every path runs through them. Here they do not.

---

## 3. The defect this audit found

**One sign contradiction: `PPARG → Alu`, asserted in both directions.**

```
e6f26f7ee3de8e7   DEREPRESSES   literature   PubMed   PMID:14668325
e7c3bb2786d3e8a   SILENCES      literature   PubMed   PMID:14668325
```

Both edges are `literature` tier and **both come from the same abstract.** This is not two
sources disagreeing — which would be legitimate and interesting. It is one extraction step
producing both directions from one piece of text, which means the extractor is
self-inconsistent.

That is why the audit reports two separate metrics: `sign_contradictions` (1) and
`sign_contradictions_within_one_layer` (**1** — verdict `DEFECT`). Cross-layer disagreement
is data; intra-source disagreement is a bug.

**It is consistent with what was already measured** about that layer: the rule-based
literature extractor was scored at precision 0.109 with direction agreement 10/21 — which is
chance — and was rejected for exactly this reason. The LLM-extracted literature edges that
*were* kept have never been validated against human annotation, and `CRITIQUE.md` lists
annotating ~100 abstracts as an open falsifier. This contradiction is that unmeasured
error rate showing up as a visible artefact.

**What has not been done:** the edge pair has not been removed. Deleting it by hand would
hide the symptom of a layer-wide problem that is honestly declared. The audit flags it on
every run.

---

## 4. The five structural weaknesses, quantified

### 4.1 The TE side is 98% empty — `te_vocabulary_coverage = 0.0199`

The vocabulary has **1,057 TE subfamilies**. **21** TE entities have any edge at all.

That is the single most important number in this document, and it should be said out loud
before anyone else finds it. The graph is not a map of TE regulation; it is a map of the
corner of TE regulation that three knockdowns and a handful of curated annotations happen to
touch. Everything about the architecture is designed for 1,057 columns; 21 are occupied.

### 4.2 The inference layer rests on four edges — `MARK_AT_edges = 4`

`MARK_AT` edges are the only bridge between "this gene writes a mark" and "this mark
silences this TE", and **R1 is the only rule that creates them.** There are four, grounding
**two** marks: H3K9me3 (from SETDB1) and 5mC (from DNMT1).

Every one of the 38 R2 and 45 R3 inferences consumes one of those four. This is the
quantitative version of the hold-out result in `ROBUSTNESS.md`: remove SETDB1 and derived
edges collapse 89 → 8.

### 4.3 A measured effect is wasted unless the gene is an enzyme — `measured_genes_wasted_on_rules = 1`

Three genes have measured TE effects. Two (SETDB1, DNMT1) carry `DEPOSITS_MARK` edges and
can satisfy R1. **TRIM28 cannot** — it is a scaffold, it deposits no mark, and so the largest
measured effect in the entire dataset (AluY +0.790, padj 0.0005) contributes **nothing** to
the reasoning layer.

This is a property of the schema, not of the biology, and it is the most actionable finding
in the audit: it says the next experiment should be another *writer or eraser*, not another
scaffold.

### 4.4 R5 can never fire — `RECRUITS_edges = 0`

**This answers "what happens with the R5 recruitment chain?" definitively.**
`R5_RECRUITMENT_CHAIN` requires `RECRUITS` edges as premises. There are **zero** in the
graph. The rule is not failing to find matches; it has no possible input. It fires 0 times
because a `RECRUITS` predicate is declared in the schema and never populated.

The biology exists and is well established — TRIM28/KAP1 recruits SETDB1, KRAB-zinc-finger
proteins recruit TRIM28, ATF7IP stabilises SETDB1 — so this is a missing-ingest problem, not
a missing-mechanism problem. Nothing in the pipeline currently converts "A recruits B" from
a curated source into a `RECRUITS` edge.

**And it is the fix that would make TRIM28's measurement count.** With `RECRUITS` edges,
TRIM28 → SETDB1 → H3K9me3 → TE becomes a traversable chain, and the largest measured effect
in the dataset would finally enter the inference layer. That single ingest is probably the
highest-value hour of work available on the graph side.

### 4.5 Half the graph is one database — `source_concentration = 0.518`

| Source | Edges |
|---|---|
| Reactome | 4,900 |
| Complex Portal | 2,321 |
| STRING v12.0 | 1,724 |
| GO (mygene.info) | 318 |

Reactome alone is 52% of all edges. Those are pathway-participation edges — real, curated,
and largely *not* what the reasoning uses. They inflate the headline edge count far more
than they inflate the graph's actual reasoning power, which is why "9,455 edges" is a number
to state carefully rather than proudly.

Related: `native_score` is present on only **19.8%** of edges and a `statistic` on **1.2%**.
That is not a defect — GO annotations have no effect size — but it means most of this graph
cannot be weighted or thresholded by strength. Only the measured layer can.

---

## 5. What a *real* validation would require, and is not done

Structural coherence is the cheap part. None of the following has been done:

1. **Held-out edge prediction.** The standard KG benchmark — mask edges, see if the model
   recovers them. Refused deliberately: three knockdowns cannot support a validation set
   (`CLAIMS.md` W11).
2. **Human annotation of the literature layer.** The LLM extractions were used as the
   reference standard for scoring the rule-based extractor and were themselves never checked
   against a human. The PPARG contradiction above is one visible instance of an unmeasured
   error rate.
3. **Recovery of known biology as a positive control.** SETDB1 and TRIM28 firing are a
   *pipeline* control, not a graph control. A graph-level control would be: hide the HUSH
   complex and ask whether the graph re-derives its role in L1 silencing.
4. **Comparison against a baseline.** Does the graph beat "every gene in GO:0010526 silences
   every TE"? Unknown. That baseline is trivial to build and has not been built.
5. **Inter-source agreement.** Where Reactome, STRING and GO all speak to the same gene
   pair, do they agree? Not computed.

Item 3 or 4 would be the most informative next hour. Item 1 needs the atlas to exist first.

---

## 6. The answer to give if asked

> Structurally it's clean — zero schema violations across 9,366 typed edges, no self-loops,
> no duplicate triples, full provenance on every edge, one connected component. The audit
> script is in the repo and prints 42 metrics.
>
> It also found a genuine defect I'd rather tell you about than have you find: one gene–TE
> pair asserted in both directions, both edges extracted from the same abstract. That's the
> literature layer's unmeasured error rate becoming visible, and it's why that layer is
> tiered below measurement.
>
> The honest weaknesses are quantified too. 21 of 1,057 TE subfamilies have any edge. Four
> `MARK_AT` edges carry the entire inference layer. Reactome is 52% of the edge count. And
> R5 has never fired because `RECRUITS` edges were never ingested — which is also the
> cheapest high-value fix available, because it's what would let TRIM28's measured effect
> reach the reasoning layer at all.
>
> What I have *not* done is validate the biology. Structural coherence is not truth.
