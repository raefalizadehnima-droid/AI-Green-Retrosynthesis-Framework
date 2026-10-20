"""
01_verify_tables.py -- recompute every derivable number in the paper from the data and
compare it with what is printed (Tables 14-20, Figs 5-12, in-text statements).

Output: output/verification_report.csv  and  output/verification_report.md
Status:  OK        recomputed value equals the printed one (within tolerance)
         MISMATCH  printed value cannot be reproduced from the data / stated equations
         INFO      informational (no printed counterpart)
"""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from common import *

df = load_pathways()
sv = survivors(df)
L = Log()

# ------------------------------------------------------------------ Table 14 / Fig. 6
stage_n = {
    "AI": len(df),
    "Plausibility": int((df.plaus == 1).sum()),
    "DFT": int(df.furthest_stage.isin(["DFT stage", "Green screening", "Top 3", "Selected"]).sum()),
    "Green": len(sv),
    "Top3": int(df.furthest_stage.isin(["Top 3", "Selected"]).sum()),
    "Final": int((df.furthest_stage == "Selected").sum()),
}
for k, v in stage_n.items():
    L.add("Table 14", f"n after stage: {k}", v, FUNNEL[k], 0)
for k, pct in FUNNEL_CUM.items():
    L.add("Table 14", f"cumulative retention % ({k})", round(100 * stage_n[k] / 48, 3), pct, 0.051,
          note="6.25% prints as 6.3 (round-half-up)" if k == "Top3" else "")
L.add("Text", "% of 48 removed by plausibility filter", round(100 * (1 - 31 / 48), 1), TEXT["filtered_pct"], 0.05)
L.add("Text/Sect. Framework robustness", 'DFT computations "decreased to about 63%"',
      round(100 * 18 / 48, 1), TEXT["dft_reduction_text"], 0.5,
      note="18/48 = 37.5% REMAIN; 62.5% is the REDUCTION. Rewrite as 'reduced by about 63%'.")

# ------------------------------------------------------------------ Table 15 / Fig. 7
b, a = df.ai_conf.astype(float), df[df.plaus == 1].ai_conf.astype(float)
for tag, s in (("before", b), ("after", a)):
    P = FIG7[tag]
    L.add("Fig. 7B", f"{tag}: n", len(s), P["n"], 0)
    L.add("Fig. 7B", f"{tag}: mean", round(s.mean(), 2), P["mean"], 0.005)
    L.add("Fig. 7B", f"{tag}: median", round(s.median(), 2), P["median"], 0.005)
    L.add("Fig. 7B", f"{tag}: SD (sample)", round(s.std(ddof=1), 2), P["sd"], 0.005)
    L.add("Fig. 7B", f"{tag}: min", round(s.min(), 2), P["min"], 0.005)
    L.add("Fig. 7B", f"{tag}: max", round(s.max(), 2), P["max"], 0.005)
    L.add("Fig. 7B", f"{tag}: n(conf>0.80)", int((s > 0.80).sum()), P["n_gt80"], 0)
    L.add("Fig. 7B", f"{tag}: % conf>0.80", round(100 * (s > 0.80).mean(), 1), P["pct_gt80"], 0.05)
L.add("Table 15 vs Fig. 7B", "min confidence after filtering", round(a.min(), 2), FIG7["table15_min_after"], 0.005,
      note="Table 15/text print 0.61-0.97 for the 31 RETAINED routes, Fig. 7B prints 0.65. Both cannot be true.")
d_unr = 100 * ((a > .8).mean() - (b > .8).mean())
L.add("Fig. 7B", "change in % >0.80 (unrounded, points)", round(d_unr, 1), FIG7["pct_change_printed"], 0.05,
      note="Printed +12.7 = 71.0 - 58.3 (rounded values). Unrounded 12.6.")

lo_b, lo_a, hi_b, hi_a = b[b <= .8], a[a <= .8], b[b > .8], a[a > .8]
for lab, x, y, claim in (("all pathways (48 vs 31)", b, a, "<0.01"),
                         ("conf <=0.80 (20 vs 9)", lo_b, lo_a, "<0.001"),
                         ("conf >0.80 (28 vs 22)", hi_b, hi_a, "ns")):
    p = stats.mannwhitneyu(x, y, alternative="two-sided").pvalue
    ok = (p < .01) if claim == "<0.01" else (p < .001) if claim == "<0.001" else (p >= .05)
    L.add("Fig. 7B", f"Mann-Whitney U p-value, {lab}", f"{p:.4g}", claim, None,
          note="consistent with printed significance" if ok else
               "NOT consistent with printed significance (note: 'after' is a subset of 'before' -> samples are not independent)")
    L.rows[-1]["status"] = "OK" if ok else "MISMATCH"

