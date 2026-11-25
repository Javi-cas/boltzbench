# ACACB probe: result

One complex, `ACACB__3PG__decoy` (2458 aa, decoy ligand 3-phosphoglycerate). Not a regulator, so no part of
the registered result is produced. 1 worker x 16 threads, fp32 CPU, 1 diffusion sample, `--use_msa_server`,
nothing else computing on the machine. Started 2026-10-28 22:42:07 CDT, finished 2026-10-29 09:56:11 CDT,
exit 0. Output in `runs_probe/`, which is not `runs/` and not the eventual `runs_v2/`.

## The three numbers

| | measured |
|---|---|
| **peak RSS** | **67.9 GiB** maximum resident set size; **76.0 GiB** peak memory footprint |
| **wall clock** | **11.23 h** (40,444 s) |
| **swapped?** | **marginally.** `swaps 0`. Swap in use went 7.07 -> 10.15 GB, all of it in the last 15 minutes |

Peak memory footprint is the figure that matters for co-residency, since it counts compressed pages. On a
128 GB machine it leaves **46 GB** free at ACACB's worst moment.

The swap detail: swap in use was flat at 7.07-7.22 GB for 10.8 of the 11.2 hours, i.e. unchanged from the
pre-run baseline. The whole 2.9 GB rise happened between 09:33 and 09:47, during the affinity-prediction
stage, which the log times at 6:38. Across the full run 198,764 pages were written out, about 777 MB. The
guard threshold was baseline + 40 GB and was never approached. This is ordinary paging under pressure, not
thrashing, and it did not cost measurable time: the affinity stage ran at its expected length.

## Against the models

**Memory: the model over-predicted, and this comparison is clean.** `RSS = 15.5 + 1.28e-5 L^2` was fitted on
two 1x16 points (331 aa, 16.9 GB; 780 aa, 23.3 GB), so a 1x16 probe is like for like. It predicted 92.8 GB at
2458 aa against 72.9 GB measured maxrss (over by 27%) or 81.6 GB footprint (over by 14%). The extrapolation
was conservative in the safe direction.

**Time: the comparison is not clean and I am not going to pretend it is.** Both time fits were built on 70
fp32 **3x5** complexes. The probe ran **1x16**. The measurement, 11.23 h, falls between the power law's
6.28 h and the quadratic's 14.17 h, but that does not adjudicate between them, because no complex in
`timing.tsv` was run in both configurations. The only two 1x16 points sit at 1.39x and 0.67x of the power-law
prediction for their own lengths -- a 2x spread -- so the thread-scaling factor needed to convert the probe
to a 3x5 equivalent is itself unknown to within a factor of two. Any single conversion I quoted would be
invented.

## Why the estimate does not need that conversion

ACACB has to run at 1 worker x 16 threads in production, for memory. **The probe is ACACB's production
configuration.** So ACACB's contribution can be taken from the measurement directly and the fit dropped for
those 8 complexes:

| | wall clock |
|---|---|
| ACACB, 8 complexes, measured, exclusive | 8 x 11.23 h = **89.9 h = 3.74 days** |
| other 21 enzymes, 156 complexes, 3x5, still fitted | 44.6 h (power law) to 49.2 h (quadratic) |
| x1.04 for v1's measured scheduling realisation | |
| **total** | **5.8 to 6.0 days** |

Previously 4.1 to 7.1 days. The range narrows because the single largest uncertainty is now measured rather
than extrapolated, and it moves up because the power-law low end was too optimistic: ACACB was budgeted at
50.2 h and costs 89.9 h. **ACACB is 65-67% of the whole queue's wall clock for 8 of 164 complexes.**

Residual uncertainty is now concentrated in the other 21 enzymes, where six targets (PC 1178, OGDH 1023,
HMGCR 888, RRM1 792, PFKP 784, CPT1A 773 aa) are at or past the fit's 780 aa edge, and in whether 3 workers
can actually be held concurrently at those lengths -- the memory model says 3 x 33 GB for PC, which the
probe's 14-27% over-prediction would bring to roughly 3 x 26 GB, and that is tight against 46 GB of fmbench
headroom rather than comfortable.

## One caveat on the 8 x 11.23 h

The probe's ligand was 3PG, a 13-atom decoy. Of ACACB's 8 complexes, 6 are small decoys and 2 are the
regulators: citrate is also small, but **palmitoyl-CoA is about 65 heavy atoms** and may be slower than the
probe. 11.23 h each is therefore a floor for the regulator rows, not a guarantee. It would not change the
decision; it could add hours, not days.

## Which pre-declared outcome this is

On memory, outcome (a): comfortably under 128 GB, real headroom for fmbench, no thrash. ACACB can run, so
the ACACA substitution rule does not fire and the panel stays at 32.

On time, outcome (c) in form: the fit is not validated, and the re-estimate above is the re-estimate that
outcome called for. Nothing has been launched. `runs_v2/` does not exist.
