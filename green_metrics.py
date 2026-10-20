"""
Green Chemistry Metrics Calculator
AI-Green-Retrosynthesis-Framework
"""

import pandas as pd


def atom_economy(desired_product_mass, total_reactant_mass):
    return (desired_product_mass / total_reactant_mass) * 100


def process_mass_intensity(total_material_mass, product_mass):
    return total_material_mass / product_mass


def e_factor(total_waste_mass, product_mass):
    return total_waste_mass / product_mass


def sustainability_score(ae, pmi, ef):
    """
    Normalized sustainability score.
    Higher values indicate greener processes.
    """

    ae_norm = ae / 100

    pmi_norm = 1 / pmi

    ef_norm = 1 / ef

    return (ae_norm + pmi_norm + ef_norm) / 3


if __name__ == "__main__":

    data = pd.read_csv("../data/pathway_scores.csv")

    data["SustainabilityScore"] = data.apply(
        lambda row: sustainability_score(
            row["AtomEconomy"],
            row["PMI"],
            row["EFactor"]
        ),
        axis=1
    )

    print(data[["Pathway", "SustainabilityScore"]])
