"""Lesson 71: cohort-relative percentiles with explicit tie and side rules."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_FILES={'passing':'data/70_fullback_team_passing_share_evidence.json',
              'cohort':'data/63_fullback_cohort_evidence.json'}
METRICS=('completed_per90','share_of_team_completions_pct')


def identity(row):
    return row['team_id'],row['player_id']


def side_group(player):
    left=player['position_starts']['Left Back'];right=player['position_starts']['Right Back']
    if type(left) is not int or type(right) is not int or min(left,right)<0 or left+right!=player['role_starts'] or left+right==0:
        raise ValueError('Starting-side counts do not reconcile')
    return 'left_only' if right==0 else 'right_only' if left==0 else 'mixed'


def percentile_for(key,peers,metric):
    keys=[identity(p) for p in peers]
    if len(keys)!=len(set(keys)) or keys.count(key)!=1:
        raise ValueError('Expected a unique target in a pool of distinct player/team identities')
    for p in peers:
        value=p[metric]
        if value is not None and (type(value) not in (int,float) or not math.isfinite(value)):
            raise ValueError('Percentile metric must be numeric, finite or missing')
    target=next(p for p in peers if identity(p)==key)
    value=target[metric]
    valid=[p for p in peers if p[metric] is not None]
    others=[p for p in valid if identity(p)!=key]
    result={'value':value,'valid_pool_size':len(valid),'other_players':len(others),
            'lower_count':None,'tied_other_count':None,'higher_count':None,'percentile':None}
    if value is None or not others:return result
    lower=sum(p[metric]<value for p in others)
    tied=sum(p[metric]==value for p in others)
    return {**result,'lower_count':lower,'tied_other_count':tied,
            'higher_count':len(others)-lower-tied,
            'percentile':100*(lower+.5*tied)/len(others)}


def build_evidence():
    data={k:json.loads((ROOT/p).read_text()) for k,p in SOURCE_FILES.items()}
    players=data['passing']['players'];cohort=data['cohort']['eligible_players']
    roles={identity(p):p for p in cohort}
    if len(roles)!=len(cohort) or len({identity(p) for p in players})!=len(players) or set(roles)!={identity(p) for p in players}:
        raise ValueError('Role and passing pools differ')
    pools={'all_fullbacks':players,
           'left_only':[p for p in players if side_group(roles[identity(p)])=='left_only'],
           'right_only':[p for p in players if side_group(roles[identity(p)])=='right_only']}
    profiles=[]
    for p in players:
        key=identity(p);side=side_group(roles[key])
        profiles.append({**p,'starting_side_group':side,
                         'percentiles_all_fullbacks':{m:percentile_for(key,players,m) for m in METRICS},
                         'percentiles_same_side':{m:percentile_for(key,pools[side],m) for m in METRICS} if side!='mixed' else None})
    return {'competition':data['passing']['competition'],'season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3: Statistical scouting','section':'Comparison: percentile rankings',
                             'url':'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#comparison-percentile-rankings'},
            'source_files':{k:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k,p in SOURCE_FILES.items()},
            'method':'100 × (strictly lower other-player values + 0.5 × equal other-player values) / valid other players. Exclude the target from the comparison denominator. Use unrounded metric values. Undefined with no valid peers or missing target metric. This is an explicit project percentile convention, not a claim that all software uses this formula.',
            'side_rule':'Exclusive side means all qualifying starts were on that side, not every played minute. Mixed-side players stay in the all-fullback pool but receive no exclusive-side percentile.',
            'metrics':list(METRICS),
            'peer_pools':{name:[{'team_id':p['team_id'],'player_id':p['player_id']} for p in group] for name,group in pools.items()},
            'players':profiles,
            'scope':'Descriptive ranks within selected historical pools, not completion accuracy, scoring probabilities, model accuracy or general football ability. Original values and exposures unchanged. No possession/difficulty adjustment, confidence interval or recruitment recommendation.'}


def rank_text(result):
    if result['percentile'] is None:return 'undefined'
    return f"{result['percentile']:.1f} (N={result['valid_pool_size']})"


def render_report(evidence):
    lines=[]
    for p in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        all_ranks=p['percentiles_all_fullbacks'];side=p['percentiles_same_side']
        side_text='not computed for mixed-side starts' if side is None else f"activity {rank_text(side['completed_per90'])}, involvement {rank_text(side['share_of_team_completions_pct'])}"
        lines.append(f"- {p['team_name']} — {p['player_name']} ({p['starting_side_group']}): all-fullback activity percentile {rank_text(all_ranks['completed_per90'])}, involvement {rank_text(all_ranks['share_of_team_completions_pct'])}; exclusive-side comparison: {side_text}.")
    rows='\n'.join(lines)
    return f'''# Fullback percentiles: always name the comparison pool

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30. Reading: [Soccermatics Lesson 3 — Statistical scouting, Comparison: percentile rankings](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#comparison-percentile-rankings).

We place two unchanged raw measures—completed eligible passes per registered 90 and share of same-window team completions—within explicit peer groups. A higher percentile means a larger value for that measure in the named group, not a better footballer.

## Comparison groups

- All selected fullbacks: {len(evidence['peer_pools']['all_fullbacks'])} player/team identities.
- Exclusively left-back qualifying starts: {len(evidence['peer_pools']['left_only'])}.
- Exclusively right-back qualifying starts: {len(evidence['peer_pools']['right_only'])}.

Four mixed-side players remain in the all-fullback comparison and have no exclusive-side percentile. These are recorded starting-role filters, not verified role-duration measures. The same three-start selection from lesson 63 remains in force; the smaller groups do not guarantee reliable ability estimates.

## How the percentile is calculated

Compare a target to other valid players in the pool: 100 × (number strictly lower + half the number tied) / number of other valid players. Unrounded metric values determine ties. For unique extremes, the lowest is 0 and highest 100; if every other value is tied, the result is 50. Missing values are not zero, and a lone valid player has an undefined percentile. This is our documented convention; software percentile-rank definitions differ.

For Majri's passing activity, 21 of the other 34 fullbacks have lower values, with no ties: 21/34 ×100 = 61.8. Her value remains 30.70 completions per 90. Bronze has the highest activity in this selected group, so all 34 others are lower and her activity percentile is 100. Neither number is pass-completion percentage or a general ability grade.

![Percentiles under all-fullback and same-side pools](../figures/65_fullback_percentile_comparisons.png)

Majri's involvement percentile changes from 73.5 among all 35 to 68.8 among the 17 exclusive left-back starters. Her involvement value stays 10.60%. The reference group changed; her actions did not. Matching starting side is only one context filter, not a full adjustment for role, possession, opponents or difficulty.

## All profiles, alphabetical by team and name

{rows}

## Use and limits

Percentiles summarize relative position, not the size or football importance of a difference. A small raw gap can change rank. These small historical cohorts do not establish present-day ability, significance, uncertainty intervals or recruitment suitability. No metric values were changed or combined into an overall player score. More passing activity or involvement is not automatically tactically preferable.

Run `python 71_fullback_percentile_comparisons.py` in Spyder or locally. [Evidence](../data/71_fullback_percentile_evidence.json) preserves pool membership, valid peer counts and lower/tied/higher counts. [Lesson](../lessons/0053-fullback-percentile-comparisons.html). Source: StatsBomb Open Data, **2019 Women's World Cup**, through saved audited profiles. Assisted worked exercise; no model fitting or video observation.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    players=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    fig,axes=plt.subplots(1,2,figsize=(11,5.5))
    for ax,p in zip(axes,players):
        for i,metric in enumerate(METRICS):
            for offset,ranks,color in ((-.18,p['percentiles_all_fullbacks'],'#969fa5'),(.18,p['percentiles_same_side'],'#24658a')):
                value=ranks[metric]['percentile']
                if value is None:continue
                ax.bar(i+offset,value,width=.34,color=color)
                ax.text(i+offset,value+1.3,f'{value:.1f}',ha='center',fontsize=10)
        n_all=p['percentiles_all_fullbacks'][METRICS[0]]['valid_pool_size']
        n_side=p['percentiles_same_side'][METRICS[0]]['valid_pool_size']
        label='right' if p['starting_side_group']=='right_only' else 'left'
        ax.set_title(f"{p['player_name']}\nAll fullbacks N={n_all}; exclusive {label}-back starts N={n_side}",fontsize=11)
        ax.set_xticks(range(2),['Completions\nper 90','Team completion\ninvolvement share'])
        ax.set_ylim(0,106);ax.set_yticks([0,25,50,75,100]);ax.set_ylabel('Percentile within stated pool')
        ax.spines[['top','right']].set_visible(False)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color='#969fa5',label='All selected fullbacks'),Patch(color='#24658a',label='Exclusive same-side starts')],
               loc='lower center',bbox_to_anchor=(.5,.11),ncol=2,frameon=False)
    fig.suptitle('Percentiles depend on the comparison group\n2019 Women’s World Cup · raw metric values unchanged',fontsize=14)
    fig.text(.5,.025,'Higher means a larger observed metric in the stated pool, not greater overall ability.\nDocumented other-player/tie convention. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.23,1,.88])
    fig.savefig(ROOT/'figures/65_fullback_percentile_comparisons.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/71_fullback_percentile_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/54_fullback_percentile_comparisons.md').write_text(render_report(evidence))
    print('Pools',{k:len(v) for k,v in evidence['peer_pools'].items()})
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p['player_name'],p['percentiles_all_fullbacks'],p['percentiles_same_side'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
