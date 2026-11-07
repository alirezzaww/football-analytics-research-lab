# What followed the pressure? Next-possession check

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Normalisation, Pressure Regains](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation). This is our assisted educational extension.

## Why use an explicitly named proxy?

[Hudl's Pressure Regains guidance](https://hudl.my.site.com/support/s/article/pressure-regains?language=en_US&topic=Statsbomb_Global_Football_Data_Glossary) describes a team's recovery within five seconds after pressure, with conditions on the following possession. It also says IQ's possession definition does not translate cleanly to Event Data. We therefore do **not** label this result the official Pressure Regains metric.

Our bounded question is: does the **first following new recorded possession** belong to the pressing team and begin within five seconds of the pressure start? This uses event-data possession labels, not a newly trained detector or video observation. We do not apply the provider's possession-entry filters, so it is intentionally a different, transparent rule.

## Fixed rule

Pressure-only custom proxy: the first following new recorded possession in the SAME period belongs to the pressing team and starts 0–5000 ms inclusive after pressure START. Possession start is first event index in each (period,possession) group; its possession_team defines the side. Do not skip an intervening possession. Already-own possession, backwards candidate time and insufficient period-end observation without a timely candidate are unassessable. Observe the team outcome even if the player is substituted during follow-up. No other event-type or play-pattern entry filter.

All 2,034 selected pressures and the original 35 profiles/minutes stay intact. Each row retains pressure identity, the candidate start event, team, possession ID, timestamp, delay and outcome status. Unassessable rows are excluded only from the outcome-share denominator, never erased from original counts. A full five-second window without a timely new possession is an observed negative for this rule. A next possession by the other side is negative even if another change follows within five seconds. We do not cross halftime/extra-time boundaries or infer a positive from a period restart.

Share = positive rows / assessable rows ×100; zero assessable rows means undefined. Observed positives per90 use original registered minutes, including exposure associated with unassessable rows, so they are observed-event rates rather than corrected complete-follow-up estimates. Outcome observation follows the team, even after a player's substitution; pressure membership itself remains restricted to the original player windows. Multiple player actions can share the same outcome, and should not be summed as unique team regains.

## Results (alphabetical)

- **Argentina Women's — Eliana Noemí Stábile**: 8/49 assessable pressures (16.33%); 3 unassessable of 52 total; observed 2.4949/90. Statuses: {'no_new_possession_within_window': 41, 'next_own_within_window': 8, 'already_own_possession': 3}.
- **Australia Women's — Ellie Madison Carpenter**: 8/41 assessable pressures (19.51%); 14 unassessable of 55 total; observed 1.6900/90. Statuses: {'already_own_possession': 14, 'no_new_possession_within_window': 33, 'next_own_within_window': 8}.
- **Brazil Women's — Letícia Santos de Oliveira**: 7/55 assessable pressures (12.73%); 4 unassessable of 59 total; observed 1.7219/90. Statuses: {'no_new_possession_within_window': 48, 'already_own_possession': 4, 'next_own_within_window': 7}.
- **Brazil Women's — Tamires Cássia Dias de Britto**: 6/40 assessable pressures (15.00%); 14 unassessable of 54 total; observed 1.2641/90. Statuses: {'already_own_possession': 14, 'next_own_within_window': 6, 'no_new_possession_within_window': 34}.
- **Cameroon W — Yvonne Patrice Leuko**: 6/59 assessable pressures (10.17%); 1 unassessable of 60 total; observed 1.7870/90. Statuses: {'no_new_possession_within_window': 52, 'next_own_within_window': 6, 'next_not_own_within_window': 1, 'already_own_possession': 1}.
- **Canada Women's — Allysha Lyn Chapman**: 4/30 assessable pressures (13.33%); 7 unassessable of 37 total; observed 1.4357/90. Statuses: {'already_own_possession': 7, 'no_new_possession_within_window': 26, 'next_own_within_window': 4}.
- **Canada Women's — Ashley Elizabeth Marie Lawrence**: 5/46 assessable pressures (10.87%); 11 unassessable of 57 total; observed 1.5433/90. Statuses: {'already_own_possession': 11, 'no_new_possession_within_window': 41, 'next_own_within_window': 5}.
- **China PR Women's — Peng Han**: 4/48 assessable pressures (8.33%); 8 unassessable of 56 total; observed 0.9290/90. Statuses: {'already_own_possession': 8, 'no_new_possession_within_window': 44, 'next_own_within_window': 4}.
- **China PR Women's — Shanshan Liu**: 5/45 assessable pressures (11.11%); 3 unassessable of 48 total; observed 1.1613/90. Statuses: {'no_new_possession_within_window': 40, 'next_own_within_window': 5, 'already_own_possession': 3}.
- **England Women's — Alex Greenwood**: 8/44 assessable pressures (18.18%); 8 unassessable of 52 total; observed 1.7940/90. Statuses: {'no_new_possession_within_window': 36, 'already_own_possession': 8, 'next_own_within_window': 8}.
- **England Women's — Demi Stokes**: 7/49 assessable pressures (14.29%); 4 unassessable of 53 total; observed 2.1735/90. Statuses: {'already_own_possession': 4, 'no_new_possession_within_window': 42, 'next_own_within_window': 7}.
- **England Women's — Lucy Bronze**: 12/81 assessable pressures (14.81%); 21 unassessable of 102 total; observed 1.5625/90. Statuses: {'next_own_within_window': 12, 'already_own_possession': 21, 'no_new_possession_within_window': 69}.
- **France Women's — Amel Majri**: 1/43 assessable pressures (2.33%); 18 unassessable of 61 total; observed 0.1785/90. Statuses: {'already_own_possession': 18, 'no_new_possession_within_window': 42, 'next_own_within_window': 1}.
- **France Women's — Marion Torrent**: 16/50 assessable pressures (32.00%); 8 unassessable of 58 total; observed 3.4910/90. Statuses: {'next_own_within_window': 16, 'no_new_possession_within_window': 34, 'already_own_possession': 8}.
- **Germany Women's — Giulia Gwinn**: 6/28 assessable pressures (21.43%); 8 unassessable of 36 total; observed 1.8349/90. Statuses: {'no_new_possession_within_window': 22, 'next_own_within_window': 6, 'already_own_possession': 8}.
- **Germany Women's — Verena Schweers**: 2/36 assessable pressures (5.56%); 1 unassessable of 37 total; observed 0.9409/90. Statuses: {'next_own_within_window': 2, 'no_new_possession_within_window': 34, 'already_own_possession': 1}.
- **Italy Women's — Alia Guagni**: 8/54 assessable pressures (14.81%); 3 unassessable of 57 total; observed 1.5845/90. Statuses: {'next_own_within_window': 8, 'no_new_possession_within_window': 46, 'already_own_possession': 3}.
- **Italy Women's — Elisa Bartoli**: 7/64 assessable pressures (10.94%); 6 unassessable of 70 total; observed 1.9839/90. Statuses: {'no_new_possession_within_window': 57, 'already_own_possession': 6, 'next_own_within_window': 7}.
- **Jamaica Women's — Deneisha Selena Blackwood**: 3/43 assessable pressures (6.98%); 6 unassessable of 49 total; observed 0.9433/90. Statuses: {'no_new_possession_within_window': 40, 'next_own_within_window': 3, 'already_own_possession': 6}.
- **Japan Women's — Aya Sameshima**: 5/40 assessable pressures (12.50%); 5 unassessable of 45 total; observed 1.1751/90. Statuses: {'no_new_possession_within_window': 35, 'next_own_within_window': 5, 'already_own_possession': 5}.
- **Japan Women's — Risa Shimizu**: 2/35 assessable pressures (5.71%); 1 unassessable of 36 total; observed 0.4700/90. Statuses: {'no_new_possession_within_window': 33, 'already_own_possession': 1, 'next_own_within_window': 2}.
- **Korea Republic Women's — Sel-Gi Jang**: 4/40 assessable pressures (10.00%); 5 unassessable of 45 total; observed 1.2529/90. Statuses: {'next_own_within_window': 4, 'no_new_possession_within_window': 36, 'already_own_possession': 5}.
- **Netherlands Women's — Desiree van Lunteren**: 11/75 assessable pressures (14.67%); 11 unassessable of 86 total; observed 1.3674/90. Statuses: {'no_new_possession_within_window': 63, 'already_own_possession': 11, 'next_own_within_window': 11, 'next_not_own_within_window': 1}.
- **Netherlands Women's — Merel van Dongen**: 5/69 assessable pressures (7.25%); 4 unassessable of 73 total; observed 1.0651/90. Statuses: {'no_new_possession_within_window': 64, 'already_own_possession': 4, 'next_own_within_window': 5}.
- **Nigeria Women's — Chidinma Nkeruka Okeke**: 2/21 assessable pressures (9.52%); 2 unassessable of 23 total; observed 0.6037/90. Statuses: {'already_own_possession': 2, 'no_new_possession_within_window': 19, 'next_own_within_window': 2}.
- **Nigeria Women's — Ngozi Ebere**: 3/34 assessable pressures (8.82%); 3 unassessable of 37 total; observed 1.0029/90. Statuses: {'no_new_possession_within_window': 31, 'next_own_within_window': 3, 'already_own_possession': 2, 'period_end_before_full_window': 1}.
- **Norway Women's — Ingrid Moe Wold**: 4/44 assessable pressures (9.09%); 5 unassessable of 49 total; observed 0.7530/90. Statuses: {'no_new_possession_within_window': 40, 'next_own_within_window': 4, 'already_own_possession': 5}.
- **Norway Women's — Kristine Minde**: 8/64 assessable pressures (12.50%); 8 unassessable of 72 total; observed 1.3728/90. Statuses: {'no_new_possession_within_window': 56, 'already_own_possession': 8, 'next_own_within_window': 8}.
- **South Africa Women's — Lebogang Ramalepe**: 7/67 assessable pressures (10.45%); 6 unassessable of 73 total; observed 2.1725/90. Statuses: {'no_new_possession_within_window': 60, 'next_own_within_window': 7, 'already_own_possession': 6}.
- **Spain Women's — Marta Corredera Rueda**: 10/74 assessable pressures (13.51%); 8 unassessable of 82 total; observed 2.3038/90. Statuses: {'next_own_within_window': 10, 'no_new_possession_within_window': 64, 'already_own_possession': 8}.
- **Sweden Women's — Hanna Erica Maria Glas**: 17/100 assessable pressures (17.00%); 9 unassessable of 109 total; observed 2.4186/90. Statuses: {'already_own_possession': 9, 'no_new_possession_within_window': 83, 'next_own_within_window': 17}.
- **Sweden Women's — Magdalena Lilly Eriksson**: 5/42 assessable pressures (11.90%); 4 unassessable of 46 total; observed 0.7314/90. Statuses: {'no_new_possession_within_window': 37, 'next_own_within_window': 5, 'already_own_possession': 4}.
- **Thailand W — Sunisa Srangthaisong**: 3/46 assessable pressures (6.52%); 2 unassessable of 48 total; observed 0.9335/90. Statuses: {'no_new_possession_within_window': 43, 'already_own_possession': 2, 'next_own_within_window': 3}.
- **United States Women's — Crystal Alyssia Dunn Soubrier**: 17/84 assessable pressures (20.24%); 9 unassessable of 93 total; observed 2.5906/90. Statuses: {'next_own_within_window': 17, 'already_own_possession': 9, 'no_new_possession_within_window': 67}.
- **United States Women's — Kelley Maureen O'Hara**: 8/53 assessable pressures (15.09%); 11 unassessable of 64 total; observed 1.3572/90. Statuses: {'already_own_possession': 11, 'next_own_within_window': 8, 'no_new_possession_within_window': 45}.

## Interpretation

The pressing team was assigned the next recorded possession quickly after these actions. This does not prove the pressing player caused it or recovered the ball herself. Next-possession labels can include restarts and are not guaranteed to identify the instant of controlled possession. No confirmed success percentage, causal effect, ability ranking or provider equivalence is claimed. An observed negative does not prove poor pressing: an action might force a backward pass, delay an attack or produce a benefit outside this rule.

## Reproduce

Run `python 77_fullback_next_possession.py` in Spyder. [Evidence](../data/77_fullback_next_possession_evidence.json) · [Lesson](../lessons/0059-fullback-next-possession.html).
Source: StatsBomb Open Data, hash-checked raw fixtures. Assisted work, no footage review or independent mastery demonstrated.
