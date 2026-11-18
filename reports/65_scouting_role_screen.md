# A first role-based scouting screen

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Case study: spreadsheet scouting](https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html); [SQLite expressions and AND](https://www.sqlite.org/lang_expr.html).
This is our assisted SQL extension.

## Illustrative requirement

right_only profiles, at least 3 qualifying starts, **completed passes/90 ≥30 AND fixed-rule forward passes/90 ≥3**. Cutoffs are teaching choices stated before this query, not measured standards, validated optimal requirements or a real club brief. Forward means a completed eligible pass with x gain≥20 coordinate units, not all forward-directed passes or line-breaking value. Side labels describe qualifying starts, not every minute or career position.

## Result

**14 eligible profiles → 6 meet the passing floor → 4 meet both floors.** This sequence adds the forward condition after passing; it is not a performance funnel or new model evaluation.

Across the same eligible pool, 8 meet the forward floor by itself. The mutually exclusive categories are: both 4, passing only 2, forward only 4, neither 4. These sum to 14; the two single-condition totals overlap and should not be added as disjoint groups.

### Profiles meeting both conditions

- **Lucy Bronze — England Women's**: 45.57 completed passes/90; 4.43 fixed-rule forward passes/90; passing floor met, forward floor met.
- **Desiree van Lunteren — Netherlands Women's**: 33.44 completed passes/90; 4.23 fixed-rule forward passes/90; passing floor met, forward floor met.
- **Ashley Elizabeth Marie Lawrence — Canada Women's**: 32.72 completed passes/90; 3.09 fixed-rule forward passes/90; passing floor met, forward floor met.
- **Risa Shimizu — Japan Women's**: 39.48 completed passes/90; 3.06 fixed-rule forward passes/90; passing floor met, forward floor met.

### Other eligible profiles, with visible reasons

- **Peng Han — China PR Women's**: 22.76 completed passes/90; 4.65 fixed-rule forward passes/90; passing floor not met, forward floor met.
- **Chidinma Nkeruka Okeke — Nigeria Women's**: 13.28 completed passes/90; 3.62 fixed-rule forward passes/90; passing floor not met, forward floor met.
- **Ingrid Moe Wold — Norway Women's**: 23.16 completed passes/90; 3.58 fixed-rule forward passes/90; passing floor not met, forward floor met.
- **Marion Torrent — France Women's**: 23.13 completed passes/90; 3.05 fixed-rule forward passes/90; passing floor not met, forward floor met.
- **Kelley Maureen O'Hara — United States Women's**: 35.80 completed passes/90; 2.71 fixed-rule forward passes/90; passing floor met, forward floor not met.
- **Ellie Madison Carpenter — Australia Women's**: 32.32 completed passes/90; 2.32 fixed-rule forward passes/90; passing floor met, forward floor not met.
- **Hanna Erica Maria Glas — Sweden Women's**: 25.47 completed passes/90; 2.28 fixed-rule forward passes/90; passing floor not met, forward floor not met.
- **Letícia Santos de Oliveira — Brazil Women's**: 15.50 completed passes/90; 1.97 fixed-rule forward passes/90; passing floor not met, forward floor not met.
- **Lebogang Ramalepe — South Africa Women's**: 15.83 completed passes/90; 1.55 fixed-rule forward passes/90; passing floor not met, forward floor not met.
- **Giulia Gwinn — Germany Women's**: 26.91 completed passes/90; 1.22 fixed-rule forward passes/90; passing floor not met, forward floor not met.

## How the screen works

SQL AND requires both conditions. The query keeps every role-eligible row and adds each condition's flag, then a meets_both flag. This makes exclusions inspectable. All comparisons use unrounded rates; rounding is only for display. Values are bound parameters. Display order is forward activity, then passing activity among the selected profiles; it is not an overall quality score or a top-N quota.

The screen rebuilds the database in memory from canonical lesson81 rows rather than reading a potentially stale local file. Original counts, playing windows and 35-player cohort remain unchanged. Eligible rows are not every right back in football, and omitted players cannot be recovered through these filters.

## What should happen next?

Treat the selected set as a bounded list for investigation. For each profile, inspect the underlying matches, passing locations and role before judging whether the observed activity fits the intended football task. Forward count is a subset of completed passes, so the two criteria are related and do not independently establish two abilities. Check whether the list changes under a reasonable nearby threshold before relying on the boundary; that sensitivity has not been calculated here. No footage has been reviewed and no availability/contract assessment is included.

## Reproduce

Run `python 82_scouting_role_screen.py` in Spyder. [Protocol](../data/82_scouting_screen_protocol.json) · [SQL query](../sql/82_role_screen.sql) · [Evidence and every eligible row](../data/82_scouting_role_screen_evidence.json) · [Lesson](../lessons/0064-scouting-role-screen.html).
The public protocol records the chosen cutoffs and purpose. Source, query and protocol hashes support exact replay. Independent user construction and interpretation remain to demonstrate.
