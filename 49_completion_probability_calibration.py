"""Lesson 49: compare completion predictions with observed group frequencies.

Uses existing out-of-fold probabilities; no model or calibrator is fitted.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDGES = (0, .6, .7, .8, .9, 1)


def probability_band(probability):
    if not isinstance(probability, (int, float)) or not math.isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError('Probability must be finite and in [0, 1]')
    for i, upper in enumerate(EDGES[1:]):
        if probability < upper or upper == 1:
            return i


def summarize(rows):
    n = len(rows)
    completions = sum(r['completed'] for r in rows)
    expected = sum(r['zone_probability'] for r in rows)
    return {'passes': n, 'completions': completions, 'predicted_completion_sum': expected,
            'mean_prediction': expected / n if n else None,
            'observed_completion_rate': completions / n if n else None,
            'pass_keys': [{'match_id': r['match_id'], 'id': r['id']} for r in rows]}


def build_evidence():
    path = ROOT / 'data/48_completion_match_cv_evidence.json'
    source = json.loads(path.read_text())
    rows = source['predictions']
    groups = []
    for i in range(len(EDGES) - 1):
        selected = [r for r in rows if probability_band(r['zone_probability']) == i]
        groups.append({'lower_inclusive': EDGES[i], 'upper': EDGES[i+1], 'upper_inclusive': i == len(EDGES)-2,
                       **summarize(selected)})
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bin_edges': list(EDGES), 'groups': groups, 'overall': summarize(rows),
            'scope': 'Descriptive group calibration of existing five-match out-of-fold predictions. Group edges chosen for this diagnostic; no calibrator fitted, no fresh data, no confidence interval or exact individual-probability claim.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/49_completion_calibration_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    groups = [r for r in evidence['groups'] if r['passes']]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    axes[0].plot([0, 100], [0, 100], color='#8a989f', linestyle='--', label='Agreement line')
    axes[0].plot([r['mean_prediction'] * 100 for r in groups], [r['observed_completion_rate'] * 100 for r in groups],
                 marker='o', linewidth=1, color='#24658a', label='Observed prediction groups')
    for r in groups:
        axes[0].annotate(f"n={r['passes']}", (r['mean_prediction']*100, r['observed_completion_rate']*100), xytext=(4, 6), textcoords='offset points', fontsize=8)
    axes[0].set_xlim(35, 100); axes[0].set_ylim(35, 100)
    axes[0].set_xlabel('Average predicted completion (%)')
    axes[0].set_ylabel('Actual completed passes (%)')
    axes[0].set_title('Do the percentages agree?')
    axes[0].legend(loc='lower right', fontsize=8)
    labels = ['<60%', '60–<70%', '70–<80%', '80–<90%', '90–100%']
    axes[1].bar(labels, [r['passes'] for r in evidence['groups']], color='#b77516')
    axes[1].tick_params(axis='x', labelrotation=20)
    axes[1].set_title('How many passes support each group?')
    axes[1].set_ylabel('Held-out pass observations')
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Completion calibration · existing match-held-out predictions\nGroup frequencies, not known true probabilities for individual passes', fontsize=14)
    fig.text(.5, .02, 'Five already inspected fixtures; bins pool different origin cells and fold fits. No recalibration or uncertainty interval.\nData: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .10, 1, .85])
    fig.savefig(ROOT / 'figures/51_completion_calibration.png', dpi=160)
    plt.show()
    for r in evidence['groups']:
        print(r['lower_inclusive'], r['upper'], r['passes'], r['mean_prediction'], r['observed_completion_rate'])


if __name__ == '__main__':
    main()
