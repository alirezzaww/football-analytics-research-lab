"""Lesson 67: audit starting-area context for the fixed forward-advancement rule."""
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_PATH='data/66_fullback_advancement_evidence.json'
THIRDS=('Defensive third','Middle third','Attacking third')


def third(x):
    if type(x) not in (int,float) or not math.isfinite(x) or not 0<=x<=120:
        raise ValueError('Starting x must be a finite coordinate in 0–120')
    return THIRDS[0] if x<40 else THIRDS[1] if x<80 else THIRDS[2]


def has_coordinate_room(x,threshold):
    third(x)
    if type(threshold) not in (int,float) or not math.isfinite(threshold) or threshold<=0:
        raise ValueError('Threshold must be a positive finite number')
    return Decimal('120')-Decimal(str(x))>=Decimal(str(threshold))


def group_player(player,rows,threshold):
    if (len(rows)!=player['eligible_completed']
            or sum(r['qualifies'] for r in rows)!=player['qualifying_completions']
            or len({(r['match_id'],r['pass_id']) for r in rows})!=len(rows)):
        raise ValueError('Source pass coverage differs or contains duplicate identities')
    groups=[]
    no_room=[]
    for row in rows:
        third(row['x'])
        if (row['team_id'],row['player_id'])!=(player['team_id'],player['player_id']):
            raise ValueError('Pass assigned to wrong player/team')
        if not has_coordinate_room(row['x'],threshold):
            if row['qualifies']:
                raise ValueError('Qualifying pass violates the pitch-length ceiling')
            no_room.append({'match_id':row['match_id'],'pass_id':row['pass_id']})
    for label in THIRDS:
        selected=[r for r in rows if third(r['x'])==label]
        count=sum(r['qualifies'] for r in selected)
        groups.append({'third':label,'completions':len(selected),'qualifying_completions':count,
                       'share_of_player_completions_pct':100*len(selected)/len(rows) if rows else None,
                       'within_third_qualifying_share_pct':100*count/len(selected) if selected else None,
                       'pass_keys':[{'match_id':r['match_id'],'pass_id':r['pass_id']} for r in selected]})
    return {**player,'starting_thirds':groups,'no_coordinate_room_completions':len(no_room),
            'no_coordinate_room_pct':100*len(no_room)/len(rows) if rows else None,
            'no_coordinate_room_keys':no_room}


