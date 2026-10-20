"""
00_export_data.py -- exports data/DATA.xlsx (sheet Pathways_48) to plain CSV files.
Outputs: data/pathways_48.csv, data/pathway_scores.csv
"""
import pandas as pd
from paper_values import DATA, ROUTES

raw = pd.read_excel(DATA / "DATA.xlsx", sheet_name="Pathways_48", header=10)
raw = raw[raw.iloc[:, 0].astype(str).str.match(r"^P\d+$")].copy()

df = pd.DataFrame({
    "id": raw.iloc[:, 0], "route": raw.iloc[:, 1],
    "ai_conf": raw.iloc[:, 2], "plaus": raw.iloc[:, 3],
    "dG": raw.iloc[:, 4], "gap": raw.iloc[:, 5], "f_plus": raw.iloc[:, 6], "dGrxn": raw.iloc[:, 7],
    "ae": raw.iloc[:, 9], "pmi": raw.iloc[:, 10], "ef": raw.iloc[:, 11],
    "furthest_stage": raw.iloc[:, 20],
})
df["route"] = df["route"].replace("—", "")
df.to_csv(DATA / "pathways_48.csv", index=False)

sv = df[df["furthest_stage"].isin(["Green screening", "Top 3", "Selected"])]
legacy = pd.DataFrame({
    "Pathway": sv["route"], "AI_confidence": sv["ai_conf"], "ActivationEnergy": sv["dG"],
    "HOMO_LUMO_Gap": sv["gap"], "Fukui": sv["f_plus"], "AtomEconomy": sv["ae"],
    "PMI": sv["pmi"], "EFactor": sv["ef"],
})
legacy.to_csv(DATA / "pathway_scores.csv", index=False)

print(f"pathways_48.csv: {len(df)} rows | survivors: {len(sv)}")
print(df["furthest_stage"].value_counts().to_string())
