# -*- coding: utf-8 -*-
"""
Read the selected samples from Part 2 and inspect the Faber-Jackson
x-y distributions with scatter plots.

Author: Fangcheng Zhu (z5532350)
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("results/part2-iter3")


def load_sample(csv_path: Path, sample_name: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["m_r"] = pd.to_numeric(df["m_r"], errors="coerce")
    df["sigma_re"] = pd.to_numeric(df["sigma_re"], errors="coerce")
    df = df[
        np.isfinite(df["m_r"])
        & np.isfinite(df["sigma_re"])
        & (df["sigma_re"] > 0)
    ].copy()
    if len(df) < 1:
        raise ValueError(f"{sample_name}: no usable galaxies found.")
    return df


def plot_scatter(df: pd.DataFrame, sample_name: str) -> None:
    x = np.log10(df["sigma_re"].to_numpy())
    y = df["m_r"].to_numpy()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x, y, s=22, alpha=0.65,
               label=f"{sample_name} (N = {len(df)})")
    ax.invert_yaxis()
    ax.set_xlabel(r"$\log_{10}(\sigma_e / \mathrm{km\ s^{-1}})$")
    ax.set_ylabel(r"$M_r$ (mag)")
    ax.set_title(f"Faber-Jackson relation: {sample_name}")
    ax.legend()
    fig.tight_layout()


samples = {
    "Elliptical": DATA_DIR / "elliptical_sample.csv",
    "Early type": DATA_DIR / "early_type_sample.csv",
}

for sample_name, csv_path in samples.items():
    df = load_sample(csv_path, sample_name)
    print(f"{sample_name}: {len(df)} usable galaxies")
    plot_scatter(df, sample_name)

plt.show()
