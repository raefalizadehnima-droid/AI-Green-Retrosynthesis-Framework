"""
05_reproduce_from_stored_scores.py
Uses the block scores stored in DATA.xlsx (sheet Pathways_48: AI / Quantum / Green / S of the 9
green-screening survivors) as the input of record and reproduces Table 18, the ranking,
Fig. 6 funnel, Fig. 10 numbers. Output: output/table18_reproduced.csv
"""
import numpy as np, pandas as pd
from common import *

raw = pd.read_excel(DATA / "DATA.xlsx", sheet_name="Pathways_48", header=10)
raw = raw[raw.iloc[:, 0].astype(str).str.match(r"^P\d+$")]
t = raw[raw.iloc[:, 12] == 1].iloc[:, [0, 1, 13, 14, 15, 16]].copy()
t.columns = ["id", "route", "AI", "Quantum", "Green", "S_stored"]
t[["AI", "Quantum", "Green", "S_stored"]] = t[["AI", "Quantum", "Green", "S_stored"]].astype(float)
t.to_csv(DATA / "stage_scores.csv", index=False)

t["S_eq7"] = composite(t, W_TABLE10)
t["rank_stored"] = t.S_stored.rank(ascending=False, method="min").astype(int)
t["rank_eq7"] = t.S_eq7.rank(ascending=False, method="min").astype(int)
t["abs_diff"] = (t.S_stored - t.S_eq7).abs()
t = t.sort_values("rank_stored")
t.to_csv(OUT / "table18_reproduced.csv", index=False)
print(t.round(3).to_string(index=False))

print("\nTable 18 rows (C,D,B,E,A) vs stored scores:")
for r, (rk, S, a, q, g) in T18.items():
    x = t[t.route == r].iloc[0]
    ok = (rk == x.rank_stored) and all(abs(x[k] - v) < 1e-9 for k, v in (("S_stored", S), ("AI", a), ("Quantum", q), ("Green", g)))
    print(f"  {r}: rank {x.rank_stored} S {x.S_stored:.2f} AI {x.AI:.2f} Q {x.Quantum:.2f} G {x.Green:.2f} -> {'OK' if ok else 'DIFF'}")
print(f"\nS range {t.S_stored.min():.2f}-{t.S_stored.max():.2f} (paper 0.41-0.94) | top-3: {list(t.route[:3])}")
print(f"ranking from Eq.7 == stored ranking: {(t.rank_eq7 == t.rank_stored).all()} | max |S_stored - S_eq7| = {t.abs_diff.max():.3f}")

M = t[["AI", "Quantum", "Green"]].values
dom = [any((M[j] >= M[i]).all() and (M[j] > M[i]).any() for j in range(len(M)) if j != i) for i in range(len(M))]
print("Pareto non-dominated routes (AI,Q,G all maximised):", list(t.route[[not d for d in dom]]))
