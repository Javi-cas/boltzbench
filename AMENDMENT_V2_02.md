# v2 amendment 2, 2026-10-29: the adjacency cut fails too, and is reported rather than replaced

Written after preparation and **before any prediction is run**. All three hashed files are unchanged
and still verify. **No rule is altered.**

## The 0.70 Tanimoto cut does not separate what it was declared to separate

Amendment 1 declared a pre-specified subset of pairs scoring below 0.70 maximum ECFP4 Tanimoto against
any ligand in a co-structure of that enzyme, and used three worked examples to motivate it. Measured:

| case | max Tanimoto | nearest bound ligand |
|---|---|---|
| G6PD / NADPH | **0.582** | NADP+ |
| PPAT / GMP | **0.661** | AMP |
| RRM1 / dGTP | 0.723 | GDP |

**Two of the three examples the amendment used to argue the subset was needed land inside the subset.**
The cut removes 6 of 32 pairs and leaves the adjacency problem substantially intact. ECFP4 Tanimoto
runs low on small phosphorylated metabolites: NADPH against NADP+, which differ by a hydride, scores
0.582, while ATP against ADP scores 0.981.

The measurement is sound and was checked rather than assumed. Every named ligand is found and is the
nearest; positive controls fire at ATP/ATP 1.000, ATP/ADP 0.981, ADP/AMP 0.849; both RDKit fingerprint
APIs agree; and no pair's own regulator appears in its enzyme's ligand set, which is the consistency
this must have with test 2.

## Decision: change nothing, and report the failure with the result

This is the **second** exposure control in this design that does not work as specified. Test 3 removed
2 pairs of 73 because the affinity head's databases do not hold endogenous metabolite enzymology. The
adjacency cut removes 6 of 32 and misses its own examples.

A third control, specified after watching the second fail, would be fishing for a filter that produces
a panel I like. So the registered analysis stands exactly as hashed: **primary on all 32, the declared
0.70 subset reported as declared, and the Tanimoto reported per pair as the continuous covariate
amendment 1 already required.** The cut's failure is reported alongside it, with these three numbers,
so a reader sees the gradient rather than a dichotomy that does not hold.

## What v2 therefore tests, stated plainly

Not "pairs the model has no exposure to". **Pairs where the model has not seen this ligand in this
enzyme, though it may have seen chemically adjacent ligands in the same pocket.** Test 2 is the control
that works, and it eliminated 39 of 73. That is a narrower claim than PLAN_V2.md implied and it is the
one the result will support.

## Three corrections to my own instructions

1. **164 input complexes, not 224.** A decoy panel belongs to the enzyme, not the pair, so PFKP's four
   pairs share one six-decoy panel exactly as v1 did for GLUD1 and PFKL. 32 regulators plus 22 by 6
   decoys. Building 224 would have predicted the same complex up to four times, returned four different
   answers at SD 0.117, and cost about 40% more.
2. **My claim that a missed decoy exclusion inflates the score was backwards.** A decoy that genuinely
   binds ranks high, so the regulator beats fewer decoys: it deflates. The direction is conservative,
   but it means a null could not be read cleanly, which is the opposite failure from the one I warned
   about.
3. **22 enzymes, not the 20 stated in the selection report.**

## Two items flagged and deliberately left alone

**PKM keeps succinate as a decoy.** Succinate appears in 9HIA and 9HIB, almost certainly a
crystallisation additive, so it is not a substrate, product or effector and the registered rule keeps
it. The small-metabolite class has only two members so no substitution exists. Flagged, kept, and it
errs conservative.

**Two decoy substitutions were made, both phosphorylated and neither exhausting the list.** PGD loses
3-phosphoglycerate because PDB 4GWK is a deliberate human 6PGD complex with it and Hitosugi et al.,
*Cancer Cell* 2012 reports 3-PG as a 6PGD inhibitor, making it an effector rather than an artefact.
PHGDH loses 3-phosphoglycerate as a substrate. Both take PEP.

## Timing, corrected

v1's queue ran **15.5 hours**, not two days; the larger figure was calendar span including the
discarded bf16 run and calibration. The fitted model `T = 0.2805 * L^1.447` carries 4.3% median error
and back-checks against v1 at 1.04x.
