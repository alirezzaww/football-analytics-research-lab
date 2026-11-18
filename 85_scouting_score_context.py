"""Lesson 85: matched action/time rates while leading, drawing or trailing."""
from bisect import bisect_left
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parent
SOURCES={'drilldown':'data/84_scouting_match_drilldown_evidence.json',
         'minutes':'data/64_fullback_playing_time_evidence.json',
         'lineups':'data/63_fullback_cohort_evidence.json'}
PROTOCOL='data/85_score_state_protocol.json'
SQL_FILES={'schema':'sql/85_score_state_schema.sql','rates':'sql/85_score_state_rates.sql'}
COLUMNS=('competition_id','season_id','team_id','player_id','match_id','score_state','duration_ms',
         'completed_passes','forward_passes','recorded_pressures')
DATABASE='data/local/85_scouting_score_context.sqlite3'
READING='https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


drill=module('drill84','84_scouting_match_drilldown.py')
pressure=module('pressure73','73_fullback_pressure_activity.py')
scoring=module('scoring22','22_score_state_context.py')
STATES=scoring.STATES


def goal_timeline(events,audit,fixture):
    lookup={e['id']:e for e in events}
    if len(lookup)!=len(events) or len({e['index'] for e in events})!=len(events):raise ValueError('Duplicate raw event ID or index')
    home=fixture['home_team']['home_team_id'];away=fixture['away_team']['away_team_id']
    _,goals,final=scoring.annotate_match(events,[],home,away)
    if final!=[fixture['home_score'],fixture['away_score']]:raise ValueError('Goal reconstruction differs from metadata')
    offsets={p['period']:sum(q['length_ms'] for q in audit['periods'] if q['period']<p['period']) for p in audit['periods']}
    lengths={p['period']:p['length_ms'] for p in audit['periods']}
    timeline=[]
    for goal in goals:
        event=lookup[goal['id']];stamp=pressure.time_module.cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])
        if event['period'] not in offsets or not 0<=stamp<=lengths[event['period']]:raise ValueError('Goal outside recorded playing periods')
        when=offsets[event['period']]+stamp
        if timeline and when<timeline[-1]['elapsed_ms']:raise ValueError('Goal clock and event order disagree')
        timeline.append({**goal,'period':event['period'],'timestamp':event['timestamp'],'elapsed_ms':when})
    return home,away,timeline,final


def state(scores,team,home,away):
    if team not in (home,away):raise ValueError('Player team outside fixture')
    return scoring.score_state(scores[0],scores[1]) if team==home else scoring.score_state(scores[1],scores[0])


def state_durations(goals,start,end,team,home,away):
    if type(start) is not int or type(end) is not int or not 0<=start<end:raise ValueError('Invalid registered interval')
    result={label:0 for label in STATES};cursor=0;scores=[0,0]
    for goal in goals:
        boundary=goal['elapsed_ms']
        overlap=max(0,min(end,boundary)-max(start,cursor))
        result[state(scores,team,home,away)]+=overlap
        scores=goal['score_after'];cursor=boundary
    result[state(scores,team,home,away)]+=max(0,end-max(start,cursor))
    if sum(result.values())!=end-start:raise ValueError('Score-state time does not reconcile')
    return result


def event_state(goals,index,team,home,away):
    position=bisect_left([g['index'] for g in goals],index)
    scores=goals[position-1]['score_after'] if position else [0,0]
    return state(scores,team,home,away)


