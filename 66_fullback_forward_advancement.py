"""Lesson 66: completed passes with an explicit pitch-length advancement rule."""
from decimal import Decimal
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_PATH='data/65_fullback_passing_per90_evidence.json'
PROTOCOL_PATH='data/66_forward_advancement_protocol.json'
SPEC=importlib.util.spec_from_file_location('passing65',ROOT/'65_fullback_passing_per90.py')
passing=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(passing)


def point(value):
    if (not isinstance(value,(list,tuple)) or len(value)!=2
            or any(type(v) not in (int,float) or not math.isfinite(v) for v in value)
            or not 0<=value[0]<=120 or not 0<=value[1]<=80):
        raise ValueError('Completed pass requires finite in-pitch start and end points')
    return value


def advancement(start,end,threshold):
    point(start);point(end)
    if type(threshold) not in (int,float) or not math.isfinite(threshold) or threshold<=0:
        raise ValueError('Threshold must be a positive finite number')
    gain=Decimal(str(end[0]))-Decimal(str(start[0]))
    return float(gain),gain>=Decimal(str(threshold))


def enrich_completions(ledger,events,threshold):
    lookup={e['id']:e for e in events}
    if len(lookup)!=len(events) or len(set(ledger['completed_ids']))!=len(ledger['completed_ids']):
        raise ValueError('Duplicate raw or selected pass identity')
    rows=[]
    for identifier in ledger['completed_ids']:
        event=lookup[identifier]
        if (event['type']['name']!='Pass' or event['team']['id']!=ledger['team_id']
                or event['player']['id']!=ledger['player_id'] or event['period'] not in (1,2,3,4)
                or event['possession_team']['id']!=event['team']['id']
                or 'outcome' in event['pass']
                or event['pass'].get('type',{}).get('name') in passing.RESTARTS):
            raise ValueError('Raw pass differs from the selected completed-pass definition')
        start=point(event['location']);end=point(event['pass']['end_location'])
        gain,qualifies=advancement(start,end,threshold)
        rows.append({'match_id':ledger['match_id'],'team_id':ledger['team_id'],
                     'player_id':ledger['player_id'],'pass_id':identifier,
                     'x':start[0],'y':start[1],'end_x':end[0],'end_y':end[1],
                     'x_gain':gain,'qualifies':qualifies})
    return rows


def summarize(player,rows):
    if len(rows)!=player['eligible_completed'] or player['duration_ms']<=0:
        raise ValueError('Completion coverage or selected minutes differ from source')
    count=sum(r['qualifies'] for r in rows)
    minutes=player['duration_ms']/60000
    return {**{k:player[k] for k in ('team_id','player_id','player_name','team_name','qualifying_match_ids','duration_ms','eligible_completed')},
            'minutes':minutes,'qualifying_completions':count,'qualifying_per90':count/minutes*90,
            'qualifying_share_pct':100*count/len(rows) if rows else None}


def build_evidence(allow_download=True):
    source=json.loads((ROOT/SOURCE_PATH).read_text())
    protocol=json.loads((ROOT/PROTOCOL_PATH).read_text())
    minutes=json.loads((ROOT/source['source_path']).read_text())
    records={m['match_id']:m['raw_input'] for m in minutes['match_audits']}
    groups={}
    for row in source['pass_ledger']:
        groups.setdefault(row['match_id'],[]).append(row)
    completions=[]
    for match_id,ledgers in groups.items():
        events=passing.time_module.cohort_module.raw.load_events(records[match_id],allow_download)
        for ledger in ledgers:
            completions.extend(enrich_completions(ledger,events,protocol['minimum_x_gain']))
    players=[]
    for player in source['players']:
        rows=[r for r in completions if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id'])]
        players.append(summarize(player,rows))
    examples=[]
    for identifier in (10178,15249):
        example=next((r for r in completions if r['player_id']==identifier and r['qualifies']),None)
        if example is not None:examples.append(example)
    return {'competition':source['competition'],'season':source['season'],'competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3: Statistical scouting','section':'Context: what to measure',
                             'url':'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure'},
            'source_path':SOURCE_PATH,'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'protocol_path':PROTOCOL_PATH,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL_PATH).read_bytes()).hexdigest(),
            'minimum_x_gain':protocol['minimum_x_gain'],'completions':completions,'players':players,
            'illustrative_ledger_examples':examples,
            'scope':protocol['limitations']}


