"""Lesson 84: trace shortlisted player averages to reconciled player-match rows."""
import argparse
from contextlib import closing
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parent
SOURCES={'database':'data/81_scouting_database_evidence.json','screen':'data/82_scouting_role_screen_evidence.json',
         'minutes':'data/64_fullback_playing_time_evidence.json','passing':'data/70_fullback_team_passing_share_evidence.json',
         'forward':'data/66_fullback_advancement_evidence.json','pressure':'data/73_fullback_pressure_activity_evidence.json',
         'lineups':'data/63_fullback_cohort_evidence.json'}
SQL_FILES={'schema':'sql/84_match_activity_schema.sql','matches':'sql/84_player_matches.sql','totals':'sql/84_player_totals.sql'}
COLUMNS=('competition_id','season_id','team_id','player_id','match_id','match_date','opponent',
         'duration_ms','completed_passes','forward_passes','recorded_pressures')
DATABASE='data/local/84_scouting_drilldown.sqlite3'
READING='https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html'
spec=importlib.util.spec_from_file_location('database81',ROOT/'81_scouting_database.py')
database=importlib.util.module_from_spec(spec);spec.loader.exec_module(database)


def match_key(row):return row['match_id'],row['team_id'],row['player_id']


def unique_windows(rows):
    table={match_key(r):r for r in rows}
    if len(table)!=len(rows):raise ValueError('Duplicate player-match window')
    return table


def assemble_rows(data):
    profiles=data['database']['rows']
    expected={(m,p['team_id'],p['player_id']) for p in profiles for m in p['qualifying_match_ids']}
    passing=unique_windows(data['passing']['windows']);pressures=unique_windows(data['pressure']['windows'])
    if set(passing)!=expected or set(pressures)!=expected:raise ValueError('Match membership differs across ledgers')
    intervals={}
    for audit in data['minutes']['match_audits']:
        for interval in audit['intervals']:
            key=(audit['match_id'],interval['team_id'],interval['player_id'])
            if key in expected:
                if key in intervals:raise ValueError('Duplicate registered interval')
                intervals[key]=interval
    if set(intervals)!=expected:raise ValueError('Registered intervals do not cover expected fixtures')
    completions={key:[] for key in expected}
    seen=set()
    for row in data['forward']['completions']:
        key=match_key(row);event_key=(row['match_id'],row['pass_id'])
        if key not in expected or event_key in seen:raise ValueError('Forward ledger has unexpected or duplicate completion')
        seen.add(event_key);completions[key].append(row)
    teams={};dates={}
    for row in data['lineups']['starter_rows']:
        match=row['match_id'];teams.setdefault(match,{})
        if row['team_id'] in teams[match] and teams[match][row['team_id']]!=row['team_name']:raise ValueError('Inconsistent team label')
        teams[match][row['team_id']]=row['team_name']
        if match in dates and dates[match]!=row['match_date']:raise ValueError('Inconsistent fixture date')
        dates[match]=row['match_date']
    output=[]
    for key in sorted(expected):
        mid,tid,pid=key;p=passing[key];d=pressures[key];interval=intervals[key]
        if any(w['start_ms']!=interval['start_ms'] or w['end_ms']!=interval['end_ms'] for w in (p,d)):
            raise ValueError('Action windows differ from registered exposure')
        completed=p['player_completed_ids'];forward=completions[key];pressure_ids=d['pressure_ids']
        if len(completed)!=len(set(completed)) or {r['pass_id'] for r in forward}!=set(completed):
            raise ValueError('Forward ledger does not cover exactly the completed passes')
        if len(pressure_ids)!=len(set(pressure_ids)):raise ValueError('Duplicate pressure within player-match')
        opponents=[name for identifier,name in teams[mid].items() if identifier!=tid]
        if tid not in teams[mid] or len(opponents)!=1:raise ValueError('Fixture must identify two teams')
        forward_ids=[r['pass_id'] for r in forward if r['qualifies']]
        output.append({'competition_id':72,'season_id':30,'team_id':tid,'player_id':pid,'match_id':mid,
                       'match_date':dates[mid],'opponent':opponents[0],'duration_ms':interval['end_ms']-interval['start_ms'],
                       'completed_passes':len(completed),'forward_passes':len(forward_ids),'recorded_pressures':len(pressure_ids),
                       'completed_pass_ids':completed,'forward_pass_ids':forward_ids,'pressure_ids':pressure_ids})
    return output


