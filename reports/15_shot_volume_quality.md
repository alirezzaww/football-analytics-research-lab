# Lesson 32: distinguish volume from average quality

**Total non-penalty xG = number of included shots × average non-penalty xG per shot.** This is an arithmetic identity, not a statistical model or causal explanation.

We retain the same France–Korea Republic fixture, shots, inclusion rules and frozen distance-only model. France's first half had 16 shots, 1.445403 model npxG, and 0.090338 per shot. Its second half had five shots, 0.197937 npxG and 0.039587 per shot.

Relative to its first half, France retained:

- 5 / 16 = **31.25% of the shot count**, a 68.75% reduction.
- 0.039587 / 0.090338 = **43.82% of average estimated quality**, a 56.18% reduction.
- 0.197937 / 1.445403 = **13.69% of total model npxG**, an 86.31% reduction.

The retained proportions multiply: 0.3125 × 0.438215 ≈ 0.136942. Do not add the percentage reductions. For a simpler example, half as many shots at half the average quality gives one quarter of the original xG, a 75% reduction.

**Coach brief:** France generated fewer attempts after halftime, and its average model-estimated chance quality also fell. Both dimensions accompany the lower second-half npxG; this calculation does not assign causal credit or explain tactical mechanisms.

Korea Republic is included in the saved evidence: its second-half count was four times its one-shot first-half count, average quality was about 4.32 times higher, and total npxG was about 17.29 times higher. These large ratios arise from a very small first-half reference (one shot, 0.008595 npxG). They do not establish sustained improvement or team ability. Inspect absolute counts and totals alongside ratios.

## Definitions and limitations

These are raw half totals, with unequal stoppage-time exposure possible. They are not per-minute rates or adjusted comparisons. Mean xG is a mean of individual probabilities, not the probability evaluated at the mean distance. Quality here means this educational distance-only model's estimate, not known true shot quality or independent validation. Penalties, shootouts and own-goal events remain excluded.

A zero-shot half has no defined mean xG per shot. A ratio with a zero reference denominator is undefined, saved as null rather than zero. Ratios above one represent increases, not invalid probabilities: these ratios are not per-shot scoring probabilities.

## Reproduce

Run `python 32_shot_volume_quality.py`. It reads the committed lesson-29 ledger without downloads, records the source SHA256, writes `data/32_volume_quality_evidence.json`, and saves `figures/35_shot_volume_quality.png`. Unit tests check the multiplicative identity, empty-half handling and saved-artifact reconciliation. Evidence checks independently reconcile half counts and total xG to existing records.

Source for average shot quality interpretation: [Hudl StatsBomb xG explanation](https://www.hudl.com/blog/expected-goals-xg-explained). Course foundation: [Soccermatics xG model fitting](https://soccermatics.readthedocs.io/en/latest/gallery/lesson2/plot_xGModelFit.html). Data: StatsBomb Open Data. This arithmetic extension was prepared with assistance; independent understanding has not yet been demonstrated.
