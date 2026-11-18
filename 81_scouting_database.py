"""Phase: reusable SQL scouting. Build a local database from the existing 35 profiles.

Run in Spyder, or: python 81_scouting_database.py --side right_only --min-starts 3
The CLI query is exploratory; saved canonical evidence always uses the original pool.
"""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
SOURCES = {'profiles': 'data/71_fullback_percentile_evidence.json',
           'forward': 'data/66_fullback_advancement_evidence.json',
           'pressure': 'data/73_fullback_pressure_activity_evidence.json'}
SQL_FILES = {'schema': 'sql/81_scouting_schema.sql', 'role_activity': 'sql/81_role_activity.sql'}
COLUMNS = ('competition_id','season_id','team_id','player_id','team_name','player_name',
           'side_group','role_starts','duration_ms','completed_passes','attempted_passes',
           'team_completed_passes','forward_passes','recorded_pressures')
DATABASE = 'data/local/81_scouting.sqlite3'
READING = 'https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html'


def profile_rows(data):
    tables = {}
    for name, source in data.items():
        if (source['competition_id'],source['season_id'],source['season']) != (72,30,'2019'):
            raise ValueError('Source competition or season differs')
        table = {(p['team_id'],p['player_id']): p for p in source['players']}
        if len(table) != len(source['players']):
            raise ValueError('Duplicate source player/team identity')
        tables[name] = table
    expected = set(tables['profiles'])
    if any(set(table) != expected for table in tables.values()):
        raise ValueError('Source cohorts differ')
    rows = []
    for key in sorted(expected):
        p = tables['profiles'][key]; f = tables['forward'][key]; d = tables['pressure'][key]
        if any(any(other[k] != p[k] for k in ('duration_ms','qualifying_match_ids')) for other in (f,d)):
            raise ValueError('Source exposure or fixture scope differs')
        if d['role_starts'] != p['role_starts']:
            raise ValueError('Pressure-source qualifying start count differs')
        if f['eligible_completed'] != p['eligible_completed']:
            raise ValueError('Forward-pass source completion count differs')
        fixtures = p['qualifying_match_ids']
        if len(fixtures) != len(set(fixtures)) or len(fixtures) != p['role_starts']:
            raise ValueError('Qualifying fixture membership differs from starts')
        rows.append({'competition_id':72,'season_id':30,'team_id':key[0],'player_id':key[1],
                     'team_name':p['team_name'],'player_name':p['player_name'],
                     'side_group':p['starting_side_group'],'role_starts':p['role_starts'],
                     'duration_ms':p['duration_ms'],'completed_passes':p['eligible_completed'],
                     'attempted_passes':p['eligible_attempts'],'team_completed_passes':p['team_completed_while_registered'],
                     'forward_passes':f['qualifying_completions'],'recorded_pressures':d['recorded_pressures'],
                     'qualifying_match_ids':fixtures})
    return rows


def create_database(connection, rows):
    connection.executescript((ROOT/SQL_FILES['schema']).read_text())
    with connection:
        connection.executemany('INSERT INTO fullbacks VALUES ('+','.join('?' for _ in COLUMNS)+')',
                               [tuple(row[k] for k in COLUMNS) for row in rows])
        connection.executemany('INSERT INTO qualifying_fixtures VALUES (?,?,?,?,?)',
                               [(r['competition_id'],r['season_id'],r['team_id'],r['player_id'],m)
                                for r in rows for m in r['qualifying_match_ids']])


def query_players(connection, side_group=None, min_starts=3):
    if side_group not in (None,'left_only','right_only','mixed') or type(min_starts) is not int or min_starts < 3:
        raise ValueError('Use a valid side and integer minimum of at least the original three starts')
    connection.row_factory = sqlite3.Row
    return [dict(r) for r in connection.execute((ROOT/SQL_FILES['role_activity']).read_text(),
                                              {'side_group':side_group,'min_starts':min_starts})]


def build_evidence(database_path=None):
    data = {k:json.loads((ROOT/p).read_text()) for k,p in SOURCES.items()}
    rows = profile_rows(data)
    with closing(sqlite3.connect(':memory:')) as connection:
        create_database(connection,rows)
        queries = {'all':query_players(connection)}
        queries.update({side:query_players(connection,side) for side in ('left_only','right_only','mixed')})
        if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or connection.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Database integrity check failed')
        counts = {name:connection.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in ('fullbacks','qualifying_fixtures')}
        if database_path is not None:
            destination = Path(database_path); destination.parent.mkdir(parents=True,exist_ok=True)
            with closing(sqlite3.connect(destination)) as target:
                connection.backup(target)
    return {'competition':'FIFA Women’s World Cup','season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3','section':'Case study: spreadsheet scouting','url':READING},
            'source_files':{k:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k,p in SOURCES.items()},
            'sql_files':{k:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k,p in SQL_FILES.items()},
            'rows':rows,'queries':queries,'table_counts':counts,'generated_database':DATABASE,
            'row_definition':'fullbacks: one competition/season/team/player profile. qualifying_fixtures: one included player-fixture membership, not a unique tournament fixture or an additional player.',
            'rate_definition':'Rates are calculated in SQL from unchanged counts and registered milliseconds: count*5,400,000/duration_ms. Percentage denominators use NULLIF for missing exposure. No mean of match rates.',
            'query_definition':'Filter side/minimum starts first; DENSE_RANK passing activity within each returned side group on unrounded values. Equal values share rank; next distinct value gets the next rank. Final display ties are ordered by names and IDs without changing rank.',
            'scope':'Historical activity exploration, not ability ranking or a transfer shortlist. Original 35-player cohort; lowering eligibility to include omitted players is not supported. Exclusive side means qualifying fullback starts only, not entire career/appearance position. Four mixed-side profiles remain a separate group. No new data, metric training or validation.'}


