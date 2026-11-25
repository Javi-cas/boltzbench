# Benchmark v2 preparation: Tanimoto covariate, decoy panels, inputs, cost

Run 2026-10-28. `shasum -a 256 -c V2.sha256` passes for `PLAN_V2.md`, `CANDIDATES_V2.md` and
`AMENDMENT_V2_01.md`, before and after; none was edited. **Nothing was launched.** `runs_v2/` does not
exist and no boltz process was started. Script: `v2_prepare.py`, raw responses cached under
`v2_prep_raw/`.

One correction to the selection report first: it said the panel covers 20 enzymes. It covers **22**.
The pair count, 32, was right.

## Step 1: the Tanimoto covariate

For each pair, the maximum ECFP4 (Morgan radius 2, 2048 bit) Tanimoto between the regulator and any
chemical component appearing in a co-structure of that enzyme or a homolog above 95% identity. The
protein side is the same RCSB sequence query test 2 used, with the same sequence and the same
`identity_cutoff` 0.95 and `evalue_cutoff` 1; the ligand side is every non-polymer component of every
matching entry, from the data API. 309 components, all with SMILES, all parsed.

**Subset for the pre-specified secondary (max Tanimoto < 0.70): 26 of 32 pairs.**

### The sanity check did not come out as predicted, and the reason is the metric, not the ligand set

The three cases named as expected-high land at 0.582, 0.723 and 0.661, so two of the three fall inside
the "structurally naive" subset. Per the instruction I treated that as a sign the ligand set was wrong
and went looking. It is not wrong:

- **G6PD/NADPH 0.582.** The ligand set is BG6, CU, GOA, GOL, **NAP**, PO4. NADP+ is found and is the
  nearest. ECFP4 scores NADPH against NADP+ at 0.582 because the redox change rewrites every atom
  environment in the nicotinamide ring, even though the adenine, both riboses and all three phosphates
  are identical.
- **RRM1/dGTP 0.723.** The ligand set contains **DTP** (dATP, 0.692), **TTP** (dTTP, 0.588), GDP
  (0.723), ATP and CDP. Both ligands named are found. dGTP against dATP scores 0.692, just under the
  cut; GDP edges it out at 0.723 and carries the pair over.
- **PPAT/GMP 0.661.** The ligand set is A1CQ3, A1CQ4, **AMP**, MG, SF4. AMP is found and is the
  nearest, at 0.661.

Three further checks. Positive controls behave: ATP against itself 1.000, ATP against ADP 0.981, ADP
against AMP 0.849, succinyl-CoA against acetyl-CoA 0.872. The two RDKit fingerprint APIs agree to
three decimals on every pair. And **no pair's own regulator component appears in its enzyme's ligand
set**, which is the consistency this must have with test 2 and does.

So the ligand sets are right and the arithmetic is right. What is off is the threshold. ECFP4 runs
low on small, heavily phosphorylated metabolites, and **0.70 does not capture the adjacency
AMENDMENT_V2_01.md was written about.** The amendment's own worked examples are G6PD/NADPH against
bound NADP+ and PPAT/GMP against bound AMP, and the rule as written puts both in the naive subset. At
26 of 32 the stratification barely stratifies: it removes 6 pairs and leaves the adjacency problem
substantially inside the subset.

I have **not** changed the cut. It was fixed in a hashed file before any prediction exists, and
changing it is a change to a registered analysis, not a fix. Flagging it before the run rather than
after is the whole point of the covariate being continuous (amendment item 3), so a reader can see
the gradient whatever the dichotomy does.

### Table A: maximum ECFP4 Tanimoto per pair

