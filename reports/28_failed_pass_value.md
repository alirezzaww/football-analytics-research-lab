# Lesson 45: what completed-pass xT leaves out

## Completed worked assignment

The standard position-based xT application demonstrated in the [socceraction documentation](https://socceraction.readthedocs.io/en/stable/documentation/valuing_actions/xT.html) values successful ball-moving actions. A completed pass receives destination value minus starting value. It does not, by itself, provide a full assessment of all pass attempts or decision quality.

We retain that completed-pass calculation, then add a **separately labelled project diagnostic**: assume an unsuccessful pass leaves zero own-team continuation value, assigning `0 − start xT`. This failure-cost scenario is not the standard successful-move xT metric, an independently validated extension or a confirmed observation of possession loss.

## Rules and source scope

Use the 3,447 Pass actions already selected in lesson 44, with the exact same fitted grid. Join raw outcome labels by match/event ID after verifying source hashes. This is the filtered possession-team, non-restart sample from both teams in five France fixtures, not every pass in those matches.

- No recorded outcome: score the completed pass as end value minus start, provided its endpoint can be valued.
- Incomplete, Out or Pass Offside: assign minus starting value under the zero-continuation assumption.
- Unknown, Injury Clearance or unexpected outcomes: exclude from the scenario sum, retaining their records and count.
- A completed pass without a usable endpoint remains unscorable rather than becoming a failure.

All selected teams together have 2,741 scored completions, 689 scored unsuccessful passes and 17 excluded outcome records. Of the latter, 16 have Unknown outcome and one Injury Clearance. All recorded endpoints in this selected pass sample map to the grid.

## France results

France's selected sample contains **2,097 pass attempts**: 1,723 scored completed passes, 367 scored unsuccessful passes, and seven Unknown outcomes excluded from this scenario.

- Signed completed-pass xT sum: **+3.767404**.
- Assumed unsuccessful-pass cost: **−8.108605**.
- Combined scenario sum: **−4.341201**.

These quantities are sums over the filtered pass actions, not shots or entire attacking possessions. The combined number is not a goal forecast, a whole-match performance rating or evidence that France performed poorly. It demonstrates how strongly an aggregate can depend on which outcomes and continuation assumptions are scored. Do not compare it directly with a provider's successful-move xT total under a different definition.

## Actual failed-pass example

The first selected France failure with a higher-valued recorded endpoint is an Incomplete pass by Griedge Mbock Bathy Nka:

- Start zone value: **0.010684**.
- Recorded endpoint zone value: **0.033988**.
- Scenario score: **−0.010684**.

Subtracting start from the recorded endpoint would incorrectly credit a successful move that did not occur. The recorded failure endpoint is not a verified intended target, and the diagnostic does not establish where a teammate could have received a successful pass. Exact event ID and coordinates are saved.

For intuition, a completed move from 0.03 to 0.08 receives +0.05. If the move is unsuccessful and we assume zero continuation, the scenario score is −0.03. The 0.03/0.08 numbers here are illustrative, not the actual example above.

## Limits of the failure assumption

An unsuccessful pass can leave a loose ball, produce a retained attacking restart or have other continuation. Out does not establish which team takes the next restart. Even an incomplete event is not a full reconstruction of the later possession. Zero continuation is therefore an explicit simplifying assumption; the model also omits the opponent's counterattack threat. A complete action-value model would require clear state transitions and an evaluation plan.

**Completed analyst brief:** “Completed-pass xT summarizes value changes on successful moves. Including unsuccessful attempts under a zero-continuation assumption changes France's aggregate substantially, but that scenario is not a complete performance metric. We should report outcome coverage and the scoring convention before comparing players or teams.”

## Reproduce and verify

Run `python 45_failed_pass_value.py`. It reproduces/verifies the existing lesson-44 source and fitted grid, joins raw outcomes, then saves `data/45_failed_pass_value_evidence.json` and `figures/47_failed_pass_value.png`. The original lesson-44 model artifact is unchanged. No new model version or fresh validation is claimed.

Tests cover positive/negative/zero completed scores, no destination credit for failed actions, unknown outcomes and excluded versus zero-valued actions. Evidence checks reconcile every original pass, source digest, raw outcomes when cached, scoring status and France/all-selected-team sums. Worked implementation completed with assistance; independent user mastery is not claimed.

Data: StatsBomb Open Data. Builds on the Soccermatics/mplsoccer educational xT exercise; the failure-cost assumption is this project's diagnostic choice, not attributed to those tutorials.
