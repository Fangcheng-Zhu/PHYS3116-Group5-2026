"""Inspect morphology categories and add quality flags for Option 2.

This script keeps the quality checks and sample selection from the earlier
iterations, then adds morphology summaries and figures.

Iteration 3 contributor: Yucheng Qian (z5645983)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# PART 2A: QUALITY FLAGS AND CATEGORY CHECKS
# Contributor: Fangcheng Zhu (z5532350)

def read_merged_observations(path: Path) -> pd.DataFrame:
    """Read and validate the merged observation table."""
    if not path.exists():
        raise FileNotFoundError(f"Merged data file not found: {path}")

    table = pd.read_csv(path)
    table.columns = table.columns.str.strip().str.lower()

    required_columns = [
        "catid",
        "cubeidpub",
        "type",
        "bad_class",
        "sample_origin",
        "m_r",
        "mstar",
        "sigma_re",
        "sigma_re_err",
        "observation_count",
        "flag_morphology_match",
        "flag_main_input_match",
    ]

    for column in required_columns:
        if column not in table:
            raise KeyError(f"Merged data does not contain {column!r}")

    return table


def add_quality_flags(table: pd.DataFrame) -> pd.DataFrame:
    """Add quality flags without removing any observations."""
    flagged = table.copy()

    numeric_columns = [
        "m_r",
        "mstar",
        "sigma_re",
        "sigma_re_err",
    ]

    for column in numeric_columns:
        flagged[column] = pd.to_numeric(flagged[column], errors="coerce")
        flagged[f"part2_flag_finite_{column}"] = np.isfinite(flagged[column])

    flagged["part2_flag_positive_sigma_re"] = flagged["sigma_re"] > 0

    flagged["part2_flag_nonnegative_sigma_re_err"] = (
        flagged["sigma_re_err"] >= 0
    )

    # Calculate the relative uncertainty in velocity dispersion.
    flagged["sigma_relative_error"] = (
        flagged["sigma_re_err"] / flagged["sigma_re"]
    )

    # Replace infinite results caused by division by zero.
    flagged["sigma_relative_error"] = flagged[
        "sigma_relative_error"
    ].replace([np.inf, -np.inf], np.nan)

    # Remove relative errors calculated from invalid measurements.
    flagged.loc[
        flagged["sigma_re"] <= 0,
        "sigma_relative_error",
    ] = np.nan

    flagged.loc[
        flagged["sigma_re_err"] < 0,
        "sigma_relative_error",
    ] = np.nan

    # Check whether the stellar kinematic measurements are usable.
    flagged["part2_flag_valid_kinematics"] = (
        flagged["part2_flag_finite_sigma_re"]
        & flagged["part2_flag_finite_sigma_re_err"]
        & flagged["part2_flag_positive_sigma_re"]
        & flagged["part2_flag_nonnegative_sigma_re_err"]
    )

    # Check the inputs needed for a magnitude-velocity dispersion relation.
    flagged["part2_flag_photometric_inputs"] = (
        flagged["flag_main_input_match"]
        & flagged["flag_morphology_match"]
        & flagged["part2_flag_finite_m_r"]
        & flagged["part2_flag_valid_kinematics"]
    )

    # Check the inputs needed for a stellar mass-velocity dispersion relation.
    flagged["part2_flag_mass_inputs"] = (
        flagged["flag_main_input_match"]
        & flagged["flag_morphology_match"]
        & flagged["part2_flag_finite_mstar"]
        & flagged["part2_flag_valid_kinematics"]
    )

    return flagged


def build_category_counts(table: pd.DataFrame) -> pd.DataFrame:
    """Count the values of important categorical variables."""
    results = []

    for column in ["type", "bad_class", "sample_origin"]:
        values = table[column].astype("string")
        values = values.fillna("Missing")
        counts = values.value_counts(dropna=False).reset_index()
        counts.columns = ["value", "count"]

        counts["variable"] = column
        counts["percent"] = (
            100 * counts["count"] / len(table)
        ).round(2)

        results.append(counts)

    return pd.concat(results, ignore_index=True)[
        ["variable", "value", "count", "percent"]
    ]


def build_quality_summary(table: pd.DataFrame) -> pd.DataFrame:
    """Summarise how many observations pass each basic quality check."""
    checks = {
        "Main catalogue matched": table["flag_main_input_match"],
        "Morphology matched": table["flag_morphology_match"],
        "Finite m_r": table["part2_flag_finite_m_r"],
        "Finite mstar": table["part2_flag_finite_mstar"],
        "Finite sigma_re": table["part2_flag_finite_sigma_re"],
        "Finite sigma_re_err": table["part2_flag_finite_sigma_re_err"],
        "Positive sigma_re": table["part2_flag_positive_sigma_re"],
        "Non-negative sigma_re_err": table[
            "part2_flag_nonnegative_sigma_re_err"
        ],
        "Valid stellar kinematics": table[
            "part2_flag_valid_kinematics"
        ],
        "Valid photometric inputs": table[
            "part2_flag_photometric_inputs"
        ],
        "Valid stellar-mass inputs": table[
            "part2_flag_mass_inputs"
        ],
    }

    rows = []

    for check_name, passed in checks.items():
        pass_count = int(passed.fillna(False).sum())
        fail_count = len(table) - pass_count

        rows.append(
            {
                "check": check_name,
                "pass_count": pass_count,
                "fail_count": fail_count,
                "pass_percent": round(
                    100 * pass_count / len(table),
                    2,
                ),
            }
        )

    return pd.DataFrame(rows)


# PART 2B: GALAXY SAMPLE SELECTION
# Added in Part 2 Iteration 2 by Dingshuo Xu (z5642019)


def add_morphology_labels(table: pd.DataFrame) -> pd.DataFrame:
    """Convert the numerical morphology types into readable labels."""
    labelled = table.copy()

    morphology_labels = {
        0.0: "Elliptical",
        0.5: "Elliptical/S0",
        1.0: "S0",
        1.5: "S0/Early Spiral",
        2.0: "Early Spiral",
        2.5: "Early/Late Spiral",
        3.0: "Late Spiral",
        5.0: "Indeterminate",
        -9.0: "No Agreement",
    }

    labelled["morphology_label"] = labelled["type"].map(
        morphology_labels
    )

    labelled["morphology_label"] = labelled[
        "morphology_label"
    ].fillna("Missing")

    labelled["flag_elliptical"] = labelled["type"] == 0.0

    labelled["flag_early_type"] = labelled["type"].isin(
        [0.0, 0.5, 1.0]
    )

    return labelled


def select_galaxy_samples(
    table: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Select clean early-type and elliptical galaxy samples."""
    selected = table.copy()

    selected["flag_clean_bad_class"] = (
        selected["bad_class"] == 0
    )

    early_type_candidates = selected.loc[
        selected["part2_flag_photometric_inputs"]
        & selected["flag_clean_bad_class"]
        & selected["flag_early_type"]
    ].copy()

    early_type_candidates = early_type_candidates.sort_values(
        ["catid", "sigma_relative_error"]
    )

    early_type_candidates["selected_best_observation"] = (
        ~early_type_candidates.duplicated(
            subset="catid",
            keep="first",
        )
    )

    repeated_observations = early_type_candidates.loc[
        early_type_candidates["observation_count"] > 1,
        [
            "catid",
            "cubeidpub",
            "observation_count",
            "sigma_re",
            "sigma_re_err",
            "sigma_relative_error",
            "selected_best_observation",
        ],
    ].copy()

    early_type_sample = early_type_candidates.loc[
        early_type_candidates["selected_best_observation"]
    ].copy()

    elliptical_sample = early_type_sample.loc[
        early_type_sample["flag_elliptical"]
    ].copy()

    return (
        early_type_sample,
        elliptical_sample,
        repeated_observations,
    )


