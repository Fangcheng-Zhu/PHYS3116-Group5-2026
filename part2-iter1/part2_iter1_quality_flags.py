"""Inspect morphology categories and add quality flags for Option 2.

Author: Fangcheng Zhu (z5532350)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


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
        default=Path("results") / "part2-iter1",
    )

    args = parser.parse_args()

    merged = read_merged_observations(args.input)
    flagged = add_quality_flags(merged)

    category_counts = build_category_counts(flagged)
    quality_summary = build_quality_summary(flagged)

    save_results(
        args.output_dir,
        flagged,
        category_counts,
        quality_summary,
    )

    repeated_galaxies = flagged.loc[
        flagged["observation_count"] > 1,
        "catid",
    ].nunique()

    print("Part 2 - Iteration 1 complete")
    print(f"Observations examined: {len(flagged):,}")
    print(f"Unique galaxies: {flagged['catid'].nunique():,}")
    print(f"Galaxies with repeated observations: {repeated_galaxies:,}")
    print()
    print(quality_summary.to_string(index=False))
    print()
    print(f"Results saved to: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()