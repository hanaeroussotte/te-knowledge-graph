# Knowledge graphs, from zero

**For someone who has never built one.** By the end you should be able to explain what a
knowledge graph *is*, why anyone bothers, how the computer actually stores and searches it,
what reasoning over one means, and exactly which of those things this project does. No
prior computer science assumed.

---

## 1. Start with the problem, not the solution

Suppose you keep your research facts in a spreadsheet. One row per gene:

| gene | function | disease | drug |
|---|---|---|---|
| DNMT3A | DNA methyltransferase | clonal haematopoiesis | azacitidine |
| SETDB1 | H3K9 methyltransferase | — | — |

This works until you ask a question that **travels**. For example:

> *Is there any route connecting SETDB1 to inflammation?*

There is no column for that. The answer might be: SETDB1 recruits nothing directly, but it
writes a chemical mark, and that mark silences a transposable element, and that element's
RNA triggers a sensor, and that sensor turns on interferon, which is inflammation. That is
**five hops**, and each hop lives in a different row of a different table.

A spreadsheet stores *facts about things*. What you actually needed was *the relationships
between things*, as first-class objects you can follow.

**That is the whole idea.** A knowledge graph is a database whose primary content is the
relationships.

---

## 2. Nodes, edges, triples

Three words and you have the vocabulary.

- A **node** is a thing. `SETDB1`. `H3K9me3`. `AluY`. `azacitidine`.
- An **edge** is a stated relationship between two nodes, *with a direction and a type*.
- A **triple** is one edge written out: **(subject, predicate, object)**.

```
        writes                 silences
SETDB1 ──────────► H3K9me3 ──────────► HERVK
 node    predicate   node    predicate  node
```

Two triples:

```
(SETDB1,  DEPOSITS_MARK, H3K9me3)
(H3K9me3, MARK_AT,       HERVK)
```

Direction matters enormously and is the commonest beginner error. `(SETDB1, SILENCES,
HERVK)` and `(HERVK, SILENCES, SETDB1)` are different claims, and only one is biology.

**Analogy.** A knowledge graph is a road map. Cities are nodes, roads are edges. A
spreadsheet of cities tells you each city's population; a *map* lets you ask "can I get
from here to there, and by what route?" The route is the answer, and only the map has
routes.

---

## 3. Why the "graph" shape is genuinely different

Here is the same question in both worlds.

**In a table.** To follow five hops you need five JOINs, and you must know in advance that
you wanted five — the query's shape hard-codes the answer's shape. If the real path turns
out to be four hops or six, your query silently returns nothing.

**In a graph.** You say: *start at SETDB1, walk outward up to 5 steps, tell me every path
that ends at inflammation.* You did not have to know the length or the route. The database
finds them.

That one capability — **variable-length path search** — is the reason knowledge graphs
exist. Everything else is bookkeeping around it.

---

## 4. How it is actually stored

Three representations, all equivalent, each convenient for something different. Worth
knowing because people will use all three words at you.

### 4.1 Edge list

Literally a table of triples. This is what our `edges_*.csv` files are:

```
subject, predicate,     object
SETDB1,  DEPOSITS_MARK, H3K9me3
SETDB1,  SILENCES,      HERVE-int
TRIM28,  RECRUITS,      SETDB1
```

Simple, human-readable, and what you want for provenance — you can put extra columns on
each row (where the fact came from, how confident you are). **This project's graph is an
edge list**, and §7 of the walkthrough lists our 13 columns.

### 4.2 Adjacency list

For each node, the list of nodes it points to. This is what makes traversal fast:

```
SETDB1  -> [H3K9me3, HERVE-int, HERV9NC-int, LTR/ERV1]
TRIM28  -> [SETDB1, AluY, AluYa5, MIR, SVA_D]
H3K9me3 -> [HERVE-int, HERV9NC-int, LTR/ERV1]
```

Why it matters: to walk from `SETDB1` you need its neighbours *immediately*, not after
scanning every row. An adjacency list gives you them in one lookup. Our code builds one at
load time (`_idx()` in `nesy_rules.py` groups edges by predicate for the same reason).

### 4.3 Adjacency matrix

A big grid of 0s and 1s: row *i*, column *j* is 1 if node *i* points to node *j*.

