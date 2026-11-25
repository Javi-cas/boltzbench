"""Secondary metric for v2 under the same 0.234 gap rule PLAN_V2.md carries over from v1. Mechanical port of
secondary_gap_rule.py.

Written 2026-11-06 before any v2 output was read, and hashed into V2_ANALYSIS.sha256 before first execution.

Deltas from secondary_gap_rule.py, both forced: paths (runs_v2/, benchmark_plan_v2.json, _v2 outputs), and
nothing else. Separate from analyze_v2.py, which it does not touch; results_summary_v2.json is not written.
Counts a decoy as beaten only where the regulator's affinity_pred_value lead exceeds 0.234 (affinity = log10
IC50, lower = tighter, so lead = decoy - regulator). p is against analyze_v2.py's own null: same seed, same
100,000 draws, and the same random stream (analyze_v2.py draws the p_binder null first, then the affinity
null, so the first draw is repeated and discarded). Also reports the count the amendment requires (pairs whose
lead over the nearest decoy exceeds 0.234) and, descriptively, how many regulators lie within 0.234 of their
nearest decoy in absolute terms. Writes results_secondary_gap_v2.json.
"""
import glob, json, os, numpy as np, pandas as pd
GAP = 0.234
HERE = os.path.dirname(os.path.abspath(__file__)); plan = json.load(open(f"{HERE}/benchmark_plan_v2.json"))
rows = []
for f in glob.glob(f"{HERE}/runs_v2/**/affinity_*.json", recursive=True):
    name = os.path.basename(f)[len("affinity_"):-5]; prot, lig, kind = name.split("__")
    rows.append(dict(protein=prot, ligand=lig, kind=kind, affinity=json.load(open(f)).get("affinity_pred_value")))
d = pd.DataFrame(rows); res = []
for prot, p in plan.items():
    for reg in p["regulators"]:
        s = d[(d.protein == prot) & ((d.ligand == reg) | (d.kind == "decoy"))]
        if reg not in set(s.ligand) or (s.kind == "decoy").sum() < 6: continue
        v = s.set_index("ligand").affinity; x = v[reg]; lead = v.drop(reg) - x        # > 0: regulator tighter
        res.append(dict(protein=prot, regulator=reg, beats_raw=float((lead > 0).mean()), beats_gap=float((lead > GAP).mean()),
                        lead_nearest=float(lead.min())))
r = pd.DataFrame(res)
rng = np.random.default_rng(20261023)
rng.integers(0, 7, size=(100000, len(r)))                                             # analyze_v2.py's p_binder draw
null = rng.integers(0, 7, size=(100000, len(r))).mean(1) / 6                           # analyze_v2.py's affinity draw
out = dict(pairs=int(len(r)), gap=GAP,
           mean_beats_decoys_raw=float(r.beats_raw.mean()), p_one_sided_raw=float((null >= r.beats_raw.mean()).mean()),
           mean_beats_decoys_gap=float(r.beats_gap.mean()), p_one_sided_gap=float((null >= r.beats_gap.mean()).mean()),
           pairs_meeting_bar=int((r.lead_nearest > GAP).sum()),
           regulators_within_gap_of_nearest_decoy=int((r.lead_nearest.abs() < GAP).sum()),
           per_pair=r.round(4).to_dict("records"))
json.dump(out, open(f"{HERE}/results_secondary_gap_v2.json", "w"), indent=1); print(json.dumps(out, indent=1))
