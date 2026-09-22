# Coupling a cellular automaton to this project

Written for a two-person collaboration: one side owns the evidence graph and the
perturbational measurements, the other owns cellular-automaton / agent-based modelling.

**The short version.** A knowledge graph plus forward-chaining rules reaches a *fixpoint*.
It has no time, no position along the chromosome, no dose, and it cannot represent feedback.
Those four absences are not incidental — they are the four things this project has already
documented as structural limitations, and they are exactly what a cellular automaton is for.
The pairing is complementary rather than fashionable, and §1 is the argument for why.

---

## 1. What the CA buys that the graph structurally cannot

### 1.1 Feedback — the one that is already a known defect

`CRITIQUE.md` records an open structural issue: cGAS has a nuclear role maintaining H3K9me3
(*Nature Aging* 2026, [10.1038/s43587-026-01206-y](https://doi.org/10.1038/s43587-026-01206-y)),
so cGAS is not only a downstream sensor of TE-derived nucleic acid — it also acts upstream in
chromatin control. The path

```
TE derepression → cytoplasmic nucleic acid → cGAS → interferon → … → chromatin state
```

therefore **contains a cycle**, and a directed-acyclic reading of it is wrong.

Forward chaining to a fixpoint over a cyclic dependency does not model the cycle; at best it
ignores it. **A dynamical system on a lattice handles cycles natively — that is what it is
for.** This is the single strongest argument for the collaboration, because it is not "we
could also add a simulation": it is "the graph has a documented representational failure and
the CA is the correct formalism for it."

### 1.2 Position along the chromosome

The graph's TE nodes are **subfamilies**. `AluY` is one node standing for 104,272 loci
scattered across the genome with no positional relationship to one another. But heterochromatin
does not act on subfamilies — it acts on *neighbourhoods*: H3K9me3 nucleates at a site and
**spreads locally**, HP1 oligomerises, boundary elements stop it. Position-effect variegation
is the classical read-out of exactly this.

A local-rule model on a 1D lattice of genomic bins is the natural formalism for spreading.
The graph cannot express "this AluY copy is 2 kb from a nucleation site and that one is
80 kb away", and that distinction is probably why only some copies respond.

### 1.3 Bistability — and this one explains an observation you already have

`TE_RESOLUTION.md` and the aggregation analysis record an unexplained finding: aggregating
subfamilies to family level *loses* signal, and the "only young subfamilies respond"
explanation was tested and **rejected**. So why do only some elements move?

And your own *GeroScience* paper contains a sharper version of the same puzzle: among
DNMT3A high-VAF carriers there were **two distinct subgroups — RTE-high and RTE-low — at the
same genotype class**, with PWWP-domain mutations exclusively RTE-high and the R882H hotspot
clustering RTE-low.

**A deterministic rule engine cannot produce that.** R2 gives one direction per gene, for all
loci, for all carriers. A stochastic local-rule model with a bistable silenced/active state
produces **bimodal outcomes from identical parameters** as a generic property — that is what
bistability means. The CA is therefore not decoration on this project: it is a candidate
*explanation* for a bimodality the current model structurally cannot generate.

### 1.4 Time and dose

Every measured edge in the graph carries `timepoint` and `dose` context columns, and every one
of them reads `not_applicable`. A knockdown is a steady-state endpoint. Whether partial loss of
a writer produces graded or switch-like derepression, and how fast silencing decays through
replication-coupled dilution, are dynamical questions the graph has no slot for.

---

## 2. Coupling A — heterochromatin spreading along a real chromosome

**The most buildable, and the one to do first.**

**Lattice.** Genomic bins (1–5 kb) along one real chromosome. Use chr19 — it is already the
project's reference chromosome, it is the most repeat-dense and Alu-rich chromosome in the
genome, and it carries the KRAB-zinc-finger clusters whose products recruit TRIM28. Real TE
positions come from the RepeatMasker annotation the project already builds
(`src/build_te_annotation.py` → per-locus GTF).

**Cell state.** Per bin: `{euchromatin, H3K9me3, 5mC, boundary}` — possibly as two independent
binary marks rather than one exclusive state, since 5mC and H3K9me3 are separate layers in the
graph and have separate writers.

**Local update rules** (the CA proper):

| Rule | Biology it encodes |
|---|---|
| nucleation | a bin containing a KRAB-ZFP binding site, or a young full-length TE, can seed H3K9me3 |
| spreading | a bin adopts a mark with probability *p* if ≥*k* of its neighbours carry it **and** an active writer for that mark exists |
| boundary | bins marked as insulators (CTCF/TAD boundaries) refuse the mark and block propagation |
| dilution | each replication step, marks are lost with probability *d* unless re-written — this is what makes DNMT1 (maintenance) mechanically different from DNMT3A (*de novo*) |
| erasure | an active eraser for the mark increases loss probability |

**Grounding, so it is not a simulation of nothing.** Which writers and erasers exist per mark
comes directly from the graph's 44 mechanism edges — 5mC: DNMT1/3A/3B versus TET1/2/3;
H3K9me3: SETDB1, SUV39H1/2, EHMT1/2 and others versus the KDM3/KDM4 families; H3K27me3:
EZH1/2 versus KDM6A/B. **A knockdown is then a single parameter change: set that writer's
activity to zero.** No new formalism, no fitted magic number.

**Validation route that exists today.** Run the CA with SETDB1 active, then with SETDB1 off.
Aggregate the per-locus silencing loss **up to subfamily level** and correlate with the
measured subfamily log₂FC. The project has those measurements for three knockdowns
(`results/deseq2_results.csv`). That is a real, if weak, check: the CA is not being asked to
predict something unobserved, it is being asked to reproduce a pattern that already exists.

**The prediction it makes that the graph cannot.** Per-locus derepression should depend on
**distance to the nearest nucleation site** and on **local TE density**, not on subfamily
identity. That is a locus-level prediction, falsifiable with a locus-level quantifier
(Telescope, [10.1371/journal.pcbi.1006453](https://doi.org/10.1371/journal.pcbi.1006453), or
SQuIRE) — and locus resolution is already the documented next frontier in
`TE_RESOLUTION.md` §8. The CA supplies the reason to go there, and the hypothesis to test
when you do.

**Falsifier, stated in advance.** If measured locus-level derepression after a writer
knockdown is independent of distance to the nearest nucleation site and of local TE density,
the spreading model is wrong for this system and should be dropped, not tuned.

---

## 3. Coupling B — clonal haematopoiesis as a stochastic CA on the niche

**The one that uses your published biology, and the more ambitious of the two.**

**Lattice.** Haematopoietic stem cells in a niche. A lattice adds local competition for niche
space; a well-mixed population is the simpler baseline and should be run first so you can
show what the spatial structure actually adds.

**Cell state.** `genotype ∈ {WT, DNMT3A-mut, TET2-mut, double}` × `TE state ∈ {low, high}` ×
inflammatory output.

**Rules.** Division, differentiation and loss; stochastic switching of the TE state with a
genotype-dependent bias (from Coupling A, or as a simple bistable switch); TE-high cells emit
TNF-α/NF-κB signal; inflammation modifies the fitness of neighbours — **and that is the
feedback edge the graph cannot carry** (§1.1).

**What it should reproduce, from your own cohort.** The *GeroScience* data gives three
independent targets:

1. DNMT3A-mutant clones reaching higher VAF than TET2-mutant.
2. **Bimodality of the RTE phenotype at fixed genotype** — the RTE-high / RTE-low split within
   DNMT3A high-VAF (§1.3).
3. TET2-mutant clones expanding **without** the TE→inflammation route, with inflammation
   arriving instead through a metabolic/redox programme (oxidative phosphorylation, ROS,
   mTORC1).

Target 3 is the interesting one: it means the model must produce inflammation by **two
different routes** and predict which genotype takes which. A model that can only do it by
hard-coding the answer has failed.

**Falsifier.** If bimodality can only be produced by tuning a switching rate to an
implausible value, or if the DNMT3A/TET2 asymmetry has to be imposed rather than emerging
from the writer/eraser difference, the model is fitting rather than explaining.

**Honest caveat.** n = 10 high-VAF donors. A CA can be made to reproduce almost any pattern in
ten samples. Treat agreement as a consistency check, never as validation, and say so before
anyone asks.

---

## 4. What not to do

Three couplings that sound good and are not worth your time:

**Do not call a graph neural network a "neural cellular automaton."** Weight-shared local
update rules on a graph *is* a GNN. The CA label adds nothing except the question "why didn't
you just say GNN", and it invites comparison to GEARS and TxPert
([10.1038/s41587-023-01905-6](https://doi.org/10.1038/s41587-023-01905-6),
[10.1038/s41587-026-03113-4](https://doi.org/10.1038/s41587-026-03113-4)), which do that
properly and at scale.

**Do not use the CA to fill in missing graph edges.** That is link prediction, which this
project deliberately refused because three measured perturbations cannot support a held-out
validation set. Generating edges from a simulation does not create validation data — it
launders a model's assumptions into the evidence layer, which is precisely what the evidence
tiers exist to prevent. If CA output ever enters the graph it needs its own tier, below
`inferred`, and it must never satisfy R1.

**Do not model TE evolutionary dynamics for the pitch.** A transposition/silencing arms race
over evolutionary time is a legitimate CA application and there is real literature, but this
project's own scope rules forbid claiming anything about forecasting TE evolution — nothing
here models sequence divergence, transposition rates or population genetics. Out of scope,
and saying so is better than being caught.

---

## 5. Division of labour

| | Graph side | CA side |
|---|---|---|
| Owns | evidence layers, provenance, tiers, the rule engine, the measured contrasts | lattice, state space, update rules, parameter inference, simulation |
| Supplies to the other | which writers/erasers exist per mark; the measured subfamily effects; TE positions from RepeatMasker | per-locus predictions; the distance/density dependence; bistability behaviour |
| Interface | `edges_mechanism.csv` (44 writer/eraser edges) + the per-locus TE GTF + `deseq2_results.csv` | a per-locus silencing probability table, aggregable to subfamily |

**Keep the interface a file, not a shared abstraction.** One CSV each way. It means neither of
you is blocked on the other's refactor, and it means the CA's outputs arrive in the same
provenance-bearing form as everything else — with a source, a date, and a tier that says
`simulated`.

---

## 6. The minimum worth building first

Coupling A on chr19, in this order:

1. Per-locus TE positions from the existing RepeatMasker pipeline. Already solved.
2. 1D lattice over chr19 at 1 kb bins; one mark (H3K9me3) only; nucleation at young
   full-length L1 and at annotated ZNF-cluster positions.
3. Two runs: writer on, writer off. Per-locus silencing loss.
4. Aggregate to subfamily; correlate with the measured SETDB1 log₂FC.
5. Plot per-locus loss against distance to nearest nucleation site — **this is the figure**,
   because it is the prediction the graph cannot make.

Steps 1–5 are a day's work for two people and need no new data. One mark, one chromosome, one
knockdown. Resist adding 5mC, replication timing and the niche model until step 5 produces
something.

**And state the under-determination honestly.** A CA has many free parameters; the constraints
available are three knockdowns at subfamily resolution. The model is under-determined, so its
value is not that it fits current data — it is that it makes **locus-level predictions that a
locus-level quantifier can refute.** That framing is defensible. "We simulated the genome and
it looks right" is not.
