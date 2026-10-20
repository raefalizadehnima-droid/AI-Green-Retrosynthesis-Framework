"""
03_sensitivity.py -- one-at-a-time (+/-10 %, others renormalised) and Latin-Hypercube (20 sets)
sensitivity of the ranking, for BOTH baselines that appear in the paper
(Table 10/13: 0.30/0.30/0.40 ; Table 20/Fig.12: 0.25/0.35/0.40) and for BOTH score sets
(raw descriptors via Eq. 5-7, 9 routes ; printed Table 18 block scores, 5 routes).

Outputs: output/sensitivity_oat.csv, output/sensitivity_lhs.csv, output/sensitivity_summary.csv
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, qmc
from common import *

SEED, N_LHS = 42, SENS["n_lhs"]
KEYS = ["AI", "Quantum", "Green"]

df = load_pathways()
sv = survivors(df)
raw = block_scores(sv, "equal")
printed = pd.DataFrame({"route": list(T18), "AI": [T18[r][2] for r in T18],
                        "Quantum": [T18[r][3] for r in T18], "Green": [T18[r][4] for r in T18]})
SETS = {"raw_9routes": raw, "printed_T18_5routes": printed}
BASES = {"Table10_0.30/0.30/0.40": W_TABLE10, "Table20_0.25/0.35/0.40": W_TABLE20}


def renorm(w):
    v = np.array([w[k] for k in KEYS], float)
    return v / v.sum()


oat, lhs, summ = [], [], []
for sname, sc in SETS.items():
    X = sc[KEYS].values
    for bname, base in BASES.items():
        w0 = renorm(base)
        s0 = X @ w0
        top0 = sc.route.iloc[int(np.argmax(s0))]
        # ---- one-at-a-time +/-10 %
        for i, k in enumerate(KEYS):
            for d in (-0.10, 0.10):
                w = w0.copy(); w[i] *= 1 + d; w = w / w.sum()
                s = X @ w
                rho = spearmanr(s0, s).statistic
                oat.append(dict(scores=sname, baseline=bname, criterion=k, delta=d,
                                w_AI=w[0], w_Q=w[1], w_G=w[2], spearman=rho,
                                top_route=sc.route.iloc[int(np.argmax(s))],
                                routeC_S=float(s[sc.route == "Route C"][0])))
        # ---- Latin hypercube: each weight sampled in [0.9 w, 1.1 w], then renormalised
        u = qmc.LatinHypercube(d=3, seed=SEED).random(N_LHS)
        W = w0 * (0.9 + 0.2 * u)
        W = W / W.sum(axis=1, keepdims=True)
        S = X @ W.T
        rhos = np.array([spearmanr(s0, S[:, j]).statistic for j in range(N_LHS)])
        cS = S[(sc.route == "Route C").values][0]
        for j in range(N_LHS):
            lhs.append(dict(scores=sname, baseline=bname, set=j + 1, w_AI=W[j, 0], w_Q=W[j, 1], w_G=W[j, 2],
                            spearman=rhos[j], routeC_S=cS[j]))
        o = [r for r in oat if r["scores"] == sname and r["baseline"] == bname]
        summ.append(dict(scores=sname, baseline=bname, top_route_baseline=top0,
                         oat_rho_min=min(r["spearman"] for r in o), oat_rho_max=max(r["spearman"] for r in o),
                         oat_top_route_always=all(r["top_route"] == top0 for r in o),
                         lhs_rho_mean=rhos.mean(), lhs_rho_sd=rhos.std(ddof=1), lhs_rho_min=rhos.min(), lhs_rho_max=rhos.max(),
                         routeC_S_baseline=float(s0[sc.route == "Route C"][0]),
                         routeC_S_lhs_mean=cS.mean(), routeC_S_lhs_sd=cS.std(ddof=1),
                         routeC_S_lhs_min=cS.min(), routeC_S_lhs_max=cS.max()))

pd.DataFrame(oat).to_csv(OUT / "sensitivity_oat.csv", index=False)
pd.DataFrame(lhs).to_csv(OUT / "sensitivity_lhs.csv", index=False)
sm = pd.DataFrame(summ)
sm.to_csv(OUT / "sensitivity_summary.csv", index=False)

pd.set_option("display.width", 250)
print(sm.round(3).T.to_string(header=False))
print("\nPaper: Spearman 0.93-0.98 (mean 0.96 +/- 0.015, 20 LHS sets); Route C S 0.922-0.958, SD 0.018; Route C always first")
