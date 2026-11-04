# Lesson 49: do the completion percentages match observed frequencies?

## Completed worked assignment

Use the **3,430 existing out-of-fold completion predictions** from lesson 48. Each pass was predicted without its match's outcomes entering the fit. Group by predicted probability, then compare the average prediction with actual completed passes divided by group attempts.

- Predictions below 60%: **174 passes**, 96 completed. Average prediction **55.76%**, observed **55.17%**.
- 60–<70%: **162 passes**, 101 completed. Average **64.42%**, observed **62.35%**.
- 70–<80%: **873 passes**, 643 completed. Average **75.20%**, observed **73.65%**.
- 80–<90%: **2,006 passes**, 1,712 completed. Average **84.71%**, observed **85.34%**.
- 90–100%: **215 passes**, 189 completed. Average **90.56%**, observed **87.91%**.

All groups reconcile to 3,430 passes and 2,741 completions. Bin edges are chosen for this descriptive diagnostic, with lower edges inclusive and upper edges exclusive except the final endpoint. No calibrator or new model is fitted.

## What the highest group means

For each of these 215 passes, the model output a value at or above 90%; their mean is 90.56%. That average is calculated from the saved predictions, not from the outcomes. Separately, the observed rate is **189/215 = 87.91%**. The average prediction exceeds the observed fraction by about **2.65 percentage points** in this group.

This describes some optimism in this sample and group. It does not prove that any individual pass's true chance is known, or that the group's underlying probability is exactly 87.91%. A high-probability pass can fail without making that prediction demonstrably wrong. Small groups and correlated match observations limit interpretation; no uncertainty interval or formal calibration test is supplied.

## Calibration versus relative model comparison

Log loss and Brier score in lesson 48 compared the whole probability predictions with real outcomes. This grouped diagnostic asks whether the numerical probabilities align with observed frequencies. Beating a constant baseline does not guarantee perfect calibration. Close overall totals also do not guarantee agreement within groups.

The groups pool different origin cells and five fitted fold models. Their apparently close frequencies cannot establish calibration within every zone, team, player or pass option. We reuse already inspected tournament matches, not a new sample; changing the model after examining this result would use this evidence for development.

**Completed analyst explanation:** “For the 215 passes predicted at 90% or higher, average model probability was 90.6%, while 189 were completed, an observed rate of 87.9%. The model was somewhat optimistic for this group in the available sample. This compares group frequencies, not known true individual probabilities.”

## Reproduce and audit

Run `python 49_completion_probability_calibration.py`. It reads the committed lesson-48 probabilities without downloads, raw caches, refitting or changing any prediction. Outputs: `data/49_completion_calibration_evidence.json` and `figures/51_completion_calibration.png`. Each group retains all original match/pass keys, counts, predicted sum and observed fraction. Empty groups have undefined means/rates rather than a made-up zero.

Tests cover exact bin boundaries, probability 1, invalid values, empty versus observed-zero groups, and predicted averages versus observed rates. Evidence checks reconcile source hash, complete unique membership and each calculation independently.

Method background: [scikit-learn probability calibration documentation](https://scikit-learn.org/stable/modules/calibration.html). Data: StatsBomb Open Data. Worked assignment completed with assistance; independent user mastery is not claimed.
