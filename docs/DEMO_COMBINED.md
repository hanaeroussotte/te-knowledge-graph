# The combined demo: an abstract theory of treatment, and a real measurement

Two people, two halves, one question. Read this top to bottom; it is the talk.

---

## 1. The two halves, one sentence each

**The abstract half** (Wolfram's metamodel of medicine). An organism is a pattern grown by a
simple rule. A *disease* is changing one cell. A *treatment* is changing a second cell. You
can then enumerate **every possible disease and every possible treatment** and ask what
recovery actually looks like — something you can never do in a real organism.

**The measured half** (this project). A real gene knockdown is a disease. The TE-expression
profile of the matched control is the healthy state. Every relationship carries its evidence
and its source, and the system refuses to answer when the evidence is thin.

**Why together.** The abstract half can enumerate all treatments but knows no biology. The
measured half knows real biology but has never once observed a *treatment* — every public
experiment breaks something and stops. So the abstract half tells us **what a cure even looks
like and how rare it is**; the measured half tells us **which genes could instantiate one**.

---

## 2. The clean example, with real numbers

Everything below was computed, not asserted. One organism, found by searching simple rules
for one with a long finite life.

**The organism.** 4 colours, each cell decided by its own and its two neighbours' previous
colours. Grown from a single seed. It **dies at step 117** — all cells white.

**The disease.** Change one cell at step 15 → it now **dies at step 70**. 47 steps of life
lost, from one cell.

**Every possible disease.** There are 3,447 single-cell changes. Enumerating all of them:

| Outcome | Count | Share |
|---|---|---|
| **self-healed** — pattern rejoins the healthy one, no treatment needed | 283 | **8%** |
| shortened life | 348 | 10% |
| extended life | 1,710 | 50% |
| **unbounded growth** — never dies, tumour-like | 1,106 | 32% |

The 8% self-healing rate is worth noting: Wolfram's own organism gives 380 of 4,383 = **8.7%**.
Two different rules, same order of magnitude — so it is a property of this class of system,
not of one hand-picked example.

**Every possible treatment.** For that one disease there are 1,479 possible second changes:

| Treatment outcome | Count |
|---|---|
| **exact cure** — back to lifetime 117 | **6** |
| overshoots past the natural lifetime | 829 |
| partial improvement | 370 |
| **unbounded growth — tumour-like** | **195 (13%)** |
| worse than the disease itself | 79 |

**Four things fall out of that table, and all four are the point:**

1. **Cures are rare — 6 in 1,479, 0.4%.** Not because the search is bad. Because they are rare.
2. **13% of treatments cause unbounded growth.** Intervening is not a free action.
3. **Nearby treatments behave completely differently.** Panel 5 of the figure is a spray, not
   a smooth landscape. You cannot interpolate your way to a cure.
4. **Every cure leaves side effects.** The cleanest of the six still leaves **1,622 cells**
   different from the healthy history. The lifetime is restored exactly; the life is not the
   same life.

**The mathematics, in full.** Lifetime *L* = number of steps until every cell is white.
Disease: *L* falls 117 → 70. Cure: *L* is back to exactly 117. Side effects: count the cells
that differ from the healthy pattern. That is all of it — counting and one subtraction.

---

## 3. The same structure in the real data

| In the abstract model | In this project | Our measured number |
|---|---|---|
| healthy organism | TE profile of the matched control | the control arm of each contrast |
| disease = change one cell | knockdown = switch off one gene | SETDB1, TRIM28, DNMT1 |
| lifetime *L* | Δ = median log₂FC of TEs − median of genes | DNMT1 **Δ = +0.13** |
| "the organism got sick" | the TE compartment moved | 63% of 503 TE families up |
| self-healing disease (8%) | a knockdown with no TE effect | SETDB1 at compartment level (corrected p 0.89) |
| **treatment = a second change** | **a second gene perturbation that restores silencing** | **none — we have never measured one** |
| side effects always remain | TE families still moved even if the total is restored | not yet measurable |
| coarse "width history", not cell-by-cell | subfamily level, not individual TE copies | 1,057 subfamilies, not 3.7 M loci |
| machine learning on width history is weak | our own prediction is weak, so we refuse | `best_tier: none` is a supported answer |
| 64 genetic variants, **identical when healthy**, different when diseased | DNMT3A **PWWP vs R882H** | RTE-high vs RTE-**low**, same gene |

**The last row is the one to say slowly.** In the model, some rule cases are never used while
the organism is healthy — so variants differing only there are *indistinguishable* until a
perturbation arrives, and then they diverge. In Hasan et al. 2026 (*GeroScience*,
[10.1007/s11357-026-02510-6](https://doi.org/10.1007/s11357-026-02510-6)), DNMT3A-mutant
carriers split into RTE-high and RTE-low by *which* mutation they carry. Same gene, same
diagnosis, opposite TE behaviour. The abstract model produces that phenomenon generically;
the measured data shows it in humans.

---

## 4. The one shared idea

Wolfram's argument is that these systems are **computationally irreducible** — the only way to
know what a rule does is to run it. No shortcut, no closed form. But inside any irreducible
process there are **pockets of reducibility**: places where a coarse question *does* have a
short answer.

That is exactly this project's epistemology, arrived at independently:

- It does not predict where it has no grounded mechanism — it returns `best_tier: none`.
- It makes claims only along paths with measured or curated support — **the pockets**.
- Its refusals are therefore not timidity. **They are the correct response to irreducibility.**

> The evidence graph is a map of the pockets of reducibility in TE regulation. The refusals
> mark where the map ends.

That sentence is the thesis of the combined project, and it is the most defensible thing
either half says alone.

---

## 5. The demo, as five beats

**Beat 1 — 45 s. "Here is an organism, a disease, and a cure."**
Panels 1–3 of the figure. It dies at 117. Change one cell at step 15 and it dies at 70. Change
a second cell at step 36 and it is back to 117. No biology yet — everyone follows it.

**Beat 2 — 45 s. "Now enumerate everything, which you can never do in a real organism."**
Panels 4–5. 8% of diseases heal themselves. Of 1,479 treatments, **6 cure and 195 cause
tumour-like growth**. And every cure leaves 1,622 cells changed. *Finding treatments is hard
for a computational reason, before any biology is involved.*

**Beat 3 — 60 s. "The same shape, in real data."**
The mapping table. Disease = knockdown. Lifetime = the TE-compartment shift. DNMT1 gives
Δ = +0.13, 63% of families up, holds when any library is dropped, corrected p = 0.045.

**Beat 4 — 60 s. "What neither half can do alone."**
The graph knows which genes write which marks and can name candidates for a rescue. The
abstract model knows what a rescue *looks like*: rare, side-effect-laden, and 13% of the time
harmful. Neither statement is available from the other side.

**Beat 5 — 60 s. "And here is what we cannot do yet."**
**No rescue experiment exists in ENCODE** — every public experiment is a single perturbation.
A real test needs control vs disease vs disease + candidate rescue. We can name the candidates
and cannot yet test them. That is the ask, and it is a specific one.

---

## 6. What we are not claiming

- **The cellular automaton is not a model of transposable elements.** Its 4 colours are not
  chromatin states and its cells are not genomic positions. It is a metamodel: a source of
  general structure about recovery, not a simulation of our system.
- **No analogy is evidence.** Only measured biological results enter the evidence graph. If
  abstract output ever enters, it gets a tier *below* `inferred` and can never ground a rule.
- **The genetic-diversity experiment did not reproduce in our organism, and we say so.** Ours
  has only one unused rule case, and it is never reached even under perturbation — so all 64
  variants behave identically and the phenomenon is absent. Wolfram's organism has three, and
  they *are* reached. Fixing this means searching for an organism with several unused cases
  that perturbation activates. **Reported rather than quietly dropped**, because the version of
  this analogy that matters — PWWP versus R882H — is real in the human data whether or not our
  toy organism reproduces it.
- **The abstract half still needs its own control.** "Recovery uses only a few dimensions" may
  simply be what search in a low-dimensional space always looks like. Run it on scrambled
  rules; if the geometry is unchanged, there is no principle to transfer.

---

## 7. What each person does next

| | Abstract side | Measured side |
|---|---|---|
| **Next** | organism with ≥3 activatable unused rule cases, so genetic diversity works | ingest `RECRUITS` edges — the only missing piece stopping TRIM28's measured effect from reaching the reasoning layer |
| **Then** | the same enumeration across many diseases; are the cure positions predictable at all? | genome-wide run: fixes the two-chromosome bias, the 16% machinery coverage and the interferon guard at once |
| **Shared** | a table of cure positions and their side-effect cost | a table of candidate rescue genes per knockdown, with evidence tiers |
| **Interface** | one CSV each way. Nothing shared but files. | |