| # | enzyme | regulator | max Tanimoto | nearest co-structure ligand | ligands searched | in subset |
|---|---|---|---|---|---|---|
| 2 | PFKP | citrate | **0.070** | F6P (6-O-phosphono-beta-D-fructofuranose) | 9 | yes |
| 3 | PFKP | fructose-2,6-bisphosphate | **0.641** | F6P (6-O-phosphono-beta-D-fructofuranose) | 9 | yes |
| 4 | PFKP | AMP | **0.849** | ADP (ADENOSINE-5'-DIPHOSPHATE) | 9 | no |
| 5 | PFKP | phosphoenolpyruvate | **0.200** | PO4 (PHOSPHATE ION) | 9 | yes |
| 8 | GCK | palmitoyl-CoA | **0.465** | ANP (PHOSPHOAMINOPHOSPHONIC ACID-ADENYLATE ) | 40 | yes |
| 13 | PKM | SAICAR | **0.452** | ADP (ADENOSINE-5'-DIPHOSPHATE) | 52 | yes |
| 15 | PKLR | alanine | **0.312** | PYR (PYRUVIC ACID) | 24 | yes |
| 16 | PDHA1 | acetyl-CoA | **0.185** | A5X (3-[(4-amino-2-methylpyrimidin-5-yl)met) | 7 | yes |
| 17 | PDHA1 | NADH | **0.178** | TPP (THIAMINE DIPHOSPHATE) | 7 | yes |
| 19 | FBP1 | fructose-2,6-bisphosphate | **0.561** | FBP (1,6-di-O-phosphono-beta-D-fructofurano) | 56 | yes |
| 21 | PC | aspartate | **0.190** | PYR (PYRUVIC ACID) | 8 | yes |
| 22 | CS | NADH | **0.465** | COA (COENZYME A) | 9 | yes |
| 23 | CS | succinyl-CoA | **0.872** | ACO (ACETYL COENZYME *A) | 9 | no |
| 27 | OGDH | succinyl-CoA | **0.183** | 8EL (2-[3-[(4-azanyl-2-methyl-pyrimidin-5-y) | 4 | yes |
| 28 | OGDH | NADH | **0.202** | 8EL (2-[3-[(4-azanyl-2-methyl-pyrimidin-5-y) | 4 | yes |
| 29 | OGDH | AMP | **0.207** | 8EL (2-[3-[(4-azanyl-2-methyl-pyrimidin-5-y) | 4 | yes |
| 31 | G6PD | NADPH | **0.582** | NAP (NADP NICOTINAMIDE-ADENINE-DINUCLEOTIDE) | 6 | yes |
| 33 | PGD | NADPH | **0.582** | NAP (NADP NICOTINAMIDE-ADENINE-DINUCLEOTIDE) | 6 | yes |
| 35 | PPAT | GMP | **0.661** | AMP (ADENOSINE MONOPHOSPHATE) | 5 | yes |
| 36 | PPAT | ADP | **0.849** | AMP (ADENOSINE MONOPHOSPHATE) | 5 | no |
| 37 | PPAT | PRPP | **0.386** | AMP (ADENOSINE MONOPHOSPHATE) | 5 | yes |
| 43 | ADSS2 | GTP | **0.982** | GDP (GUANOSINE-5'-DIPHOSPHATE) | 1 | no |
| 47 | CTPS2 | GTP | **0.688** | ATP (ADENOSINE-5'-TRIPHOSPHATE) | 9 | yes |
| 50 | RRM1 | dGTP | **0.723** | GDP (GUANOSINE-5'-DIPHOSPHATE) | 14 | no |
| 53 | DCK | dCTP | **0.811** | DCM (2'-DEOXYCYTIDINE-5'-MONOPHOSPHATE) | 54 | no |
| 54 | PHGDH | serine | **0.316** | TLA (L(+)-TARTARIC ACID) | 27 | yes |
| 60 | GLUD1 | palmitoyl-CoA | **0.474** | ADP (ADENOSINE-5'-DIPHOSPHATE) | 20 | yes |
| 63 | ACACB | citrate | **0.057** | 6U3 (2-[1-[(2~{R})-2-(2-methoxyphenyl)-2-(o) | 4 | yes |
| 64 | ACACB | palmitoyl-CoA | **0.119** | 6U3 (2-[1-[(2~{R})-2-(2-methoxyphenyl)-2-(o) | 4 | yes |
| 65 | CPT1A | malonyl-CoA | **0.000** | no ligand in any co-structure | 0 | yes |
| 66 | HMGCR | sterol / lanosterol | **0.183** | Y01 (CHOLESTEROL HEMISUCCINATE) | 27 | yes |
| 73 | SAMTOR | S-adenosylmethionine | **0.000** | no ligand in any co-structure | 0 | yes |

Subset (< 0.70): **26 of 32**. At or above the cut: PFKP/AMP 0.849; CS/succinyl-CoA 0.872; PPAT/ADP 0.849; ADSS2/GTP 0.982; RRM1/dGTP 0.723; DCK/dCTP 0.811.

## Step 2: the decoy panels

PLAN_V2.md's rule unchanged: two phosphorylated non-nucleotides from 3-phosphoglycerate (3PG),
glycerol-3-phosphate (G3P), PEP, ribose-5-phosphate (R5P) and glucose-6-phosphate (G6P), in that
order; two neutral sugars, sucrose (SUC) and trehalose (TRE); two small metabolites, succinate (SIN)
and taurine (TAU). Decoys belong to the enzyme, as in v1.

Each candidate was checked three ways rather than from memory. First the catalysed reaction. Second,
**whether the decoy is actually bound in a deposited structure of that enzyme**, by InChIKey skeleton
match against the same ligand sets computed in step 1: this is objective and it found five hits,
G6PD/G6P, PGD/3PG, PHGDH/3PG, PKLR/PEP and PKM/succinate. Third, a PubMed screen of all 198
enzyme-decoy combinations, whose counts turned out to be pathway co-mention noise (citrate synthase
and succinate co-occur 193 times because both are TCA) and were used only to decide what to read.

**Two substitutions**, both in the phosphorylated class, and no enzyme exhausted the list.

### Table B: decoy panel per enzyme

| enzyme | len | pairs | regulator CCDs | six decoys | substitution |
|---|---|---|---|---|---|
| ACACB | 2458 | 2 | CIT, PKZ | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| ADSS2 | 456 | 1 | GTP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| CPT1A | 773 | 1 | MLC | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| CS | 466 | 2 | NAI, SCA | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| CTPS2 | 586 | 1 | GTP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| DCK | 260 | 1 | DCP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| FBP1 | 338 | 1 | FDP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| G6PD | 515 | 1 | NDP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| GCK | 465 | 1 | PKZ | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| GLUD1 | 558 | 1 | PKZ | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| HMGCR | 888 | 1 | LAN | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| OGDH | 1023 | 3 | SCA, NAI, AMP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| PC | 1178 | 1 | ASP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| PDHA1 | 390 | 2 | ACO, NAI | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| PFKP | 784 | 4 | CIT, FDP, AMP, PEP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| PGD | 483 | 1 | NDP | G3P, PEP, SUC, TRE, SIN, TAU | **-3PG**: inhibitor: human 6PGD complexed with 3-phosphoglycerate, PDB 4GWK, Hitosugi et al. Cancer Cell 2012 |
| PHGDH | 533 | 1 | SER | G3P, PEP, SUC, TRE, SIN, TAU | **-3PG**: substrate; bound in deposited structures |
| PKLR | 574 | 1 | ALA | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| PKM | 531 | 1 | SSS | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| PPAT | 517 | 3 | 5GP, ADP, PRP | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| RRM1 | 792 | 1 | DGT | 3PG, G3P, SUC, TRE, SIN, TAU | none |
| SAMTOR | 405 | 1 | SAM | 3PG, G3P, SUC, TRE, SIN, TAU | none |

Recorded but never reached, because the first two phosphorylated candidates already passed: G6P is
G6PD's substrate and GCK's product, PEP is the substrate of PKM and PKLR and an inhibitor of PFKP
(and the regulator of pair 5), R5P is an isomer of PGD's product and the precursor of PPAT's
substrate.

### The two calls worth disputing

**PGD/3PG is excluded, and this is a judgement.** PDB **4GWK** is titled "Crystal structure of
6-phosphogluconate dehydrogenase complexed with 3-phosphoglyceric acid", human, from Hitosugi et al.,
*Cancer Cell* 2012, which reports 3-PG as an inhibitor of 6PGD. That makes 3PG an effector of PGD by
the plan's own wording, so it is skipped and PEP substituted. Without that structure the PubMed
screen alone (6 hits) would not have caught it.

**PKM/succinate is kept, and should not be trusted.** Succinate is bound in two deposited PKM2
structures, **9HIA** and **9HIB** (acetylated PKM2, titles mention FBP, so succinate is almost
certainly a crystallisation additive). It is not a substrate, product or effector of PKM, so the rule
as written keeps it. But it is a ligand the model may have seen in that protein, which is exactly
what a decoy should not be, and **the small-metabolite class has only two members, so the rule
provides no substitute**. Excluding it would mean either running PKM with five decoys or adding a
compound to the list, and both change the registered design.

**On the direction of the bias**, since the instruction says getting this wrong inflates the score:
it does not, it deflates it. A decoy that genuinely binds gets ranked high by the model, so the
regulator beats fewer decoys and the share falls. Leaving a substrate or effector in the panel makes
the test harder, not easier. That makes these errors conservative, which is the better way to be
wrong, but it also means a null result cannot be read cleanly if the panel is contaminated.

## Step 3: inputs built, and the cost

**164 input files in `inputs_v2/`**, plus `benchmark_plan_v2.json` for the runner. Single chain,
one diffusion sample, fp32, CPU, `--output_format pdb`, affinity property on ligand L: the format is
byte-identical to v1's `inputs/` after substituting sequence and CCD, and the five enzymes shared
with v1 (FBP1, G6PD, GLUD1, PKM, PPAT) carry byte-identical sequences. All 32 regulator components
and all 9 decoy components resolve in Boltz's own dictionary.

**164, not 224.** The 32 pairs by 7 complexes are 224 pair-complex slots, but a decoy complex belongs
to the enzyme and not to the pair, so PFKP's four pairs share one six-decoy panel. That is exactly
what v1 did, where GLUD1 and PFKL each had two regulators over one decoy set, and it is what "same
decoy panel construction" means. 32 regulator complexes plus 22 x 6 decoys = 164. Running the 224
separately instead would mean predicting the same complex up to four times, which at a measured
run-to-run SD of 0.117 would give four different answers, and would cost about 40% more.

### Time

Fitted on v1's 70 fp32 complexes at 3 workers x 5 threads, 318 to 780 aa: `T = 0.2805 * L^1.447` s,
median error 4.3%. The model back-checks against v1's own queue, which ran 67 complexes in 15.46 h
wall against 14.82 h ideal, a **scheduling realisation factor of 1.04**. v1's "roughly two days" was
the calendar span including the discarded bf16 run and the fp32 calibration; the queue itself was
15.5 hours.

| | cpu-slot hours | wall clock |
|---|---|---|
| power law, memory-aware worker counts | 184 | 3.9 d |
| quadratic fit instead | 261 | 6.8 d |
| x1.04 realisation | | **4.1 to 7.1 days** |
| the same without ACACB | 133 to 148 | **2.0 to 2.2 days** |

So most of a week, as guessed, and the spread is real: six of the 22 targets are longer than anything
v1 measured, so the fit is extrapolating and the two functional forms disagree by 2.3x at the top end.

### ACACB is the problem, and it is not mainly a time problem

ACACB is **2458 aa**, 3.2x the longest target v1 ran. It contributes **2 of 32 pairs and 8 of 164
complexes**, but **half to two thirds of the entire cost**: 50 cpu-hours under the power law, 113
under the quadratic, and it cannot share the machine, so that is 2.1 to 4.7 days of the 4.1 to 7.1.

Memory is the harder constraint. v1 measured peak RSS of 16.9 GB at 331 aa and 23.3 GB at 780 aa,
which fits `15.5 + 1.28e-5 * L^2` GB and predicts **about 93 GB for a single ACACB process** on a
128 GB machine that is also running the fmbench embedding job. That is a two-point quadratic
extrapolated 3.2x, so treat 93 GB as an order of magnitude, not a number. If it is right, ACACB runs
alone with no headroom; if it is optimistic, it swaps, and a swapping run invalidates the time
estimate entirely.

| enzyme | len | complexes | s/complex | predicted peak RSS | workers that fit |
|---|---|---|---|---|---|
| ACACB | 2458 | 8 | 22,593 to 50,997 | ~93 GB | 1 |
| PC | 1178 | 7 | 7,794 | 33 GB | 3 |
| OGDH | 1023 | 9 | 6,355 | 29 GB | 3 |
| HMGCR | 888 | 7 | 5,178 | 26 GB | 3 |
| RRM1 | 792 | 7 | 4,388 | 24 GB | 3 |
| PFKP | 784 | 10 | 4,324 | 23 GB | 3 |

Everything from CPT1A (773 aa) down is inside v1's measured range and takes 3 workers comfortably.

## What is not decided

Three things are flagged and none is acted on, because each would change what is computed:

1. **The 0.70 Tanimoto cut** does not separate what the amendment wanted it to separate. 26 of 32 is
   a weak stratification. The continuous covariate is reported either way.
2. **PKM's succinate decoy** is bound in two PKM2 structures and the rule offers no substitute.
3. **ACACB** may not be runnable on this machine, and dropping it would be dropping a line, which is
   reported rather than done. A single ACACB decoy complex run first would settle both the memory
   question and the extrapolation for about 6 to 14 hours.

## Files

`v2_prepare.py`; `v2_sequences.json`, `v2_ligands.json`, `v2_tanimoto.json`, `v2_decoy_flags.json`,
`v2_decoy_screen.json`, `v2_decoys.json`, `benchmark_plan_v2.json`; `inputs_v2/` (164 yaml);
`v2_prep_raw/` (cached responses); `logs/v2_ligands_stage.log`, `logs/v2_tanimoto_stage.log`,
`logs/v2_decoy_screen.log`, `logs/v2_decoys_stage.log`, `logs/v2_inputs_stage.log`,
`logs/v2_cost_stage.log`.

Stopping here: nothing is launched.
