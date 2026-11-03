"""Lesson 31: locate the same frozen-model shots on a pitch, by team and half.

A descriptive visualization extension. No new model or independent validation.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_evidence():
    path = ROOT / 'data/29_match_xg_evidence.json'
    source = json.loads(path.read_text())
    panels = []
    for team in source['teams']:
        for period in (1, 2):
            rows = [r for r in source['shots'] if r['team'] == team['team'] and r['period'] == period]
            # Plot original coordinates: mplsoccer handles vertical orientation.
            assert all(60 <= r['x'] <= 120 and 0 <= r['y'] <= 80 for r in rows), 'Half-pitch would hide a shot'
            panels.append({'team': team['team'], 'period': period, 'shots': len(rows),
                           'model_npxg': sum(r['model_probability'] for r in rows),
                           'mean_distance_template_m': sum(r['distance_template_m'] for r in rows) / len(rows) if rows else None,
                           'shot_ids': [r['id'] for r in rows]})
    assert sum(p['shots'] for p in panels) == len(source['shots'])
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'fixture': source['fixture'], 'panels': panels,
            'display_rule': 'StatsBomb original x,y; VerticalPitch half=True; all teams attack top. Circle area = probability * 1800 points squared; black stars mark goals.',
            'scope': 'Same 26 non-penalty shots, frozen distance-only probabilities; descriptive location comparison, not tactical causation.'}, source


def main():
    evidence, source = build_evidence()
    (ROOT / 'data/31_shot_location_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    from mplsoccer import VerticalPitch
    pitch = VerticalPitch(pitch_type='statsbomb', half=True, line_color='#9ba7ad', line_zorder=1)
    fig, axes = plt.subplots(2, 2, figsize=(11, 11))
    for i, (panel, ax) in enumerate(zip(evidence['panels'], axes.flat)):
        pitch.draw(ax=ax)
        rows = [r for r in source['shots'] if r['id'] in panel['shot_ids']]
        color = '#24658a' if i < 2 else '#b77516'
        pitch.scatter([r['x'] for r in rows], [r['y'] for r in rows],
                      s=[r['model_probability'] * 1800 for r in rows], color=color,
                      edgecolors='white', linewidths=.7, alpha=.8, zorder=3, ax=ax)
        goals = [r for r in rows if r['goal']]
        pitch.scatter([r['x'] for r in goals], [r['y'] for r in goals],
                      marker='*', s=75, color='black', zorder=4, ax=ax)
        name = panel['team'].replace(" Women's", '')
        ax.set_title(f"{name} · half {panel['period']}\n{panel['shots']} shots · {panel['model_npxg']:.3f} model npxG", fontsize=12, pad=14)
    # Identical area mapping and pitch dimensions in every panel.
    handles = [plt.scatter([], [], s=p * 1800, color='#657b88', alpha=.8, label=f'{p:.2f} xG') for p in [.05, .15, .30]]
    handles.append(plt.scatter([], [], marker='*', s=75, color='black', label='Goal'))
    fig.legend(handles=handles, loc='lower center', ncol=4, frameon=False, bbox_to_anchor=(.5, .045), labelspacing=1)
    fig.suptitle('Where did the chances come from? · France v Korea Republic\nBoth teams attack the top goal in every panel', fontsize=15)
    fig.text(.5, .015, 'Same shots as the timeline · frozen distance-only model · circle area reflects model xG\nData: StatsBomb Open Data. Locations show shots, not buildup or tactical causes.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.83, bottom=.15, hspace=.32, wspace=.15)
    fig.savefig(ROOT / 'figures/34_shot_location_maps.png', dpi=160)
    plt.show()
    for panel in evidence['panels']:
        print(panel['team'], panel['period'], 'mean reference distance', panel['mean_distance_template_m'])


if __name__ == '__main__':
    main()