```
           SETDB1  H3K9me3  HERVK
SETDB1        0       1       0
H3K9me3       0       0       1
HERVK         0       0       0
```

Nobody stores a biological graph this way — with 1,910 nodes that is 3.6 million cells,
almost all zero (the graph is **sparse**). But the matrix view is what makes the
mathematics work, and one fact is worth carrying:

> **If `A` is the adjacency matrix, then `A²` tells you about 2-hop paths, `A³` about
> 3-hop paths, and so on.** Entry (i,j) of `A^n` counts the paths of length exactly *n*
> from *i* to *j*.

That is the formal reason "reachability" is a matrix-power question, and it is the seed of
every graph embedding method in §8.

---

## 5. Schema: the part people skip, and the part that mattered most here

A **schema** (or **ontology**) says which *types* of node exist and which *types* of edge
are allowed between them. It is the graph's grammar.

```
Gene   --DEPOSITS_MARK-->  ChromatinMark
Gene   --SILENCES------->  TEFamily
Gene   --MEMBER_OF------>  Complex
Gene   --PARTICIPATES_IN-> Pathway
```

Why this is not bureaucracy:

**You cannot store a fact your schema has no type for.** This is the entire origin of this
project. PrimeKG, Hetionet and Open Targets have node types for genes, diseases, drugs,
pathways, phenotypes, anatomy. **None of them models a transposable element as a
first-class entity.** So `(SETDB1, SILENCES, HERVK)` is not a statement that is *false* in
those graphs — it is a statement they cannot write down. There is nowhere to put `HERVK`.

Our schema adds three node types that the big graphs lack: `TEFamily`, `TEClass` and
`ChromatinMark`. The third is less obvious and does just as much work — because once
`H3K9me3` is a node in its own right, you can reason *"this gene writes the same mark as
that gene, so it may have the same effect"*. Without it, that thought has nowhere to live.

*Scoping note, because it matters: an ontology for **bacterial** mobile elements does exist
(ICEO), and nothing prevents anyone building a TE-aware graph tomorrow. The claim is about
the major general-purpose human biomedical graphs, on a stated date.*

---

## 6. Querying: traversal, paths, and why you must bound the search

### 6.1 Neighbours

The simplest query: *what does SETDB1 connect to?* One adjacency-list lookup.

### 6.2 Paths

The interesting query: *how does SETDB1 connect to interferon?* The computer does a
**breadth-first search** — look at everything one hop away, then everything two hops away,
and so on — recording the route it took.

### 6.3 The problem with that, and the two guards we use

Real biological graphs are horrifyingly well connected. Within five or six hops, almost
everything reaches almost everything. So an unbounded path search returns thousands of
paths that are *technically true and completely useless*: "SETDB1 interacts with a protein
that participates in a pathway that contains a protein that interacts with interferon."

Two guards, both in `nesy_rules.py`:

**`MAX_HOPS = 4`.** A hard limit. Blunt, and necessary.

**A path grammar.** Only certain *sequences of edge types* count as an explanation. For
example `DEPOSITS_MARK → MARK_AT → SENSED_BY → SIGNALS_TO` is admissible; a chain of four
`INTERACTS_WITH` edges is not, because protein-interaction chains read like mechanism and
are not. This is the single most useful thing we do to path search: **restrict by edge
type, not just by length.**

**Analogy.** Without a grammar you are the person who proves any two actors are connected
through six films. True, and no use to a casting director. The grammar says: only count
connections of the kind that actually predict something.

---

## 7. Provenance: where a knowledge graph becomes science

Most tutorials stop at nodes and edges. For research use, the critical question about any
edge is **why do you believe it?**

Every edge in this project carries 13 columns, and the important ones are:

| Column | Why it exists |
|---|---|
| `evidence_tier` | `measured` / `curated` / `mechanism` / `literature` / `inferred` |
| `source` | the specific database, paper, or experimental contrast |
| `effect_size`, `statistic` | the number, and its p-value |
| `edge_id` | a stable hash — `e` + 14 hex characters of a SHA-1 |

