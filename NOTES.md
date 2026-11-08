# Teaching notes

Use PROJECT_BRIEF.md and LEARNING_JOURNAL.md for the established project history.
The user wants practical analyst training, a credible CV project and continuing GitHub
updates. Python work should be usable in Spyder. Explain the code and football meaning;
move faster when concepts are easy. Do not treat assistant-executed lessons as proof of
independent mastery. Keep learning records for demonstrated understanding only.

Lesson 19 introduces time-window sensitivity; an independent written interpretation
and a new 8-second calculation remain practice, not completed student work.

Lesson 20 adds within-starting-third comparisons and distinguishes location mix from
within-zone qualifying share. Independent Parris/Walsh interpretation remains pending.
Next teaching should build from explanation of denominators and context, not assume
that assistant-generated features demonstrate independent analytical competence.

Lesson 21 introduces a paired whole-match bootstrap as an illustrative uncertainty
exercise. Do not describe its interval as reliable population inference from seven
selected fixtures or as probability of player superiority. Independent explanation
of sampling units, pairing and resampling versus new evidence is still pending.

The user reported understanding bootstrap after simpler concrete examples; do not
repeat the entire method unless requested. Lesson 22 moves to whole-team score-state
context, explicitly changing scope from attacking-third player comparisons. Explain
pre-pass labeling and opponent/score confounding in plain language. Coach-facing
independent interpretation remains pending.

Lesson 23 checks fixture overlap and shows how restricting the Drawing/Trailing
comparison to USA and Sweden changes the pooled ordering. Explain in plain language
that a common fixture set still does not isolate score effects. Missing exposure and
measured zero are different; do not infer mastery from material covered.

Lesson 24 uses a concrete timeline to distinguish 12 pass actions from three
represented shots and three possessions. Do not imply direct passer-to-recipient
links or causal credit from the selected timeline. The independent reporting task
is pending; avoid recording the lesson as demonstrated mastery.

The user explicitly wants easy concepts covered faster. Lesson 25 returns to the
Soccermatics xG path and bundles angle features with grouped training-only validation.
Keep the live explanation focused on the feature, fair check and negative result;
formulas and implementation details can be opened on request. Independent defence
of the modelling workflow remains pending; do not equate coverage with competence.

Before resuming lesson 26, the user needed repeated clarification of model training,
predicted probabilities versus binary outcomes, true unknown per-shot xG, and relative
comparison versus practical reliability. Use one concrete group example at a time;
do not assume familiarity with fitting or validation from prior code coverage.
The calibration diagnostic is now implemented, but independent interpretation remains
pending. More fresh match data is needed for an honest reliability assessment.

Lesson 27 supplies actual new-fixture evidence after the user's questions about
reliability. Clearly distinguish 114 TRAINING shots from 1,131 EVALUATION shots: no
refit occurred. Model beats its fixed baseline on the 45 other same-tournament
fixtures; do not imply exact true xG, different-season validation or readiness.
The protocol was committed first. The new evaluation is now inspected; later tuning
against it cannot be described as fresh. Independent explanation remains pending.

The user again clarified the meaning of the 11/114 baseline and how the distance
model changes it. Lesson 28 connects actual grouped training counts to real frozen
formula outputs, then adds the new concept of extrapolation. Explain one example
at a time. Neither group sample rates nor curve outputs are known true individual
xG; independent explanation remains pending. Training-support plots are in-sample
and the evaluation coverage audit reuses already inspected data.

The user explicitly requests faster, compact explanations for familiar/easy concepts, without skipping lessons or assignments. Complete assignments as assisted worked examples and document that status; do not imply independent user mastery. Use deeper explanation when concepts are new or requested.

The user needed repeated concrete explanations of baseline versus zone completion probabilities: show all-training counts versus one-zone counts, keep training data distinct from checked outcomes, and state that we use all 24 zones while focusing on one example for teaching. Avoid jumping from zone context to a specific pass-option probability.

Employment remains central. On 2026-11-04 the user answered “anything” for job location/remote/on-site/sponsorship targeting: treat location preferences as broad, not as evidence of work authorization or no sponsorship need. Pair future technical lessons with job-relevant deliverables; SQL and independent reproduction are next practical gaps.

For joins, show separate corner and shot tables before the joined rows. User found the two-corner example helpful; carry that row-grain explanation into grouped queries.

The user requests that references always identify the competition and season being studied so they can read alongside the practice. Include the exact Soccermatics lesson/section and its link as well, to make the course reading location clear. Current dataset: 2019 Women’s World Cup, StatsBomb competition 72 / season 30; recruitment phase reading: Lesson 3, Statistical scouting; use the current reference and RESOURCES.md for the latest section.

User deferred manual/system data collection practice; continue analysis lessons. Lesson 74 adds opponent-attempt exposure context, not pressure success or individual opportunity measurement.

Lesson 75 adds pressure location mix. Keep examples concrete: Bronze has more opponent-third pressures, Majri a larger share. User needed clarification that opponent passes are passes by the other team, anywhere on pitch during selected registered windows.

Lesson 76 separates counterpressing (pressure after loss, provider flag) from pressure regains (outcome not calculated). Bronze has coincidentally 20 opponent-third pressures and 20 counterpress-flagged pressures; equal counts do not mean the same events. Use the imagined loss→pressure timeline, clearly labelled as illustrative.

Lesson 77 uses an explicitly custom next-recorded-possession proxy, not official Pressure Regains. Provider guidance warns IQ possession differs from raw Event Data. Own-possession-labelled pressures are unclear, not confirmed failures; Bronze has21 and Majri18 such cases. Explain with the real Bronze00:51.472→England possession00:53.660 first-half example, not an unsupported causal claim.

Lesson78 teaches actor team versus sequence-start possession_team. Use the real Scotland pass at06:43.781 in England-labelled sequence17, then Bronze pressure06:45.362. All240 selected own-labelled pressures follow their sequence first timestamp;200 share sequences containing opponent Pass/Carry. Do not imply200 unique possessions or label errors. Previous outcomes unchanged.

Lesson79 links pressure IDs to opponent Pass IDs via related_events; do not use nearest-in-time guessing or apply the old passing eligibility filter. Majri has7 linked unique passes,3notcompleted; other54 pressures are not failures. Bronze28 linked passes include1Unknown. Deduplicate per player, preserve whole pressure coverage. Next sensible milestone: consolidate the passing/defensive profiling work into a readable portfolio brief before adding more small metrics.
