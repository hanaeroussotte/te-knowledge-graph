# Where we are — a plain walkthrough

Written to be read when tired. No jargon that isn't explained. Newest work last.

---

## 1. What the project is, in one paragraph

Transposable elements (TEs) are repeated pieces of DNA making up about half the human
genome. Cells keep them switched off using chemical marks on DNA and on the proteins DNA
wraps around. When the machinery that applies those marks breaks, TEs switch back on — and
that has been linked to inflammation and ageing.

This project does four things: it **re-analyses public experiments** where someone switched
off a gene, to see what happened to TEs (which the original authors usually never looked at);
it turns each result into a **relationship with a source attached** ("gene X silences TE Y,
measured here, this confidence level"); it **combines those with known biology** from public
databases into one network; and it **reasons over the network** to propose things nobody has
measured — always showing its working, and saying "not enough evidence" when that is the
answer.

The long-term object is an atlas of perturbations. Right now it is an architecture with three
worked experiments. That distinction is the first thing to say out loud.

---

## 2. The three experiments everything rests on

Public data from ENCODE, all in K562 (a leukaemia cell line), 11 sequencing libraries:

| Gene switched off | What it does | What we saw in TEs |
|---|---|---|
| **SETDB1** | writes the H3K9me3 mark | two families of endogenous retroviruses went up |
| **TRIM28** | scaffold — recruits SETDB1 | Alu elements went up strongly (AluY, the clearest single result) |
| **DNMT1** | maintains DNA methylation (5mC) | no single TE family passed the threshold, but the **whole TE compartment shifted up** |

The DNMT1 row is the important one, because DNA methylation is the only route by which the
reasoning layer can reach **DNMT3A** and **TET2** — the two genes in your own published
hypothesis. If the DNMT1 result falls, that whole derivation falls with it.

---

## 3. What happened today, in order

### 3.1 Modal got connected, and pre-flight caught three things

Modal is cloud compute — you rent machines by the second. Before spending anything I read
the code that would run, and found three problems that would each have wasted the run:

1. **The recipe was missing an ingredient.** The setup step downloaded the genome and built
   the search index, said "success", and **never built the TE list** the counting tool needs.
   Every worker would have crashed — *after* the expensive 1–2.5 hour index build.
2. **The documented command couldn't work.** The instructions said `modal run`, but the code
   is written to be started differently. It would have failed immediately.
3. **There was no way to get the results back.** The counting step writes to cloud storage;
   the analysis step reads local files. A *fully successful* run would have left you with
   nothing to analyse.

All three are fixed. Lesson worth keeping: **the run reported success on a broken setup** —
that is why it now refuses rather than reporting success when something is missing.

### 3.2 The statistics got attacked, and one headline number was retracted

You sent the summary out for review. The reviewer found the real weakness, so I tested it
rather than argued.

**The problem, simply.** We were saying "the TE compartment shifted, p = 0.000000016". That
p-value was calculated as if the ~350 TE families were 350 independent pieces of evidence.
They are not — they rise and fall together, because they share the same machinery and similar
sequences. It is like asking 350 people in the same family for an opinion and reporting it as
350 independent opinions.

**How bad?** I measured it. In the SETDB1 and TRIM28 experiments, 322 TE families carry about
**two families' worth** of independent information. So the p-value was overstating the
evidence roughly 150-fold.

**What survived.** DNMT1 — the one that had to:

- the shift is **+0.13**, and 63% of 503 TE families moved up
- **the same direction in all six** different ways of defining "the TE set"
- **drop any one library and it holds** (+0.10 to +0.19, direction never flips)
- it is the most extreme of the three possible ways of shuffling the labels, by 3.7×
- corrected p = **0.045**, after measuring the inflation

Weaker than before, and much better supported. **The 5mC anchor holds.**

**What didn't.** TRIM28's *whole-compartment* claim. Shuffling the sample labels produced a
*bigger* effect than the real labels did. So that is now reported as an effect size with weak
statistical support. Its **individual** results are untouched — AluY is a different
calculation and still stands.

**The sentence to say:** *with two replicates per group there are only three possible label
shufflings, so no p-value below 0.333 is even reachable. That is a limit of the experiment,
not of the analysis.* Anyone quoting a tiny p-value from a two-replicate design is quoting an
artefact.

### 3.3 The cellular-automata collaboration got a design

Your collaborator's framing — abstract system discovers general principles of recovery, the
graph looks for biological analogies, real data tests them — is better than what I first
proposed, because it refuses to claim "dimension 3 = gene X". Two things to add:

- **Pre-commit to what each principle predicts before looking at the graph.** In a network
  with 9,366 relationships you will *always* find something analogous to any abstract
  principle. Writing the prediction down first is what makes it a test instead of a story.
- **The abstract side needs its own control.** "Recovery uses only a few dimensions" may just
  be what optimisation in 8 dimensions always looks like. Run the same search on scrambled
  rules; if the geometry is the same, there is no principle to transfer.

### 3.4 And then the check that hurt

The collaboration design asks: *when you break one silencer, does the cell compensate with
another?* That is testable, so I tested it — and while doing so ran the most basic check of
all, which had never been applied to these three experiments: **did each knockdown actually
work?** You check that by asking whether the targeted gene's own activity went down.

| Gene | its own activity change | how much remains | verdict |
|---|---|---|---|
| **DNMT1** | −1.87 | 27% | **worked** |
| **TRIM28** | −1.12 | 46% | **worked** |
| **SETDB1** | −0.35 (not significant) | **78%** | **not confirmed** |

**SETDB1's knockdown cannot be confirmed in this data**, and SETDB1 is the anchor for the
H3K9me3 mark — remove it and the derived predictions collapse from 89 to 8.

Two honest qualifications, both real:

- The method used for SETDB1 (CRISPRi) blocks transcription, and we are reading a steady-state
  snapshot at shallow depth — so a weak reading is not proof the experiment failed.
- **Something did happen**: SETDB1 knockdown produced the two endogenous-retrovirus results.
  A perturbation that did nothing should not do that.

So the correct statement is *not confirmed*, not *failed*. But it now belongs in the
limitations, and full-depth sequencing would settle it. This is exactly the check written into
the pre-registration for the upcoming experiment, and it had never been pointed at the
existing three. Pointing your own checks at your own old results is how this kind of thing
gets found.

**The compensation question itself could not be answered**: only **9 of 55** genes in the
silencing machinery are even measurable in the current two-chromosome reference (16%), and only
2–3 alternative writers per experiment. SETDB1's knockdown showed alternative writers up
(+0.215 versus +0.018 for genes generally) which *points* toward compensation, but with n = 3
that is a hint, not a result. **Refused, with the number that would fix it: going genome-wide.**

---

## 4. Where that leaves you

**What is solid**
- DNMT1 moves the TE compartment: +0.13, consistent every way it is sliced, survives dropping
  any library, corrected p = 0.045. **The 5mC anchor holds, so the DNMT3A/TET2 derivation stands.**
- TRIM28 and DNMT1 knockdowns demonstrably worked.
- AluY up 0.79-fold (log₂) after TRIM28 loss, with the strongest individual statistic in the project.
- The network is structurally clean: 0 schema violations, full provenance, one connected component.
- The system refuses when evidence is thin — and did so three more times today.

**What is now weaker than it was this morning**
- Every Mann–Whitney p-value: retracted.
- TRIM28's whole-compartment claim: effect size only.
- SETDB1's knockdown efficiency: unconfirmed.

**What is unchanged**
- The reasoning layer, the proof trees, the provenance, the anchor-dependence result, the
  prior-art work, and the demo.

---

## 5. The one decision left

The genome-wide run on Modal has not been started. It would fix, in one go: the
two-chromosome bias, the 16% silencing-machinery coverage, the interferon coverage guard, and
the SETDB1 efficiency question. It costs 1–2.5 hours for the shared index plus about an hour
of parallel work.

**But you can give the whole talk without it**, and today's statistical correction was worth
more than the compute would have been. If there is time, start the index build and let it run
while you present. If not, present what you have — including the three refusals, which are
the most distinctive thing in the room.
