"""Lesson 72: describe how one omitted own match changes a fixed-pool profile."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_FILES={'passing':'data/70_fullback_team_passing_share_evidence.json',
              'percentiles':'data/71_fullback_percentile_evidence.json'}
SPEC=importlib.util.spec_from_file_location('percentiles71',ROOT/'71_fullback_percentile_comparisons.py')
ranks=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ranks)
METRICS=ranks.METRICS


def validate_windows(player,windows):
    if (len({w['match_id'] for w in windows})!=len(windows)
            or {w['match_id'] for w in windows}!=set(player['qualifying_match_ids'])
            or any((w['team_id'],w['player_id'])!=(player['team_id'],player['player_id']) for w in windows)
            or sum(w['end_ms']-w['start_ms'] for w in windows)!=player['duration_ms']
            or sum(len(w['player_completed_ids']) for w in windows)!=player['eligible_completed']
            or sum(len(w['team_completed_ids']) for w in windows)!=player['team_completed_while_registered']):
        raise ValueError('Selected windows do not reconcile to the original profile')


def leave_out(player,window):
    if (window['match_id'] not in player['qualifying_match_ids']
            or (window['team_id'],window['player_id'])!=(player['team_id'],player['player_id'])):
        raise ValueError('Omitted window is not part of the target profile')
    duration=player['duration_ms']-(window['end_ms']-window['start_ms'])
    own=player['eligible_completed']-len(window['player_completed_ids'])
    team=player['team_completed_while_registered']-len(window['team_completed_ids'])
    if duration<=0 or not 0<=own<=team:
        raise ValueError('Remaining exposure or counts are invalid')
    return {'omitted_match_id':window['match_id'],
            'remaining_match_ids':[m for m in player['qualifying_match_ids'] if m!=window['match_id']],
            'remaining_qualifying_starts':len(player['qualifying_match_ids'])-1,
            'remaining_duration_ms':duration,'remaining_minutes':duration/60000,
            'remaining_completed':own,'remaining_team_completed':team,
            'completed_per90':own/(duration/60000)*90,
            'share_of_team_completions_pct':100*own/team if team else None}


def rank_variant(player,variant,reference):
    key=ranks.identity(player)
    peers=[{**p,**{metric:variant[metric] for metric in METRICS}} if ranks.identity(p)==key else p for p in reference]
    return {metric:ranks.percentile_for(key,peers,metric) for metric in METRICS}


def observed_range(values):
    valid=[v for v in values if v is not None]
    return {'minimum':min(valid) if valid else None,'maximum':max(valid) if valid else None,
            'defined_cases':len(valid)}


def range_text(result):
    if result['minimum'] is None:return 'undefined'
    return f"{result['minimum']:.2f}–{result['maximum']:.2f}"


def build_evidence():
    data={k:json.loads((ROOT/p).read_text()) for k,p in SOURCE_FILES.items()}
    reference=data['percentiles']['players'];players=data['passing']['players']
    if {ranks.identity(p) for p in reference}!={ranks.identity(p) for p in players}:
        raise ValueError('Original peer pool differs from the target profiles')
    output=[]
    for player in players:
        key=ranks.identity(player)
        baseline=next(p for p in reference if ranks.identity(p)==key)
        if any(baseline[m]!=player[m] for m in METRICS):raise ValueError('Baseline metric differs')
        windows=[w for w in data['passing']['windows'] if (w['team_id'],w['player_id'])==key]
        validate_windows(player,windows)
        by_match={w['match_id']:w for w in windows}
        cases=[]
        for match_id in player['qualifying_match_ids']:
            variant=leave_out(player,by_match[match_id])
            cases.append({**variant,'percentiles_fixed_peers':rank_variant(player,variant,reference)})
        output.append({'team_id':player['team_id'],'player_id':player['player_id'],
                       'player_name':player['player_name'],'team_name':player['team_name'],
                       'baseline':player,'baseline_percentiles':baseline['percentiles_all_fullbacks'],
                       'cases':cases,'metric_ranges':{m:observed_range([c[m] for c in cases]) for m in METRICS},
                       'percentile_ranges':{m:observed_range([c['percentiles_fixed_peers'][m]['percentile'] for c in cases]) for m in METRICS}})
    return {'competition':data['passing']['competition'],'season':'2019','competition_id':72,'season_id':30,
            'course_reading':data['percentiles']['course_reading'],
            'source_files':{k:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k,p in SOURCE_FILES.items()},
            'players':output,'cases':sum(len(p['cases']) for p in output),
            'method':'For each target separately, remove each of her own qualifying match windows in turn from own completions, team completions and registered minutes. Recalculate activity/involvement and compare the altered target with all other players held at original full-sample values. Use the original 35-player pool and percentile convention.',
            'scope':'Descriptive deletion sensitivity conditional on the original cohort. Eligibility and starting-side labels are not reselected, even when a three-start player is reduced to two. These ranges are not confidence intervals, future prediction limits, model cross-validation or proof of reliability. Other players sharing the omitted fixture retain their original observations.'}


def render_report(evidence):
    rows=[]
    for p in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        activity=p['metric_ranges']['completed_per90'];share=p['metric_ranges']['share_of_team_completions_pct']
        percentile=p['percentile_ranges']['completed_per90']
        rows.append(f"- {p['team_name']} — {p['player_name']}: baseline activity {p['baseline']['completed_per90']:.2f}/90; one-own-match-omitted activity {range_text(activity)}/90; involvement {range_text(share)}%; fixed-peer activity percentile {range_text(percentile)}. {len(p['cases'])} cases.")
    results='\n'.join(rows)
    return f'''# How much does a single match influence a fullback profile?

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30. Course reading: [Soccermatics Lesson 3 — Statistical scouting, Comparison: percentile rankings](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#comparison-percentile-rankings). This is a custom sensitivity extension, not the course's exact assignment.

We recalculate each player's two passing measures after omitting each of her own qualifying match windows in turn. All {len(evidence['players'])} original players stay in the reference population; the {evidence['cases']} target-specific cases remove own completions, same-window team completions and registered minutes together.

![Calculated activity after leaving out each own qualifying match](../figures/66_fullback_match_sensitivity.png)

## Worked interpretation

Bronze's original activity is 45.57 completions per 90. The seven calculated values after omitting each own match range from 42.99 to 47.36. Majri's original value is 30.70; her five deletion values range from 26.88 to 34.77. These describe dependence on the observed selected matches. They do not show how either player will perform in a future match or prove one is more reliable.

## All profiles

{results}

## What is held fixed

Only the target's own observed windows change in each case. Other players—including teammates or opponents from that fixture—keep their original full-sample values. Their original cohort eligibility also stays fixed. A player selected for three fullback starts remains in this conditional exercise after one is removed; we do not re-run a two-start recruitment selection. We use the overall fullback pool for percentile comparisons, not the exclusive-side pools.

The percentile change therefore answers a narrow question: where would this altered target profile sit against the original other players? It is not a global removal of the match from the tournament, a fresh-data test or a causal adjustment. Counts are pooled and divided by the remaining registered exposure; match percentages are not averaged.

## Limits

The minimum and maximum are simply the smallest and largest calculated deletion values. They are not 95% confidence intervals or complete uncertainty estimates, and narrow ranges do not prove stable ability. Minutes still use the registered-time convention with recorded added/extra time, temporary absences retained and halftime/shootouts excluded. Role, team possession, difficulty and opponents remain incompletely adjusted for. No signing recommendation or model fitting follows from this exercise.

## Reproduce

Run `python 72_fullback_match_sensitivity.py` in Spyder or locally. It uses saved windows and profiles without downloading data. [Evidence](../data/72_fullback_match_sensitivity_evidence.json) records every omitted match ID, remaining counts/minutes and fixed-peer ranks. [Lesson](../lessons/0054-fullback-match-sensitivity.html). Source: StatsBomb Open Data, **2019 Women's World Cup**, through the unchanged hash-linked records. Assisted historical exercise.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    selected=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    fig,axes=plt.subplots(1,2,figsize=(11,5.5))
    ymax=max(max(c['completed_per90'] for c in p['cases']) for p in selected)*1.18
    for ax,p,color in zip(axes,selected,('#24658a','#b77516')):
        cases=p['cases'];x=list(range(1,len(cases)+1))
        ax.plot(x,[c['completed_per90'] for c in cases],marker='o',color=color,label='One own match left out')
        ax.axhline(p['baseline']['completed_per90'],color='#526874',linestyle='--',label='Original selected matches')
        ax.set_xticks(x);ax.set_xlabel('Omitted match, in selected-fixture order')
        ax.set_ylabel('Completed eligible passes per registered 90')
        ax.set_ylim(0,ymax);ax.set_title(f"{p['player_name']} · {len(cases)} calculated cases",fontsize=11)
        ax.spines[['top','right']].set_visible(False);ax.legend(loc='lower right',frameon=False,fontsize=8)
    fig.suptitle('One match can change a tournament summary\n2019 Women’s World Cup · counts and minutes removed together',fontsize=14)
    fig.text(.5,.025,'Each point recalculates the target after one of her own matches is omitted.\nThese are sensitivity results, not confidence intervals or future predictions. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.12,1,.88])
    fig.savefig(ROOT/'figures/66_fullback_match_sensitivity.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/72_fullback_match_sensitivity_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/55_fullback_match_sensitivity.md').write_text(render_report(evidence))
    print('Targets',len(evidence['players']),'cases',evidence['cases'])
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p['player_name'],p['metric_ranges'],p['percentile_ranges'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
