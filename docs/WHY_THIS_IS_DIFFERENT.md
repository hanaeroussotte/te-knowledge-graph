# Why this is different

**Written for someone with no background.** It explains what the thing actually is, what
already existed before it, and precisely which part is new — after a deliberate attempt to
prove that none of it is (`PRIOR_ART.md`). If you can only remember one sentence, remember
the one in §7.

---

## 1. First, what problem are we in?

Your genome is about 3.1 billion letters. Only ~2% of it is genes. A large part of the rest
is **transposable elements** — ancient viruses and molecular parasites that copied
themselves into our ancestors' chromosomes and stayed. There are about 3.8 million copies,
in roughly a thousand different varieties.

Cells switch them off with chemical marks. When the switching-off machinery breaks, some of
them switch back on, and the cell's antiviral alarm mistakes their RNA for an infection. You
get inflammation with no pathogen. This is suspected to matter in ageing, in blood cancers
and in autoimmune disease.

So the scientific question is: **which genes control which transposable elements, and what
happens downstream when they fail?**

## 2. What already existed

This is the part most "novel tool" pitches skip, and it is the part a reviewer will attack
first. Four things already existed, and all four are good.

**(a) Tools that measure transposable-element expression.** The hard technical problem is
that a million Alu copies look nearly identical, so when you sequence RNA you cannot tell
which copy a fragment came from. **TEtranscripts** (2015) solved this by splitting each
ambiguous read fractionally across its candidate sources. Others followed — Telescope,
SQuIRE, SalmonTE, TEspeX, MATES, and in 2026 MAJEC. **We use TEtranscripts. We did not
invent any of this**, and saying otherwise to anyone in the field would end the
conversation.

**(b) Experiments that hunt for TE regulators.** Researchers have been systematically
switching genes off and looking for transposon activation since at least 2003 in worms,
2013 in flies, and 2018 in human cells. Any claim that nobody has done this is simply
false.

**(c) Biological knowledge graphs.** Databases shaped like networks — PrimeKG, Hetionet,
Open Targets — that hold genes, diseases, drugs and the relationships between them, so you
can ask questions that traverse several steps.

**(d) Machine learning that predicts perturbation outcomes.** **TxPert** (2026) uses
knowledge graphs to predict what happens to gene expression when you perturb a gene, and
does it well.

## 3. So what is actually missing?

Three gaps, and they interlock.

**Gap 1 — the measuring tools and the reasoning tools have never met.** The TE
quantification tools produce a table of numbers. The knowledge graphs hold biological
relationships. Nothing carries a *measurement* into a *graph* in a form you can reason
over. The output of (a) never becomes an input to (c).

**Gap 2 — the graphs have no vocabulary for the thing.** PrimeKG, Hetionet and Open Targets
have no node type for a transposable element. "SETDB1 silences HERVK" is not a statement
that is false in those graphs; it is a statement they cannot express. So even if you had
the measurement, there is nowhere to put it.

**Gap 3 — the experiments that could answer this were already run, for other reasons.**
ENCODE contains 1,114 human knockdown RNA-seq experiments across 570 genes. Almost none
were designed to study transposable elements. The reads are sitting there. The TE signal
was in the data all along and nobody counted it, because counting it requires (a) and
because it was not the question being asked.

## 4. What this project does

It connects the four existing things and fills the three gaps.

```
  existing perturbation experiments (ENCODE, 570 genes)
        │   ← nobody measured TEs in these
        ▼
  re-quantify with TEtranscripts, keeping multi-mapping reads
        │   ← established tool, credited
        ▼
  two statistics: per-TE-family, and TE compartment vs protein-coding genes
        │
        ▼
  signed relationships with full provenance
  "TRIM28 loss raises AluY, log2FC +0.79, padj 0.0005, K562, CRISPRi, RNA-seq"
        │
        ▼
  a knowledge graph that HAS a TE node type
        │   ← the missing vocabulary
        ▼
  mechanistic rules that generate hypotheses about genes never tested
        │
        ▼
  an answer with a printed proof tree, or an explicit refusal
```

## 5. The three things that make it different in practice

### 5.1 Measurement becomes a first-class graph citizen

Most knowledge graphs are assembled from what humans curated into databases. Ours has a
layer that is **our own measurement from raw sequencing reads**, tagged as such, sitting
beside the curated layer and outranking it. When the engine answers a question, you can see
which part of the answer is somebody's published assertion and which part is a number we
computed, and the difference is machine-readable, not a footnote.

### 5.2 It answers about genes that have never been tested — and shows its work

Ask most systems about `TET2` and transposable elements and you get nothing: TET2 has no TE
annotation in Gene Ontology and no knockdown experiment in ENCODE. Ask a language model and
you get a fluent paragraph you cannot check.

This system derives an answer from a stated rule and prints the derivation:

