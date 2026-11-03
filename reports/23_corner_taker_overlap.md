# Lesson 40: taker mix and comparison overlap

## Completed worked assignment

Before interpreting the delivery-type rates, inspect who took each technique in the same five-match, 45-delivery France sample.

- **Amel Majri:** 15 inswingers, two outswingers, four Straight and three unrecorded-technique deliveries.
- **Gaëtane Thiney:** two inswingers, eight outswingers, five Straight and three unrecorded-technique deliveries.
- **Onema Grace Geyoro:** two deliveries, both technique-unrecorded.
- **Elise Bussaglia:** one delivery, technique-unrecorded.

Majri supplied **15/17 inswingers**, while Thiney supplied **8/10 outswingers**. Therefore the overall type comparison uses different taker mixtures. All nine missing technique labels remain visible; they are not imputed from player identity or foot.

## Within-taker descriptive outcomes

Thiney's inswingers associate with phase shots in **2/2** cases, versus **4/8** outswingers. Majri's corresponding figures are **7/15** and **1/2**. These small raw comparisons are reported without treating 2/2 as a reliable 100% future rate. Even the within-taker direction differs: inswinging is higher for Thiney but slightly lower for Majri. This does not establish an interaction or a general effect; exposures are sparse and contexts differ.

A taker having both types somewhere in the tournament is weaker overlap than having both in the same match. Only **two observed taker/match contexts** contain both recorded types:

- Majri against Korea Republic: six inswingers and one outswinger.
- Majri against Nigeria: one inswinger and one outswinger.

No Thiney match contains both recorded types. Both-type status means at least one delivery of each, not sufficient evidence or sample size for an adjusted recommendation.

## What this teaches

**Confounding concern:** a player's ability, chosen side, opponent or match context may affect both delivery choice and whether a shot follows. These recorded distributions demonstrate imbalance; they do not prove which contextual factor caused the outcome differences.

**Overlap:** to compare techniques within a context, that context must include examples of both. Little or no overlap makes such a comparison unsupported or fragile. Grouping by taker alone does not hold side, opponent, score state, target or defensive setup constant.

**Completed analyst brief:** “The aggregate inswinging/outswinging comparison also changes the taker mix: Majri took most inswingers and Thiney most outswingers. Only two taker/match contexts contain both recorded types, each with one outswinging delivery. This limits a like-for-like comparison; we cannot recommend switching technique from these data alone.”

No formal adjusted model, causal effect, player ranking, significance test or video scouting is claimed. The next evidence needed would include larger overlapping samples, additional context and video review; fitting a complex model to these sparse cells would not create missing comparison data.

## Reproduce

Run `python 40_corner_taker_overlap.py`. It uses the committed lesson-39 records only, without network or raw caches. Outputs: `data/40_corner_taker_overlap_evidence.json` and `figures/43_corner_taker_overlap.png`. Each category retains explicit match/corner keys and original phase outcomes. The heatmap shows delivery counts, not success rates; a zero cell means no recorded exposure to that labelled technique, not zero effectiveness.

Tests cover positive-exposure overlap, unknown categories and cache-free artifact reproduction. Evidence checks reconcile every subgroup with the source ledger and verify the overall 45-delivery/19-shot-associated-corner totals.

Worked assignment prepared with assistance; independent mastery is not claimed. Data: StatsBomb Open Data. Builds on the documented delivery techniques and phase definitions in lessons 36–39; no new model or validation dataset.
