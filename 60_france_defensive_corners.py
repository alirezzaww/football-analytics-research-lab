"""Lesson 60: count opposition corner phases against France using the existing rule."""
import hashlib
import importlib.util
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
SOURCE_PATH = 'data/38_france_corner_study_evidence.json'


def helper(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT/filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scanner = helper('defensive_phase36', '36_corner_phase_analysis.py')
study_helper = helper('defensive_pool38', '38_france_tournament_corners.py')


def analyze_team(events, attacking_team, protocol):
    """Count one attacking team's corners; its opponent is defending."""
    if len({e['id'] for e in events}) != len(events):
        raise ValueError('Duplicate raw event ID')
    if len({e['index'] for e in events}) != len(events):
        raise ValueError('Duplicate raw event index')
    events = sorted(events, key=lambda e: e['index'])
    included = {e['id']: {'goal': int(e['shot']['outcome']['name']=='Goal'),
                         'model_probability': None}
                for e in events if e['type']['name']=='Shot'
                and e['period'] in protocol['periods_included']
                and e['team']['name']==attacking_team
                and e['shot']['type']['name']!='Penalty'}
    corners = [e for e in events if e['type']['name']=='Pass'
               and e['period'] in protocol['periods_included']
               and e['team']['name']==attacking_team
               and e['pass'].get('type',{}).get('name')=='Corner']
    phases = []
    assigned = set()
    for corner in corners:
        result = scanner.phase_after(corner, events, included, protocol)
        for shot in result['shots']:
            if shot['shot_id'] in assigned:
                raise ValueError('Shot assigned to multiple corner phases')
            assigned.add(shot['shot_id'])
            del shot['model_probability']
        phases.append({'corner_id':corner['id'], 'period':corner['period'],
                       'minute':corner['minute'], 'second':corner['second'], **result})
    positive = sum(bool(p['shots']) for p in phases)
    return {'attacking_team':attacking_team, 'deliveries':len(phases),
            'corners_with_phase_shot':positive,
            'phase_shots':sum(len(p['shots']) for p in phases),
            'phase_shot_goals':sum(s['goal'] for p in phases for s in p['shots']),
            'phase_shot_rate':positive/len(phases) if phases else None,
            'extra_time_deliveries':sum(p['period'] in (3,4) for p in phases),
            'phases':phases}


def load_events(record, allow_download=True):
    path = ROOT/record['relative_path']
    if not path.exists():
        if not allow_download:
            raise FileNotFoundError(path)
        with urlopen(record['source_url'], timeout=60) as response:
            payload = response.read()
        if hashlib.sha256(payload).hexdigest()!=record['sha256']:
            raise ValueError('Downloaded events differ from the recorded source hash')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:
        raise ValueError('Cached events differ from the recorded source hash')
    return json.loads(path.read_text())


def build_evidence(allow_download=True):
    source = json.loads((ROOT/SOURCE_PATH).read_text())
    protocol_path = source['protocol_path']
    protocol = json.loads((ROOT/protocol_path).read_text())
    matches = []
    for old in source['matches']:
        fixture = old['fixture']
        teams = [fixture['home_team'], fixture['away_team']]
        if protocol['team'] not in teams or teams[0]==teams[1]:
            raise ValueError('Fixture does not identify a unique France opponent')
        opponent = next(team for team in teams if team!=protocol['team'])
        events = load_events(old['raw_input'], allow_download)
        result = analyze_team(events, opponent, protocol)
        matches.append({'fixture':fixture, 'defending_team':protocol['team'],
                        'opponent':opponent, 'raw_input':old['raw_input'], **result})
    return {'source_path':SOURCE_PATH,
            'source_sha256':hashlib.sha256((ROOT/SOURCE_PATH).read_bytes()).hexdigest(),
            'protocol_path':protocol_path,
            'protocol_sha256':hashlib.sha256((ROOT/protocol_path).read_bytes()).hexdigest(),
            'team_selection':'In each existing France fixture select the other team as attacking; France is defending. All five fixtures retained.',
            'shot_eligibility':'Opponent non-penalty shots in periods 1–4, with the unchanged same-possession, at-most-15-second phase boundaries.',
            'matches':matches, 'pooled':study_helper.pool(matches),
            'france_attacking_reference':source['pooled'],
            'scope':'Descriptive defensive view of already inspected fixtures. New aggregation, not fresh validation, causal attribution or a defensive ability ranking. Shot goals only; own goals and penalties are not counted as phase shot goals.'}


def rate_text(row):
    if not row['deliveries']:
        return 'no deliveries; rate undefined'
    return f"{row['corners_with_phase_shot']}/{row['deliveries']} ({row['phase_shot_rate']*100:.1f}%)"


def render_report(evidence):
    rows = '\n'.join(f"- {r['opponent']}: {rate_text(r)} corners associated with a shot; "
                     f"{r['phase_shots']} phase shots, {r['phase_shot_goals']} shot goals."
                     for r in evidence['matches'])
    pooled = evidence['pooled']
    attacking = evidence['france_attacking_reference']
    return f'''# France defending opposition corners

France faced **{pooled['deliveries']} opposition corner deliveries** in the existing five-match sample. **{rate_text(pooled)}** were associated with at least one opposition shot under the fixed phase rule. Those phases contained **{pooled['phase_shots']} shots and {pooled['phase_shot_goals']} shot goals**.

{rows}

![Opposition corner phase rates against France](../figures/55_france_defensive_corner_rates.png)

## What changed

The old question counted France's attacking corners: {rate_text(attacking)} led to a France shot. This report switches the attacking team to France's opponent in each fixture. The denominator is now opposition corners faced, and the numerator is opposition corners associated with an opposition shot. These are separate sets of deliveries, not complementary percentages.

The five fixtures and phase rules are unchanged: periods 1–4 including extra time; non-penalty shots; same possession; at most 15 seconds; stop at restart, period/possession change, shot goal or own goal. The goal shot is included before stopping. A shot is assigned only once. This is a counting study with no xG prediction or shot-quality adjustment.

## Interpretation for an analyst

The measured rate describes shot association per corner faced. It does not establish why a shot occurred, whether a marker made an error, or France's defensive ability relative to other teams. Opponents, delivery choices and match contexts differ, and we do not adjust for them. A corner without a linked phase shot is not automatically an excellent defensive action: the bounded rule can miss later attacks or stop after a possession change.

These records nominate events for video review; no footage was reviewed in this lesson. The next practical review question is: on the shot-associated opposition corners, who made first contact, was the first clearance controlled, and how did the shot arise? Event records alone do not establish those answers.

## Reproduce

Run `python 60_france_defensive_corners.py` in Spyder or locally. Previously downloaded files are reused and checked against the existing raw hashes. If absent, only the five recorded match files are downloaded and hash checked. [Saved evidence](../data/60_france_defensive_corner_evidence.json) preserves every selected corner and shot ID. [Short lesson](../lessons/0042-france-defensive-corners.html).

This is an assisted worked extension on already inspected data. Source: [StatsBomb Open Data](https://github.com/statsbomb/open-data), using the original source snapshots and attribution. The view changes; the source population and definition do not.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    rows = evidence['matches']
    fig, ax = plt.subplots(figsize=(10,5.5))
    for i,row in enumerate(rows):
        value = row['phase_shot_rate']*100 if row['phase_shot_rate'] is not None else 0
        ax.barh(i,value,color='#24658a',height=.55)
        ax.text(min(value+2,83),i,rate_text(row),va='center',fontsize=10)
    ax.set_yticks(range(len(rows)),[r['opponent'].replace(" Women's",'') for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(0,105)
    ax.set_xlabel('Opposition corners associated with a phase shot (%)')
    ax.set_title('France defending corners · five 2019 World Cup fixtures\nSame 15-second phase rule; opposition delivery denominators')
    ax.spines[['top','right']].set_visible(False)
    fig.text(.5,.025,'Counts are per opposition corner, not a defensive ability ranking.\nSource: StatsBomb Open Data. Extra time included; no video review.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.09,1,1])
    fig.savefig(ROOT/'figures/55_france_defensive_corner_rates.png',dpi=160)
    plt.show()


def main():
    evidence = build_evidence()
    (ROOT/'data/60_france_defensive_corner_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/43_france_defensive_corners.md').write_text(render_report(evidence))
    for match in evidence['matches']:
        print(match['opponent'],rate_text(match),'shots',match['phase_shots'],'shot goals',match['phase_shot_goals'])
    print('Pooled',evidence['pooled'])
    plot_evidence(evidence)


if __name__ == '__main__':
    main()