The stable `edge_id` is worth dwelling on. Because it is a hash of
subject/predicate/object/tier, it is **the same every time the graph is rebuilt.** That is
what makes a citation like `[e3f9a1c04b2e77]` resolvable, and what lets someone else check
a proof line by line. An edge you cannot cite is an edge you cannot audit.

We also carry the **experimental context** of every edge as columns — cell type, species,
perturbation modality, assay, timepoint, dose, reference genome, TE resolution, quantifier
— because `SETDB1 —SILENCES→ HERVE-int` read without them is a universal claim, and what
we measured was one cell line, one modality, one assay.

---

## 8. Two ways to get new knowledge out of a graph

This is the fork in the road, and this project deliberately takes the left branch while
saying the right branch is where things are heading.

### 8.1 Embeddings and link prediction (the machine-learning route)

**Idea.** Give every node a list of numbers — a **vector**, say 128 of them — chosen so
that nodes which sit in similar positions in the graph get similar vectors. That is an
**embedding**. Then train a model: given two node vectors, predict whether an edge should
exist between them.

**Why it works at all.** It is guilt by association, formalised. If gene A and gene B both
belong to the same complex, both write the same mark, and both silence four of the same TE
families, their vectors end up close — and the model will propose the fifth TE family for
whichever gene lacks it.

**What it gives you.** Coverage. A score for *every* possible pair, including pairs nobody
has ever studied. This is roughly what TxPert does for perturbation responses, with
considerably more sophistication.

**What it costs you.** Two things:

1. **No explanation.** The output is "0.87". You cannot ask *why*, and you cannot check it.
2. **It needs enough known edges to learn from, and a held-out set to prove it learned.**

**We did not build this, and the reason is the second point.** With three measured
knockdowns there is no way to hold out a validation set. An unvalidated AUC would have been
the most impressive-looking and least meaningful number in the project. It is listed as
deliberately not shipped.

### 8.2 Rules and forward chaining (the symbolic route — what we do)

**Idea.** Write down, in advance, logical rules of the form *if these facts are in the
graph, then add this fact*. Apply them repeatedly until nothing new appears.

A rule (this is our R3, in plain form):

```
IF   gene G erases chromatin mark M
AND  mark M represses TE family T
THEN G is predicted to DEREPRESS T
```

**Forward chaining** is the algorithm: sweep the whole graph, fire every rule that
matches, add the conclusions, sweep again. Repeat until a full sweep adds nothing. That
terminal state is called the **fixpoint**.

```
round 1:  apply all rules → 60 new edges
round 2:  apply all rules → 29 new edges   (some rules needed round 1's output)
round 3:  apply all rules → 0 new edges    ← fixpoint, stop
```

**Why it always terminates:** rules only ever *add* edges, the vocabulary of possible edges
is finite, so you cannot add forever. Guaranteed, not hoped for.

**What it gives you that embeddings cannot: the proof.** Because you know which rule fired
and on which premises, you can print the derivation as a tree:

```
TET2 → DEREPRESSES → TE:global                      [inferred, R3]
├── TET2 erases 5mC                                 [curated: GO:0070579]
└── 5mC represses TEs                               [inferred, R1]
    ├── DNMT1 writes 5mC                            [curated: GO:0003886]
    └── DNMT1 loss raised the TE compartment        [MEASURED, p = 1.6e-08]
```

Three facts, one of them our own measurement, and **every line is attackable**. That is the
difference between a prediction and an assertion.

**What it costs you:** coverage. Rules fire only where their premises exist. Our engine
derives 89 edges; an embedding model would happily score millions of pairs.

### 8.3 The honest position

Symbolic reasoning is not permanently better than learning. It is better *now*, for this
project, because the measured matrix is tiny and auditability is the product. The rule
engine is a **bootstrap**: it generates testable hypotheses until the atlas is big enough
to train on. Eventually both should coexist — rules for the auditable mechanistic path,
learning for coverage.

---

## 9. Tiers, and why confidence takes the *weakest* link

Our five evidence tiers, strongest first: `measured`, `curated`, `mechanism`,
`literature`, `inferred`.

When a conclusion rests on a chain, what confidence does it get? The rule we use:

> **A path's tier is the weakest tier on it.** Not the average, not the strongest.