def create_match_table(connection,rows):
    connection.executescript((ROOT/SQL_FILES['schema']).read_text())
    with connection:
        connection.executemany('INSERT INTO match_activity VALUES ('+','.join('?' for _ in COLUMNS)+')',
                               [tuple(r[k] for k in COLUMNS) for r in rows])


def query_matches(connection,team_id,player_id):
    if any(type(v) is not int or v<=0 for v in (team_id,player_id)):raise ValueError('Positive integer player/team IDs required')
    connection.row_factory=sqlite3.Row
    return [dict(r) for r in connection.execute((ROOT/SQL_FILES['matches']).read_text(),{'team_id':team_id,'player_id':player_id})]


def query_totals(connection):
    connection.row_factory=sqlite3.Row
    return [dict(r) for r in connection.execute((ROOT/SQL_FILES['totals']).read_text())]


def reconcile(profiles,totals):
    expected={(p['team_id'],p['player_id']):p for p in profiles}
    actual={(p['team_id'],p['player_id']):p for p in totals}
    if len(expected)!=len(profiles) or len(actual)!=len(totals) or set(expected)!=set(actual):raise ValueError('Aggregated profile coverage differs')
    for key,p in expected.items():
        total=actual[key]
        if total['qualifying_matches']!=len(p['qualifying_match_ids']):raise ValueError('Match count differs')
        for field in ('duration_ms','completed_passes','forward_passes','recorded_pressures'):
            if total[field]!=p[field]:raise ValueError('Match rows do not reconcile: '+field)