def build_selection_audit(
    table: pd.DataFrame,
    early_type_sample: pd.DataFrame,
    elliptical_sample: pd.DataFrame,
) -> pd.DataFrame:
    """Record the number of observations and galaxies after selection."""
    valid_photometric = table.loc[
        table["part2_flag_photometric_inputs"]
    ]

    clean_quality = valid_photometric.loc[
        valid_photometric["bad_class"] == 0
    ]

    early_type_candidates = clean_quality.loc[
        clean_quality["flag_early_type"]
    ]

    audit_rows = [
        {
            "step": "All merged observations",
            "observations": len(table),
            "unique_galaxies": table["catid"].nunique(),
        },
        {
            "step": "Valid photometric inputs",
            "observations": len(valid_photometric),
            "unique_galaxies": valid_photometric["catid"].nunique(),
        },
        {
            "step": "BAD_CLASS equals zero",
            "observations": len(clean_quality),
            "unique_galaxies": clean_quality["catid"].nunique(),
        },
        {
            "step": "Early-type morphology",
            "observations": len(early_type_candidates),
            "unique_galaxies": early_type_candidates["catid"].nunique(),
        },
        {
            "step": "One observation per early-type galaxy",
            "observations": len(early_type_sample),
            "unique_galaxies": early_type_sample["catid"].nunique(),
        },
        {
            "step": "Strict elliptical sample",
            "observations": len(elliptical_sample),
            "unique_galaxies": elliptical_sample["catid"].nunique(),
        },
    ]

    return pd.DataFrame(audit_rows)


