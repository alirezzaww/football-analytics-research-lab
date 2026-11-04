"""Lesson 57: label recorded periods and compare corner rates with SQL CASE."""
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
QUERY = ROOT / 'sql/57_corner_half_rates.sql'
SPEC = importlib.util.spec_from_file_location('joins55', ROOT / '55_football_sql_joins.py')
joins = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(joins)


def query_rates(connection):
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(QUERY.read_text())]


def build_evidence():
    source = ROOT / 'data/38_france_corner_study_evidence.json'
    corners, shots = joins.source_tables(json.loads(source.read_text()))
    with closing(sqlite3.connect(':memory:')) as connection:
        joins.create_database(connection, corners, shots)
        rows = query_rates(connection)
    return {
        'source_path': source.relative_to(ROOT).as_posix(),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'query_path': QUERY.relative_to(ROOT).as_posix(),
        'query_sha256': hashlib.sha256(QUERY.read_bytes()).hexdigest(),
        'rows': rows,
        'scope': 'Existing France five-match corner sample; periods 1 and 2 separate, periods 3 and 4 pooled as extra time. Empty groups are absent, not zero-rate rows. Assisted descriptive SQL exercise; no causal or significance claim.'
    }


def render_report(evidence):
    results = '\n'.join(
        f"- {r['match_phase']}: {r['corners_with_shot']}/{r['deliveries']} corners with a shot "
        f"({r['corner_shot_rate_pct']:.1f}%); {r['phase_shots']} phase shots."
        for r in evidence['rows'])
    return f'''# France corner rates by match phase

SQL CASE labels each delivery using its recorded period, then GROUP BY pools corners with the same label across the existing five France fixtures.

{results}

The second-half observed rate is slightly higher, but the first half produced more phase shots. These are different measures. The counts sum to 45 deliveries, 19 corners with a shot and 21 shots, matching the original study.

## Definition and interpretation

- Period 1 means first half, including its added time. A period-1 corner at minute 46 is not a second-half corner.
- Period 2 means second half, including added time. Periods 3 and 4 are pooled as extra time.
- The source schema permits only periods 1–4, so the CASE ELSE branch contains only extra time. The query would need revisiting for a different schema including shootouts.
- Extra time contains only three corners from the Brazil match, not five matches of comparable exposure. It is kept separate.
- Rates describe the fraction of corners associated with a shot, not corners or shots per minute. Phase lengths and game context differ.
- A small descriptive difference does not establish improvement after half-time, a coach effect, or a statistically reliable difference. No significance test was run.
- Groups with no deliveries are absent from the query result; absence is not a measured 0% rate.

The existing 15-second same-possession phase rule and restart/period boundaries remain unchanged. All corners, including zero-shot corners, remain in their group's denominator. Shots are summarized by full match/corner key before the join.

## Reproduce and learn

Run `python 57_sql_match_phase_comparison.py` in the local environment or Spyder. Read [the query](../sql/57_corner_half_rates.sql), [saved evidence](../data/57_sql_match_phase_evidence.json) and [short lesson](../lessons/0039-sql-match-phase-comparison.html).

This is an assisted assignment. Independently explaining and modifying the query remains to demonstrate. Primary source: [SQLite CASE expressions](https://www.sqlite.org/lang_expr.html#the_case_expression).
'''


def main():
    evidence = build_evidence()
    (ROOT / 'data/57_sql_match_phase_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    (ROOT / 'reports/40_sql_match_phase_comparison.md').write_text(render_report(evidence))
    for row in evidence['rows']:
        print(f"{row['match_phase']}: {row['corners_with_shot']}/{row['deliveries']} = {row['corner_shot_rate_pct']:.1f}% ({row['phase_shots']} shots)")


if __name__ == '__main__':
    main()
