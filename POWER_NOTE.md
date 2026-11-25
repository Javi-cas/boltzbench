# Power of the 12-pair benchmark, computed 2026-10-27 before any result was read

**This note does not alter the plan.** README.md, benchmark_plan.json, run_all.py and analyze.py are
unchanged and still verify against PLAN.sha256. Nothing here changes the statistic, the null or the
decoy panel. It records what the benchmark can and cannot detect, written now so that a weak result
is read correctly later rather than argued about afterwards.

Simulation: 200,000 draws, 12 pairs, 6 decoys each, null = uniform rank among 7.

- Null mean share: 0.500. **One-sided 5% critical value: mean share 0.653.**

Power, if the regulator truly beats each decoy independently with probability p:

| true per-decoy p | expected mean share | power |
|---|---|---|
| 0.60 | 0.60 | **0.15** |
| 0.70 | 0.70 | 0.77 |
| 0.75 | 0.75 | 0.96 |
| 0.80 | 0.80 | 1.00 |

**How to read the result when it lands.**

- A mean share at or above about 0.70 is a real positive and the benchmark is well powered for it.
- A mean share near 0.60 is the dangerous zone: a genuine but modest ability to rank regulators above
  decoys would be missed 85% of the time. **A non-significant result there means underpowered, not
  refuted,** and must be reported with that number rather than as evidence of no effect.
- Only a mean share at or near 0.50 supports the stronger reading that the model does no better than
  chance on this task.

This is the same failure mode the CAR-T work hit with 13-patient cohorts: small cohorts exclude large
effects, not all effects. Stating the boundary before the number exists is the only way to keep that
distinction honest.

The subgroup analyses named in the README (phosphorylated decoys only; within-chain versus interface
sites) split 12 pairs further and are weaker still. They are hypothesis-generating by construction and
no significance claim should rest on them.

---

## Addendum, 2026-10-27: the boundaries, fixed before the result exists

The table above left three ranges unspecified and one failure mode unhandled. Settled here, still
before any result. The plan files remain unchanged and still verify against PLAN.sha256.

### The anchors in the table were the wrong shape, and that is corrected here

Saying "a mean share at or above about 0.70 is a real positive" implied that a significant result below
0.70 is somehow less of one. That is a category error and it is withdrawn. **Significance governs
positives; power governs nulls.** Power says how often a true effect would be missed, so it bears on
how to read a failure to reject, and not at all on how to read a rejection.

### The verdict rule, complete

Let `s` be the observed mean share on the primary metric, the binder-probability aggregate, and let the
critical value be whatever `analyze.py` computes for the pairs that actually ran.

1. **`s` at or above the critical value (p < 0.05): a positive.** Report the share and the p and stop.
   Do not hedge it on power grounds, and do not mention the power figures in the same breath, because
   they are not about this case.
2. **`s` between the null mean of 0.50 and the critical value: the test does not reject, and the
   benchmark cannot tell a modest effect from none.** Report the share, the p, and the power figures in
   the same sentence. **Do not write that the model performs no better than chance**, and do not write
   that it fails, because the data do not distinguish those from a real effect of 0.60 to 0.65.
3. **`s` at or below 0.50: the only case where "no better than chance" is accurate**, because the point
   estimate itself shows no tendency in the predicted direction. Say it plainly there.

No threshold is invented. Boundary 1 is the test's own critical value and boundary 2 is the null's own
mean. The range 0.653 to 0.70 falls in case 1 and is a positive.

### If any complex fails

`analyze.py` drops the affected pair and recomputes its own null, so the critical value shifts.
**Use the critical value `analyze.py` reports for the pairs that actually ran, never 0.653 from memory**,
and state the pair count with the verdict. If the count falls below 12, the power figures above no
longer apply and must be recomputed for the new count before any case-2 wording is used; say so rather
than reusing them.

### Scope

This rule governs the primary metric only. The secondary, predicted affinity, stays under the 0.234 gap
rule of amendment 2026-10-26b and is unaffected by anything here.
