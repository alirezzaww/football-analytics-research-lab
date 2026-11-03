# Lesson 39: recorded corner-delivery profiles

## Completed worked assignment

Join every corner in the five-match France study to its raw `pass.technique.name`, retaining the existing 15-second phase membership and all 45 deliveries:

- **Inswinging:** 17 deliveries, nine with a phase shot — **52.94%**.
- **Outswinging:** ten deliveries, five with a phase shot — **50.00%**.
- **Straight:** nine deliveries, three with a phase shot — **33.33%**.
- **Other / unrecorded:** nine deliveries, two with a phase shot — **22.22%**. In this dataset all nine have absent technique labels, not another observed technique.

The categories reconcile to the original **45 deliveries and 19 shot-associated corners**. Per-category rates use every delivery in that category, including those with no associated shot. A phase with two shots still contributes only one to the corners-with-shots numerator.

## Football definitions and coding

An inswinging delivery curls toward goal; an outswinging delivery curls away. The provider's Straight label is retained as recorded, without inferring a curved trajectory. These definitions describe ball delivery, not goal outcome or taker ability. [Vancouver Whitecaps' analyst explanation](https://www.whitecapsfc.com/news/analysts-corner-attacking-corners) explains the inswinging/outswinging distinction; the [StatsBomb specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf) documents the technique field.

We do not infer technique from contact foot, corner side, arrow direction or pass length. Missing labels remain Other / unrecorded rather than becoming Straight, short corners or non-crosses. Nine absent labels represent **20% of the sample**, so reporting their coverage matters. The observed unknown-group rate does not identify how those deliveries would split among the known categories, and the missingness mechanism has not been established.

## Description is not a tactical recommendation

The inswinging and outswinging rates differ by only about **2.94 percentage points** in these small observed groups. We have not estimated uncertainty or adjusted for taker, opponent, corner side, match state or delivery target. The choices were not randomized. These factors may differ across groups, and missing labels can further affect interpretation.

**Completed analyst brief:** “Among recorded technique labels, France's inswinging deliveries were associated with a phase shot in 9/17 cases and outswinging deliveries in 5/10. The small unadjusted samples and nine missing technique labels prevent recommending one approach as superior from this study.”

The next investigation would examine group overlap across takers/opponents and review corresponding video before making recommendations. No video review, causal effect estimate or xG model change has occurred here.

## Reproduce and inspect

Run `python 39_corner_delivery_profiles.py`. It reconstructs and verifies the existing five-match source using its hash-checked caches/downloads, then adds the technique tag by match and corner ID. Outputs: `data/39_corner_delivery_profiles_evidence.json` and `figures/42_corner_delivery_profiles.png`. The new evidence preserves raw technique, category, taker, opponent, event key and unchanged phase outcome.

Tests verify label handling, missing groups and the all-deliveries denominator. Evidence checks reconcile exact corner membership, original outcomes, group totals and source digest; cached raw events additionally verify technique/taker fields. No delivery is excluded because its label is absent.

Worked assignment and implementation completed with assistance; independent user mastery is not claimed. Course foundation: Soccermatics; data: StatsBomb Open Data. This is an original descriptive project extension.
