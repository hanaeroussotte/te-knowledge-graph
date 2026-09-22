# Running it today, alone, on Modal

Written on the day, for one person with limited hours and credits that cost real money.

> **Before anything else: you can give the whole talk with no compute.** The deck, the
> demo, the repository, the hold-out result and the prior-art work are all done and saved.
> Everything below *adds* to a complete story. If Modal fights you for an hour, stop and
> rehearse instead. That is not defeat, it is triage.

---

## 0. The blocker to fix first (5 minutes)

**`list_compute` returns empty.** Credits in your Modal account are not the same thing as
Modal being connected to this session. Both are needed.

```bash
pip install modal
modal token new          # opens a browser, writes ~/.modal.toml
modal profile current    # confirm the workspace with the credits
```

Then **Customize → Compute → add Modal** in the sidebar. After that `list_compute` returns
it and jobs can be dispatched from a conversation.

Validate the plan with no account at all — this works right now:

```bash
python src/modal_app.py --dry-run --manifest data/manifests/manifest_prospective.csv
```

---

## 1. Start the reference build immediately — it is the critical path

Nothing else can run until this finishes, and **it is the longest single step of the day.**

```bash
modal run src/modal_app.py::build_reference --scope genome
```

- 8 CPU, 32 GB, 6-hour timeout. `hisat2-build` on GRCh38 realistically takes **1–2.5 hours**.
- It writes into a **shared read-only Volume** (`te-refs`). Built **once**; every later
  container mounts it. That is the whole architectural argument for Modal in one command.
- **Launch it and walk away.** Do not sit and watch. Go rehearse the talk — §4 of
  `TOMORROW.md` — because nothing in the presentation depends on this finishing.

**If it fails:** the most likely causes are the image build (bioconda resolution) and the
genome download. Re-run; `hisat2-build` restarts cleanly. If it fails twice, fall back to
`--scope chr_subset`, which is far quicker and still lets you demonstrate the fan-out
architecture on real data.

---

## 2. Calibrate cost on 4 libraries before launching 23

Credits are finite and you are alone. **Run the smallest real job first, look at the
dashboard, then decide.**

```bash
modal run src/modal_app.py --manifest data/manifests/manifest_prospective.csv --reads 30000000
```

Four libraries: DNMT3B knockdown ×2 and matched HepG2 CRISPR control ×2. This is the
**pre-registered prospective test** — the prediction is written down in
`PREREGISTRATION.md` and the data has never been opened.

When it finishes, read the Modal dashboard for actual cost and wall-clock per library, then
multiply. Only then decide whether to launch the larger runs.

**Why `--reads 30000000` and not `--reads 0`:** 30 M reads genome-wide is already **20×
more reads across 12× more genome** than everything measured so far (1.5 M reads on
chr1+chr19). Full depth on a 258 M-read library costs roughly eight times as much for a
marginal gain in a compartment-level statistic. Go to `--reads 0` only on DNMT1, and only
if credits are clearly sufficient.

---

## 3. Read the prospective result in the right order

**This ordering is load-bearing. Do not skip to the TE numbers.**

1. **Did the knockdown work?** Check DNMT3B's own counts dropped in the KD arm.
   A CRISPR that failed produces a perfect null that is *indistinguishable* from a
   refutation. If DNMT3B did not drop, **the test is void, not negative** — say exactly
   that and move on.
2. Only then open `results_prospective/setlevel_tests.csv`.
3. Apply §4 of `PREREGISTRATION.md`, which fixed the interpretation of every outcome in
   advance — including the row committing to retract if the sign flips.

**State the confound before the result, every time:** the prediction is grounded in K562 and
the only ENCODE DNMT3B knockdown is HepG2, so this tests R2 writer-transfer *and*
cross-cell-type generalisation simultaneously. A failure cannot distinguish them. That
limitation is in the pre-registration because it was known before the data was opened.

---

## 4. The finding that should change your ask

Computed today against `encode_kd_inventory.csv` (1,114 experiments, 570 target genes):

**Of the 40 chromatin-mark writers and erasers in the graph, exactly three have an ENCODE
knockdown.**

| Enzyme | Mark | Cell | Status |
|---|---|---|---|
| SETDB1 | H3K9me3 | K562 | already measured — grounds H3K9me3 |
| DNMT1 | 5mC | K562 | already measured — grounds 5mC |
| **DNMT3B** | 5mC | HepG2 | **today's run — the last one available** |

No SUV39H1, no SUV39H2, no KDM4A–E, no EZH2, no TET1/2/3, no DNMT3A. `ROBUSTNESS.md` §19.4
concluded that the highest-value next experiment is *more writers and erasers of the same
two marks*. **ENCODE is exhausted after DNMT3B.**

