# Fullback profiles: activity needs football context

**Alireza Erfanian · Football Analytics Research Lab · Prepared 18 November 2026 · Guided portfolio work**

**Study:** FIFA Women's World Cup, **2019** (StatsBomb competition 72 / season 30). **Question:** What behaviours should a scout investigate in these two historical profiles? The full profiling pool has 35 players; this brief uses two familiar examples with different starting sides, not ranked or interchangeable recruitment candidates.

## Executive Summary

- Bronze recorded **45.57 completed eligible passes per 90**, versus **30.70** for Majri. Their shares of same-window team completions were **12.34%** and **10.60%**. These identify different observed involvement, without isolating ability from role or team context. [1]
- Bronze's pressure rate was higher per 90 (**13.28 vs 10.89**), but the figures were close per 100 eligible opponent attempts (**5.01 vs 4.89**). Majri made a larger share of her pressures in the opponent third (**24.6% vs 19.6%**). The denominator and location change the question, not the original actions. [2, 3]
- Use these findings to focus further observation. The outcome proxies contain unclear cases and limited pass-link coverage; they do **not** support an overall defensive-quality ranking or a signing decision. Neither footage review nor current availability assessment has been performed. [4, 5]

## Lucy Bronze — England Women's

7 right back starts; 691.2 reconstructed registered minutes in those qualifying fixtures. These include later role changes, not verified time spent solely at fullback.

- **Passing involvement:** 350/436 eligible passes completed (80.3%); **45.57 completions per 90**. Her 350 completions represent **12.34%** of 2837 same-window eligible team completions. [1]
- **Forward movement:** 34 completed passes advanced at least 20 x-coordinate units (4.43/90). The near-goal alternative includes 36 (4.69/90). These are project definitions, not measured action value. [6]
- **Pressure context:** 102 recorded pressures, **13.28/90**; **5.01 per 100** eligible opponent pass attempts (2034 attempts). This ratio is a volume proxy, not the percentage of passes she pressured. [2]
- **Where and when:** 20/102 mapped starts in the opponent third (19.6%); 20/102 pressures flagged as counterpressing (19.6%). Location and post-turnover timing do not establish success. [3, 7]
- **Outcome coverage:** the custom next-possession check matches 12/81 assessable pressures, with 21 unclear cases. Separately, 28/102 pressures link to 28 unique opponent passes: 19 completed, 8 not completed, 1 unassessable. The two outcome measures have different populations and are not combined into a success score. [4, 5]

## Amel Majri — France Women's

5 left back starts; 504.2 reconstructed registered minutes in those qualifying fixtures. These include later role changes, not verified time spent solely at fullback.

- **Passing involvement:** 172/222 eligible passes completed (77.5%); **30.70 completions per 90**. Her 172 completions represent **10.60%** of 1623 same-window eligible team completions. [1]
- **Forward movement:** 18 completed passes advanced at least 20 x-coordinate units (3.21/90). The near-goal alternative includes 19 (3.39/90). These are project definitions, not measured action value. [6]
- **Pressure context:** 61 recorded pressures, **10.89/90**; **4.89 per 100** eligible opponent pass attempts (1248 attempts). This ratio is a volume proxy, not the percentage of passes she pressured. [2]
- **Where and when:** 15/61 mapped starts in the opponent third (24.6%); 17/61 pressures flagged as counterpressing (27.9%). Location and post-turnover timing do not establish success. [3, 7]
- **Outcome coverage:** the custom next-possession check matches 1/43 assessable pressures, with 18 unclear cases. Separately, 7/61 pressures link to 7 unique opponent passes: 4 completed, 3 not completed, 0 unassessable. The two outcome measures have different populations and are not combined into a success score. [4, 5]


## What should a scout investigate?

For Bronze, check whether the higher passing involvement repeatedly reflects useful progression or predominantly safe circulation in her right-sided role. For Majri, check which situations produce the greater opponent-third share of pressure starts in her left-sided role. For both, inspect the options available, teammates' support and the opponent's response before attributing value to an action. These are questions suggested by the profiles, not observations already established.

The existing queue below gives six deliberately chosen event references: four pass-definition examples and two first linked-pressure/pass examples. They are starting points for inspection, not a representative performance sample. Match/period clocks need aligning to available footage; no video-file offsets are supplied. Review these cases when footage is available, then check whether observations recur across comparable situations before making a player judgement.

### Passing examples already queued

- **Lucy Bronze vs Scotland W**, 2019-06-09, period 1, 00:23:43.899: Fixed-rule example. Match 22936, event `a4f3b3e8-e86d-4753-82e2-ab37fcbaeafe`. **Not reviewed**; observation unfilled.
- **Lucy Bronze vs Scotland W**, 2019-06-09, period 2, 00:40:02.457: Additional alternative-rule example. Match 22936, event `0c5e5756-2841-4f30-9635-7d7656e51871`. **Not reviewed**; observation unfilled.
- **Amel Majri vs Korea Republic Women's**, 2019-06-07, period 1, 00:02:30.477: Fixed-rule example. Match 22921, event `1b526257-b7c8-4af3-955a-25bdff16fa99`. **Not reviewed**; observation unfilled.
- **Amel Majri vs Nigeria Women's**, 2019-06-17, period 2, 00:49:48.019: Additional alternative-rule example. Match 22980, event `ad95822f-e335-4ae0-8316-50b4ab28fabb`. **Not reviewed**; observation unfilled.

