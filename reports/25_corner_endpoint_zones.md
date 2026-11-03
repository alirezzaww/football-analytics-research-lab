# Lesson 42: spatial zones for recorded corner endpoints

## Completed worked assignment

Join each of the same 45 France corner deliveries to its recorded `pass.end_location`, then classify that point into mutually exclusive zones:

- **Six-yard box:** 15 deliveries; five associated with a phase shot (**33.33%**).
- **Rest of penalty area:** 19 deliveries; 11 associated with a phase shot (**57.89%**).
- **Outside penalty area:** 11 deliveries; three associated with a phase shot (**27.27%**).
- **Endpoint unknown:** zero deliveries; no rate defined.

All 45 endpoints are recorded in this sample. Category totals reproduce the original 45 deliveries and 19 corners associated with shots. Failed deliveries remain included. Phase outcomes come unchanged from the fixed 15-second study.

## Spatial binning

Using StatsBomb's normalized attacking coordinates, define the six-yard box as 114 ≤ x ≤ 120 and 30 ≤ y ≤ 50. Define the penalty area as 102 ≤ x ≤ 120 and 18 ≤ y ≤ 62. Test the six-yard box first, then the rest of the larger penalty area: otherwise the nested boxes would double-count or mislabel points. Boundary lines are included in the most specific zone.

All other finite endpoints fall outside the penalty-area rectangle, including off-pitch endpoints if present. Missing or nonfinite locations remain Endpoint unknown, not outside. The plot uses mplsoccer to orient the original coordinates; no manual x/y swap is performed. If a recorded endpoint is behind halfway, the implementation expands to a full-pitch view rather than hiding it. The saved records preserve every point and phase outcome; point overlap can conceal individual dots visually.

Primary coordinate reference: [StatsBomb Working with R](https://blogarchive.statsbomb.com/uploads/2021/11/Working-with-R.pdf), including the penalty/six-yard rectangles. These are normalized coordinate regions, not measured venue geometry.

## What endpoints do not reveal

The point is the recorded pass end. It does not independently reveal the intended target, who controlled the ball, whether the delivery reached an attacker or the ball's curved flight path. Incomplete deliveries can have endpoints in any zone. A short corner can remain outside the penalty area and still lead to a later associated shot.

This is grouping by an observed post-delivery characteristic, not an experiment assigning target zones. Technique, taker, side, defensive actions and other circumstances can affect both where a pass ends and whether a shot follows. Therefore the higher observed rest-of-area rate is not evidence that deliberately aiming there would improve outcomes. We have not established first-contact location or intention from video.

## Completed analyst brief

“France's 45 corner deliveries had 15 recorded endpoints inside the six-yard box, 19 elsewhere in the penalty area and 11 outside it. Shot-associated phases occurred in 5/15, 11/19 and 3/11 cases respectively. These are descriptive endpoint groups; they do not identify intended targets, controlled receptions or a causal best zone.”

Next investigation: inspect first-contact/reception events and video to distinguish where the ball was intended to go from how the delivery actually developed. The current map supports selecting examples for review, not a targeting recommendation.

## Reproduce and audit

Run `python 42_corner_endpoint_zones.py`. It verifies and reuses the five-fixture source via existing hash-checked caches/downloads. Outputs: `data/42_corner_endpoint_evidence.json` and `figures/45_corner_endpoint_zones.png`. The new ledger adds only endpoint, pass-outcome label and zone to the prior records; it does not modify shot eligibility, phase outcomes or model predictions.

Tests cover nested boundaries, missing and off-pitch points, group denominators and empty rates. Evidence checks reconcile original fields, raw endpoints/outcomes when cached, zone membership and all totals. Code and worked assignment were prepared with assistance; independent user mastery is not claimed.

Data: StatsBomb Open Data. Builds on the project's Soccermatics spatial-analysis foundation; no new fitting, causal estimate or fresh validation.
