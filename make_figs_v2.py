"""Figures for the v2 report. Reads the written result files; computes no new statistic
except the descriptive decoy-win counts and the MW easy/hard split already in the report."""
import json, re, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, FAINT = "#0b0b0b", "#52514e", "#b8b7b0"
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": FAINT,
                     "axes.linewidth": 0.8, "xtick.color": MUTED, "ytick.color": MUTED,
                     "text.color": INK, "axes.labelcolor": MUTED, "figure.facecolor": "white",
                     "axes.facecolor": "white", "savefig.facecolor": "white"})

def finish(ax, xmax=1.0):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_xlim(0, xmax); ax.xaxis.grid(True, color="#ececea", lw=0.8); ax.set_axisbelow(True)

def save(fig, name):
    for ext in ("svg", "png", "pdf"):
        fig.savefig(f"figures_v2/{name}.{ext}", bbox_inches="tight", dpi=200)
    plt.close(fig); print("wrote", name)

v1 = json.load(open("results_summary.json")); v2 = json.load(open("results_summary_v2.json"))
bl = json.load(open("results_baseline_descriptors_v2.json"))
ranks = pd.read_csv("results_ranks_v2.csv"); tab = pd.read_csv("results_table_v2.csv")
plan = json.load(open("benchmark_plan_v2.json"))

# ---------------------------------------------------------------- F1 registered result
fig, ax = plt.subplots(figsize=(6.4, 2.5))
lab = ["v1  binder probability", "v1  predicted affinity", "v2  binder probability", "v2  predicted affinity"]
val = [v1["p_binder"]["mean_beats_decoys"], v1["affinity"]["mean_beats_decoys"],
       v2["p_binder"]["mean_beats_decoys"], v2["affinity"]["mean_beats_decoys"]]
col = [AQUA, AQUA, BLUE, BLUE]
y = np.arange(4)[::-1]
ax.barh(y, val, color=col, height=0.58)
ax.axvline(0.5, color=MUTED, lw=1, ls="--"); ax.text(0.5, 3.75, " chance", color=MUTED, fontsize=8, va="top")
for yy, v in zip(y, val): ax.text(v + 0.012, yy, f"{v:.3f}", va="center", fontsize=9, color=INK)
ax.set_yticks(y); ax.set_yticklabels(lab); ax.set_xlabel("mean share of decoys beaten")
finish(ax, 1.0)
ax.set_title("The registered result: v2 holds after removing exposure", loc="left", fontsize=10.5, color=INK, pad=10)
save(fig, "f1_primary")

# ---------------------------------------------------------------- F2 baselines
fig, ax = plt.subplots(figsize=(6.4, 2.8))
rows = [("molecular weight", bl["mw"]["mean_beats_decoys"], ORANGE),
        ("Boltz-2  predicted affinity", v2["affinity"]["mean_beats_decoys"], BLUE),
        ("heavy-atom count", bl["heavy_atoms"]["mean_beats_decoys"], ORANGE),
        ("Boltz-2  binder probability", v2["p_binder"]["mean_beats_decoys"], BLUE),
        ("phosphorus count", bl["phosphorus"]["mean_beats_decoys"], ORANGE)]
rows.sort(key=lambda r: r[1])
y = np.arange(len(rows))
ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.58)
tr = ax.get_xaxis_transform()
ax.axvline(0.5, color=MUTED, lw=1, ls="--"); ax.text(0.5, 0.02, " chance", color=MUTED, fontsize=8, transform=tr, va="bottom")
ax.axvline(0.599, color=MUTED, lw=1, ls=":"); ax.text(0.599, 0.02, " bar", color=MUTED, fontsize=8, transform=tr, va="bottom")
for yy, r in zip(y, rows): ax.text(r[1] + 0.012, yy, f"{r[1]:.3f}", va="center", fontsize=9, color=INK)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows]); ax.set_xlabel("mean share of decoys beaten")
finish(ax, 1.0)
h = [plt.Rectangle((0,0),1,1,color=BLUE), plt.Rectangle((0,0),1,1,color=ORANGE)]
ax.legend(h, ["Boltz-2", "descriptor baseline (no protein)"], frameon=False, fontsize=8.5,
          loc="lower right", bbox_to_anchor=(1.0, -0.42), ncol=2)
