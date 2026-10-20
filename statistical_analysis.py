"""
Statistical Analysis
AI-Green-Retrosynthesis-Framework

Performs descriptive statistics and principal component
analysis (PCA) for the multi-objective optimization framework.

Author: Nima Alizadeh Raef
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv("../data/pathway_scores.csv")

# --------------------------------------------------
# Variables used in PCA
# --------------------------------------------------

variables = [
    "AI_confidence",
    "ActivationEnergy",
    "HOMO_LUMO_Gap",
    "Fukui",
    "AtomEconomy",
    "PMI",
    "EFactor"
]

X = df[variables]

# --------------------------------------------------
# Standardization
# --------------------------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# --------------------------------------------------
# PCA
# --------------------------------------------------

pca = PCA(n_components=2)

principal_components = pca.fit_transform(X_scaled)

results = pd.DataFrame(
    principal_components,
    columns=["PC1", "PC2"]
)

results["Pathway"] = df["Pathway"]

results.to_csv(
    "../output/pca_results.csv",
    index=False
)

# --------------------------------------------------
# Descriptive statistics
# --------------------------------------------------

stats = df[variables].describe()

stats.to_csv(
    "../output/descriptive_statistics.csv"
)

print(results)

print("\nExplained variance ratio:")

print(pca.explained_variance_ratio_)

print("\nStatistical analysis completed.")
