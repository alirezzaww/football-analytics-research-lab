# Lesson 34: verify the passes behind the headers

We follow up on all three headers in the existing France–Korea Republic shot ledger, rather than inferring their source from body part alone. The frozen xG model and shot selection remain unchanged. This is inspection of already used events, not fresh validation or video review.

## Verified findings

- **34:54, first half:** Gaëtane Thiney's recorded corner delivery is linked to Wendie Renard's header goal.
- **37:52, first half:** Elise Bussaglia's pass, explicitly flagged as a cross, is linked to Gaëtane Thiney's off-target header. The play pattern is Regular Play.
- **46:57, first-half added time:** Amel Majri's recorded corner delivery is linked to another Renard header goal. The period field is 1; this is not a second-half event.

Both scored headers in this match followed directly linked corner passes. This does not establish corner conversion efficiency: we have selected headers, not counted all corners. Nor does it prove crossing superiority or explain France's overall first-half advantage. There are only three selected events.

## How the join works

The shot's `shot.key_pass_id` points to a pass event ID. The pass's `pass.assisted_shot_id` must point back to the shot. We verify event type, same team, period and possession, and pass index before shot index. We do not select the nearest earlier pass or assume every header has an assisting cross. Missing and unavailable links remain explicit unresolved statuses; inconsistent links raise an error.

The plot shows only each linked pass and the header location, not a continuous full possession. Blue arrow endpoints are recorded pass endpoints; the gold star is the separately recorded shot start. These locations need not coincide. An arrow is a schematic start-to-end link, not a measured curved flight trajectory.

## Why shot type is insufficient here

All three shot events have `shot.type.name = Open Play`. Two nevertheless have `play_pattern.name = From Corner` and linked passes with `pass.type.name = Corner`. The provider's shot-type field is not a complete classification of the preceding attacking phase. We retain these fields separately instead of treating Open Play as proof that no corner preceded the shot. The cross flag is present and true for Bussaglia's pass; it is absent on these corner passes, saved as null and described as not recorded rather than assumed false.

Definitions: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). The source defines explicit assisting-event fields and distinguishes a shot taken directly from a corner from an ordinary shot; a header following a corner delivery is not the corner kick itself. This lesson uses observed historical raw labels, not an inferred modern platform classification.

## Reproduce and audit

Run `python 34_header_assisting_passes.py` in Spyder. It reads lesson 33's tagged ledger, uses the existing one-fixture hash-checked cache/download procedure, and writes `data/34_header_assists_evidence.json` and `figures/37_header_assisting_passes.png`. Unit tests cover valid links, missing links and rejected reciprocal/context mismatches. Saved evidence reconciles header identity and probabilities without raw data; when the raw cache is present, pass and shot attributes are independently reconciled against the source events.

Prepared with assistance. Independent task: write a three-sentence coach brief stating the verified header origins, the sample/denominator limitation, and a video question. Suggested question: how did Renard's movement and defensive marking differ across the two corner deliveries? Event positions alone cannot answer it. No video has been reviewed or made available in this lesson.

Data: StatsBomb Open Data. Foundation: Soccermatics; this is an original project extension. Independent interpretation remains pending.
