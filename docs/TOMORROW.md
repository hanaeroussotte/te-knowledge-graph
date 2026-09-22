# Tomorrow: what to actually do

**Written for someone who has not done this before.** Every command is copy-pasteable,
every step says what "working" looks like, and every step says what to do when it doesn't.
Nothing here assumes you remember anything from the build.

**The mindset for the day.** You are not trying to finish the science — the science is
finished and committed. You are trying to (a) not break anything, (b) run one new
computation on the cloud, and (c) explain it well. In that order of importance, and the
third one matters most.

> **If everything goes wrong and nothing runs:** you still have a complete repository, a
> 12-slide deck, a working local demo, and the strongest slide in the talk (the hold-out
> robustness result) already computed and saved. **You can give the entire presentation with
> no compute at all.** Read that sentence again before you start worrying about anything.

---

## Part 0 — Tonight, 10 minutes

Two things only, both administrative, both things I could not do for you.

### 0.1 Add a LICENSE

Without one, default copyright applies and nobody can legally reuse your code — which is
awkward if a judge asks "can we look at this?".

On GitHub: go to your repo → **Add file** → **Create new file** → type `LICENSE` as the
filename → a **"Choose a license template"** button appears on the right → pick **MIT**
(simplest: anyone can use it, you keep credit, no warranty) → Commit.

*If you'd rather be more protective, Apache-2.0 adds an explicit patent grant. MIT is the
common default for research code.*

### 0.2 Decide on repo visibility

The repo is **private**. If the URL goes on a slide, or a judge wants to look, it needs to
be **public**.

Settings → General → scroll to **Danger Zone** → Change visibility → Public.

**This is not reversible in spirit** — once public, assume someone has a copy. Everything
in there is defensible (that was the point of the last several days), so this is a
decision, not a risk. If you're unsure, leave it private and offer to add a judge as a
collaborator instead.

### 0.3 Sleep. Genuinely.

The talk matters more than one more commit.

---

## Part 1 — First 20 minutes on the day: prove it still works

Before anything exciting, check the machine you're on can run what you built. Do this
first, always, because finding out at minute 90 is much worse.

### Step 1.1 — Get the code

```bash
git clone https://github.com/hanaeroussotte/te-knowledge-graph.git
cd te-knowledge-graph
```

**Working looks like:** a folder with `src/`, `docs/`, `tests/`, `Makefile`.

**If it asks for a password:** the repo is still private and you're not signed in. Either
make it public (0.2) or use a personal access token as the password.

### Step 1.2 — Set up the environment

```bash
conda env create -f environment.yml
conda activate te-pipeline
pip install -r requirements.txt
```

**Working looks like:** the prompt changes to show `(te-pipeline)`.

**If conda isn't installed:** install Miniconda first, or skip to Step 1.4 — the demo and
the deck need nothing but a browser.

**What this is doing, in plain terms.** An "environment" is a private box of software
versions, so this project's tools can't conflict with anything else on the machine. Think
of it as a separate toolbox rather than throwing everything in one drawer.

### Step 1.3 — Run the gate

```bash
make gate
```

This is the most useful single command in the repository. It checks seven things: the graph
re-derives, no retracted claim is asserted anywhere, **every citation resolves against
Crossref and PubMed**, the reasoning conclusions are unchanged, the figures rebuild from
the saved tables, every script parses, and then it prints the diff for you to read.

**Working looks like:** `GATE PASSED` at the end, with `AUDIT PASS`, `CITATIONS PASS` and
`PASS — proof trees … unchanged` above it.

**If citations fail:** almost certainly the venue wifi. It retries automatically; run it
again. A genuine failure names the specific DOI or PMID.

**If the regression fails:** *read the diff, do not "fix" it.* It prints exactly which
conclusion changed. If you didn't change any code, something is wrong with the checkout,
not with the science.

### Step 1.4 — Check the two things you'll actually show

```bash
open demo/presentation.html      # macOS;  on Linux: xdg-open
open demo/demo.html
```

**Working looks like:** the deck opens, arrow keys move between 12 slides, `f` goes
fullscreen, `s` hides the speaker notes.

**Do this now**, not at minute 200. A browser that won't open your deck is a five-minute
problem at 9am and a catastrophe at 5pm.

