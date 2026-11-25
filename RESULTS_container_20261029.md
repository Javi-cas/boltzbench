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