def build_evidence():
    source=json.loads((ROOT/SOURCE_PATH).read_text())
    players=[]
    for player in source['players']:
        selected=[r for r in source['completions'] if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id'])]
        players.append(group_player(player,selected,source['minimum_x_gain']))
    return {'competition':source['competition'],'season':source['season'],
            'competition_id':source['competition_id'],'season_id':source['season_id'],
            'course_reading':source['course_reading'],'source_path':SOURCE_PATH,
            'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'minimum_x_gain':source['minimum_x_gain'],
            'third_rule':'0≤x<40 defensive; 40≤x<80 middle; 80≤x≤120 attacking. These are coarse project starting-area groups, not equal tactical situations.',
            'room_rule':'Geometric room exists only when 120−start_x ≥ the fixed threshold. For threshold 20, x=100 can qualify; x>100 cannot. This says nothing about feasible passing options.',
            'players':players,
            'scope':'Unchanged completed-pass sample, rule, minutes and per-90 results. Descriptive starting-area stratification and a geometric ceiling check, not causal adjustment, a new opportunity-rate model or player ranking.'}


def render_report(evidence):
    lines=[]
    for player in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        counts='; '.join(f"{g['third']}: {g['qualifying_completions']}/{g['completions']}" for g in player['starting_thirds'])
        lines.append(f"- {player['team_name']} — {player['player_name']}: {counts}. No coordinate room: {player['no_coordinate_room_completions']}/{player['eligible_completed']} completions.")
    rows='\n'.join(lines)
    return f'''# Starting-area context for forward advancement

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30. Reading: [Soccermatics Lesson 3 — Statistical scouting, Context: what to measure](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure).

The fixed measure requires a completed pass to gain at least 20 units along a 0–120 pitch. A pass starting beyond x=100 cannot qualify because even the maximum end_x=120 leaves a gain below 20. A pass at x=100 can still qualify if it ends exactly at x=120. This is a mathematical boundary, not evidence of a feasible passing option or poor play.

We retain every source completion and split by starting third. Within-third share uses the number of completed passes starting in that third as its denominator. It does not use pass attempts or minutes. The original overall shares and per-90 rates remain unchanged.

![Starting-area distributions and within-third shares](../figures/62_fullback_starting_area_context.png)

## A concrete comparison

Bronze has 20/350 completions starting beyond x=100 (5.7%); Majri has 20/172 (11.6%). The same count is a different fraction of their activity. Those passes cannot meet our fixed rule, but they can still be valuable.

In the middle third, Bronze has 21/174 qualifying completions (12.1%) and Majri 13/104 (12.5%). This is a more specific descriptive comparison than mixing all starting areas; it does not make opponents, starting side, exact location, pressure or passing options equal. The small difference does not establish an ability difference or explain the overall difference causally. No significance test was run.

## All 35 profiles

Each fraction below is qualifying completions divided by eligible completions in the stated starting third. Zero exposure means an undefined rate, not 0%.

{rows}

## What this audit does not do

The three groups are broad project choices aligned with pitch thirds. We do not refit the metric, remove near-goal completions from the original denominator, produce a standardized ranking, or call every completion with geometric room a genuine football opportunity. Team possession, roles and difficulty remain unadjusted. Matching a coarse third is not matching the full situation. A future choice to change the definition would need to be documented and checked separately.

## Reproduce

Run `python 67_fullback_starting_area_context.py` locally or in Spyder. It uses the saved lesson 66 ledger without downloading data. [Evidence](../data/67_fullback_starting_context_evidence.json) preserves group membership through match/pass keys. [Lesson](../lessons/0049-fullback-starting-area-context.html). Source: StatsBomb Open Data, **2019 Women's World Cup**, via the unchanged hash-linked completed-pass evidence. Assisted worked exercise, not independent proficiency.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    selected=[next(p for p in evidence['players'] if p['player_id']==i) for i in (10178,15249)]
    fig,axes=plt.subplots(1,2,figsize=(12,5.5))
    for ax,field,title,ylabel in (
        (axes[0],'share_of_player_completions_pct','Where the completions start','Share of player completions (%)'),
        (axes[1],'within_third_qualifying_share_pct','Qualifying share within each starting third','Qualifying completions / third completions (%)')):
        for i,(player,color) in enumerate(zip(selected,('#24658a','#b77516'))):
            positions=[j+(i-.5)*.34 for j in range(3)]
            values=[g[field] for g in player['starting_thirds']]
            for x,g,value in zip(positions,player['starting_thirds'],values):
                if value is None:continue
                ax.bar(x,value,width=.32,color=color,label=player['player_name'] if x==positions[0] else None)
                denominator=player['eligible_completed'] if field.startswith('share_of') else g['completions']
                numerator=g['completions'] if field.startswith('share_of') else g['qualifying_completions']
                ax.text(x,value+.5,f'{numerator}/{denominator}',ha='center',fontsize=8)
        ax.set_xticks(range(3),['Defensive','Middle','Attacking'])
        ax.set_xlabel('Starting third');ax.set_ylabel(ylabel,fontsize=9);ax.set_title(title,fontsize=11)
        ax.set_ylim(0,75 if field.startswith('share_of') else 27)
        ax.spines[['top','right']].set_visible(False)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.11),ncol=2,frameon=False)
    fig.suptitle('Starting areas change the context of a passing metric\n2019 Women’s World Cup · unchanged completed-pass sample',fontsize=14)
    fig.text(.5,.025,'Fixed rule: completed pass gains ≥20 on the 0–120 length scale. Starts beyond x=100 cannot qualify.\nCoarse starting-area groups do not isolate ability. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.21,1,.88])
    fig.savefig(ROOT/'figures/62_fullback_starting_area_context.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/67_fullback_starting_context_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/50_fullback_starting_area_context.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p['player_name'],p['no_coordinate_room_completions'],p['no_coordinate_room_pct'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
