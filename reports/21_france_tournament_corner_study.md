# Phase 2 / Lesson 38: France's corner phases across five matches

## Research question and completed assignment

How often were France's corner deliveries associated with a shot under the same bounded phase definition across its 2019 World Cup campaign?

We select **all five France fixtures** from the existing tournament metadata, not a subset chosen by results: Korea Republic, Norway, Nigeria, Brazil and USA. Selection and counting rules are recorded in `data/38_france_corner_study_protocol.json` before running this extension. All these match files had already been inspected for the earlier xG evaluation; this is broader descriptive research, not fresh validation or a new-season test.

## Findings

- Korea Republic: **6/13 corners with a phase shot (46.15%)**; seven shots, two goals.
- Norway: **3/9 (33.33%)**; four shots, no goals.
- Nigeria: **4/9 (44.44%)**; four shots, no goals.
- Brazil: **2/7 (28.57%)**; two shots, no goals. Three of the seven deliveries occurred in extra time.
- USA: **4/7 (57.14%)**; four shots, no goals.

**Pooled result: 19/45 deliveries (42.22%)**, associated with 21 unique shots and two goals. All observed phase goals came in the Korea Republic fixture. This distinction between shot association and goal outcome prevents one productive goal-scoring match from standing in for the whole campaign.

These rates are descriptive and based on small denominators. They do not establish opponent strength, repeatable corner skill, a significant match difference or a tactical cause. No video was reviewed.

## Consistent phase rules and scope

Each corner Pass event starts a phase of at most 15 seconds inclusive. Stop at the first provider possession change, period change, new restart pass, shot goal or own-goal event. A shot can be associated with only one corner. Failed deliveries remain in the denominator. Shots are France's non-penalty Shot events; shootouts are excluded.

Periods 1–4 are included, so the Brazil extra-time corners remain. This is a delivery-level study, not a per-90 or equal-duration comparison. Retaining extra-time exposure is appropriate to this stated all-deliveries question, but its contribution is explicitly reported.

Unlike the previous educational xG model, this shot-count study requires no location/geometry filter and runs no probability inference. A qualifying non-penalty shot is eligible even if location data would be unsuitable for model geometry. The Korea Republic membership reproduces lesson 36 exactly; its broader eligibility makes no difference in that fixture. No xG values are imputed or mixed across models.

## Pool counts before dividing

Sum corners associated with a shot across matches, then divide by total deliveries: **(6+3+4+2+4)/(13+9+9+7+7) = 19/45**. This weights each delivery equally. Averaging the five match percentages would instead weight each match equally and answer a different question. Neither quantity is automatically invalid, but it must match the stated unit of analysis.

## Completed analyst brief

“Across France's five 2019 World Cup matches, 19 of 45 recorded corner deliveries were associated with at least one shot under a fixed 15-second same-possession phase rule. The phases contained 21 shots, but both observed goals came against Korea Republic. Match denominators are small, and the phase association is a definition-based description rather than causal corner value or opponent-adjusted performance.”

Follow-up research: review delivery types and attacking/defensive movement across matched video clips, and repeat the fixed method on a larger, clearly scoped sample before making team-level recommendations.

## Reproduce and audit

Run `python 38_france_tournament_corners.py`. It uses five ignored cached match files, fetching only missing files from their recorded public URLs and validating the existing SHA256 digests. It saves fixture-level corner and shot IDs, exact elapsed times, boundary reasons, source records and pooled counts in `data/38_france_corner_study_evidence.json`. The chart is `figures/41_france_corner_match_variation.png`.

Unit tests check pooled versus equal-match weighting and zero exposure. Evidence checks verify complete fixture selection, source/protocol digests, unique shot membership, extra-time exposure, pooled arithmetic and raw phase replay when caches are available. The original one-match result is reproduced. The CI checks saved artifacts without downloading the raw sources or installing plotting libraries.

Source definitions: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf); course foundation: [Soccermatics possession chains](https://soccermatics.readthedocs.io/en/latest/gallery/lesson4/plot_PossesionChain.html). Boundary rules are project-specific. Assignment and implementation completed with assistance; independent user mastery or professional impact is not claimed.
