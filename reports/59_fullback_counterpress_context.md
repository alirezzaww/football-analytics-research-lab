# Pressure after losing the ball: counterpress context

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Context: what to measure](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure). This is our assisted context extension, not a separate numbered lesson from the course.

## Meaning and method

The [StatsBomb Open Data specification, Pressure → counterpress](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf) defines the flag as pressing within five seconds of an open-play turnover, recorded only when true. In football terms, a team loses the ball during play and promptly applies pressure. We read the provider flag; we do not independently reconstruct the lost-ball instant or apply a new five-second rule.

Select the unchanged 2,034 Pressure events from lesson 73. Match each to the hash-checked raw event by fixture and ID, verify player/team, type, period, timestamp and index, then inspect top-level counterpress. Only the actual Boolean true counts. False, null and absent states are retained separately and described collectively as not flagged. Unexpected non-Boolean values stop calculation. Missing coordinates do not exclude an action.

Flagged share = flagged Pressure starts / all selected Pressure starts ×100. Per90 = flagged starts / original registered minutes ×90. Counts are pooled across fixtures. Zero pressures gives an undefined share, rather than zero; positive time with no flagged actions gives zero per90. All 35 profiles retain the original cohort, pressure totals and minutes.

## Results (alphabetical)

- **Argentina Women's — Eliana Noemí Stábile**: 7/52 pressures flagged (13.46%); 2.1830/90. Raw flag states: {'true': 7, 'false': 0, 'null': 0, 'missing': 45}.
- **Australia Women's — Ellie Madison Carpenter**: 15/55 pressures flagged (27.27%); 3.1687/90. Raw flag states: {'true': 15, 'false': 0, 'null': 0, 'missing': 40}.
- **Brazil Women's — Letícia Santos de Oliveira**: 6/59 pressures flagged (10.17%); 1.4759/90. Raw flag states: {'true': 6, 'false': 0, 'null': 0, 'missing': 53}.
- **Brazil Women's — Tamires Cássia Dias de Britto**: 13/54 pressures flagged (24.07%); 2.7388/90. Raw flag states: {'true': 13, 'false': 0, 'null': 0, 'missing': 41}.
- **Cameroon W — Yvonne Patrice Leuko**: 1/60 pressures flagged (1.67%); 0.2978/90. Raw flag states: {'true': 1, 'false': 0, 'null': 0, 'missing': 59}.
- **Canada Women's — Allysha Lyn Chapman**: 7/37 pressures flagged (18.92%); 2.5124/90. Raw flag states: {'true': 7, 'false': 0, 'null': 0, 'missing': 30}.
- **Canada Women's — Ashley Elizabeth Marie Lawrence**: 17/57 pressures flagged (29.82%); 5.2471/90. Raw flag states: {'true': 17, 'false': 0, 'null': 0, 'missing': 40}.
- **China PR Women's — Peng Han**: 10/56 pressures flagged (17.86%); 2.3225/90. Raw flag states: {'true': 10, 'false': 0, 'null': 0, 'missing': 46}.
- **China PR Women's — Shanshan Liu**: 8/48 pressures flagged (16.67%); 1.8580/90. Raw flag states: {'true': 8, 'false': 0, 'null': 0, 'missing': 40}.
- **England Women's — Alex Greenwood**: 11/52 pressures flagged (21.15%); 2.4668/90. Raw flag states: {'true': 11, 'false': 0, 'null': 0, 'missing': 41}.
- **England Women's — Demi Stokes**: 13/53 pressures flagged (24.53%); 4.0366/90. Raw flag states: {'true': 13, 'false': 0, 'null': 0, 'missing': 40}.
- **England Women's — Lucy Bronze**: 20/102 pressures flagged (19.61%); 2.6042/90. Raw flag states: {'true': 20, 'false': 0, 'null': 0, 'missing': 82}.
- **France Women's — Amel Majri**: 17/61 pressures flagged (27.87%); 3.0343/90. Raw flag states: {'true': 17, 'false': 0, 'null': 0, 'missing': 44}.
- **France Women's — Marion Torrent**: 11/58 pressures flagged (18.97%); 2.4000/90. Raw flag states: {'true': 11, 'false': 0, 'null': 0, 'missing': 47}.
- **Germany Women's — Giulia Gwinn**: 12/36 pressures flagged (33.33%); 3.6698/90. Raw flag states: {'true': 12, 'false': 0, 'null': 0, 'missing': 24}.
- **Germany Women's — Verena Schweers**: 10/37 pressures flagged (27.03%); 4.7046/90. Raw flag states: {'true': 10, 'false': 0, 'null': 0, 'missing': 27}.
- **Italy Women's — Alia Guagni**: 9/57 pressures flagged (15.79%); 1.7826/90. Raw flag states: {'true': 9, 'false': 0, 'null': 0, 'missing': 48}.
- **Italy Women's — Elisa Bartoli**: 7/70 pressures flagged (10.00%); 1.9839/90. Raw flag states: {'true': 7, 'false': 0, 'null': 0, 'missing': 63}.
- **Jamaica Women's — Deneisha Selena Blackwood**: 5/49 pressures flagged (10.20%); 1.5722/90. Raw flag states: {'true': 5, 'false': 0, 'null': 0, 'missing': 44}.
- **Japan Women's — Aya Sameshima**: 6/45 pressures flagged (13.33%); 1.4101/90. Raw flag states: {'true': 6, 'false': 0, 'null': 0, 'missing': 39}.
- **Japan Women's — Risa Shimizu**: 4/36 pressures flagged (11.11%); 0.9400/90. Raw flag states: {'true': 4, 'false': 0, 'null': 0, 'missing': 32}.
- **Korea Republic Women's — Sel-Gi Jang**: 9/45 pressures flagged (20.00%); 2.8190/90. Raw flag states: {'true': 9, 'false': 0, 'null': 0, 'missing': 36}.
- **Netherlands Women's — Desiree van Lunteren**: 15/86 pressures flagged (17.44%); 1.8647/90. Raw flag states: {'true': 15, 'false': 0, 'null': 0, 'missing': 71}.
- **Netherlands Women's — Merel van Dongen**: 5/73 pressures flagged (6.85%); 1.0651/90. Raw flag states: {'true': 5, 'false': 0, 'null': 0, 'missing': 68}.
- **Nigeria Women's — Chidinma Nkeruka Okeke**: 5/23 pressures flagged (21.74%); 1.5092/90. Raw flag states: {'true': 5, 'false': 0, 'null': 0, 'missing': 18}.
- **Nigeria Women's — Ngozi Ebere**: 5/37 pressures flagged (13.51%); 1.6715/90. Raw flag states: {'true': 5, 'false': 0, 'null': 0, 'missing': 32}.
- **Norway Women's — Ingrid Moe Wold**: 6/49 pressures flagged (12.24%); 1.1296/90. Raw flag states: {'true': 6, 'false': 0, 'null': 0, 'missing': 43}.
- **Norway Women's — Kristine Minde**: 9/72 pressures flagged (12.50%); 1.5444/90. Raw flag states: {'true': 9, 'false': 0, 'null': 0, 'missing': 63}.
- **South Africa Women's — Lebogang Ramalepe**: 16/73 pressures flagged (21.92%); 4.9658/90. Raw flag states: {'true': 16, 'false': 0, 'null': 0, 'missing': 57}.
- **Spain Women's — Marta Corredera Rueda**: 14/82 pressures flagged (17.07%); 3.2253/90. Raw flag states: {'true': 14, 'false': 0, 'null': 0, 'missing': 68}.
- **Sweden Women's — Hanna Erica Maria Glas**: 16/109 pressures flagged (14.68%); 2.2763/90. Raw flag states: {'true': 16, 'false': 0, 'null': 0, 'missing': 93}.
- **Sweden Women's — Magdalena Lilly Eriksson**: 8/46 pressures flagged (17.39%); 1.1702/90. Raw flag states: {'true': 8, 'false': 0, 'null': 0, 'missing': 38}.
- **Thailand W — Sunisa Srangthaisong**: 6/48 pressures flagged (12.50%); 1.8671/90. Raw flag states: {'true': 6, 'false': 0, 'null': 0, 'missing': 42}.
- **United States Women's — Crystal Alyssia Dunn Soubrier**: 19/93 pressures flagged (20.43%); 2.8954/90. Raw flag states: {'true': 19, 'false': 0, 'null': 0, 'missing': 74}.
- **United States Women's — Kelley Maureen O'Hara**: 11/64 pressures flagged (17.19%); 1.8662/90. Raw flag states: {'true': 11, 'false': 0, 'null': 0, 'missing': 53}.

## Interpretation and limits

The flag describes when the pressing action happened relative to a turnover. It does not state that the player or her team recovered possession. Counterpressing and pressure regains are different concepts: one concerns pressure after a loss, the other concerns recovering the ball after pressure. We have not calculated regain outcomes here.

One lost-ball episode can have several Pressure events and several players involved, so these counts are not unique turnovers. Other defensive event types can also carry counterpress flags; this report deliberately covers Pressure starts only. Not flagged is not independently verified absence of counterpressing in footage. Shares depend on team losses, tactics and other pressure activity; no opportunity-adjusted ability ranking or success rate is claimed. A counterpress can happen in any pitch third: the time context and the spatial context answer different questions.

## Reproduce

Run `python 76_fullback_counterpress_context.py` in Spyder. [Evidence](../data/76_fullback_counterpress_context_evidence.json) · [Lesson](../lessons/0058-fullback-counterpress-context.html).
Source: StatsBomb Open Data. No footage reviewed or independent mastery demonstrated.
