"""Lesson 61: add supplied StatsBomb xG to the fixed defensive shot selection."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_PATH = 'data/60_france_defensive_corner_evidence.json'
SPEC = importlib.util.spec_from_file_location('defense60', ROOT/'60_france_defensive_corners.py')
defense = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(defense)


def probability(value):
    if type(value) not in (int,float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('Supplied xG must be a finite number between zero and one.')
    return float(value)


def enrich_match(match, events):
    lookup = {e['id']:e for e in events}
    if len(lookup)!=len(events):
        raise ValueError('Duplicate raw event ID')
    rows = []
    seen = set()
    for phase in match['phases']:
        corner = lookup[phase['corner_id']]
        if (corner['type']['name']!='Pass' or corner['pass'].get('type',{}).get('name')!='Corner'
                or corner['team']['name']!=match['attacking_team'] or corner['period']!=phase['period']):
            raise ValueError('Corner identity does not match defensive selection')
        for selected in phase['shots']:
            event = lookup[selected['shot_id']]
            if event['id'] in seen:
                raise ValueError('Repeated selected shot')
            seen.add(event['id'])
            if (event['type']['name']!='Shot' or event['team']['name']!=match['attacking_team']
                    or event['period']!=phase['period'] or event['period'] not in (1,2,3,4)
                    or event['shot']['type']['name']=='Penalty'):
                raise ValueError('Shot identity does not match defensive selection')
            goal = int(event['shot']['outcome']['name']=='Goal')
            if goal!=selected['goal']:
                raise ValueError('Saved goal label differs from raw event')
            xg = probability(event['shot']['statsbomb_xg'])  # Missing data must not become zero.
            x,y = event['location'][:2]
            if (type(x) not in (int,float) or type(y) not in (int,float)
                    or not math.isfinite(x) or not math.isfinite(y) or not 0<=x<=120 or not 0<=y<=80):
                raise ValueError('Shot location is outside the StatsBomb pitch')
            rows.append({'match_id':match['fixture']['match_id'],'corner_id':phase['corner_id'],
                         'shot_id':event['id'],'opponent':match['opponent'],
                         'period':event['period'],'minute':event['minute'],'second':event['second'],
                         'elapsed_seconds':selected['elapsed_seconds'],'x':x,'y':y,
                         'provider_xg':xg,'goal':goal,'body_part':event['shot']['body_part']['name'],
                         'outcome':event['shot']['outcome']['name']})
    if len(rows)!=match['phase_shots']:
        raise ValueError('Enrichment changed the number of selected shots')
    return rows


def summarize(shots, deliveries):
    positive = len({(s['match_id'],s['corner_id']) for s in shots})
    if deliveries < positive:
        raise ValueError('More shot-associated corners than deliveries')
    total = math.fsum(probability(s['provider_xg']) for s in shots)
    return {'deliveries':deliveries,'corners_with_shot':positive,'shots':len(shots),
            'shot_goals':sum(s['goal'] for s in shots),'provider_xg':total,
            'corner_shot_rate':positive/deliveries if deliveries else None,
            'shots_per_corner':len(shots)/deliveries if deliveries else None,
            'provider_xg_per_shot':total/len(shots) if shots else None,
            'provider_xg_per_corner':total/deliveries if deliveries else None}


def build_evidence(allow_download=True):
    source = json.loads((ROOT/SOURCE_PATH).read_text())
    shots = []
    matches = []
    for match in source['matches']:
        rows = enrich_match(match,defense.load_events(match['raw_input'],allow_download))
        shots.extend(rows)
        matches.append({'fixture':match['fixture'],'opponent':match['opponent'],
                        'raw_input':match['raw_input'],**summarize(rows,match['deliveries'])})
    return {'source_path':SOURCE_PATH,
            'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'xg_source':'Raw shot.statsbomb_xg from the recorded StatsBomb snapshots, not our educational distance model. Provider model version is not identified in these snapshots.',
            'matches':matches,'shots':shots,
            'pooled':summarize(shots,source['pooled']['deliveries']),
            'display_rule':'Original StatsBomb coordinates; all attacking teams face the top in vertical pitch panels. Circle area = supplied xG * 1800 points squared. Every selected shot displayed.',
            'scope':'Same four defensive corner-phase shots and 15 opposition deliveries. Descriptive provider-xG enrichment, no model fitting, new selection, causal attribution or independent validation.'}


def render_report(evidence):
    pooled = evidence['pooled']
    rows = '\n'.join(f"- {s['opponent']}, period {s['period']} at {s['minute']:02d}:{s['second']:02d}: "
                     f"{s['provider_xg']:.6f} xG; {s['body_part']}; {s['outcome']}."
                     for s in evidence['shots'])
    addition = ' + '.join(f"{s['provider_xg']:.9f}" for s in evidence['shots'])
    return f'''# Quality of the corner-phase shots France allowed

The unchanged five-match defensive selection contains **{pooled['shots']} shots from {pooled['deliveries']} opposition corners**, with **{pooled['shot_goals']} shot goals**. Their supplied StatsBomb xG sums to **{pooled['provider_xg']:.6f}**.

{rows}

Calculation: {addition} = {pooled['provider_xg']:.9f} xG. Values displayed here are rounded; saved evidence preserves the supplied numerical values.

![The four selected opposition shots and their supplied xG](../figures/56_defensive_corner_shot_quality.png)

## Frequency, quality and outcome

- Corners associated with a shot: {pooled['corners_with_shot']}/{pooled['deliveries']} = {pooled['corner_shot_rate']*100:.1f}%.
- Average supplied xG per shot: {pooled['provider_xg']:.6f}/{pooled['shots']} = {pooled['provider_xg_per_shot']:.6f}.
- Supplied xG per corner faced: {pooled['provider_xg']:.6f}/{pooled['deliveries']} = {pooled['provider_xg_per_corner']:.6f}.
- Actual shot goals in these phases: {pooled['shot_goals']}.

The frequency counts how often a corner was associated with a shot. Mean xG describes the provider-estimated scoring chance of the selected shots. Goals record what actually happened. None is a substitute for the other two.

The identity is xG per corner = shots per corner × mean xG per shot. Use the number of shots here, not the number of positive corners: they happen to both be four in this sample, but one corner can produce several shots. The xG-per-corner number is an average expected-goal total per observed delivery, not generally the probability that a corner produces at least one goal.

## What the xG numbers mean

These are the existing provider's shot.statsbomb_xg values. We did not fit, improve or evaluate our earlier educational model here. A value around 0.147 is the provider's estimated 14.7% scoring probability for that shot, not a known true chance or a guaranteed outcome. The exact provider model version is not supplied in these snapshots.

Summed xG is an expected-goal total under those shot estimates, not the probability of at least one goal. Zero actual goals alongside about 0.38 xG does not prove exceptional defending or goalkeeper performance. Two of these shots were blocked and two saved. This sample is small, unadjusted and uses only the bounded phase definition; later chances and penalties are outside it. No new footage was reviewed.

## Reproduce

Run `python 61_defensive_corner_shot_quality.py` locally or in Spyder. All selected shot IDs are preserved and checked against the original hash-verified event files. Missing or invalid xG stops enrichment rather than becoming zero. No-shot matches have zero selected xG and an undefined mean xG per shot.

[Saved evidence](../data/61_defensive_corner_quality_evidence.json) · [Short lesson](../lessons/0043-defensive-corner-shot-quality.html). Assisted worked extension, not independent proficiency.

Source: [StatsBomb Open Data](https://github.com/statsbomb/open-data). Definition reference: [Hudl StatsBomb expected goals glossary](https://support.hudl.com/s/article/expected-goals?language=en_US&topic=Statsbomb_Global_Football_Data_Glossary).
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    from mplsoccer import VerticalPitch
    shots = evidence['shots']
    if len(shots)!=4:
        raise ValueError('This four-panel teaching figure expects the fixed four-shot selection')
    if not all(60<=s['x']<=120 for s in shots):
        raise ValueError('Half-pitch would hide a selected shot')
    pitch = VerticalPitch(pitch_type='statsbomb',half=True,line_color='#9ba7ad')
    fig,axes = plt.subplots(2,2,figsize=(10,10.5))
    fig.set_layout_engine(None)
    for ax,shot in zip(axes.flat,shots):
        pitch.draw(ax=ax)
        pitch.scatter([shot['x']],[shot['y']],s=[shot['provider_xg']*1800],
                      color='#24658a',edgecolors='white',zorder=3,ax=ax)
        name=shot['opponent'].replace(" Women's",'')
        ax.set_title(f"{name} · P{shot['period']} {shot['minute']:02d}:{shot['second']:02d}\n"
                     f"{shot['provider_xg']:.3f} supplied xG · {shot['outcome']}",fontsize=11)
    fig.suptitle('The four corner-phase shots France allowed\nFive 2019 World Cup fixtures · opponents attack towards the top',fontsize=14)
    fig.text(.5,.025,'Circle area represents supplied StatsBomb xG, not our practice model.\nSame fixed shot selection; no goals in these four shots. Source: StatsBomb Open Data.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.04,right=.96,bottom=.10,top=.83,hspace=.46,wspace=.16)
    fig.savefig(ROOT/'figures/56_defensive_corner_shot_quality.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/61_defensive_corner_quality_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/44_defensive_corner_shot_quality.md').write_text(render_report(evidence))
    print(evidence['pooled'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
