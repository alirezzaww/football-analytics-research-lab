"""Lesson 62: inspect recorded positions in the same four shot freeze frames."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_PATH = 'data/61_defensive_corner_quality_evidence.json'
GOAL_POSTS = [[120.0,36.0],[120.0,44.0]]
SPEC = importlib.util.spec_from_file_location('quality61',ROOT/'61_defensive_corner_shot_quality.py')
quality = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quality)


def point(value):
    if (not isinstance(value,(list,tuple)) or len(value)!=2
            or any(type(v) not in (int,float) or not math.isfinite(v) for v in value)
            or not 0<=value[0]<=120 or not 0<=value[1]<=80):
        raise ValueError('Expected a finite in-pitch StatsBomb x,y point')
    return tuple(float(v) for v in value)


def in_goal_triangle(location,shot_location):
    """Closed triangle from shot origin to (120,36) and (120,44)."""
    x,y = point(location)
    sx,sy = point(shot_location)
    if sx>=120:
        raise ValueError('Goal-line shot makes this triangle degenerate')
    if x<sx-1e-9 or x>120+1e-9:
        return False
    fraction = (x-sx)/(120-sx)
    lower = sy+fraction*(36-sy)
    upper = sy+fraction*(44-sy)
    return lower-1e-9<=y<=upper+1e-9


def enrich_frame(selected,event):
    if (event['id']!=selected['shot_id'] or event['type']['name']!='Shot'
            or event['team']['name']!=selected['opponent']
            or point(event['location'][:2])!=point([selected['x'],selected['y']])
            or event['period']!=selected['period']
            or event['shot']['statsbomb_xg']!=selected['provider_xg']):
        raise ValueError('Raw event differs from selected shot')
    frame = event['shot'].get('freeze_frame')
    if frame is None or frame==[]:
        return {**selected,'frame_available':False,'players':[],
                'recorded_players':None,'recorded_defending_outfield':None,
                'defending_outfield_in_triangle':None,'recorded_defending_keepers':None,
                'defending_keepers_in_triangle':None}
    if not isinstance(frame,list):
        raise ValueError('Freeze frame must be a list')
    players = []
    ids = set()
    for row in frame:
        if type(row['teammate']) is not bool:
            raise ValueError('Freeze-frame teammate must be a boolean')
        identifier = row['player']['id']
        if identifier in ids:
            raise ValueError('Duplicate player ID in frame')
        ids.add(identifier)
        x,y = point(row['location'])
        role = row['position']['id']
        if type(role) is not int or not 1<=role<=25:
            raise ValueError('Expected recorded player position ID 1–25')
        players.append({'player_id':identifier,'name':row['player']['name'],
                        'x':x,'y':y,'teammate':row['teammate'],'is_goalkeeper':role==1,
                        'in_goal_triangle':in_goal_triangle([x,y],[selected['x'],selected['y']])})
    defenders = [p for p in players if not p['teammate'] and not p['is_goalkeeper']]
    keepers = [p for p in players if not p['teammate'] and p['is_goalkeeper']]
    return {**selected,'frame_available':True,'players':players,'recorded_players':len(players),
            'recorded_defending_outfield':len(defenders),
            'defending_outfield_in_triangle':sum(p['in_goal_triangle'] for p in defenders),
            'recorded_defending_keepers':len(keepers),
            'defending_keepers_in_triangle':sum(p['in_goal_triangle'] for p in keepers)}


def build_evidence(allow_download=True):
    source = json.loads((ROOT/SOURCE_PATH).read_text())
    records = {m['fixture']['match_id']:m['raw_input'] for m in source['matches']}
    lookups = {key:{e['id']:e for e in quality.defense.load_events(record,allow_download)}
               for key,record in records.items()}
    shots = [enrich_frame(s,lookups[s['match_id']][s['shot_id']]) for s in source['shots']]
    return {'source_path':SOURCE_PATH,
            'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'raw_inputs':list(records.values()),'goal_posts':GOAL_POSTS,
            'rule':'Count recorded defending outfield player centres in the closed 2D triangle from shot location to goalposts (120,36) and (120,44); numerical tolerance 1e-9. Goalkeepers (position ID 1) counted separately. teammate is relative to the shooting team.',
            'shots':shots,
            'scope':'Same four opposition corner-phase shots. Recorded shot snapshots, not continuous tracking or video. Missing/empty frames have undefined counts. Geometric presence is not a verified block, pressure measure or causal explanation of supplied xG.'}


def render_report(evidence):
    lines = []
    for shot in evidence['shots']:
        if not shot['frame_available']:
            lines.append(f"- {shot['opponent']}: frame unavailable; counts undefined.")
            continue
        lines.append(f"- {shot['opponent']}: {shot['recorded_players']} recorded frame players; "
                     f"{shot['defending_outfield_in_triangle']}/{shot['recorded_defending_outfield']} recorded defending outfield players inside the triangle; "
                     f"{shot['defending_keepers_in_triangle']}/{shot['recorded_defending_keepers']} recorded defending goalkeepers inside. "
                     f"Supplied xG {shot['provider_xg']:.3f}; {shot['outcome']}.")
    rows = '\n'.join(lines)
    return f'''# Defensive context at the moment of the shot

We joined the same four selected shot IDs to their recorded StatsBomb shot.freeze_frame arrays. We have not added tracking data or watched footage.

{rows}

![Recorded player positions and the drawn goal triangle](../figures/57_defensive_shot_freeze_frames.png)

## Definition

The drawn triangle connects the shot origin to goalposts (120,36) and (120,44) in the StatsBomb coordinate system, matching the installed mplsoccer StatsBomb pitch dimensions. We count recorded player centres on or inside that closed triangle, with numerical tolerance 1e-9. This is a transparent project calculation inspired by the goal-cone concept, not a claim to reproduce the provider's exact feature implementation.

teammate=True means a teammate of the shooter: an opposition attacker in this defensive study. teammate=False means a French player. Recorded position ID 1 identifies goalkeepers, counted separately from outfield defenders. The shooter is drawn at the shot origin as a star; the frame need not include the shooter as a separate player record. Every supplied frame player is shown.

## What this adds—and what it cannot establish

We can see recorded French player positions around each attempt, and whether their centres lie geometrically between the shot and the goalmouth. These counts do not prove a player was able to block the ball. Body size, movement, ball height, timing and the actual shot trajectory are not modelled. Three attempts were headers, making a flat ground-position diagram particularly incomplete.

Frames contain relevant recorded players, not a guaranteed complete set of everyone on the pitch. Different recorded counts must not be interpreted as players missing from the team or proof of a defensive overload. Missing/empty frames produce undefined counts, not zeros. A recorded frame with no qualifying defender is a different case.

We have four selected shots, no comparison model and no controlled experiment. We cannot attribute their xG differences to this count, infer assigned marking responsibilities, or grade defenders from it. The feature describes shot-time context, not pre-corner shape or live movement. No new model was trained.

## Reproduce

Run `python 62_defensive_shot_freeze_frames.py` in Spyder or locally. The existing raw snapshot hashes are checked. [Saved evidence](../data/62_defensive_freeze_frame_evidence.json) preserves each recorded player position and triangle membership. [Short lesson](../lessons/0044-defensive-shot-freeze-frames.html). This worked assignment was assisted.

Primary sources: [StatsBomb freeze-frame explanation](https://blogarchive.statsbomb.com/news/statsbomb-data-case-studies-freeze-frames-and-defender-locations/) and [Open Data specification, Appendix 3](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Football source: StatsBomb Open Data. Geometry labels describe this project's explicit calculation.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon
    from mplsoccer import VerticalPitch
    shots=evidence['shots']
    if len(shots)!=4 or not all(s['frame_available'] for s in shots):
        raise ValueError('This teaching figure expects the fixed four available frames')
    lower=min(95,min(p['x'] for s in shots for p in s['players'])-2,min(s['x'] for s in shots)-2)
    pitch=VerticalPitch(pitch_type='statsbomb',half=True,line_color='#9ba7ad')
    if pitch.dim.right!=120 or {pitch.dim.goal_bottom,pitch.dim.goal_top}!={36,44}:
        raise ValueError('Pitch geometry differs from the documented goal posts')
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    fig.set_layout_engine(None)
    for ax,shot in zip(axes.flat,shots):
        pitch.draw(ax=ax)
        ax.set_ylim(lower,123)
        ax.add_patch(Polygon([(shot['y'],shot['x']),(36,120),(44,120)],
                             facecolor='#b77516',edgecolor='#b77516',alpha=.15,zorder=2))
        for p in shot['players']:
            color='#24658a' if p['teammate'] else '#b77516'
            marker='o'
            if not p['teammate'] and p['is_goalkeeper']:
                color='#446b57';marker='s'
            pitch.scatter([p['x']],[p['y']],s=65,c=color,marker=marker,
                          edgecolors='black' if p['in_goal_triangle'] and not p['teammate'] else 'white',
                          linewidths=.7,zorder=3,ax=ax)
        pitch.scatter([shot['x']],[shot['y']],s=170,marker='*',c='#172d3b',edgecolors='white',zorder=4,ax=ax)
        name=shot['opponent'].replace(" Women's",'')
        ax.set_title(f"{name} · {shot['provider_xg']:.3f} supplied xG\n"
                     f"Recorded France outfield inside triangle: {shot['defending_outfield_in_triangle']}",fontsize=10)
    fig.suptitle('Where were the recorded players when the shot was taken?\nSame four opposition corner-phase shots · attacking towards the top',fontsize=14,y=.97)
    legend=[Line2D([],[],marker='o',linestyle='',color='#24658a',label='Opposition attacker'),
            Line2D([],[],marker='o',linestyle='',color='#b77516',label='France outfield'),
            Line2D([],[],marker='s',linestyle='',color='#446b57',label='France goalkeeper'),
            Line2D([],[],marker='*',linestyle='',color='#172d3b',label='Shooter')]
    fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.085),ncol=4,frameon=False,fontsize=9)
    fig.text(.5,.025,'Shaded triangle: shot origin to goalposts; black outline highlights recorded France players inside.\nSnapshots are not full tracking. Geometric presence does not prove a block. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.04,right=.96,bottom=.19,top=.81,hspace=.72,wspace=.18)
    fig.savefig(ROOT/'figures/57_defensive_shot_freeze_frames.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/62_defensive_freeze_frame_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/45_defensive_shot_freeze_frames.md').write_text(render_report(evidence))
    for shot in evidence['shots']:
        print(shot['opponent'],'outfield in triangle',shot['defending_outfield_in_triangle'],
              'recorded outfield',shot['recorded_defending_outfield'],'keeper in triangle',shot['defending_keepers_in_triangle'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
