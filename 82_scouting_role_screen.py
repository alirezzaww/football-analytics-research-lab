"""Lesson 82: an auditable two-condition role screen over the existing database."""
from contextlib import closing
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
SOURCE = 'data/81_scouting_database_evidence.json'
PROTOCOL = 'data/82_scouting_screen_protocol.json'
QUERY = 'sql/82_role_screen.sql'
spec = importlib.util.spec_from_file_location('scouting81', ROOT/'81_scouting_database.py')
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)
READING = 'https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html'


def parameters(protocol):
    if (protocol['competition_id'],protocol['season_id'],protocol['season']) != (72,30,'2019'):
        raise ValueError('Screen competition or season differs')
    if protocol['side_group'] not in ('left_only','right_only','mixed'):
        raise ValueError('Invalid side group')
    if type(protocol['min_starts']) is not int or protocol['min_starts'] < 3:
        raise ValueError('Minimum starts cannot expand the original three-start pool')
    for field in ('min_completed_per90','min_forward_per90'):
        value = protocol[field]
        if type(value) not in (int,float) or not math.isfinite(value) or value < 0:
            raise ValueError('Activity floors must be finite nonnegative numbers')
    return {k:protocol[k] for k in ('side_group','min_starts','min_completed_per90','min_forward_per90')}


def screen(connection, protocol):
    bound = parameters(protocol)
    connection.row_factory = sqlite3.Row
    return [dict(r) for r in connection.execute((ROOT/QUERY).read_text(),bound)]


def summarize(rows):
    identities = [(r['competition_id'],r['season_id'],r['team_id'],r['player_id']) for r in rows]
    if len(identities) != len(set(identities)):
        raise ValueError('Duplicate eligible profile')
    counts = {'eligible':len(rows),'meet_passing_floor':0,'meet_forward_floor':0,
              'meet_both':0,'passing_only':0,'forward_only':0,'neither':0}
    for row in rows:
        a,b,both = row['meets_passing_floor'],row['meets_forward_floor'],row['meets_both']
        if a not in (0,1) or b not in (0,1) or both not in (0,1) or bool(both) != (bool(a) and bool(b)):
            raise ValueError('Inconsistent screen flags')
        counts['meet_passing_floor'] += a
        counts['meet_forward_floor'] += b
        counts['meet_both'] += both
        if a and not b: counts['passing_only'] += 1
        elif b and not a: counts['forward_only'] += 1
        elif not a and not b: counts['neither'] += 1
    if sum(counts[k] for k in ('meet_both','passing_only','forward_only','neither')) != len(rows):
        raise ValueError('Screen categories do not partition the eligible pool')
    return counts


def build_evidence():
    source = json.loads((ROOT/SOURCE).read_text())
    protocol = json.loads((ROOT/PROTOCOL).read_text())
    parameters(protocol)
    if (source['competition_id'],source['season_id'],source['season']) != (72,30,'2019'):
        raise ValueError('Database evidence competition or season differs')
    # Rebuild in memory from canonical rows; do not trust a stale local database file.
    for record in source['sql_files'].values():
        if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Database SQL changed since canonical evidence was built')
    with closing(sqlite3.connect(':memory:')) as connection:
        database.create_database(connection,source['rows'])
        rows = screen(connection,protocol)
    selected = [r for r in rows if r['meets_both']]
    return {'competition':source['competition'],'season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3','section':'Case study: spreadsheet scouting','url':READING},
            'source_path':SOURCE,'source_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
            'protocol_path':PROTOCOL,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest(),
            'query_path':QUERY,'query_sha256':hashlib.sha256((ROOT/QUERY).read_bytes()).hexdigest(),
            'parameters':parameters(protocol),'eligible_rows':rows,'selected_rows':selected,'counts':summarize(rows),
            'scope':'A demonstration screen on the original historical cohort, not a validated football role model, scouting grade, causal finding or signing recommendation. Two related passing measures are not independent quality evidence. No pressure floor, composite weighting, new training or footage review.'}


