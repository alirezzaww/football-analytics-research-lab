"""Lesson 29: turn frozen shot probabilities into a descriptive match brief.

Select the first chronological fixture in the existing evaluation protocol.
No fitting or new validation. Non-penalty shots only; own goals are not shot goals.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def summarize(shots, teams):
    """Count each shot once; retain teams with zero shots and undefined mean."""
    keys = [(r['match_id'], r['id']) for r in shots]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate shot IDs would double count xG')
    if any(r['team'] not in teams for r in shots):
        raise ValueError('Unexpected team')
    output = []
    for team in teams:
        rows = [r for r in shots if r['team'] == team]
        total = sum(r['model_probability'] for r in rows)
        output.append({'team': team, 'shots': len(rows), 'shot_goals': sum(r['goal'] for r in rows),
                       'model_npxg': total, 'model_npxg_per_shot': total / len(rows) if rows else None})
    return output


def build_evidence():
    source_path = ROOT / 'data/27_frozen_evaluation_evidence.json'
    source = json.loads(source_path.read_text())
    protocol = json.loads((ROOT / source['protocol_path']).read_text())
    fixture = protocol['fixture_metadata'][0]
    match_id = fixture['match_id']
    record = next(r for r in source['raw_inputs'] if r['match_id'] == match_id)
    path = ROOT / record['relative_path']
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with urlopen(record['source_url'], timeout=60) as response:
            payload = response.read()
        if hashlib.sha256(payload).hexdigest() != record['sha256']:
            raise ValueError('Downloaded events differ from frozen source')
        path.write_bytes(payload)
    if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError('Cached events differ from frozen source')
    events = {r['id']: r for r in json.loads(path.read_text())}
    rows = []
    for shot in source['shots']:
        if shot['match_id'] != match_id:
            continue
        event = events[shot['id']]
        assert event['type']['name'] == 'Shot'
        assert int(event['shot']['outcome']['name'] == 'Goal') == shot['goal']
        rows.append({**shot, 'team': event['team']['name'], 'minute': event['minute'],
                     'second': event['second'], 'period': event['period']})
    teams = [fixture['home_team'], fixture['away_team']]
    return {'source_path': source_path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'selection_rule': 'First chronological fixture in the frozen evaluation protocol; no outcome-based selection',
            'fixture': fixture, 'raw_input': record, 'shots': rows, 'teams': summarize(rows, teams),
            'scope': 'Existing frozen distance-model probabilities; non-penalty shot goals only. Not a new validation or match result forecast.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/29_match_xg_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    teams = evidence['teams']
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
    names = [r['team'].replace(" Women's", '') for r in teams]
    for ax, field, title in zip(axes, ['shots', 'model_npxg', 'model_npxg_per_shot'],
                              ['Shot volume', 'Total model npxG', 'Mean model npxG / shot']):
        values = [r[field] for r in teams]
        ax.bar(names, values, color=['#24658a', '#b77516'])
        ax.set_ylim(0, max(values) * 1.25 if max(values) else 1)
        ax.set_title(title)
        for i, value in enumerate(values):
            ax.text(i, value, f'{value:.0f}' if field == 'shots' else f'{value:.3f}', ha='center', va='bottom')
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('France v Korea Republic · 7 June 2019\nNon-penalty shots · educational distance-only model', fontsize=13)
    fig.text(.5, .01, 'Descriptive shot summary; xG is not a guaranteed score. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .05, 1, .87])
    fig.savefig(ROOT / 'figures/32_match_xg_summary.png', dpi=160)
    plt.show()
    for team in teams:
        print(team)


if __name__ == '__main__':
    main()
