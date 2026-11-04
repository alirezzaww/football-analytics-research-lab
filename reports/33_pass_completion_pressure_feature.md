# Lesson 50: test a pressure-context feature

## Completed worked assignment

Extend the starting-zone completion model with the event's recorded `under_pressure` flag, retaining exactly the same **3,430 passes**, known outcome labels and five whole-match folds. The original origin-only predictions are reproduced exactly before comparison. A new protocol records the feature rule and fixed smoothing settings before calculating the result.

There are **444 explicitly pressure-flagged passes** in this sample. Absent/null/false flags mean **not flagged**, not independently verified absence of defensive pressure. Raw flag value and field presence are preserved. Unexpected nonboolean values raise an error rather than silently becoming a category.

## Result: little change, inconsistent across matches

Pooled out-of-fold scores:

- Origin only: **log loss 0.480395**, Brier **0.153225**.
- Origin plus recorded pressure: **log loss 0.479978**, Brier **0.153015**.

The log-loss difference is about **−0.000417**, a tiny numerical improvement. The candidate improves log loss in three folds (Korea Republic, Brazil, USA) and worsens it in two (Norway, Nigeria). We did not tune the smoothing or search other settings after seeing this result. This does not establish a meaningful, statistically reliable or generalizable improvement.

**Completed analyst statement:** “Adding recorded pressure context with fixed hierarchical smoothing changed pooled probability error very little and did not improve every match check. The experiment is documented, but it does not justify claiming a clear practical upgrade.”

## What changed in the model

Origin-only estimates use completions/attempts for each starting cell, smoothed toward that fold's global completion rate. The candidate splits each cell into two recorded-flag groups, then smooths each smaller group toward that same fold's smoothed origin estimate:

```text
Group probability = (group completions + 20 × origin probability)
                  / (group attempts + 20)
```

Every count and prior is fitted using only the other four matches. The group strength 20 was fixed for this exercise. This candidate adds a feature **and** a hierarchy for sparse groups; the comparison assesses that whole candidate, not a causal isolated effect of pressure or a formal feature-importance estimate. A zero-observation subgroup falls back to its training origin probability.

## Example from our familiar cell

For the USA-held-out fit, cell 8 had 194 training attempts and 178 completions, with origin prediction **90.676%**. Its flag split is:

- Not flagged: **169 completions / 184 attempts**, resulting smoothed prediction **91.733%**.
- Flagged: **9 / 10**, resulting smoothed prediction **90.451%**.

The groups reconcile to the same 178/194 counts. These are training counts, not actual USA completion rates. The flagged subgroup is small and therefore pulled toward the origin estimate. The numbers do not imply that pressure has little causal effect in football: event selection, labels, contexts and group size all matter.

## Feature availability and limits

The source is an event-level pressure annotation. This exercise uses it retrospectively as recorded; we have not established that it would be available before a decision in a live prediction system. In particular, an annotation associated with an event's duration should not automatically be treated as a verified pre-action observation. This remains different from reconstructing the chance of a particular proposed pass.

The candidate still does not include a feasible destination, receiving situation, player ability or complete defensive context. These five match files and their outcomes had already been inspected. Reusing them to develop a candidate is exploratory model development, not fresh validation or evidence of readiness. No causal conclusion, statistical interval, new-season test or ranking is claimed.

## Reproduce and audit

Run `python 50_pass_completion_pressure_feature.py`. It joins raw pressure tags by match/event ID using the five existing SHA256-verified caches, downloading only missing raw files. Source/protocol/raw-manifest hashes and all fold counts, priors, probabilities and metrics are saved in `data/50_pressure_feature_evidence.json`. The chart is `figures/52_completion_pressure_feature.png`.

Tests cover flag types, sparse/empty subgroup behavior and exclusion of held-out outcomes from fitting. Evidence checks independently reconcile raw flags when cached, every source ID/label, origin-model reproduction, hierarchical probabilities and all fold/pooled scores.

Source field: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Model and smoothing choices are this project's educational design. Worked assignment completed with assistance; independent user mastery is not claimed.
