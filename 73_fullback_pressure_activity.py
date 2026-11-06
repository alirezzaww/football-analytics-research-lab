"""Lesson 73: recorded defensive pressure activity in the existing player windows."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_PATH='data/64_fullback_playing_time_evidence.json'
SPEC=importlib.util.spec_from_file_location('minutes64',ROOT/'64_fullback_playing_time.py')
time_module=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(time_module)


def location_or_none(value):
    if (isinstance(value,(list,tuple)) and len(value)==2
            and all(type(v) in (int,float) and math.isfinite(v) for v in value)
            and 0<=value[0]<=120 and 0<=value[1]<=80):
        return value[0],value[1]
    return None,None


def pressure_rows(events,audit,intervals):
    lookup={e['id']:e for e in events}
    if len(lookup)!=len(events):raise ValueError('Duplicate raw event ID')
    selected={(r['team_id'],r['player_id']):r for r in intervals}
    if len(selected)!=len(intervals):raise ValueError('Duplicate selected interval')
    offsets={p['period']:sum(q['length_ms'] for q in audit['periods'] if q['period']<p['period']) for p in audit['periods']}
    rows=[]
    for event in events:
        if event['type']['name']!='Pressure' or event['period'] not in offsets:continue
        key=(event['team']['id'],event['player']['id'])
        if key not in selected:continue
        interval=selected[key]
        when=offsets[event['period']]+time_module.cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])
        if (not interval['start_ms']<=when<=interval['end_ms']
                or not lookup[interval['start_event_id']]['index']<=event['index']<=lookup[interval['end_event_id']]['index']):
            raise ValueError('Recorded pressure is outside selected registration: '+event['id'])
        x,y=location_or_none(event.get('location'))
        rows.append({'match_id':audit['match_id'],'team_id':key[0],'player_id':key[1],
                     'event_id':event['id'],'index':event['index'],'period':event['period'],
                     'minute':event['minute'],'second':event['second'],
                     'timestamp':event['timestamp'],'elapsed_ms':when,
                     'x':x,'y':y,'location_valid':x is not None})
    return rows


def summarize(player,rows):
    if player['duration_ms']<=0 or any((r['team_id'],r['player_id'])!=(player['team_id'],player['player_id']) for r in rows):
        raise ValueError('Invalid pressure identity or selected exposure')
    if any(r['match_id'] not in player['qualifying_match_ids'] for r in rows):
        raise ValueError('Pressure comes from a nonqualifying fixture')
    return {**player,'recorded_pressures':len(rows),
            'pressures_per90':len(rows)/(player['duration_ms']/60000)*90,
            'mapped_pressures':sum(r['location_valid'] for r in rows),
            'unmapped_pressures':sum(not r['location_valid'] for r in rows)}


def build_evidence(allow_download=True):
    source=json.loads((ROOT/SOURCE_PATH).read_text())
    rows=[];windows=[]
    for audit in source['match_audits']:
        keys={(p['team_id'],p['player_id']) for p in source['players'] if audit['match_id'] in p['qualifying_match_ids']}
        if not keys:continue
        intervals=[r for r in audit['intervals'] if (r['team_id'],r['player_id']) in keys]
        if len(intervals)!=len(keys):raise ValueError('Pressure-window coverage differs from source')
        events=time_module.cohort_module.raw.load_events(audit['raw_input'],allow_download)
        matched=pressure_rows(events,audit,intervals);rows.extend(matched)
        for interval in intervals:
            identifiers=[r['event_id'] for r in matched if (r['team_id'],r['player_id'])==(interval['team_id'],interval['player_id'])]
            windows.append({'match_id':audit['match_id'],'team_id':interval['team_id'],'player_id':interval['player_id'],
                            'start_ms':interval['start_ms'],'end_ms':interval['end_ms'],'pressure_ids':identifiers})
    players=[]
    for player in source['players']:
        own_windows=[w for w in windows if (w['team_id'],w['player_id'])==(player['team_id'],player['player_id'])]
        if {w['match_id'] for w in own_windows}!=set(player['qualifying_match_ids']):raise ValueError('Pressure fixtures differ from minutes')
        if sum(w['end_ms']-w['start_ms'] for w in own_windows)!=player['duration_ms']:raise ValueError('Pressure minutes differ')
        own=[r for r in rows if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id'])]
        players.append(summarize(player,own))
    return {'competition':source['competition'],'season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3: Statistical scouting','section':'Counts of actions; Normalisation',
                             'url':'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#counts-of-actions',
                             'normalisation_url':'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'},
            'source_path':SOURCE_PATH,'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'rows':rows,'windows':windows,'players':players,
            'rule':'Count recorded event type Pressure starts by the selected player, periods 1–4, in qualifying fixtures and registered clock/event-order bounds. Do not apply the passing possession-team or restart filters. No duration weighting or success/regain label is used. Invalid/missing locations remain counted but unmapped.',
            'scope':'Observed pressure activity, not tackles, ball wins, successful pressing, team defensive quality or continuous tracking. Same registered-minute convention and original cohort. Not adjusted for opponent possession or pressing opportunities; later role changes remain included.'}


def render_report(evidence):
    lines=[]
    for p in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        lines.append(f"- {p['team_name']} — {p['player_name']}: {p['recorded_pressures']} recorded pressures in {p['minutes']:.1f} registered minutes; **{p['pressures_per90']:.2f}/90**; valid map locations {p['mapped_pressures']}/{p['recorded_pressures']}.")
    rows='\n'.join(lines)
    examples=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    worked='\n'.join(f"- {p['player_name']}: {p['recorded_pressures']} / {p['minutes']:.6f} ×90 = {p['pressures_per90']:.6f} pressures per 90." for p in examples)
    return f'''# Defensive participation: recorded pressure activity

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30. Reading: [Soccermatics Lesson 3 — Counts of actions](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#counts-of-actions) and [Normalisation](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation).

We add a defensive activity count to the existing 35-player fullback profiling exercise. We count the provider's recorded Pressure events, representing a player applying pressure to an attacking player. We do not detect pressure ourselves from player proximity or infer it from pass outcomes. The counted event is the start of the recorded pressure; duration is not summed or weighted.

## Worked examples

{worked}

![Recorded pressure start locations for two familiar examples](../figures/67_fullback_pressure_activity.png)

## All profiles, alphabetical by team and name

{rows}

## Matched scope and location coverage

Each numerator uses the player's unchanged qualifying fullback-start fixtures and registered intervals from lesson 64. Both elapsed time and event order are checked. Added/extra time and temporary absences retain the earlier registered-time convention; halftime and shootouts are excluded. Later role changes are included, so these are not verified position-specific minutes or actions.

Pressure events are off-ball actions. We do not copy the passing filter requiring event team to equal possession team: that would omit legitimate defensive actions against an opponent in possession. A pass event labelled under_pressure is also not counted as a Pressure event by the passer. Restart-delivery filters for passes are not applied to this distinct event type.

Counts include every selected Pressure event regardless of location availability. Missing or invalid in-pitch coordinate pairs are saved as unmapped, never moved to (0,0) or dropped from the count. Map dots show recorded start locations, not running trajectories or all defensive positioning. Window event IDs and source hashes allow replay.

## Football interpretation

More pressures per 90 means more recorded pressure activity in these selected minutes. It does not establish that the actions were successful, led to regains, or made the player a better defender. A player with less pressure activity may have faced fewer opportunities or followed different instructions. We have not adjusted for opponent possession, game state, difficulty or team tactics. No pressure-regain metric or causal effect is calculated here. This is a custom defensive extension applying the course's counts/context ideas, not a complete defensive assessment or signing recommendation.

## Reproduce

Run `python 73_fullback_pressure_activity.py` in Spyder or locally. [Evidence](../data/73_fullback_pressure_activity_evidence.json) · [Lesson](../lessons/0055-fullback-pressure-activity.html). Source: StatsBomb Open Data, **2019 Women's World Cup**, hash-checked archived events. Definition: [Open Data specification, Pressure event](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Assisted worked exercise; no new model or video observation.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    from mplsoccer import Pitch
    selected=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    pitch=Pitch(pitch_type='statsbomb',line_color='#a3afb4')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    fig.set_layout_engine(None)
    for ax,p,color in zip(axes,selected,('#24658a','#b77516')):
        pitch.draw(ax=ax)
        rows=[r for r in evidence['rows'] if (r['team_id'],r['player_id'])==(p['team_id'],p['player_id']) and r['location_valid']]
        if rows:pitch.scatter([r['x'] for r in rows],[r['y'] for r in rows],s=22,color=color,alpha=.6,ax=ax)
        ax.set_title(f"{p['player_name']} · {p['recorded_pressures']} recorded pressures\n{p['pressures_per90']:.2f} per 90 · mapped {p['mapped_pressures']}/{p['recorded_pressures']}",fontsize=11)
    fig.suptitle('Recorded pressure starts · 2019 Women’s World Cup\nFocus teams attack towards the right in normalized coordinates',fontsize=14,y=.96)
    fig.text(.5,.035,'Dots show provider-recorded Pressure events, not success, regains or continuous player tracking.\nSame selected registered windows; opponent possession not adjusted for. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.03,right=.97,bottom=.18,top=.76,wspace=.14)
    fig.savefig(ROOT/'figures/67_fullback_pressure_activity.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/73_fullback_pressure_activity_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/56_fullback_pressure_activity.md').write_text(render_report(evidence))
    print('Profiles',len(evidence['players']),'pressure events',len(evidence['rows']))
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p['player_name'],p['recorded_pressures'],p['pressures_per90'],p['unmapped_pressures'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
