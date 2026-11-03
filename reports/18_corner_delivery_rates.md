# Lesson 35: count all corner deliveries before calculating a rate

France had **13 recorded corner pass events** against Korea Republic: ten in the first half, three in the second. **Two deliveries have verified reciprocal direct shot links, and both linked shots were goals.**

The recorded direct shot-link rate is **2/13 = 15.38%**. The recorded direct goal-link rate is also **2/13 = 15.38%**. Both direct links are the first-half Renard headers inspected in lesson 34. The two linked shots happened to become goals; this is one match, not a reliable estimate of future corner performance. Korea Republic had one corner delivery and no recorded direct shot link; that 0/1 observation is not a meaningful team ranking.

## Define the denominator

Count every period-1/2 Pass event with `pass.type.name = Corner`, without filtering on completion, shot linkage, outcome or recipient. This retains seven France deliveries labelled Incomplete, as well as six without a pass-outcome label. The latter are not sufficient evidence that a shot followed. Short corners would be retained by the same rule. These are recorded deliveries, not an independently reconciled count of corners awarded; retakes or logging conventions may matter in other matches.

## Define the numerator

A delivery counts as directly linked to a shot only if `pass.assisted_shot_id` resolves to a Shot whose `shot.key_pass_id` points back to that delivery, with consistent team, period, possession and event order. All populated links resolve in this fixture. Invalid links raise errors. A directly linked goal additionally requires the linked shot's outcome to be Goal.

The chart's three counts are nested: goal-linked deliveries are a subset of shot-linked deliveries, which are a subset of all deliveries. They must not be added together.

## What is outside this measure?

No recorded direct link does **not** mean no later shot, no pressure or a failed set piece. A short corner followed by another pass, a clearance recycled into the box or a rebound can produce a later chance that this direct-link definition does not capture. This lesson does not quantify all corner-phase shots/goals, assign tactical causes, estimate causal corner value or fit an xG model. The existing shot sample and frozen predictions are unchanged.

The next broader phase analysis would require explicit rules for when a corner phase ends. Those rules should be specified before comparing results. For now, use the precise label **recorded direct corner-to-shot link rate**, not a generic “corner success rate.”

## Reproduce

Run `python 35_corner_delivery_rates.py`. It uses the hash-verified single-fixture cache/download procedure, then saves all 14 deliveries from both teams with IDs, timestamps, outcomes and link statuses in `data/35_corner_delivery_evidence.json`. The figure is `figures/38_corner_delivery_rates.png`. Tests check inclusion of unlinked deliveries and undefined empty denominators. Evidence checks reconcile saved summaries, all raw corner IDs and reciprocal shot links when raw events are cached. Saved aggregates remain checkable without the raw cache.

Source definitions: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Data: StatsBomb Open Data. Original project extension, prepared with assistance; independent interpretation pending.

Practice: explain why two goals from the two inspected header chances is not the same calculation as two directly linked goals from 13 corner deliveries. The first conditions on selected shot chances; the second uses all recorded corner deliveries.
