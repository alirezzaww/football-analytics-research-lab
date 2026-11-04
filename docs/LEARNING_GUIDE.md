# Guided lesson archive

Commands and script paths below are relative to the project root. This archive preserves the progression of the learning project; start with the repository README for the portfolio overview.

# Football Analytics
A practical portfolio following Soccermatics, starting with event data and shooting analysis.

Read [the practical project brief](../PROJECT_BRIEF.md) for the current case-study scope.
Read [the learning journal](../LEARNING_JOURNAL.md) for the questions, methods, verified
findings, limitations, and independent practice behind the guided examples.

## Lesson 1
`notebooks/01_statsbomb_event_analysis.ipynb` explores competitions, matches and events, calculates team/player shooting metrics, and interprets an England shot map. `figures/01_shot_map.png` is the exported figure.

## Guided Spyder lessons
Open `01_getting_started.py` in Spyder and use the interpreter `/Users/alireza/football-analytics/venv/bin/python`. Run the script to load competitions, matches, events, team/player shooting totals, and shot maps. Internet access is required. The earlier notebook remains a worked example.

- `figures/02_england_shot_locations.png`: equal-sized markers for learning coordinates.
- `figures/03_england_xg_shot_map.png`: marker area proportional to xG.
- [Written match assessment](../reports/01_england_sweden_shooting_assessment.md): evidence, interpretation, and limitations.

## Optional earlier notebook
The current lessons use the Python scripts in **Spyder** as described above.
The commands below are only for reopening the earlier notebook example.
From this project directory, use the existing Python 3.11 environment:
```sh
source venv/bin/activate
python -m jupyter notebook
```
Open the notebook and run all cells in order using the environment's Python kernel. Internet access is needed for StatsBomb downloads. To execute from the command line with this interpreter:
```sh
venv/bin/python -m jupyter nbconvert --execute --to notebook --inplace notebooks/01_statsbomb_event_analysis.ipynb
```
The environment already has the dependencies; `requirements.txt` records their installed versions. For a future fresh checkout, create a Python 3.11 environment and install that file. No installation is needed here.

