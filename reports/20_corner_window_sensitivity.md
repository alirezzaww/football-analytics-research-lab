# Lesson 37: test the time-window assumption

## Completed worked assignment

Keep the same 13 France corner deliveries, shot eligibility, provider possession rule and restart/period/goal boundaries. Change only the maximum elapsed time, reporting all four windows chosen in `data/37_corner_window_protocol.json` before this calculation:

- **5 seconds:** four corners associated with four shots; 4/13 = **30.77%**.
- **10 seconds:** six corners associated with six shots; 6/13 = **46.15%**.
- **15 seconds:** six corners associated with seven shots; 6/13 = **46.15%**.
- **20 seconds:** six corners associated with seven shots; 6/13 = **46.15%**.

Two associated shots became goals at every window. Korea Republic's single corner has no associated shot under any of the four rules. These are repeated definitions on one inspected match, not four independent samples.

## Interpretation

The corners-with-a-shot result is stable across the tested 10–20 second limits, but lower at five seconds. This is limited robustness to the selected window values, not proof that 15 seconds is correct or that the rate generalizes to other matches. We do not select the largest observed percentage as the best definition. Longer windows allow additional associations but do not establish stronger causal attribution.

The shot count changes between ten and 15 seconds even though the corners-with-shots count stays six. A second shot occurs 10.282 seconds after the 12:11 delivery, within a corner phase already containing an earlier shot. This reinforces why shot counts and corners producing shots are different outcomes.

The shot after the 53:40 delivery occurs **5.003 seconds** later: it is outside the five-second window. Use millisecond timestamps for inclusion, not rounded displayed minutes/seconds. Another shot at 6.324 seconds after the 32:28 delivery explains the other additional shot-associated corner at ten seconds.

**Completed analyst brief:** “With fixed possession and restart boundaries, six of France's 13 corners associate with a shot using 10-, 15- or 20-second limits, versus four at five seconds. This supports reporting the exact rule and the tested sensitivity, rather than presenting one rate as an assumption-free measure.”

## What sensitivity is—and is not

Changing a chosen analysis rule measures definition sensitivity. A confidence interval addresses a different question about uncertainty under sampling/model assumptions. This chart is not a confidence interval and does not quantify how France would perform in future matches. No model was fitted, recalibrated or newly validated. All windows reuse the same events, and only the window varies; no broad search over possession or boundary rules was performed.

## Reproduce

Run `python 37_corner_window_sensitivity.py`. It reuses the lesson-36 scanner, preserves all phase memberships and stop reasons in `data/37_corner_window_evidence.json`, records source/protocol SHA256 digests, and saves `figures/40_corner_window_sensitivity.png`. The 15-second memberships must reproduce lesson 36 exactly. The evidence checker validates every team's denominator, nested membership, shot totals and reference result; cached raw data allow replaying each window. Unit tests include a 5.003-second endpoint.

Worked assignment completed with assistance. Independent user mastery is not claimed. Foundation: the project's earlier passing-window sensitivity exercise and [Soccermatics possession chains](https://soccermatics.readthedocs.io/en/latest/gallery/lesson4/plot_PossesionChain.html). Data/timestamp structure: [StatsBomb specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). These window choices are project-specific.
