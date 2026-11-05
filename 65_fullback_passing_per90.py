"""Lesson 65: matched-scope passing activity per reconstructed 90 minutes."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_PATH='data/64_fullback_playing_time_evidence.json'
RESTARTS={'Throw-in','Corner','Free Kick','Kick Off','Goal Kick'}
FAILURES={'Incomplete','Out','Pass Offside'}
EXCLUDED_OUTCOMES={'Unknown','Injury Clearance'}
SPEC=importlib.util.spec_from_file_location('minutes64',ROOT/'64_fullback_playing_time.py')
time_module=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(time_module)


def count_match(events,audit,selected_intervals):
    lookup={e['id']:e for e in events}
    if len(lookup)!=len(events):
        raise ValueError('Duplicate raw event ID')
    offsets={p['period']:sum(q['length_ms'] for q in audit['periods'] if q['period']<p['period']) for p in audit['periods']}
    intervals={(r['team_id'],r['player_id']):r for r in selected_intervals}
    if len(intervals)!=len(selected_intervals):
        raise ValueError('Repeated selected interval identity')
    output={key:{'match_id':audit['match_id'],'team_id':key[0],'player_id':key[1],
                 'candidate_passes':0,'attempt_ids':[],'completed_ids':[],
                 'excluded':{'restart':0,'not_possession_team':0,'unknown_or_injury':0}}
            for key in intervals}
    for event in events:
        if event['type']['name']!='Pass' or event['period'] not in offsets:
            continue
        key=(event['team']['id'],event['player']['id'])
        if key not in intervals:
            continue
        interval=intervals[key]
        when=offsets[event['period']]+time_module.cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])
        if (not interval['start_ms']<=when<=interval['end_ms']
                or not lookup[interval['start_event_id']]['index']<=event['index']<=lookup[interval['end_event_id']]['index']):
            raise ValueError('Selected player pass is outside the registered interval')
        row=output[key];row['candidate_passes']+=1
        detail=event['pass']
        if detail.get('type',{}).get('name') in RESTARTS:
            row['excluded']['restart']+=1;continue
        if event['possession_team']['id']!=event['team']['id']:
            row['excluded']['not_possession_team']+=1;continue
        outcome=detail['outcome']['name'] if 'outcome' in detail else None
        if outcome in EXCLUDED_OUTCOMES:
            row['excluded']['unknown_or_injury']+=1;continue
        if outcome is not None and outcome not in FAILURES:
            raise ValueError('Unrecognized pass outcome')
        row['attempt_ids'].append(event['id'])
        if outcome is None:
            row['completed_ids'].append(event['id'])
    return [output[key] for key in sorted(output)]


def player_summary(player,rows):
    if player['duration_ms']<=0:
        raise ValueError('Positive playing-time exposure is required')
    attempts=sum(len(r['attempt_ids']) for r in rows)
    completed=sum(len(r['completed_ids']) for r in rows)
    minutes=player['duration_ms']/60000
    return {**{k:player[k] for k in ('team_id','player_id','player_name','team_name','role_starts','qualifying_match_ids','duration_ms')},
            'minutes':minutes,'eligible_attempts':attempts,'eligible_completed':completed,
            'attempts_per90':attempts/minutes*90,'completed_per90':completed/minutes*90,
            'completion_pct':100*completed/attempts if attempts else None}


def build_evidence(allow_download=True):
    source=json.loads((ROOT/SOURCE_PATH).read_text())
    players=source['players'];rows=[]
    for match in source['match_audits']:
        keys={(p['team_id'],p['player_id']) for p in players if match['match_id'] in p['qualifying_match_ids']}
        if not keys:
            continue
        intervals=[r for r in match['intervals'] if (r['team_id'],r['player_id']) in keys]
        if len(intervals)!=len(keys):
            raise ValueError('Selected player interval coverage differs')
        events=time_module.cohort_module.raw.load_events(match['raw_input'],allow_download)
        rows.extend(count_match(events,match,intervals))
    summaries=[]
    for player in players:
        selected=[r for r in rows if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id'])]
        if {r['match_id'] for r in selected}!=set(player['qualifying_match_ids']):
            raise ValueError('Passing numerator does not cover the minute denominator fixtures')
        summaries.append(player_summary(player,selected))
    return {'competition':source['competition'],'season':source['season'],
            'competition_id':source['competition_id'],'season_id':source['season_id'],
            'course_reading':source['course_reading'],'source_path':SOURCE_PATH,
            'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'pass_rule':'Non-restart Pass events by the selected player in a qualifying fixture and registered interval, periods 1–4, with possession_team equal to event team. No outcome means completed. Incomplete/Out/Pass Offside remain attempted failures. Unknown/Injury Clearance excluded. Subsequent passes after a restart can remain eligible; no location filter.',
            'pass_ledger':rows,'players':summaries,
            'scope':'Activity rates per 90 reconstructed registered minutes; same qualifying-start fixtures as lesson 64. Not verified position-specific activity, possession-adjusted rates, pass difficulty estimates or player ability rankings. Historical 2019 exercise.'}


def render_report(evidence):
    rows=[]
    for p in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        rate=f"{p['completion_pct']:.1f}%" if p['completion_pct'] is not None else 'undefined'
        rows.append(f"- {p['team_name']} — {p['player_name']}: {p['eligible_completed']}/{p['eligible_attempts']} eligible passes completed ({rate}); {p['minutes']:.1f} minutes; {p['attempts_per90']:.2f} attempts and {p['completed_per90']:.2f} completions per 90.")
    results='\n'.join(rows)
    examples=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    calculations='\n'.join(f"- {p['player_name']}: {p['eligible_completed']} / {p['minutes']:.6f} × 90 = {p['completed_per90']:.6f} completed eligible passes per 90." for p in examples)
    return f'''# Fullback passing activity per 90

Competition/season: **2019 FIFA Women’s World Cup** (StatsBomb competition 72, season 30).
Reading: [Soccermatics Lesson 3 — Statistical scouting, Normalisation](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation).

The unchanged 35-player pool now has matched-scope passing counts and playing-time denominators. Each count uses only the player's qualifying starting-role matches and registered intervals from lesson 64.

## Worked examples

{calculations}

![Counts and per-90 activity for the two familiar examples](../figures/60_fullback_passing_per90.png)

## All player summaries, alphabetical by team and name

{results}

## Definitions

Keep period-1–4 passes by the selected player in the selected fixtures, with timestamps and event order inside the registered interval. Exclude restart deliveries: Throw-in, Corner, Free Kick, Kick Off and Goal Kick. Also exclude passes where possession_team differs from the event team. A pass with no outcome annotation is completed; Incomplete, Out and Pass Offside count as attempted failures. Unknown and Injury Clearance are excluded from both the attempt denominator and completed count. Other unexpected outcome labels stop calculation. No location filter is applied.

This is a non-restart delivery filter, not a claim to remove every set-piece possession: later passes in the same possession may remain. Saved event-ID lists preserve eligible attempts and completed subsets; exclusion categories are applied in the written order and reconcile to candidate pass totals. Passes for a selected identity outside its registered interval trigger an error rather than silently disappearing.

Attempts per 90 = attempts / selected minutes × 90. Completions per 90 uses completed passes instead. Completion percentage = completed / attempted × 100; it does not use minutes. A zero-attempt player has an undefined percentage, not 0%.

## Interpretation

Per-90 activity standardizes the time denominator; it does not adjust for team possession, opponents, game state, passing difficulty or subsequent tactical role changes. Higher completion volume does not automatically mean better passing ability. Left/right starting-role splits remain in the cohort evidence but are not adjusted for here. These are selected-fixture activity profiles, not pure fullback-position measures or current transfer recommendations. No model was trained and no ability ranking is presented.

## Reproduce

Run `python 65_fullback_passing_per90.py` in Spyder or locally. [Evidence](../data/65_fullback_passing_per90_evidence.json) · [Lesson](../lessons/0047-fullback-passing-per90.html) · [Definitions and references](../reference/recruitment-analysis.html). Source: StatsBomb Open Data, **2019 Women’s World Cup**, archived hash-checked event files. This is an assisted worked extension.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    players=[next(p for p in evidence['players'] if p['player_id']==i) for i in (10178,15249)]
    fig,axes=plt.subplots(1,2,figsize=(10,5))
    for ax,field,title,label in ((axes[0],'eligible_completed','Completed eligible passes','Passes (count)'),
                                  (axes[1],'completed_per90','Completed eligible passes per 90','Passes per 90 registered minutes')):
        values=[p[field] for p in players]
        ax.bar(range(2),values,color=['#24658a','#b77516'],width=.55)
        for i,value in enumerate(values):ax.text(i,value+max(values)*.025,f'{value:.1f}' if field.endswith('90') else str(value),ha='center')
        ax.set_xticks(range(2),[p['player_name'] for p in players]);ax.set_title(title,fontsize=11)
        ax.set_ylabel(label);ax.set_ylim(0,max(values)*1.18)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Count and rate answer different questions\n2019 Women’s World Cup · qualifying starting-role fixtures',fontsize=14)
    fig.text(.5,.025,'Non-restart, possession-team passes with known outcomes. Added/extra time included in minutes.\nTime normalization does not establish passing ability. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.12,1,.88])
    fig.savefig(ROOT/'figures/60_fullback_passing_per90.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/65_fullback_passing_per90_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/48_fullback_passing_per90.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p)
    plot_evidence(evidence)


if __name__=='__main__':
    main()
