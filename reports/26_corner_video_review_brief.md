# Lesson 43: corner video-review brief

## Question for the review

What observable first-contact, receiving and marking details help explain the event sequences behind the endpoint groups?

## Data finding to investigate

Across five France matches, 19 of 45 corner deliveries associate with a shot under the fixed phase rule. Recorded endpoints fall inside the six-yard box (15), elsewhere in the penalty area (19), or outside it (11). These counts describe events; they do not identify intended targets or controlled receptions.

## Selected examples

One example is selected for each zone and each phase-shot status, preferring fixtures not already selected. This deliberate selection supplies review contrasts; it cannot estimate overall rates or causal differences. All percentages remain calculated from the full 45 deliveries.

1. **France v Korea Republic · 2019-06-07 · 33:50 (first half)**
   Amel Majri; Six-yard box; no phase shot under the rule.
   Match `22921`, corner `1a92a4e1-a29c-43c6-966a-dc1a3cded70d`, event index `1111`.
   Review status: **not reviewed**. First contact: unknown. Attacking control: unknown. Video reference: unavailable.

2. **France v Norway · 2019-06-12 · 25:25 (first half)**
   Amel Majri; Six-yard box; phase shot recorded.
   Match `22948`, corner `53cfdc02-7047-42ef-bcbd-efa23cd52551`, event index `703`.
   Review status: **not reviewed**. First contact: unknown. Attacking control: unknown. Video reference: unavailable.

3. **France v Nigeria · 2019-06-17 · 71:03 (second half)**
   Amel Majri; Rest of penalty area; no phase shot under the rule.
   Match `22980`, corner `82c00f82-bc17-4969-8411-eb4e3250f6d5`, event index `2528`.
   Review status: **not reviewed**. First contact: unknown. Attacking control: unknown. Video reference: unavailable.

4. **France v United States · 2019-06-28 · 31:54 (first half)**
   Gaëtane Thiney; Rest of penalty area; phase shot recorded.
   Match `69202`, corner `270adf53-14f0-41a0-839b-3b8454cd02b8`, event index `970`.
   Review status: **not reviewed**. First contact: unknown. Attacking control: unknown. Video reference: unavailable.

5. **France v Brazil · 2019-06-23 · 19:53 (first half)**
   Amel Majri; Outside penalty area; no phase shot under the rule.
   Match `69137`, corner `0466f6e9-18f1-437b-b87a-c72fafe60bfc`, event index `646`.
   Review status: **not reviewed**. First contact: unknown. Attacking control: unknown. Video reference: unavailable.

6. **France v Korea Republic · 2019-06-07 · 32:28 (first half)**
   Amel Majri; Outside penalty area; phase shot recorded.
   Match `22921`, corner `5e672927-1b11-4a57-8f2a-0f93d907aa9b`, event index `1086`.
   Review status: **not reviewed**. First contact: unknown. Attacking control: unknown. Video reference: unavailable.

## Review questions

- Who makes the first visible contact, if the footage shows it?
- Is an attacking receiver clearly in control after the delivery?
- What observable movement, marking or goalkeeper action precedes the outcome?
- Does the visible sequence agree with the logged endpoint and phase boundary?

Use unknown/unclear when an observation is not visible. Distinguish observable actions from a tactical interpretation. A camera cut or obscured player is missing evidence, not evidence of no action.

## Locate the event correctly

The times above are recorded match-clock labels, not positions in a video file. Use the period and opponent/date as well as the clock: first-half added time can overlap nominal second-half minutes. Find the delivery in the footage and record its actual video reference before coding. No footage has been accessed or reviewed for this assignment.

## Reproduce and assignment status

Run `python 43_corner_video_review_brief.py`. It saves `data/43_corner_review_queue_evidence.json` and regenerates this report from the recorded event candidates. Source/protocol hashes and all 45 candidates are preserved so the purposive selection can be reproduced and audited.

**Completed assignment:** a sourced six-example review queue and observation questions. **Not performed:** video observation or tactical coding; those require footage. Preparing the brief does not establish independent user mastery.

This complements the existing StatsBomb event analysis and Soccermatics learning project. No new model, causal effect or fresh validation is claimed.
