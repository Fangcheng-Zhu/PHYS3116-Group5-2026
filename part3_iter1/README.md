# Part 3 - Iteration 1: Initial scatter plots

**Contributor:** Fangcheng Zhu (z5532350)

This iteration uses the galaxy samples prepared in Part 2 to explore the Faber–Jackson relation.

The script:

- reads the elliptical and early-type galaxy samples;
- converts `m_r` and `sigma_re` to numeric values;
- removes rows with missing or invalid values;
- calculates `log10(sigma_re)`;
- plots  `m_r` against `log10(sigma_re)`;

The elliptical sample is a subset of the early-type sample. This iteration is used for an initial visual check only. The formal fitting and quantitative comparison will be completed in later iterations.

## Input files

The script uses:

- `part2-iter3/results/elliptical_sample.csv`
- `part2-iter3/results/early_type_sample.csv`

## Run

Run the script from the repository root:

```bash
python3 part3-iter1/part3_iter1_scatter.py
```


## Next step

Iteration 2 will fit the Faber–Jackson relation and calculate the slope and intercept.
