"""Lesson 58: enrich corner records and produce a player report with HAVING."""
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
SQL_FILES = {'schema': 'sql/58_corner_takers_schema.sql',
             'query': 'sql/58_corner_taker_report.sql'}
SOURCE_FILES = ['data/38_france_corner_study_evidence.json',
                'data/39_corner_delivery_profiles_evidence.json']
SPEC = importlib.util.spec_from_file_location('joins55', ROOT / '55_football_sql_joins.py')
joins = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(joins)
AUDIT_SPEC = importlib.util.spec_from_file_location('corner_audit59', ROOT / '59_corner_data_quality.py')
audit = importlib.util.module_from_spec(AUDIT_SPEC)
AUDIT_SPEC.loader.exec_module(audit)


def create_database(connection, corners, shots, takers):
    """Require complete one-to-one metadata before an inner join can be safe."""
    audit.require_valid_relationships(corners, shots, takers)
    joins.create_database(connection, corners, shots)
    connection.executescript((ROOT / SQL_FILES['schema']).read_text())
    connection.executemany('INSERT INTO corner_takers VALUES (?, ?, ?)',
                           [(r['match_id'], r['corner_id'], r['passer']) for r in takers])
    connection.commit()


def query_report(connection, min_deliveries=0):
    if type(min_deliveries) is not int or min_deliveries < 0:
        raise ValueError('Minimum deliveries must be a nonnegative integer.')
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(
        (ROOT / SQL_FILES['query']).read_text(), {'min_deliveries': min_deliveries})]


def build_evidence():
    study, profiles = [json.loads((ROOT / p).read_text()) for p in SOURCE_FILES]
    corners, shots = joins.source_tables(study)
    takers = [{k: r[k] for k in ('match_id', 'corner_id', 'passer')}
              for r in profiles['deliveries']]
    with closing(sqlite3.connect(':memory:')) as connection:
        create_database(connection, corners, shots, takers)
        all_takers = query_report(connection)
        filtered = query_report(connection, 10)
    return {
        'sources': [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}
                    for p in SOURCE_FILES],
        'sql_files': {k: {'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}
                      for k, p in SQL_FILES.items()},
        'taker_rows': takers, 'all_takers': all_takers,
        'display_min_deliveries': 10, 'filtered_takers': filtered,
        'scope': 'Descriptive player-name groups in the same five France fixtures. Ten deliveries is an illustrative display filter, not a reliability threshold. Complete corner metadata checked before the inner join. No player ability ranking or independent SQL mastery claimed.'
    }


def render_report(evidence):
    rows = '\n'.join(
        f"- {r['passer']}: {r['corners_with_shot']}/{r['deliveries']} corners with a shot "
        f"({r['corner_shot_rate_pct']:.1f}%); {r['phase_shots']} phase shots, {r['phase_goals']} shot goals."
        for r in evidence['all_takers'])
    names = ', '.join(r['passer'] for r in evidence['filtered_takers'])
    return f'''# France corner-taker SQL report

Question: who delivered France's corners, and how often were those deliveries associated with a shot under our existing phase rule?

{rows}

All four groups sum to 45 deliveries, 19 corners with a shot, 21 phase shots and two shot goals. Goals are phase outcomes, not credited assists. Display order is delivery volume, not a ranking of ability.

## The SQL workflow

The existing corner table identifies deliveries; the new corner_takers table adds one recorded passer name per full match/corner key. The loader rejects missing, duplicate or extra metadata before joining, so the inner metadata join cannot silently drop a corner. Shots are grouped per corner before the left join to preserve the delivery denominator.

GROUP BY passer creates a summary for each name in this sample. HAVING COUNT(*) >= :min_deliveries filters those completed groups. At the illustrative threshold of 10, the displayed names are {names}. All-player results remain saved and visible above. Parameters are bound as values rather than interpolated SQL text.

WHERE filters input rows before grouping; HAVING filters resulting groups. Filtering to shot-positive corners before counting would remove unsuccessful deliveries from the denominator and answer a different question.

## Football interpretation

Bussaglia's 1/1 is 100%, but one attempt does not establish a better taker than Majri's 10/24. Ten is only an example display rule: it is not a statistically justified sample-size threshold, and 24 attempts do not establish stable player ability either. No significance test was run. This descriptive report is not a recommendation to change the taker.

The earlier taker/side analysis found different delivery contexts. This report does not adjust for side, technique, opponent, runners or defenders. Only the existing five France fixtures are included, with the unchanged 15-second same-possession phase rule and its restart/period boundaries. Name labels are used because the saved source provides them; a larger multi-team player database should use stable player IDs rather than assume names are unique.

## Reproduce

Run `python 58_sql_corner_taker_report.py` locally or in Spyder. Read [the SQL](../sql/58_corner_taker_report.sql), [saved evidence](../data/58_sql_corner_taker_evidence.json) and [short lesson](../lessons/0040-sql-corner-taker-report.html). The assignment was completed with assistance; independent query construction remains to demonstrate.

Primary source: [SQLite SELECT, GROUP BY and HAVING](https://www.sqlite.org/lang_select.html). Football source: StatsBomb Open Data through the existing lesson 38 and 39 ledgers.
'''


def main():
    evidence = build_evidence()
    (ROOT / 'data/58_sql_corner_taker_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    (ROOT / 'reports/41_sql_corner_taker_report.md').write_text(render_report(evidence))
    for row in evidence['all_takers']:
        print(f"{row['passer']}: {row['corners_with_shot']}/{row['deliveries']} = {row['corner_shot_rate_pct']:.1f}%")
    print('Display filter: at least 10 deliveries:', ', '.join(r['passer'] for r in evidence['filtered_takers']))


if __name__ == '__main__':
    main()
