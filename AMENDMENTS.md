# Amendments (benchmark_plan.json / PLAN.sha256 unchanged)

## 2026-10-24: run-time and device check, no benchmark comparison made
- CPU test on PRKAG1__AMP__true completed: 9,396 s (structure about 96 min, affinity about 60 min). 72 complexes at this rate is about 8 days.
- Apple GPU (MPS, --accelerator gpu) test on the same complex: about 2 min, but the prediction is not usable:
  CA RMSD to the CPU model 19.9 A, complex pLDDT 0.32 vs 0.77 on CPU, confidence 0.40 vs 0.80.
  MPS is therefore excluded as a device for this benchmark (numerical failure, judged on structure confidence and
  CPU agreement only; no decoy has been run, so no ranking was seen).
- Next: choose between CPU with reduced sampling, a smaller complex set, or an NVIDIA GPU; recorded here before running.

## 2026-10-24b: run on the Mac CPU in parallel (settings unchanged)
- Decision: keep the full plan on the Mac CPU. No change to inputs, complexes, Boltz version, sampling, or analysis.
- New runner `run_parallel.py` (sha256 fc3d787adc28fc414ae638146a7503d8b0e8a62ef705b9f876614036ad57010c) issues exactly
  run_all.py's command per complex, reuses each protein's MSA the same way, writes the same outputs, and only schedules
  up to N complexes at once (default 6, OMP threads = cores / N), longest proteins first. One Boltz process used about
  1.5 cores, so parallel runs should cut wall time without touching the method.
- Estimated wall time from the PRKAG1 test (331 aa, 2.6 h) scaled by protein length: roughly 3 to 4 days with 6 workers;
  PFKL (780 aa) is the slowest.

## 2026-10-25: Boltz-2 inference in fp32 instead of bf16-mixed (written 19:32 CDT = 00:32 UTC 26 Oct, before any fp32 run)
- Cause of the slow and apparently stalled CPU runs: boltz 2.0.3 hard-codes the Lightning precision for Boltz-2 at
  boltz/main.py:1118, `precision=32 if model == "boltz1" else "bf16-mixed"` (installed main.py sha256
  655e5b93a89cb31686778dcf98e6e19f2763e074319d589398b03156a8ccfc65). With torch 2.14.1 this CPU reports capability
  DEFAULT and has no bf16 kernels, so under bf16 autocast every matmul falls to PyTorch's generic single-threaded scalar
  path (stack samples: cpublas_gemm_impl, bf16_dot_with_fp32_arith). Measured on this Mac, 512x512 matmul, 4 threads:
  fp32 0.25 ms, bf16 90.9 ms, fp32 inputs under bf16 autocast 91.1 ms, about 360x. This is why every worker ran at about
  one core whatever its thread count, in all three runs.
- Change: Boltz-2 runs in full fp32 (`precision=32`, the value boltz 2.0.3 already uses for Boltz-1). This RAISES
  numerical precision; it does not lower it. torch.set_float32_matmul_precision("highest") (main.py:977) stays.
  The model's own fp32 safeguards are torch.autocast("cuda", enabled=False) blocks, which do nothing on CPU, so the bf16
  CPU run had even those sections in bf16; in fp32 every section is fp32.
- Method: line 1118 of the installed boltz/main.py is edited to `precision=32,`; the original file is kept as
  boltz/main.py.orig_2026-10-25 and the patched sha256 is recorded below once made. The single Trainer at main.py:1112
  serves both structure and affinity prediction, so this one line covers both.
- No prediction setting changes: same inputs, same boltz 2.0.3 and checkpoints, `--accelerator cpu`,
  `--diffusion_samples 1`, `--output_format pdb`, default recycling and sampling steps, same MSA handling, same
  analysis (analyze.py as hashed). MPS stays excluded (2026-10-24). Full 72 complexes, no subset
  (AMENDMENTS_PENDING.md and subset_2026-10-25.txt remain unapplied).
- State when made: one complex computed, PRKAG1__AMP__true (bf16; confidence 0.802, ligand_iptm 0.934,
  affinity_probability_binary 0.805; 9,396 s). It is discarded and recomputed in fp32. Its bf16 outputs are moved
  unchanged to runs_bf16_discarded/ as the record; its timing.tsv row (9396 s) is bf16. No decoy has completed, so no
  ranking has been seen. Partial runs (PRPS1 x2, six regulator complexes from 2026-10-24) produced no predictions;
  their MSAs and processed inputs do not depend on precision and are reused.
- Calibration before the queue: PRKAG1__AMP__true alone in fp32, one worker, all threads, on an otherwise idle machine,
  against the bf16 2.6 h. Stop rule fixed in advance: if boltz rejects precision=32 or the speedup is under about 5x,
  stop and report instead of working around it. The fp32 scores are checked only for sanity (not compared for ranking).
