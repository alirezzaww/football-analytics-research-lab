"""Lesson 51: audit fitting-group support and the influence of smoothing.

Descriptive diagnostic of existing predictions, not a new fit or causal explanation.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANDS = ('No fitting passes', '1–19 fitting passes', '20–49 fitting passes', '50+ fitting passes')


def support_band(n):
    if type(n) is not int or n < 0:
        raise ValueError('Support must be a nonnegative integer')
    return BANDS[0] if n == 0 else BANDS[1] if n < 20 else BANDS[2] if n < 50 else BANDS[3]


def prior_weight(n, strength):
    support_band(n)
    if not isinstance(strength, (int, float)) or not math.isfinite(strength) or strength <= 0:
        raise ValueError('Smoothing strength must be positive')
    return strength / (n + strength)


def build_evidence():
    path = ROOT / 'data/50_pressure_feature_evidence.json'
    source = json.loads(path.read_text())
    lookups = {f['held_out_match_id']: {(g['cell'], g['pressure_flag']): g for g in f['model']['groups']} for f in source['folds']}
    strengths = {f['held_out_match_id']: f['model']['pressure_strength'] for f in source['folds']}
    rows = []
    for original in source['predictions']:
        group = lookups[original['match_id']][(original['start_cell'], original['pressure_flag'])]
        n = group['attempts']; successes = group['completions']; strength = strengths[original['match_id']]
        rows.append({'match_id': original['match_id'], 'id': original['id'], 'pressure_flag': original['pressure_flag'],
                     'training_group_attempts': n, 'training_group_completions': successes,
                     'support_band': support_band(n), 'smoothing_strength': strength,
                     'raw_group_completion_rate': successes / n if n else None,
                     'origin_prior': group['origin_prior'], 'prior_weight': prior_weight(n, strength),
                     'pressure_probability': original['pressure_probability']})
    summaries = []
    for band in BANDS:
        selected = [r for r in rows if r['support_band'] == band]
        summaries.append({'support_band': band, 'predictions': len(selected),
                          'pressure_flagged_predictions': sum(r['pressure_flag'] for r in selected),
                          'mean_prior_weight': sum(r['prior_weight'] for r in selected) / len(selected) if selected else None,
                          'pass_keys': [{'match_id': r['match_id'], 'id': r['id']} for r in selected]})
    usa = next(f for f in source['folds'] if f['held_out_match_id'] == 69202)
    examples = []
    for group in usa['model']['groups']:
        if group['cell'] == 8:
            examples.append({**group, 'prior_weight': prior_weight(group['attempts'], usa['model']['pressure_strength'])})
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'predictions': rows, 'support_groups': summaries, 'usa_cell_8_examples': examples,
            'scope': 'Support bands are descriptive choices, not reliability cutoffs. Smoothing weights are formula weights, not confidence levels. Reused predictions, no refit or proof that small groups caused any match error.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/51_completion_group_support_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    ns = list(range(201))
    axes[0].plot(ns, [prior_weight(n, 20) * 100 for n in ns], color='#24658a')
    for example in evidence['usa_cell_8_examples']:
        n = example['attempts']; weight = example['prior_weight'] * 100
        axes[0].scatter(n, weight, color='#b77516', zorder=3)
        axes[0].annotate(f'n={n}: {weight:.1f}%', (n, weight), xytext=(-65 if n > 100 else 8, 8), textcoords='offset points', fontsize=9)
    axes[0].set_xlabel('Training passes in the zone/flag group')
    axes[0].set_ylabel('Weight on the origin reference (%)')
    axes[0].set_title('Smaller groups lean more on the reference')
    axes[0].set_ylim(0, 105)
    groups = evidence['support_groups']
    axes[1].bar(['0', '1–19', '20–49', '50+'], [g['pressure_flagged_predictions'] for g in groups], color='#b77516')
    axes[1].set_title('Support for pressure-flagged predictions')
    axes[1].set_xlabel('Training passes in that prediction’s subgroup')
    axes[1].set_ylabel('Held-out pressure-flagged predictions')
    for i, group in enumerate(groups):
        axes[1].text(i, group['pressure_flagged_predictions'], str(group['pressure_flagged_predictions']), ha='center', va='bottom')
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Why subdividing the data can make estimates fragile\nExisting pressure-feature model · no changed predictions', fontsize=14)
    fig.text(.5, .02, 'Reference weight is a smoothing formula, not a confidence percentage. Counts do not alone determine reliability.\nData: StatsBomb Open Data. Five-match development diagnostic.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, .85])
    fig.savefig(ROOT / 'figures/53_completion_group_support.png', dpi=160)
    plt.show()
    for group in groups:
        print(group['support_band'], group['predictions'], group['pressure_flagged_predictions'])
    for example in evidence['usa_cell_8_examples']:
        print('Cell 8', example['pressure_flag'], example['attempts'], example['prior_weight'])


if __name__ == '__main__':
    main()