ax.set_title("Molecular weight alone outranks Boltz-2 on this panel", loc="left", fontsize=10.5, color=INK, pad=10)
save(fig, "f2_baselines")

# ---------------------------------------------------------------- F3 decomposition
mw = pd.DataFrame(bl["per_pair_mw"])
pb = ranks[ranks.metric=="p_binder"][["protein","regulator","beats_decoys"]].rename(columns={"beats_decoys":"pb"})
af = ranks[ranks.metric=="affinity"][["protein","regulator","beats_decoys"]].rename(columns={"beats_decoys":"af"})
m = mw.merge(pb, on=["protein","regulator"]).merge(af, on=["protein","regulator"])
easy, hard = m[m.mw_beats==1.0], m[m.mw_beats<1.0]
fig, ax = plt.subplots(figsize=(5.4, 2.9))
x = np.array([0, 1]); w = 0.33
ax.bar(x-w/2, [easy.pb.mean(), hard.pb.mean()], w, color=BLUE, label="binder probability")
ax.bar(x+w/2, [easy.af.mean(), hard.af.mean()], w, color=AQUA, label="predicted affinity")
ax.axhline(0.5, color=MUTED, lw=1, ls="--"); ax.text(1.52, 0.5, "chance", color=MUTED, fontsize=8, va="center")
for xx, vals in zip(x, ([easy.pb.mean(), easy.af.mean()], [hard.pb.mean(), hard.af.mean()])):
    for dx, v in zip((-w/2, w/2), vals): ax.text(xx+dx, v+0.02, f"{v:.3f}", ha="center", fontsize=8.5, color=INK)
ax.set_xticks(x); ax.set_xticklabels([f"weight already solves\n(n = {len(easy)})", f"weight fails\n(n = {len(hard)})"])
ax.set_ylabel("mean share of decoys beaten"); ax.set_ylim(0, 1.05)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.yaxis.grid(True, color="#ececea", lw=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
ax.set_title("Where weight fails, Boltz-2 is at chance", loc="left", fontsize=10.5, color=INK, pad=10)
save(fig, "f3_decomposition")

# ---------------------------------------------------------------- F4 per-pair scatter
fig, ax = plt.subplots(figsize=(5.2, 4.2))
rng = np.random.default_rng(7)
jx = m.mw_beats + rng.uniform(-.022,.022,len(m)); jy = m.pb + rng.uniform(-.022,.022,len(m))
ishard = (m.mw_beats < 1.0).to_numpy()
ax.scatter(jx[~ishard], jy[~ishard], s=46, color=BLUE, alpha=.85, edgecolor="white", lw=1, zorder=3, label="weight solves it")
ax.scatter(jx[ishard], jy[ishard], s=56, color=ORANGE, edgecolor="white", lw=1, zorder=4, label="weight fails")
placed = []
for (_, r), xx, yy in zip(m[ishard].iterrows(), jx[ishard], jy[ishard]):
    dy = -3
    while any(abs(xx-px) < .12 and abs((yy+dy/260.) - py) < .055 for px, py in placed):
        dy -= 11
    placed.append((xx, yy + dy/260.))
    arrow = dict(arrowstyle="-", color=FAINT, lw=0.7, shrinkA=0, shrinkB=4) if dy < -8 else None
    ax.annotate(f"{r.protein}/{r.regulator}", (xx, yy), textcoords="offset points", xytext=(7, dy),
                fontsize=7.5, color=MUTED, arrowprops=arrow)
ax.axhline(0.5, color=FAINT, lw=1, ls="--")
ax.set_xlabel("molecular-weight baseline, share of decoys beaten")
ax.set_ylabel("Boltz-2 binder probability, share beaten")
ax.set_xlim(-.07, 1.12); ax.set_ylim(-.07, 1.12)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.grid(True, color="#f0f0ee", lw=0.8); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
ax.set_title("Pair by pair, Boltz-2 tracks the size heuristic", loc="left", fontsize=10.5, color=INK, pad=10)
save(fig, "f4_scatter")

# ---------------------------------------------------------------- F5 ACACB
a = tab[tab.protein=="ACACB"].copy()
names = {"PKZ":"PKZ (regulator)","CIT":"citrate (regulator)","SIN":"succinate","SUC":"sucrose",
         "TAU":"taurine","TRE":"trehalose","3PG":"3-phosphoglycerate","G3P":"glycerol-3-P"}
fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9))
for ax_, col_, ttl, asc in ((axes[0], "p_binder", "binder probability", True),
                            (axes[1], "affinity", "predicted affinity (lower = tighter)", False)):
    s = a.sort_values(col_, ascending=asc)
    c = [ORANGE if k == "true" else FAINT for k in s.kind]
    ax_.barh(np.arange(len(s)), s[col_], color=c, height=.6)
    ax_.set_yticks(np.arange(len(s))); ax_.set_yticklabels([names.get(l,l) for l in s.ligand], fontsize=8)
    ax_.set_xlabel(ttl, fontsize=8.5)
    for sp in ("top","right"): ax_.spines[sp].set_visible(False)
    ax_.xaxis.grid(True, color="#ececea", lw=0.8); ax_.set_axisbelow(True)