def build_evidence(database_path=None):
    data={k:json.loads((ROOT/path).read_text()) for k,path in SOURCES.items()}
    for record in data['database']['sql_files'].values():
        if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Base database SQL changed')
    rows=assemble_rows(data)
    with closing(sqlite3.connect(':memory:')) as connection:
        database.create_database(connection,data['database']['rows']);create_match_table(connection,rows)
        totals=query_totals(connection);reconcile(data['database']['rows'],totals)
        focus=[]
        for selected in data['screen']['selected_rows']:
            matches=query_matches(connection,selected['team_id'],selected['player_id'])
            total=next(t for t in totals if (t['team_id'],t['player_id'])==(selected['team_id'],selected['player_id']))
            if not math.isclose(total['forward_per90'],selected['forward_per90']):raise ValueError('Screen and match aggregation differ')
            focus.append({'team_id':selected['team_id'],'player_id':selected['player_id'],'player_name':selected['player_name'],
                          'team_name':selected['team_name'],'matches':matches,'totals':total})
        if connection.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Match database foreign key failure')
        if database_path is not None:
            target=Path(database_path);target.parent.mkdir(parents=True,exist_ok=True)
            with closing(sqlite3.connect(target)) as destination:connection.backup(destination)
    return {'competition':'FIFA Women’s World Cup','season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3','section':'Case study: spreadsheet scouting','url':READING},
            'source_files':{k:{'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for k,path in SOURCES.items()},
            'sql_files':{k:{'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for k,path in SQL_FILES.items()},
            'rows':rows,'all_player_totals':totals,'focused_profiles':focus,'generated_database':DATABASE,
            'row_definition':'One player/team/qualifying fixture for competition 72 season 30. Count/action ledgers and registered intervals are matched before SQL insertion; no raw pass-pressure join that could multiply rows.',
            'scope':'Same historical cohort and shortlist. Match variation is descriptive, not future form, causal opponent effects, confidence intervals or an ability/consistency ranking. Later role changes and the original registered-time convention remain included. No footage reviewed.'}


def render_report(evidence):
    sections=[]
    for p in evidence['focused_profiles']:
        t=p['totals']
        matches='\n'.join(f"- {r['match_date']} vs {r['opponent']}: {r['forward_passes']} fixed-rule forward completions in {r['registered_minutes']:.2f} registered minutes = **{r['forward_per90']:.2f}/90**; {r['completed_passes']} eligible completions; {r['recorded_pressures']} pressures. Match {r['match_id']}." for r in p['matches'])
        sections.append(f"## {p['player_name']} — {p['team_name']}\n\nPooled rate: {t['forward_passes']} forward completions / {t['duration_ms']/60000:.6f} minutes ×90 = **{t['forward_per90']:.4f}/90** across {t['qualifying_matches']} included fixtures. Observed match rates span {t['observed_min_match_forward_per90']:.2f}–{t['observed_max_match_forward_per90']:.2f}/90. An equally weighted mean of match rates is {t['unweighted_mean_match_forward_per90']:.4f}/90; that answers a different weighting question.\n\n{matches}")
    return f'''# Look behind the shortlisted player averages

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Case study: spreadsheet scouting]({READING}); SQL: [SQLite SUM and AVG](https://www.sqlite.org/lang_aggfunc.html). Custom guided tool extension.

The original four-profile shortlist now has a match drill-down. The database contains {len(evidence['rows'])} player–match activity rows for all 35 profiles. Every player's match counts and registered milliseconds reconcile exactly to the existing profile. Source event IDs remain in the saved evidence.

{chr(10).join(sections)}

## Read the averages correctly

A pooled per90 rate describes all selected playing time together. It does not imply the same activity in every game. Calculate total actions / total minutes ×90; averaging match rates gives each match equal weight even if the player played different durations. A short registered interval can produce a high rate from few actions. The min–max range above describes only the included matches; it is not a confidence interval or a forecast.

The database has one row per player–fixture, joined to one parent player profile with the full compound key. Pass, forward-pass and pressure counts are assembled at this grain before joining; joining raw event tables could multiply counts. The existing qualifying_fixtures table supplies the foreign-key membership check. Both source fixture membership and clock-window coverage are verified.

This view identifies matches worth inspecting, not why a rate differed. Opponent strength, score state, possession, instructions, role changes and opportunities are not adjusted here. A high or low match value alone is not a performance judgement. No new shortlist, model, player-quality grade or footage observation is introduced.

## Run locally

Run `python 84_scouting_match_drilldown.py` in Spyder to rebuild the local database and report. Or use `python 84_scouting_match_drilldown.py --team-id 865 --player-id 10178` from the project directory to print Bronze's included matches. The original database stays unchanged; this extension is saved at `{DATABASE}` and ignored by Git.

[Match rows, event IDs and source hashes](../data/84_scouting_match_drilldown_evidence.json) · [Schema](../sql/84_match_activity_schema.sql) · [Player query](../sql/84_player_matches.sql) · [Totals query](../sql/84_player_totals.sql) · [Lesson](../lessons/0066-scouting-match-drilldown.html).
Assisted implementation; independent query construction and interpretation remain to demonstrate.
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--team-id',type=int);parser.add_argument('--player-id',type=int);args=parser.parse_args()
    if (args.team_id is None)!=(args.player_id is None):parser.error('Supply both team-id and player-id')
    if args.team_id is not None and min(args.team_id,args.player_id)<=0:parser.error('IDs must be positive')
    evidence=build_evidence(ROOT/DATABASE)
    (ROOT/'data/84_scouting_match_drilldown_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/67_scouting_match_drilldown.md').write_text(render_report(evidence))
    if args.team_id is not None:
        with closing(sqlite3.connect(ROOT/DATABASE)) as connection:
            matches=query_matches(connection,args.team_id,args.player_id)
            if not matches:print('No qualifying player-match rows for those IDs.')
            for row in matches:print(row)
    else:
        for p in evidence['focused_profiles']:
            t=p['totals'];print(p['player_name'],t['qualifying_matches'],'matches;',round(t['forward_per90'],4),'pooled/90; match range',round(t['observed_min_match_forward_per90'],2),round(t['observed_max_match_forward_per90'],2))


if __name__=='__main__':main()