def render_report(evidence):
    examples = []
    for pid in (10178,15249):
        p = next(r for r in evidence['queries']['all'] if r['player_id'] == pid)
        examples.append(f"- **{p['player_name']}**: {p['side_group']}; {p['completed_per90']:.2f} completed passes/90; passing-activity rank {p['passing_activity_rank']} in {p['eligible_peers']} eligible profiles in that side group.")
    groups = '\n'.join(f"- {side}: {len(evidence['queries'][side])} profiles." for side in ('left_only','right_only','mixed'))
    return f'''# A reusable SQL scouting database

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Case study: spreadsheet scouting]({READING}); SQL reference: [SQLite window functions](https://www.sqlite.org/windowfunctions.html).
This is our custom SQL extension, not a SQL exercise copied from Soccermatics.

## What was built

The existing passing, fixed forward-pass and recorded pressure counts now share a local SQLite database with {evidence['table_counts']['fullbacks']} player profiles and {evidence['table_counts']['qualifying_fixtures']} qualifying player–fixture memberships. The second count is not 145 distinct matches or players. Stable compound IDs prevent duplicate profiles; the fixture table links to its parent using foreign keys. The generated database is ignored by Git; source SQL, rebuilding code and evidence are public.

{groups}

## First queries

{chr(10).join(examples)}

Ranks sort passing activity, not player quality. All original values and selected fixtures remain unchanged. No composite score or validated recruitment criterion is introduced.

## New SQL concept: rank within a group

```sql
DENSE_RANK() OVER (
    PARTITION BY side_group
    ORDER BY completed_per90 DESC
)
```

PARTITION BY gives each side group its own comparison. DENSE_RANK gives tied values equal ranks: 10,10,8 → ranks1,1,2. Unlike GROUP BY, it keeps each player's row. The activity rate is calculated from full precision counts/time; display rounding does not create ties.

The query's eligible CTE applies role/minimum-start filters before ranking, so ranks and peer counts refer to that returned eligible pool. Mixed-side players are kept separate rather than silently assigned to left/right. Original cohort membership was at least three qualifying starts; raising the query minimum narrows this existing pool, while omitted players cannot be recovered by lowering a SQL filter. A rank of1 means highest measured passing activity in the eligible side pool, not best fullback.

## Run locally

In Spyder, run `81_scouting_database.py`. Or from the project directory:

```sh
python 81_scouting_database.py --side right_only --min-starts 3
python 81_scouting_database.py --side left_only --min-starts 4
```

The generated database is `data/local/81_scouting.sqlite3`. The script always rebuilds canonical three-start evidence; the CLI then prints your exploratory filtered query without rewriting the original cohort results. Values are bound as SQL parameters. No app installation or browser notebook is required; sqlite3 is included with Python.

## Evidence and limits

{evidence['row_definition']}

{evidence['rate_definition']}

Per90 normalizes registered time, not possession, difficulty or time strictly in the fullback position. The forward rule remains end_x−start_x≥20 coordinate units; Pressure counts describe provider-recorded starts, not successful defending. A single-metric order is an inspection starting point; compare football roles and further evidence before making judgements.

[Saved rows, source/SQL hashes and query results](../data/81_scouting_database_evidence.json) · [Schema](../sql/81_scouting_schema.sql) · [Parameterized query](../sql/81_role_activity.sql) · [Lesson](../lessons/0063-scouting-database.html).
Assisted implementation; independent SQL construction and explanation remain to demonstrate.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--side',choices=('all','left_only','right_only','mixed'),default='all')
    parser.add_argument('--min-starts',type=int,default=3)
    args = parser.parse_args()
    if args.min_starts < 3:
        parser.error('Minimum starts must be at least the original three-start cohort rule')
    evidence = build_evidence(ROOT/DATABASE)
    (ROOT/'data/81_scouting_database_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/64_scouting_database.md').write_text(render_report(evidence))
    with closing(sqlite3.connect(ROOT/DATABASE)) as connection:
        rows = query_players(connection,None if args.side == 'all' else args.side,args.min_starts)
    print('Database:',ROOT/DATABASE)
    print('Selected',len(rows),'profiles. Rank orders passing activity within each eligible side group.')
    for p in rows:
        print(p['side_group'],p['passing_activity_rank'],p['player_name'],f"{p['completed_per90']:.2f} completions/90",'peers',p['eligible_peers'])


if __name__ == '__main__':
    main()