Why the average would be wrong: a chain of one beautiful measurement plus one dodgy
text-mined edge is only as good as the dodgy edge. Averaging lets a strong link launder a
weak one. A chain is a chain.

This is the same logic as a rope: its strength is the strength of its weakest strand, not
the mean of the strands.

---

## 10. The one thing that stops the language model lying

The word **neurosymbolic** describes a split, and it is worth being precise about where the
line sits.

- The **neural** part — a language model — is used for exactly one job: reading 3,120 paper
  abstracts and converting English sentences into structured triples. Turning language into
  structure is what it is good at.
- The **symbolic** part — explicit rules over the graph — does all the reasoning.
- **Neither is asked to do the other's job.**

And at the boundary sits the **citation gate**. Every sentence the system displays must
contain an edge id matching `\[(e[0-9a-f]{14})\]`. Sentences without one are **discarded
before display**, not flagged. On eight worked genes: 19 sentences kept, 2 rejected.

This is the structural answer to hallucination. The model never decides what is true. It
proposes structure; anything that cannot point at a resolvable edge id does not reach you.

---

## 11. Our graph, in numbers

| | |
|---|---|
| Nodes | **1,910** — 1,199 Complex, 400 Pathway, 280 Gene, 27 GOTerm, 3 ChromatinMark, TEFamily |
| Edges | **9,366** across five evidence layers |
| ↳ curated | 9,263 (GO, STRING v12 ≥700, Reactome, Complex Portal) |
| ↳ mechanism | 44 (hand-built writer/eraser map, cited) |
| ↳ literature | 32 (LLM-extracted from 3,120 abstracts) |
| ↳ measured | 12 (our own re-analysis of ENCODE knockdowns) |
| ↳ inflammation | 15 (all `NO_DETECTED_EFFECT_ON` — a measured absence) |
| Derived by rules | **89** — R3 45, R2 38, R1 4, R4 2, R5 0, R6 0 |
| Rules that fire 0 times | R5, R6 — **reported, not hidden** |

Two numbers deserve a second look.

**Only 12 measured edges out of 9,366.** The curated layer is vastly larger. That is normal
and fine — but it is why the measured layer is tiered *above* curated: it is the part that
is ours, and the part that grounds everything the rules derive.

**89 derived edges from 3 experiments**, and we measured how fragile that is. Remove
SETDB1's 8 measured edges and the derived layer collapses to **8**, because only four
`MARK_AT` edges exist and each chromatin mark is grounded by exactly one knockdown. See
§19 of the walkthrough. Knowing that number is better than not knowing it.

---

## 12. Words you will hear, and what they mean

| Term | Plain meaning |
|---|---|
| **triple** | one edge: (subject, predicate, object) |
| **schema / ontology** | which node and edge types are allowed |
| **RDF** | a W3C standard for writing triples; the "formal" way. We use CSV instead |
| **property graph** | the other main style, where nodes and edges carry arbitrary attributes. Ours is effectively this |
| **SPARQL / Cypher** | query languages for RDF and property graphs respectively. We query in Python |
| **traversal** | walking edges from a starting node |
| **BFS** | breadth-first search: explore all 1-hop, then all 2-hop, … |
| **sparse** | almost all node pairs have no edge. Always true in biology |
| **embedding** | a node represented as a list of numbers |
| **link prediction** | scoring whether a missing edge should exist |
| **forward chaining** | apply rules repeatedly until nothing new is derived |
| **fixpoint** | the state where another round of rules adds nothing |
| **Horn clause** | a rule shaped "if A and B and C then D" |
| **provenance** | the record of where a fact came from |
| **inference vs assertion** | derived by a rule vs stated by a source |

---

## 13. If you remember four things

1. **A knowledge graph is a database of relationships**, and its point is answering
   questions that travel across several hops.
2. **The schema decides what is even sayable.** No TE node type means no TE statement —
   which is why this project needed its own graph.
3. **Provenance and a stable edge id are what make it science** rather than a pile of
   assertions. If you cannot cite an edge, you cannot audit a conclusion.
4. **Reasoning gives you proofs; learning gives you coverage.** We chose proofs because the
   measured layer is small and auditability is the product — and said plainly that once the
   atlas grows, learning becomes the right addition.
