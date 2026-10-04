# Part 2 - Iteration 3

This iteration keeps the quality checks and sample selection from the
earlier iterations and adds morphology analysis and figures.

## Analysis

Galaxies are divided into:

- Early type: `type = 0.0, 0.5, 1.0`
- Transition: `type = 1.5`
- Spiral: `type = 2.0, 2.5, 3.0`

The analysis uses clean observations with valid magnitude, stellar mass,
velocity dispersion, and `bad_class == 0`. Repeated observations are
reduced to one row per galaxy.

## Results

- Morphology analysis sample: 2,134 galaxies
- Early type: 779
- Transition: 303
- Spiral: 1,052
- Strict elliptical sample: 230

## Outputs

- `morphology_summary.csv`
- `morphology_by_origin.csv`
- `morphology_counts.png`
- `magnitude_sigma_by_morphology.png`

The figures compare the number and distribution of galaxies in different
morphology groups. The formal Faber-Jackson fitting is left for Part 3.
