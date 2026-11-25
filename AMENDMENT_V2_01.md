# v2 amendment 1, 2026-10-29: test 3 does far less than the plan claimed

Written after selection and **before any prediction is run**. PLAN_V2.md and CANDIDATES_V2.md are
unchanged and still verify against V2.sha256. **The registered rule is not altered**; what follows
records a weakness in it and declares a stratification, both before any result exists.

## The design claim that was wrong

PLAN_V2.md justified selecting on database absence rather than on dates with this reasoning: the
affinity head trains on ChEMBL and BindingDB with no disclosed cutoff, so a temporal filter would
leave the secondary metric uncontrolled, and test 3 "is the control a temporal design cannot give, and
it is the reason the panel is selected this way".

**Test 3 eliminated two pairs of 73**, both CAD rows. Sixty-four of 73 passed it. The reason is that
ChEMBL and BindingDB are medicinal-chemistry resources holding drug-like compounds screened against
targets, while enzymology on endogenous metabolites lives in BRENDA and SABIO-RK. The control I built
the design around barely bites.

The arm is working correctly, which was checked rather than assumed: PRKAG1/AMP returns 13 ChEMBL
records through the identical code path, PFKP and G6PD resolve to targets carrying 228 and 797
activities, human GLUD1 is genuinely absent from ChEMBL, and the BindingDB matcher parsed 2,260 of
2,260 ligands with its self-test firing. The databases are being read correctly and do not contain
this kind of measurement.

**Two real bugs were caught upstream by the sanity check and fixed before the run**: PubChem CID
445555 for "fructose 1,6-bisphosphate" is the 2,5-anhydro analogue, which would have missed every
F-1,6-BP co-structure, and `gene_exact:GCK` returns MAP4K2 because GCK is also a synonym for germinal
centre kinase. Chemistry is now anchored on the PDB component dictionary.

## What this does and does not mean

It does not mean the affinity head is exposed to these pairs. It means **absence from these two
databases bounds per-pair exposure and not per-target exposure.** PFKP with 228 deposited activities
is a pocket the model has seen many ligands in, even though ATP is not one of them. That distinction
was not in the plan and should have been.

Adding BRENDA or SABIO-RK would change the registered rule after seeing the filter's output, so it is
not done. It is the right change for a v3.

## The larger problem: chemical adjacency

Roughly half the surviving panel is chemically adjacent to an exposed pair. G6PD passes on NADPH while
17 structures hold NADP+ at the same site. RRM1 passes on dGTP while dATP and dTTP are bound. PPAT
passes on GMP and ADP while AMP is bound. The registered rule is per-pair, so these pass as written
and none was dropped.

A co-structure with a near-identical ligand at the same site is exposure in every sense that matters
for this benchmark, and the plan's test 2 does not capture it.

## Declared now, before any prediction

1. **Primary analysis: all 32 pairs**, as registered. Power 1.00 at a true share of 0.70 and 0.92 at
   0.65, so the panel is comfortably sized.
2. **Pre-specified secondary: the structurally naive subset.** For each surviving pair, compute the
   maximum ECFP4 Tanimoto between the regulator and any ligand appearing in a co-structure of that
   enzyme. The subset is pairs scoring **below 0.70**, the conventional similarity threshold. Report
   both the full panel and the subset. Power stays adequate down to 16 pairs (0.90 at a true share of
   0.70) and the subset's size is reported whatever it is.
3. **Maximum Tanimoto is reported per pair** as a continuous covariate alongside the result, so a
   reader can see the exposure gradient rather than only a dichotomy.
4. **Target-level ChEMBL activity count is reported per enzyme**, for the same reason.
5. **PFKP and CTPS2 are not like-for-like with v1**, which used PFKL and CTPS1. Any v1-to-v2 comparison
   excludes those two rows or states the substitution.
6. **Test 1 as executed verified that on-topic primary literature exists**, not that each regulation is
   established specifically by kinetics or mutagenesis. That is weaker than the plan's wording and is
   reported as such. Four rows screened zero on nomenclature alone (UniProt's "Pyruvate kinase PKM"
   against the literature's "pyruvate kinase M2") and were verified by hand; none was dropped.

## Why this is an amendment and not a rewrite

The panel, the rule that produced it, and the statistic are all unchanged. What is added is a
stratification whose definition is fixed before any prediction exists, and an honest statement that
the control the plan leaned on turned out to be nearly vacuous. The result of v2 will be reported
against the registered primary either way.
