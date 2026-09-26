# Part 1 - Iter 2: Cleaning and merging Dingshuo Xu (z5642019)

Part 1 - Iter 2 is cumulative. It contains all Part 1 - Iter 1 cleaning and adds merging.

New work in this iteration:

- counts observations per `CATID`;
- flags galaxies with repeated observations;
- left-joins kinematics, morphology, and the combined input catalogue;
- preserves every supplied kinematic observation;
- creates an observation-level table and a unique-galaxy index;
- records merge row counts for checking.

No repeated observation is chosen or discarded, and no scientific sample selection is applied.

Run from the repository root:

```bash
python3 part1-iter2/part1_iter2_cleaning_merging.py --data-dir row-data
```

The script creates `part1-iter2/results/` when run. Generated results are intentionally not included in the repository.

## Handoff to Iter 3
Iteration 2 is complete. The four Option 2 catalogues have been cleaned and
merged using `CATID`. Repeated observations have been identified and kept for
later checking. No galaxy has been removed at this stage.

The main outputs are:

- `results/sami_merged_observations.csv`;
- `results/sami_unique_galaxy_index.csv`;
- `results/repeated_galaxies.csv`;
- `results/merge_audit.csv`.

The work is now handed over to **Yucheng Qian** for Iteration 3. The next step
is to check missing values, review the main data categories, and produce basic
numerical summaries and exploratory correlations.