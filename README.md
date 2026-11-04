# Football Analytics Research Lab

**Football analytics portfolio · Python/pandas · In progress**
**Author:** Alireza Erfanian

[![Research checks](https://github.com/alirezzaww/football-analytics-research-lab/actions/workflows/evidence.yml/badge.svg)](https://github.com/alirezzaww/football-analytics-research-lab/actions/workflows/evidence.yml)

**[Explore the live portfolio](https://alireza-england-2019-research.sara-erfania-6316.chatgpt.site)** ·
[Study the source](https://github.com/alirezzaww/football-analytics-research-lab)

**Start here:** [France corner case study](reports/36_france_corner_portfolio_case_study.md) · [Employment learning plan](docs/CAREER_PLAN.md)

A growing collection of reproducible football research using StatsBomb Open Data,
covering passing involvement, expected-goals modelling and match analysis across
multiple teams at the 2019 Women's World Cup.

The current research has three connected parts:

- **England passing case study:** seven fixtures, player involvement before shots,
  reconstructed playing time and sensitivity to definitions.
- **Tournament xG evaluation:** a frozen educational model checked on 1,131 shots
  from 45 other fixtures, covering teams beyond England.
- **Match interpretation:** France–Korea Republic chance volume, average quality,
  timelines, shot locations and body-part context.

This is a guided learning portfolio built with assistant support and grounded in
Soccermatics. Individual case studies retain their own team, sample and method
limits; the broader project name does not imply professional model readiness.

A separate educational xG extension now evaluates a **frozen 114-shot model on 1,131
shots from 45 other fixtures**, with lower log loss than a frozen training-rate
baseline (0.2696 versus 0.3052). See the [fixed-model evaluation](reports/10_frozen_model_evaluation.md)
for the protocol committed before event downloads, calibration, uncertainty and limits.

## Explore the research

- **[England passing case study](docs/CASE_STUDY.md)**
- [Tournament model evaluation](reports/10_frozen_model_evaluation.md)
- [France–Korea Republic match analysis](reports/12_match_xg_summary.md)
- [Shot body-part context](reports/16_shot_body_part_context.md)
- [Methods and definitions](docs/METHODS.md)
- [Reproduce the results](docs/REPRODUCIBILITY.md)
- [Project scope and remaining work](PROJECT_BRIEF.md)

![How the shot-xG threshold changes player rates](figures/17_england_xg_threshold_sensitivity.png)

## Findings from the England passing sample

- **200 qualifying passes** across seven games: completed possession-team passes
  within 15 seconds before a same-possession England shot, excluding listed restarts.
- **113** remain when the following shot must have xG > 0.07; **98** at xG > 0.10.
- At 0.10, Kirby records **2.17 per reconstructed 90** and Bronze **1.43**, from
  12 and 11 passes. Kirby has the highest rate among outfield players meeting the
  chosen 270-minute display minimum.
- Nine of Kirby's 12 selected passes **started inside the final third**, while only
  two **entered it from outside**. Those are different contributions.

These are descriptive findings from a small tournament sample. They do not establish
player superiority, assists, causal chance creation or statistical significance.

## Skills demonstrated by the guided workflow

Event acquisition and filtering; possession/time matching; totals versus rates;
playing-time reconstruction; definition sensitivity; spatial analysis; evidence
reconciliation; reproducible, qualified reporting. The code was prepared with assistance;
the learning journal distinguishes coverage from independent practice.

## Run in Spyder or a terminal

Use **Python 3.11** on Windows, macOS or Linux. Clone this repository, open its
folder in a terminal, then follow [the setup guide](docs/REPRODUCIBILITY.md).
After installing `requirements-core.txt`, run the core research pipeline:

```bash
python scripts/run_research.py --headless
```

For Spyder, select your environment's interpreter and open the numbered lesson files.
The runner executes tournament stages 11, 13–26 and 28 and then validates saved evidence.
The early numbered files remain independent learning exercises.
Internet is needed to acquire source data. Raw events are cached locally and ignored
by Git; saved derived evidence and figures are included for immediate study.
You can inspect the saved evidence without installing analysis libraries:

```bash
python scripts/check_evidence.py
```

## Educational xG modelling extension

`18_first_xg_model.py` adapts [Soccermatics Lesson 2](https://soccermatics.readthedocs.io/en/latest/gallery/lesson2/plot_xGModelFit.html)
to both teams' non-penalty shots in our seven cached fixtures. A distance-only
logistic regression trains on 114 shots from the first five matches and tests on
36 from the final two. Test Brier error is 0.1315 versus 0.1438 for a constant
training-goal-rate baseline. This tiny selected sample is for learning, not a
validated scouting model. It excludes angle, body part and defensive context.
Run `python 18_first_xg_model.py` after creating the raw cache in lesson 13.

![First educational xG model](figures/21_first_xg_distance_model.png)

## Repository guide

- `01_*.py`–`10_*.py`: foundational guided lessons and single-match analyses.
- `11_*.py`–`17_*.py`: tournament selection, rates, sensitivity, profiles, match variation and passing-volume comparison.
- `figures/`: charts with scope and source captions.
- `data/`: derived evidence and source-input manifest; raw cache is ignored.
- `docs/`: case study, methods, reproduction and résumé presentation.
- `reports/`: earlier England–Sweden shooting assessment.
- `LEARNING_JOURNAL.md`: findings, limitations, practice and progress.

## Status

The descriptive pipeline is implemented. Match variation, weighted rates and qualifying share of completed passes are examined. Role-specific comparison,
opportunity adjustment, statistical uncertainty and video review remain future work.
The passing case study uses provider xG. A separate educational distance-only xG
model is now implemented in lesson 18; no general predictive reliability, significance
test or finished recruitment recommendation is claimed.

[Learning journal](LEARNING_JOURNAL.md) · [Lesson archive](docs/LEARNING_GUIDE.md)
· [Résumé presentation](docs/RESUME.md)

## Sources and acknowledgement

Data: **[StatsBomb Open Data](https://github.com/hudl/open-data)**, competition 72,
season 30. Source data retains the provider's [licence](https://github.com/hudl/open-data/blob/master/LICENSE.pdf);
this project grants no additional data rights.

![StatsBomb](assets/statsbomb-logo.png)

Foundation: [Soccermatics pass heat maps](https://soccermatics.readthedocs.io/en/latest/gallery/lesson1/plot_PassHeatMap.html)
and [passing networks](https://soccermatics.readthedocs.io/en/latest/gallery/lesson1/plot_PassNetworks.html).
Methods and code were adapted and extended with assistant support. xG is supplied
by StatsBomb for the passing analysis. Lesson 18 separately trains a small
educational model from shot outcomes, without using provider xG as an input.

## Reuse, contribute and deploy

Original code and documentation are released under [MIT](LICENSE). Provider data,
derived records, course adaptations and logos have [separate notices](THIRD_PARTY.md).
See [contributing](CONTRIBUTING.md) and [citation metadata](CITATION.cff).

The responsive static website lives in `web/`. Read [deployment and device support](docs/DEPLOYMENT.md)
to serve or publish your own copy. The website is readable on phones and computers;
Python analysis runs in a computer environment.

## Latest lesson: testing the time window

[Lesson 19](lessons/0001-time-window-sensitivity.html) and its
[research report](reports/02_time_window_sensitivity.md) compare 5, 10 and 15 seconds
before shots while keeping xG > 0.10 and playing-time denominators fixed. Selections
contain 38, 68 and 98 passes. Walsh's comparison with Bronze changes with the window.
Run `python 19_time_window_sensitivity.py` in Spyder or a terminal. The lesson HTML
can be downloaded and opened locally; GitHub displays its source.

## Passing context: compare within starting thirds

[Lesson 20](lessons/0002-pass-location-context.html) adds a
[spatial denominator comparison](reports/03_pass_location_context.md), preserving a
2,837-pass audit ledger and within-third summaries for all players. Kirby's attacking-third
qualifying share is 9/57 (15.8%), compared with Bronze's 7/81 (8.6%). These are
completed-pass shares, not completion rates or overall player-quality ratings.
Run `python 20_pass_location_context.py` after caching events with lesson 13.

## Match-sample uncertainty

[Lesson 21](lessons/0003-match-bootstrap-uncertainty.html) adds a
[paired match-bootstrap demonstration](reports/04_match_bootstrap_uncertainty.md).
The observed Kirby-minus-Bronze attacking-third gap is 7.15 percentage points;
an illustrative percentile interval from 10,000 paired fixture draws is −3.19 to
+19.13 points. Only seven selected matches are available: this is not a validated
population interval, p-value or player-quality ranking. Run
`python 21_match_bootstrap_uncertainty.py` using the saved lesson-20 evidence.

## Match score context

[Lesson 22](lessons/0004-score-state-context.html) reconstructs the score immediately
before each eligible pass and [compares leading, drawing and trailing](reports/05_score_state_context.md).
England's qualifying shares are 4.34%, 2.74% and 1.96% respectively, across all starting
locations. Trailing occurs only against USA and Sweden, preventing a causal score-effect
claim. Final scores reconcile to provider metadata; same-second ordering, halftime,
shootout exclusion and own-goal handling have tests. Run
`python 22_score_state_context.py` after lesson 13; match metadata downloads once if missing.

## Compare score states on the same fixture set

[Lesson 23](lessons/0005-within-match-comparisons.html) checks
[fixture overlap](reports/06_within_match_score_comparison.md). No fixture has eligible
passes while both leading and trailing. USA and Sweden support a drawing/trailing
comparison: 0/120 versus 12/611 when pooled over those same two fixtures. This reverses
the seven-match pooled ordering, showing why group composition must accompany a
percentage comparison. Game phase and other context remain uncontrolled. Run
`python 23_within_match_score_comparison.py` using saved lesson-22 evidence.

## Audit what a passing count represents

[Lesson 24](lessons/0006-passes-shots-possessions.html) inspects
[the attacks behind the trailing-pass total](reports/07_passes_shots_and_possessions.md).
The 12 selected passes link to three represented shots in three possessions, with four
passes per shot. Timelines and identity checks distinguish action counts from shot
counts and demonstrate why repeated shot xG must not be summed per preceding pass.
Run `python 24_passes_shots_and_possessions.py` after caching raw events with lesson 13.

## xG extension: test shot angle with training-only validation

[Lesson 25](lessons/0007-shot-angle-and-validation.html) compares
[constant, distance-only and distance-plus-angle candidates](reports/08_shot_angle_model_comparison.md).
Leave-one-match-out validation inside the first five fixtures selects distance-only:
log loss 0.2924 versus 0.3002 with angle. Both candidates use a common 105x68 reference
geometry and fold-local scaling. The last two fixtures are explicitly a reused check,
not a fresh final evaluation. This small educational result does not imply angle is
unimportant or establish production quality. Run `python 25_shot_angle_model.py`.

## Inspect probability calibration

[Lesson 26](lessons/0008-probability-calibration.html) adds a
[binned diagnostic](reports/09_probability_calibration.md) of the selected candidate's
114 out-of-fold predictions. The 32-shot 5–<10% group has a 7.46% mean prediction and
five goals (15.625% observed). These small, reused development groups do not establish
true individual-shot probabilities or practical model reliability. No recalibration
is fitted. Run `python 26_probability_calibration.py` using saved lesson-25 evidence.

## Check the fixed model on previously unused fixtures

[Lesson 27](lessons/0009-frozen-model-evaluation.html) adds a
[protocol-first evaluation](reports/10_frozen_model_evaluation.md) on all 45 fixtures
outside the seven development games. The model remains trained on 114 shots; it is
not refitted on the new 1,131 shots. Its probability errors are lower than the frozen
constant baseline in this fixture set. This does not establish new-season reliability,
perfect calibration or practical readiness.

Run `python 27_frozen_model_evaluation.py`, or add `--extended-evaluation` to the
headless pipeline command. The first run caches about 133 MB of raw events outside
Git. Default pipeline runs still validate the saved evaluation artifacts without
rerunning this download stage.

## Understand the learned distance pattern and its support

[Lesson 28](lessons/0010-training-pattern-and-support.html) compares
[training distance-group counts with the frozen formula](reports/11_training_distance_support.md).
The original training range is about 3.97–34.66 reference-pitch metres; 36 of the
already evaluated shots lie outside it. All 1,131 evaluation shots remain included.
This is a descriptive coverage audit, not new fitting or fresh validation. Run
`python 28_training_distance_support.py` without downloads.

## Turn shot predictions into a match brief

[Lesson 29](lessons/0011-match-xg-summary.html) distinguishes shot volume, total non-penalty xG and average shot quality using France–Korea Republic. [The report](reports/12_match_xg_summary.md) documents the frozen-model calculation and its limits. Run `python 29_match_xg_summary.py`; only one raw fixture downloads if absent. No model refitting or fresh validation.

## Follow chance creation through a match

[Lesson 30](lessons/0012-cumulative-xg-timeline.html) adds a [cumulative non-penalty xG timeline](reports/13_cumulative_xg_timeline.md) for the same fixture. Separate half clocks preserve added time, with cumulative totals carried across halftime. Run `python 30_cumulative_xg_timeline.py`; no downloads or model changes.

## Connect chance timing with shot locations

[Lesson 31](lessons/0013-shot-location-maps.html) adds [shot maps by team and half](reports/14_shot_location_maps.md) for the same fixture. Circle areas share one frozen-model xG scale and stars mark goals. Run `python 31_shot_location_maps.py` without downloads. Descriptive locations do not establish tactical causes.

## Separate shot volume from average quality

[Lesson 32](lessons/0014-shot-volume-and-quality.html) explains the identity `total npxG = shots × mean npxG per shot`. [The report](reports/15_shot_volume_quality.md) shows how the two half-to-half ratios multiply and why percentage reductions should not be added. Run `python 32_shot_volume_quality.py`; no new fitting or downloads.

## Add body-part context to the match brief

[Lesson 33](lessons/0015-shot-body-part-context.html) separates headers from foot shots using hash-verified event labels. [The report](reports/16_shot_body_part_context.md) distinguishes reporting tags from model features, and contact foot from preferred-foot status. Run `python 33_shot_body_part_context.py`; the frozen distance model is unchanged.

## Inspect the passes behind the headers

[Lesson 34](lessons/0016-header-assisting-passes.html) uses explicit reciprocal shot/pass IDs to inspect all three headers. [The report](reports/17_header_assisting_passes.md) separates corner deliveries, crossed passes, shot type and play pattern without guessing from location alone. Run `python 34_header_assisting_passes.py`; frozen probabilities remain unchanged.

## Count the corner-delivery denominator

[Lesson 35](lessons/0017-corner-delivery-rates.html) counts every recorded corner pass event, including incomplete deliveries, before calculating direct shot/goal link rates. [The report](reports/18_corner_delivery_rates.md) distinguishes direct links from later corner-phase chances. Run `python 35_corner_delivery_rates.py`; the model remains unchanged.

## Extend direct links to bounded corner phases

[Lesson 36](lessons/0018-corner-phase-analysis.html) completes a [worked phase-analysis assignment](reports/19_corner_phase_analysis.md): same possession, at most 15 seconds, with restart/period/goal boundaries. Six of France's 13 corners associate with seven shots under this rule, compared with two direct links. Run `python 36_corner_phase_analysis.py`. This is a descriptive proxy, not causal attribution.

## Check sensitivity to the corner-phase time limit

[Lesson 37](lessons/0019-corner-window-sensitivity.html) completes a [four-window robustness assignment](reports/20_corner_window_sensitivity.md) while keeping delivery and phase boundaries fixed. France has 4/13 shot-associated corners at five seconds and 6/13 at 10, 15 and 20 seconds. Run `python 37_corner_window_sensitivity.py`; this is definition sensitivity, not fresh validation.

## Phase 2: multi-match set-piece research

[Lesson 38](lessons/0020-france-tournament-corners.html) applies the fixed corner-phase method to [all five France tournament fixtures](reports/21_france_tournament_corner_study.md): 19 of 45 deliveries associate with 21 shots, with two goals. Match variation, pooled denominators and extra-time exposure are explicit. Run `python 38_france_tournament_corners.py`; missing raw caches download with hash verification. No xG inference or fresh validation.

## Compare recorded corner-delivery profiles

[Lesson 39](lessons/0021-corner-delivery-profiles.html) adds [delivery-technique groups](reports/22_corner_delivery_profiles.md) to the five-match study, retaining missing labels and all phase outcomes. Inswinging and outswinging rates are descriptive, not a causal tactical ranking. Run `python 39_corner_delivery_profiles.py`.

## Audit taker and opponent overlap

[Lesson 40](lessons/0022-corner-taker-overlap.html) checks [who supplied each technique](reports/23_corner_taker_overlap.md), retaining empty cells and missing labels. Different taker mixtures and sparse same-taker/match overlap limit tactical interpretation. Run `python 40_corner_taker_overlap.py`; no downloads or causal modelling.

## Add corner-side context before interpreting technique

[Lesson 41](lessons/0023-corner-side-context.html) checks [taker, side and match together](reports/24_corner_side_context.md). No such context contains both recorded inswinging and outswinging deliveries, limiting a direct like-for-like comparison. Run `python 41_corner_side_context.py`; this is an overlap audit, not an adjusted tactical effect.

## Map recorded corner endpoints into pitch zones

[Lesson 42](lessons/0024-corner-endpoint-zones.html) classifies [corner pass endpoints](reports/25_corner_endpoint_zones.md) into disjoint six-yard, remaining penalty-area and outside zones. All 45 deliveries remain included. Run `python 42_corner_endpoint_zones.py`; recorded endpoints do not establish intended targets or controlled receptions.

## Turn the event study into a video-review brief

[Lesson 43](lessons/0025-corner-video-review-brief.html) prepares [six sourced review examples](reports/26_corner_video_review_brief.md) across five opponents, covering endpoint zones and phase-shot outcomes. Run `python 43_corner_video_review_brief.py` to regenerate the queue and report. The brief is complete; video observations remain unreviewed and the purposive examples are not an estimation sample.

## Phase 3: expected threat and ball progression

[Lesson 44](lessons/0026-first-expected-threat.html) fits a [first educational position-based xT model](reports/27_first_expected_threat.md) using 6,770 selected actions from both teams in five fixtures. The 6×4 grid values completed passes as destination value minus starting value. Run `python 44_first_expected_threat.py`. This is a training exercise, without independent validation or player-ranking claims.

## Check what successful-pass xT omits

[Lesson 45](lessons/0027-failed-pass-value.html) adds a [clearly labelled failure-cost scenario](reports/28_failed_pass_value.md), alongside standard completed-pass xT. Unknown outcomes remain excluded, and zero continuation is an assumption rather than verified possession loss. Run `python 45_failed_pass_value.py`; this is not a complete performance rating or a new model.

## Compare hypothetical pass risk and reward

[Lesson 46](lessons/0028-pass-decision-expected-value.html) completes a [probability-weighted decision exercise](reports/29_pass_decision_expected_value.md) using saved grid values and explicitly assumed completion probabilities. Run `python 46_pass_decision_expected_value.py` without downloads. This is not an observed-options analysis or a trained pass-completion model.

## Learn a first pass-completion model

[Lesson 47](lessons/0029-first-pass-completion-model.html) estimates [smoothed origin-zone completion probabilities](reports/30_first_pass_completion_model.md) from four fixtures and checks them on the already inspected fifth. Run `python 47_first_pass_completion_model.py` without downloads. This estimates zone context, not completion of a specific proposed passing option.

## Validate completion estimates across all five fixtures

[Lesson 48](lessons/0030-completion-match-cross-validation.html) completes [leave-one-match-out checks](reports/31_completion_match_cross_validation.md), refitting both zone counts and baseline within each fold. All 3,430 passes receive one out-of-fold prediction. Run `python 48_completion_match_cross_validation.py` without downloads; this is exploratory grouped validation of already inspected fixtures.

## Check the meaning of predicted completion percentages

[Lesson 49](lessons/0031-completion-probability-calibration.html) adds a [group calibration diagnostic](reports/32_completion_probability_calibration.md) using existing held-out predictions. The highest group averages 90.6% predicted completion versus 189/215 = 87.9% observed. Run `python 49_completion_probability_calibration.py`; predictions are unchanged and no calibrator is fitted.

## Test a recorded-pressure feature

[Lesson 50](lessons/0032-pass-completion-pressure-feature.html) evaluates [origin plus recorded pressure](reports/33_pass_completion_pressure_feature.md) on the same folds. Pooled log loss changes only from 0.480395 to 0.479978, with two folds worsening. Run `python 50_pass_completion_pressure_feature.py`; the small exploratory difference is documented without a practical-upgrade claim.

## Audit the data supporting each prediction

[Lesson 51](lessons/0033-completion-group-support.html) audits [local fitting sample sizes and smoothing weights](reports/34_completion_group_support.md) without changing the pressure model. Of 444 flagged predictions, 224 use fewer than 20 local fitting examples. Run `python 51_completion_group_support.py`; counts and formula weights are not confidence guarantees.

## Test the pitch-grid resolution choice

[Lesson 52](lessons/0034-completion-grid-resolution.html) compares [one, six, 24 and 96 origin cells](reports/35_completion_grid_resolution.md) using the same passes, folds and smoothing. The original 24-cell model has the lowest observed error among these settings; the finer grid does not improve it. Run `python 52_completion_grid_resolution.py`; this is development-data sensitivity, not a universal optimal grid.

## Portfolio milestone: report a football finding

[Lesson 53](lessons/0035-employer-facing-case-study.html) packages the audited corner work into a concise coach/employer case study, generated by `53_portfolio_case_study.py`. The employment plan links verified role requirements to the skills still to demonstrate independently. No job applications or video review are implied.

## SQL block: query the football evidence

[Lesson 54](lessons/0036-first-football-sql.html) builds a [first SQLite database and query exercise](reports/37_first_football_sql.md) from the 45 corner deliveries. Run `python 54_first_football_sql.py`; inspect the committed `sql/54_*.sql` files for counts, filters and grouped rates. The generated database is ignored by Git and rebuildable from source. Guided first exercise, not independent SQL proficiency.
