"""
Sensitivity Analysis
AI-Green-Retrosynthesis-Framework

Evaluates the robustness of pathway rankings by perturbing
the weighting coefficients used in the composite score.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# Base weights
BASE = np.array([0.30, 0.30, 0.40])

# Load normalized scores
df = pd.read_csv("../output/composite_scores.csv")

scores = df[["AI_score", "Quantum_score", "Green_score"]].values
reference = df["CompositeScore"].values

results = []

for i in range(3):

    for delta in [-0.10, 0.10]:

        w = BASE.copy()

        w[i] *= (1 + delta)

        w /= w.sum()

        new_score = scores @ w

        rho, _ = spearmanr(reference, new_score)

        results.append({
            "Criterion": ["AI", "Quantum", "Green"][i],
            "Perturbation": delta,
            "Weight_AI": w[0],
            "Weight_Quantum": w[1],
            "Weight_Green": w[2],
            "Spearman_rho": rho
        })

results = pd.DataFrame(results)

results.to_csv("../output/sensitivity_results.csv", index=False)

print(results)
print("\nSensitivity analysis completed.")