# PART 2C: MORPHOLOGY ANALYSIS
# Added in Part 2 Iteration 3 by Yucheng Qian (z5645983)


def build_morphology_analysis_sample(
    table: pd.DataFrame,
) -> pd.DataFrame:
    """Build a clean one-row-per-galaxy sample for morphology analysis."""
    reliable_types = [
        0.0,
        0.5,
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
    ]

    analysis_sample = table.loc[
        table["part2_flag_photometric_inputs"]
        & table["part2_flag_mass_inputs"]
        & (table["bad_class"] == 0)
        & table["type"].isin(reliable_types)
    ].copy()

    analysis_sample = analysis_sample.sort_values(
        ["catid", "sigma_relative_error"]
    )

    analysis_sample = analysis_sample.drop_duplicates(
        subset="catid",
        keep="first",
    )

    analysis_sample["morphology_group"] = "Spiral"

    analysis_sample.loc[
        analysis_sample["type"].isin([0.0, 0.5, 1.0]),
        "morphology_group",
    ] = "Early type"

    analysis_sample.loc[
        analysis_sample["type"] == 1.5,
        "morphology_group",
    ] = "Transition"

    return analysis_sample


def build_morphology_summary(
    analysis_sample: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise the main measurements for each morphology group."""
    rows = []

    for group_name in ["Early type", "Transition", "Spiral"]:
        group = analysis_sample.loc[
            analysis_sample["morphology_group"] == group_name
        ]

        if len(group) == 0:
            continue

        rows.append(
            {
                "morphology_group": group_name,
                "galaxies": len(group),
                "median_m_r": round(group["m_r"].median(), 3),
                "median_mstar": round(group["mstar"].median(), 3),
                "median_sigma_re": round(
                    group["sigma_re"].median(),
                    3,
                ),
            }
        )

    return pd.DataFrame(rows)


def build_origin_summary(
    analysis_sample: pd.DataFrame,
) -> pd.DataFrame:
    """Count morphology groups in the GAMA and Cluster samples."""
    rows = []

    for origin in ["GAMA", "Cluster"]:
        origin_sample = analysis_sample.loc[
            analysis_sample["sample_origin"] == origin
        ]

        for group_name in ["Early type", "Transition", "Spiral"]:
            group = origin_sample.loc[
                origin_sample["morphology_group"] == group_name
            ]

            rows.append(
                {
                    "sample_origin": origin,
                    "morphology_group": group_name,
                    "galaxies": len(group),
                }
            )

    return pd.DataFrame(rows)


def plot_morphology_counts(
    morphology_summary: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Plot the number of galaxies in each morphology group."""
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 5))

    plt.bar(
        morphology_summary["morphology_group"],
        morphology_summary["galaxies"],
        color=["tab:red", "tab:orange", "tab:blue"],
    )

    plt.xlabel("Morphology group")
    plt.ylabel("Number of galaxies")
    plt.title("Morphology of the selected SAMI sample")
    plt.tight_layout()

    plt.savefig(
        output_dir / "morphology_counts.png",
        dpi=200,
    )

    plt.close()


