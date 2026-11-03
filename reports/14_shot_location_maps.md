# Lesson 31: where did the shots come from?

We extend the France–Korea Republic brief with four comparable shot maps: each team, each half. These show the same 26 non-penalty shots used in lessons 29–30, without fitting another model or collecting more data.

**Finding:** France took 16 first-half shots and five second-half shots. Its average shot distance from goal centre increased from **16.16 to 20.12 reference-pitch metres**. Together, the count and location summary describe fewer and, on average, more distant attempts after halftime. This does not mean every second-half shot was farther than every first-half shot, or establish a tactical cause. The first-half total was 1.445 model npxG versus 0.198 afterward. Do not infer mean probability from mean distance: the fitted probability relationship is nonlinear.

Korea Republic took one first-half shot at 30.85 reference metres, then four second-half shots averaging 21.25 reference metres. These are small descriptive samples, not general estimates of team ability.

## Read the map

- Each coloured circle is a shot location, not a shot destination or a pass.
- Circle area is proportional to the frozen model probability, using the same scale across all four panels. It is not the physical size of a chance or a player's ability.
- A black star marks a goal, overlaid on the probability circle. A goal does not automatically receive 1.0 xG.
- Both teams attack the top goal in all panels. These are normalized StatsBomb coordinates, not literal stadium compass directions. The library handles the vertical display; do not swap the stored x and y yourself.

All shots lie in the attacking half in this fixture. The script explicitly rejects a shot outside the displayed half instead of silently hiding it. For another fixture with a shot behind halfway, use a full-pitch view. Marker overlap can obscure individual shots: panel counts and the saved shot-ID ledger remain the auditable record.

The model uses distance alone. Circle size therefore adds a visual representation of that fitted distance relationship, not independent evidence validating it. The map also exposes a limitation: two shots at equal distance get the same estimate even if their angles or defensive situations differ. Distance is calculated using an assumed 105×68 m reference pitch; it is not a measured venue distance.

## Reproduce and investigate

Run `python 31_shot_location_maps.py` in Spyder. It reads the committed lesson-29 ledger, writes panel membership and summaries to `data/31_shot_location_evidence.json`, and saves `figures/34_shot_location_maps.png`. No downloads are needed. The evidence checker reconciles unique shot identities, panel counts, source digest, original coordinates and aggregate distances/xG against the ledger and prior timeline.

A useful next video question is: **How did France reach its closer first-half shooting positions, and what changed in its attacking sequences after halftime?** The locations alone cannot answer this. They support a question for investigation, not a causal conclusion.

Sources: [mplsoccer official scatter example](https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_plots/plot_scatter.html) for vertical shot mapping and probability-sized markers; [Soccermatics model fitting](https://soccermatics.readthedocs.io/en/latest/gallery/lesson2/plot_xGModelFit.html) for the course foundation. Data: [StatsBomb Open Data](https://github.com/statsbomb/open-data). This is an assisted project extension, not an independent scouting assessment or fresh validation. Independent interpretation remains pending.
