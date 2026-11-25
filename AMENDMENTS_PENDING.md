# Draft amendment, NOT yet in AMENDMENTS.md and not yet in force (awaiting the user's approval)

## 2026-10-25: reduced complex set chosen by compute cost; harness fixes (no benchmark output inspected)
- Observed rate: the six workers launched 2026-10-24 16:59 CDT (PFKL, CTPS1, GLUD1, PKM, PPAT, G6PD regulator complexes,
  515 to 780 aa) were still in structure prediction after 19.3 h, at about 1 core and about 11 GB RSS each, with swap
  at 13 of 14 GB. PRKAG1 (331 aa) took 2.6 h alone. All 72 complexes on this CPU is not feasible in a useful window.
- Criterion, fixed before any further prediction and using only input properties: keep every complex of each protein
  whose length in benchmark_plan.json is at most 400 aa. There is a natural gap from 338 aa to 514 aa, so the cut sits
  in it and no protein lies near the boundary. Result: PRPS1 (318), PRKAG1 (331), FBP1 (338); 3 regulator pairs
  (PRPS1+ADP, PRKAG1+AMP, FBP1+AMP), each with its full panel of 6 decoys, 21 complexes (3 true, 18 decoy), the same
  1:6 balance as the full plan. Whole proteins only, because analyze.py skips any pair with fewer than 6 decoys, and the
  phosphorylated-decoy contrast needs 3PG and G3P.
- Analysis unchanged: analyze.py as hashed in PLAN.sha256, run once after the subset is complete.
- Disclosed: the PRKAG1+AMP true complex finished on 2026-10-24 and its scores were seen (confidence 0.802,
  ligand_iptm 0.934, affinity_probability_binary 0.805). It is included because the length rule includes it, not
  because of its score. No decoy has been run, so no ranking has been seen.
- Power, stated in advance (null: regulator rank uniform among 7, one-sided alpha 0.05): with 3 pairs the mean share of
  decoys beaten must exceed 0.833 for p < 0.05 (all three top-1 gives p = 0.0029). If the model ranks the regulator
  first in a share q of pairs and is otherwise at chance, power is 0.17 / 0.33 / 0.56 for q = 0.3 / 0.5 / 0.7. With
  12 pairs it would be 0.48 / 0.82 / 0.98. This subset can detect only a strong effect; a null result is not evidence
  of no effect. Of the 3 pairs, 1 (PRPS1) is an interface site, so the within-chain vs interface split is 2 vs 1 and
  is descriptive only.
- Harness (run_parallel.py, previous version kept as run_parallel.py.2026-10-24b): prediction command unchanged
  (`--accelerator cpu --diffusion_samples 1 --output_format pdb`, MPS stays excluded per 2026-10-24). New `--subset FILE`
  (subset_2026-10-25.txt); default worker count now min(performance cores // 2, (RAM - 32 GB) // 12 GB) from sysctl,
  which is 8 on this Mac; 2 OMP threads per worker; timing.tsv rows fsynced as each complex finishes. Launched by
  launch.sh under nohup and caffeinate -is, log in logs/.
- sha256: run_parallel.py, launch.sh, and subset_2026-10-25.txt, filled in at approval time.
