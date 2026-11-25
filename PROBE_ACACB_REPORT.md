# ACACB probe: result, and what it changes

The probe **had already been run** before this session: it started 2026-10-28 22:42:07 CDT and
finished 2026-10-29 09:56:11 CDT, exit 0. I did not re-run it — an 11-hour re-run would reproduce the
same number — so this report reads the existing artefacts in `runs_probe/`. Nothing was launched in
this session, and `runs_v2/` still does not exist.

Provenance checks, all passing:

- The complex is `ACACB__3PG__decoy`, a **decoy**. No regulator complex was run, so no part of the
  registered v2 result exists. Output is in `runs_probe/`, outside `runs/` and `runs_v2/`.
- `runs_probe/ACACB__3PG__decoy.yaml` is byte-identical to `inputs_v2/ACACB__3PG__decoy.yaml`
  (sha256 `f38f499b…c3f33`), 2458 aa, ligand CCD 3PG, affinity on L.
- `shasum -a 256 -c V2.sha256` passes. No registered file was touched.
- It ran **alone**. The only things modified in `boltzbench` during the window were the probe's own
  files; nothing in `fmbench` was touched at all, and no other boltz, python or measurement job was
  running. An earlier launch at 22:41 refused itself correctly (`refusing: nice 5`).

## The three numbers asked for

| | value |
|---|---|
| **Peak RSS** | **67.9 GiB** (72.9 GB decimal) of 128 GiB |
| peak memory footprint | 76.0 GiB (81.6 GB) — 59% of RAM |
| **Wall clock** | **40,444 s = 11.23 h** (structure 11:06:00, affinity 6:38, MSA fetch < 1 min) |
| **Did it swap?** | **Not during the compute.** See below. |

Peak RSS and footprint are from `/usr/bin/time -l`. **Ignore the `peak_sampled_rss_GB=0.0012` line in
`runs_probe/summary.txt`**: the sampler in `probe_acacb.sh` matched on `boltz predict $root/$n.yaml`,
which never matched the real argv, so `peak_rss_kb` holds garbage (1280). A replacement sampler
(`sample2.log`) worked and recorded a 15-second-polled peak of 62.56 GiB, consistent with and below
the authoritative 67.9 GiB maxrss.

### Swap, in detail

- Baseline was already 7,073 MB used, from 26 days of uptime — not caused by the probe.
- Through the **entire 10.8 h of structure prediction** (22:42 → 09:31) swap went 7,073 → 7,215 MB.
  **Growth of 142 MB.** Effectively zero.
- Between 09:37 and 09:47 it rose to 10,147 MB, a ~2.9 GB burst, while boltz was tearing down the
  structure model and loading the affinity model (RSS was falling, 43 → 7.7 GiB, through that window).
  A transient at a phase boundary, not sustained pressure.
- **Swapins over the whole run: 3,097 pages = 50 MB.** Page-ins are the thrashing indicator, and
  50 MB in 11 hours is nothing. Swapouts were 198,764 pages = 3.26 GB, i.e. the OS evicting cold
  pages (idle Electron, Dropbox) to make room, which is the system working correctly.
- The 40 GB guard never came close to tripping.

## Outcome: memory passes, time does not

**Memory: outcome 1, comfortably.** The prediction was ~93 GB for a single ACACB process, and the
report said to treat it as an order of magnitude. It over-predicted by 37%. Measured 67.9 GiB leaves
**52 GiB of headroom**. For the record, fmbench's measured peak was 15.1 GB
(`fmbench/logs/mem_fmbench_1025.tsv`), so it would have fitted in that headroom anyway — and it is
finished: `emb_R1/R2/R3.npz` all exist with all seven cell lines at 512/768/2058 dims, and
`fmbench/AMENDMENTS_PENDING.md` has no open items. **The contention premise no longer applies.**

So **ACACB runs.** No substitution is needed, the ACACA question is moot, and the panel stays at
32 pairs. Nothing is dropped.

The memory model re-fits well with the new point. `15.5 + 1.28e-5*L^2` was too steep; through all
three measured maxrss values (331 aa 16.96, 780 aa 23.31, 2458 aa 67.91 GiB):

**RSS = 14.77 + 2.16e-4 * L^1.59 GiB**, max residual 0.03 GiB.

This *lowers* the mid-range predictions slightly (PC 1178 aa: 33.3 → 31.3 GiB), so every
memory-aware worker count in the cost table stays valid or improves.

**Time: outcome 3. The fit needs re-fitting, and the optimistic arm is dead.**

The raw 40,444 s sits inside the reported 22,593–50,997 s envelope, which looks like a pass. It is
not, because the envelope was built on a **3 workers × 5 threads** basis and the probe ran **1 worker
× 16 threads**. Correcting for that is what changes the answer.

The thread-scaling factor is measurable, from `logs/measure_chain_20261026.log`:

- PRKAG1, 331 aa, 3×5: measured 1,259 s vs the fit's 1,242 s — ratio 1.014. The fit is accurate on
  its own basis.