### Step 1.5 — Ask the engine something

```bash
make query GENE=TET2
```

**Working looks like:** a proof tree, with a line beginning `!` warning that the prediction
is grounded in K562.

**You have now verified everything you need for the talk.** Anything after this is upside.

---

## Part 2 — Connect Modal (30 minutes, do it early)

Modal is the cloud-compute service. You get credits on the day. The reason to do this early
is that account setup can go wrong and you want that discovered at hour one.

### Step 2.1 — Install and authenticate

```bash
pip install modal
modal token new
```

That opens a browser to sign in and writes a token to your machine.

**Working looks like:** `Token written to ~/.modal.toml`.

### Step 2.2 — Also add it to Claude Science

In the sidebar: **Customize → Compute → Add**. This lets me dispatch jobs for you rather
than you running them by hand.

**Say so when it's done** and I'll re-check — I've been checking all along and it's been
empty.

### Step 2.3 — Dry-run before spending anything

```bash
python src/modal_app.py --dry-run --manifest data/manifests/manifest_prospective.csv
```

**Working looks like:** a printed plan — 4 libraries, the image contents, 8 CPU / 32 GB for
the reference build, 4 CPU / 16 GB per worker, **no GPU**, and the four sample names.

**Why this step exists:** it validates the plan and the manifest *without* touching your
credits. A typo in a manifest discovered here costs nothing; discovered after dispatch it
costs credits and twenty minutes.

---

## Part 3 — The one new computation (2–4 hours, mostly waiting)

This is the prospective test. **Read `docs/PREREGISTRATION.md` before you run it** — it
contains the prediction and, more importantly, what each possible outcome means. That
document exists so the interpretation cannot be renegotiated once the numbers appear.

### What you are testing, in one paragraph

The engine predicts that **losing DNMT3B raises TE expression**. It got there by a rule
called R2, which transfers a measured effect from one writer of a chemical mark to another
writer of the same mark. That rule is the shakiest thing in the engine, because DNMT1 (which
we measured) *maintains* methylation while DNMT3B *establishes* it — like inferring
something about a builder from what you observed about a maintenance crew. ENCODE has a
DNMT3B knockdown with 258 million reads that this project has never opened. So: prediction
first, then look.

### Step 3.1 — Build the reference on Modal (~40 min, once)

```bash
modal run src/modal_app.py --build-reference-only --ref-scope genome
```

This downloads the human genome and builds a search index into a shared cloud volume. It
happens **once** and every worker then mounts it read-only — which is the whole reason this
shape suits cloud compute.

**Working looks like:** a list of files in `/refs` at the end.

**If it fails:** you can still do everything else. Skip to Part 4.

### Step 3.2 — Run the four libraries

```bash
modal run src/modal_app.py --manifest data/manifests/manifest_prospective.csv --reads 0
```

`--reads 0` means full depth. If you're short on time or credits, use `--reads 5000000`
(5 million reads per library) — faster, noisier, and enough to see a compartment-level
shift.

**Working looks like:** `4/4 libraries quantified`.

### Step 3.3 — Turn counts into an answer

```bash
python src/te_pipeline.py merge --outdir results_prospective
python src/run_de.py --counts results_prospective/counts_matrix.tsv \
    --manifest data/manifests/manifest_prospective.csv --outdir results_prospective
```

### Step 3.4 — Read it in the right order. This part matters.

**First, the gate — before you look at any TE number:**

```bash
python -c "
import pandas as pd
d = pd.read_csv('results_prospective/deseq2_results.csv', index_col=0)
print(d[d.index.str.contains('DNMT3B', na=False)][['log2FoldChange','padj','baseMean']])
"
```

You are checking that **DNMT3B itself went down** in the knockdown arm. If the CRISPR didn't
work, you get a perfect null that looks *exactly* like a refutation. A negative log₂FC here
means the knockdown worked and you may proceed. If it's near zero, **the test is void, not
negative** — say that and stop.

**Then the actual result:**

```bash
cat results_prospective/setlevel_tests.csv
```

Read `median_log2FC_TE` against `median_log2FC_gene`, and the `mannwhitney_p`.

**Then apply §4 of the pre-registration, which decides for you:**

