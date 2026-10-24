# Scientific discussion of the Faber–Jackson analysis

## Research questions and method

We examine whether brighter early-type galaxies have higher stellar velocity dispersions in the supplied SAMI data, compare a strict elliptical sample with a broader early-type sample, and compare our fitted relation with published results. The analysis uses absolute r-band magnitude, `m_r`, and the stellar velocity-dispersion column `sigma_re`, expressed in km/s.

We fit

```text
M_r = a × log10[σ_e / (km s⁻¹)] + b
```

Absolute magnitude and luminosity are related by `M_r = −2.5 × log10(L_r/L_ref) + C`, where `L_ref` is a fixed reference luminosity. If luminosity follows `L_r ∝ σ_e^γ`, the fitted magnitude slope gives:

```text
γ = −a / 2.5
s_γ = s_a / 2.5
```

Here, `s_a` and `s_γ` are the formal standard errors of the slope and exponent. A negative magnitude slope means that galaxies with larger dispersions are brighter. The plots reverse the magnitude axis for readability; this does not change the fitted slope.

The code uses unweighted ordinary least squares in magnitude at fixed log dispersion. `np.polyfit(..., cov=True)` estimates coefficient covariance from the residual scatter under this model. The square roots of its diagonal elements give the reported formal standard errors. Individual observational uncertainties are not supplied to the fit.

## Sample definition

| Step | Observations | Unique galaxies |
| --- | ---: | ---: |
| All merged observations | 3,426 | 3,068 |
| Valid photometric inputs | 2,249 | 2,249 |
| `BAD_CLASS == 0` | 2,236 | 2,236 |
| Early-type morphology | 779 | 779 |
| One observation per early-type galaxy | 779 | 779 |
| Strict elliptical sample | 230 | 230 |

Source: [`sample_selection_audit.csv`](../part2-iter3/results/sample_selection_audit.csv).

The input checks require catalogue and morphology matches, finite magnitude and kinematic values, positive dispersion and non-negative dispersion uncertainty. The early-type selection includes `TYPE = 0, 0.5, 1`; the strict elliptical sample uses `TYPE = 0`. When several candidates survive for one galaxy, the documented rule keeps the observation with the smallest relative dispersion uncertainty. All 779 candidates are already unique after the preceding filters, so this rule removes no further rows in the present run. It is not the survey's official best-observation flag. The 230 ellipticals are contained within the 779 early-type galaxies.

## Final results

| Sample | N | Slope a (mag/dex) | Intercept b (mag) | Gamma | RMS residual (mag) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Elliptical | 230 | −4.838 ± 0.235 | −10.608 ± 0.508 | 1.935 ± 0.094 | 0.637 |
| Early type | 779 | −4.704 ± 0.120 | −10.763 ± 0.261 | 1.882 ± 0.048 | 0.570 |

Values are rounded from [`fit_summary.csv`](./part3-fitting%20results/fit_summary.csv). Uncertainties are formal standard errors under the unweighted fit, not a complete error budget.

![Elliptical sample and unweighted fit](./part3-fitting%20results/elliptical_fit.png)

![Early-type sample and unweighted fit](./part3-fitting%20results/early_type_fit.png)

Both samples show the expected brightness trend. The residual scatter indicates that luminosity is not described exactly by a single straight line in this projection. The smaller RMS in the broader sample is descriptive and does not prove that this sample is physically more uniform.

The two gamma estimates are close. However, comparing a sample with its subset does not provide an independent test of morphology. These fits alone cannot establish that including elliptical/S0 and S0 galaxies alongside ellipticals has no effect, or identify a causal effect of morphology.

## Comparison with published work

The classical Faber–Jackson relation is commonly described by a luminosity exponent near four, following [Faber and Jackson (1976)](https://doi.org/10.1086/154215). Our exponents near 1.9 are substantially lower. The original work concerned a different galaxy sample and nuclear velocity-dispersion measurements, so its exponent should not be treated as an exact calibration target for this analysis.

[Nigoche-Netro et al. (2010)](https://arxiv.org/abs/1004.5496) found that fitted relation parameters depend on galaxy luminosity and the magnitude interval used. This motivates matching magnitude ranges when comparing our results with other studies. It does not demonstrate that magnitude selection causes the difference in our particular data.

Our comparison also needs consistent photometric bands, velocity-dispersion definitions and fitting conventions. The present calculation uses r-band magnitudes and the supplied `sigma_re` column, with unweighted regression in magnitude. We have not repeated the analysis under matched literature selections or alternative regression models, so we cannot assign the lower gamma to a particular cause. Nor does the discrepancy alone show that the underlying empirical relation fails.

## Limitations

- The formal errors describe uncertainty within the fitted model; they do not include all observational errors, selection effects or systematic uncertainty.
- Dispersion errors are not explicitly modelled in the regression, and the code does not fit intrinsic scatter separately from observational scatter.
- Catalogue matches, morphology classes and quality cuts determine which galaxies enter the samples. Passing a finite-value check does not by itself establish full scientific reliability.
- The analysis is restricted to the four supplied files. It does not apply additional survey quality selections available only in other catalogues.
- The two samples overlap. No separate elliptical-versus-S0 fit or independent morphology comparison has been performed here.
- The present analysis is observational and does not establish causation between luminosity and velocity dispersion.

## What the project answers and what remains open

The analysis recovers a brightness–dispersion trend in both selected samples and quantifies it with reproducible fit parameters. It does not reproduce a classical exponent near four with the current selection and regression. It also does not yet isolate why the exponent is lower or determine a distinct morphology effect.

The work highlights the need to distinguish observation counts from galaxy counts, document selection rules, and separate formal fitting errors from the full uncertainty of a scientific interpretation.

## Future investigations

1. Fit disjoint elliptical and S0 samples over comparable magnitude ranges, rather than treating the overlapping samples as independent.
2. Vary quality and magnitude cuts and record the resulting counts, fitted exponents and scatter.
3. Use a regression model that accounts for measurement uncertainty and intrinsic scatter, and assess sensitivity to regression direction.
4. Match photometric bands, dispersion definitions and sample ranges to a selected published study before comparing slopes.
5. Examine residuals against morphology and catalogue origin, and check whether a single straight line adequately describes the full range.

These are proposed extensions, not analyses already completed. Full bibliographic details are in [REFERENCES.md](../REFERENCES.md).
