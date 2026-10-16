"""
04_figures.py -- regenerates the data-driven figures straight from the CSV files
(Fig. 5A/5B, 6, 7A, 8A, 9A/9B, 10B, 12B). Every panel is annotated with the value PRINTED
in the paper next to the value RECOMPUTED here, so a mismatch is visible on the figure itself.
Run 01-03 first.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from common import *

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
df = load_pathways()
sv = survivors(df)
sc = block_scores(sv, "equal")
sc["S"] = composite(sc, W_TABLE10)


def save(fig, name):
    fig.tight_layout(); fig.savefig(FIG / f"{name}.png", dpi=300); plt.close(fig)


# ---------------- Fig. 5A  PCA loadings (3 block scores, 9 survivors)
X = StandardScaler().fit_transform(sc[["AI", "Quantum", "Green"]])
pca = PCA(2).fit(X)
load = pca.components_.T * np.sqrt(pca.explained_variance_)
fig, ax = plt.subplots(figsize=(4.2, 4))
for (x, y), lab in zip(load, ["AI", "Quantum", "Green"]):
    ax.annotate("", xy=(x, y), xytext=(0, 0), arrowprops=dict(arrowstyle="->"))
    ax.text(x, y, lab, ha="left")
ax.axhline(0, c="grey", lw=.5); ax.axvline(0, c="grey", lw=.5); ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
ax.set_xlabel(f"PC1 ({100*pca.explained_variance_ratio_[0]:.1f}%)  [paper 58.3%]")
ax.set_ylabel(f"PC2 ({100*pca.explained_variance_ratio_[1]:.1f}%)  [paper 24.7%]")
ax.set_title("Fig. 5A  PCA loading plot (recomputed)")
save(fig, "fig5A_pca")

# ---------------- Fig. 5B  OAT Spearman bars
oat = pd.read_csv(OUT / "sensitivity_oat.csv")
o = oat[(oat.scores == "raw_9routes") & (oat.baseline.str.startswith("Table10"))]
fig, ax = plt.subplots(figsize=(5, 3.5))
for j, (lab, d) in enumerate((("-10%", -0.10), ("+10%", 0.10))):
    ax.bar(np.arange(3) + (j - .5) * .3, [o[(o.criterion == k) & (o.delta == d)].spearman.iloc[0] for k in ["AI", "Quantum", "Green"]], .3, label=lab)
ax.set_xticks(range(3)); ax.set_xticklabels(["AI 0.30", "Quantum 0.30", "Green 0.40"])
ax.set_ylim(0.9, 1.02); ax.set_ylabel("Spearman rho vs baseline"); ax.legend()
ax.set_title("Fig. 5B  OAT sensitivity (recomputed; paper shows 0.93-0.95)")
save(fig, "fig5B_sensitivity")

# ---------------- Fig. 6  funnel
st = [("AI-generated", 48), ("Plausibility", 31), ("DFT", 18), ("Green", 9), ("Multi-obj.", 3), ("Final", 1)]
fig, ax = plt.subplots(figsize=(6, 3))
ax.bar([s[0] for s in st], [s[1] for s in st], color="#4c72b0")
for i, (_, n) in enumerate(st):
    ax.text(i, n + 1, f"n={n}\n{100*n/48:.1f}%", ha="center", fontsize=8)
ax.set_ylim(0, 60); ax.set_ylabel("candidate pathways"); ax.set_title("Fig. 6  progressive reduction (Table 14)")
save(fig, "fig6_funnel")

# ---------------- Fig. 7A  confidence histogram
b = df.ai_conf.astype(float); a = df[df.plaus == 1].ai_conf.astype(float)
bins = np.arange(0.50, 1.0001, 0.05)
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.hist(b, bins, alpha=.6, label=f"before (n={len(b)}) mean={b.mean():.2f} SD={b.std():.2f}", color="#4c72b0")
ax.hist(a, bins, alpha=.6, label=f"after (n={len(a)}) mean={a.mean():.2f} SD={a.std():.2f}", color="#dd8452")
ax.set_xlabel("AI confidence"); ax.set_ylabel("number of pathways"); ax.legend(fontsize=7)
ax.set_title("Fig. 7A (recomputed from reconstructed confidences)")
save(fig, "fig7A_confidence")

# ---------------- Fig. 8A  gap vs dG
d = df[df.furthest_stage.isin(["DFT stage", "Green screening", "Top 3", "Selected"])]
slope, icpt, r, p, _ = stats.linregress(d.gap.astype(float), d.dG.astype(float))
fig, ax = plt.subplots(figsize=(4.8, 4))
ax.scatter(d.gap, d.dG, c="lightgrey", edgecolor="k", s=25)
for rt in ROUTES:
    q = df[df.route == rt].iloc[0]; ax.scatter(q.gap, q.dG, s=45, label=rt); ax.text(q.gap + .02, q.dG, rt[-1])
xs = np.linspace(d.gap.min(), d.gap.max(), 10); ax.plot(xs, icpt + slope * xs, "k--", lw=.8)
ax.set_xlabel("HOMO-LUMO gap (eV)"); ax.set_ylabel("dG# (kcal/mol)")
ax.set_title(f"Fig. 8A  r = {r:+.2f}, R2 = {r*r:.2f}  (paper prints r = -0.91)")
save(fig, "fig8A_gap_vs_dG")

# ---------------- Fig. 9A/B
g = pd.DataFrame(GREEN).T
fig, axs = plt.subplots(1, 2, figsize=(9, 3.5))
x = np.arange(5)
for j, (col, lab) in enumerate((("AE", "Atom economy (%)"), ("PMI", "PMI"), ("EF", "E-factor"))):
    axs[0].bar(x + (j - 1) * .27, g[col].astype(float), .27, label=lab)
axs[0].set_xticks(x); axs[0].set_xticklabels(ROUTES, rotation=20); axs[0].legend(fontsize=7); axs[0].set_title("Fig. 9A")
green9 = sc.set_index("route").loc[ROUTES, "Green"]
axs[1].bar(x - .17, [FIG9B[r] for r in ROUTES], .34, label="Fig. 9B as printed")
axs[1].bar(x + .17, green9.values, .34, label="Green score recomputed (Eq. 5/6)")
axs[1].set_xticks(x); axs[1].set_xticklabels(ROUTES, rotation=20); axs[1].legend(fontsize=7); axs[1].set_title("Fig. 9B check")
save(fig, "fig9_green")

# ---------------- Fig. 10B  contribution
share = {k: np.mean([W_TABLE10[k] * T18[r][i] / T18[r][1] for r in T18]) for k, i in (("AI", 2), ("Quantum", 3), ("Green", 4))}
t = sum(share.values())
fig, ax = plt.subplots(figsize=(4, 4))
ax.pie([share[k] / t for k in share], labels=[f"{k}\n{100*share[k]/t:.1f}% (paper {FIG10B[k]}%)" for k in share], startangle=90)
ax.set_title("Fig. 10B  share of S (weights x printed Table 18 scores)")
save(fig, "fig10B_contribution")

# ---------------- Fig. 12B  LHS Spearman
l = pd.read_csv(OUT / "sensitivity_lhs.csv")
l = l[(l.scores == "raw_9routes") & (l.baseline.str.startswith("Table20"))]
fig, ax = plt.subplots(figsize=(6, 3.2))
ax.bar(l.set, l.spearman, color="#4c72b0"); ax.axhline(0.90, c="r", ls="--", lw=.8)
ax.set_ylim(0.8, 1.02); ax.set_xlabel("LHS weight set"); ax.set_ylabel("Spearman rho")
ax.set_title(f"Fig. 12B recomputed: mean {l.spearman.mean():.3f} (paper 0.96 +/- 0.015)")
save(fig, "fig12B_lhs")
print("figures written to", FIG)
