# Lesson 47: learn completion probabilities from existing passes

## Completed worked assignment

The previous decision exercise assumed completion chances. We now fit a simple empirical model: estimate completion from the **starting zone** of a pass. This is a zone-context model, not a prediction of whether a specific proposed pass would succeed.

Use both teams in each fixture. Fit counts on the first four France fixtures (Korea Republic, Norway, Nigeria and Brazil), then check predictions on France–USA. The raw events for all five games were already inspected in earlier work, so this fixture separation is exploratory, not fresh independent validation. Split/rules are recorded before running this completion experiment in `data/47_completion_model_protocol.json`.

**Training: 2,808 passes, 2,253 completed — 80.24%.** The fifth-match check has **622 passes, 488 completed**. Unknown and Injury Clearance labels are excluded; all pass selection otherwise comes from the existing lesson-45 ledger, itself a filtered possession-team/non-restart sample.

## Where the probabilities come from

For each of the fixed 24 starting cells, count training pass attempts and completions. Raw completion rate is completions divided by attempts. To reduce extreme probabilities from small cells, blend that count with a training-only global reference:

```text
Smoothed probability = (zone completions + 20 × global training rate)
                     / (zone attempts + 20)
```

Twenty is a chosen smoothing strength, fixed for this exercise rather than tuned on check results or claimed as a universal standard. It acts like twenty reference attempts at the global training completion rate. A cell with no training attempts uses that reference rate; its raw rate remains undefined. A large observed cell relies more heavily on its own counts. This is a simple modelling convention, not a guarantee that uncertainty is small.

These probabilities are **completion estimates**, not xT zone values. The grid geometry is shared, but the model uses only starting-cell membership and training completion counts. It does not use any learned xT values, endpoints, test labels, the five-match xT fit or a pass-outcome feature during prediction. Actual outcome labels are used to fit training counts and score check predictions, never as prediction inputs.

## Exploratory results

- Zone model check log loss: **0.501806**; Brier score **0.161248**.
- Constant 80.24% training-rate baseline: log loss **0.522044**; Brier score **0.169339**.

The zone model has lower probability error on these 622 passes. This is a relative result on one already inspected fixture, not proof of calibrated completion chances, stable performance across competitions or practical readiness. No confidence interval, tuning search or new-season validation was conducted. The baseline percentage comes only from training passes, not the check-match rate.

## What to understand

**Completed explanation:** “Instead of assuming a probability, we calculate one from previous passes in a starting zone, with smoothing toward the overall training rate. We then compare those probabilities with the completion outcomes in a separate match. The zone model improves on the constant reference in this exploratory check, but it still cannot distinguish an easy and difficult option starting in the same zone.”

Starting location is available before a pass, unlike an observed failed-pass endpoint. But a credible option-specific model would also require appropriate pre-action information about the proposed destination, distance, receivers, pressure and defensive context. This first model provides one probability per origin zone regardless of destination. Therefore do not substitute it uncritically into lesson 46 as the success chance of a particular hypothetical choice.

## Reproduce and audit

Run `python 47_first_pass_completion_model.py`. It uses saved records only, without raw downloads or refitting xT. Outputs: `data/47_completion_model_evidence.json` and `figures/49_first_pass_completion_model.png`. Each retained pass records its ID, split, starting cell, true label and both probability predictions; exclusions remain explicit.

Tests check sparse-cell smoothing, empty cells, probability scoring and training/check fixture separation. Evidence checks independently reconstruct labels and split membership, training counts, smoothed predictions and proper probability-error scores. The map shows training-derived completion estimates and training sample sizes per cell.

Method background: [scikit-learn probability calibration documentation](https://scikit-learn.org/stable/modules/calibration.html) discusses probability evaluation and proper scoring; the group-count smoothing rule is this project's educational choice. Data: StatsBomb Open Data. Worked assignment completed with assistance; independent user mastery is not claimed.
