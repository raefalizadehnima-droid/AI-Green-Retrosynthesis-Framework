"""
===========================================================
Composite Score Calculation
AI-Green-Retrosynthesis-Framework
===========================================================
"""

import pandas as pd

# Weighting coefficients
WEIGHTS = {
    "AI": 0.30,
    "Quantum": 0.30,
    "Green": 0.40
}


def normalize_positive(series):
    """Higher values are better."""
    return (series - series.min()) / (series.max() - series.min())


def normalize_negative(series):
    """Lower values are better."""
    return (series.max() - series) / (series.max() - series.min())


# Read input data
df = pd.read_csv("../data/pathway_scores.csv")

# AI score
df["AI_score"] = normalize_positive(df["AI_confidence"])

# Quantum score
df["Act_score"] = normalize_negative(df["ActivationEnergy"])
df["Gap_score"] = normalize_negative(df["HOMO_LUMO_Gap"])
df["Fukui_score"] = normalize_positive(df["Fukui"])

df["Quantum_score"] = (
    df["Act_score"] +
    df["Gap_score"] +
    df["Fukui_score"]
) / 3

# Green chemistry score
df["AE_score"] = normalize_positive(df["AtomEconomy"])
df["PMI_score"] = normalize_negative(df["PMI"])
df["EFactor_score"] = normalize_negative(df["EFactor"])

df["Green_score"] = (
    df["AE_score"] +
    df["PMI_score"] +
    df["EFactor_score"]
) / 3

# Composite score
df["CompositeScore"] = (
    WEIGHTS["AI"] * df["AI_score"] +
    WEIGHTS["Quantum"] * df["Quantum_score"] +
    WEIGHTS["Green"] * df["Green_score"]
)

# Ranking
df = df.sort_values(by="CompositeScore", ascending=False)
df["Rank"] = range(1, len(df) + 1)

# Save output
output = df[
    [
        "Rank",
        "Pathway",
        "CompositeScore",
        "AI_score",
        "Quantum_score",
        "Green_score",
    ]
]

output.to_csv("../output/composite_scores.csv", index=False)

print(output)

print("\nComposite score calculation completed.")
