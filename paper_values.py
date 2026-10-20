"""
paper_values.py -- single source of truth for every number printed in the paper.
Nothing here is computed: these are the values the scripts are checked against.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT, FIG = ROOT / "data", ROOT / "output", ROOT / "figures"
for _p in (DATA, OUT, FIG):
    _p.mkdir(exist_ok=True)

ROUTES = ["Route A", "Route B", "Route C", "Route D", "Route E"]

# Tables 10 / 13 / Fig. 5B
W_TABLE10 = {"AI": 0.30, "Quantum": 0.30, "Green": 0.40}
# Table 20 / Fig. 12 baseline (differs from Table 10 !)
W_TABLE20 = {"AI": 0.25, "Quantum": 0.35, "Green": 0.40}
# Table 11 (sub-weights inside the green block)
W_GREEN_SUB = {"AE": 0.18, "PMI": 0.12, "EF": 0.10}

# Table 14 / Fig. 6
FUNNEL = {"AI": 48, "Plausibility": 31, "DFT": 18, "Green": 9, "Top3": 3, "Final": 1}
FUNNEL_CUM = {"Plausibility": 64.6, "DFT": 37.5, "Green": 18.8, "Top3": 6.3, "Final": 2.1}

# Table 15 / Fig. 7
FIG7 = {
    "before": dict(n=48, mean=0.79, median=0.81, sd=0.11, min=0.61, max=0.97, n_gt80=28, pct_gt80=58.3),
    "after":  dict(n=31, mean=0.84, median=0.85, sd=0.08, min=0.65, max=0.97, n_gt80=22, pct_gt80=71.0),
    "table15_min_after": 0.61,           # Table 15 / text say 0.61-0.97 for the retained set
    "pct_change_printed": 12.7,
    "mwu_p": {"all": "<0.01", "le80": "<0.001", "gt80": "ns"},
}

# Table 16 (DFT) -- published
DFT = {
    "Route A": dict(dG=33.8, gap=5.61, f=0.21, dGrxn=-8.2),
    "Route B": dict(dG=25.4, gap=4.93, f=0.28, dGrxn=-12.5),
    "Route C": dict(dG=18.6, gap=4.28, f=0.34, dGrxn=-18.1),
    "Route D": dict(dG=22.1, gap=4.54, f=0.30, dGrxn=-15.7),
    "Route E": dict(dG=22.7, gap=4.60, f=0.25, dGrxn=-14.8),
}
FIG8 = {"R2": 0.82, "pearson_r_printed": -0.91}

# Table 17 (green) -- published
GREEN = {
    "Route A": dict(AE=58.4, PMI=38.4, EF=31.2, env_rank=5),
    "Route B": dict(AE=74.8, PMI=24.6, EF=18.9, env_rank=3),
    "Route C": dict(AE=87.3, PMI=16.8, EF=12.6, env_rank=1),
    "Route D": dict(AE=79.5, PMI=22.7, EF=16.8, env_rank=2),
    "Route E": dict(AE=72.9, PMI=26.3, EF=20.5, env_rank=4),
}
# Fig. 9B bar labels
FIG9B = {"Route A": 0.42, "Route B": 0.73, "Route C": 0.94, "Route D": 0.82, "Route E": 0.69}

# Table 18: route -> (rank, S, AI, Quantum, Green)
T18 = {
    "Route C": (1, 0.94, 0.89, 0.92, 0.96),
    "Route D": (2, 0.82, 0.85, 0.78, 0.83),
    "Route B": (3, 0.73, 0.81, 0.74, 0.64),
    "Route E": (4, 0.69, 0.72, 0.70, 0.65),
    "Route A": (5, 0.41, 0.55, 0.38, 0.35),
}
FIG10B = {"AI": 27, "Quantum": 31, "Green": 42}

# Table 19
T19 = {
    "Ibuprofen":   dict(n0=48, route="Route C", S=0.94, dG=18.6, AE=87.3, PMI=16.8, EF=12.6),
    "Naproxen":    dict(n0=45, route="Route B", S=0.91, dG=19.8, AE=84.5, PMI=18.1, EF=13.9),
    "Paracetamol": dict(n0=41, route="Route A", S=0.89, dG=20.4, AE=82.8, PMI=19.5, EF=15.2),
}

# Table 20 / Fig. 5 / Fig. 12
SENS = {
    "spearman_min": 0.93, "spearman_max": 0.98, "spearman_mean_lhs": 0.96, "spearman_sd_lhs": 0.015,
    "routeC_S_range": (0.922, 0.958), "routeC_S_sd": 0.018, "n_lhs": 20,
    "pc1": 58.3, "pc2": 24.7,
    "fig5B": {"AI": (0.941, 0.947), "Quantum": (0.936, 0.944), "Green": (0.932, 0.939)},  # read from bars
}
TEXT = {"filtered_pct": 35.4, "dft_reduction_text": 63, "waste_reduction_A_to_C_pct": 60}
