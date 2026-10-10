# -*- coding: utf-8 -*-
"""
This script keeps the scatter plots and linear Faber-Jackson fit, then
calculates gemma and uncertainties in parameters.

Iteration 3 contributor: Yucheng Qian (z5645983)
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path("results/part2-iter3")
OUT_DIR = Path("results") / "part3-fitting results"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def fit_sample(csv_path: Path, sample_name: str) -> dict:
    """Fit one sample and save its Faber-Jackson plot."""
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

    x = np.log10(df["sigma_re"].to_numpy())
    y = df["m_r"].to_numpy()

    if np.unique(x).size < 2:
        raise ValueError(f"{sample_name}: velocity dispersion has no range.")

    # Unweighted least-squares fit.
    (slope, intercept), covariance = np.polyfit(x, y, deg=1, cov=True)
    slope_err, intercept_err = np.sqrt(np.diag(covariance))

    # L is propotional to sigma^gamma and M = -2.5 log10(L) + constant
    # M_r = -2.5 gamma log10(sigma_e) + constant
    gamma = -slope / 2.5
    gamma_err = slope_err / 2.5

    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = slope * x_line + intercept
    y_fit = slope * x + intercept

    residuals = y - y_fit
    rms = np.sqrt(np.mean(residuals**2))
    residual_std = np.std(residuals, ddof=2)

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
        f"(intercept: {intercept:+.3f})\n"
        f"RMS residual = {rms:.3f} mag",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.85},
    )

    ax.legend()
    fig.tight_layout()

    safe_name = sample_name.lower().replace(" ", "_")
    fig.savefig(OUT_DIR / f"{safe_name}_fit.png", dpi=200)
    plt.close(fig)

    return {
        "sample": sample_name,
        "n_galaxies": len(df),
        "slope_mag_per_dex": slope,
        "slope_std_err": slope_err,
        "intercept_mag": intercept,
        "intercept_std_err": intercept_err,
        "gamma_luminosity": gamma,
        "gamma_std_err": gamma_err,
        "rms_residual_mag": rms,
        "residual_std_mag": residual_std,
    }


results = [
    fit_sample(DATA_DIR / "elliptical_sample.csv", "Elliptical"),
    fit_sample(DATA_DIR / "early_type_sample.csv", "Early type"),
]

summary = pd.DataFrame(results)
print(summary.to_string(index=False))
summary.to_csv(OUT_DIR / "fit_summary.csv", index=False)
print(f"\nSaved outputs to: {OUT_DIR.resolve()}")
