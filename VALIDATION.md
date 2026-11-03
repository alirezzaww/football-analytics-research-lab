# Validation record

Updated: 30 October 2026.

- Saved-evidence checker passed with all seven cached raw-input hashes verified.
- Checker also passed in a clean temporary directory without the raw cache or
  third-party dependencies.
- Selected pass IDs, 200-pass baseline, 113/98 threshold subsets, player-time totals,
  per-90 rates and Kirby spatial counts reconcile.
- Python source compiled successfully. Local Markdown links and referenced images resolve.
- Installed `requirements-core.txt` successfully into a new Python 3.11 virtual
  environment on macOS. Ran `scripts/run_research.py --headless` in a clean project
  copy without an existing event cache. All stages (11, 13–18) and evidence checks
  completed. All seven regenerated evidence files matched saved results within
  1e-10 numerical tolerance; all seven raw-input hashes verified.
- Analysis stages were executed and charts inspected during the guided project.
- [Initial public GitHub Actions run](https://github.com/alirezzaww/football-analytics-research-lab/actions/runs/41046075862)
  passed on Windows, macOS and Ubuntu. It checks saved evidence, website assets/data,
  browser script syntax and Python compilation. It does not install the full plotting
  environment or rerun network-dependent analysis on all three operating systems.
- Browser inspection at phone and desktop widths found no page-wide horizontal
  overflow; all chart images loaded. Selecting xG > 0.07 updated the table to 113
  passes. Moving the distance slider from 15 to 25 changed its estimate from 10.2%
  to 3.1%. This is responsive browser verification, not testing on every physical device.
- Website assets and JSON mirror reconcile with the original figures and research
  evidence. Sites reported a successful public production deployment.

These checks support artifact consistency and inspection. They do not establish
statistical significance, tactical causality or general player quality.

Match-variation evidence now reconciles by fixture against the selected pass IDs and
player intervals, including absence handling, pooled rates and leave-one-out results.

Passing-volume evidence reconciles 98 selected events against 2,837 eligible completed
passes; per-player shares and the volume × share decomposition match per-90 rates.

Lesson 18 executed successfully: optimiser converged; 114/36 match-disjoint split;
training-only scaling and all stored probabilities/test scores reconcile independently.
Figure 21 visually inspected. No external or general model-quality claim is inferred.

## Lesson 19 validation — 30 October 2026

The new time-window script ran successfully in the project environment. The resulting
figure was visually inspected. Counts are 38, 68 and 98 for inclusive 5, 10 and 15
seconds at fixed xG > 0.10. The evidence checker reconciles every selected ID, player
count, unchanged minutes and per-90 rate. With the raw cache present, it independently
reconstructs all three selections from all seven matches. The 15-second set equals
the existing 98-pass selection. Python compilation, website mirror checks and local
link checks pass. This extension does not rerun or alter the educational xG model.

## Lesson 20 validation — 30 October 2026

The new script executed successfully in the project environment and figure 23 was
visually inspected. All 2,837 eligible event IDs and starting locations reconcile to
cached raw inputs across seven matches; the selected subset is exactly the original
98 events. Per-player totals match lesson 17. Three offline unit tests cover zone
boundaries/invalid coordinates, missing denominators versus measured zero, and
pooled counts versus an unweighted mean. Saved-evidence checks validate every zone,
count, percentage and empty cell. Full CI results are available under the repository's
Actions tab for the published commit; local checks alone do not imply remote success.

## Lesson 21 validation — 30 October 2026

The match-bootstrap script ran successfully and figure 24 was visually inspected.
Fixture summaries reconcile to the attacking-third ledger. All 10,000 valid draw
differences replay exactly using the saved seed; no zero-denominator draw occurred.
Observed shares, percentage-point difference and linear-interpolated interval endpoints
reconcile. Four new unit tests cover pairing, repeated counts, zero exposure and
quantile interpolation. Numerical consistency does not validate interval coverage
with seven selected fixtures. Remote checks are recorded under the published commit
in GitHub Actions.

## Lesson 22 validation — 30 October 2026

The score-state script ran and figure 25 was visually inspected. All seven final
scores reconcile to provider match metadata. All 2,837 pass identities and 98 selected
flags match lesson 20. Goal timelines, pre-pass scores, state labels and all team,
player and fixture denominators reconcile; the raw-event audit independently verifies
all seven fixtures. The newly cached metadata SHA-256 is checked when present.
Four new unit tests exercise same-second event ordering, halftime/shootout handling,
own-goal counterparts and empty state denominators. These tests cover synthetic
own-goal cases; none occurs in the seven research fixtures.

## Lesson 23 validation — 31 October 2026

The fixture-overlap script ran successfully; figure 26 was visually inspected. All
coverage cells and pairwise pools reconcile to the unchanged lesson-22 ledger.
Drawing/Trailing common fixtures are exactly USA and Sweden; Leading/Trailing has
none and its restricted comparison is undefined. Three new tests cover positive
exposure with zero qualifiers, missing overlap and pooled counts with unequal fixture
sizes. No new source data or interval estimation is introduced.

## Lesson 24 validation — 31 October 2026

The new script ran successfully and figure 27 was visually inspected. All 12 pass
IDs match the selected trailing subset; the three assigned shots and possessions,
nominal time gaps, event order, shooters, outcomes and xG match cached raw data.
Scores before the shots reconcile to the saved goal timelines. The represented-shot
sum and intentionally duplicated demonstration sum reconcile separately. Four new
unit tests cover aggregation units and duplicate/conflicting identity handling.

## Lesson 25 validation — 31 October 2026

The new model-comparison script executed successfully. All 12 logistic optimisations across the five folds plus final training converge;
the six constant baselines use analytic fitting-subset goal rates. Figure 28 was visually inspected. Six new
offline tests cover goalpost geometry, symmetry/equal distances, invalid coordinates,
grouped folds, probability scoring and stored scaling. The evidence checker verifies
angles independently by vector dot products, fold-local means/scales and likelihood
gradients, every held-out/reused-check prediction, all metrics and the selection rule.
This validates numerical consistency, not general predictive reliability.

## Lesson 26 validation — 31 October 2026

The calibration script ran successfully and figure 29 was visually inspected. All
114 records match the selected lesson-25 candidate's out-of-fold predictions, with
no last-two-fixture rows included. Every shot belongs to exactly one fixed band;
all counts, goals, prediction sums and rates reconcile. Four tests cover boundaries,
probability means versus observed fractions, missing/zero distinctions and invalid
or duplicate records. No new model fit or claim of reliable calibration is made.

## Lesson 27 validation — 31 October 2026

Frozen protocol was committed before new event downloads. The fixed evaluation ran
successfully and figure 30 was visually inspected. Counts are 45 fixtures, 1,131
included shots and 103 goals; 29 excluded events comprise 22 penalties and seven
shootout shots. No fit was changed. All new raw hashes, fixture teams and every
included/excluded shot record reconcile. Fixed probabilities, both scoring metrics,
match loss sums and calibration cells reconcile independently. All 5,000 paired
match-bootstrap draws replay from the protocol seed. Four new tests cover membership,
losses, repeated match totals and paired resampling. These checks support numerical
integrity, not general professional suitability.

## Lesson 28 validation — 1 November 2026

The support script ran successfully and figure 31 was visually inspected. All 114
training shot identities and all 1,131 evaluation identities partition exactly once;
counts, goals, rates, full-precision bounds and actual frozen-model outputs reconcile.
The frozen protocol digest is unchanged. Six tests cover band boundaries, range
endpoints, missing versus measured-zero groups, pooled rates and pipeline ordering.
No source events, model fit or prior evaluation inclusion criteria were changed.

### Lesson 29 (2026-11-03)

Match summary executed with the frozen probabilities and hash-verified raw fixture. Saved shot identity, probability and aggregate reconciliation are covered by unit tests; raw team/timing verification runs when cache is present. This is descriptive interpretation, not a new validation dataset or a model update.

### Lesson 30 (2026-11-03)

Executed the timeline from the committed lesson-29 ledger without downloads or fitting. Independently reconciled shot steps, half totals and final totals in unit tests; covered added-time period boundaries, halftime carry-forward and empty halves. Inspected the saved chart for labels and full y-range visibility.

### Lesson 31 (2026-11-03)

Executed the map from the saved match ledger, verified all 26 shots fit the displayed half, and inspected panel layout and common marker-size legend. Evidence checker reconciles source digest, unique panel membership, counts, average distances, xG and prior timeline totals. No new fitting or validation data.

### Lesson 32 (2026-11-03)

Executed the volume/quality calculation from the saved ledger. Tests cover multiplicative changes, undefined empty-half means and saved-artifact reconciliation. Evidence checks independently reconcile counts, half xG and ratios to the existing map records. Chart visually inspected. No refitting or new evaluation.

### Lesson 33 (2026-11-03)

Reconstructed the existing match ledger against hash-verified raw events, then joined body-part labels by shot ID. Evidence checker reconciles tags, full original probabilities, counts, goal outcomes, memberships and group means; raw label checks run when cached. Unit tests cover explicit contact categories, unknown labels and absent groups. Chart inspected. No fitting or new validation.

### Lesson 34 (2026-11-03)

Executed all-three-header pass inspection with raw SHA256 verification. Tests cover valid reciprocal links, absent/unavailable links and mismatched type/team/period/order/possession/shot IDs. Saved evidence reconciliation checks header identity and unchanged probabilities; cached raw events additionally verify pass attributes and context. Inspected the three-panel chart. No new model or video review.

### Lesson 35 (2026-11-03)

Executed all-corner selection with the existing raw hash check. Unit tests verify inclusion of unlinked deliveries and distinguish zero observed rates from undefined empty exposure. Evidence checker reconstructs all raw corner IDs, direct reciprocal links, team/half summaries and denominators when cached; saved aggregate reconciliation is cache-free. Chart inspected. No xG model changes.

### Lesson 36 (2026-11-03)

Executed the fixed-rule phase scan, preserving millisecond timing and unique shot assignments. Tests cover exact 15-second inclusion, added time, possession/period/restart stops, multiple shots and goal/own-goal stops. Saved evidence checks reconcile protocol/source digests and team rates; cached raw replay verifies each phase membership and stop reason. Chart inspected. Descriptive reuse, not fresh validation.

### Lesson 37 (2026-11-03)

Executed four chosen windows with all other phase rules unchanged. Unit check covers a shot 5.003 seconds after delivery. Evidence checks reconcile hashes, denominators, unique/nested shot memberships, aggregate rates and exact 15-second reproduction; cached raw replay verifies every window membership and stop. Chart inspected. No new data or model fitting.

### Phase 2 / Lesson 38 (2026-11-03)

Executed the five-fixture study from SHA256-verified raw events. Verified all France fixtures from the existing metadata, unique assignment within each fixture, explicit extra-time counts, pooled denominators and exact original-fixture memberships. Cached raw replay checks each phase. Unit tests cover delivery-weighted pooling and undefined empty exposure. Chart inspected; no xG inference or new validation.

### Lesson 39 (2026-11-03)

Executed technique join on all five hash-verified raw files. Unit tests cover category/missing-label handling and all-delivery denominators. Evidence checks preserve exact source corner order, original phase outcomes, group IDs and totals; cached raw labels and takers reconcile. Chart inspected. No new model or causal comparison.
