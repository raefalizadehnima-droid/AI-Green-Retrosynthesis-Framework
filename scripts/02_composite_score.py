"""
02_composite_score.py -- Eq. (4)-(7) exactly as written in the paper.

Writes
  output/composite_scores_eq5_7.csv   : S recomputed from RAW descriptors of the 9 survivors
  output/composite_scores_table18.csv : S recomputed from the PRINTED block scores of Table 18
and prints both next to the printed Table 18 so that every difference is visible.

IMPORTANT: this script does NOT tune anything to hit the printed values. If the printed
Table 18 cannot be reproduced from Eq. 5-7, the difference is reported, not hidden.
"""
import pandas as pd
from common import *

df = load_pathways()
sv = survivors(df)

rows = []
for mode in ("equal", "table11"):
    sc = block_scores(sv, mode)
    sc["S"] = composite(sc, W_TABLE10)
    sc["green_mode"] = mode
    rows.append(sc)
res = pd.concat(rows)
res["rank"] = res.groupby("green_mode")["S"].rank(ascending=False).astype(int)
res.sort_values(["green_mode", "rank"]).to_csv(OUT / "composite_scores_eq5_7.csv", index=False)

t18 = pd.DataFrame(T18, index=["rank_paper", "S_paper", "AI_paper", "Quantum_paper", "Green_paper"]).T
t18["S_from_printed_blocks"] = (W_TABLE10["AI"] * t18.AI_paper + W_TABLE10["Quantum"] * t18.Quantum_paper
                                + W_TABLE10["Green"] * t18.Green_paper)
t18["diff"] = t18.S_paper - t18.S_from_printed_blocks
t18.index.name = "route"
t18.to_csv(OUT / "composite_scores_table18.csv")

pd.set_option("display.width", 200)
print("Eq. 5-7 on raw data (green block = equal thirds)")
print(res[res.green_mode == "equal"].sort_values("rank").round(3).to_string(index=False))
print("\nTable 18 vs Eq. 7 applied to its own printed block scores")
print(t18.round(3).to_string())
