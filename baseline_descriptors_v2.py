"""POST-HOC descriptor baseline for v2. Written 2026-11-06 AFTER the registered result was known, and
labelled post-hoc for that reason. It is not part of PLAN_V2.md and does not alter the registered result.

Why: v2's regulators are mostly large phosphorylated nucleotides and cofactors while its decoys are
sugars, succinate, taurine and small phosphorylated three-carbon compounds. A reader is entitled to ask
whether a ranker that knows nothing about the protein reproduces Boltz-2's share. This computes exactly
that, with the same statistic, the same pairs and the same tie convention as analyze_v2.py (a tie counts
as NOT beaten).

Baselines, each a single number per ligand, highest first:
  mw            molecular weight from the CCD formula
  heavy_atoms   non-hydrogen atom count
  phosphorus    number of P atoms

Formulas come from v2_chem.json where the selection recorded them. The six decoy codes were not in that
file (it was built for regulators), so their PDB CCD formulas are listed here explicitly and are the only
hand-entered values in the script: 3PG C3H7O7P, G3P C3H9O6P, SUC C12H22O11, TRE C12H22O11, SIN C4H6O4,
TAU C2H7NO3S. Writes results_baseline_descriptors_v2.json.
"""
import glob, json, os, re, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(f"{HERE}/benchmark_plan_v2.json"))
chem = json.load(open(f"{HERE}/v2_chem.json"))

DECOY_FORMULA = {"3PG": "C3 H7 O7 P", "G3P": "C3 H9 O6 P", "SUC": "C12 H22 O11",
                 "TRE": "C12 H22 O11", "SIN": "C4 H6 O4", "TAU": "C2 H7 N O3 S"}
MASS = {"C": 12.011, "H": 1.008, "N": 14.007, "O": 15.999, "P": 30.974, "S": 32.06}

formula = dict(DECOY_FORMULA)
for v in chem.values():
    for a in v.get("anchors", []):
        if a.get("ccd") and a.get("formula"):
            formula.setdefault(a["ccd"], a["formula"])

def desc(f):
    at = {}
    for el, n in re.findall(r"([A-Z][a-z]?)\s*(\d*)", f):
        if el: at[el] = at.get(el, 0) + (int(n) if n else 1)
    return dict(mw=sum(MASS.get(e, 0) * n for e, n in at.items()),
                heavy_atoms=sum(n for e, n in at.items() if e != "H"),
                phosphorus=at.get("P", 0))

D = {k: desc(v) for k, v in formula.items()}
missing = sorted({l for p in plan.values() for l in p["regulators"] + p["decoys"]} - set(D))
if missing:
    raise SystemExit(f"no formula for: {missing}")

out, per = {}, []
for metric in ("mw", "heavy_atoms", "phosphorus"):
    fr = []
    for prot, p in plan.items():
        for reg in p["regulators"]:
            x = D[reg][metric]; dec = np.array([D[l][metric] for l in p["decoys"]])
            f = float((dec < x).mean())                      # higher is better; ties are NOT beaten
            fr.append(f)
            if metric == "mw": per.append(dict(protein=prot, regulator=reg, mw_beats=f))
    fr = np.array(fr); obs = float(fr.mean())
    rng = np.random.default_rng(20261023)
    null = rng.integers(0, 7, size=(100000, len(fr))).mean(1) / 6
    out[metric] = dict(pairs=int(len(fr)), mean_beats_decoys=obs, p_one_sided=float((null >= obs).mean()),
                       top1=int((fr == 1).sum()))
out["boltz_p_binder_for_comparison"] = json.load(open(f"{HERE}/results_summary_v2.json"))["p_binder"]["mean_beats_decoys"]
out["per_pair_mw"] = per
json.dump(out, open(f"{HERE}/results_baseline_descriptors_v2.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "per_pair_mw"}, indent=1))
