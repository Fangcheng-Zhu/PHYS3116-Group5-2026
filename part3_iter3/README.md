# Iteration 3: Analysis

**Contributor:** Yucheng Qian(z5645983)


This iteration performs a more detailed analysis for the elliptical and early-type galaxy samples and the corresponding Faber–Jackson fits.

The script:
- reads the elliptical and early-type galaxy samples prepared in Part 2;
- converts `m_r` and `sigma_re` to numeric values;
- removes rows with missing or invalid values;
- calculates `log10(sigma_re)`;
- performs an unweighted linear fit of `m_r` against `log10(sigma_re)`;
- estimates the standard errors of the fitted slope and intercept from the fit covariance matrix;
- calculates the power-law index, `gamma` and its uncertainty;
- calculates RMS residual;
- plots the scatter points together with the fitted line for each sample, and show the uncertainties in parameters;
- saves the plots and a summary table.

## Run

Run the script from the repository root:

```bash
python3 part3-iter3/part3_iter3_full.py
```

## Outputs

```text
results/part3-fitting results/
elliptical_fit.png
early_type_fit.png
fit_summary.csv
```

The current fit is ordinary unweighted least squares. `cov=True` supplies an estimate of the covariance matrix of the fitted coefficients. Observational uncertainties are NOT supplied. 

The next step is to compare the results with literature.
