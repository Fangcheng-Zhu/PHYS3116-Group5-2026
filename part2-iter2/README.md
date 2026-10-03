# Part 2 - Iteration 2

This iteration selects galaxy samples for the Faber-Jackson analysis
using the merged catalogue produced in Part 1.

## Selection

The code keeps observations with:

- valid magnitude and stellar velocity dispersion;
- valid velocity-dispersion uncertainty;
- `bad_class == 0`;
- a reliable early-type morphology.

The early-type sample includes:

- `type = 0.0`: elliptical;
- `type = 0.5`: E/S0;
- `type = 1.0`: S0.

The strict elliptical sample only uses `type = 0.0`.

For repeated observations of the same galaxy, the observation with the
smallest `sigma_re_err / sigma_re` is selected.

## Results

- Early-type sample: 779 galaxies
- Elliptical sample: 230 galaxies
- Each sample contains one row per galaxy.

## Run

From the repository root:

```powershell
python part2-iter2/part2_iter2_sample_selection.py --input part1-iter3/results/sami_merged_observations.csv --output-dir part2-iter2/results
