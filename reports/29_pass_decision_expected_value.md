# Lesson 46: compare pass options before observing the result

## Completed worked assignment

A successful pass to a high-value zone can earn a large xT increase, but that does not automatically make it the better choice before it is played. A decision exercise also needs the probability of reaching that zone and the continuation after failure.

We use actual fitted values from lesson 44, but construct **hypothetical destinations and assumed completion probabilities**. These are not observed simultaneous choices in a match, and no pass-completion model has been trained.

Starting cell 8 has value **0.013004**. A nearer destination, cell 9, has value **0.018158**. A higher-value destination, cell 11, has value **0.103652**. Assume failure leaves zero own-team continuation value, as in the explicitly labelled diagnostic in lesson 45.

```text
Expected change = p(complete) × destination value
                + (1 − p(complete)) × failure value
                − starting value
```

- Safer option, assumed **90%** completion: expected change **+0.003339**.
- Riskier option, assumed **15%** completion: expected change **+0.002544**.
- Riskier option, assumed **20%** completion: expected change **+0.007727**.

At 15%, the safer option has higher expected value; at 20%, the riskier destination does. This is a result of the chosen assumptions, not evidence about an actual player's decision.

## Break-even calculations

With zero failure continuation, the riskier option matches the starting-zone value when `p = start / risky destination`, here **12.55%**. It matches the assumed safer option when `p = 0.90 × safe destination / risky destination`, here **15.77%**. These thresholds are algebraic outputs from the existing grid and assumptions, not empirical completion probabilities or recommended pass-selection cutoffs.

For a simpler purely illustrative example, start at 0.03. A safe destination valued 0.04 at 90% completion gives `0.90 × 0.04 − 0.03 = +0.006`. A risky destination valued 0.08 at 40% gives `0.40 × 0.08 − 0.03 = +0.002`. The more valuable destination can therefore have the smaller expected gain.

## Decision quality versus observed outcome

A pass with good expected value can fail. A pass with poor expected value can succeed. The observed outcome is one realization; it cannot alone establish whether the choice was good beforehand. However, applying this principle to an actual event requires credible probabilities and feasible alternatives. We have neither verified alternative passing lanes nor a completion model here.

Our fitted grid is location-only and training-only. Defensive positioning, pressure, receiving control, player ability, game state and the opponent's counterattack are omitted. Changing the assumed failure continuation changes the expectation too. This exercise is probability-weighted arithmetic using the educational grid, not a validated decision-value model or live tactical advice.

**Completed analyst explanation:** “Compare the expected benefit of each available option by weighting its outcome value by how likely it is. A high-value destination alone does not identify the best pass. A single success or failure does not settle the quality of the original choice.”

## Reproduce and audit

Run `python 46_pass_decision_expected_value.py`. It needs only the saved lesson-44 evidence, without raw caches, downloads or refitting. It writes `data/46_pass_decision_evidence.json` and `figures/48_pass_decision_expected_value.png`. The source hash, chosen cells, assumed probabilities and failure value are preserved explicitly.

Tests cover probability endpoints, nonzero failure continuation, invalid inputs and both equality thresholds. Evidence checks reconcile source values, each weighted expectation and threshold. The worked assignment was completed with assistance; independent user mastery is not claimed.

Method background: [Karun Singh's original xT explanation](https://karun.in/blog/expected-threat.html) develops probability-weighted location values. This separate pass-choice exercise and its completion assumptions are project-specific. Data behind the fitted grid: StatsBomb Open Data; model foundation: Soccermatics/mplsoccer.
