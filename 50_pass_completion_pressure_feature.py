"""Lesson 50: test a recorded-pressure feature with fold-local group estimates."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def recorded_pressure(value):
    if value is not None and type(value) is not bool:
        raise ValueError('Pressure field must be boolean or absent/null')
    return value is True


def helper():
    spec = importlib.util.spec_from_file_location('pressure_completion_base', ROOT / '47_first_pass_completion_model.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def fit_pressure(rows, origin_strength=20, pressure_strength=20):
    if not math.isfinite(pressure_strength) or pressure_strength <= 0:
        raise ValueError('Pressure smoothing strength must be positive and finite')
    origin = helper().fit_zones(rows, origin_strength)
    groups = []
    for zone in origin['zones']:
        for flag in (False, True):
            selected = [r for r in rows if r['start_cell'] == zone['cell'] and r['pressure_flag'] == flag]
            n = len(selected); successes = sum(r['completed'] for r in selected)
            prior = zone['smoothed_probability']
            groups.append({'cell': zone['cell'], 'pressure_flag': flag, 'attempts': n, 'completions': successes,
                           'origin_prior': prior, 'probability': (successes + pressure_strength * prior) / (n + pressure_strength)})
    return {'origin_model': origin, 'pressure_strength': pressure_strength, 'groups': groups}


def cross_validate(rows, match_ids, origin_strength, pressure_strength):
    scorer = helper()
    folds = []; predictions = []
    for omitted in match_ids:
        train = [r for r in rows if r['match_id'] != omitted]
        check = [r for r in rows if r['match_id'] == omitted]
        model = fit_pressure(train, origin_strength, pressure_strength)
        lookup = {(g['cell'], g['pressure_flag']): g['probability'] for g in model['groups']}
        scored = [{**r, 'origin_probability': model['origin_model']['zones'][r['start_cell']]['smoothed_probability'],
                   'pressure_probability': lookup[(r['start_cell'], r['pressure_flag'])]} for r in check]
        folds.append({'held_out_match_id': omitted, 'training_match_ids': [m for m in match_ids if m != omitted],
                      'model': model, 'origin_metrics': scorer.score_probabilities(scored, 'origin_probability'),
                      'pressure_metrics': scorer.score_probabilities(scored, 'pressure_probability')})
        predictions.extend(scored)
    assert len({(r['match_id'], r['id']) for r in predictions}) == len(rows)
    return {'folds': folds, 'predictions': predictions,
            'pooled_origin_metrics': scorer.score_probabilities(predictions, 'origin_probability'),
            'pooled_pressure_metrics': scorer.score_probabilities(predictions, 'pressure_probability')}


def build_evidence():
    protocol_path = ROOT / 'data/50_pressure_feature_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    source_path = ROOT / protocol['source_predictions']
    source = json.loads(source_path.read_text())
    raw_manifest_path = ROOT / 'data/44_first_xt_evidence.json'
    manifest = json.loads(raw_manifest_path.read_text())
    lookups = {}
    for raw in manifest['raw_inputs']:
        path = ROOT / raw['relative_path']
        if not path.exists():
            with urlopen(raw['source_url'], timeout=60) as response:
                payload = response.read()
            assert hashlib.sha256(payload).hexdigest() == raw['sha256']
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == raw['sha256']
        lookups[raw['match_id']] = {e['id']: e for e in json.loads(path.read_text())}
    rows = []
    for row in source['predictions']:
        event = lookups[row['match_id']][row['id']]
        raw_value = event.get('under_pressure')
        rows.append({**{k: row[k] for k in ['match_id', 'id', 'team', 'start_cell', 'completed']},
                     'pressure_field_present': 'under_pressure' in event, 'raw_pressure_value': raw_value,
                     'pressure_flag': recorded_pressure(raw_value)})
    result = cross_validate(rows, source['match_ids'], protocol['origin_smoothing_strength'], protocol['pressure_group_smoothing_strength'])
    assert result['pooled_origin_metrics'] == source['pooled_zone_metrics']
    # Every origin reference reproduces the existing held-out prediction exactly.
    reference = {(r['match_id'], r['id']): r for r in source['predictions']}
    for row in result['predictions']:
        assert row['origin_probability'] == reference[(row['match_id'], row['id'])]['zone_probability']
    return {'source_path': source_path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'protocol_path': protocol_path.relative_to(ROOT).as_posix(), 'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'raw_manifest_path': raw_manifest_path.relative_to(ROOT).as_posix(),
            'raw_manifest_sha256': hashlib.sha256(raw_manifest_path.read_bytes()).hexdigest(),
            'match_ids': source['match_ids'], **result, 'scope': protocol['interpretation']}


def main():
    evidence = build_evidence()
    (ROOT / 'data/50_pressure_feature_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    study = json.loads((ROOT / 'data/38_france_corner_study_evidence.json').read_text())
    names = {r['fixture']['match_id']: r['opponent'].replace(" Women's", '') for r in study['matches']}
    for i, fold in enumerate(evidence['folds']):
        ax.bar(i-.18, fold['origin_metrics']['log_loss'], width=.36, color='#24658a', label='Origin only' if i == 0 else None)
        ax.bar(i+.18, fold['pressure_metrics']['log_loss'], width=.36, color='#b77516', label='Origin + recorded pressure' if i == 0 else None)
    ax.set_xticks(range(5), [names[f['held_out_match_id']] for f in evidence['folds']])
    ax.set_ylabel('Held-out log loss · lower is better')
    ax.set_title('Does one extra feature help?\nSame pass sample and whole-match checks; new fold-local pressure groups')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False)
    fig.text(.5, .02, 'Recorded pressure flag is a reporting feature; no flag does not establish no actual pressure.\nExploratory development comparison, not fresh validation or causal pressure effects. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, 1])
    fig.savefig(ROOT / 'figures/52_completion_pressure_feature.png', dpi=160)
    plt.show()
    print('Origin', evidence['pooled_origin_metrics'])
    print('Pressure', evidence['pooled_pressure_metrics'])
    print('Flagged', sum(r['pressure_flag'] for r in evidence['predictions']))
    for fold in evidence['folds']:
        print(names[fold['held_out_match_id']], fold['origin_metrics']['log_loss'], fold['pressure_metrics']['log_loss'])
    usa = next(f for f in evidence['folds'] if f['held_out_match_id']==69202)
    print('Example cell 8', [g for g in usa['model']['groups'] if g['cell']==8])


if __name__ == '__main__':
    main()
