# Questions you will be asked, and the answers

Forty-one questions, from the external review of 2026-09-22 plus the four already in
`PRESENTATION_GUIDE.md`. Every answer here is grounded in a number this repository can
produce, or it says plainly that there isn't one.

**Three rules for answering anything.**

1. **The honest answer is always shorter than the defensive one.** "No, that's prior art,
   we cite it" takes four seconds and ends the attack. A hedge invites three follow-ups.
2. **Never guess a number.** "I'd have to check" is a completely acceptable answer from a
   scientist and a fatal one from a bluffer. The numbers worth memorising are in
   `TOMORROW.md`'s cheat sheet.
3. **If you don't know, say what would settle it.** Every gap in this project has a named
   next experiment. Reaching for it turns a weakness into a plan.

---

## A. "Isn't this just …?" — the attribution questions

**1. Isn't this TEtranscripts plus Claude?**
No. TEtranscripts is one measurement component and we credit it explicitly. The system adds
perturbation re-analysis, a provenance-bearing evidence schema, mechanistic reasoning with
inspectable derivations, and evidence tiers. TEcount produces the counts; it does not
produce a signed edge with a citation and a proof.

**2. Did you invent TE quantification?**
No. TEtranscripts, Jin et al. 2015. There are at least 16 tools — She et al. benchmarked
them in 2026.

**3. Why TEcount specifically?**
Mature, validated, joint gene/TE quantification at the resolution the inference layer uses.
Not a claim of superiority.

**4. Why not Telescope or SQuIRE?**
Both are locus-resolution methods. The graph reasons at subfamily level, so locus
quantification would be resolution we cannot currently consume. When `TELocus` exists as a
node type, they become the right tools.

**5. Why not MAJEC?**
It is the most interesting recent challenge and it targets a failure mode we have not
addressed — gene-overlap contamination. It reports r = 0.987 subfamily-level concordance
with TEtranscripts, which is why the subfamily conclusions are not expected to be
quantifier-dependent. The head-to-head is specified and pre-registered in
`QUANTIFIER_ROBUSTNESS.md`, including a retract-if-sign-flips row, and deliberately not yet
run. Rushing it would produce a number I could not defend.

**6. Have you read the 16-tool benchmark?**
She J, Wang J, Yang E., *Genomics Proteomics Bioinformatics* 2026, 10.1093/gpbjnl/qzag044.
If you have not read it before the pitch, say so honestly and say it is on the list.

**7. Are there already TE databases and atlases?**
Yes, and large ones — TE-SCALE (1.3 M cells, 330 samples, 20 cancer types), TEITbase
(33 cancer types), REdiscoverTE across TCGA, ERVmap. They answer **where TEs are active**.
This answers **what perturbation changed them**. Different axis; neither substitutes for the
other.

**8. Are there already TE networks or graphs?**
Yes. TEKRABber builds TE–KRAB-ZFP networks; PlaNC-TE is a plant ncRNA–TE knowledgebase;
ICEO makes bacterial mobile elements first-class ontology entities. Never claim the first
TE graph.

**9. What's wrong with PrimeKG?**
Nothing. Its schema was designed for different questions — 10 node types covering
gene/protein, disease, drug, pathway, anatomy, GO, phenotype, exposure. It has no TE node
type, so TE regulatory statements cannot be expressed in it directly. That is a scope
difference, not a defect.

**10. What about ROME Therapeutics?**
The closest industrial precedent, and they were ahead on biology — they solved the LINE-1
ORF2p structure (*Nature* 2024) and built reverse-transcriptase inhibitors. What I have not
found in their public work is this architecture: public perturbation data re-analysed
against the repeat genome into a common evidence schema with inspectable reasoning. Say it
with respect.

**11. Didn't ROME shut down? Doesn't that tell you something?**
A company winding down does not establish that the science failed. Reported to continue
under Pretzel Therapeutics — I have not independently verified the corporate detail.

**12. Why not GEARS or TxPert?**
Their output space is conventional gene expression; TEs are not the predicted variable, and
they do not emit a derivation you can inspect. But the gap is closable, not closed: TxPert
on a TE-aware count matrix would be a strong competitor, and at scale that is a logical next
phase rather than a rival. The rule engine is a bootstrap for the low-data regime.

