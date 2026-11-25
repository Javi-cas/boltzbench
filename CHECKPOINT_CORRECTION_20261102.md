# Correction to the 45 h checkpoint, 2026-11-02

## What you got right, including two good catches

- **142 of 156, zero failures.** Confirmed; a grep for fail, error, traceback and non-zero exits across
  the whole run log returns nothing.
- **The 1h57m log gap is not a stall.** Confirmed from the other side: `OGDH__SCA__true` is in its
  affinity stage as I write, with 3PG and G3P started at 00:37 and 00:45 UTC. Three long complexes
  finishing in step is exactly the pattern, and reading it that way was right.
- **The daylight-saving catch is correct and genuinely useful.** Local time fell back at 02:00 on
  1 November, so any end time computed by subtracting local timestamps across that boundary undercounts
  by an hour. Reading elapsed from `etime` and labelling CST is the right response.
- **The memory finding is good news and well characterised.** OGDH workers at 9.2 to 12.5 GiB against
  about 28 GiB predicted, 85% free, compressor 2.9 GiB. Three workers needs no second thought.
- **The per-protein ratios are a real finding**, and declining to re-fit mid-run was right.

## Three corrections

**1. The artefacts are 142 / 143 / 143, not 142 / 142 / 142.** One complex, `OGDH__SCA__true`, has its
pdb and confidence written and no affinity yet, because it is in the affinity stage now. Benign, but it
matters for the handover: **step 2 of the handover requires both an affinity and a confidence file per
complex, and an in-flight complex will show exactly this shape.** Do not read that one-file gap as a
failure when you run the gate. Wait for the queue to drain, then count.

**2. Elapsed is 50.58 h, not 45.44 h, on the same `etime` basis.** Stale by 5.14 h. Yesterday's report
was stale by 5.15 h. **That is systematic, not a slip**: you are reading `etime` at a liveness check and
then composing the report later without re-reading it. Re-read elapsed as the last thing before you
write the numbers, not the first.

**3. The end times still do not follow from the totals.** 60.3 h from 00:07:21 UTC on 31 October is
12:25 UTC, which is **06:25 CST**, not 11:24. 62.6 h is 08:43 CST, not 13:42. All three are about five
hours late, which is the same five hours as the staleness, so the totals and the end times are two
different uses of one stale number and they disagree with each other.

## The band is at risk, and this is the part to act on

To keep the total inside 6.5 d with phase 2 at 89.8 h, **phase 1 must finish under 66.2 h**.

Simulating the 11 queued complexes on 3 workers, with the in-flight trio closing at about 51.5 h:

| PC per complex | ratio to model | phase 1 | total | band |
|---|---|---|---|---|
| 222 min | 1.20x | 64.5 h | 6.43 d | inside |
| 245 min | 1.32x | 65.3 h | 6.46 d | inside |
| 268 min | 1.45x | 66.1 h | 6.49 d | inside, by 6 minutes |
| 280 min | 1.51x | 66.5 h | 6.51 d | **breach** |

**The breach point is PC at 272 min, which is 1.47x model. The worst ratio you have actually observed is
1.46x, on HMGCR.** Those are the same number to within two minutes per complex.

So the margin is not the 1.84x you reported. That figure inherited the stale elapsed. **If PC behaves
like HMGCR already behaved, this run lands on the 6.5 d boundary rather than inside it.** My scheduler
also packs longest-first, which is optimal, whereas the real queue is length-ordered shortest-first and
packs worse at the tail, so the true breach point is if anything below 1.47x.

Revised honest projection: **phase 1 ends 09:48 to 11:38 CST today, total 6.38 to 6.49 d.**

## What that does and does not mean

It is a cost estimate produced by amendment 3's re-fit rule, not a registered prediction under test, so
landing on or just past 6.5 d is a cost overrun and not a scientific failure. Nothing needs to change in
the run. **But the conclusion "I am not treating the band as at risk" should be withdrawn**, because the
next decision that leans on it will lean on a number that was five hours stale.

Your step 2 report should say the non-ACACB total came in near **2.65 to 2.73 d against amendment 3's
2.02 d, about 31 to 35% over**, rather than the 25% computed from 45.44 h. State it plainly; the
under-prediction in the tail is the most useful thing this run has produced about the cost model.

## The monitor

Re-arming was right and the reasoning was right: the 30 h cap would have expired before the end. The 22 h
replacement covers to about 18:30 CST, which still covers the corrected 09:48 to 11:38 CST window with
room. No change needed.

Nothing else moves: six-step handover with steps 1 and 2 gating, probe not reused, phase 2 at 8 x 11.23 h.
