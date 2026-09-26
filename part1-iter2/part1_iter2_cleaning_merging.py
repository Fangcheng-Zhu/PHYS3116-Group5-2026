"""Clean and merge the four CSV files supplied for Moodle Option 2.

This script keeps the cleaning steps from Iter 1 and adds data merging.

Iteration 2 contributor: Dingshuo Xu (z5642019)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


OPTION2_FILES = {
    "gama": "InputCatGAMADR3.csv",
    "clusters": "samiDR3InputCatClusters.csv",
    "kinematics": "samiDR3StelKin.csv",
    "morphology": "samiDR3VisualMorphology.csv",
}


# PART 1A: DATA CLEANING
# Carried forward from Iter 1 by Fangcheng Zhu (z5532350)

def read_option2_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required Option 2 file not found: {path}")

    table = pd.read_csv(path, dtype={"CATID": "string", "catid": "string"})
    table.columns = table.columns.str.strip().str.lower()
    exported_index = [name for name in table if name.startswith("unnamed:")]
    return table.drop(columns=exported_index)


def check_unique_identifier(
    table: pd.DataFrame, table_name: str, identifier: str
) -> dict[str, object]:
    if identifier not in table:
        raise KeyError(f"{table_name} does not contain {identifier!r}")

    missing = int(table[identifier].isna().sum())
    duplicates = int(table[identifier].duplicated().sum())
    if missing or duplicates:
        raise ValueError(
            f"{table_name}: {identifier} has {missing} missing and "
            f"{duplicates} duplicated values"
        )

    return {
        "table": table_name,
        "identifier": identifier,
        "rows": len(table),
        "missing_identifier": missing,
        "duplicate_identifier": duplicates,
    }


def clean_option2_tables(
    data_dir: Path,
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, pd.DataFrame]:
    tables = {
        label: read_option2_csv(data_dir / filename)
        for label, filename in OPTION2_FILES.items()
    }

    audit_rows = [
        check_unique_identifier(tables["gama"], "GAMA input", "catid"),
        check_unique_identifier(tables["clusters"], "Cluster input", "catid"),
        check_unique_identifier(tables["morphology"], "Visual morphology", "catid"),
        check_unique_identifier(
            tables["kinematics"], "Stellar kinematics", "cubeidpub"
        ),
    ]

    input_catalogue = pd.concat(
        [
            tables["gama"].assign(sample_origin="GAMA"),
            tables["clusters"].assign(sample_origin="Cluster"),
        ],
        ignore_index=True,
        sort=False,
    )
    audit_rows.append(
        check_unique_identifier(input_catalogue, "Combined input", "catid")
    )
    return tables, input_catalogue, pd.DataFrame(audit_rows)


def save_cleaning_results(
    output_dir: Path,
    tables: dict[str, pd.DataFrame],
    input_catalogue: pd.DataFrame,
    cleaning_audit: pd.DataFrame,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for label, table in tables.items():
        table.to_csv(output_dir / f"cleaned_{label}.csv", index=False)
    input_catalogue.to_csv(output_dir / "combined_input_catalogue.csv", index=False)
    cleaning_audit.to_csv(output_dir / "cleaning_audit.csv", index=False)


# PART 1B: DATA MERGING
# Added in Iter 2 by Dingshuo Xu (z5642019)

def merge_option2_tables(
    kinematics: pd.DataFrame,
    morphology: pd.DataFrame,
    input_catalogue: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Merge the catalogues by CATID and keep repeated observations for review."""
    observation_counts = (
        kinematics.groupby("catid", as_index=False)
        .size()
        .rename(columns={"size": "observation_count"})
    )

    merged_observations = (
        kinematics.merge(
            observation_counts, on="catid", how="left", validate="many_to_one"
        )
        .merge(morphology, on="catid", how="left", validate="many_to_one")
        .merge(input_catalogue, on="catid", how="left", validate="many_to_one")
    )
    check_unique_identifier(
        merged_observations, "Merged observations", "cubeidpub"
    )

    merged_observations["flag_repeated_catid"] = (
        merged_observations["observation_count"] > 1
    )
    merged_observations["flag_morphology_match"] = merged_observations["type"].notna()
    merged_observations["flag_main_input_match"] = merged_observations[
        "sample_origin"
    ].notna()
    for column in ["m_r", "mstar", "sigma_re", "sigma_re_err"]:
        merged_observations[f"flag_finite_{column}"] = np.isfinite(
            merged_observations[column]
        )
    merged_observations["flag_positive_sigma_re"] = (
        merged_observations["sigma_re"] > 0
    )

    galaxy_index = (
        observation_counts.merge(
            morphology, on="catid", how="left", validate="one_to_one"
        ).merge(
            input_catalogue, on="catid", how="left", validate="one_to_one"
        )
    )
    galaxy_index["flag_repeated_catid"] = galaxy_index["observation_count"] > 1
    galaxy_index["flag_morphology_match"] = galaxy_index["type"].notna()
    galaxy_index["flag_main_input_match"] = galaxy_index["sample_origin"].notna()

    merge_audit = pd.DataFrame(
        [
            {
                "dataset": "Kinematic observations",
                "rows": len(kinematics),
                "unique_galaxies": kinematics["catid"].nunique(),
            },
            {
                "dataset": "Merged observations",
                "rows": len(merged_observations),
                "unique_galaxies": merged_observations["catid"].nunique(),
            },
            {
                "dataset": "Unique-galaxy index",
                "rows": len(galaxy_index),
                "unique_galaxies": galaxy_index["catid"].nunique(),
            },
        ]
    )
    return merged_observations, galaxy_index, merge_audit


def save_merging_results(
    output_dir: Path,
    merged_observations: pd.DataFrame,
    galaxy_index: pd.DataFrame,
    merge_audit: pd.DataFrame,
) -> None:
    merged_observations.to_csv(
        output_dir / "sami_merged_observations.csv", index=False
    )
    galaxy_index.to_csv(output_dir / "sami_unique_galaxy_index.csv", index=False)
    merge_audit.to_csv(output_dir / "merge_audit.csv", index=False)
    galaxy_index.loc[
        galaxy_index["observation_count"] > 1, ["catid", "observation_count"]
    ].to_csv(output_dir / "repeated_galaxies.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("row-data"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
    )
    args = parser.parse_args()

    # Clean the source tables.
    tables, input_catalogue, cleaning_audit = clean_option2_tables(args.data_dir)
    save_cleaning_results(args.output_dir, tables, input_catalogue, cleaning_audit)

    # Merge the catalogues.
    merged, galaxies, merge_audit = merge_option2_tables(
        tables["kinematics"], tables["morphology"], input_catalogue
    )
    save_merging_results(args.output_dir, merged, galaxies, merge_audit)

    print("Part 1 - Iter 2 complete: cleaning + merging")
    print(merge_audit.to_string(index=False))
    print(f"Results saved to: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
