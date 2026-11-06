"""Lesson 68: compare a near-goal rule with the fixed advancement definition."""
from decimal import Decimal
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_PATH='data/66_fullback_advancement_evidence.json'
CONTEXT_PATH='data/67_fullback_starting_context_evidence.json'
PROTOCOL_PATH='data/68_adaptive_advancement_protocol.json'
SPEC=importlib.util.spec_from_file_location('advance66',ROOT/'66_fullback_forward_advancement.py')
original=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(original)


def compare_pass(row,base_gain=20,fraction=.5):
    original.point([row['x'],row['y']]);original.point([row['end_x'],row['end_y']])
    if (type(base_gain) not in (int,float) or not math.isfinite(base_gain) or base_gain<=0
            or type(fraction) not in (int,float) or not math.isfinite(fraction) or not 0<fraction<=1):
        raise ValueError('Expected a positive base gain and fraction in (0,1]')
    gain=Decimal(str(row['end_x']))-Decimal(str(row['x']))
    required=min(Decimal(str(base_gain)),Decimal(str(fraction))*(Decimal('120')-Decimal(str(row['x']))))
    fixed=gain>=Decimal(str(base_gain))
    if type(row['qualifies']) is not bool or row['qualifies']!=fixed:
        raise ValueError('Original classification differs from the documented fixed rule')
    alternative=gain>0 and gain>=required
    if fixed and not alternative:
        raise ValueError('Alternative unexpectedly removed a fixed-rule pass')
    return {**{k:row[k] for k in ('match_id','team_id','player_id','pass_id')},
            'fixed_qualifies':fixed,'alternative_qualifies':alternative,
            'required_x_gain':float(required),'newly_included':alternative and not fixed}


def summarize(player,rows):
    if (len(rows)!=player['eligible_completed'] or player['duration_ms']<=0
            or sum(r['fixed_qualifies'] for r in rows)!=player['qualifying_completions']):
        raise ValueError('Comparison coverage or original count differs')
    count=sum(r['alternative_qualifies'] for r in rows)
    added=sum(r['newly_included'] for r in rows)
    if count!=player['qualifying_completions']+added:
        raise ValueError('Definition change does not reconcile')
    return {**player,'alternative_completions':count,'alternative_per90':count/(player['duration_ms']/60000)*90,
            'alternative_share_pct':100*count/len(rows) if rows else None,
            'newly_included_completions':added}


def build_evidence():
    source=json.loads((ROOT/SOURCE_PATH).read_text())
    protocol=json.loads((ROOT/PROTOCOL_PATH).read_text())
    if source['minimum_x_gain']!=protocol['base_x_gain']:
        raise ValueError('Fixed definition differs from the chosen comparison')
    comparisons=[compare_pass(r,protocol['base_x_gain'],protocol['remaining_x_fraction']) for r in source['completions']]
    players=[]
    for player in source['players']:
        rows=[r for r in comparisons if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id'])]
        players.append(summarize(player,rows))
    lookup={(r['match_id'],r['pass_id']):r for r in source['completions']}
    examples=[]
    for identifier in (10178,15249):
        changed=next((r for r in comparisons if r['player_id']==identifier and r['newly_included']),None)
        if changed:
            examples.append({**lookup[(changed['match_id'],changed['pass_id'])],**changed})
    return {'competition':source['competition'],'season':source['season'],'competition_id':72,'season_id':30,
            'course_reading':source['course_reading'],
            'sources':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in (SOURCE_PATH,CONTEXT_PATH)],
            'protocol_path':PROTOCOL_PATH,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL_PATH).read_bytes()).hexdigest(),
            'base_x_gain':protocol['base_x_gain'],'remaining_x_fraction':protocol['remaining_x_fraction'],
            'comparisons':comparisons,'players':players,'illustrative_new_passes':examples,
            'summary':{'completed_passes':len(comparisons),'fixed_qualifying':sum(r['fixed_qualifies'] for r in comparisons),
                       'alternative_qualifying':sum(r['alternative_qualifies'] for r in comparisons),
                       'newly_included':sum(r['newly_included'] for r in comparisons)},
            'scope':protocol['scope']}


