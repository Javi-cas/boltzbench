# v2: three decisions, then the phase 1 to phase 2 handover

**Status, re-read from the machine at 16:37 UTC on 2 November, replacing the stale header this
file carried until now.** Phase 1 is at **155 of 156, zero failures**. The last complex,
`PC__TRE__decoy`, started 14:09 UTC and is due about **17:58 UTC (11:58 CST) on 2 November**.

The numbers this file previously carried were from 31 October and are **wrong in the opposite
direction**. Correcting them, because step 2 asks you to report against amendment 3 and you would
otherwise be reconciling against a false baseline:

| | this file used to say | measured |
|---|---|---|
| progress | 72 of 156 | **155 of 156** |
| vs amendment 3's 2.02 d | 22% **faster** | **25.2% slower** |
| phase 1 end | 13:50 UTC 1 Nov | **~17:58 UTC 2 Nov** |
| phase 1 total | (implied ~1.6 d) | **60.67 h = 2.528 d** |
| run total | ~5.3 d | **~6.27 d**, inside the 5.5 to 6.5 band, near the top |

PC is measured, not bracketed: six complexes at 213.5 to 236.4 min, mean **229.5 min = 1.24x
model**. OGDH is **174.8 min over n=9 = 1.31x**. Nothing is at risk; the band holds on
measurement rather than on projection. Do not re-fit anything.

**Clock hazard, applies to every projection you report.** US DST ended **02:00 Sunday 1
November**: 31 October is CDT, 1 and 2 November are CST. Any interval computed by subtracting
local timestamps across that boundary **undercounts by exactly one hour**. Read elapsed from
`etime`, not from local-time subtraction, and label everything CST (UTC-6). This sits on top of
the existing UTC/CDT hazard and bites in the same place.

All three decisions are recorded in `AMENDMENT_V2_04.md`, which is on your machine and is deliberately
**not** in `V2.sha256`. Read it; the reasons matter more than the rulings.

## The three answers

**1. Do not reuse the probe. Phase 2 runs all eight ACACB complexes, including `ACACB__3PG__decoy`.**

Not because the configuration is wrong. Amendment 3 establishes the probe input was byte-identical to
`inputs_v2/` and that phase 2's flags give 1x16 exactly as the probe was measured. The objection is that
amendment 3 already states, in the registered record, *"no part of the registered result was produced"*
by the probe. Promoting it now would falsify that sentence after the fact, and the reason would be that
we have since learned it saves 11.23 h. Cost accepted: 3.1% of the run.

**Keep `runs_probe/` exactly where it is.** It is the feasibility evidence amendment 3 cites. Do not
merge, move or symlink it into `runs_v2/`.

**2. `launch_v2.sh` is endorsed. Flagging it was right.** Your reasoning was the same one amendment 3
gives for the runner: v1 must stay reproducible because the paper reports v1 and v2 side by side, and
`launch.sh` hardwires `run_parallel.py` so it could not have launched v2. Keep `launch.sh` untouched.

**3. The inert double-launch guard is authorized, with conditions.** Amendment 3's assurance covers
self-matching, which is a different failure; yours is failure to match, and the rename created it. Change
the one string to a pattern matching both names, as `launch_v2.sh` already does. Also correct the
docstring at lines 4 and 11 still saying `benchmark_plan.json`, in the same edit.

**Until that lands, launch only through `launch_v2.sh`.** Its guard does match and would correctly refuse
a phase 2 start while phase 1 is live.

## The handover, in this order, at phase 1's end

1. **Confirm phase 1 is actually complete.** 156 `OK` lines, and no non-zero return codes anywhere in
   `logs/run_parallel_v2_20261031_000721.log`. If any complex failed, stop and report before step 2:
   a silent gap is cheaper to fix now than after phase 2 spends 3.7 days.

2. **Verify the artefacts, not just the log.** Every one of the 156 should carry both
   `predictions/<name>/affinity_<name>.json` and `predictions/<name>/confidence_<name>_model_0.json`.
   Report the count of each and name any complex missing either. The log saying `OK` is not evidence the
   files landed.

3. **Apply the guard fix and the docstring correction**, now that nothing is executing the file.

4. **Prove both transitions, as you proved precondition 4.** Start a runner, attempt a second start, show
   it refuses. Then show a single start still succeeds. A guard that matches its own command line and
   refuses *every* start is the failure mode on the other side, and the probe watcher already
   demonstrated exactly that on this machine. Do not skip the second half of the proof.

5. **Hash both launcher copies into a manifest**, `run_parallel_v2.py` and `launch_v2.sh`, while neither
   is in use, so v2 has the provenance guarantee v1 has. A new file, e.g. `V2_LAUNCHERS.sha256`.
   **Do not add anything to `V2.sha256` or alter the four files it covers.**

6. **Idle window: run the CAR-T E19 cohort C job here, if it is being run at all.** Phase 1 is
   finished and phase 2 has not started, so the machine is free and no Boltz timing can be biased.
   Follow `~/scratch/cart/mac/PROMPT_e19_cohortC.md`. It is about an hour. **Declare the wall-clock
   cost and add it to the run total**, which is a clean declared delay rather than a contaminated
   measurement. If you would rather not spend the hour here, skip it: E19 has already failed its
   pass rule and cohort C only completes the registered report. **Never run it concurrently with
   phase 2**, which is a timing benchmark at 1x16 and would be biased by it.

7. **Launch phase 2 through `launch_v2.sh`**, `--workers 1 --min-len 2000`, expecting exactly 8 complexes.
   Verify the split returns 8 before launching, as you verified 156 before phase 1.

## Report

After step 2, and again after step 7: finished of 164, elapsed, projection, and any non-zero codes. In
the step 2 report include the measured non-ACACB total against amendment 3's 2.02 d, since that is now a
completed measurement rather than an estimate and belongs in the record.

If anything in steps 1 or 2 does not come out clean, **report and stop**. Phase 2 is 3.7 days and is not
worth starting on top of an incomplete phase 1.

## One thing not to spend time on

Do not try to recover the two days the probe's announcement was lost, or re-derive the probe's numbers.
Amendment 3 has them, they are accepted, and the only live question about the probe was reuse, answered
above.
