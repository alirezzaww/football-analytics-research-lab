# Join pressure actions to linked opponent passes

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Context: what to measure](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure). Custom assisted extension.
Definition: [StatsBomb specification — related_events and Pass outcome](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Related-event IDs connect recorded observations; a relationship is not proof that pressure caused an outcome.

## Method and denominator

Read directed related_events from each selected Pressure start; join IDs within fixture to opposite-team Pass events in the same period. Save all link types and reciprocity. No nearest-event, possession-label, timing-window, location or restart-delivery filter. Deduplicate passes by (match,pass_id) within player before counting outcomes. Completed=no outcome; Incomplete/Out/Pass Offside=not completed; Unknown/Injury Clearance=unassessable.

All original 2,034 pressure rows and 35 profiles are preserved, including missing locations. A pressure may link to no passes, one pass or more; other event types remain represented in link-type counts. Unresolved or duplicate IDs stop the join. Reciprocal references are recorded and checked, rather than silently presumed. Same-team passes are logged separately and excluded from opponent-pass results. Restart deliveries can remain because this is a distinct directly linked-event question, not lesson 65's eligible-passing denominator. A related pass need not start after pressure starts; no arbitrary five-second cutoff is applied.

Outcome counts use unique (fixture, pass ID) records within each player's links. Repeated links to the same pass do not increase that player's pass denominator. The saved non-completion share uses only unique linked passes with assessable outcomes; an empty assessable set means undefined. Unknown/Injury Clearance outcomes stay visible. Passes may still recur between different player profiles, so summing profiles does not yield unique team passes. Missing links are not an outcome observation.

## All profiles

- **Argentina Women's — Eliana Noemí Stábile**: 17/52 pressures link to an opponent pass; 17 unique passes: 8 completed, 9 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Australia Women's — Ellie Madison Carpenter**: 15/55 pressures link to an opponent pass; 15 unique passes: 9 completed, 6 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Brazil Women's — Letícia Santos de Oliveira**: 16/59 pressures link to an opponent pass; 16 unique passes: 12 completed, 3 not completed, 1 unassessable. Nonreciprocal pass links: 0.
- **Brazil Women's — Tamires Cássia Dias de Britto**: 15/54 pressures link to an opponent pass; 15 unique passes: 6 completed, 9 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Cameroon W — Yvonne Patrice Leuko**: 25/60 pressures link to an opponent pass; 25 unique passes: 19 completed, 6 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Canada Women's — Allysha Lyn Chapman**: 9/37 pressures link to an opponent pass; 9 unique passes: 4 completed, 5 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Canada Women's — Ashley Elizabeth Marie Lawrence**: 11/57 pressures link to an opponent pass; 11 unique passes: 5 completed, 6 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **China PR Women's — Peng Han**: 11/56 pressures link to an opponent pass; 11 unique passes: 8 completed, 3 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **China PR Women's — Shanshan Liu**: 9/48 pressures link to an opponent pass; 9 unique passes: 6 completed, 3 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **England Women's — Alex Greenwood**: 15/52 pressures link to an opponent pass; 15 unique passes: 8 completed, 7 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **England Women's — Demi Stokes**: 17/53 pressures link to an opponent pass; 17 unique passes: 12 completed, 5 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **England Women's — Lucy Bronze**: 28/102 pressures link to an opponent pass; 28 unique passes: 19 completed, 8 not completed, 1 unassessable. Nonreciprocal pass links: 0.
- **France Women's — Amel Majri**: 7/61 pressures link to an opponent pass; 7 unique passes: 4 completed, 3 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **France Women's — Marion Torrent**: 14/58 pressures link to an opponent pass; 14 unique passes: 7 completed, 7 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Germany Women's — Giulia Gwinn**: 9/36 pressures link to an opponent pass; 9 unique passes: 4 completed, 5 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Germany Women's — Verena Schweers**: 9/37 pressures link to an opponent pass; 9 unique passes: 7 completed, 2 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Italy Women's — Alia Guagni**: 13/57 pressures link to an opponent pass; 13 unique passes: 7 completed, 6 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Italy Women's — Elisa Bartoli**: 13/70 pressures link to an opponent pass; 13 unique passes: 10 completed, 3 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Jamaica Women's — Deneisha Selena Blackwood**: 12/49 pressures link to an opponent pass; 12 unique passes: 5 completed, 7 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Japan Women's — Aya Sameshima**: 10/45 pressures link to an opponent pass; 10 unique passes: 5 completed, 5 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Japan Women's — Risa Shimizu**: 6/36 pressures link to an opponent pass; 6 unique passes: 4 completed, 2 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Korea Republic Women's — Sel-Gi Jang**: 10/45 pressures link to an opponent pass; 10 unique passes: 9 completed, 1 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Netherlands Women's — Desiree van Lunteren**: 23/86 pressures link to an opponent pass; 23 unique passes: 13 completed, 10 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Netherlands Women's — Merel van Dongen**: 13/73 pressures link to an opponent pass; 13 unique passes: 11 completed, 2 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Nigeria Women's — Chidinma Nkeruka Okeke**: 7/23 pressures link to an opponent pass; 7 unique passes: 6 completed, 1 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Nigeria Women's — Ngozi Ebere**: 7/37 pressures link to an opponent pass; 7 unique passes: 5 completed, 2 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Norway Women's — Ingrid Moe Wold**: 12/49 pressures link to an opponent pass; 13 unique passes: 10 completed, 3 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Norway Women's — Kristine Minde**: 18/72 pressures link to an opponent pass; 18 unique passes: 14 completed, 4 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **South Africa Women's — Lebogang Ramalepe**: 26/73 pressures link to an opponent pass; 26 unique passes: 17 completed, 8 not completed, 1 unassessable. Nonreciprocal pass links: 0.
- **Spain Women's — Marta Corredera Rueda**: 27/82 pressures link to an opponent pass; 27 unique passes: 20 completed, 7 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Sweden Women's — Hanna Erica Maria Glas**: 40/109 pressures link to an opponent pass; 40 unique passes: 29 completed, 10 not completed, 1 unassessable. Nonreciprocal pass links: 0.
- **Sweden Women's — Magdalena Lilly Eriksson**: 15/46 pressures link to an opponent pass; 15 unique passes: 9 completed, 6 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **Thailand W — Sunisa Srangthaisong**: 13/48 pressures link to an opponent pass; 13 unique passes: 10 completed, 3 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **United States Women's — Crystal Alyssia Dunn Soubrier**: 35/93 pressures link to an opponent pass; 35 unique passes: 17 completed, 18 not completed, 0 unassessable. Nonreciprocal pass links: 0.
- **United States Women's — Kelley Maureen O'Hara**: 21/64 pressures link to an opponent pass; 21 unique passes: 14 completed, 6 not completed, 1 unassessable. Nonreciprocal pass links: 0.

## First linked-pass examples for the two familiar players

- Match 22936, period 1: pressure `c543af09-bb3b-4cc7-a196-32cbded861b8` at 00:06:45.362 links to Christie Murray's pass `ffb5226d-4927-4364-9d1b-2b58cb80bd83` at 00:06:45.418. Recorded outcome: Completed (no outcome field). Reciprocal: True.
- Match 22921, period 1: pressure `fb96a1cf-d47a-46cd-a0da-82ab6288aba7` at 00:16:03.342 links to Hye-Ri Kim's pass `f9fe2285-e271-4884-b807-809131dd96f1` at 00:16:04.526. Recorded outcome: Incomplete. Reciprocal: True.

## Interpretation

This records what happened to the linked passes. It does not establish whether pressure caused incompletion or whether the pressure itself was effective. A completed pass might be backwards and helpful to the defending team; an incomplete pass might have gone wrong for another reason. Links do not cover every pressure or every on-ball action. Small, different selected subsets are not fair player-success comparisons, control groups or interchangeable recruitment recommendations. Earlier possession-proxy results remain unchanged.

## Reproduce

Run `python 79_pressure_linked_passes.py` in Spyder. [Evidence](../data/79_pressure_linked_passes_evidence.json) · [Lesson](../lessons/0061-pressure-linked-passes.html).
Source: StatsBomb Open Data. Assisted event-ID join; no footage review or independent mastery claimed.
