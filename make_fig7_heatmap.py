"""Figure 7: per-pair binder-probability difference, regulator minus each decoy.
Descriptive; computes no new statistic. Columns ordered heaviest decoy to lightest."""
import json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

BLUE, ORANGE, INK, MUTED, FAINT = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#b8b7b0"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "text.color": INK,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})

plan = json.load(open("benchmark_plan_v2.json"))
tab  = pd.read_csv("results_table_v2.csv")
bl   = json.load(open("results_baseline_descriptors_v2.json"))
hardset = {(r["protein"], r["regulator"]) for r in bl["per_pair_mw"] if r["mw_beats"] < 1.0}

MW   = {"SUC":342,"TRE":342,"3PG":186,"PEP":168,"G3P":172,"TAU":125,"SIN":118}
SLOT = ["SUC","TRE","3PG","G3P","TAU","SIN"]          # heaviest to lightest; PEP substitutes 3PG
NAME = {"SUC":"sucrose\n342 Da","TRE":"trehalose\n342 Da","3PG":"3PG / PEP\n186 / 168 Da",
        "G3P":"glycerol-3-P\n172 Da","TAU":"taurine\n125 Da","SIN":"succinate\n118 Da"}

rows, labels, hard = [], [], []
for prot, p in plan.items():
    s = tab[tab.protein == prot].set_index("ligand").p_binder
    for reg in p["regulators"]:
        d = {l: float(s[reg] - s[l]) for l in p["decoys"]}
        if "PEP" in d and "3PG" not in d: d["3PG"] = d.pop("PEP")   # same slot
        rows.append([d[k] for k in SLOT]); labels.append(f"{prot} / {reg}")
        hard.append((prot, reg) in hardset)
M = np.array(rows); order = np.argsort(M.mean(1))
M, labels, hard = M[order], [labels[i] for i in order], [hard[i] for i in order]

cmap = LinearSegmentedColormap.from_list("div", [ORANGE, "#f2f1ee", BLUE])
lim  = float(np.abs(M).max())
fig, ax = plt.subplots(figsize=(5.6, 8.4))
im = ax.imshow(M, cmap=cmap, norm=TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim), aspect="auto")
ax.set_xticks(range(len(SLOT))); ax.set_xticklabels([NAME[k] for k in SLOT], fontsize=7.5, color=MUTED)
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=7.5)
for t, h in zip(ax.get_yticklabels(), hard):
    t.set_color(ORANGE if h else MUTED)
ax.set_xticks(np.arange(-.5, len(SLOT), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
ax.grid(which="minor", color="white", lw=1.6); ax.tick_params(which="minor", length=0)
for s_ in ax.spines.values(): s_.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=.045, pad=.03)
cb.set_label("regulator minus decoy, binder probability", fontsize=8, color=MUTED)
cb.outline.set_visible(False); cb.ax.tick_params(labelsize=7.5, color=FAINT, labelcolor=MUTED)
ax.set_title("Blue = the regulator wins that cell", loc="left", fontsize=10.5, color=INK, pad=28)
ax.text(0, 1.012, "Rows sorted by mean difference; the eight pairs molecular weight cannot solve are labelled in orange",
        transform=ax.transAxes, fontsize=7.5, color=MUTED, va="bottom")
for ext in ("svg","png","pdf"):
    fig.savefig(f"figures_v2/f7_binder_heatmap.{ext}", bbox_inches="tight", dpi=200)
print("wrote f7_binder_heatmap; range %.3f to %.3f; cells negative: %d of %d"
      % (M.min(), M.max(), int((M < 0).sum()), M.size))
