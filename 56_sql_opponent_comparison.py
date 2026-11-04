"""Lesson 56: reproduce opponent corner rates with join-safe GROUP BY."""
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
QUERY = ROOT / 'sql/56_opponent_corner_rates.sql'
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
        'scope': 'Existing five France fixtures; 15-second same-possession corner phases. Descriptive opponent groups, not opponent strength estimates. Assisted SQL exercise.'
    }


def main():
    evidence = build_evidence()
    (ROOT / 'data/56_sql_opponent_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    for row in evidence['rows']:
        print(f"{row['opponent']}: {row['corners_with_shot']}/{row['deliveries']} corners with a shot = {row['corner_shot_rate_pct']:.1f}% ({row['phase_shots']} shots)")


if __name__ == '__main__':
    main()