That is not a disappointment, it is a result, and it sharpens the pitch:

> Our robustness analysis told us exactly what to measure next — another writer or eraser
> of the same mark, because those are the only experiments that add an inference anchor. We
> then found that ENCODE contains exactly one we had not used, and we ran it today. Going
> further means leaving ENCODE for GEO and SRA, and that is a data-acquisition problem, not
> a compute problem.

**It also tells you what to do after the hackathon:** find SUV39H1/H2, EZH2 or TET2
knockdown RNA-seq in GEO/SRA. Each one is a new independent anchor, and §19 shows what a
second H3K9me3 anchor would be worth — SETDB1 currently carries 3 of the 4 `MARK_AT` edges
alone.

---

## 5. If credits allow, the two runs worth adding

### 5.1 Genome-wide re-run of the three existing contrasts (11 libraries)

```bash
modal run src/modal_app.py --manifest data/manifests/manifest_core.csv --reads 30000000
```

**Why it is the highest scientific value on the list.** The 5mC anchor — the single point of
failure for the entire DNMT3A/TET2 story — currently rests on one contrast at 1.5 M reads
across two chromosomes, one of which (chr19) is the most gene-dense, most Alu-rich chromosome
in the genome and carries the KRAB-zinc-finger clusters. Genome-wide at 30 M reads removes
both objections at once.

**And it retires the panel.** Every coverage guard exists because the reference held two
chromosomes. Genome-wide, GO:0006954's 725 members are all present by construction, the
0.535 coverage refusal disappears, and the interferon arm can be scored without the panel
workaround at all.

### 5.2 Two contrasts that are not anchors but are worth having (8 libraries)

```bash
modal run src/modal_app.py --manifest data/manifests/manifest_anchor_expansion.csv --reads 30000000
```

Built today, validated by dry run. **Neither adds an R1 anchor** — neither is a mark enzyme,
so both hit the same wall TRIM28 does. What they add is measured edges, and one of them is
pointed:

- **MORC2** (K562, ENCSR990DKW vs ENCSR978MMZ). MORC2 is the HUSH-associated chromatin
  remodeller. **Your own *GeroScience* paper found HUSH-mediated silencing enriched in the
  RTE-high DNMT3A clones**, read as a compensatory response — so this is the one contrast
  that connects today's compute directly to your published finding.
- **SUZ12** (K562, ENCSR682DZY vs ENCSR516TLX). PRC2 core component, so it reaches the
  H3K27me3 arm of the graph — which has 11 curated mark enzymes and **zero** measurements.

Run these only after §5.1, and only if the dashboard says you can afford them.

---

## 6. What to do while jobs run

Do not watch the dashboard. In order:

1. **Rehearse.** `DEMO_5MIN.md` for the script, `PRESENTATION_GUIDE.md` for what to say per
   slide, `JURY_QUESTIONS.md` for the 44 questions.
2. **Open the deck once** and check it renders on the machine you will present from:
   `open demo/presentation.html` — arrows navigate, `f` fullscreen, `s` hides notes.
3. **Run the local demo once** so the command is in your shell history:
   `make query GENE=TET2`
4. **Run `make validate`** — 42 structural metrics, and it names the one defect the audit
   found, which is a good thing to have said before anyone else finds it.

---

## 7. Failure table

| Symptom | Do this |
|---|---|
| `list_compute` empty after adding Modal | Re-check Customize → Compute; confirm `modal profile current` is the workspace with credits |
| Image build fails on bioconda | Re-run once. Conda resolution is flaky, not broken |
| `build_reference` times out | Re-run; or fall back to `--scope chr_subset` and demo the architecture instead of the scale |
| A library fails mid-run | `retries=2` is already set. One dead library out of 23 is not a problem — the manifest is independent per row |
| Everything is too slow | Drop to `--reads 5000000`. A compartment-level shift is still visible |
| Out of credits mid-run | Stop. You already have a complete talk. Present what finished and say what is still running |
| Results look wrong | **Check the knockdown efficiency first** (§3). Then check you are reading the right reference scope |

---

## 8. The honest framing for the talk

If the runs finish, you have a genuine agentic-science beat: *the robustness analysis
identified what to measure, the pre-registration fixed the interpretation before the data
was opened, and the computation ran on Modal during the event.*

If they do not finish, the beat is still there — you identified the experiment, committed to
the interpretation in advance, and dispatched it. **Naming the right next experiment is the
scarcer skill**, and the pre-registration is the artefact that proves you did it before
seeing the answer.

Either way, do not claim a result you have not read, and do not read a TE number before the
knockdown-efficiency check.