fig.suptitle("ACACB: the two heads disagree on citrate", x=0.02, y=0.99, ha="left", fontsize=10.5, color=INK)
fig.tight_layout(rect=[0,0,1,0.95])
save(fig, "f5_acacb")

# ---------------------------------------------------------------- F6 who beats the regulators
PH = {"3PG","G3P","PEP"}
MWD = {"SUC":342.3,"TRE":342.3,"SIN":118.1,"TAU":125.1,"3PG":186.1,"G3P":172.1,"PEP":168.0}
NAME = {"SUC":"sucrose","TRE":"trehalose","SIN":"succinate","TAU":"taurine",
        "3PG":"3-phosphoglycerate","G3P":"glycerol-3-P","PEP":"phosphoenolpyruvate"}
win = {}
for prot, p in plan.items():
    s = tab[(tab.protein==prot)].set_index("ligand").p_binder
    for reg in p["regulators"]:
        for l in p["decoys"]:
            if s[l] >= s[reg]: win[l] = win.get(l, 0) + 1
o = sorted(win.items(), key=lambda kv: kv[1])
fig, ax = plt.subplots(figsize=(6.2, 2.6))
ax.barh(np.arange(len(o)), [c for _, c in o],
        color=[AQUA if l in PH else FAINT for l, _ in o], height=.58)
ax.set_yticks(np.arange(len(o)))
ax.set_yticklabels([f"{NAME[l]}  ({MWD[l]:.0f} Da)" for l, _ in o], fontsize=8.5)
for i, (_, c) in enumerate(o): ax.text(c + .25, i, str(c), va="center", fontsize=9, color=INK)
ax.set_xlabel("times this decoy outranked a regulator (of 32 pairs)")
for s_ in ("top","right"): ax.spines[s_].set_visible(False)
ax.xaxis.grid(True, color="#ececea", lw=0.8); ax.set_axisbelow(True)
h = [plt.Rectangle((0,0),1,1,color=AQUA), plt.Rectangle((0,0),1,1,color=FAINT)]
ax.legend(h, ["phosphorylated", "not phosphorylated"], frameon=False, fontsize=8.5, loc="lower right")
ax.set_title("The model is fooled by small neutral metabolites, not by phosphate",
             loc="left", fontsize=10.5, color=INK, pad=10)
save(fig, "f6_decoy_wins")
print("\nsplit: easy n=%d pb %.4f af %.4f | hard n=%d pb %.4f af %.4f"
      % (len(easy), easy.pb.mean(), easy.af.mean(), len(hard), hard.pb.mean(), hard.af.mean()))
