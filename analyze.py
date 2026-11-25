"""Pre-specified analysis (see README). Reads Boltz-2 affinity outputs under runs/."""
import glob, json, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); plan = json.load(open(f"{HERE}/benchmark_plan.json"))
rows = []
for f in glob.glob(f"{HERE}/runs/**/affinity_*.json", recursive=True):
    name = os.path.basename(f)[len("affinity_"):-5]; prot, lig, kind = name.split("__")
    a = json.load(open(f)); c = glob.glob(os.path.join(os.path.dirname(f), "confidence_*.json"))
    conf = json.load(open(c[0])) if c else {}
    rows.append(dict(protein=prot, ligand=lig, kind=kind, p_binder=a.get("affinity_probability_binary"),
                     affinity=a.get("affinity_pred_value"), ligand_iptm=conf.get("ligand_iptm"), iptm=conf.get("iptm")))
d = pd.DataFrame(rows); d.to_csv(f"{HERE}/results_table.csv", index=False)
res = []
for prot, p in plan.items():
    for reg in p["regulators"]:
        s = d[(d.protein == prot) & ((d.ligand == reg) | (d.kind == "decoy"))]
        if reg not in set(s.ligand) or (s.kind == "decoy").sum() < 6: continue
        for metric, better_high in (("p_binder", True), ("affinity", False)):   # affinity = log10 IC50, lower = tighter
            v = s.set_index("ligand")[metric]; x = v[reg]; dec = v.drop(reg)
            frac = float(((dec < x) if better_high else (dec > x)).mean())     # share of decoys the regulator beats
            ph = dec[[l for l in dec.index if l in ("3PG", "G3P", "PEP", "R5P", "G6P")]]
            frac_ph = float(((ph < x) if better_high else (ph > x)).mean())
            res.append(dict(protein=prot, regulator=reg, metric=metric, beats_decoys=frac, beats_phosphorylated=frac_ph,
                            interface_site=("interface" in p["site"])))
r = pd.DataFrame(res); r.to_csv(f"{HERE}/results_ranks.csv", index=False)
rng = np.random.default_rng(20261023); out = {}
for metric in ("p_binder", "affinity"):
    m = r[r.metric == metric]
    if m.empty: continue
    obs = m.beats_decoys.mean()
    null = rng.integers(0, 7, size=(100000, len(m))).mean(1) / 6     # regulator's rank uniform among 7
    out[metric] = dict(pairs=int(len(m)), mean_beats_decoys=float(obs), p_one_sided=float((null >= obs).mean()),
                       top1=int((m.beats_decoys == 1).sum()), mean_beats_phosphorylated=float(m.beats_phosphorylated.mean()),
                       single_chain_sites=float(m[~m.interface_site].beats_decoys.mean()),
                       interface_sites=float(m[m.interface_site].beats_decoys.mean()) if m.interface_site.any() else None)
json.dump(out, open(f"{HERE}/results_summary.json", "w"), indent=1); print(json.dumps(out, indent=1))