def render_report(evidence):
    lines=[]
    for p in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        share=f"{p['qualifying_share_pct']:.1f}%" if p['qualifying_share_pct'] is not None else 'undefined'
        lines.append(f"- {p['team_name']} — {p['player_name']}: {p['qualifying_completions']}/{p['eligible_completed']} eligible completions meet the rule ({share}); {p['qualifying_per90']:.2f} per 90 over {p['minutes']:.1f} registered minutes.")
    rows='\n'.join(lines)
    names={p['player_id']:p['player_name'] for p in evidence['players']}
    examples='\n'.join(f"- {names[r['player_id']]}: ({r['x']}, {r['y']}) → ({r['end_x']}, {r['end_y']}); x gain {r['x_gain']}; pass ID {r['pass_id']}." for r in evidence['illustrative_ledger_examples'])
    return f'''# Fullback passing: substantial forward advancement

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30. Reading: [Soccermatics Lesson 3 — Statistical scouting, Context: what to measure](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure).

We enrich the unchanged lesson 65 completed-pass sample with observed start/end coordinates. The project rule counts a completion when **end_x − start_x ≥ {evidence['minimum_x_gain']}** on the 0–120 pitch-length scale. Teams act towards x=120 in these normalized coordinates. The threshold is in coordinate units, not metres or total pass length.

## All 35 profiles, alphabetical by team and name

{rows}

![Qualifying completed-pass maps for two familiar players](../figures/61_fullback_forward_advancement.png)

## Concrete recorded examples

{examples}

These are the first qualifying passes in the saved ledger for two familiar players, selected only to illustrate the rule. They are not representative samples or recommendations. Every qualifying pass for those two players is included in the plotted maps.

## Numerators, denominators and validation

Per 90 = qualifying completion count / the unchanged selected registered minutes × 90. Share = qualifying completions / all eligible completed passes × 100. The share is not pass completion percentage: failed attempts are not its denominator. A zero-completion player has an undefined share.

Every completed eligible pass is retained and checked against its raw event identity, team, player and completion status. Missing or invalid start/end coordinates stop enrichment; none is silently dropped or treated as zero gain. Decimal subtraction makes exact-threshold cases such as 84.6 → 104.6 count correctly. Existing non-restart, possession-team and known-outcome rules and selected fixtures remain unchanged.

## Interpretation

Toy examples: x=40 → 65 gains 25 and qualifies; x=70 → 75 gains five and does not; a sideways pass can be long yet have zero x gain. A pass from x=110 → 119 can be highly valuable near goal while failing this rule. This is a transparent spatial count, not a universal progressive-pass standard, line-breaking measure or action-value model.

We have added direction/context to activity, but not possession adjustment, pressure, defender lines, difficulty or actual role-duration adjustment. Starting zones affect opportunities to gain 20 units: a player already near goal has little room. Higher counts do not establish better ability or current recruitment suitability. This exercise uses already inspected historical data; no new model was trained.

## Reproduce

Run `python 66_fullback_forward_advancement.py` in Spyder or locally. [Protocol](../data/66_forward_advancement_protocol.json) · [Evidence](../data/66_fullback_advancement_evidence.json) · [Lesson](../lessons/0048-fullback-forward-advancement.html). Source: StatsBomb Open Data, **2019 Women's World Cup**, hash-checked archived events. Assisted worked exercise applying course ideas rather than reproducing a standard provider metric.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    from mplsoccer import Pitch
    players=[next(p for p in evidence['players'] if p['player_id']==i) for i in (10178,15249)]
    pitch=Pitch(pitch_type='statsbomb',line_color='#a3afb4')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    fig.set_layout_engine(None)
    for ax,player,color in zip(axes,players,('#24658a','#b77516')):
        pitch.draw(ax=ax)
        rows=[r for r in evidence['completions'] if r['player_id']==player['player_id'] and r['team_id']==player['team_id'] and r['qualifies']]
        if rows:
            pitch.arrows([r['x'] for r in rows],[r['y'] for r in rows],[r['end_x'] for r in rows],[r['end_y'] for r in rows],
                         color=color,width=1.1,headwidth=3,alpha=.65,ax=ax)
            pitch.scatter([r['x'] for r in rows],[r['y'] for r in rows],s=10,color=color,zorder=3,ax=ax)
        ax.set_title(f"{player['player_name']} · {player['qualifying_completions']} completions\n{player['qualifying_per90']:.2f} per 90 · {player['qualifying_share_pct']:.1f}% of eligible completions",fontsize=11)
    fig.suptitle('Completed passes gaining at least 20 pitch-length units\n2019 Women’s World Cup · both teams attack towards the right',fontsize=14,y=.96)
    fig.text(.5,.035,'Arrows: recorded start to end of every qualifying completion for these players.\nProject threshold, not a universal progression or player-ability measure. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.03,right=.97,bottom=.18,top=.76,wspace=.14)
    fig.savefig(ROOT/'figures/61_fullback_forward_advancement.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/66_fullback_advancement_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/49_fullback_forward_advancement.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p)
    plot_evidence(evidence)


if __name__=='__main__':
    main()