- PFKL, 780 aa, solo 16-thread: 2,865 s vs the fit's 4,293 s at 780 aa — **solo-16 is 1.50× faster
  per complex** than 3×5.

So ACACB's 40,444 s solo becomes **60,607 s on the fit's basis**:

| | s/complex at 2458 aa | measured vs predicted |
|---|---|---|
| power law `0.2805*L^1.447` | 22,593 | **2.68× too low** |
| quadratic arm | 50,997 | **1.19× too low** |
| measured (3×5 basis) | **60,607** | — |

The measurement lands **above both arms**. The 3.9-day power-law figure, and with it the 4.1-day end
of the 4.1–7.1 day range, is excluded. A single power law cannot span the whole range: forcing one
through the low end and ACACB under-predicts v1's measured 318 aa point by half, so the curve is
convex in log-log, as an O(L²)–O(L³) pair-representation cost would be.

Re-fitted above 780 aa, anchored on the two solid points (780 aa, 4,293 s) and (2458 aa, 60,607 s):

**T = 9.17e-4 * L^2.306 s** (3×5 basis), used only for L > 780; the v1 power law is kept at or below
780 aa where it was validated to 4.3% median error.

| enzyme | len | old s/cplx | re-fitted | change | complexes |
|---|---|---|---|---|---|
| PC | 1178 | 7,794 | 11,111 | +43% | 7 |
| OGDH | 1023 | 6,355 | 8,025 | +26% | 9 |
| HMGCR | 888 | 5,178 | 5,790 | +12% | 7 |
| RRM1 | 792 | 4,388 | 4,447 | +1% | 7 |
| PFKP | 784 | 4,324 | 4,344 | 0% | 10 |

### Re-estimate

| block | cost | wall clock |
|---|---|---|
| ACACB, 8 complexes solo at 11.23 h | 89.9 cpu-h | 3.74 d |
| the other 156 complexes, 3 workers | 145.4 cpu-slot h (was 133.3) | 2.02 d |
| × 1.04 realisation | | **6.0 days** |
| if the probe's completed complex is reused | | 5.5 days |

**Revised: ~6.0 days, with a plausible band of 5.5 to 6.5**, against 4.1–7.1 before. The range
narrows and shifts to its upper half. Non-ACACB alone is 2.1 days, still inside the earlier
2.0–2.2 d figure; essentially all of the change is ACACB.

## Two things for the user, neither acted on

1. **`AMENDMENT_V2_02.md` does not exist.** It is not in `boltzbench`, and a search of the whole home
   directory finds no file matching `*V2_02*` and no file containing the string. `V2.sha256` covers
   **three** files, not four — `CANDIDATES_V2.md`, `PLAN_V2.md`, `AMENDMENT_V2_01.md` — and all three
   verify. The decisions described as being recorded in it (the Tanimoto cut failing, 164 being right
   rather than 224, the inflate/deflate correction, the 22-enzyme correction) are currently recorded
   only in `V2_PREPARATION_REPORT.md`, which is **not** hashed. I have not written the file: it is the
   registered record of your decisions and I should not author it or re-hash `V2.sha256` for you.
2. **The probe's finished complex could be reused**, saving 11.2 h. The input is byte-identical to
   `inputs_v2/ACACB__3PG__decoy.yaml` and the command matches `run_parallel.py`, so reusing it changes
   nothing that is computed — but it was produced as a probe outside `runs_v2/`, so that is your call,
   not mine. Also worth knowing: with 52 GiB of headroom, two ~19 GiB enzymes could run alongside
   ACACB, though they would compete for cores with its 16 threads. Also not acted on.

**Nothing was launched. The main queue was not started and no regulator complex was run.**

## Postscript: two orphaned monitor loops, and why nothing reported back on 2026-10-29

No boltz process is running. But two zsh loops from the 2026-10-28 session are **still alive after
~2 days**, PIDs 77944 and 78853:

- 77944 is the replacement RSS sampler that wrote `sample2.log`.
- 78853 is a watcher meant to print `PROBE FINISHED` and `cat runs_probe/summary.txt` when boltz exited.

Both poll `pgrep -f "boltz predict runs_probe"`, and **that pattern matches their own command lines**,
so each one sees itself, concludes boltz is still running, and never exits. This is why the probe
finished at 09:56 on 2026-10-29 and **the watcher never announced it** — the result sat unreported for
a day. It also means `sample2.log` never got its final `peak_GB=` line; the 62.56 GiB figure above was
recovered by scanning the samples.

They are inert sleep loops, they write nothing further, and `runs_probe/summary.txt` is complete, so
nothing is lost. I have **not** killed them, since `CLAUDE.md` says not to stop the Boltz-2 job and I
would rather you confirm these two are not it (they are not — the job itself exited at 09:56 on
2026-10-29). To clear them: `kill 77944 78853`.

Worth fixing before the full queue runs, because the same bug would silently break its monitoring:
match on something the monitor's own argv cannot contain, e.g. `pgrep -f "[b]oltz predict runs_v2"`,
or track the child PID directly instead of by pattern.
