# Part 1 - Iter 1: Data cleaning Fangcheng Zhu (z5532350)

Part 1 focuses on preparing the SAMI data for later analysis. It is divided
into three stages: data cleaning, catalogue merging, and basic data exploration.

This iteration uses only the four CSV files supplied in Moodle Option 2.

It:

- loads each CSV with `CATID` preserved as text;
- standardises column names;
- removes accidental exported index columns;
- checks the expected identifiers for missing or duplicate values;
- combines the GAMA and cluster input catalogues while recording their origin.

It does not merge all four catalogues, select galaxies, or perform any fitting.

Run from the repository root:

```bash
python3 part1-iter1/part1_iter1_cleaning.py --data-dir row-data
```

The script creates `part1-iter1/results/` when run. Generated results are intentionally not included in the repository.

## Handoff to Iter 2
Iteration 1 is complete. The four Option 2 CSV files have been loaded,
cleaned, and checked. Column names have been standardised, unnecessary index
columns have been removed, and the main identifiers have been checked for
missing or duplicated values.

The GAMA and cluster input catalogues have also been combined. The main
outputs are:

- `results/cleaned_gama.csv`;
- `results/cleaned_clusters.csv`;
- `results/cleaned_kinematics.csv`;
- `results/cleaned_morphology.csv`;
- `results/combined_input_catalogue.csv`;
- `results/cleaning_audit.csv`.

The work is now handed over to **Dingshuo Xu** for Iteration 2. The next step
is to merge the catalogues using `CATID` and identify repeated kinematic
observations without removing them.