def render_report(evidence):
    lines=[]
    for p in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        lines.append(f"- {p['team_name']} — {p['player_name']}: fixed {p['qualifying_completions']} ({p['qualifying_per90']:.2f}/90); alternative {p['alternative_completions']} ({p['alternative_per90']:.2f}/90); newly included {p['newly_included_completions']}.")
    rows='\n'.join(lines)
    examples='\n'.join(f"- Player ID {r['player_id']}, pass {r['pass_id']} in match {r['match_id']}: x={r['x']} → {r['end_x']}, gain {r['x_gain']}; alternative requires {r['required_x_gain']}." for r in evidence['illustrative_new_passes'])
    totals=evidence['summary']
    return f'''# Test a smaller forward-gain requirement near goal

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30. Reading: [Soccermatics Lesson 3 — Statistical scouting, Context: what to measure](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure).

The user identified that the rule should account for near-goal situations. We compare a documented alternative with the original fixed 20-unit rule, keeping all {totals['completed_passes']} source completions, players, fixtures and registered minutes unchanged.

## Alternative definition

Required x gain = min(20, 0.5 × (120 − start_x)). A completed eligible pass must advance by a strictly positive amount and meet that requirement. Through x=80, the requirement stays 20. At x=90 it becomes 15; at x=100 it is 10; at x=110 it is five. At x=120, no positive in-pitch gain is possible, so no pass qualifies. Decimal comparisons include the exact threshold.

This is a relative reduction in remaining pitch length along x, not Euclidean distance to goal, total pass length or expected threat. The fraction one half is a chosen exercise setting, not an optimized or universal standard.

## Comparison results

Across the whole selected sample: fixed rule {totals['fixed_qualifying']}; alternative {totals['alternative_qualifying']}; added {totals['newly_included']}. All fixed-rule positives remain positive under the alternative. Additional passes start beyond x=80 and have positive x gain. More counted passes is an expected consequence of the definition, not validation of quality.

![Required gain and observed per-90 changes](../figures/63_adaptive_forward_advancement.png)

{rows}

## Recorded examples newly included

{examples}

The examples are the first newly included ledger pass for each familiar player, not representative samples. Every pass's two classifications and required gain are saved. Earlier lesson results and files remain unchanged.

## What we learned

The original metric had a geometric blind spot beyond x=100; this alternative allows some advancing passes there to count. It still misses valuable sideways/backward passes, ignores pressure and defender lines, and may reward tiny x gains extremely close to goal. A pass can be a good decision without meeting either rule. Neither definition has been validated as an action-value measure or shown to identify better players. We did not search fractions, train a model or evaluate against independent pass-value labels. This is definition sensitivity on already inspected data.

## Reproduce

Run `python 68_adaptive_forward_advancement.py` in Spyder or locally. [Protocol](../data/68_adaptive_advancement_protocol.json) · [Evidence](../data/68_adaptive_advancement_evidence.json) · [Lesson](../lessons/0050-adaptive-forward-advancement.html). Source: StatsBomb Open Data, **2019 Women's World Cup**, via saved hash-linked pass evidence. Assisted worked extension of the user's idea.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,5.5))
    x=list(range(121))
    base=evidence['base_x_gain'];fraction=evidence['remaining_x_fraction']
    axes[0].plot(x,[base]*len(x),color='#969fa5',linestyle='--',label='Fixed rule')
    axes[0].plot(x,[min(base,fraction*(120-v)) for v in x],color='#24658a',label='Alternative')
    axes[0].scatter([110],[5],color='#24658a')
    axes[0].annotate('Start 110 → require 5',xy=(110,5),xytext=(35,7),arrowprops={'arrowstyle':'->'},fontsize=9)
    axes[0].set_xlabel('Starting x (0–120 coordinate units)');axes[0].set_ylabel('Required forward x gain (units)')
    axes[0].set_title('What changes in the rule?',fontsize=11)
    axes[0].set_xlim(0,120);axes[0].set_ylim(0,23);axes[0].legend(frameon=False,fontsize=9)
    players=[next(p for p in evidence['players'] if p['player_id']==i) for i in (10178,15249)]
    for i,p in enumerate(players):
        for offset,field,count_field,color in ((-.18,'qualifying_per90','qualifying_completions','#969fa5'),
                                                (.18,'alternative_per90','alternative_completions','#24658a')):
            axes[1].bar(i+offset,p[field],width=.34,color=color)
            axes[1].text(i+offset,p[field]+.08,f"{p[field]:.2f}\n(n={p[count_field]})",ha='center',fontsize=9)
    axes[1].set_xticks(range(2),[p['player_name'] for p in players]);axes[1].set_ylabel('Qualifying completions per 90 minutes')
    axes[1].set_ylim(0,max(p['alternative_per90'] for p in players)*1.3)
    axes[1].set_title('Same passes and minutes, different definition',fontsize=11)
    for ax in axes:ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Near-goal definition sensitivity · 2019 Women’s World Cup',fontsize=14)
    fig.text(.5,.025,'Alternative: positive gain ≥ min(20, half the remaining x distance). At x=120 no pass qualifies.\nMore counted passes does not prove a better metric. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.12,1,.91])
    fig.savefig(ROOT/'figures/63_adaptive_forward_advancement.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/68_adaptive_advancement_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/51_adaptive_forward_advancement.md').write_text(render_report(evidence))
    print(evidence['summary'])
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p['player_name'],p['qualifying_completions'],p['alternative_completions'],p['alternative_per90'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
