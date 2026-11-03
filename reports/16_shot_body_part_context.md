# Lesson 33: shot body-part mix and missing model context

We join the same 26 non-penalty shots from France–Korea Republic to the raw events' `shot.body_part.name`, using shot ID. Original raw-event SHA256 and the full lesson-29 ledger are checked before the join. The frozen distance-only probabilities are retained exactly; no model is fitted or validated again.

France's first half contained **13 foot shots and three headers**. Headers accounted for **3/16 = 18.75%** of its included first-half shots. Its second half contained **five foot shots and no headers**. Korea Republic had one foot shot before halftime and four afterward. There are no other or missing body-part labels in this fixture.

Two of France's three headers became goals, while two of its 18 foot shots became goals across the match. These small observational groups have different shooting situations and were not randomized or distance-matched. Their conversion rates do not establish that headers are inherently better, identify finishing skill or explain the first/second-half xG change. The header count is also not a cross count: a header can follow different preceding actions. No buildup mechanism has been checked here.

## Feature versus reporting tag

A **model feature** is information the prediction formula actually uses. Our frozen model uses distance only. A **reporting tag** lets us split or inspect the results; adding body part to this report does not make the predictions body-part-aware. Thus an equal-distance header and foot shot still receive the same estimate from this model, even if their true scoring probabilities differ.

[Hudl StatsBomb's xG explanation](https://www.hudl.com/blog/expected-goals-xg-explained) identifies body part as a common model input and describes the general importance of foot versus headed shots. This broad modelling context is separate from our small single-match result. Adding body part to a future model would require a new version and appropriate validation; the already inspected 2019 evaluation cannot be described as fresh for a model tuned using it.

## Foot contact does not establish weak-foot status

The source distinguishes Left Foot and Right Foot. Neither label establishes the player's preferred foot, the pass or shot's difficulty, or why an attempt failed. Preferred-foot information would need a separate verified source; causal statements about a weak foot would require further evidence. This answers the earlier learning question about whether contact-foot data exists without overstating what it tells us.

## Reproduce

Run `python 33_shot_body_part_context.py`. The script uses lesson 29's hash-verified cache/download routine for this single fixture, verifies the saved ledger is unchanged, then saves the tagged ledger and group membership to `data/33_body_part_evidence.json`. The chart is `figures/36_shot_body_part_mix.png`. Left Foot and Right Foot combine as Foot; Head is separate; everything else, including absent values, remains Other / unknown. No category is silently treated as a foot shot.

Group shares use each team's half-specific shot count. An absent category has zero shots and undefined mean probability, not a demonstrated zero scoring chance. Saved evidence can be reconciled without a raw cache; if available, raw labels and SHA256 are checked too. Tests cover category boundaries, missing labels and empty groups.

Next investigation: review the three first-half header events and their preceding actions. Do not claim that crossing caused France's first-half advantage without checking those sequences and broader context.

Course foundation: [Soccermatics xG fitting](https://soccermatics.readthedocs.io/en/latest/gallery/lesson2/plot_xGModelFit.html), including its suggested header/non-header extension. Data: [StatsBomb Open Data](https://github.com/statsbomb/open-data). Assisted implementation; independent interpretation remains pending.
