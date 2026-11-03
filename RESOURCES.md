# Football analytics resources

## Knowledge

- [Soccermatics: pass heat maps](https://soccermatics.readthedocs.io/en/latest/gallery/lesson1/plot_PassHeatMap.html)
  Primary course example for 15-second pass selection, possession matching and duplicate handling.
  Our 5/10/15-second comparison is a project extension, not a copied course lesson.
- [StatsBomb Open Data](https://github.com/hudl/open-data)
  Primary event-data source; use for source schema, competition data and licensing.
- [Soccermatics: fitting an xG model](https://soccermatics.readthedocs.io/en/latest/gallery/lesson2/plot_xGModelFit.html)
  Foundation for the separate educational model in lesson 18; its results do not replace provider xG.

- [SciPy: bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
  Primary reference for replacement sampling, paired indices and percentile intervals.
  Lesson 21 implements an explicit teaching loop; small-sample coverage remains unvalidated.

- [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf)
  Primary event definitions, including Shot outcomes and own-goal event types; used
  for lesson-22 score reconstruction and its explicit accounting convention.

- [scikit-learn: LeaveOneGroupOut](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html)
  Primary grouped-validation design reference. Lesson 25 implements fixture-held-out
  folds directly without adding the library as a dependency.
- [scikit-learn: cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
  Primary reference for fitting preprocessing on the fitting subset before transforming
  held-out rows. Use with the source xG lesson for model-comparison work.

- [scikit-learn: probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
  Primary reference for reliability diagrams and comparison of bin-average probabilities
  with observed positive fractions. Lesson 26 is diagnostic only, with no recalibrator.

- [SciPy: extrapolation background](https://docs.scipy.org/doc/scipy/tutorial/interpolate/extrapolation_examples.html)
  Introduces evaluation outside an observed data domain using interpolation examples.
  Lesson 28 uses the outside-range concept for a logistic distance model; it does not
  use those interpolation routines or infer that all extrapolations must fail.

## Gaps

Role-specific comparisons, statistical uncertainty, larger-sample model validation and
video review remain future project work. No community participation has been requested.

- [Hudl StatsBomb: What are Expected Goals?](https://www.hudl.com/blog/expected-goals-xg-explained) — probability interpretation, average shot quality and team analysis; used for lesson 29 (2026-11-03).

- [JoGall: Adjusting xG per possession](https://jogall.github.io/2019-01-16-adjusted-xG/) — author example of cumulative match xG timelines; separate R package, not the Python Soccermatics course. Lesson 30 uses its own implementation and unchanged shot-level sums.

- [mplsoccer official scatter example](https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_plots/plot_scatter.html) — vertical shot maps and probability-sized markers; lesson 31 uses proportional circle area with a common scale (2026-11-03).

- [Hudl StatsBomb xG: body-part context](https://www.hudl.com/blog/expected-goals-xg-explained) — revisited for lesson 33, distinguishing general model features from a single-match descriptive split (2026-11-03).

- [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf) — revisited for lesson 34: key-pass links, assisted-shot IDs, pass type and shot type. Historical raw fields are retained separately from phase interpretation.

- [Whitecaps analysts: attacking corners](https://www.whitecapsfc.com/news/analysts-corner-attacking-corners) — club analyst definitions of inswinging and outswinging deliveries; used in lesson 39 alongside the StatsBomb technique specification.

- [StatsBomb Working with R](https://blogarchive.statsbomb.com/uploads/2021/11/Working-with-R.pdf) — provider coordinate reference with penalty-area and six-yard-box rectangles; used for lesson 42 spatial bins.
