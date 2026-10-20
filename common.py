"""Shared helpers: data loading, Eq. (4)-(7) of the paper, comparison log."""
import numpy as np
import pandas as pd
from paper_values import *  # noqa: F401,F403


def norm_pos(s):
    """Eq. (5): beneficial criteria (higher is better)."""
    s = pd.Series(s, dtype=float)
    return (s - s.min()) / (s.max() - s.min())


def norm_neg(s):
    """Eq. (6): cost-type criteria (lower is better)."""
    s = pd.Series(s, dtype=float)
    return (s.max() - s) / (s.max() - s.min())


def load_pathways():
    return pd.read_csv(DATA / "pathways_48.csv")


def survivors(df):
    """The 9 routes that reach the multi-objective stage."""
    keep = ["Green screening", "Top 3", "Selected"]
    return df[df["furthest_stage"].isin(keep)].copy().reset_index(drop=True)


def block_scores(sv, green_weights="equal"):
    """Normalised block scores (Eq. 5/6).
    The paper does not define the weights *inside* the AI and Quantum blocks -> equal weights
    (documented assumption). Inside the Green block use 'equal' (as in the repo) or 'table11'."""
    out = sv[["id", "route"]].copy()
    out["AI"] = norm_pos(sv["ai_conf"])
    out["Quantum"] = (norm_neg(sv["dG"]) + norm_neg(sv["gap"]) + norm_pos(sv["f_plus"])) / 3
    ae, pmi, ef = norm_pos(sv["ae"]), norm_neg(sv["pmi"]), norm_neg(sv["ef"])
    if green_weights == "table11":
        w = W_GREEN_SUB
        out["Green"] = (w["AE"] * ae + w["PMI"] * pmi + w["EF"] * ef) / sum(w.values())
    else:
        out["Green"] = (ae + pmi + ef) / 3
    return out


def composite(scores, w):
    """Eq. (7): S = sum(w_i * x_i*), weights renormalised to sum to 1."""
    v = np.array([w["AI"], w["Quantum"], w["Green"]], float)
    v = v / v.sum()
    return scores[["AI", "Quantum", "Green"]].values @ v


class Log:
    """Collects check results -> output/verification_report.csv"""

    def __init__(self):
        self.rows = []

    def add(self, section, name, computed, paper=None, tol=None, note="", info=False):
        if info or paper is None or tol is None:
            status = "INFO"
        else:
            try:
                status = "OK" if abs(float(computed) - float(paper)) <= tol else "MISMATCH"
            except (TypeError, ValueError):
                status = "OK" if str(computed) == str(paper) else "MISMATCH"
        self.rows.append(dict(section=section, check=name, computed=computed,
                              paper=paper, tol=tol, status=status, note=note))

    def df(self):
        return pd.DataFrame(self.rows)