def split_match_row(row,interval,events,goals,home,away,periods):
    lookup={e['id']:e for e in events}
    exposure=state_durations(goals,interval['start_ms'],interval['end_ms'],row['team_id'],home,away)
    output={label:{**{k:row[k] for k in ('competition_id','season_id','team_id','player_id','match_id')},
                   'score_state':label,'duration_ms':exposure[label],
                   'completed_pass_ids':[],'forward_pass_ids':[],'pressure_ids':[]} for label in STATES}
    if not set(row['forward_pass_ids'])<=set(row['completed_pass_ids']):raise ValueError('Forward actions are not completed-pass subset')
    offsets={p['period']:sum(q['length_ms'] for q in periods if q['period']<p['period']) for p in periods}
    begin_index=lookup[interval['start_event_id']]['index'];end_index=lookup[interval['end_event_id']]['index']
    for field,kind in (('completed_pass_ids','Pass'),('pressure_ids','Pressure')):
        ids=row[field]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate selected action ID')
        for identifier in ids:
            event=lookup[identifier]
            if event['period'] not in offsets:raise ValueError('Selected action outside playing periods')
            when=offsets[event['period']]+pressure.time_module.cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])
            if (event['type']['name']!=kind or (event['team']['id'],event['player']['id'])!=(row['team_id'],row['player_id'])
                    or not interval['start_ms']<=when<=interval['end_ms'] or not begin_index<=event['index']<=end_index):
                raise ValueError('Selected action identity or registered scope differs')
            label=event_state(goals,event['index'],row['team_id'],home,away)
            output[label][field].append(identifier)
            if field=='completed_pass_ids' and identifier in row['forward_pass_ids']:output[label]['forward_pass_ids'].append(identifier)
    for result in output.values():
        result.update({'completed_passes':len(result['completed_pass_ids']),'forward_passes':len(result['forward_pass_ids']),
                       'recorded_pressures':len(result['pressure_ids'])})
    for metric in ('duration_ms','completed_passes','forward_passes','recorded_pressures'):
        if sum(r[metric] for r in output.values())!=row[metric]:raise ValueError('State rows do not reproduce match '+metric)
    return list(output.values())


def create_state_table(connection,rows):
    connection.executescript((ROOT/SQL_FILES['schema']).read_text())
    with connection:connection.executemany('INSERT INTO score_state_activity VALUES ('+','.join('?' for _ in COLUMNS)+')',
                                         [tuple(r[k] for k in COLUMNS) for r in rows])


def query_rates(connection):
    connection.row_factory=sqlite3.Row
    return [dict(r) for r in connection.execute((ROOT/SQL_FILES['rates']).read_text())]


