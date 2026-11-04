"""Lesson 48: match-grouped exploratory validation of zone completion estimates."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def completion_helper():
    spec = importlib.util.spec_from_file_location('completion_cv_helper', ROOT / '47_first_pass_completion_model.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    return helper


def leave_match_out(rows, match_ids, strength):
    helper = completion_helper()
    if len(set(match_ids)) != len(match_ids) or set(match_ids) != {r['match_id'] for r in rows}:
        raise ValueError('Match IDs must identify every observed fixture exactly once')
    folds = []; predictions = []
    for held_out in match_ids:
        train = [r for r in rows if r['match_id'] != held_out]
        check = [r for r in rows if r['match_id'] == held_out]
        model = helper.fit_zones(train, strength)
        scored = [{**r, 'zone_probability': model['zones'][r['start_cell']]['smoothed_probability'],
                   'baseline_probability': model['global_training_rate']} for r in check]
        folds.append({'held_out_match_id': held_out, 'training_match_ids': [m for m in match_ids if m != held_out],
                      'model': model, 'zone_metrics': helper.score_probabilities(scored, 'zone_probability'),
                      'baseline_metrics': helper.score_probabilities(scored, 'baseline_probability')})
        predictions.extend(scored)
    if len({(r['match_id'], r['id']) for r in predictions}) != len(rows):
        raise ValueError('Each pass must receive exactly one held-out prediction')
    return {'folds': folds, 'predictions': predictions,
            'pooled_zone_metrics': helper.score_probabilities(predictions, 'zone_probability'),
            'pooled_baseline_metrics': helper.score_probabilities(predictions, 'baseline_probability')}


def build_evidence():
    path = ROOT / 'data/47_completion_model_evidence.json'
    source = json.loads(path.read_text())
    protocol = json.loads((ROOT / source['protocol_path']).read_text())
    match_ids = protocol['training_match_ids'] + protocol['exploratory_check_match_ids']
    # Retain only the labels and starting geometry, never the earlier fitted predictions.
    rows = [{k: r[k] for k in ['match_id', 'id', 'team', 'start_cell', 'completed']} for r in source['passes']]
    result = leave_match_out(rows, match_ids, source['model']['smoothing_strength'])
    prior_match = protocol['exploratory_check_match_ids'][0]
    prior = next(r for r in result['folds'] if r['held_out_match_id'] == prior_match)
    assert prior['model'] == source['model']
    assert prior['zone_metrics'] == source['zone_model_check_metrics']
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'match_ids': match_ids, 'smoothing_strength': source['model']['smoothing_strength'], **result,
            'scope': 'Five-match grouped exploratory validation on already inspected events. Fixed model family and strength, no tuning. Not chronological future prediction, new-season reliability, independent untouched validation or a completion model for specific options.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/48_completion_match_cv_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    study = json.loads((ROOT / 'data/38_france_corner_study_evidence.json').read_text())
    names = {r['fixture']['match_id']: r['opponent'].replace(" Women's", '') for r in study['matches']}
    fig, ax = plt.subplots(figsize=(10, 5))
    x = list(range(len(evidence['folds'])))
    ax.bar([i - .18 for i in x], [f['zone_metrics']['log_loss'] for f in evidence['folds']], width=.36, color='#24658a', label='Zone model')
    ax.bar([i + .18 for i in x], [f['baseline_metrics']['log_loss'] for f in evidence['folds']], width=.36, color='#b77516', label='Fold training-rate baseline')
    ax.set_xticks(x, [names[f['held_out_match_id']] for f in evidence['folds']])
    ax.set_xlabel('Held-out fixture: France v opponent (both teams’ passes checked)')
    ax.set_ylabel('Log loss · lower is better')
    ax.set_title('Does the completion model improve the baseline in every match?\nEach fixture predicted using only the other four fixtures')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False)
    fig.text(.5, .02, 'Already inspected five-match sample; exploratory grouped validation, not a fresh or chronological test.\nModel and baseline are refitted within each fold. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, 1])
    fig.savefig(ROOT / 'figures/50_completion_match_cross_validation.png', dpi=160)
    plt.show()
    for fold in evidence['folds']:
        print(names[fold['held_out_match_id']], fold['zone_metrics']['log_loss'], fold['baseline_metrics']['log_loss'])
    print('Pooled zone', evidence['pooled_zone_metrics'])
    print('Pooled baseline', evidence['pooled_baseline_metrics'])


if __name__ == '__main__':
    main()
