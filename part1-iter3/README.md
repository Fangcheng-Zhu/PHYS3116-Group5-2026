# Part 1 - Iter 3: Cleaning, merging, and basic exploration Yucheng Qian (z5645983)

Part 1 - Iter 3 is cumulative. It contains all Part 1 - Iter 1 cleaning and Part 1 - Iter 2 merging, then adds basic exploration.

New work in this iteration:

- inventories the four source tables;
- reports missing values in the merged observation table;
- counts raw `sample_origin`, `BAD_CLASS`, and morphology `TYPE` values;
- summarises redshift, absolute magnitude, stellar mass, velocity dispersion, and its uncertainty;
- calculates exploratory Pearson correlations.

These are descriptive checks only. This iteration does not select a galaxy sample, interpret morphology, choose a preferred repeated observation, fit the Faber–Jackson relation, or compare with literature.

Run from the repository root:

```bash
python3 part1-iter3/part1_iter3_full.py --data-dir row-data
```

The script creates `part1-iter3/results/` when run. Generated results are intentionally not included in the repository.

## Handoff
Part 1 is now complete. The four Option 2 catalogues have been cleaned,
checked, and merged. Repeated observations have been marked but not removed.
Basic data exploration has also been completed.

The next stage is Part B: galaxy sample selection and morphology analysis.
Responsibility for this part is currently being assigned.