def build_evidence(database_path=None,allow_download=True):
    data={k:json.loads((ROOT/path).read_text()) for k,path in SOURCES.items()}
    original=data['drilldown']
    if tuple(json.loads((ROOT/PROTOCOL).read_text())['score_states'])!=STATES:raise ValueError('Protocol state labels differ from implementation')
    for record in list(original['source_files'].values())+list(original['sql_files'].values()):
        if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Drill-down source or SQL changed')
    raw=pressure.time_module.cohort_module.raw
    metadata_record=data['lineups']['metadata_input']
    metadata=raw.load_events({**metadata_record,'source_url':metadata_record['url']},allow_download)
    fixtures={f['match_id']:f for f in metadata}
    rows=[];audits=[]
    for audit in data['minutes']['match_audits']:
        selected=[r for r in original['rows'] if r['match_id']==audit['match_id']]
        if not selected:continue
        events=raw.load_events(audit['raw_input'],allow_download)
        home,away,goals,final=goal_timeline(events,audit,fixtures[audit['match_id']])
        intervals={(r['team_id'],r['player_id']):r for r in audit['intervals']}
        for row in selected:rows.extend(split_match_row(row,intervals[(row['team_id'],row['player_id'])],events,goals,home,away,audit['periods']))
        audits.append({'match_id':audit['match_id'],'home_team_id':home,'away_team_id':away,'final_score_home_away':final,'goals':goals,'raw_input':audit['raw_input']})
    database_source=json.loads((ROOT/original['source_files']['database']['path']).read_text())
    for record in database_source['sql_files'].values():
        if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Base database SQL changed')
    with closing(sqlite3.connect(':memory:')) as connection:
        drill.database.create_database(connection,database_source['rows']);drill.create_match_table(connection,original['rows']);create_state_table(connection,rows)
        rates=query_rates(connection)
        for old in original['all_player_totals']:
            states=[r for r in rates if (r['team_id'],r['player_id'])==(old['team_id'],old['player_id'])]
            if {r['score_state'] for r in states}!=set(STATES):raise ValueError('State coverage differs')
            for field in ('duration_ms','completed_passes','forward_passes','recorded_pressures'):
                if sum(r[field] for r in states)!=old[field]:raise ValueError('Score-state totals differ from profile')
        if connection.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('State table parent membership failure')
        if database_path is not None:
            target=Path(database_path);target.parent.mkdir(parents=True,exist_ok=True)
            with closing(sqlite3.connect(target)) as destination:connection.backup(destination)
    focus=[{**{k:p[k] for k in ('team_id','player_id','player_name','team_name')},
            'states':[r for r in rates if (r['team_id'],r['player_id'])==(p['team_id'],p['player_id'])]} for p in original['focused_profiles']]
    return {'competition':original['competition'],'season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3: Statistical scouting','section':'Normalisation','url':READING},
            'source_files':{k:{'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for k,path in SOURCES.items()},
            'sql_files':{k:{'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for k,path in SQL_FILES.items()},
            'protocol_path':PROTOCOL,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest(),
            'metadata_input':metadata_record,'rows':rows,'rates':rates,'focused_profiles':focus,'match_audits':audits,
            'generated_database':DATABASE,
            'scope':'Descriptive action rates by observed score context with matched state-time exposure. Approximate goal timestamp boundaries, registered-time convention and later role changes retained. Zero exposure gives undefined rates. No causal score effect, opponent/possession adjustment, fresh validation or player-quality ranking.'}


def render_report(evidence):
    profiles=[]
    for p in evidence['focused_profiles']:
        lines=[]
        for r in p['states']:
            value='undefined (no state-time exposure)' if r['forward_per90'] is None else f"{r['forward_per90']:.2f}/90"
            lines.append(f"- **{r['score_state']}**: {r['forward_passes']} fixed-rule forward completions in {r['registered_minutes']:.2f} registered minutes → {value}; {r['completed_passes']} eligible completions; {r['recorded_pressures']} pressures.")
        profiles.append(f"## {p['player_name']} — {p['team_name']}\n\n"+'\n'.join(lines))
    return f'''# Passing activity with matched score-state time

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Normalisation]({READING}); [SQLite CASE and expressions](https://www.sqlite.org/lang_expr.html). This is our custom score-context extension.

Earlier score-state work counted actions while leading/drawing/trailing. Here each count is paired with registered time in that same state. All {len(evidence['rows'])} player–match–state rows reconcile to the original 145 player–match rows, and the {len(evidence['rates'])} player-state aggregates reconcile to all 35 profiles. Reconstructed final scores match metadata in all {len(evidence['match_audits'])} included fixtures.

{chr(10).join(profiles)}

## Exact conventions

Use the existing raw event-index goal accounting: Shot/Goal or Own Goal Against, ignoring its Own Goal For counterpart and shootouts. Count each selected action in the state immediately before it by event index. Split registered elapsed milliseconds at logged goal timestamps, with the score updated at that timestamp. Period lengths and no-halftime-gap convention come from lesson 64; added and extra time remain. Logged goal-event start times approximate the instant the score changed; event index resolves ties for actions while clock overlap determines duration.

A goal may therefore change the state partway through one player's registered interval. All three states remain present, including zero-exposure states. Rates use SUM(actions)*5,400,000/NULLIF(SUM(state milliseconds),0). No exposure gives an undefined rate, not zero performance. A boundary action can be retained even with zero measured duration for that state; its rate remains undefined. Counts and time are pooled before division, not averaged across match/state rates.

## Interpretation

These rates describe activity in different observed circumstances. They do not establish that leading or trailing caused a change: opponents, match phase, tactics, possession and role remain intertwined. Short state exposure can give a large rate from few actions; always inspect counts and minutes. A state appearing in only a few fixtures is not equivalent to a broad repeated comparison. No signing recommendation or new shortlist is generated. No footage has been reviewed.

## Reproduce

Run `python 85_scouting_score_context.py` in Spyder. The new local database is `{DATABASE}`; earlier databases remain unchanged. [Protocol](../{PROTOCOL}) · [State rows, action IDs, goal audits and source hashes](../data/85_scouting_score_context_evidence.json) · [SQL rates](../sql/85_score_state_rates.sql) · [Lesson](../lessons/0067-scouting-score-context.html).
Source: StatsBomb Open Data. Assisted implementation; independent reasoning and reproduction remain learning milestones.
'''


def main():
    evidence=build_evidence(ROOT/DATABASE)
    (ROOT/'data/85_scouting_score_context_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/68_scouting_score_context.md').write_text(render_report(evidence))
    print('State rows',len(evidence['rows']),'goal-checked fixtures',len(evidence['match_audits']))
    for p in evidence['focused_profiles']:
        print(p['player_name'],[(r['score_state'],round(r['registered_minutes'],2),r['forward_passes'],None if r['forward_per90'] is None else round(r['forward_per90'],2)) for r in p['states']])


if __name__=='__main__':main()
