"""Lesson 35: denominator-aware rates for recorded corner-to-shot links.

Counts corner PASS events, not corners awarded or all subsequent set-piece phases.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def summarize(rows):
    n = len(rows)
    linked = sum(r['link_status'] == 'Verified reciprocal link' for r in rows)
    goals = sum(r['linked_shot_goal'] is True for r in rows)
    return {'deliveries': n, 'direct_linked_shots': linked, 'direct_linked_goals': goals,
            'recorded_direct_shot_link_rate': linked / n if n else None,
            'recorded_direct_goal_link_rate': goals / n if n else None,
            'delivery_ids': [r['id'] for r in rows]}


def load_helper(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def build_evidence():
    path = ROOT / 'data/29_match_xg_evidence.json'
    source = json.loads(path.read_text())
    helper = load_helper('corner_raw_source', '29_match_xg_summary.py')
    assert helper.build_evidence() == source
    link_helper = load_helper('corner_link_helper', '34_header_assisting_passes.py')
    raw_path = ROOT / source['raw_input']['relative_path']
    events = json.loads(raw_path.read_text())
    lookup = {r['id']: r for r in events}
    rows = []
    for event in events:
        if event['period'] not in (1, 2) or event['type']['name'] != 'Pass':
            continue
        p = event['pass']
        if p.get('type', {}).get('name') != 'Corner':
            continue
        # Keep incomplete/out deliveries and short corners: denominator is ALL corner pass events.
        target = p.get('assisted_shot_id')
        status = 'No assisted-shot link recorded'
        goal = None
        if target:
            if target not in lookup:
                raise ValueError('Assisted shot unavailable; do not silently count as no link')
            shot = lookup[target]
            if shot['type']['name'] != 'Shot':
                raise ValueError('Assisted event is not a shot')
            status, reciprocal = link_helper.linked_pass(shot, lookup)
            if status != 'Verified reciprocal link' or reciprocal['id'] != event['id']:
                raise ValueError('Corner and shot links do not agree')
            goal = shot['shot']['outcome']['name'] == 'Goal'
        rows.append({'id': event['id'], 'team': event['team']['name'], 'period': event['period'],
                     'minute': event['minute'], 'second': event['second'], 'passer': event['player']['name'],
                     'pass_outcome': p.get('outcome', {}).get('name'), 'assisted_shot_id': target,
                     'link_status': status, 'linked_shot_goal': goal})
    summaries = []
    for team in source['teams']:
        selected = [r for r in rows if r['team'] == team['team']]
        summaries.append({'team': team['team'], **summarize(selected),
                          'halves': [{'period': h, **summarize([r for r in selected if r['period'] == h])} for h in (1, 2)]})
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'fixture': source['fixture'], 'raw_input': source['raw_input'], 'corner_deliveries': rows,
            'teams': summaries,
            'scope': 'All period-1/2 corner pass events, including incomplete/out. Recorded direct assisting links only; not all corner-phase shots or goals, corners awarded, causal effectiveness or fresh model validation.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/35_corner_delivery_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    france = evidence['teams'][0]
    values = [france[k] for k in ('deliveries', 'direct_linked_shots', 'direct_linked_goals')]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(['All corner\ndeliveries', 'Deliveries with a\ndirect shot link', 'Deliveries with a\ndirect goal link'], values,
           color=['#24658a', '#b77516', '#446b57'], width=.55)
    for i, value in enumerate(values):
        ax.text(i, value + .2, str(value), ha='center')
    ax.set_ylim(0, max(values) + 3)
    ax.set_ylabel('Recorded corner pass events')
    ax.set_title('France: start with every corner delivery\nFrance v Korea Republic · recorded direct links only')
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.5, .02, 'Nested counts, not separate categories: the 2 goal links are included in the 2 shot links.\nNo direct link does not mean no later chance. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .10, 1, 1])
    fig.savefig(ROOT / 'figures/38_corner_delivery_rates.png', dpi=160)
    plt.show()
    for team in evidence['teams']:
        print(team['team'], team['deliveries'], team['direct_linked_shots'], team['direct_linked_goals'])


if __name__ == '__main__':
    main()