## Sources and methods
Credit: **StatsBomb** for [StatsBomb Open Data](https://github.com/statsbomb/open-data). Observe the repository's attribution and usage terms when sharing analysis. Data is loaded live using `mplsoccer.Sbopen`; provider updates may change outputs. Match 69301, competition 72, season 30 (2019 Women's World Cup). xG values are supplied by StatsBomb; this lesson does not train a model. Shot goals exclude own goals; comparisons are limited to this match.

Tutorials: [Using StatsBomb](https://soccermatics.readthedocs.io/en/latest/gallery/plot_UsingStatsbomb.html) and [Plotting Shots](https://soccermatics.readthedocs.io/en/latest/gallery/lesson1/plot_PlottingShots.html).

## Learning roadmap
1. StatsBomb event data — event analysis notebook
2. Shot maps and xG — match shooting analysis (included in Lesson 1)
3. Pass maps — player and team passing analysis
4. Passing networks — team buildup visualization
5. Pass heatmaps — spatial passing analysis
6. Expected goals — simple xG model
7. Statistical scouting — player comparison dashboard
8. Expected threat (xT) — action-value analysis
9. Player clustering — similar-player identification
10. Recruitment analysis — final portfolio project

Future project: *Data-Driven Football Recruitment: Finding Similar Players Using Event Data and Machine Learning*. Current guided work covers event data, shooting, passing networks, and pass heatmaps. The later modelling and recruitment stages are future work.

## Passing lesson
Open `02_passing_analysis.py` in Spyder and run it with the existing project interpreter. This independent script loads match 69301 and draws Lucy Bronze’s passes, excluding throw-ins as in the Soccermatics player-map example. Start and end coordinates are printed in the Console. Blue arrows are completed passes; gold arrows show other recorded outcomes. Output: `figures/04_lucy_bronze_pass_map.png`.

## Passing network — in progress
`03_passing_network.py` follows [Soccermatics Passing Networks](https://soccermatics.readthedocs.io/en/latest/gallery/lesson1/plot_PassNetworks.html). Step 1 counts directed completed England pass connections before England’s first substitution, excluding throw-ins, using the explicit StatsBomb event index. It saves `data/03_directed_pass_connections.csv`. Step 2 calculates average pass/reception locations and saves `data/03_passing_nodes.csv` plus `figures/06_england_passing_nodes.png`. Step 3 combines both passing directions for each player pair and plots links with at least 3 completed passes, saving `data/03_undirected_pass_connections.csv` and `figures/07_england_passing_network.png`. Line width shows the combined pass count; lines join average player locations, not individual pass paths. Step 4 prints each player’s completed passes made and the course centralisation score, using all 220 selected passes rather than only the displayed links. This time window differs from the full-match player analysis.

## Forward passing network challenge
Open `04_forward_passing_network.py` in Spyder. It keeps completed England passes before the first England substitution, excludes throw-ins, then requires `end_x > x`. Player positions and circle sizes are recalculated from this forward-only subset. Links combine qualifying passes in both directions and require at least 3. Output: `figures/09_england_forward_passing_network.png` and `data/04_forward_*.csv`. Any increase in x qualifies; this is a direction filter rather than a progressive-pass or chance-quality measure.

Additional guided practice in script04 prints each player’s forward completed passes divided by all her completed passes (percentage). This is forward share among completions, not the success rate of attempted forward passes. Same time window and exclusions apply.

## Forward-pass success rate
`05_forward_pass_success.py` is extra practice after the course challenge. Run it in Spyder to compare completed forward passes with attempted forward passes, before England’s first substitution and excluding throw-ins. It prints missing-coordinate and Unknown-outcome exclusions, counts, and rates. This denominator includes failed forward passes and differs from script04’s forward share among completed passes.

## Heatmap introduction
`06_pass_heatmap.py` prepares for the [Soccermatics Pass heat maps lesson](https://soccermatics.readthedocs.io/en/latest/gallery/lesson1/plot_PassHeatMap.html). It counts the start locations of the same220 completed England passes before the first substitution, excluding throw-ins, across a6-by-5 pitch grid. All directions are included; each labelled zone is a raw count. Output: `figures/10_england_pass_start_heatmap.png`. This introductory adaptation does not yet implement the tutorial’s tournament-wide passes within15seconds before a shot.

## Passes before shots: the 15-second rule
`07_passes_before_shots.py` introduces the Soccermatics danger-pass definition in one match window, before England’s first substitution. It keeps completed passes made by the possession team, removes the tutorial’s listed restarts, matches England shots by match/half/possession, requires the pass to precede the shot by0–15seconds, and counts each pass once against its nearest upcoming qualifying shot. It prints actual pass/shot times for learning. This is a time-window proxy, not causal attribution or an assist count; tournament aggregation comes later.

## Plot passes before shots
Run `08_plot_passes_before_shots.py` in Spyder. It runs script07 to reuse its selection, then draws qualifying pass start/end arrows and associated shot stars. White’s22:40pass is highlighted as the6-second example. Output: `figures/11_england_passes_before_shots.png`. Arrows may overlap; several qualifying passes can belong to the same shot sequence.

## Heatmap of passes before shots
Run `09_passes_before_shots_heatmap.py` in Spyder. It runs script07 and counts the nine selected pass START locations on the same6-by-5grid as script06. Labels show rawpasscounts, not shots, success rates, or per-game tournament averages. All zonecounts sumto9; the smallsample describes thismatchwindow only. Output: `figures/12_england_passes_before_shots_heatmap.png`.

## Full-match passes before shots
`10_full_match_passes_before_shots.py` reuses events from script07, removes the first-substitution cutoff, and reapplies the same possession-team/completion/restart/15-second filters across both halves. Each pass is counted once against its nearest upcoming qualifying shot in the same half and possession. The earlier nine qualifying pass IDs must be included. Output: `figures/13_england_full_match_passes_before_shots_heatmap.png`. Counts are raw totals for one match, not rates or tournament averages.

## Tournament heatmap per game
Run `11_tournament_passes_per_game.py` in Spyder. It loads all seven England matches in the2019WorldCup and applies the existing pass-before-shot rules to fullmatches. Total200 qualifyingpasses;200/7=28.57perteamgame. Eachzonecount is dividedbyall7matches. Output: `figures/14_england_tournament_passes_before_shots_per_game.png`; exactcounts/rates andselectedpassIDs: `data/11_tournament_passes_evidence.json`. TheSwedencount reproduces18. Per-game averages do not adjust for possession or player minutes.

## Player contributions before shots
Run `12_players_passes_before_shots.py` after script11 has saved its evidence JSON. It groups the same200passes by passer and divides each total byall7Englandteamgames. The chart displays the top10of18passers; allcounts sum200. Bronze28/7=4.00; Kirby24/7=3.43. Output: `figures/15_england_players_passes_before_shots.png`. This describes contribution perteamgame, not performance adjusted for minutes or appearances.

## Playing time, per90 and the shot-quality challenge
Run `13_minutes_and_shot_quality.py` after lesson11. It uses/downloads the seven raw StatsBomb event files into `data/cache_2019_events/`, reconstructs registered playing intervals (added time included, halftime excluded, temporary injury absences retained), and adjusts for substitutions and dismissals. It reproduces the200originalpassIDs, then selects113unique passes before shots with xG strictly above0.07. It filters shots before matching/deduplicating passes. Chart16compares per90rates for outfield players with270+reconstructedminutes; allplayersremainintheJSONevidence. Output: `figures/16_england_passes_per90_shot_quality.png`; audit: `data/13_minutes_and_quality_evidence.json`. Course threshold and display minimum are choices, not quality guarantees.

## Threshold sensitivity and a player profile
Run `14_threshold_sensitivity.py` after script 13. It compares shot-xG thresholds
0.07 and 0.10 using the same minutes and matching rules, preserving the baseline.
Then run `15_kirby_passing_profile.py` to examine Kirby's 12 selected passes at
0.10, including nine final-third starts and two final-third entries. Figures 17
and 18 and their JSON evidence record the outputs. The project brief describes
what is complete and what remains before a defensible portfolio assessment.

## Lesson 29: write a match brief

Use [the match-summary lesson](../lessons/0011-match-xg-summary.html) and run `29_match_xg_summary.py` in Spyder. Distinguish volume (shots), combined expectation (npxG) and average quality (npxG/shot). Submit a two-sentence coach brief with a limitation for feedback.

## Lesson 30: follow the timeline

Run `30_cumulative_xg_timeline.py` in Spyder and use [the timeline lesson](../lessons/0012-cumulative-xg-timeline.html). Explain a jump, a flat stretch and the halftime carry-forward. Then describe the half contrast and propose one video question without claiming a cause.

## Lesson 31: connect the pitch and timeline

Run `31_shot_location_maps.py` and read [the shot-map lesson](../lessons/0013-shot-location-maps.html). Describe changes in volume and average distance, then formulate a video question. Keep distance-only model limitations visible.

## Lesson 32: explain a changing xG total

Run `32_shot_volume_quality.py` and use [the volume/quality lesson](../lessons/0014-shot-volume-and-quality.html). Distinguish count, average and total; multiply retained proportions rather than adding percentage reductions.

## Lesson 33: add football context carefully

Run `33_shot_body_part_context.py` and read [the body-part lesson](../lessons/0015-shot-body-part-context.html). Explain why a reporting column does not change model predictions and why Left Foot does not establish weak-foot status.

## Lesson 34: trace a chance through linked event IDs

Run `34_header_assisting_passes.py` and read [the header-link lesson](../lessons/0016-header-assisting-passes.html). Explain the reciprocal ID join and why selecting headers cannot establish corner conversion efficiency.

## Lesson 35: define a corner rate

Run `35_corner_delivery_rates.py` and read [the denominator lesson](../lessons/0017-corner-delivery-rates.html). Explain why 2/2 and 2/13 answer different questions, and why no direct shot link does not prove no later chance.

## Lesson 36: bounded sequence analysis

Run `36_corner_phase_analysis.py`; [the compact lesson](../lessons/0018-corner-phase-analysis.html) and [completed worked assignment](../reports/19_corner_phase_analysis.md) show why phase boundaries alter shot association without changing the delivery denominator.

## Lesson 37: challenge an analysis assumption

Run `37_corner_window_sensitivity.py`. [The compact lesson](../lessons/0019-corner-window-sensitivity.html) and [completed worked assignment](../reports/20_corner_window_sensitivity.md) compare fixed-boundary 5/10/15/20-second windows. Separate definition sensitivity from sampling uncertainty.

## Phase 2 / Lesson 38: repeat a fixed method across fixtures

Run `38_france_tournament_corners.py`. [The lesson](../lessons/0020-france-tournament-corners.html) and [completed study](../reports/21_france_tournament_corner_study.md) cover complete fixture selection, pooled exposure, match variation and explicit extra-time inclusion.

## Lesson 39: compare a tactical category

Run `39_corner_delivery_profiles.py`. [The lesson](../lessons/0021-corner-delivery-profiles.html) and [completed report](../reports/22_corner_delivery_profiles.md) cover inswinging/outswinging groups, missing labels and confounding.

## Lesson 40: check comparison support

Run `40_corner_taker_overlap.py`; [the compact lesson](../lessons/0022-corner-taker-overlap.html) and [worked audit](../reports/23_corner_taker_overlap.md) explain taker mix, confounding and sparse overlap.

## Lesson 41: add side to the comparison

Run `41_corner_side_context.py`. [The lesson](../lessons/0023-corner-side-context.html) and [completed audit](../reports/24_corner_side_context.md) show how adding side changes the observed overlap within taker/match contexts.

## Lesson 42: spatial binning

Run `42_corner_endpoint_zones.py`. [The lesson](../lessons/0024-corner-endpoint-zones.html) and [completed report](../reports/25_corner_endpoint_zones.md) cover disjoint nested boxes, missing points and careful endpoint interpretation.

## Lesson 43: prepare a practical review brief

Run `43_corner_video_review_brief.py` and read [the compact lesson](../lessons/0025-corner-video-review-brief.html). [The generated brief](../reports/26_corner_video_review_brief.md) completes example selection and observation-question preparation; actual video review requires footage and remains unperformed.

## Phase 3 / Lesson 44: value a pass with expected threat

Run `44_first_expected_threat.py`. [The lesson](../lessons/0026-first-expected-threat.html), [worked report](../reports/27_first_expected_threat.md) and [reference](../reference/expected-threat.html) introduce location value and end-minus-start pass scoring. The model is a descriptive training fit, not independently validated.

## Lesson 45: outcome coverage in pass valuation

Run `45_failed_pass_value.py`. [The lesson](../lessons/0027-failed-pass-value.html) and [worked report](../reports/28_failed_pass_value.md) compare successful-pass scoring with an explicit assumed-loss scenario, preserving unknown outcomes and interpretation limits.

## Lesson 46: probability-weighted options

Run `46_pass_decision_expected_value.py`; [the lesson](../lessons/0028-pass-decision-expected-value.html) and [worked report](../reports/29_pass_decision_expected_value.md) compare a safer and riskier hypothetical option. Completion probabilities are assumptions, not learned predictions.

## Lesson 47: learn completion from training counts

Run `47_first_pass_completion_model.py`. [The lesson](../lessons/0029-first-pass-completion-model.html) and [worked report](../reports/30_first_pass_completion_model.md) cover empirical probabilities, training-only smoothing and exploratory fixture-separated scoring.

## Lesson 48: repeat whole-match checks

Run `48_completion_match_cross_validation.py`. [The lesson](../lessons/0030-completion-match-cross-validation.html) and [worked report](../reports/31_completion_match_cross_validation.md) cover fold-local counts, whole-fixture exclusion and pooled out-of-fold metrics.

## Lesson 49: inspect numerical probabilities

Run `49_completion_probability_calibration.py`; [the lesson](../lessons/0031-completion-probability-calibration.html) and [worked report](../reports/32_completion_probability_calibration.md) compare average predictions with completed/attempted counts in groups. No recalibration is fitted.

## Lesson 50: evaluate an extra feature

Run `50_pass_completion_pressure_feature.py`. [The lesson](../lessons/0032-pass-completion-pressure-feature.html) and [worked report](../reports/33_pass_completion_pressure_feature.md) compare the same passes/folds with a recorded-pressure feature and hierarchical smoothing. Report the tiny, inconsistent result honestly.