# ------------------------------------------------------------------ Table 16 / Fig. 8
dft = df[df.furthest_stage.isin(["DFT stage", "Green screening", "Top 3", "Selected"])]
L.add("Results/DFT", "min dG# of the 18 survivors", dft.dG.min(), 18.6, 0.005)
L.add("Results/DFT", "max dG# of the 18 survivors", dft.dG.max(), 33.8, 0.005)
L.add("Results/DFT", "min HOMO-LUMO gap", dft.gap.min(), 4.28, 0.005)
L.add("Results/DFT", "max HOMO-LUMO gap", dft.gap.max(), 5.61, 0.005)
r, _ = stats.pearsonr(dft.gap.astype(float), dft.dG.astype(float))
L.add("Fig. 8A", "R^2 (gap vs dG#, 18 routes)", round(r * r, 2), FIG8["R2"], 0.005)
L.add("Fig. 8A", "Pearson r sign", round(r, 2), FIG8["pearson_r_printed"], 0.005,
      note="Data (and the text 'low gap -> low barrier') give POSITIVE r. Fig. 8A prints r = -0.91 and calls it "
           "'inverse'. Correct the figure/text to r = +0.91 (|r| and R^2 are fine).")
L.rows[-1]["status"] = "MISMATCH" if r > 0 else "OK"
for rt, P in DFT.items():
    row = df[df.route == rt].iloc[0]
    for key, col in (("dG", "dG"), ("gap", "gap"), ("f", "f_plus"), ("dGrxn", "dGrxn")):
        L.add("Table 16", f"{rt} {key}", row[col], P[key], 1e-9)
fD, fE = df[df.route == "Route D"].f_plus.iloc[0], df[df.route == "Route E"].f_plus.iloc[0]
L.add("Text/DFT", "f+ difference Route D vs E (%)", round(100 * (fD - fE) / fE, 1), 20, 0.5)
L.add("Text/DFT", "all dGrxn negative (18 routes)", bool((dft.dGrxn < 0).all()), True, None)
L.rows[-1]["status"] = "OK" if (dft.dGrxn < 0).all() else "MISMATCH"

# ------------------------------------------------------------------ Table 17 / Fig. 9
for rt, P in GREEN.items():
    row = df[df.route == rt].iloc[0]
    L.add("Table 17", f"{rt} AE", row.ae, P["AE"], 1e-9)
    L.add("Table 17", f"{rt} PMI", row.pmi, P["PMI"], 1e-9)
    L.add("Table 17", f"{rt} E-factor", row.ef, P["EF"], 1e-9)
    L.add("Table 17", f"{rt} PMI - E-factor (=1 for closed mass balance, PMI = E + 1)",
          round(P["PMI"] - P["EF"], 2), 1.0, 0.05,
          note="Eq.(2)/(3) imply PMI = E + 1 when 'waste' = all inputs minus product. Paper values differ by 4.2-7.2: "
               "either waste excludes something (state it) or the numbers are inconsistent.")
L.add("Text/Green", "E-factor reduction Route A -> C (%)", round(100 * (31.2 - 12.6) / 31.2, 1),
      TEXT["waste_reduction_A_to_C_pct"], 1.0, note="59.6% -> 'almost 60%' is fine")
L.add("Text/Green", "PMI(A)/PMI(C)", round(38.4 / 16.8, 2), 2.0, None, info=True,
      note="'over double ... the other routes' holds only vs Route C (A/B 1.56, A/D 1.69, A/E 1.46)")
# environmental rank from the Fig. 9B scores vs Table 17 ranking
rk9 = pd.Series(FIG9B).rank(ascending=False).astype(int)
for rt, P in GREEN.items():
    L.add("Table 17 vs Fig. 9B", f"{rt} environmental rank", int(rk9[rt]), P["env_rank"], 0)
# does Fig 9B equal the Green score of Table 18, or the composite S?
for rt in ROUTES:
    L.add("Fig. 9B vs Table 18", f"{rt}: Fig.9B 'sustainability score' vs Table 18 Green score",
          FIG9B[rt], T18[rt][4], 0.005,
          note=f"Fig. 9B value equals composite S ({T18[rt][1]})" if abs(FIG9B[rt] - T18[rt][1]) <= 0.011 else "")

# ------------------------------------------------------------------ Table 10/11/13 weights
L.add("Table 10/13", "sum of weights", round(sum(W_TABLE10.values()), 6), 1.0, 1e-9)
L.add("Table 11", "green sub-weights sum = green weight", round(sum(W_GREEN_SUB.values()), 6), W_TABLE10["Green"], 1e-9)
L.add("Table 20 vs Table 10", "AI weight", W_TABLE20["AI"], W_TABLE10["AI"], 1e-9,
      note="Table 20/Fig. 12 use 0.25/0.35/0.40, Tables 10/13/Fig. 5B use 0.30/0.30/0.40.")
L.add("Table 20 vs Table 10", "Quantum weight", W_TABLE20["Quantum"], W_TABLE10["Quantum"], 1e-9)

