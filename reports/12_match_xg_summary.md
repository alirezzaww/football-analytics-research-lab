# Lesson 29: from shot predictions to a match brief

**Question:** Did France generate more shots, better average chances, or both against Korea Republic?

We use the first chronological fixture in the already inspected 45-match evaluation set: France–Korea Republic, 7 June 2019 (22921). This selection follows protocol order, not a search for a striking result. No model was refitted, and this is not fresh validation.

The frozen educational distance model assigns France's 21 non-penalty shots **1.643 npxG**, averaging **0.078 per shot**. Korea Republic's five shots receive **0.157 npxG**, averaging **0.031 per shot**. The corresponding shot goals are four and zero. These are our model's estimates, not StatsBomb's supplied xG.

France had more attempts and higher average estimated chance quality under this model. The summary supports a chance-generation description; it does not establish tactical causes, finishing skill, possession control or who deserved to win. The model uses distance only and was fitted on 114 shots.

## Calculation

- Total non-penalty xG: add each included shot's probability once.
- Average non-penalty xG per shot: divide that total by the number of included shots.
- Actual shot goals: count goal outcomes among those same shots.

For illustration, probabilities 0.10 + 0.20 + 0.30 sum to 0.60 xG, and their mean is 0.20 xG per shot. The total is an expected goal count for the observed chances under the model, not a 60% chance of winning or a guaranteed score. Summing expectations does not require independent shots; interpreting a replay or a goal-count distribution needs additional assumptions. Rebounds can belong to the same attacking sequence, so do not treat the observed chance set as a literal replay of the match.

## Reproduce and audit

Run `python 29_match_xg_summary.py` in Spyder's environment. It uses saved frozen probabilities and joins shot IDs to the original events for team identity. It verifies the recorded raw-event SHA256 and downloads only that one fixture if its ignored cache is absent. A changed upstream file causes an error, rather than silently changing the source. The committed derived ledger allows cache-free reconciliation in unit tests; when raw data are available, the tests also verify team and timing fields.

Outputs: `data/29_match_xg_evidence.json` and `figures/32_match_xg_summary.png`. Includes non-penalty shots only; excludes shootouts and own-goal events as shot goals. In this fixture the included shot goals match the 4–0 score; that equivalence should not be assumed for every match.

Data: [StatsBomb Open Data](https://github.com/statsbomb/open-data). Conceptual source: [Hudl StatsBomb xG explanation](https://www.hudl.com/blog/expected-goals-xg-explained), including average shot quality. Course foundation: [Soccermatics xG model fitting](https://soccermatics.readthedocs.io/en/latest/gallery/lesson2/plot_xGModelFit.html). This lesson is a project extension, not a copied course exercise.

Implementation prepared with assistance. Independent task: write two sentences distinguishing France's shot volume from its average chance quality, and add one limitation. Completion is not recorded until the user submits an interpretation.
