# Result, 2026-10-27

Plan hashed before any prediction; PLAN.sha256 verified immediately before the run. All 72 complexes
completed, no non-zero return codes, exactly one affinity file per complex. 12 of 12 pairs scored, so
the critical value and power figures in POWER_NOTE.md apply as written.

## Primary metric, binder probability: POSITIVE

| | value |
|---|---|
| pairs | 12 |
| mean share of decoys beaten | **0.8333** |
| one-sided p | **0.00024** |
| critical value (analyze.py's own null, 100,000 draws) | 0.653 |
| regulator ranked first | 7 of 12 |

Case 1 of the verdict rule in POWER_NOTE.md: at or above the critical value, report the share and the
p and stop. Power is not cited here because it governs nulls, not rejections. For the record it was
0.96 against a true share of 0.75, so this is not a marginal call that happened to land.

**Boltz-2 ranks the known regulator above its decoys well above chance.**

## The caveat that was declared in advance, and now matters most

From the README, written before any prediction: *"Most of these complexes have pre-2023 PDB structures,
so they are probably in Boltz-2's training data: this measures whether the model reproduces known
biology, not discovery."*

A positive result is exactly the case where that sentence does the most work. **This says the model has
learned these regulatory relationships, not that it can find new ones.** Single-chain inputs also miss
interface sites, and one diffusion sample per complex was used on CPU. None of this is a retraction;
all of it was fixed in writing beforehand, which is the only reason it can be stated plainly now.

## Subgroups: descriptive only, no significance claimed

| subgroup | mean share |
|---|---|
| phosphorylated decoys only | 1.000 |
| single-chain sites | 0.8704 |
| interface sites | 0.7222 |

Both splits were pre-registered as separate reports, and POWER_NOTE.md declared them
hypothesis-generating because they divide 12 pairs further. No p value is attached to either.

Two observations worth recording at that strength. The phosphorylated-decoy result answers the
question the README posed, **"does the model just reward phosphate charge?"**, in the negative: the
regulator beat every phosphorylated decoy in every pair. Most of these regulators are themselves
phosphorylated (AMP, ADP, GTP, CTP, ATP, NADP+, fructose-1,6-bisphosphate), so a model rewarding
phosphate alone would not separate them from phosphorylated decoys at all. And interface sites score
below single-chain sites, 0.72 against 0.87, which is the direction predicted in advance from the
pocket analysis, since single-chain inputs cannot form a subunit interface.

## Secondary metric: POSITIVE (resolved 2026-10-27)

analyze.py reports mean share 0.9167 at p = 0.0 on predicted affinity, but **that number does not yet
satisfy its own pre-registration.** Amendment 2026-10-26b requires a pair's affinity result to count
only where the regulator's lead exceeds 0.234, and analyze.py does not apply that threshold. Until the
gap rule is applied the secondary is unreported, not confirmed.

This is an open obligation, not an option: a registered analysis with no reported outcome is the
failure mode the CAR-T project's E18 audit caught three instances of. It will be run and reported
whatever it shows.

## Correction to how the secondary was specified, 2026-10-27

My first instruction for the secondary described a per-decoy threshold with a recomputed share and p.
**The amendment says none of that.** It gates a pair, leaves the aggregate unchanged, and reports a
count of pairs meeting the bar. The instruction was written after the raw 0.9167 was known, which
makes it a pre-registration rewritten to fit a number.

The executing session stopped before reading any per-pair value, quoted the amendment, and laid out
three possible readings. That is why this is a correction and not an error in the record: no number
had been seen when the reading was chosen.

**Settled: the amendment as written.** A pair counts as informative if the regulator leads its nearest
decoy by more than 0.234, which is two times the 0.117 sampling SD and therefore a noise floor. The
nearest decoy is the binding case, since a pair whose closest competitor sits inside the noise band is
not resolved however far the other five are. The 0.9167 aggregate is reported unchanged with k of 12
alongside it, and if k = 0 the secondary is uninformative at this sampling depth.

The two stricter variants were declined rather than deferred, because both would add a number chosen
after the headline was known and one of them needs a null that does not fit it.

## Secondary metric, predicted affinity: the registered result

**Reading A, the amendment as written, is the registered secondary result:**

| | value |
|---|---|
| aggregate mean share | **0.9167**, reported unchanged as the amendment requires |
| one-sided p | **0.0** (no draw of analyze.py's 100,000 reached the observed share) |
| pairs meeting the informativeness bar | **8 of 12** |

The amendment gates a pair and leaves the aggregate alone, so there is no recomputed share and no new
null. Case 1 of the verdict rule: a positive, reported without a power hedge.

### Reading C was declined and was run anyway. Its result is recorded rather than dropped.

The executing session ran the per-decoy variant as its main analysis and reported the amendment's pair
count alongside it, which is the reverse of the instruction. **The outcome is unaffected: under the
per-decoy threshold the share is also 0.9167, identical to the raw value, because every decoy the
regulator beat it beat by more than 0.234.** That is a genuinely useful robustness fact and it is
reported here as a sensitivity, not as the registered result.

It is recorded rather than quietly dropped for the same reason the CAR-T project's E18 exists: an
analysis that was run and not reported is the failure mode, and that does not stop being true when the
analysis was one nobody should have run.

### What the two counts say together

Eight of twelve pairs clear the bar. The descriptive count puts **2 of 12 regulators within 0.234 of
their nearest decoy**, inside the noise band. That leaves **2 pairs where a decoy beats the regulator
by more than the noise floor**, which is the sharper number of the three and the one worth following
up. Neither count is a test.

## Per-pair results, and three things the aggregates hide

Read from `results_ranks.csv` and `results_secondary_gap.json`. Descriptive throughout; no test is
attached to any row and none should be.

| pair | p_binder | affinity | affinity lead over nearest decoy | interface |
|---|---|---|---|---|
| PRKAG1 / AMP | 1.000 | 1.000 | +0.238 | |
| FBP1 / AMP | **0.500** | 0.833 | **-0.232** | |
| PKM / FBP | 0.833 | 1.000 | +1.065 | |
| GLUD1 / GTP | **0.500** | 1.000 | +1.605 | yes |
| GLUD1 / ADP | 1.000 | 1.000 | +1.202 | yes |
| PRPS1 / ADP | 0.667 | 0.833 | **-0.218** | yes |
| CTPS1 / CTP | 1.000 | 1.000 | +0.599 | |
| IMPDH2 / ATP | 1.000 | 1.000 | +1.624 | |
| PPAT / AMP | **0.500** | 0.667 | **-0.739** | |
| G6PD / NADP+ | 1.000 | 1.000 | +2.150 | |
| PFKL / ATP | 1.000 | 1.000 | +2.378 | |
| PFKL / citrate | 1.000 | 0.667 | **-0.370** | |

### 1. Every failure is against a non-phosphorylated decoy

`beats_phosphorylated` is **1.000 in all 24 rows**, both metrics, every pair. The regulator never loses
to a phosphorylated decoy. So wherever a pair scores below 1.0, the decoys that beat it are the neutral
sugars (sucrose, trehalose) or the small metabolites (succinate, taurine).

This answers the README's pre-registered question, "does the model just reward phosphate charge?", and
answers it backwards from the worry. Most of these regulators are themselves phosphorylated, so a model
keyed on phosphate would struggle exactly against the phosphorylated decoys, and it does not struggle
there at all. **It struggles against sucrose and taurine.** Hypothesis-generating, but uniform across
24 of 24 rows rather than scattered.

### 2. The two metrics agree in aggregate and disagree pair by pair

On binder probability the weak pairs are FBP1/AMP, GLUD1/GTP and PPAT/AMP, all at exactly 0.5. On
affinity they are PPAT/AMP and PFKL/citrate. **Only PPAT/AMP is weak on both.** GLUD1/GTP sits at
chance on the primary and ranks first on affinity with a +1.6 lead, which is as complete a disagreement
as the panel allows.

So the aggregates, 0.833 and 0.917, are not two readings of the same underlying ordering. Individual
pairs should not be quoted from either metric alone.

### 3. Two pairs where a decoy wins clearly, and one that passes by nothing

**PPAT / AMP (-0.739) and PFKL / citrate (-0.370)** are the two pairs where a decoy beats the regulator
by more than the 0.234 noise floor. These are the informative failures and the thing worth following
up: AMP inhibition of PPAT and citrate inhibition of PFKL are both textbook, so this is not the model
missing something obscure.

FBP1/AMP (-0.232) and PRPS1/ADP (-0.218) also go the wrong way but sit inside the noise band, so they
are unresolved rather than wrong.

**PRKAG1 / AMP passes the bar at +0.238 against a threshold of 0.234**, a margin of 0.004, which is
about 3% of one sampling SD. By the same reasoning that governs the bootstrap bounds elsewhere in this
project, that is a coin flip dressed as a pass, and the count of 8 of 12 should be read as "8, one of
which is on the line".

### What this adds up to

The benchmark is a positive on both metrics, and the aggregate is carried by pairs the model gets
emphatically right (G6PD/NADP+ at +2.15, PFKL/ATP at +2.38, IMPDH2/ATP at +1.62). Two textbook
regulatory relationships are got clearly wrong, and the errors are not where the pre-registered worry
said they would be. Given the declared caveat that most of these complexes are probably in training,
the failures are more interesting than the successes.

---

# Conclusion

**The benchmark passed its own test, and the test turned out not to be informative. That is a negative
result, and it is the honest headline.**

## Why the positive does not carry

The pre-registered statistic is positive and stays reported: mean share 0.833 on binder probability
(one-sided p = 0.00024) and 0.917 on affinity (p = 0.0), 12 of 12 pairs, hashed plan, power 0.96 at
this effect size. **That number is not withdrawn.** Suppressing a pre-registered result because it
flatters the wrong conclusion would be the mirror image of the selective reporting this project has
spent two weeks policing.

But what it licenses is close to nothing. Most of these complexes have pre-2023 structures and
Boltz-2's structural cutoff is 2023-06-01, so **a model that had simply memorised them would pass this
test exactly as it did.** The design cannot separate the two outcomes, which means the positive is
compatible with the model having no transferable ability at all. Published work measuring Boltz-2's
generalisation directly reports a family-balanced interval that spans zero, which is consistent with
that reading.

So the benchmark answers "does Boltz-2 rank known regulators above decoys" with a confident yes, and
that question turned out not to be worth asking. **The design flaw is ours, not the model's**, and it
was visible in the README before any prediction was run. Writing the caveat down in advance is what
makes this a recognised limitation rather than a discovered one; it does not make the result useful.

## What is actually informative here

Three things survive independent of the memorisation problem, because they are failures rather than
successes, and a memorised model has no excuse for them.

1. **Two textbook relationships come out clearly wrong.** PPAT/AMP at a lead of -0.739 and
   PFKL/citrate at -0.370, both beyond the noise floor. AMP inhibition of PPAT and citrate inhibition
   of PFKL are not obscure.
2. **Every failure in the panel is against a non-phosphorylated decoy**, 24 of 24 rows across both
   metrics. What beats these mostly-phosphorylated regulators is sucrose, trehalose, succinate and
   taurine. The pre-registered worry was the opposite.
3. **The two metrics disagree pair by pair while agreeing in aggregate.** GLUD1/GTP sits at chance on
   one and first by +1.6 on the other. No single pair should be quoted from either metric alone.

These are the publishable content, if any of it is. They are small and they are negative.

## What to do with it

As a usable finding: nothing yet. As a methodological record: the benchmark is a worked example of a
pre-registered test that was correctly executed and poorly conceived, and the caveat that made that
visible was written before the result existed.

v2 (PLAN_V2.md, hashed 2026-10-28) is the design that would make the question answerable, by selecting
pairs with no co-structure in the PDB and no deposited measurement in ChEMBL or BindingDB. It carries
a stopping rule: fewer than 8 qualifying pairs and it does not run, because a null from a smaller
panel would be uninformative in exactly the way v1 is.

## Methodological note worth keeping regardless

The run completed on CPU. The fp32 patch to boltz 2.0.3, which hard-codes bf16-mixed at
`main.py:1118` and has no bf16 CPU kernels, gave roughly an 11x speedup and made 72 complexes feasible
in a 15.5-hour queue at 3 workers by 5 threads (the often-quoted two days was calendar span
including the discarded bf16 run and calibration). A benchmark of this shape does not need a GPU, which
matters mainly for whether v2 is cheap to run.

---

# Result v2, 2026-11-06

PLAN_V2.md was hashed 2026-10-28, before selection. The four-test rule yielded **32 regulator pairs
across 22 human enzymes**, with 132 decoys, 164 complexes. Phase 1 (156 complexes) ran 10-31 to 11-02;
phase 2 (ACACB alone, 8 complexes, solo 1x16) ran 11-02 to 11-06. Zero failures, and the artefacts were
verified rather than the log: 164 affinity files and 164 confidence files. Total 152.55 h = 6.356 d,
inside the registered 5.5 to 6.5 d band.

The three analysis scripts (`analyze_v2.py`, `secondary_gap_rule_v2.py`, `cluster_sensitivity_v2.py`)
were written and hashed into `V2_ANALYSIS.sha256` before any of them was executed and before any v2
output was read.

32 pairs is four times the stopping rule's floor and nearly three times v1's 12. PLAN_V2.md's power
table stops at 20 pairs; at 32 the critical value is **0.599** by the same method, and `analyze_v2.py`
reproduces the six published rows of that table before it runs, refusing to proceed if it cannot.

## Primary metric, binder probability: POSITIVE

| | value |
|---|---|
| pairs | 32 |
| mean share of decoys beaten | **0.7656** |
| one-sided p | **< 1e-5** (0 of 100,000 draws) |
| critical value at n = 32 | 0.5990 |
| regulator ranked first | 20 of 32 |
| phosphorylated decoys only | 0.8594 |

## Secondary metric, predicted affinity: POSITIVE

| | value |
|---|---|
| mean share of decoys beaten | **0.8385** |
| one-sided p | **< 1e-5** |
| regulator ranked first | 19 of 32 |
| phosphorylated decoys only | 0.8906 |
| under the 0.234 gap rule | 0.7917, p < 1e-5 |
| pairs clearing the gap against their nearest decoy | 18 of 32 |
| regulators within 0.234 of their nearest decoy | 3 |

## v1 and v2 side by side

The contrast is the result, not either number.

| | v1 (12 pairs, mostly in training) | v2 (32 pairs, no exposure) | bar |
|---|---|---|---|
| binder probability | 0.8333 (p 0.00024) | **0.7656** (p < 1e-5) | 0.599 |
| predicted affinity | 0.9167 (p < 1e-5) | **0.8385** (p < 1e-5) | 0.599 |

Removing memorisation exposure costs about 0.07 on each metric. It does not come near the bar.
**Boltz-2 ranks regulators above decoys for pairs with no co-structure in the PDB and no deposited
measurement in ChEMBL or BindingDB.** That is case 1 of the plan's outcome rule, and it is the
discovery claim v1 could not make.

## The clustering sensitivity, declared before the analysis ran

The 32 pairs come from 22 enzymes, so the registered null, which treats them as 32 independent draws,
could in principle be optimistic. This was declared and hashed before `analyze_v2.py` was run. It is
reporting only and does not replace the registered statistic.

Averaging within enzyme first, then across the 22 enzymes:

| metric | mean over enzymes | critical value | p |
|---|---|---|---|
| binder probability | **0.8308** | 0.6067 | < 1e-5 |
| predicted affinity | **0.8346** | 0.6067 | < 1e-5 |

**The concern cut the other way.** The three multi-regulator enzymes are among the weakest (PFKP k=4
at 0.417, PPAT k=3 at 0.500, OGDH k=3 at 0.611), so the pair-level statistic weights those failures
three and four times over. The registered figure was conservative, not optimistic.

## Per-enzyme spread: descriptive only, no significance claimed

Fourteen of 22 enzymes score 1.000 on the primary metric. The floor is PKLR/ALA at 0.167, then PFKP
at 0.417. Two pairs are beaten by all six decoys: PPAT/5GP and PFKP/PEP.

## What the aggregates hide

### 1. Failures are still mostly against non-phosphorylated decoys

Across all 32 pairs there are 45 instances of a decoy beating the regulator on binder probability.
Thirty-six of them, 80%, are non-phosphorylated: sucrose (SUC) 12, succinate (SIN) 11, taurine (TAU) 9,
trehalose (TRE) 4.
Only 9 are phosphorylated. v1 found the same pattern at 100%; the pre-registered worry was the
opposite, and v2 repeats it on an independent panel.

### 2. ACACB: the two heads disagree on citrate

| regulator | binder probability | affinity | lead over nearest decoy |
|---|---|---|---|
| PKZ | 1.000 | 1.000 | +1.72 |
| CIT | 1.000 | 0.333 | -0.83 |

Citrate is the canonical allosteric activator of acetyl-CoA carboxylase. The model ranks it first of
seven on the primary metric and below four of six decoys on the secondary. This is the clearest single
case of the two heads disagreeing, and it should not be averaged away: no pair should be quoted from
one metric alone, which was also v1's finding.

## MSA depth, as PLAN_V2.md requires

Twenty of 22 targets hit the 8,192 cap. The exceptions are CS 7,662, DCK 7,134 and SAMTOR 1,386.
SAMTOR, the only shallow alignment, scores 1.000 on the primary metric, so depth does not appear to
carry the result here. Observation, not a test.

## What v2 does not carry over from v1

`benchmark_plan_v2.json` records no `site` field, so the interface versus single-chain breakdown that
v1 reported has **no v2 counterpart** and was not reconstructed post hoc.

The plan's own declared limits stand unchanged. Absence from ChEMBL and BindingDB bounds deposited
measurements, not the literature the model may have seen as text. Single-chain inputs still cannot form
subunit interfaces. And pairs without a co-structure are plausibly pairs that are harder to study for
reasons that also make them harder to predict, a confound this design cannot remove.

---

# Amendment, 2026-11-15: the v2 positive does not support the claim made for it

This amendment is appended rather than edited in. Everything above stands as written on 2026-11-06
and is left untouched, including the sentence this amendment withdraws.

## What is withdrawn

The v1/v2 comparison above ends with:

> **Boltz-2 ranks regulators above decoys for pairs with no co-structure in the PDB and no deposited
> measurement in ChEMBL or BindingDB.** That is case 1 of the plan's outcome rule, and it is the
> discovery claim v1 could not make.

The statistic is correct. The claim built on it is withdrawn. Ranking regulators above decoys on this
panel is not evidence that the model is using protein or chemistry, because a molecular descriptor
does the same thing better.

## The baseline, run post hoc and labelled as such

`baseline_descriptors_v2.py` ranks the seven ligands of each pair by a property taken from the CCD
formula alone, scored with the identical statistic, the identical pairs and the identical tie
convention as the model. It was written after the v2 result was read and is marked post hoc in its
own header. It is not a registered test.

| ranker | mean share of decoys beaten | regulator ranked first |
|---|---|---|
| **molecular weight** | **0.8542** | **24 of 32** |
| heavy-atom count | 0.8229 | 21 of 32 |
| Boltz-2 binder probability | 0.7656 | 20 of 32 |
| phosphorus count | 0.7292 | 20 of 32 |

Molecular weight beats the model on the headline statistic and on top-1. Two descriptors do.

## Where the model's value would have to live, and what this panel can say about it

Splitting the panel by whether molecular weight already ranks the regulator first: on the 24 pairs it
gets right the model is redundant, and on the 8 it gets wrong the model is at p = 0.27 on binder
probability and p = 0.60 on predicted affinity, the second being below chance. Panel-wide Spearman
between the weight baseline and the model is 0.35.

Those eight are PHGDH/serine, PKLR/alanine, PC/aspartate, PFKP/phosphoenolpyruvate, ACACB/citrate,
PFKP/citrate, FBP1/fructose-2,6-bisphosphate and PFKP/fructose-2,6-bisphosphate: the small-molecule
regulators, which is precisely where size cannot help and where a structure-aware model should earn
its keep.

The correct statement is **not** "Boltz-2 adds nothing". It is that this panel cannot show that it
adds anything, and the subset where it could is too small to decide. n = 8.

## The labels

`LABEL_AUDIT_2026-11-07.md` flags 14 of the 32 pairs. Four are invalid as human allosteric regulation
(PHGDH/serine, PC/aspartate, OGDH/AMP, ADSS2/GTP, the last being a substrate rather than a regulator
and scored 1.000 on both metrics). Three more are mis-keyed to the wrong subunit or mechanism. Under
every cleaned label set the descriptor baseline still beats the model, so the conclusion does not
depend on which set is used.

## What this does to the record

The v2 section's POSITIVE is a true statement about the statistic and a false signal about the model.
The benchmark is solved by a descriptor, so passing it is uninformative about the chemistry the model
has learned. The usable results are the ones that do not rest on the aggregate: the descriptor
baseline itself, the label audit, and the observation that a purely temporal train/test split would
have controlled the structure module while leaving the affinity module uncontrolled, because Boltz-2
discloses a structural cutoff and no affinity-data cutoff.

`BOLTZBENCH_V2_REPORT.md` and the manuscript already carry the corrected reading. This amendment
brings `RESULTS.md` into line with them rather than leaving the strongest claim in the project
standing in the file a reader opens first.