- Patch made 2026-10-25 (before any fp32 run): main.py:1118 now `precision=32,`; patched sha256
  008ff45740b3ce67385757195014474b41b6d371d7e0c36403018e3184508441; original kept as main.py.orig_2026-10-25 (sha256
  655e5b93...). bf16 PRKAG1 outputs moved unchanged to runs_bf16_discarded/PRKAG1__AMP__true/.

## 2026-10-26: replicate variance measured; stop rule resolved against the primary metric; subset reconsidered
- Replicate of PRKAG1__AMP__true in fp32 (runs_measure/rep2) against the accepted run: affinity_pred_value
  0.1053 vs -0.1180 (d = 0.2233 log10), affinity_probability_binary 0.7603 vs 0.7889 (d = 0.0286),
  confidence 0.8578 vs 0.8605, ligand_iptm 0.9665 vs 0.9707. CA RMSD 5.01 A over 331 residues, 0.54 A over
  the 241 residues with pLDDT >= 0.8 in both; divergence confined to residues 1-20, 123-125, 270-272, 331.
  The two internal affinity models moved 0.487 -> -0.041 and -0.277 -> -0.196, disagreeing by 0.76 then 0.15.
- The pre-specified 0.10/0.25 stop rule was stated in log10 affinity units and therefore governs
  affinity_pred_value, which README.md fixes as the SECONDARY statistic. The PRIMARY statistic is the binder
  probability, which moved 0.0286. Recorded before any further run: the decision is taken on the primary
  metric, the structure is judged reproducible on the confident core, and the secondary metric is under
  suspicion pending a variance estimate.
- n = 2 gives a range and not a variance, so three further replicates (rep3-5) are run before the queue, and
  the decision on whether affinity_pred_value is reportable at diffusion_samples = 1 is deferred to that
  estimate. If its SD is large enough that run-to-run noise could reorder a regulator against its decoys, the
  plan will be amended to report the primary metric only, in writing and before any decoy score is opened.
- Throughput measured, three complexes, fp32: 1 x 16 sequentially 2,438 s (4.43 complexes/h, 19.8 GB peak);
  3 x 5 concurrently 1,242 s (8.70 complexes/h, 46.4 GB peak). 3 x 5 adopted. 4 x 4 not run, about 88 GB.
  Measured on 318-338 aa proteins only.
- Consequence for AMENDMENTS_PENDING.md: that draft reduced the benchmark to 3 regulator pairs because 72
  complexes was about 8 days under bf16, and it records the resulting power as 0.17/0.33/0.56 against
  0.48/0.82/0.98 for 12 pairs. The fp32 fix removes that constraint for the small proteins. The draft is
  therefore NOT applied pending one measurement, PFKL (780 aa) alone, which decides whether the long
  proteins are feasible and at what worker count. No complex has been dropped and no decoy score opened.
- No decoy output has been inspected beyond wall time and RSS. runs/ and runs_bf16_discarded/ unchanged.

## 2026-10-26b: replicate variance resolved; full plan launched; secondary metric given a pre-specified discount rule
- Five fp32 replicates of PRKAG1__AMP__true: affinity_probability_binary (PRIMARY) mean 0.7726, SD 0.0140,
  range 0.030. affinity_pred_value (SECONDARY) mean -0.0931, SD 0.1170, range 0.293. The secondary's spread
  is driven by boltz's internal model 1 (SD 0.2354) and run1 is its high outlier at +0.487 against -0.087
  to +0.036 for the other four; model 2 is comparatively stable (SD 0.0958). Confidence 0.8582 (SD 0.0044)
  and ligand_iptm 0.9668 (SD 0.0028). CA RMSD to run1 over residues with pLDDT >= 0.8 in both: 0.54, 0.99,
  0.90, 0.54 A, so the confident core reproduces within 1 A every time; whole-chain values of 2.1 to 14.5 A
  are the flexible N-terminus.
- PRIMARY is fit for purpose at diffusion_samples = 1 and carries the benchmark.
- SECONDARY is retained as pre-registered rather than dropped, with this rule fixed before any decoy score
  is seen: **the per-pair secondary result is reported but treated as uninformative unless that pair's
  regulator-to-decoy gap in affinity_pred_value exceeds 0.234, which is twice the measured run-to-run SD.**
  The number of pairs meeting that bar is reported alongside the secondary aggregate. If none do, the
  secondary is reported as uninformative at this sampling depth and no claim is made from it.
- PRKAG1__AMP__true keeps its run1 value, because every complex in the plan gets exactly one run at
  diffusion_samples = 1 and substituting a different draw for one complex alone would be inconsistent. That
  run is disclosed as the high outlier of five draws on the secondary metric; its primary value (0.7603)
  sits inside the five-run range.
- Full 72 confirmed feasible: PFKL (780 aa, the longest) 2,865 s and 23.3 GB alone at 16 threads; peak RSS
  fits 15.3 GB + 13.1e-6 x L^2, so 3 workers fit every protein in the plan within about 90 GB. Estimated
  total about 29 h. AMENDMENTS_PENDING's reduced complex set is therefore NOT applied, and no complex is
  dropped.
