# Benchmark v2: does Boltz-2 rank regulators it has not memorised?

Written 2026-10-28, before any pair is selected and before any prediction is run. **This plan is
hashed before selection begins**, because which pairs enter the panel is the largest researcher degree
of freedom in the design and the one most able to manufacture either result.

## The question v1 could not answer

v1 established that Boltz-2 ranks a known regulator above decoys at 0.833 on binder probability
(p = 0.00024) and 0.917 on affinity (p = 0.0), over 12 pairs. It also declared in advance that most of
those complexes are probably in training, so the result measures reproduction of known biology rather
than discovery. v2 asks the question that separates the two.

## What the exposure actually is, and why dates alone will not control it

Two facts set the design, both from the published record rather than from assumption.

1. **Boltz-2's structural training cutoff is 2023-06-01**, later than the 2021-09-30 used in
   AlphaFold3-style splits. The v1 README's "pre-2023" heuristic was therefore roughly right and
   slightly conservative.
2. **No affinity-data cutoff is disclosed.** The affinity head trains on ChEMBL and BindingDB with no
   stated date. **A purely temporal design would control the structure module and leave the affinity
   module, which is our secondary metric, entirely uncontrolled.**

Published work measuring this for Boltz-2 reports a large point-estimate generalisation gap with an
interval whose family-balanced endpoint spans zero, and finds that MSA depth moves novel-family pose
success dramatically (2% to 46% with a deeper MSA). So MSA depth is a confound, not a detail.

## Selection rule, fixed now

A candidate pair (enzyme E, metabolite M) enters the panel only if **all four** hold. Each is checkable
and each is recorded per pair, so a reader can audit the panel rather than trust it.

1. **The regulation is established**, by kinetics, mutagenesis or equivalent biochemistry, in at least
   one peer-reviewed paper. Record the citation.
2. **No co-structure.** The PDB contains no structure of E (or a homolog above 95% sequence identity)
   in complex with M, deposited at any date. Record the query and the date it was run.
3. **No deposited affinity measurement.** Neither ChEMBL nor BindingDB holds a binding or inhibition
   measurement for the E-M pair. Record the query. **This is the control a temporal design cannot
   give, and it is the reason the panel is selected this way rather than by date.**
4. **Human enzyme**, to match v1 and keep the decoy panel comparable.

Pairs are collected by working through established allosteric and feedback regulation in central
carbon, nucleotide and amino-acid metabolism, applying the four tests in order, and **keeping every
pair that passes**. No pair is dropped after its prediction is seen, and no pair is added once
selection closes.

## Everything else is unchanged from v1, deliberately

Same decoy panel construction (two phosphorylated non-nucleotides, two size-matched neutral sugars, two
small metabolites, skipping any that is a substrate, product or effector of that enzyme). Same primary
metric, binder probability. Same secondary, predicted affinity, under the same 0.234 gap rule. Same
statistic, mean share of decoys beaten against a uniform-rank null. Same one diffusion sample on CPU.

Holding these fixed is the point: **the only intended difference between v1 and v2 is memorisation
exposure**, so the comparison between them is interpretable.

## Power, and the stopping rule that follows from it

Simulated, 200,000 draws, 6 decoys per pair:

| pairs | critical value | power at 0.70 | at 0.75 | at 0.80 |
|---|---|---|---|---|
| 6 | 0.722 | 0.32 | 0.59 | 0.83 |
| 8 | 0.688 | 0.52 | 0.80 | 0.96 |
| 10 | 0.667 | 0.67 | 0.91 | 0.99 |
| 12 | 0.653 | 0.77 | 0.96 | 1.00 |
| 15 | 0.644 | 0.85 | 0.98 | 1.00 |
| 20 | 0.625 | 0.95 | 1.00 | 1.00 |

**Stopping rule, fixed now: if selection yields fewer than 8 pairs, the benchmark is not run.** At 6
pairs a true effect of 0.70 is missed two times in three, and a null from that panel would say nothing
about the model while looking like it did. Below 8, report the selection outcome and the count, and
stop there.

## What each outcome licenses, stated before any of them exists

- **v2 share at or above its critical value.** Boltz-2 ranks regulators above decoys for pairs it has
  no structural or affinity exposure to. That is the discovery claim v1 could not make.
- **v2 share between 0.50 and the critical value.** Not a refutation. Report the share, the p and the
  power, and say the panel cannot separate a modest effect from none. This is the likely outcome at
  realistic panel sizes and is worth saying in advance.
- **v2 share at or below 0.50.** The v1 result is reproduction without generalisation.
- **In every case, report v1 and v2 side by side.** The contrast is the result, not either number.

## Declared in advance

MSA depth is recorded per target and reported with the result; v1 did not record it and v2 cannot
reinterpret v1 on it. Absence from ChEMBL and BindingDB bounds deposited measurements, not the
literature the model may have seen in text. Single-chain inputs still cannot form subunit interfaces.
Pairs without a co-structure are plausibly pairs that are harder to study for reasons that also make
them harder to predict, which is a confound this design cannot remove and should not pretend to.
