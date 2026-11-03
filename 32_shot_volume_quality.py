"""Lesson 32: total npxG = shot count × mean npxG per shot.

Descriptive ratio identity, not a causal decomposition. No fitting or downloads.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def compare_halves(first, second):
    """Undefined ratios remain None when a reference quantity is zero."""
    means = [r['model_npxg'] / r['shots'] if r['shots'] else None for r in (first, second)]
    volume = second['shots'] / first['shots'] if first['shots'] else None
    quality = means[1] / means[0] if means[0] and means[1] is not None else None
    total = second['model_npxg'] / first['model_npxg'] if first['model_npxg'] else None
    if volume is not None and quality is not None and total is not None:
        assert math.isclose(volume * quality, total)
    return {'first_half': {**first, 'model_npxg_per_shot': means[0]},
            'second_half': {**second, 'model_npxg_per_shot': means[1]},
            'second_over_first_shot_ratio': volume,
            'second_over_first_mean_quality_ratio': quality,
            'second_over_first_total_npxg_ratio': total}


def build_evidence():
    path = ROOT / 'data/29_match_xg_evidence.json'
    source = json.loads(path.read_text())
    comparisons = []
    for team in source['teams']:
        halves = []
        for period in (1, 2):
            rows = [r for r in source['shots'] if r['team'] == team['team'] and r['period'] == period]
            halves.append({'shots': len(rows), 'model_npxg': sum(r['model_probability'] for r in rows),
                           'shot_ids': [r['id'] for r in rows]})
        comparisons.append({'team': team['team'], **compare_halves(*halves)})
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'fixture': source['fixture'], 'comparisons': comparisons,
            'scope': 'Arithmetic description of the same non-penalty shots and frozen model. Ratios use raw half totals, not per-minute rates. Not causal attribution or new validation.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/32_volume_quality_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    france = evidence['comparisons'][0]
    fields = ['second_over_first_shot_ratio', 'second_over_first_mean_quality_ratio', 'second_over_first_total_npxg_ratio']
    values = [france[k] * 100 for k in fields]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(['Shots', 'Mean model npxG / shot', 'Total model npxG'], values, color=['#24658a', '#b77516', '#446b57'], width=.55)
    ax.axhline(100, linestyle='--', color='#657b88', label='First half = 100%')
    for i, value in enumerate(values):
        ax.text(i, value + 2, f'{value:.1f}%', ha='center')
    ax.set_ylim(0, 120)
    ax.set_ylabel('Second half as % of first half')
    ax.set_title('France: fewer shots and lower average estimated quality\nSame frozen distance-only model · France v Korea Republic')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False)
    fig.text(.5, .02, 'Ratios multiply: shot ratio × quality ratio = total npxG ratio.\nRaw half totals; no exposure adjustment or tactical cause inferred. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .10, 1, 1])
    fig.savefig(ROOT / 'figures/35_shot_volume_quality.png', dpi=160)
    plt.show()
    for row in evidence['comparisons']:
        print(row['team'], {k: row[k] for k in fields})


if __name__ == '__main__':
    main()