def render_report(evidence):
    p = evidence['parameters']; c = evidence['counts']
    def line(row):
        return f"- **{row['player_name']} — {row['team_name']}**: {row['completed_per90']:.2f} completed passes/90; {row['forward_per90']:.2f} fixed-rule forward passes/90; passing floor {'met' if row['meets_passing_floor'] else 'not met'}, forward floor {'met' if row['meets_forward_floor'] else 'not met'}."
    selected = '\n'.join(line(r) for r in evidence['selected_rows']) or 'No profiles meet both floors.'
    excluded = '\n'.join(line(r) for r in evidence['eligible_rows'] if not r['meets_both']) or 'No eligible profiles excluded.'
    return f'''# A first role-based scouting screen

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Case study: spreadsheet scouting]({READING}); [SQLite expressions and AND](https://www.sqlite.org/lang_expr.html).
This is our assisted SQL extension.

## Illustrative requirement

{p['side_group']} profiles, at least {p['min_starts']} qualifying starts, **completed passes/90 ≥{p['min_completed_per90']:g} AND fixed-rule forward passes/90 ≥{p['min_forward_per90']:g}**. Cutoffs are teaching choices stated before this query, not measured standards, validated optimal requirements or a real club brief. Forward means a completed eligible pass with x gain≥20 coordinate units, not all forward-directed passes or line-breaking value. Side labels describe qualifying starts, not every minute or career position.

## Result

**{c['eligible']} eligible profiles → {c['meet_passing_floor']} meet the passing floor → {c['meet_both']} meet both floors.** This sequence adds the forward condition after passing; it is not a performance funnel or new model evaluation.

Across the same eligible pool, {c['meet_forward_floor']} meet the forward floor by itself. The mutually exclusive categories are: both {c['meet_both']}, passing only {c['passing_only']}, forward only {c['forward_only']}, neither {c['neither']}. These sum to {c['eligible']}; the two single-condition totals overlap and should not be added as disjoint groups.

### Profiles meeting both conditions

{selected}

### Other eligible profiles, with visible reasons

{excluded}

## How the screen works

SQL AND requires both conditions. The query keeps every role-eligible row and adds each condition's flag, then a meets_both flag. This makes exclusions inspectable. All comparisons use unrounded rates; rounding is only for display. Values are bound parameters. Display order is forward activity, then passing activity among the selected profiles; it is not an overall quality score or a top-N quota.

The screen rebuilds the database in memory from canonical lesson81 rows rather than reading a potentially stale local file. Original counts, playing windows and 35-player cohort remain unchanged. Eligible rows are not every right back in football, and omitted players cannot be recovered through these filters.

## What should happen next?

Treat the selected set as a bounded list for investigation. For each profile, inspect the underlying matches, passing locations and role before judging whether the observed activity fits the intended football task. Forward count is a subset of completed passes, so the two criteria are related and do not independently establish two abilities. Check whether the list changes under a reasonable nearby threshold before relying on the boundary; that sensitivity has not been calculated here. No footage has been reviewed and no availability/contract assessment is included.

## Reproduce

Run `python 82_scouting_role_screen.py` in Spyder. [Protocol](../{PROTOCOL}) · [SQL query](../{QUERY}) · [Evidence and every eligible row](../data/82_scouting_role_screen_evidence.json) · [Lesson](../lessons/0064-scouting-role-screen.html).
The public protocol records the chosen cutoffs and purpose. Source, query and protocol hashes support exact replay. Independent user construction and interpretation remain to demonstrate.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/82_scouting_role_screen_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/65_scouting_role_screen.md').write_text(render_report(evidence))
    print('Counts:',evidence['counts'])
    for row in evidence['selected_rows']:
        print(row['player_name'],f"{row['completed_per90']:.2f} completed/90",f"{row['forward_per90']:.2f} forward/90")


if __name__ == '__main__':
    main()
