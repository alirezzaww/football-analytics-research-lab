"""Lesson 59: audit structured corner records before the player-report join."""
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
SOURCE_FILES = ['data/38_france_corner_study_evidence.json',
                'data/39_corner_delivery_profiles_evidence.json']
SQL_FILES = {'schema': 'sql/59_staging_schema.sql',
             'checks': 'sql/59_corner_relationship_audit.sql'}
SPEC = importlib.util.spec_from_file_location('joins55', ROOT/'55_football_sql_joins.py')
joins = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(joins)


def audit_records(corners, shots, takers):
    """Inspect the expected list-of-dictionaries format without repairing records."""
    with closing(sqlite3.connect(':memory:')) as connection:
        connection.executescript((ROOT/SQL_FILES['schema']).read_text())
        for table, rows, fields in (
            ('staging_corners', corners, ('match_id','corner_id')),
            ('staging_shots', shots, ('match_id','shot_id','corner_id')),
            ('staging_takers', takers, ('match_id','corner_id','passer')),
        ):
            placeholders = ','.join('?' for _ in fields)
            connection.executemany(f'INSERT INTO {table} VALUES ({placeholders})',
                                   [tuple(row.get(field) for field in fields) for row in rows])
        connection.row_factory = sqlite3.Row
        checks = [dict(row) for row in connection.execute((ROOT/SQL_FILES['checks']).read_text())]
    for check in checks:
        check['passed'] = check['violation_count'] == 0
    return checks


def require_valid_relationships(corners, shots, takers):
    checks = audit_records(corners, shots, takers)
    failed = [r['check_name'] for r in checks if not r['passed']]
    if failed:
        raise ValueError('Corner relationship audit failed: ' + ', '.join(failed))
    return checks


def build_evidence():
    study, profiles = [json.loads((ROOT/p).read_text()) for p in SOURCE_FILES]
    corners, shots = joins.source_tables(study)
    takers = profiles['deliveries']
    checks = audit_records(corners, shots, takers)
    return {
        'sources': [{'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}
                    for p in SOURCE_FILES],
        'sql_files': {k: {'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()}
                      for k,p in SQL_FILES.items()},
        'input_counts': {'corners': len(corners), 'shots': len(shots), 'taker_records': len(takers)},
        'checks': checks, 'passed': all(r['passed'] for r in checks),
        'scope': 'Nine structural checks on existing structured source ledgers. No automatic deletion or repair. Does not verify real-world event accuracy, raw-event completeness, all field types, timing, phase definitions or football conclusions.'
    }


def render_report(evidence):
    results = '\n'.join(f"- {r['check_name']}: {r['violation_count']} violations; "
                        f"{'PASS' if r['passed'] else 'FAIL'}." for r in evidence['checks'])
    counts = evidence['input_counts']
    return f'''# Corner data relationship audit

Inputs: {counts['corners']} corner records, {counts['shots']} phase-shot records and {counts['taker_records']} taker records from the existing five-match France study.

{results}

Overall structural audit: **{'PASS' if evidence['passed'] else 'FAIL'}**.

## Why this matters

A duplicate positive corner could change a rate from 1/2 to 2/3. An inner join could silently remove a corner with missing taker metadata. A shot linked to the wrong match/corner key could be lost or assigned incorrectly. We inspect incoming records before putting them into the reporting database.

Temporary staging tables allow problematic records to be counted instead of failing at the first insertion. The final reporting tables retain their strict keys and foreign-key constraints. Full identities use match ID plus corner ID, or match ID plus shot ID. A missing taker is an error under this report's complete-metadata requirement; a corner without a shot is valid and must remain in the denominator.

The duplicate checks count key groups appearing more than once; relationship/name checks count affected records. These violation counts have different meanings and must not be added into a count of unique bad events. One record can fail several checks. An empty corner input fails, rather than receiving an all-clear result.

## How the audit is used

Run `python 59_corner_data_quality.py` in Spyder or the local environment. It saves the audit evidence and report, then exits unsuccessfully if any check fails. The lesson 58 player-report loader calls the same validation before loading records; the research runner executes this audit before lesson 58. No records are automatically dropped or repaired.

The nine checks pass on our current records. That does not prove the provider annotated every action correctly or that all real corners were captured. It also does not validate every field type, event timing, model assumption or tactical conclusion. Previous evidence checks cover additional source hashes and phase logic. This is a focused relationship audit, not a universal data-quality certificate.

## Learn and reproduce

[Short lesson](../lessons/0041-corner-data-quality.html) · [SQL checks](../sql/59_corner_relationship_audit.sql) · [Saved evidence](../data/59_corner_data_quality_evidence.json).

Worked assignment completed with assistance. Tests deliberately introduce synthetic defects into tiny examples; no corruption was found or introduced into the actual source data.

Primary reference: [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html), which enforce the existence of related parent records. The audit additionally checks the report-specific requirement that every corner has taker metadata.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/59_corner_data_quality_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/42_corner_data_quality.md').write_text(render_report(evidence))
    print('Input records:', evidence['input_counts'])
    for check in evidence['checks']:
        print(check['check_name'], check['violation_count'], 'PASS' if check['passed'] else 'FAIL')
    if not evidence['passed']:
        raise SystemExit('Audit failed. Investigate the records before creating the player report.')


if __name__ == '__main__':
    main()
