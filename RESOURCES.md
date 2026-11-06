# Football analytics resources

## Current study and reading

- **Dataset:** FIFA Women’s World Cup, **2019** — StatsBomb competition ID 72, season ID 30. [Tournament match metadata](https://github.com/statsbomb/open-data/blob/master/data/matches/72/30.json).
- **Course:** [Soccermatics Lesson 3 — Statistical scouting, Comparison: percentile rankings](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#comparison-percentile-rankings).
- **Current practice:** [Lesson 71 — percentile comparisons](lessons/0053-fullback-percentile-comparisons.html), explicit ranks and tie handling within named overall and starting-side pools.

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

- [Soccermatics: position-based expected threat](https://soccermatics.readthedocs.io/en/latest/gallery/lesson4/plot_ExpectedThreat.html) and [mplsoccer xT tutorial](https://mplsoccer.readthedocs.io/en/latest/gallery/tutorials/plot_xt.html) — primary method sources for lesson 44; our model uses its own coarse grid, action scope and saved evidence.

- [socceraction xT documentation](https://socceraction.readthedocs.io/en/stable/documentation/valuing_actions/xT.html) — standard application to successful ball-moving actions; lesson 45 separately labels its project-specific unsuccessful-pass diagnostic.

- [Karun Singh: Introducing Expected Threat](https://karun.in/blog/expected-threat.html) — original explanation of probability-weighted location value; lesson 46 derives a separately labelled hypothetical pass-choice exercise with assumed probabilities.

- [scikit-learn LeaveOneGroupOut](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html) — general method for omitting one group per fold; lesson 48 uses match IDs with a standard-library implementation.

- StatsBomb Open Data specification revisited for lesson 50 event-level `under_pressure` field. The model treats only explicit true as flagged; absent/null/false is not verified absence of real defensive pressure.

- Employer requirements reviewed 4 November 2026: [Pluto careers](https://www.plutodata.co.uk/careers), [Newcastle scouting role, expired 2 November](https://careers.newcastleunited.com/job/scouting-analyst-africa-6063955), and [Blackburn lead academy role via UK Sport, listed deadline 10 November](https://www.uksport.gov.uk/global/jobs/blackburn-rovers-football--athletic-ltd/2026/11/10/lead-academy-analyst--youth-development-phase). Used as skill/role references with status and seniority distinctions in the employment plan, not as a suitable-job shortlist.

- [SQLite SELECT](https://www.sqlite.org/lang_select.html) and [Python 3.11 sqlite3 tutorial](https://docs.python.org/3.11/library/sqlite3.html) — primary sources for lesson 54 database loading, read queries, filters and aggregates.

- [SQLite join processing](https://www.sqlite.org/lang_select.html) and [foreign-key support](https://www.sqlite.org/foreignkeys.html) — primary references for lesson 55 relational keys, LEFT JOIN and parent-child integrity.

- [SQLite CASE expressions](https://www.sqlite.org/lang_expr.html#the_case_expression) — primary source for lesson 57 conditional labels before grouped match-phase summaries.

- [Hudl StatsBomb xG glossary](https://support.hudl.com/s/article/expected-goals?language=en_US&topic=Statsbomb_Global_Football_Data_Glossary) — provider definition revisited for lesson 61. The analysis reads the archived shot.statsbomb_xg values rather than claiming the current provider model version generated them.

- [StatsBomb freeze frames and defender locations](https://blogarchive.statsbomb.com/news/statsbomb-data-case-studies-freeze-frames-and-defender-locations/) and [Open Data specification Appendix 3](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf) — primary sources for lesson 62 shot-time snapshots, recorded player roles and spatial context. Project triangle counting is explicitly defined rather than asserted to reproduce the provider model.

- [Soccermatics statistical scouting](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html) and [spreadsheet scouting case study](https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html) — primary course sources revisited for the recruitment phase. Lesson 63 is a custom historical fullback-cohort exercise applying context and comparison principles.
