"""Pre-specified analysis for v2 (PLAN_V2.md). Mechanical port of analyze.py; same statistic, same metrics.

Written 2026-11-06 after phase 2 finished but BEFORE any v2 output was read, and hashed into
V2_ANALYSIS.sha256 before first execution, so the record shows it was not tuned to the result.

Deltas from analyze.py, all four forced rather than chosen, and nothing else differs:
 1. Paths: runs_v2/ and benchmark_plan_v2.json; outputs carry the _v2 suffix. analyze.py is untouched
    and v1's outputs are not overwritten, because the paper reports v1 and v2 side by side.
 2. The interface vs single-chain breakdown is DROPPED. benchmark_plan_v2.json records no "site" field
    (v1's plan did), so that split cannot be computed for v2 from the registered artefacts. It is not
    recovered from any post-hoc source.
 3. MSA depth per target is ADDED, because PLAN_V2.md registers it: "MSA depth is recorded per target
    and reported with the result." Depth = len(sequences) in the run's own processed/msa npz. It is
    reported only; it enters no statistic.
 4. The critical value at the realised number of pairs is reported, by the method that produced
    PLAN_V2.md's power table (200,000 draws, 95th percentile of the null mean). _verify_table() below
    reproduces the six published rows and raises if any differs, which is the proof that this is that
    method and not a new one. The table stops at 20 pairs; v2's panel is larger.

Unchanged: primary metric binder probability, secondary predicted affinity (lower = tighter), the
phosphorylated-decoy subset list, the >= 6 decoy requirement, and the p-value null (100,000 draws,
seed 20261023, p_binder stream drawn first).
"""
import glob, json, os, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(f"{HERE}/benchmark_plan_v2.json"))

def _crit(n, draws=200000, seed=20261028):
    return float(np.quantile(np.random.default_rng(seed).integers(0, 7, size=(draws, n)).mean(1) / 6, 0.95))

def _verify_table():
    """PLAN_V2.md's published critical values. Raises if this method does not reproduce them."""
    for n, v in ((6, 0.722), (8, 0.688), (10, 0.667), (12, 0.653), (15, 0.644), (20, 0.625)):
        got = _crit(n)
        if abs(got - v) > 0.001:
            raise SystemExit(f"critical-value method does not reproduce PLAN_V2.md at n={n}: {got:.4f} vs {v}")
_verify_table()

def _msa_depth(run_dir):
    f = glob.glob(os.path.join(run_dir, "**", "processed", "msa", "*_0.npz"), recursive=True)
    if not f:
        return None
    return int(len(np.load(f[0], allow_pickle=True)["sequences"]))

rows, depth = [], {}
for f in glob.glob(f"{HERE}/runs_v2/**/affinity_*.json", recursive=True):
    name = os.path.basename(f)[len("affinity_"):-5]; prot, lig, kind = name.split("__")
    a = json.load(open(f)); c = glob.glob(os.path.join(os.path.dirname(f), "confidence_*.json"))
    conf = json.load(open(c[0])) if c else {}
    rows.append(dict(protein=prot, ligand=lig, kind=kind, p_binder=a.get("affinity_probability_binary"),
                     affinity=a.get("affinity_pred_value"), ligand_iptm=conf.get("ligand_iptm"), iptm=conf.get("iptm")))
    if prot not in depth:
        d = _msa_depth(os.path.join(f"{HERE}/runs_v2", name))
        if d is not None:
            depth[prot] = d
d = pd.DataFrame(rows); d.to_csv(f"{HERE}/results_table_v2.csv", index=False)

res = []
for prot, p in plan.items():
    for reg in p["regulators"]:
        s = d[(d.protein == prot) & ((d.ligand == reg) | (d.kind == "decoy"))]
        if reg not in set(s.ligand) or (s.kind == "decoy").sum() < 6: continue
        for metric, better_high in (("p_binder", True), ("affinity", False)):   # affinity = log10 IC50, lower = tighter
            v = s.set_index("ligand")[metric]; x = v[reg]; dec = v.drop(reg)
            frac = float(((dec < x) if better_high else (dec > x)).mean())      # share of decoys the regulator beats
            ph = dec[[l for l in dec.index if l in ("3PG", "G3P", "PEP", "R5P", "G6P")]]
            frac_ph = float(((ph < x) if better_high else (ph > x)).mean())
            res.append(dict(protein=prot, regulator=reg, metric=metric, beats_decoys=frac,
                            beats_phosphorylated=frac_ph, msa_depth=depth.get(prot)))
r = pd.DataFrame(res); r.to_csv(f"{HERE}/results_ranks_v2.csv", index=False)

rng = np.random.default_rng(20261023); out = {}
for metric in ("p_binder", "affinity"):
    m = r[r.metric == metric]
    if m.empty: continue
    obs = m.beats_decoys.mean()
    null = rng.integers(0, 7, size=(100000, len(m))).mean(1) / 6     # regulator's rank uniform among 7
    out[metric] = dict(pairs=int(len(m)), mean_beats_decoys=float(obs), p_one_sided=float((null >= obs).mean()),
                       critical_value=_crit(len(m)), top1=int((m.beats_decoys == 1).sum()),
                       mean_beats_phosphorylated=float(m.beats_phosphorylated.mean()))
out["msa_depth_by_target"] = {k: depth[k] for k in sorted(depth)}
json.dump(out, open(f"{HERE}/results_summary_v2.json", "w"), indent=1); print(json.dumps(out, indent=1))
