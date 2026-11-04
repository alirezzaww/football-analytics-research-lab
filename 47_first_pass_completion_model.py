"""Lesson 47: training-only zone completion estimates and exploratory match check."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fit_zones(rows, strength):
    if not rows or not math.isfinite(strength) or strength <= 0:
        raise ValueError('Nonempty fitting data and positive finite smoothing strength required')
    baseline = sum(r['completed'] for r in rows) / len(rows)
    zones = []
    for zone in range(24):
        selected = [r for r in rows if r['start_cell'] == zone]
        successes = sum(r['completed'] for r in selected)
        n = len(selected)
        zones.append({'cell': zone, 'attempts': n, 'completions': successes,
                      'raw_completion_rate': successes / n if n else None,
                      'smoothed_probability': (successes + strength * baseline) / (n + strength)})
    return {'training_attempts': len(rows), 'training_completions': sum(r['completed'] for r in rows),
            'global_training_rate': baseline, 'smoothing_strength': strength, 'zones': zones}


def score_probabilities(rows, key):
    n = len(rows)
    if not n:
        raise ValueError('Need check observations')
    logloss = brier = 0.0
    for row in rows:
        p = row[key]; y = row['completed']
        if not 0 < p < 1 or y not in (0, 1):
            raise ValueError('Invalid probability or label')
        logloss -= y * math.log(p) + (1 - y) * math.log1p(-p)
        brier += (p - y) ** 2
    return {'passes': n, 'completions': sum(r['completed'] for r in rows), 'log_loss': logloss / n, 'brier_score': brier / n}


def build_evidence():
    path = ROOT / 'data/45_failed_pass_value_evidence.json'
    source = json.loads(path.read_text())
    protocol_path = ROOT / 'data/47_completion_model_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    train_ids = set(protocol['training_match_ids']); test_ids = set(protocol['exploratory_check_match_ids'])
    assert not train_ids & test_ids
    rows = []; excluded = []
    for row in source['passes']:
        outcome = row['pass_outcome']
        if outcome is not None and outcome not in ('Incomplete', 'Out', 'Pass Offside'):
            excluded.append({'match_id': row['match_id'], 'id': row['id'], 'outcome': outcome}); continue
        assert row['match_id'] in train_ids | test_ids
        rows.append({'match_id': row['match_id'], 'id': row['id'], 'team': row['team'],
                     'start_cell': row['start_cell'], 'completed': int(outcome is None),
                     'split': 'train' if row['match_id'] in train_ids else 'exploratory_check'})
    model = fit_zones([r for r in rows if r['split'] == 'train'], protocol['smoothing_strength'])
    for row in rows:
        row['zone_probability'] = model['zones'][row['start_cell']]['smoothed_probability']
        row['baseline_probability'] = model['global_training_rate']
    check = [r for r in rows if r['split'] == 'exploratory_check']
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'protocol_path': protocol_path.relative_to(ROOT).as_posix(),
            'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'model': model, 'passes': rows, 'excluded': excluded,
            'zone_model_check_metrics': score_probabilities(check, 'zone_probability'),
            'constant_baseline_check_metrics': score_probabilities(check, 'baseline_probability'),
            'scope': protocol['interpretation'], 'validation_limit': protocol['split_rule']}


def main():
    evidence = build_evidence()
    (ROOT / 'data/47_completion_model_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    import numpy as np
    from mplsoccer import Pitch
    grid = np.array([z['smoothed_probability'] for z in evidence['model']['zones']]).reshape(4, 6)
    pitch = Pitch(pitch_type='statsbomb', line_color='white', line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 6)); fig.set_layout_engine(None)
    ax.imshow(grid, extent=[0, 120, 80, 0], origin='upper', cmap='Blues', vmin=0, vmax=1, zorder=0)
    for y in range(4):
        for x in range(6):
            row = evidence['model']['zones'][y * 6 + x]
            ax.text((x + .5) * 20, (y + .5) * 20, f"{row['smoothed_probability']:.0%}\nn={row['attempts']}",
                    ha='center', va='center', color='white' if row['smoothed_probability'] > .6 else '#172d3b', fontsize=10)
    fig.suptitle('First pass-completion model · starting location only\nTraining counts from the first four France fixtures · both teams', fontsize=14)
    fig.text(.5, .02, 'Smoothed training probabilities, not xT zone values or specific passing-option predictions.\nThe fifth fixture is an exploratory check on previously inspected events. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.82, bottom=.13)
    fig.savefig(ROOT / 'figures/49_first_pass_completion_model.png', dpi=160)
    plt.show()
    print('Training', evidence['model']['training_attempts'], evidence['model']['training_completions'], evidence['model']['global_training_rate'])
    print('Zone model', evidence['zone_model_check_metrics'])
    print('Baseline', evidence['constant_baseline_check_metrics'])


if __name__ == '__main__':
    main()
