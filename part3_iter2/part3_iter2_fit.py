# -*- coding: utf-8 -*-
"""
This script keeps the scatter plots from Iter 1, then perform a 
linear Faber-Jackson fit with fitted parameters shown.

Author: Dingshuo Xu (z5642019)
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
    if len(df) < 3:
        raise ValueError(f"{sample_name}: fewer than 3 usable galaxies.")
    return df


def plot_fit(df: pd.DataFrame, sample_name: str) -> None:
    x = np.log10(df["sigma_re"].to_numpy())
    y = df["m_r"].to_numpy()

    if np.unique(x).size < 2:
        raise ValueError(f"{sample_name}: velocity dispersion has no range.")

    slope, intercept = np.polyfit(x, y, deg=1)
    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = slope * x_line + intercept

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(x, y, s=22, alpha=0.65,
               label=f"{sample_name} (N = {len(df)})")
    ax.plot(x_line, y_line, lw=2, label="Least-squares fit")
    ax.invert_yaxis()
    ax.set_xlabel(r"$\log_{10}(\sigma_e / \mathrm{km\ s^{-1}})$")
    ax.set_ylabel(r"$M_r$ (mag)")
    ax.set_title(f"Faber-Jackson relation: {sample_name}")
    ax.text(
        0.04, 0.96,
        f"$M_r = {slope:.3f}\\log_{{10}}(\\sigma_e)$\n"
        f"(intercept: {intercept:+.3f})\n",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.85},
    )
    ax.legend()
    fig.tight_layout()


samples = {
    "Elliptical": DATA_DIR / "elliptical_sample.csv",
    "Early type": DATA_DIR / "early_type_sample.csv",
}

for sample_name, csv_path in samples.items():
    df = load_sample(csv_path, sample_name)
    plot_fit(df, sample_name)

plt.show()
