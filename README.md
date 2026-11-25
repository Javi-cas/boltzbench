# boltzbench: does Boltz-2 know which metabolites regulate which human enzymes?

A CPU-only benchmark of whether the open structure-and-affinity model **Boltz-2** ranks a human metabolic
enzyme's known allosteric regulator above six decoys. The analysis plan was written and hashed before any
prediction was run, in both rounds.

**The headline is a negative, and it is the point of the repository.** The registered test passes. A baseline
with no protein, no structure and no model then beats it.

## Result

| Round | Panel | Regulator's mean share of decoys beaten | Chance | p |
|---|---|---|---|---|
| v1 | 12 pairs, 10 enzymes | 0.833 (binder probability) | 0.653 | 0.00024 |
| v2 | 32 pairs, 22 enzymes, no co-structure in the PDB and no binding measurement in ChEMBL or BindingDB | 0.766 (binder probability), 0.839 (predicted affinity) | 0.599 | below 1e-5 |

Then the post-hoc checks:

- **Molecular weight alone scores 0.854**, and heavy-atom count 0.823. Both beat Boltz-2 on the same panel.
- **Splitting on that baseline:** on the 24 pairs where weight already ranks the regulator first, Boltz-2
  scores 0.826. On the 8 pairs where weight fails, it scores 0.583 on binder probability (p = 0.27) and
  0.479 on predicted affinity, at or below chance.
- **A literature audit of the panel** found that 14 of the 32 regulations do not hold as labelled
  (`LABEL_AUDIT_2026-11-07.md`).

The registered result stands exactly as registered. What fails is the inference drawn from it: the
uniform-rank null holds chance constant while letting molecular size vary, so it is the wrong null for the
scientific question. A fixed analysis plan protected the statistic and the null; it did not protect the decoy
panel or the labels, and no amount of pre-specification would have.

## What is here

| File | Contents |
|---|---|
| `PLAN_V1_README.md` | The v1 plan, written before any prediction |
| `PLAN_V2.md`, `CANDIDATES_V2.md`, `AMENDMENT_V2_*.md` | The v2 plan and its amendments, hashed before pair selection |
| `PLAN.sha256`, `V2.sha256`, `V2_ANALYSIS.sha256` | Hashes of the plans and analysis code |
| `RESULTS.md` | The v1 result |
| `BOLTZBENCH_V2_REPORT.md` | The v2 result, the baseline that dissolves it, and the decomposition |
| `LABEL_AUDIT_2026-11-07.md` | Per-pair audit of the regulatory claims in the panel |
| `POWER_NOTE.md` | Power and the verdict rule, fixed in advance |
| `manuscript.md` | Preprint draft |
| `run_all.py`, `analyze.py`, `*_v2.py` | Prediction driver and the analysis scripts |
| `benchmark_plan*.json`, `inputs*/` | The panels and model inputs |
| `results_*.csv`, `results_*.json`, `figures*/` | Derived scores and figures |

Raw Boltz-2 outputs (about 2 GB per round) are not in the repository; the per-pair scores derived from them
are, in `results_ranks*.csv` and `results_table*.csv`.

**Verifying the v1 plan hash.** `PLAN.sha256` hashes the v1 plan under its original filename `README.md`.
That file is preserved byte for byte as `PLAN_V1_README.md`, so
`shasum -a 256 PLAN_V1_README.md` reproduces the first line of `PLAN.sha256`.

## Reproducing

    python3 -m venv .venv && source .venv/bin/activate     # Python 3.10 to 3.12
    pip install -r requirements.txt
    python run_all.py --only PRKAG1__AMP__true             # one complex; first run downloads about 6.2 GB
    python run_all.py                                      # the full panel, resumable
    python analyze.py

The full v2 panel ran on a laptop CPU. Boltz loads its checkpoints as Python pickles, from the Boltz
authors' Hugging Face repository (`boltz-community/boltz-2`).

## Licence

Code MIT (see `LICENSE`). Boltz-2 is the Boltz authors' work under its own licence; the enzyme and
metabolite annotations come from the cited literature and from UniProt, ChEMBL, BindingDB and the PDB.