---

## B. Resolution and quantification

**13. Why subfamilies and not loci?**
Measured, not assumed. Aggregating *upward* destroys signal — AluY is significant at
padj 0.0005 while pooled `Alu:SINE` gives +0.616, not significant; SETDB1 goes from 2 hits
to 0 and TRIM28 from 4 to 1. Subfamily was the level at which signal survived at this depth.
The field is moving down to loci and the ontology is already split to permit
`TEClass → TEFamily → TESubfamily → TELocus → TETranscript`. Those last two are roadmap, not
built.

**14. Isn't the locus the real biological unit?**
Often, yes — copies in one subfamily differ. The ontology should support both levels, with
evidence attached wherever the experiment supports it.

**15. How reliable are multi-mapping reads?**
They create uncertainty, not impossibility. Probabilistic allocation is established
methodology. The honest limitation is method-dependence, which is why the quantifier
benchmark is pre-registered.

**16. What happens to reads mapping more than 100 places?**
`-k 100` is a practical truncation and reads above it are under-represented. It is a stated
limitation, not a solved problem.

**17. Could host-gene transcription masquerade as TE transcription?**
Yes, and this is the sharpest technical criticism available. Joint models such as MAJEC
exist specifically to address it, reporting exon-overlap contamination reduced from over 40%
to roughly 5%. We have not run it.

**18. Why only chr1 and chr19, and 1.5 M reads?**
Because this is pipeline validation, not final quantification, and the documentation says so
throughout. Alignment rates of 17–20% are exactly what a two-chromosome index predicts. The
genome-wide full-depth run is the named next step and the reason Modal is in the architecture.

---

## C. The biology, and what it does not mean

**19. Does TE RNA mean retrotransposition?** No.

**20. Does TE RNA mean dsRNA?** No.

**21. Does TE RNA mean inflammation?** No. Each arrow in
TE RNA → dsRNA → cDNA → sensor activation → interferon → phenotype needs its own
measurement. `CRITIQUE.md` carries the full caveat chain.

**22. Then why model viral mimicry at all?**
As a downstream hypothesis requiring independent sensing evidence — which is why R6 exists
and why it fires **zero** times. R6 demands TE derepression *and* inflammation induction in
the same contrast. It has never once been satisfied.

**23. Why didn't K562 show an interferon response?**
Because the pathway's entry points are not expressed. CGAS 0.21 CPM, ZBP1 0.26, NLRP3 0.20,
TLR3 0.00 — against TYK2 799, MAVS 586, IRF3 317, STING1 270. The transducers are present
and the sensors are absent. The correct conclusion is that **this dataset cannot test viral
mimicry**, not that viral mimicry did not occur.

**24. Isn't SETDB1 already known to silence TEs?**
Completely. It is a positive control. If it had not come out, the pipeline would be broken.

**25. Same for TRIM28?**
Yes. Same reason.

**26. So what did you actually discover biologically?**
Nothing about SETDB1 or TRIM28 — those validate the pipeline. The measured result worth
having is DNMT1: no TE subfamily clears FDR 0.1, yet the whole TE compartment shifts
+0.117 against −0.014 for protein-coding genes, p = 1.6 × 10⁻⁸. A per-feature-only analysis
would have reported "no effect". And the honest answer to the question as asked is that this
build validates an architecture and generates hypotheses; it is not yet a paper claiming a
novel regulator.

**27. Are the inferred edges causal?**
No. They are mechanistic hypotheses. The rules are candidate-generation rules; the tiers say
so and the proof tree shows exactly which step is inference.

**28. Why would two H3K9 methyltransferases behave the same way?**
They may not, and that is the honest limitation. A shared mark is candidate-generating
evidence, not proof — targeting matters. SETDB1 recruited via TRIM28 to one set of loci is
not equivalent to another H3K9 writer in a different chromatin context.

**29. Doesn't recruitment matter?**
Critically. And our own hold-out analysis demonstrates it from the other direction: TRIM28
has the largest measured effect in the dataset and contributes **zero** inferential value,
because a scaffold has no `DEPOSITS_MARK` edge and cannot satisfy R1.

