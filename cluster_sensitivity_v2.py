"""Clustering sensitivity for v2. REPORTING ONLY: it does not replace the registered statistic.

Declared and hashed 2026-11-06, BEFORE analyze_v2.py was executed and before any v2 output was read.
Reason, stated in advance: v2's 32 regulator pairs come from 22 enzymes, not 32 (PFKP 4, OGDH 3, PPAT 3,
ACACB 2, CS 2, PDHA1 2, the other 16 one each). The registered null treats the 32 pairs as independent
draws, so if an enzyme's regulators share a failure or success mode the effective n is nearer 22 and the
registered p is optimistic. This quantifies that; it does not adjudicate it. PLAN_V2.md's statistic stands
as written and is reported by analyze_v2.py.

Statistic: the share of decoys beaten is averaged WITHIN each enzyme first, then across enzymes, so every
enzyme carries equal weight regardless of how many regulators it contributed.

Null: for each enzyme with k regulators, draw k ranks uniform among 7, average within the enzyme, then
average across enzymes, which reproduces the panel's own k per enzyme rather than assuming one each.
200,000 draws, seed 20261106 (new null shape, so a new seed, documented rather than reused). The critical
value is the 95th percentile of that null, the same method that reproduces PLAN_V2.md's power table.

Same inputs and same per-pair quantities as analyze_v2.py: runs_v2/, benchmark_plan_v2.json, binder
probability primary, predicted affinity secondary (lower = tighter), six decoys required.
Writes results_cluster_sensitivity_v2.json. Touches no other output.
"""
import glob, json, os, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(f"{HERE}/benchmark_plan_v2.json"))

rows = []
for f in glob.glob(f"{HERE}/runs_v2/**/affinity_*.json", recursive=True):
    name = os.path.basename(f)[len("affinity_"):-5]; prot, lig, kind = name.split("__")
    a = json.load(open(f))
    rows.append(dict(protein=prot, ligand=lig, kind=kind, p_binder=a.get("affinity_probability_binary"),
                     affinity=a.get("affinity_pred_value")))
d = pd.DataFrame(rows)

res = []
for prot, p in plan.items():
    for reg in p["regulators"]:
        s = d[(d.protein == prot) & ((d.ligand == reg) | (d.kind == "decoy"))]
        if reg not in set(s.ligand) or (s.kind == "decoy").sum() < 6: continue
        for metric, better_high in (("p_binder", True), ("affinity", False)):
            v = s.set_index("ligand")[metric]; x = v[reg]; dec = v.drop(reg)
            res.append(dict(protein=prot, regulator=reg, metric=metric,
                            beats_decoys=float(((dec < x) if better_high else (dec > x)).mean())))
r = pd.DataFrame(res)

out = {}
for metric in ("p_binder", "affinity"):
    m = r[r.metric == metric]
    if m.empty: continue
    per_enzyme = m.groupby("protein").beats_decoys.mean()
    counts = m.groupby("protein").size().reindex(per_enzyme.index).to_numpy()
    obs = float(per_enzyme.mean())
    rng = np.random.default_rng(20261106)
    draws = [rng.integers(0, 7, size=(200000, int(k))).mean(1) / 6 for k in counts]
    null = np.mean(np.column_stack(draws), axis=1)
    out[metric] = dict(enzymes=int(len(per_enzyme)), pairs=int(len(m)),
                       mean_over_enzymes=obs, p_one_sided=float((null >= obs).mean()),
                       critical_value=float(np.quantile(null, 0.95)),
                       regulators_per_enzyme={k: int(v) for k, v in zip(per_enzyme.index, counts)},
                       per_enzyme={k: round(float(v), 4) for k, v in per_enzyme.items()})
json.dump(out, open(f"{HERE}/results_cluster_sensitivity_v2.json", "w"), indent=1); print(json.dumps(out, indent=1))
