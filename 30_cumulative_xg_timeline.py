"""Lesson 30: follow cumulative frozen-model npxG through two separate halves.

Uses the committed lesson-29 ledger only. No downloads, fitting or new validation.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_timelines(shots, teams):
    """Keep added time in its own period; carry totals across halftime."""
    if len({(r['match_id'], r['id']) for r in shots}) != len(shots):
        raise ValueError('Duplicate shot identity')
    if any(r['period'] not in (1, 2) or r['team'] not in teams for r in shots):
        raise ValueError('This two-half lesson requires known teams and periods 1–2')
    ordered = sorted(shots, key=lambda r: (r['period'], r['minute'], r['second']))
    output = []
    for team in teams:
        total = 0.0
        for period in (1, 2):
            start = total
            points = []
            for row in ordered:
                if row['team'] != team or row['period'] != period:
                    continue
                total += row['model_probability']
                points.append({'id': row['id'], 'minute': row['minute'], 'second': row['second'],
                               'half_clock_minute': row['minute'] - (45 if period == 2 else 0) + row['second'] / 60,
                               'shot_xg': row['model_probability'], 'goal': row['goal'], 'cumulative_npxg': total})
            output.append({'team': team, 'period': period, 'start_npxg': start, 'end_npxg': total,
                           'half_npxg': total - start, 'shots': len(points), 'points': points})
    return output


def build_evidence():
    path = ROOT / 'data/29_match_xg_evidence.json'
    source = json.loads(path.read_text())
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'fixture': source['fixture'],
            'timelines': build_timelines(source['shots'], [r['team'] for r in source['teams']]),
            'clock_rule': 'Separate periods; second-half nominal minute minus 45; seconds retained. Stable source order within tied seconds.',
            'scope': 'Existing non-penalty shots and frozen distance-model probabilities. Not possession, tactical causation, live win probability or fresh validation.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/30_cumulative_xg_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    colors = ['#24658a', '#b77516']
    teams = list(dict.fromkeys(r['team'] for r in evidence['timelines']))
    for period, ax in enumerate(axes, 1):
        groups = [r for r in evidence['timelines'] if r['period'] == period]
        end = max([45] + [p['half_clock_minute'] for r in groups for p in r['points']])
        for team, color in zip(teams, colors):
            group = next(r for r in groups if r['team'] == team)
            points = group['points']
            x = [0] + [p['half_clock_minute'] for p in points] + [end]
            y = [group['start_npxg']] + [p['cumulative_npxg'] for p in points] + [group['end_npxg']]
            ax.step(x, y, where='post', color=color, label=team.replace(" Women's", ''), linewidth=2)
            goals = [p for p in points if p['goal']]
            ax.scatter([p['half_clock_minute'] for p in goals], [p['cumulative_npxg'] for p in goals],
                       color=color, marker='*', s=130, zorder=3)
        ax.set_title('First half' if period == 1 else 'Second half · totals carried forward')
        ax.set_xlabel('Nominal minutes within this half')
        ax.set_xlim(0, end)
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(axis='y', alpha=.2)
    axes[0].set_ylim(0, max(r['end_npxg'] for r in evidence['timelines']) * 1.12 or 1)
    axes[0].set_ylabel('Cumulative model non-penalty xG')
    axes[0].legend(loc='upper left')
    fig.suptitle('France v Korea Republic · when did the chances arrive?\nFrozen educational distance-only model · stars mark shot goals', fontsize=13)
    fig.text(.5, .015, 'Separate clocks retain first-half added time. Plot ends at 45 minutes or last shot, not a verified whistle.\nData: StatsBomb Open Data. Flat sections mean no included shots; they do not measure possession.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .10, 1, .88])
    fig.savefig(ROOT / 'figures/33_cumulative_xg_timeline.png', dpi=160)
    plt.show()
    for group in evidence['timelines']:
        print(group['team'], 'half', group['period'], 'shots', group['shots'], 'half npxG', round(group['half_npxg'], 3))


if __name__ == '__main__':
    main()
