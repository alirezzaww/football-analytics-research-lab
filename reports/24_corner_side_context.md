# Lesson 41: corner side and comparison support

## Completed worked assignment

Add recorded delivery start location to the same 45 corners. Preserve the existing technique labels, takers and phase outcomes. Group delivery counts by taker and normalized corner side, then check for both recorded inswinging and outswinging techniques within the same taker/side/match.

**Key finding:** all 15 of Majri's inswingers start near the normalized y=80 touchline; both of her outswingers start near y=0. Her same-taker comparison therefore also changes delivery side. This does not prove that side alone determines her choice, nor infer her preferred foot.

Thiney has one inswinger and no outswingers near y=0; near y=80 she has one inswinger and eight outswingers. The nine technique-unrecorded deliveries remain unrecorded. Geyoro and Bussaglia have only those unrecorded labels in this sample, so no technique comparison is supported for them.

Across all five matches, **zero observed taker/side/match groups contain both recorded inswinging and outswinging deliveries**. Lesson 40 had found two same-taker/match groups containing both; adding side separates them. This is a descriptive overlap/support result, not a statistical significance test or an estimate of a zero tactical effect.

## Why this matters

“Compare the same player” addresses player identity but can still mix sides, opponents, score states and delivery targets. Here, adding one more contextual variable removes the observed within-group technique overlap. These records therefore do not directly support a comparison of both choices with player, side and match all held fixed.

This does not prohibit descriptive tournament-level summaries. It also does not prove a model could never be fitted; a model could borrow information across contexts, but its result would rely on additional assumptions rather than directly observed choices within those exact groups. A recommendation to switch technique would need stronger evidence, more representative overlap and football context/video.

## Coordinate rule and missing data

Use the recorded StatsBomb start location: y<40 labels the touchline-side nearer y=0; y>40 labels the side nearer y=80. Missing/invalid coordinates or exactly y=40 remain Side unknown. The data use normalized attacking coordinates, so labels are not literal stadium compass directions or a guarantee about screen-left/right in another plot. We do not infer trajectory from a straight start/end arrow, contact foot or taker identity.

All 45 deliveries have known sides in this sample. Unknown-side groups remain represented in the saved output even with zero exposure, so absence is not silently recoded as a known side. The two-panel chart displays the observed known-side counts; an empty known-technique cell means no recorded exposure, not zero effectiveness.

## Completed analyst brief

“Majri used inswingers from one recorded corner side and outswingers from the other. Once taker, side and match are grouped together, no context contains both recorded techniques. This limits a direct like-for-like comparison and prevents recommending a technique switch from this dataset alone.”

The next decision is to seek broader comparable evidence or change the research question to a descriptive delivery profile. Repeatedly splitting this small sample or fitting a more complex model does not create the missing comparisons. No new xG model, causal effect estimate or video review was performed.

## Reproduce and verify

Run `python 41_corner_side_context.py`. It verifies the existing five-fixture source through its hash-checked cache/download path, then joins start locations by match and corner ID. Outputs: `data/41_corner_side_evidence.json` and `figures/44_corner_side_context.png`. The saved ledger retains every original record unchanged plus side/location; source SHA256 is recorded.

Unit tests cover touchline coordinates, invalid/ambiguous locations and missing-technique overlap; full regeneration is tested only if all raw caches are already present. Evidence checks reconcile every taker/side group and exact-context membership without downloading, and verify raw start locations when cached.

Definitions/data: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Builds on [lesson 40's overlap audit](23_corner_taker_overlap.md). Original project extension prepared with assistance; independent user mastery is not claimed.