| What you see | What it means |
|---|---|
| TE median clearly above gene median, p < 0.01 | **Prediction confirmed** across cell types — a stronger result than a same-cell-type confirmation would have been |
| Same direction, p between 0.01 and 0.1 | Consistent but underpowered. "Weak support", not a win |
| No difference | R2 or cross-cell-type transfer fails here. **Record it, don't bury it** |
| TE median *below* gene median | The most interesting outcome: the rule's *sign* is wrong, and R2 should be restricted or removed |

**Every one of those four is a good outcome for the talk.** A refutation of your own rule,
pre-registered and reported, is a better story than a confirmation — because anyone can
show a confirmation, and almost nobody shows the other thing.

---

## Part 4 — The talk

### 4.1 Read these two, in this order

1. `docs/DEMO_5MIN.md` — the timed script, four beats, 4:40.
2. `docs/PRESENTATION_GUIDE.md` — every slide explained, with the number you must be able
   to defend and the four questions you will definitely be asked.

### 4.2 The three things to have completely fluent

**(1) The DNMT1 story.** Nothing clears FDR; the compartment test gives p = 1.6 × 10⁻⁸.
*Why that isn't cheating:* size factors are per-sample, so a normalisation error shifts TE
and gene fold-changes by the same amount and cancels in the difference between their
medians. A normalisation artefact cannot manufacture a gap between two feature sets measured
in the same libraries. The test itself is standard; what's ours is using it as the *primary*
TE readout for that reason.

**(2) The hold-out.** Remove SETDB1 and the inference layer collapses 89 → 8. Say it
yourself, early. It converts your biggest weakness into your strongest demonstration of
rigour, and it makes the ask specific: more writers and erasers of the same two marks, not
"more data".

**(3) cGAS at 0.21 CPM.** The interferon answer is null, and the sensors aren't expressed —
so the honest claim is "this dataset cannot test viral mimicry", not "TEs don't cause
inflammation".

### 4.3 Never say

Check `docs/CLAIMS.md` §0. The four most tempting errors: *"no knowledge graph has TEs"*,
*"nobody has looked for TE regulators"*, *"our quantification method"* (it's TEtranscripts
— credit it), and *"the TE atlas"*.

---

## Part 5 — If something breaks

| Symptom | Do this |
|---|---|
| `make gate` fails on citations | Wifi. Run it again; it retries. A real failure names the DOI |
| `make gate` fails on regression | **Read the diff.** It names the changed conclusion. Don't edit code to make it pass |
| Modal won't authenticate | Skip Part 3 entirely. The talk doesn't need it |
| `make query` errors about missing edge files | You're in the wrong directory. `cd` to the repo root |
| A figure won't display in the deck | The images are embedded as base64 inside the HTML — if the deck opens at all, they're there |
| Conda environment won't build | The deck and demo need only a browser. Present from those |
| You're asked something you don't know | **"We haven't measured that. The experiment that would settle it is ___."** This is the correct answer and it is the best thing you can say all day |

---

## The single-page cheat sheet

```bash
# verify everything (do this first)
make gate

# ask the engine about any gene
make query GENE=TET2

# open the talk
open demo/presentation.html

# validate the cloud plan without spending credits
python src/modal_app.py --dry-run --manifest data/manifests/manifest_prospective.csv

# run the prospective test
modal run src/modal_app.py --manifest data/manifests/manifest_prospective.csv --reads 0
```

**Numbers to know cold:** 3.8 M TE copies · 1,057 subfamilies · 1,114 ENCODE knockdowns ·
9,366 edges · 89 derived predictions · **89 → 8 without SETDB1** · TRIM28 +0.41 at
p = 3.5 × 10⁻¹⁵ · DNMT1 p = 1.6 × 10⁻⁸ with nothing at FDR < 0.1 · interferon coverage
17% → 77% · cGAS 0.21 CPM · 28 structurally tractable targets with no clinical programme.

**And the one sentence:**

> An evidence-traceable neurosymbolic reasoning system for transposable-element regulation:
> it re-analyses perturbation experiments for effects on the repetitive genome, converts
> those measurements into signed, provenance-tracked relationships, connects them to known
> mechanisms, and generates testable hypotheses whose evidence paths can be inspected and
> falsified — and tells you when the evidence isn't enough.

Good luck. The work is done; tomorrow is about explaining it.
