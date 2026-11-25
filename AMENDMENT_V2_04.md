# v2 amendment 4, 2026-10-31: three launcher decisions, taken mid-phase-1

Written while phase 1 runs (72 of 156 at 17:32 UTC). **No registered rule is altered and no result is
touched.** Like amendment 3, this file is deliberately **not** in `V2.sha256`; the manifest covers the
four files it covered at launch.

## 1. The ACACB probe result is NOT reused. Phase 2 re-runs all eight.

The configuration is not the objection. `AMENDMENT_V2_03.md` establishes that the probe's input was
**byte-identical to `inputs_v2/`** and that phase 2's `--workers 1 --min-len 2000` gives **"1x16 as the
probe was measured"**, at fp32. On configuration alone the artefact would be admissible.

**The objection is that the registered record already says it is not part of the result.** Amendment 3,
written before any main-queue run: *"The probe ran one ACACB decoy complex (3PG), byte-identical to
`inputs_v2/`, alone, so **no part of the registered result was produced**."* Promoting that artefact to a
registered data point now would make a sentence in the registered record false after the fact, and the
reason for doing it would be that we have since learned it saves 11.23 hours. That is post hoc
convenience, and this project does not spend its credibility at that exchange rate.

Two supporting reasons, neither sufficient alone. The probe's `runs_probe/summary.txt` carries a
known-corrupt field, `peak_sampled_rss_GB=0.0012`, garbage from the same watcher bug that suppressed the
probe's announcement for two days; an entry in the registered set should not need a footnote explaining
which of its own recorded fields to ignore. And the benchmark's claim is that every entry came from one
registered pipeline invocation under one manifest, which is worth more than 11.23 hours.

**Cost of the decision: 11.23 h on a run now projected at 5.3 days, so 3.1%.** `runs_probe/` is kept as
the feasibility evidence amendment 3 cites, and is not merged into `runs_v2/`.

## 2. `launch_v2.sh` is endorsed, and is a fourth provenance file

Copying rather than editing was correct, and it is the same reasoning amendment 3 gives for the runner:
*"v1's launcher is part of v1's provenance, and the paper reports v1 and v2 side by side, so v1 must
remain reproducible exactly as run."* `launch.sh` hardwires `python -u run_parallel.py`, so it could not
have launched v2; editing it in place would have cost v1's reproducibility for no gain. Four functional
lines differ (script name, log name, the live-runner guard, and `--phased` now refusing rather than
silently running v1's `queue_full_20261026.sh`), plus four comments. `launch.sh` untouched.

Flagging it as beyond the three authorized lines was the right call and the answer is yes. **Both copied
files, `run_parallel_v2.py` and `launch_v2.sh`, should be hashed into a manifest at phase 1's end**, when
neither is in use, so the v2 run has the same provenance guarantee v1 has.

## 3. The inert double-launch guard IS fixed, with a proof, between phase 1 and phase 2

`live_runner()` tests `"run_parallel.py" in <ps output>`. The string `"run_parallel_v2.py"` does not
contain it, so the runner will **not** refuse to start a second concurrent v2 process writing into the
same `runs_v2/`. Amendment 3's assurance does not cover this: it says the self-matching `pgrep` bug is
confined to the probe watcher and that `live_runner()` "cannot self-match", which is true and is a
different failure. This one is failure **to** match, and the rename created it.

**Authorized: change that one string**, to a pattern matching both names as `launch_v2.sh`'s guard
already does. Conditions:

- **Apply it between phase 1 and phase 2**, not during phase 1. Editing a module Python has already
  imported cannot disturb the running process, so the reason is not technical: it is that the fix should
  be verified against a file nobody is executing, and phase 2's launch is the first moment the guard
  matters.
- **Prove both transitions, as precondition 4 was proved.** Start a runner, attempt a second start, show
  it refuses; then show a single start still succeeds. A guard that refuses *every* start, by matching
  its own command line, is the failure mode on the other side, and the one the probe watcher already
  demonstrated on this machine.
- The docstring at lines 4 and 11 still saying `benchmark_plan.json` may be corrected in the same edit.
  Comments cannot affect a result, and leaving a wrong path in a deposited file is worse than touching it.

Until that fix lands, **launch only through `launch_v2.sh`**, whose `grep -qE 'run_parallel(_v2)?\.py'`
does match and would correctly refuse a phase 2 start while phase 1 is live.

## Progress, and a correction to a figure I gave

72 of 156 phase-1 complexes at 17:32 UTC, from a 00:07 UTC start: **14.5 min per complex** of wall
throughput at 3 workers, mean per-complex wall time 30.5 min, max 51 min. Phase 1 projects to **37.8 h
total**, ending about **13:50 UTC on 1 November**, which is **22% faster** than the 2.02 d in amendment 3.
Phase 2 at 8 x 11.23 h solo is 89.8 h. **Total about 5.3 days, ending about 07:40 UTC on 5 November**,
below the 5.5 to 6.5 band amendment 3 registered. The estimate was the output of outcome 3's re-fit rule
rather than a hypothesis under test, so running fast is not a deviation; it is recorded because the band
is on the record.

**Correction.** I earlier reported this run as "67 of 132" with completion "around 08:00 UTC tomorrow".
The denominator was wrong: I read 132 from `benchmark_plan_v2.json` (22 enzymes x 6) and missed that the
panel is **164** (32 + 132), split 156 in phase 1 and 8 in phase 2. The corrected figures are above.

**An operational note on checking liveness from the analysis container.** `pgrep` and
`ps -o command= -p <pid>` both return nothing useful from here, because the container's shell runs under
`--unshare-pid` and cannot see host processes. Both produced a false "runner not alive" today. **Liveness
is judged from the run log's mtime and its advancing OK count**, never from a process check made in the
container.
