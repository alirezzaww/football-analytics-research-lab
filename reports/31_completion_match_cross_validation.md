# Lesson 48: check the completion model across every fixture

## Completed worked assignment

The previous result used one held-out fixture. This extension checks the same fixed starting-zone model family and smoothing strength across all five fixtures with **leave-one-match-out cross-validation**. Each fold fits on the other four whole matches, using both teams, and predicts only the omitted match. Every eligible pass receives exactly one out-of-fold prediction.

We reuse all **3,430 known-outcome selected passes**. No xT values, destination coordinates, previous fitted predictions or held-out labels enter the fit. The global baseline is also recomputed from that fold's training matches. Smoothing strength stays 20; no tuning or model-family selection is performed here.

## Results

Held-out fixture log loss, zone model versus fold training-rate baseline:

- Korea Republic: **0.396493 versus 0.410253**.
- Norway: **0.541687 versus 0.574986**.
- Nigeria: **0.460556 versus 0.488240**.
- Brazil: **0.520940 versus 0.555375**.
- USA: **0.501806 versus 0.522044**.

The zone model has lower log loss in each observed fold. Pooling all out-of-fold predictions gives:

- Zone model: **log loss 0.480395**, **Brier 0.153225**.
- Constant fold baseline: **log loss 0.505889**, **Brier 0.161929**.

The pooled scores weight every pass equally. They are not a simple equal-weight average of match scores. The USA fold exactly reproduces lesson 47's fitted model, counts, predictions and error result.

## Why omit the whole match?

Passes in one match share players, opponents, match conditions and tactical context. A random pass split can put these shared conditions into both training and check sets. Grouping by fixture directly asks whether the method predicts another match within this observed sample. Every count and baseline must be fitted inside each fold; calculating a zone rate from all five matches first would use held-out outcomes.

The [scikit-learn LeaveOneGroupOut documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html) describes the general method; our implementation uses match IDs as groups and standard-library counting, without adding a scikit-learn dependency.

## What this supports

**Completed analyst statement:** “With training-only zone counts and a fixed smoothing setting, the origin-zone completion model had lower log loss than a constant training-rate baseline in all five held-out fixtures. This is exploratory evidence within a small tournament sample; it does not establish calibrated probabilities or reliable completion predictions for specific pass options.”

All five match files were already inspected before this exercise. These are development-data grouped results, not five untouched tests. France appears in every fixture, and other shared conditions persist, so fixture grouping does not remove all dependence or guarantee generalization. Some folds train on matches later than the held-out fixture; this is not a chronological future-forecast test. No significance interval, team/player holdout, new-season evaluation or practical readiness claim is made.

A success here does not improve the feature set: the model still gives every pass starting in the same cell the same probability. Its conditional calibration and option-specific limitations remain questions for further analysis.

## Reproduce and audit

Run `python 48_completion_match_cross_validation.py`. It uses saved lesson-47 records only, without network, raw caches or xT refitting. Outputs: `data/48_completion_match_cv_evidence.json` and `figures/50_completion_match_cross_validation.png`. Each fold preserves its training IDs, counts, baseline and smoothed probabilities; every out-of-fold pass is saved with the true outcome and both predictions.

Tests change a held-out match's labels and verify that its fitted model and probabilities do not change, while its error scores do. They also check whole-fixture exclusion and unique predictions. Evidence checks independently reconstruct all fold counts, smoothing, predictions and pooled scores, with exact lesson-47 reproduction.

Worked assignment completed with assistance; independent mastery is not claimed. Data: StatsBomb Open Data; original model and smoothing remain educational project choices.
