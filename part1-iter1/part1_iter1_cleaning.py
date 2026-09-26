"""Clean and validate the four CSV files supplied for Moodle Option 2.

Author: Fangcheng Zhu (z5532350)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


OPTION2_FILES = {
    "gama": "InputCatGAMADR3.csv",
    "clusters": "samiDR3InputCatClusters.csv",
    "kinematics": "samiDR3StelKin.csv",
    "morphology": "samiDR3VisualMorphology.csv",
}


# PART 1A: DATA CLEANING
# Contributor: Fangcheng Zhu (z5532350)

def read_option2_csv(path: Path) -> pd.DataFrame:
    """Read one supplied CSV and apply only structural cleaning."""
    if not path.exists():
        raise FileNotFoundError(f"Required Option 2 file not found: {path}")

    table = pd.read_csv(path, dtype={"CATID": "string", "catid": "string"})
    table.columns = table.columns.str.strip().str.lower()

    exported_index = [name for name in table if name.startswith("unnamed:")]
    return table.drop(columns=exported_index)


def check_unique_identifier(
    table: pd.DataFrame, table_name: str, identifier: str
) -> dict[str, object]:
    """Check one identifier and return a summary for the cleaning audit."""
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
    """Load, clean, and validate the four supplied catalogues."""
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
    """Save the cleaned tables and audit summary to the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for label, table in tables.items():
        table.to_csv(output_dir / f"cleaned_{label}.csv", index=False)
    input_catalogue.to_csv(output_dir / "combined_input_catalogue.csv", index=False)
    cleaning_audit.to_csv(output_dir / "cleaning_audit.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("row-data"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
    )
    args = parser.parse_args()

    tables, input_catalogue, cleaning_audit = clean_option2_tables(args.data_dir)
    save_cleaning_results(args.output_dir, tables, input_catalogue, cleaning_audit)

    print("Part 1 - Iter 1 complete: data cleaning")
    print(cleaning_audit.to_string(index=False))
    print(f"Results saved to: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
