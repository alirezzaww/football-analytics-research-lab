"""Lesson 54: query audited football records with SQLite and Python.

One database row is one France corner delivery, including those without shots.
Rebuilds only the generated lesson database; no raw downloads or fitting.
"""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
SQL_FILES = {'schema':'sql/54_schema.sql', 'overall':'sql/54_overall.sql',
             'by_opponent':'sql/54_by_opponent.sql','extra_time':'sql/54_extra_time.sql','sample':'sql/54_sample.sql'}
COLUMNS = ('match_id','corner_id','match_date','opponent','period','minute','second','phase_shots','phase_goals','has_phase_shot')


def corner_rows(study):
    rows=[]
    for match in study['matches']:
        for phase in match['phases']:
            rows.append({'match_id':match['fixture']['match_id'],'corner_id':phase['corner_id'],
                         'match_date':match['fixture']['match_date'],'opponent':match['opponent'],
                         'period':phase['period'],'minute':phase['minute'],'second':phase['second'],
                         'phase_shots':len(phase['shots']),'phase_goals':sum(r['goal'] for r in phase['shots']),
                         'has_phase_shot':int(bool(phase['shots']))})
    return rows


def create_database(connection, rows):
    connection.executescript((ROOT/SQL_FILES['schema']).read_text())
    # Bind values as parameters, preserving apostrophes without SQL interpolation.
    connection.executemany('INSERT INTO corners VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           [tuple(row[k] for k in COLUMNS) for row in rows])
    connection.commit()


def query_results(connection):
    connection.row_factory=sqlite3.Row
    return {name:[dict(r) for r in connection.execute((ROOT/path).read_text()).fetchall()]
            for name,path in SQL_FILES.items() if name!='schema'}


def build_evidence(database_path=None):
    path=ROOT/'data/38_france_corner_study_evidence.json'
    study=json.loads(path.read_text())
    rows=corner_rows(study)
    with closing(sqlite3.connect(':memory:')) as connection:
        create_database(connection,rows)
        results=query_results(connection)
        assert connection.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        if database_path is not None:
            database_path=Path(database_path)
            database_path.parent.mkdir(parents=True,exist_ok=True)
            # This path is a disposable generated artifact, rebuilt on each run.
            with closing(sqlite3.connect(database_path)) as destination:
                connection.backup(destination)
    return {'source_path':path.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'sql_files':{name:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for name,p in SQL_FILES.items()},
            'row_definition':'One row per recorded France corner delivery; includes incomplete and no-shot deliveries. Existing phase rules unchanged.',
            'rows':rows,'queries':results,
            'generated_database':'data/local/54_corners.sqlite3',
            'scope':'SQL reproduces existing audited counts; it does not add observations, fit a model or establish independent SQL proficiency.'}


def main():
    evidence=build_evidence(ROOT/'data/local/54_corners.sqlite3')
    (ROOT/'data/54_first_sql_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('Overall',evidence['queries']['overall'][0])
    for row in evidence['queries']['by_opponent']:
        print(row['opponent'],row['deliveries'],row['corners_with_shot'])
    print('Extra-time deliveries',len(evidence['queries']['extra_time']))
    print('Generated database:',evidence['generated_database'])


if __name__=='__main__':
    main()
