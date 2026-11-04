"""Lesson 44: fit a coarse educational position-based expected-threat model.

Based on the Soccermatics and mplsoccer xT method. Descriptive training fit only.
"""
import hashlib
import json
import math
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
NX, NY = 6, 4
RESTARTS = {'Corner', 'Free Kick', 'Throw-in', 'Goal Kick', 'Kick Off'}


def cell(point):
    if not isinstance(point, list) or len(point) < 2:
        return None
    x, y = point[:2]
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (x, y)) or not (0 <= x <= 120 and 0 <= y <= 80):
        return None
    return min(int(y / 80 * NY), NY - 1) * NX + min(int(x / 120 * NX), NX - 1)


def fit_grid(actions):
    n_cells = NX * NY
    counts = [0] * n_cells; goals = [0] * n_cells
    transitions = [[0] * n_cells for _ in range(n_cells)]
    for row in actions:
        start = row['start_cell']; counts[start] += 1
        goals[start] += row['goal']
        if row['type'] != 'Shot' and row['successful_move']:
            transitions[start][row['end_cell']] += 1
    immediate = [goals[i] / counts[i] if counts[i] else 0 for i in range(n_cells)]
    matrix = [[value / counts[i] if counts[i] else 0 for value in transitions[i]] for i in range(n_cells)]
    values = [0.0] * n_cells
    for iteration in range(1, 10001):
        updated = [immediate[i] + sum(matrix[i][j] * values[j] for j in range(n_cells)) for i in range(n_cells)]
        change = max(abs(a - b) for a, b in zip(updated, values))
        values = updated
        if change <= 1e-12:
            break
    else:
        raise ValueError('xT iteration failed to converge')
    residual = max(abs(values[i] - immediate[i] - sum(matrix[i][j] * values[j] for j in range(n_cells))) for i in range(n_cells))
    return {'action_counts': counts, 'goal_counts': goals, 'successful_move_counts': transitions,
            'immediate_goal_per_action': immediate, 'successful_transition_per_action': matrix,
            'zone_values': values, 'iterations': iteration, 'max_update': change, 'fixed_point_residual': residual}


def build_evidence():
    source_path = ROOT / 'data/38_france_corner_study_evidence.json'
    source = json.loads(source_path.read_text())
    actions = []; excluded = {}; raw_inputs = []
    def reject(reason):
        excluded[reason] = excluded.get(reason, 0) + 1
    for match in source['matches']:
        record = match['raw_input']; path = ROOT / record['relative_path']
        if not path.exists():
            with urlopen(record['source_url'], timeout=60) as response:
                payload = response.read()
            assert hashlib.sha256(payload).hexdigest() == record['sha256']
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
        raw_inputs.append(record)
        events = sorted(json.loads(path.read_text()), key=lambda r: r['index'])
        for event in events:
            kind = event['type']['name']
            if kind not in ('Pass', 'Carry', 'Shot'):
                continue
            if event['period'] not in (1, 2, 3, 4):
                reject('shootout_or_other_period'); continue
            if event['team']['id'] != event['possession_team']['id']:
                reject('event_team_not_possession_team'); continue
            if kind == 'Pass' and event['pass'].get('type', {}).get('name') in RESTARTS:
                reject('restart_pass'); continue
            if kind == 'Shot' and event['shot']['type']['name'] == 'Penalty':
                reject('penalty_shot'); continue
            start = cell(event.get('location'))
            if start is None:
                reject('invalid_or_outside_start'); continue
            end = event.get(kind.lower(), {}).get('end_location') if kind != 'Shot' else None
            end_cell = cell(end)
            success = kind != 'Shot' and end_cell is not None and (kind == 'Carry' or 'outcome' not in event['pass'])
            actions.append({'match_id': match['fixture']['match_id'], 'id': event['id'], 'index': event['index'],
                            'team': event['team']['name'], 'player': event['player']['name'], 'type': kind,
                            'start': event['location'][:2], 'end': end[:2] if isinstance(end, list) else None,
                            'start_cell': start, 'end_cell': end_cell,
                            'successful_move': success, 'goal': int(kind == 'Shot' and event['shot']['outcome']['name'] == 'Goal')})
    model = fit_grid(actions)
    examples = []
    for label in ('Positive', 'Zero', 'Negative'):
        for row in actions:
            if row['type'] != 'Pass' or not row['successful_move'] or row['team'] != "France Women's":
                continue
            start = model['zone_values'][row['start_cell']]; end = model['zone_values'][row['end_cell']]
            delta = end - start
            if ('Positive' if delta > 1e-12 else 'Negative' if delta < -1e-12 else 'Zero') == label:
                examples.append({'label': label, **row, 'start_xt': start, 'end_xt': end, 'added_xt': delta})
                break
    return {'source_path': source_path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'grid': {'nx': NX, 'ny': NY, 'row_direction': 'y=0 to y=80', 'attack_direction': 'x=0 to x=120'},
            'raw_inputs': raw_inputs, 'actions': actions, 'excluded_action_counts': excluded,
            'model': model, 'examples': examples,
            'selection': 'Both teams in all five existing France fixtures; periods 1–4; possession-team Pass/Carry/non-penalty Shot, excluding restart passes. Failed moves remain in action denominators; only successful in-pitch moves transition.',
            'scope': 'Educational 6x4 training fit. No out-of-sample validation, player ranking, causal credit or professional readiness. Completion-only pass examples are illustrative and omit failed-pass cost.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/44_first_xt_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    import numpy as np
    from mplsoccer import Pitch
    pitch = Pitch(pitch_type='statsbomb', line_color='white', line_zorder=2)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    values = np.array(evidence['model']['zone_values']).reshape(NY, NX)
    for ax in axes:
        pitch.draw(ax=ax)
        ax.imshow(values, extent=[0, 120, 80, 0], origin='upper', cmap='YlOrRd', alpha=.8, zorder=0)
    for y in range(NY):
        for x in range(NX):
            axes[0].text((x + .5) * 120 / NX, (y + .5) * 80 / NY, f'{values[y,x]:.3f}', ha='center', va='center', fontsize=9)
    axes[0].set_title('Fitted zone values · training data only')
    colors = {'Positive': '#126b38', 'Zero': '#24658a', 'Negative': '#5f217c'}
    for row in evidence['examples']:
        pitch.arrows(*row['start'], *row['end'], color=colors[row['label']], width=2.5, headwidth=4, ax=axes[1],
                     label=f"{row['label']}: {row['added_xt']:+.4f}", zorder=4)
    axes[1].legend(loc='lower left', fontsize=9)
    axes[1].set_title('Three actual completed-pass examples')
    fig.suptitle('First expected-threat model · value at end minus value at start\n6×4 grid · both teams in five France fixtures · attacks right', fontsize=14)
    fig.text(.5, .02, 'Coarse educational fit; values describe a simplified location-only action model. No independent reliability assessment.\nExamples are selected by sign for teaching. Data: StatsBomb Open Data; method: Soccermatics / mplsoccer.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.78, bottom=.17, wspace=.15)
    fig.savefig(ROOT / 'figures/46_first_expected_threat.png', dpi=160)
    plt.show()
    print('Actions', len(evidence['actions']), 'shots', sum(r['type']=='Shot' for r in evidence['actions']), 'goals', sum(r['goal'] for r in evidence['actions']))
    print('Iterations', evidence['model']['iterations'], 'residual', evidence['model']['fixed_point_residual'])
    for row in evidence['examples']:
        print(row['label'], row['player'], row['start_xt'], row['end_xt'], row['added_xt'])


if __name__ == '__main__':
    main()
