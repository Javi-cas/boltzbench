# Correction to the 24 h checkpoint, 2026-11-01

Everything you measured directly is exact. Three derived figures are not, and they share one cause.

## Verified against the log, no change needed

- **111 of 156 in phase 1**, zero failures, zero non-zero return codes. A grep for fail, error,
  traceback and non-zero exits across the whole run log returns nothing.
- **70.75 cpu-slot hours** measured. Matches to the digit.
- **The model under-predicts by 7.4%** (70.75 against 65.9). Carrying it as an upper bound rather than
  re-fitting mid-run was the right call.
- **The tail is real and steeper than the mean suggests**: complexes 1 to 72 averaged 30.5 min, 73 to 111
  averaged **52.6 min**, maximum 90 (CPT1A__MLC__true). Nothing has stalled; CPT1A__SUC__decoy closed at
  05:02 UTC and CPT1A__G3P__decoy was still writing at 05:18 UTC.
- **Memory**: no reason to doubt it, and nothing in the log contradicts it.

## The clock is 5.2 hours stale, and two figures inherit it

**Elapsed is 29.19 h, not 24.0 h.** Start was 2026-10-31 00:07:21 UTC; the count of 111 is current as of
05:19 UTC on 1 November. Your `etime 1-00:02` places the liveness check at about 00:09 UTC, so the report
pairs a **current count** with a **five-hour-old clock**.

| figure | as reported | actual |
|---|---|---|
| elapsed | 24.00 h | **29.19 h** |
| throughput | 13.0 min/complex | **15.8 min/complex** (the report is 22% optimistic) |
| worker occupancy | 0.981 | **0.808** overall |
| realisation | 1.019 | **1.238** overall |

The occupancy figure is the one to discard. 70.75 slot-hours over 3 workers needs 23.58 h of wall if
perfectly packed; against 24.0 h that is 0.983, which is where 0.981 came from. Against the true 29.19 h
it is 0.808. The sign error you caught and corrected was real, but the corrected figure still rests on
the stale input, so it is wrong by a different route.

## Your phase 1 total is nonetheless right, and here is why

Overall occupancy of 0.808 is not the right input for the remaining tail, because the early loss was MSA
fetching serialising at the head of each enzyme. **In the recent stretch, complexes 73 to 111, occupancy
is 0.967** over 11.78 h of wall and 34.2 slot-hours. That is the figure the tail should be projected on.

Independent estimate, remaining 45 complexes at 0.967 occupancy across 3 workers:

| mean wall per complex | more hours | phase 1 total |
|---|---|---|
| 75 min | 19.4 | 48.6 h |
| **85 min** | **22.0** | **51.2 h** |
| 95 min | 24.6 | 53.8 h |

So your 51.0 h lands inside the range and close to the centre. **The answer is right; the working has two
errors that happened to cancel.** The optimistic throughput and the too-high occupancy pulled the
estimate down, and the 7.4% model under-prediction carried as an upper bound pulled it back. Worth fixing
rather than leaving, because at the next checkpoint they will not cancel.

## One further inconsistency, in the end time rather than the total

51.0 h from 00:07:21 UTC on 31 October gives **03:07 UTC on 2 November, which is 22:07 CDT on 1 November**.
The report states phase 1 ending "02:05 to 05:04 CDT on 2 November", which is 07:05 to 10:04 UTC and
therefore 55 to 58 h from the start, not 51. That looks like a UTC timestamp carried into a CDT label.

**This matters for the fallback.** A 30 h cap armed at about 00:09 UTC on 1 November expires at 06:09 UTC
on 2 November, which is 01:09 CDT. Against the true projected end of roughly 22:07 CDT on 1 November the
cap is comfortable. Against the end time the report states, the cap would fire **before** phase 1
finished. The cap is adequate, but only because the stated end time is wrong, so please recompute it from
the start timestamp in UTC and convert once, at the end.

## Nothing else changes

The six-step handover stands exactly as written, steps 1 and 2 gating. The step 2 report should give the
measured non-ACACB total against amendment 3's 2.02 d; on these numbers that lands near 2.13 d, about 5%
over, which is the same conclusion you reached. Phase 2 at 8 x 11.23 h is unchanged, and the probe is
still not reused.