**30. Doesn't cell type matter?**
Critically. Hyacinthe & Bourque report 456 cell-type–histone–TE triplets. Every edge here
carries a context tuple for that reason, and derived edges inherit it — agreement inherits,
disagreement becomes `mixed(a|b)`, and any specific experimental context sets
`context_generalization_required=yes`.

**31. Why K562?**
Matched perturbation data and known positive controls. Not intended as a universal context —
and the interferon result is the clearest demonstration that it isn't one.

---

## D. Scope, rigour and what would break it

**32. Three genes?**
Enough to demonstrate the workflow end to end; nowhere near enough for learned prediction.
Stated in the README, the deck and here.

**33. Why no link prediction?**
Three knockdowns cannot support a held-out validation set. Shipping an unvalidated link
predictor would have been the single easiest way to make the demo look better and the
science worse.

**34. How much does the reasoning actually rest on?**
Less than it looks, and we measured it. Only **four** `MARK_AT` edges exist. H3K9me3 is
grounded solely by SETDB1, 5mC solely by DNMT1. Remove SETDB1 and derived edges collapse
from 89 to 8. Remove TRIM28 — the largest measured effect — and nothing changes at all.
**No hold-out ever flipped a direction**; genes either keep the prediction or return
`best_tier: none`.

**35. What would falsify the framework?**
Predictions failing repeatedly when measured; a quantifier change reversing a sign; the
prospective DNMT3B test coming back with TEs moving down. Each has a pre-registered
interpretation, written before the data was opened.

**36. What experiment would most strengthen it?**
Per §19.4 of the walkthrough: **more writers and erasers of the same two marks**, not more
scaffolds and not "more data". SUV39H1/H2 and the KDM4 family would add independent R1
groundings. That is a specific, ranked answer derived from the hold-out analysis, and it is
the best evidence that the robustness check was worth running.

**37. What's the single biggest weakness?**
Context. Three knockdowns, one cell type, reduced depth, partial-genome reference. TE
regulation is cell-type × locus × chromatin-state × developmental-state specific, and we
have one cell in one state.

**38. What's your moat?**
Today: the architecture and the workflow. At scale: a uniquely processed perturbational TE
dataset that does not currently exist. Do not claim the second one yet.

---

## E. The platforms

**39. Why Claude?**
Not for numerical ground truth. For deciding what evidence exists, distinguishing measured
from inferred, noticing what is missing, launching the computation that would fill it, and
returning an answer whose derivation survives inspection. The interesting capability is not
generating a hypothesis — it is knowing when the evidence is insufficient to have one.

**40. Why Modal?**
The workload shape fits: alignment and quantification are CPU/RAM-bound and embarrassingly
parallel across libraries; references are large and reusable, which is a shared Volume; the
reasoning layer is tiny and does not belong in the cloud at all. **No GPU is requested** —
claiming one would be theatre.

**41. Why not Nextflow or Snakemake on AWS or HPC?**
They could absolutely run this pipeline, and for a production genomics facility with a
stable Slurm stack they may be the better answer. Modal's advantage here is not capability,
it is that an agent can decide at runtime which computation is needed, acquire compute, fan
out, reuse a shared reference volume and shut down — without a human managing
infrastructure. For an AI-native exploratory system that is a real difference; for a stable
production pipeline it is not. Say both halves.

---

## F. The two questions worth wanting

**"What happens when the evidence isn't enough?"**
Then the system says so. Three results were withheld rather than shipped: a rule-based
literature extractor measured at 0.109 precision, link prediction with no validation set,
and an interferon conclusion drawn from a reference containing 17% of the signature. The
third was fixed properly — a panel reference took type-I interferon coverage to 77% — and
the answer was *still* a null, now with a mechanism attached. `best_tier: none` is a
supported output, not an error path.

**"What should we compute next?"**
The hold-out analysis answers this quantitatively rather than rhetorically: the marginal
value of another scaffold is zero and the marginal value of another writer or eraser of
H3K9me3 or 5mC is high, because only four edges currently ground the entire inference layer.
That is what turns a knowledge graph into an experimental-design tool, and it is the most
promising direction this project has.