def plot_magnitude_sigma_by_morphology(
    analysis_sample: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Plot magnitude and velocity dispersion by morphology."""
    output_dir.mkdir(parents=True, exist_ok=True)

    colours = {
        "Early type": "tab:red",
        "Transition": "tab:orange",
        "Spiral": "tab:blue",
    }

    plt.figure(figsize=(7, 5))

    for group_name in ["Early type", "Transition", "Spiral"]:
        group = analysis_sample.loc[
            analysis_sample["morphology_group"] == group_name
        ]

        plt.scatter(
            np.log10(group["sigma_re"]),
            group["m_r"],
            label=group_name,
            color=colours[group_name],
            alpha=0.6,
            s=18,
        )

    plt.xlabel(r"$\log_{10}(\sigma_e / \mathrm{km\,s^{-1}})$")
    plt.ylabel(r"$M_r$ (mag)")
    plt.title("Magnitude and velocity dispersion by morphology")
    plt.gca().invert_yaxis()
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        output_dir / "magnitude_sigma_by_morphology.png",
        dpi=200,
    )

    plt.close()


def save_results(
    output_dir: Path,
    flagged: pd.DataFrame,
    category_counts: pd.DataFrame,
    quality_summary: pd.DataFrame,
) -> None:
    """Save the Part 2 Iteration 1 output tables."""
    output_dir.mkdir(parents=True, exist_ok=True)

    flagged.to_csv(
        output_dir / "part2_flagged_observations.csv",
        index=False,
    )
    category_counts.to_csv(
        output_dir / "part2_category_counts.csv",
        index=False,
    )
    quality_summary.to_csv(
        output_dir / "part2_quality_summary.csv",
        index=False,
    )


def save_selection_results(
    output_dir: Path,
    early_type_sample: pd.DataFrame,
    elliptical_sample: pd.DataFrame,
    repeated_observations: pd.DataFrame,
    selection_audit: pd.DataFrame,
) -> None:
    """Save the Part 2 Iteration 2 sample selection results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    early_type_sample.to_csv(
        output_dir / "early_type_sample.csv",
        index=False,
    )

    elliptical_sample.to_csv(
        output_dir / "elliptical_sample.csv",
        index=False,
    )

    repeated_observations.to_csv(
        output_dir / "repeated_observations.csv",
        index=False,
    )

    selection_audit.to_csv(
        output_dir / "sample_selection_audit.csv",
        index=False,
    )


def save_morphology_results(
    output_dir: Path,
    analysis_sample: pd.DataFrame,
    morphology_summary: pd.DataFrame,
    origin_summary: pd.DataFrame,
) -> None:
    """Save the Part 2 Iteration 3 morphology results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_sample.to_csv(
        output_dir / "morphology_analysis_sample.csv",
        index=False,
    )

    morphology_summary.to_csv(
        output_dir / "morphology_summary.csv",
        index=False,
    )

    origin_summary.to_csv(
        output_dir / "morphology_by_origin.csv",
        index=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results") / "sami_merged_observations.csv",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results") / "part2-iter3",
    )

    args = parser.parse_args()

    merged = read_merged_observations(args.input)
    flagged = add_quality_flags(merged)
    labelled = add_morphology_labels(flagged)
    early_type_sample, elliptical_sample, repeated_observations = (
        select_galaxy_samples(labelled)
    )
    selection_audit = build_selection_audit(
        labelled,
        early_type_sample,
        elliptical_sample,
    )
    analysis_sample = build_morphology_analysis_sample(labelled)
    morphology_summary = build_morphology_summary(analysis_sample)
    origin_summary = build_origin_summary(analysis_sample)
    category_counts = build_category_counts(labelled)
    quality_summary = build_quality_summary(labelled)

    save_results(
        args.output_dir,
        labelled,
        category_counts,
        quality_summary,
    )

    save_selection_results(
        args.output_dir,
        early_type_sample,
        elliptical_sample,
        repeated_observations,
        selection_audit,
    )

    save_morphology_results(
        args.output_dir,
        analysis_sample,
        morphology_summary,
        origin_summary,
    )

    figures_dir = args.output_dir / "figures"
    
    plot_morphology_counts(
        morphology_summary,
        figures_dir,
    )

    plot_magnitude_sigma_by_morphology(
        analysis_sample,
        figures_dir,
    )

    repeated_galaxies = flagged.loc[
        flagged["observation_count"] > 1,
        "catid",
    ].nunique()

    print("Part 2 - Iteration 3 complete")
    print(f"Observations examined: {len(flagged):,}")
    print(f"Morphology analysis galaxies: {len(analysis_sample):,}")
    print()
    print(morphology_summary.to_string(index=False))
    print()
    print(f"Results saved to: {args.output_dir.resolve()}")
    print(f"Selected early-type galaxies: {len(early_type_sample):,}")
    print(f"Selected elliptical galaxies: {len(elliptical_sample):,}")
    print(f"Galaxies with repeated observations: {repeated_galaxies:,}")

if __name__ == "__main__":
    main()