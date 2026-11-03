# Lesson 36: direct links versus bounded corner phases

## Worked assignment result

Using the same **13 France corner deliveries**, the direct-link definition associates two corners with shots (**15.38%**). A broader, explicitly bounded phase proxy associates **six corners with seven shots (46.15% of deliveries)**. Two of the seven shots are goals. Five associated shots have no direct corner-assist link; no fitting or new validation occurred.

The six shot-associated deliveries are at 12:11 (two shots), 21:29, 32:28, 34:52, 46:55 in first-half added time, and 53:40 in the second half. Each associated shot is saved with an ID and elapsed time. The last three corners occur in quick succession at 53:00, 53:20 and 53:40; only the final one receives the later shot under these rules. No shot is assigned to multiple corners.

## Rules defined before this calculation

`data/36_corner_phase_protocol.json` was written before running this phase calculation. It is a transparent analysis definition, not a preregistered fresh test: this match and its events had already been inspected in previous lessons.

Start at each period-1/2 corner Pass event from lesson 35. Continue through event order within the same provider possession, for at most 15 seconds inclusive. Stop at the first possession-ID change, period change, new restart pass (Corner, Free Kick, Throw-in, Goal Kick or Kick Off), shot goal or own-goal event. Keep a goal shot before stopping. Only the same team's non-penalty shots from the existing lesson-29 ledger are eligible. Millisecond timestamps retain first-half added time and enforce the exact 15-second endpoint without floating-point subtraction ambiguity.

This proxy can include actions after an initially incomplete delivery if the provider still retains the same possession. It excludes shots after a possession change or after 15 seconds, even when a human reviewer might consider them part of a corner phase. New-restart boundaries stop attribution carrying into another delivery. This is one operational definition, not a universal provider or tactical standard, and it was not tuned to maximize the result.

## Denominators and interpretation

**Corners with at least one associated shot / all corner deliveries = 6/13.** Do not substitute seven shots in the numerator of that percentage: one corner produced two shots. A separate shots-per-delivery count is 7/13; it answers a different question and need not be bounded by one in general. Goal counts are observed shot goals, not expected goals or a probability forecast. No shot xG was changed or refitted.

**Completed analyst brief:** “France had 13 recorded corner deliveries. Two had explicit direct shot links, while six were followed by at least one same-possession shot within the bounded 15-second phase rule. The broader definition captures follow-up attempts, but neither rate measures causal corner value or establishes repeatable performance from one match.”

The other team's single delivery had no associated shot under either rule. Do not rank team set-piece ability using these sample sizes. No video was reviewed, and a positive phase association does not identify the exact buildup mechanism.

## Reproduce and checks

Run `python 36_corner_phase_analysis.py`. It uses the existing hash-verified raw cache/download routine. Outputs are `data/36_corner_phase_evidence.json` and `figures/39_corner_phase_comparison.png`. The protocol and input artifact hashes are recorded. Unit tests cover millisecond endpoints, first-half added time, possession/period/restart boundaries, multiple shots, goal termination and own goals. Saved membership/aggregates reconcile without raw caches; cached raw data permit replaying every phase boundary and assignment.

Assignment completed as an assisted worked example, not independent user practice. Learning goal: define a sequence before measuring it, distinguish shot counts from corners-with-shots, and explain sensitivity to phase boundaries.

Sources: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf) for event structure, timestamps and possession fields; [Soccermatics possession chains](https://soccermatics.readthedocs.io/en/latest/gallery/lesson4/plot_PossesionChain.html) for the course foundation. The 15-second rule is this project's choice, not a rule attributed to those sources.
