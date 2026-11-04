# Lesson 51: how much data supports each prediction?

## Completed worked assignment

Audit the existing pressure-feature model without changing its fit or predictions. For every held-out pass, retrieve the number of training attempts in its starting-zone/flag subgroup and the weight placed on the broader origin estimate.

Across the 3,430 predictions:

- 268 use a subgroup with **1–19 training passes**.
- 297 use **20–49**.
- 2,865 use **50 or more**.
- None uses an empty subgroup.

Of the **444 pressure-flagged predictions**, **224** use a subgroup with fewer than 20 fitting passes and **220** use 20–49. None has 50 or more local fitting examples. These are counts of held-out predictions, not counts of distinct subgroups or independent training samples. Many passes reuse the same fitted subgroup estimate.

## How smoothing responds

Our existing candidate blends a subgroup's raw completion rate with its broader origin probability:

```text
Probability = (n / (n + 20)) × local completion rate
            + (20 / (n + 20)) × origin reference
```

This is the same count formula already used in lesson 50, rewritten to show its weights. With no local examples, the prediction falls back to the origin estimate. At 20 local examples, each term has half the weight. With many local examples, the group relies more on its own rate.

These weights are **not confidence percentages**. The chosen strength 20 and diagnostic support bands are modelling/reporting choices, not validated reliability thresholds. Fifty observations do not automatically make a subgroup reliable, and fewer than twenty does not automatically make it wrong.

## The familiar zone example

For the USA-held-out fit, starting cell 8 has:

- Not flagged: **169 completions / 184 attempts**. The origin reference gets **9.80%** of the formula weight.
- Flagged: **9 / 10**. The origin reference gets **66.67%** of the formula weight.

The common origin reference is **90.676%**. The resulting subgroup probabilities remain **91.733%** and **90.451%**. We have simply explained their existing calculation, not improved their calibration.

For a simpler illustration, if a new group has only one completed pass out of one attempt and the reference is 80%, strength 20 gives `(1 + 20×0.8)/(1+20) = 80.95%`. The model does not jump to 100% from one success. These illustration numbers are separate from the actual groups above.

## What this supports

**Completed analyst explanation:** “Adding pressure context split our origin groups, leaving many flagged predictions supported by small local training samples. The smoothing rule then relies more heavily on the broader origin estimate. This shows the data-support tradeoff of adding detail, but does not prove that small groups caused the model's tiny or inconsistent performance changes.”

Data support, calibration, relevance, annotation quality and population shift are different questions. This audit answers how much local fitting data supports each prediction; it does not estimate uncertainty intervals, show causal pressure effects or select a better model.

## Reproduce and audit

Run `python 51_completion_group_support.py`. It reads committed lesson-50 results without raw downloads or refitting. Outputs: `data/51_completion_group_support_evidence.json` and `figures/53_completion_group_support.png`. Every pass retains its source key, fitting support, raw group rate, origin prior, reference weight and unchanged probability.

Tests cover support boundaries, decreasing prior weight, invalid inputs and algebraic equivalence to the original formula. Evidence checks reconcile all subgroup counts and weights against the source fold, validate complete unique membership and reproduce each probability as a weighted average.

Assignment and implementation completed with assistance. Data: StatsBomb Open Data. This is an audit of this project's fixed smoothing convention, not a new external standard or a fresh model evaluation. Independent user mastery is not claimed.