```
TET2 is predicted to DEREPRESS transposable elements globally.   [inferred, R3]
├── TET2 removes the 5mC mark                    [curated: GO:0070579]
└── 5mC represses transposable elements          [inferred, R1]
    ├── DNMT1 writes the 5mC mark                [curated: GO:0003886]
    └── DNMT1 loss raised the TE compartment     [MEASURED, p = 1.6e-08]
```

Three facts, one of them ours, and you can attack any line of it. That is the difference
between a prediction and an assertion. **These are mechanistic hypotheses, not causal
deductions** — the vocabulary matters, and printing the tree is what makes the weaker word
safe.

### 5.3 It is built to say "we cannot know this yet"

This is the part that is genuinely unusual, and the part worth leading with.

We wanted to know whether transposable-element reactivation triggers an interferon
response. First attempt: only 17% of the relevant genes were inside the reference we were
using, so the measurement would have described our chromosome selection rather than the
biology. The code **refused to report it** — a coverage threshold, enforced in software,
not a caveat in prose.

Then we fixed the coverage problem properly, getting it to 77%. The answer came back: no
interferon response. And rather than publish that, we checked whether the cell line can
even mount one — and found the sensors are not expressed. `CGAS` sits at 0.21 counts per
million; the machinery downstream of it is 1000× higher. The pathway has no entry point.

So the finding is not "TE activation does not cause inflammation". It is:

> This dataset cannot test the question, and here is the specific experiment that could.

Three components were built, measured, and **deliberately not shipped**: a rule-based
literature extractor (precision 0.109 — no better than chance), a link-prediction model
(no way to validate it with three knockdowns), and that interferon result. The code for all
three is in the repository. The measurements that condemned them are in the repository.

## 6. What this is *not*

Stating this plainly is what makes the rest credible.

- **Not a new way to measure transposable elements.** That is TEtranscripts, credited.
- **Not the first systematic search for TE regulators.** Screens have done that since 2003.
- **Not a new statistical test.** Comparing one feature set's fold changes against all
  others is competitive gene-set testing, and it is decades old.
- **Not a validated atlas.** Three knockdowns, one cell line, 10% of the genome, shallow
  depth. It is an architecture with a worked example, not a resource.
- **Not safe from competition.** Anyone who puts a TE-aware expression matrix into TxPert
  has a strong competitor. That gap is closable. It is simply not closed today.

## 7. The claim that survives

> **An evidence-traceable perturbational reasoning system for transposable-element
> regulation.**
>
> It re-analyses perturbation experiments for effects on the repetitive genome, converts
> those measurements into signed and provenance-tracked biological relationships, connects
> them to known mechanisms, and generates testable hypotheses whose evidence paths can be
> inspected and falsified.

Every clause is doing work. *Re-analyses* — the experiments already exist. *Repetitive
genome* — the part they did not measure. *Signed and provenance-tracked* — direction plus
where it came from. *Connects to known mechanisms* — the rules. *Inspected and falsified* —
the proof tree, and the refusals.

## 8. Why this is interesting beyond the biology

There is a version of AI-for-science that produces plausible hypotheses on demand. That is
not hard any more, and it is not obviously useful, because the bottleneck in science was
never a shortage of plausible hypotheses.

The harder and more valuable question is: **can a system tell when the available evidence
is insufficient to answer, and say so?**

This project has that behaviour encoded in several places, not as good intentions but as
code and as decisions that cost us results:

- a coverage guard that refuses to interpret a gene set the reference cannot see;
- a citation gate that discards any sentence without a resolvable evidence id;
- an evidence tier on every edge, with multi-step conclusions inheriting the *weakest* link
  rather than an average;
- three finished components withheld on the basis of their own measured performance;
- a headline biological question answered with "this system cannot test it, run this
  instead".

The useful framing of the AI's role is not *"tell me whether TET2 activates transposable
elements."* It is: *determine what evidence exists, distinguish measurement from inference,
identify what is missing, run the computation that would settle it, inspect the result, and
return a claim whose derivation someone else can audit* — with permission to conclude that
the answer is not yet knowable, and to name the experiment that would make it knowable.

## 9. Where it goes

The long-term object is not the DNMT3A/TET2 question — that is one worked example. It is a
**perturbational TE atlas**: what happens to the repetitive genome across hundreds of
perturbations that were run for entirely different reasons.

The rule engine is best understood as a **bootstrap**. It generates testable hypotheses
while the measured matrix is too small for machine learning. Once the atlas is large
enough to hold out a validation set, a TE-specific TxPert- or GEARS-style model becomes
feasible, and rules and learned prediction should coexist — rules for the mechanistic,
auditable path; learning for coverage. Arguing that symbolic reasoning will permanently
beat learning would be a weaker position and an unnecessary one.

The end state is a system that answers not only *what do we know* but **which computation
would most reduce our uncertainty** — if five methyltransferases are predicted to regulate
the same TE programme, you do not test all five, you test the one that best discriminates
between the competing explanations. That turns a knowledge graph into an experimental-design
engine, which is a considerably more valuable object than a database.
