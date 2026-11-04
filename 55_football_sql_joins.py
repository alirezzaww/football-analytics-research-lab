"""Lesson 55: join corner/shot tables while preserving the delivery denominator."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parent
SQL_FILES={'schema':'sql/55_schema.sql','preview':'sql/55_join_preview.sql',
           'diagnostic':'sql/55_join_diagnostic.sql','summary':'sql/55_corner_summary.sql'}
CORNER_COLUMNS=('match_id','corner_id','match_date','opponent','period','minute','second')
SHOT_COLUMNS=('match_id','shot_id','corner_id','elapsed_seconds','goal')


def source_tables(study):
    corners=[];shots=[]
    for match in study['matches']:
        for phase in match['phases']:
            corners.append({'match_id':match['fixture']['match_id'],'corner_id':phase['corner_id'],
                'match_date':match['fixture']['match_date'],'opponent':match['opponent'],
                'period':phase['period'],'minute':phase['minute'],'second':phase['second']})
            for shot in phase['shots']:
                shots.append({'match_id':match['fixture']['match_id'],'shot_id':shot['shot_id'],
                    'corner_id':phase['corner_id'],'elapsed_seconds':shot['elapsed_seconds'],'goal':shot['goal']})
    return corners,shots


def create_database(connection,corners,shots):
    connection.execute('PRAGMA foreign_keys = ON')
    assert connection.execute('PRAGMA foreign_keys').fetchone()[0]==1
    connection.executescript((ROOT/SQL_FILES['schema']).read_text())
    connection.executemany('INSERT INTO corners VALUES (?, ?, ?, ?, ?, ?, ?)',
        [tuple(r[k] for k in CORNER_COLUMNS) for r in corners])
    connection.executemany('INSERT INTO phase_shots VALUES (?, ?, ?, ?, ?)',
        [tuple(r[k] for k in SHOT_COLUMNS) for r in shots])
    connection.commit()


def query_results(connection):
    connection.row_factory=sqlite3.Row
    return {name:[dict(r) for r in connection.execute((ROOT/path).read_text())]
            for name,path in SQL_FILES.items() if name!='schema'}


def build_evidence(database_path=None):
    path=ROOT/'data/38_france_corner_study_evidence.json'
    study=json.loads(path.read_text())
    corners,shots=source_tables(study)
    with closing(sqlite3.connect(':memory:')) as con:
        create_database(con,corners,shots)
        queries=query_results(con)
        assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
        if database_path is not None:
            database_path=Path(database_path);database_path.parent.mkdir(parents=True,exist_ok=True)
            with closing(sqlite3.connect(database_path)) as destination:
                con.backup(destination)
    return {'source_path':path.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'sql_files':{name:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for name,p in SQL_FILES.items()},
        'corner_rows':corners,'shot_rows':shots,'queries':queries,
        'generated_database':'data/local/55_corner_relationships.sqlite3',
        'scope':'One-to-many SQL relationship on existing corner phases. LEFT JOIN preserves no-shot corners; joined-row counts are not delivery counts. No new observations or model fitting.'}


def main():
    evidence=build_evidence(ROOT/'data/local/55_corner_relationships.sqlite3')
    (ROOT/'data/55_sql_join_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('Source tables',len(evidence['corner_rows']),'corners',len(evidence['shot_rows']),'shots')
    print('Join diagnostic',evidence['queries']['diagnostic'][0])
    print('Correct corner summary',evidence['queries']['summary'][0])


if __name__=='__main__':
    main()
