# Lesson 52: choose the number of pitch boxes using evidence

## Completed worked assignment

Earlier, we chose a 6×4 grid for a starting-zone completion model. This experiment varies that choice while retaining the same 3,430 passes, known outcomes, five whole-match folds and smoothing strength 20. No pressure feature, destination or xT zone value is used.

All candidate grids are recorded in `data/52_completion_grid_protocol.json` before calculation. The events and validation matches were already inspected, so this is development-data sensitivity analysis rather than an independent untouched model-selection test.

Pooled out-of-fold results, lower being better:

- **1×1, one cell:** log loss **0.505889**, Brier **0.161929**. This reproduces the fold-specific global training-rate baseline.
- **3×2, six cells:** log loss **0.486997**, Brier **0.155392**.
- **6×4, 24 cells:** log loss **0.480395**, Brier **0.153225**. This reproduces lesson 48.
- **12×8, 96 cells:** log loss **0.481989**, Brier **0.154018**.

The existing 24-cell grid has the lowest observed error among these tested settings. The 96-cell result is slightly worse, so finer location detail did not improve this particular model/setting/sample. The difference is small and no uncertainty interval or formal comparison test is supplied. Do not infer that 24 cells is universally or significantly better, or that it is guaranteed optimal outside this experiment.

## Why grid size creates a tradeoff

A single cell gives all passes the same completion estimate and loses spatial detail. Small boxes describe location more precisely but spread the training observations across more groups, increasing reliance on smoothing in sparse cells and potentially making local estimates unstable. Too coarse can miss patterns; too fine can fit noisy patterns. Both are possibilities, not proven causes of the errors here.

Average fitting observations per cell across these folds are 2,744 for one cell, about 457 for six cells, 114 for 24, and 29 for 96. These are arithmetic averages: actual cell counts differ substantially and some cells may have much less data. They are not minimum reliability guarantees.

Every grid covers the entire normalized pitch. For an nx×ny grid, column width is 120/nx and row width is 80/ny. Outer coordinates x=120 or y=80 remain in the final column/row; internal boundaries belong to the next cell. The geometry is a modelling convention, not a set of tactical field markings.

## Completed analyst explanation

“We compared four origin-grid resolutions using identical pass data and whole-match checks. The 24-cell setting had the lowest observed probability errors in this exercise, while the finer 96-cell grid did not improve it. This supports testing the resolution choice instead of assuming smaller boxes are automatically better.”

The original completion model and all earlier saved results remain unchanged. No smoothing search or additional features were introduced. Selecting a setting from these results would use this data for development; a stronger claim would require appropriate further validation. This experiment concerns completion probabilities, not refitting the xT scoring-potential grid.

## Reproduce and audit

Run `python 52_completion_grid_resolution.py`. It reads saved pass start coordinates and outcomes without raw downloads or xT refitting. Outputs: `data/52_completion_grid_evidence.json` and `figures/54_completion_grid_resolution.png`. Input event keys, each candidate's per-fold counts/references/probabilities, and every out-of-fold prediction are retained with source/protocol hashes.

Tests cover grid edges, empty cells, equivalence of one cell to a constant training baseline, and held-out label isolation. Evidence checks independently re-bin coordinates, reconstruct all fold counts and smoothing, verify identical prediction coverage, recompute scores and reproduce the original 24-cell results.

Data: StatsBomb Open Data. This extends the project's existing grouped-completion model; geometry and smoothing are educational design choices. Worked assignment completed with assistance; independent user mastery is not claimed.
