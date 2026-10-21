# Part 2 - Iteration 1

This iteration performs initial quality checks on the merged SAMI catalogue.

It:

- checks the required input columns;
- adds quality flags for magnitude, stellar mass, and velocity dispersion;
- calculates the relative velocity-dispersion uncertainty;
- summarises morphology and catalogue categories;
- does not select the final galaxy sample.

## Run

From the repository root:

```bash
python part2-iter1/part2_iter1_quality_flags.py
```

The script reads `part1-iter3/results/sami_merged_observations.csv`
and writes its outputs to `part2-iter1/results/`.
