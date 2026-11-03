"""Lesson 33: describe body-part mix without changing the frozen xG model."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATEGORIES = ('Foot', 'Head', 'Other / unknown')


def category(body_part):
    if body_part in ('Left Foot', 'Right Foot'):
        return 'Foot'
    return 'Head' if body_part == 'Head' else 'Other / unknown'


def summarize(rows):
    groups = []
    for label in CATEGORIES:
        selected = [r for r in rows if category(r['body_part']) == label]
        count = len(selected)
        total = sum(r['model_probability'] for r in selected)
        groups.append({'category': label, 'shots': count, 'share_of_half_shots': count / len(rows) if rows else None,
                       'shot_goals': sum(r['goal'] for r in selected), 'model_npxg': total,
                       'mean_model_npxg': total / count if count else None, 'shot_ids': [r['id'] for r in selected]})
    return groups


def build_evidence():
    source_path = ROOT / 'data/29_match_xg_evidence.json'
    source = json.loads(source_path.read_text())
    # Reuse lesson 29's hash-checked single-fixture cache/download procedure.
    spec = importlib.util.spec_from_file_location('body_part_source', ROOT / '29_match_xg_summary.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    verified = helper.build_evidence()
    assert verified == source, 'Existing match ledger differs from raw-backed reconstruction'
    path = ROOT / source['raw_input']['relative_path']
    events = {r['id']: r for r in json.loads(path.read_text())}
    rows = [{**r, 'body_part': events[r['id']]['shot'].get('body_part', {}).get('name')}
            for r in source['shots']]
    panels = []
    for team in source['teams']:
        for period in (1, 2):
            selected = [r for r in rows if r['team'] == team['team'] and r['period'] == period]
            panels.append({'team': team['team'], 'period': period, 'total_shots': len(selected),
                           'groups': summarize(selected)})
    return {'source_path': source_path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'fixture': source['fixture'], 'raw_input': source['raw_input'], 'shots': rows, 'panels': panels,
            'scope': 'Body part is a descriptive tag, not a new model feature. Same frozen distance-only predictions; no fitting or fresh validation. Body part does not identify preferred or weak foot.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/33_body_part_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    panels = evidence['panels']
    fig, ax = plt.subplots(figsize=(10, 5))
    bottoms = [0] * len(panels)
    for label, color in zip(CATEGORIES, ['#24658a', '#b77516', '#8c9397']):
        values = [next(g['shots'] for g in p['groups'] if g['category'] == label) for p in panels]
        ax.bar(range(len(panels)), values, bottom=bottoms, color=color, label=label, width=.55)
        for i, value in enumerate(values):
            if value:
                ax.text(i, bottoms[i] + value / 2, str(value), ha='center', va='center', color='white', fontweight='bold')
        bottoms = [a + b for a, b in zip(bottoms, values)]
    ax.set_xticks(range(len(panels)), [p['team'].replace(" Women's", '') + f"\nhalf {p['period']}" for p in panels])
    ax.set_ylabel('Included non-penalty shots')
    ax.set_title('Shot body-part mix · France v Korea Republic\nContext tags added; distance-only model unchanged')
    ax.set_ylim(0, max(bottoms) + 4)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, loc='upper right')
    fig.text(.5, .02, 'Counts describe this match; they do not establish which body part is more effective.\nData: StatsBomb Open Data. Left/right foot identifies the contact foot, not preferred-foot status.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, 1])
    fig.savefig(ROOT / 'figures/36_shot_body_part_mix.png', dpi=160)
    plt.show()
    for panel in panels:
        print(panel['team'], panel['period'], [(g['category'], g['shots'], g['shot_goals']) for g in panel['groups']])


if __name__ == '__main__':
    main()
