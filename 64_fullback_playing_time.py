"""Lesson 64: audit registered minutes in qualifying fullback-start matches."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_PATH='data/63_fullback_cohort_evidence.json'
SPEC=importlib.util.spec_from_file_location('cohort63',ROOT/'63_fullback_recruitment_cohort.py')
cohort_module=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cohort_module)


def reconstruct_match(events,match_id):
    if len({e['id'] for e in events})!=len(events) or len({e['index'] for e in events})!=len(events):
        raise ValueError('Duplicate raw event identity or index')
    periods=sorted({e['period'] for e in events if e['period'] in (1,2,3,4)})
    if periods not in ([1,2],[1,2,3,4]):
        raise ValueError('Incomplete period sequence')
    lengths={};endings=[]
    for period in periods:
        ends=[e for e in events if e['period']==period and e['type']['name']=='Half End']
        if not ends or any(e.get('half_end',{}).get('early_video_end',False) for e in ends):
            raise ValueError('Complete recorded period end is required')
        end=max(ends,key=lambda e:(cohort_module.raw.scanner.timestamp_milliseconds(e['timestamp']),e['index']))
        lengths[period]=cohort_module.raw.scanner.timestamp_milliseconds(end['timestamp'])
        endings.append({'period':period,'length_ms':lengths[period],'end_event_id':end['id']})
    offsets={p:sum(lengths[q] for q in periods if q<p) for p in periods}
    duration=sum(lengths.values())
    if duration<=0:
        raise ValueError('Nonpositive match duration')
    def elapsed(event):
        value=cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])
        if not 0<=value<=lengths[event['period']]:
            raise ValueError('Registration event is outside its recorded period')
        return offsets[event['period']]+value
    starts=[e for e in events if e['type']['name']=='Starting XI' and e['period']==1]
    if len(starts)!=2 or len({e['team']['id'] for e in starts})!=2:
        raise ValueError('Expected two distinct starting teams')
    intervals=[];audits=[]
    for start in sorted(starts,key=lambda e:e['team']['id']):
        team_id=start['team']['id'];team_name=start['team']['name']
        lineup=start['tactics']['lineup']
        if len(lineup)!=11 or len({p['player']['id'] for p in lineup})!=11:
            raise ValueError('Expected 11 distinct starters')
        active={p['player']['id']:(0,p['player']['name'],start['id']) for p in lineup}
        appeared=set(active);team_intervals=[];departures=[];temporary=[]
        lost=0
        def close(player_id,end,reason,event_id):
            began,name,begin_event=active.pop(player_id)
            if end<began:
                raise ValueError('Negative playing interval')
            team_intervals.append({'match_id':match_id,'team_id':team_id,'team_name':team_name,
                'player_id':player_id,'player_name':name,'start_ms':began,'end_ms':end,
                'duration_ms':end-began,'minutes':(end-began)/60000,
                'start_event_id':begin_event,'end_event_id':event_id,'end_reason':reason})
        for event in sorted(events,key=lambda e:e['index']):
            if event['period'] not in periods or event.get('team',{}).get('id')!=team_id:
                continue
            kind=event['type']['name']
            card=(event.get('foul_committed',{}).get('card') or event.get('bad_behaviour',{}).get('card') or {}).get('name')
            permanent=kind=='Player Off' and event.get('player_off',{}).get('permanent',False)
            if kind=='Substitution':
                outgoing=event['player']['id'];incoming=event['substitution']['replacement']
                if outgoing not in active or incoming['id'] in appeared:
                    raise ValueError('Substitution conflicts with active player registration')
                when=elapsed(event)
                close(outgoing,when,'Substitution',event['id'])
                active[incoming['id']]=(when,incoming['name'],event['id']);appeared.add(incoming['id'])
            elif card in ('Red Card','Second Yellow') or permanent:
                player_id=event['player']['id'];when=elapsed(event)
                on_field=player_id in active
                reason=card or 'Permanent departure'
                departures.append({'event_id':event['id'],'player_id':player_id,'elapsed_ms':when,
                                   'reason':reason,'changed_active_registration':on_field})
                if on_field:
                    close(player_id,when,reason,event['id']);lost+=duration-when
            elif kind in ('Player Off','Player On'):
                temporary.append({'event_id':event['id'],'player_id':event['player']['id'],
                                  'kind':kind,'elapsed_ms':elapsed(event)})
        for player_id in sorted(active):
            close(player_id,duration,'Full time',endings[-1]['end_event_id'])
        total=sum(r['duration_ms'] for r in team_intervals)
        if total!=11*duration-lost:
            raise ValueError('Team registered-time balance failed')
        intervals.extend(team_intervals)
        audits.append({'team_id':team_id,'team_name':team_name,'interval_count':len(team_intervals),
                       'registered_player_ms':total,'expected_player_ms':11*duration-lost,
                       'permanent_absence_ms':lost,'departures':departures,
                       'temporary_absence_events_retained':temporary})
    return {'match_id':match_id,'periods':endings,'match_duration_ms':duration,
            'team_audits':audits,'intervals':intervals}


def aggregate_players(players,matches):
    indexed={m['match_id']:m for m in matches}
    result=[]
    for player in players:
        selected=[]
        for match_id in player['qualifying_match_ids']:
            rows=[r for r in indexed[match_id]['intervals'] if r['team_id']==player['team_id'] and r['player_id']==player['player_id']]
            if len(rows)!=1 or rows[0]['start_ms']!=0:
                raise ValueError('Qualifying role starter must have one interval starting at zero')
            selected.append(rows[0])
        total=sum(r['duration_ms'] for r in selected)
        result.append({'team_id':player['team_id'],'player_id':player['player_id'],
                       'player_name':player['player_name'],'team_name':player['team_name'],
                       'role_starts':player['role_starts'],'qualifying_match_ids':player['qualifying_match_ids'],
                       'duration_ms':total,'minutes':total/60000,'starts_times_90':player['role_starts']*90,
                       'end_reasons':[{'match_id':r['match_id'],'reason':r['end_reason'],'minutes':r['minutes']} for r in selected]})
    return result


def build_evidence(allow_download=True):
    source=json.loads((ROOT/SOURCE_PATH).read_text())
    matches=[{'raw_input':record,**reconstruct_match(cohort_module.raw.load_events(record,allow_download),record['match_id'])}
             for record in source['raw_inputs']]
    players=aggregate_players(source['eligible_players'],matches)
    return {'competition':'FIFA Women’s World Cup','season':'2019','competition_id':72,'season_id':30,
            'source_path':SOURCE_PATH,'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'course_reading':{'lesson':'Soccermatics Lesson 3: Statistical scouting','section':'Normalisation',
                             'url':'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'},
            'time_convention':'Registered intervals in qualifying fullback-start fixtures. Recorded period lengths include added time and extra time; halftime breaks and shootouts excluded. Temporary absences retained. Substitutions, dismissals and permanent departures close intervals. Later role changes do not split these intervals.',
            'match_audits':matches,'players':players,
            'summary':{'matches_audited':len(matches),'teams_audited':sum(len(m['team_audits']) for m in matches),
                       'players':len(players),'selected_starts':sum(p['role_starts'] for p in players),
                       'selected_duration_ms':sum(p['duration_ms'] for p in players)},
            'scope':'Minutes reconstructed from event timestamps, not independent official minute totals or ball-in-play time. Restricted to each eligible player’s qualifying starting-role matches, not all appearances or verified minutes spent at fullback. No performance rates or ability ranking yet.'}


def render_report(evidence):
    players=sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name']))
    rows='\n'.join(f"- {p['team_name']} — {p['player_name']}: {p['role_starts']} qualifying starts; "
                   f"{p['minutes']:.2f} reconstructed minutes (starts × 90 would give {p['starts_times_90']})." for p in players)
    return f'''# Playing-time denominators for the fullback study

Competition and season: **FIFA Women’s World Cup, 2019**. StatsBomb competition 72, season 30.

Course reading: [Soccermatics Lesson 3 — Statistical scouting, Normalisation](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation). This custom exercise prepares minute denominators for later per-90 profiling.

We reconstructed registered playing intervals across all {evidence['summary']['matches_audited']} tournament matches and checked the time balance for {evidence['summary']['teams_audited']} teams in those matches. The unchanged 35-player pool contributes {evidence['summary']['selected_starts']} qualifying fullback starts. We sum each player's intervals in those qualifying fixtures only.

{rows}

## Time convention and audit

The maximum recorded Half End timestamp defines each period length; missing or explicitly early-video-end signals stop reconstruction. Period offsets add playing periods together, excluding halftime gaps. Recorded added time and extra time count; shootouts do not. Substitutions close the outgoing registration and open the replacement at the same instant. Active dismissals and permanent departures close an interval without replacement. Temporary Player Off/On absences are retained under the registered-time convention; they are not physical-on-pitch or ball-in-play minutes.

For every team we verify: summed player interval time = 11 × recorded match duration − time lost after active permanent departures. An inactive-player dismissal cannot reduce that team’s active player time again. Full interval and event-ID audit trails are saved. This arithmetic audit is not an independent comparison with official playing-time totals.

## Use these denominators correctly

Three starts need not equal 270 minutes. Early substitutions can lower the time, while added time or extra time can raise it. A toy example: 10 selected actions in 200 minutes gives 10/200 × 90 = 4.5 per 90; the action count is illustrative, not an observed player result.

These intervals cover only the matches where the selected player started in an eligible role. Other appearances are excluded from the selected denominator. They include later tactical role changes, so they are not verified position-specific minutes. Future action counts must use exactly the same selected fixtures and active-player intervals. Possession and opponent context still need attention after time normalization. No action-rate calculation or ranking is produced in this lesson.

![Qualifying starts versus reconstructed minutes for two familiar examples](../figures/59_fullback_playing_time_examples.png)

## Reproduce and read

Run `python 64_fullback_playing_time.py` in Spyder or locally. [Evidence](../data/64_fullback_playing_time_evidence.json) · [Lesson](../lessons/0046-fullback-playing-time.html) · [Recruitment reference](../reference/recruitment-analysis.html).

Source: [StatsBomb Open Data](https://github.com/statsbomb/open-data), **2019 Women’s World Cup**; fields documented in the [Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Assisted historical exercise; independent skill remains to demonstrate.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    selected=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    fig,ax=plt.subplots(figsize=(9,5))
    for i,player in enumerate(selected):
        ax.barh(i-.17,player['starts_times_90'],height=.3,color='#969fa5',label='Starts × 90' if i==0 else None)
        ax.barh(i+.17,player['minutes'],height=.3,color='#24658a',label='Reconstructed registered time' if i==0 else None)
        ax.text(player['starts_times_90']+5,i-.17,f"{player['starts_times_90']:.0f}",va='center')
        ax.text(player['minutes']+5,i+.17,f"{player['minutes']:.1f}",va='center')
    ax.set_yticks(range(2),[f"{p['player_name']} ({p['role_starts']} qualifying starts)" for p in selected])
    ax.set_xlim(0,max(p['minutes'] for p in selected)*1.15)
    ax.set_xlabel('Minutes in qualifying starting-role matches')
    ax.set_title('Starts are not a playing-time denominator\n2019 Women’s World Cup · two familiar examples')
    ax.spines[['top','right']].set_visible(False)
    fig.legend(loc='lower center',bbox_to_anchor=(.5,.115),ncol=2,frameon=False,fontsize=9)
    fig.text(.5,.025,'Recorded added/extra time included; halftime and shootouts excluded; temporary absences retained.\nNot verified fullback-position minutes. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.22,1,1])
    fig.savefig(ROOT/'figures/59_fullback_playing_time_examples.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/64_fullback_playing_time_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/47_fullback_playing_time.md').write_text(render_report(evidence))
    print(evidence['summary'])
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p['player_name'],p['role_starts'],p['minutes'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