# ------------------------------------------------------------------ Table 18 : two ways
# (a) S recomputed from the PRINTED block scores
for rt, (rk, S, ai, q, g) in T18.items():
    S_re = W_TABLE10["AI"] * ai + W_TABLE10["Quantum"] * q + W_TABLE10["Green"] * g
    L.add("Table 18 (Eq. 7 on printed scores)", f"{rt} S", round(S_re, 3), S, 0.005,
          note=f"printed {S}, recomputed {S_re:.3f}")
# (b) S recomputed from raw descriptors with Eq. 5-7 (9 survivors)
for mode in ("equal", "table11"):
    sc = block_scores(sv, mode)
    sc["S"] = composite(sc, W_TABLE10)
    sc = sc.sort_values("S", ascending=False).reset_index(drop=True)
    L.add(f"Table 18 (Eq. 5-7 on raw data, green={mode})", "top-3 routes", ", ".join(sc.route[:3]), "Route C, Route D, Route B", None,
          note="paper ranking cannot be reproduced from Eq. 5-7" if list(sc.route[:3]) != ["Route C", "Route D", "Route B"] else "")
    L.rows[-1]["status"] = "OK" if list(sc.route[:3]) == ["Route C", "Route D", "Route B"] else "MISMATCH"
    for rt in ROUTES:
        s = sc[sc.route == rt].iloc[0]
        for blk, idx in (("AI", 2), ("Quantum", 3), ("Green", 4)):
            L.add(f"Table 18 (Eq. 5-7 on raw data, green={mode})", f"{rt} {blk} score", round(s[blk], 2), T18[rt][idx], 0.005)
        L.add(f"Table 18 (Eq. 5-7 on raw data, green={mode})", f"{rt} S", round(s.S, 2), T18[rt][1], 0.005)

# contribution shares (Fig. 10B) from printed scores, mean over the 5 routes
share = {}
for blk, idx in (("AI", 2), ("Quantum", 3), ("Green", 4)):
    share[blk] = np.mean([W_TABLE10[blk] * T18[r][idx] / T18[r][1] for r in T18])
tot = sum(share.values())
for blk in share:
    L.add("Fig. 10B", f"share of S: {blk} (%)", round(100 * share[blk] / tot, 1), FIG10B[blk], 1.0,
          note="share of S contributed by the block (weights x printed scores)")

# ------------------------------------------------------------------ PCA (Fig. 5A)
sc = block_scores(sv, "equal")
pca = PCA(2).fit(StandardScaler().fit_transform(sc[["AI", "Quantum", "Green"]]))
L.add("Fig. 5A", "PC1 explained variance (%)", round(100 * pca.explained_variance_ratio_[0], 1), SENS["pc1"], 0.05,
      note="PCA on the 3 block scores of the 9 survivors")
L.add("Fig. 5A", "PC2 explained variance (%)", round(100 * pca.explained_variance_ratio_[1], 1), SENS["pc2"], 0.05)
p5 = PCA(2).fit(StandardScaler().fit_transform(pd.DataFrame({k: [T18[r][i] for r in T18] for k, i in (("AI", 2), ("Quantum", 3), ("Green", 4))})))
L.add("Fig. 5A", "PC1 (3 printed block scores, 5 routes) (%)", round(100 * p5.explained_variance_ratio_[0], 1), SENS["pc1"], 0.05)

# ------------------------------------------------------------------ Table 19 consistency
for api, P in T19.items():
    L.add("Table 19", f"{api}: PMI - E-factor", round(P["PMI"] - P["EF"], 2), 1.0, 0.05,
          note="same issue as Table 17")
L.add("Table 19", "Naproxen/Paracetamol 'Route B'/'Route A' labels", "Route B / Route A", "Route C", None, info=True,
      note="Route A was REJECTED for ibuprofen; labels are per-API, say so in the table caption.")

# ------------------------------------------------------------------ write
rep = L.df()
rep.to_csv(OUT / "verification_report.csv", index=False)
n = rep.status.value_counts().to_dict()
with open(OUT / "verification_report.md", "w", encoding="utf-8") as fh:
    fh.write(f"# Verification report\n\nOK: {n.get('OK',0)} | MISMATCH: {n.get('MISMATCH',0)} | INFO: {n.get('INFO',0)}\n\n")
    fh.write("## MISMATCHES\n\n| Section | Check | Computed | Paper | Note |\n|---|---|---|---|---|\n")
    for _, r in rep[rep.status == "MISMATCH"].iterrows():
        fh.write(f"| {r.section} | {r.check} | {r.computed} | {r.paper} | {r.note} |\n")
print(rep.status.value_counts().to_string())
print("\nMISMATCHES:")
print(rep[rep.status == "MISMATCH"][["section", "check", "computed", "paper"]].to_string(index=False))
