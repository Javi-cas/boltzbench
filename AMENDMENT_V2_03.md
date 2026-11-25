# v2 amendment 3, 2026-10-31: the ACACB probe result, and the re-estimate it triggers

Written after the probe and **before any main-queue run**. No registered rule is altered. The probe ran
one ACACB **decoy** complex (3PG), byte-identical to `inputs_v2/`, alone, so no part of the registered
result was produced.

## The probe had already run, and the result was not lost

It started 2026-10-28 22:42 and finished 2026-10-29 09:56, exit 0. A watcher bug suppressed the
announcement for two days: two monitor loops poll `pgrep -f "boltz predict runs_probe"`, a pattern that
matches **their own command lines**, so each saw itself and never exited. The artefacts were complete
throughout. One line in `runs_probe/summary.txt`, `peak_sampled_rss_GB=0.0012`, is garbage from the same
bug; the 67.9 GiB maxrss is the real figure.

## The three numbers

| | |
|---|---|
| Peak RSS | **67.9 GiB** of 128 (footprint 76.0 GiB, 59% of RAM) |
| Wall clock | **11.23 h** (40,444 s) |
| Swapped | **No.** Swap grew 142 MB over 10.8 h of structure prediction; total swapins 50 MB |

## Memory: outcome 1, and the substitution branch is closed

The ~93 GB prediction over-shot by 37%, leaving 52 GiB of headroom. The contention premise is gone
independently: **fmbench is finished** (all three `.npz` complete, peak 15.1 GB, last activity Oct 26),
so it would have fitted regardless.

**ACACB runs. ACACA is not substituted. The panel stays at 32.** The ACACA branch written into the probe
instructions is closed unused, and the two ACACB pairs stay in.

Memory re-fits to `14.77 + 2.16e-4 * L^1.59` GiB across all three measured points, residual 0.03 GiB.
That slightly **lowers** mid-range predictions, so every worker count in the existing table stays valid.

## Time: outcome 3, and the registered rule is followed

The raw 40,444 s appears to sit inside the 22,593 to 50,997 s envelope, but **the envelope is on a 3x5
basis and the probe ran 1x16**. `measure_chain` calibrates the difference: PFKL at 780 aa took 2,865 s
solo-16 against the fit's 4,293 s, so solo-16 is **1.50x faster per complex**. On the fit's basis ACACB
is **60,607 s**, which is **2.68x the power law** and **1.19x above even the quadratic arm**. The
measurement lands above both.

Outcome 3's registered rule is to re-fit and re-estimate **before committing**, which is what follows.
A single power law cannot span the range: forcing one through both ends under-predicts v1's measured
318 aa point by half. The v1 fit is therefore kept at <= 780 aa where it was validated, and re-fitted
above it as `T = 9.17e-4 * L^2.306`. Costs: PC +43%, OGDH +26%, HMGCR +12%. Below 790 aa nothing changes.

**Revised estimate: ~6.0 days** (ACACB 3.74 d solo plus 2.02 d for the other 156 at 3 workers, x1.04),
band roughly 5.5 to 6.5, against 4.1 to 7.1 before. Non-ACACB work is 2.1 d and unchanged: essentially
all the movement is ACACB itself. **The 3.9-day power-law figure and the 4.1-day end of the range are
withdrawn.**

Nothing has been launched on the strength of this.

## Two operational items

**The monitor pattern must be fixed before the queue runs.** The same self-matching `pgrep` would break
monitoring on a six-day run exactly as silently as it did on an eleven-hour one, and on a six-day run
nobody would know the queue had finished or died.

**The sync gap that hid this amendment's predecessor.** `AMENDMENT_V2_02.md`, `V2.sha256` and
`RESULTS.md` were written together at 03:29:03 on 2026-10-29 in the analysis container and never copied
to the local machine, so the local `V2.sha256` covered three files instead of four and amendment 2
appeared not to exist. All four files verify against the container manifest. The registered record was
never lost, only unsynced, and the decisions amendment 2 carries (the Tanimoto cut failing, 164 inputs
over 224, the inflate/deflate correction, the 22-enzyme count) stand as hashed.

## Addendum, 2026-10-31: launcher wiring, resolved before launch

`run_parallel.py` as it stands is wired to v1 at three lines: `RUNS = f"{HERE}/runs"` (25),
`benchmark_plan.json` (37) and `inputs/*.yaml` (38). Launched unmodified it would re-run v1.

**It is not edited in place.** v1's launcher is part of v1's provenance, and the paper reports v1 and
v2 side by side, so v1 must remain reproducible exactly as run. A copy, `run_parallel_v2.py`, carries
the three path substitutions and nothing else, verified by a diff showing three changed lines.

Confirmed present before launch: `inputs_v2/` with exactly **164** yaml, `benchmark_plan_v2.json`, no
`runs_v2/`, and the fp32 patch intact at `boltz/main.py:1118` reading `precision=32` in a venv that was
not rebuilt since v1.

The run ordering needs no code change. Existing flags reproduce the measured bases exactly: phase 1
`--workers 3 --max-len 1200` gives 3x5 as v1 was measured, phase 2 `--workers 1 --min-len 2000` gives
1x16 as the probe was measured.

The self-matching `pgrep` bug is confined to the ad-hoc probe watcher. `run_parallel.py` holds its
children as `Popen` objects and checks a specific PID, so neither it nor `live_runner()` can self-match.
Monitoring goes through `logs/run_parallel.pid` and the run log, proved with a dummy job first.