### Pressure/pass examples

- Match 22936, period 1: pressure `c543af09-bb3b-4cc7-a196-32cbded861b8` at 00:06:45.362 → Christie Murray pass `ffb5226d-4927-4364-9d1b-2b58cb80bd83` at 00:06:45.418; outcome Completed (no outcome field). **Not reviewed**; event-data association only.
- Match 22921, period 1: pressure `fb96a1cf-d47a-46cd-a0da-82ab6288aba7` at 00:16:03.342 → Hye-Ri Kim pass `f9fe2285-e271-4884-b807-809131dd96f1` at 00:16:04.526; outcome Incomplete. **Not reviewed**; event-data association only.

## Definitions and practical limits

The cohort requires at least three Left Back/Right Back starts; actions and minutes use only qualifying starting fixtures and reconstructed registered windows. Added/extra time is included; halftime and shootouts are excluded. Later changes of role remain included. Eligible passing excludes restart deliveries, non-possession-team passes and Unknown/Injury Clearance outcomes; later passes after restarts can remain. Team shares include the player and goalkeeper and pool counts before division. [1, 6]

Opponent-pass exposure uses the same eligibility concept for the other team in each player's window; it is not possession duration or a count of personal pressing opportunities. Opponent-third shares use mapped pressure locations, with x≥80 on the normalized 0–120 pitch. Counterpress flags describe pressure within five seconds of an open-play turnover, not regaining possession. [2, 3, 7]

The next-possession proxy follows the first new same-period possession within five seconds of pressure start and reports unclear rows separately. It is not official StatsBomb Pressure Regains. Related-pass results instead use directed event links, without a five-second or restart filter, and deduplicate passes within player. Unknown pass outcomes remain visible. A missing link is not a failed pressure; several players can be linked to the same pass, and a linked incompletion does not establish pressure causation. Do not compare these two outcome denominators as if they describe the same test. [4, 5]

This historical tournament sample does not establish current form, fitness, contract status, availability or transfer suitability. The two players have different starting sides and team contexts. No composite score, causal adjustment or new model validation has been introduced.

## Sources and reproducibility

1. **Passing**: [saved evidence](../data/70_fullback_team_passing_share_evidence.json); SHA-256 `58f695db526d7dd64cca84bb27f298a596353e113e0cccb496a6b7614dac07ce`.
2. **Opponent**: [saved evidence](../data/74_fullback_opponent_pass_context_evidence.json); SHA-256 `52d2792e968d82bf923aaaaf1b334af441ab81277a8f92603b708a981e8b3917`.
3. **Areas**: [saved evidence](../data/75_fullback_pressure_areas_evidence.json); SHA-256 `720f7c4aaedfa9830ce49b6ec982ff2e7ff5174bf0a9323fd9acd01ef18ff5ce`.
4. **Proxy**: [saved evidence](../data/77_fullback_next_possession_evidence.json); SHA-256 `2ea2ee9ff5619fc769310793e07042c98b7790a0898949ef988e6f4092d12a59`.
5. **Linked Passes**: [saved evidence](../data/79_pressure_linked_passes_evidence.json); SHA-256 `e6c9777dc67424c521b49e7265eddc93541234a2a8715f0ad180b629bd98ef4e`.
6. **Original Brief**: [saved evidence](../data/69_fullback_recruitment_brief_evidence.json); SHA-256 `ed0d561b6c3ac758481100668eb4494be1064c9f5208bfeb3e7ad0dabc8753f1`.
7. **Counterpress**: [saved evidence](../data/76_fullback_counterpress_context_evidence.json); SHA-256 `a36394db6744f7e06649d4f96321ea954955d9f9a3a60ae10e9a5cf2c034af9d`.

Reading: [Soccermatics Lesson 3 — Statistical scouting, Modesty](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#modesty); definitions: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Data source: [StatsBomb Open Data](https://github.com/hudl/open-data).

Run `python 80_fullback_portfolio_synthesis.py` in Spyder or locally to rebuild this brief from the saved evidence; no downloads or new estimation are needed. [Synthesis evidence](../data/80_fullback_portfolio_synthesis_evidence.json) · [Lesson 80](../lessons/0062-fullback-portfolio-synthesis.html). Earlier reports remain available, including the [first passing brief](52_fullback_recruitment_brief.md).

**Contribution statement:** Prepared with AI assistance as guided portfolio work. Independent reproduction, interpretation and footage review have not been demonstrated. The event queue remains unreviewed; independent reproduction and interpretation are next learning milestones.
