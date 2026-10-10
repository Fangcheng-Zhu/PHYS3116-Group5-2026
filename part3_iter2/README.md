# Part 3 - Iteration 2: Preliminary Faber–Jackson fit

**Contributor:** Dingshuo Xu (z5642019)

This iteration builds on the scatter plots from Iteration 1 by fitting a straight line to the Faber–Jackson relation.

The script:

- reads the elliptical and early-type galaxy samples prepared in Part 2;
- converts `m_r` and `sigma_re` to numeric values;
- removes rows with missing or invalid values;
- calculates `log10(sigma_re)`;
- performs an unweighted linear fit of `m_r` against `log10(sigma_re)`;
- plots the scatter points together with the fitted line for each sample.

The fitted slope and intercept are used to draw the line, it is intended to check whether a linear trend appears reasonable before performing the full analysis.


## Run

Run the script from the repository root:

```bash
python3 part3-iter2/part3_iter2_fit.py
```

## Next step

Iteration 3 will complete the analysis by estimating the fit-parameter uncertainties, calculating gamma and its uncertainty.
