"""Lesson 41: add recorded corner side to the taker/technique overlap audit."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDES = ('Near y=0 touchline', 'Near y=80 touchline', 'Side unknown')
CATEGORIES = ('Inswinging', 'Outswinging', 'Straight', 'Other / unrecorded')


def corner_side(location):
    if not isinstance(location, list) or len(location) < 2:
        return SIDES[2]
    x, y = location[:2]
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (x, y)) or not (0 <= x <= 120 and 0 <= y <= 80):
        return SIDES[2]
    return SIDES[0] if y < 40 else SIDES[1] if y > 40 else SIDES[2]


def both_types(rows):
    kinds = {r['category'] for r in rows}
    return 'Inswinging' in kinds and 'Outswinging' in kinds


def build_evidence():
    path = ROOT / 'data/39_corner_delivery_profiles_evidence.json'
    source = json.loads(path.read_text())
    spec = importlib.util.spec_from_file_location('side_profile_source', ROOT / '39_corner_delivery_profiles.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    assert helper.build_evidence() == source  # Ensures all raw files and source joins remain hash-verified.
    study = json.loads((ROOT / source['source_path']).read_text())
    lookups = {m['fixture']['match_id']: {r['id']: r for r in json.loads((ROOT / m['raw_input']['relative_path']).read_text())}
               for m in study['matches']}
    rows = [{**r, 'start_location': lookups[r['match_id']][r['corner_id']].get('location'),
             'corner_side': corner_side(lookups[r['match_id']][r['corner_id']].get('location'))}
            for r in source['deliveries']]
    taker_sides = []
    for name in dict.fromkeys(r['passer'] for r in rows):
        for side in SIDES:
            selected = [r for r in rows if r['passer'] == name and r['corner_side'] == side]
            taker_sides.append({'passer': name, 'corner_side': side, 'deliveries': len(selected),
                                'both_recorded_types': both_types(selected),
                                'groups': helper.summarize(selected)})
    contexts = []
    for match_id, name, side in dict.fromkeys((r['match_id'], r['passer'], r['corner_side']) for r in rows):
        selected = [r for r in rows if (r['match_id'], r['passer'], r['corner_side']) == (match_id, name, side)]
        contexts.append({'match_id': match_id, 'passer': name, 'corner_side': side,
                         'opponent': selected[0]['opponent'], 'both_recorded_types': both_types(selected),
                         'corner_keys': [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in selected]})
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'side_rule': 'StatsBomb normalized start y<40 versus y>40; y=40, missing or invalid location remains unknown. Labels are coordinate sides, not stadium compass directions.',
            'deliveries': rows, 'taker_sides': taker_sides, 'taker_side_match_contexts': contexts,
            'contexts_with_both_types': sum(r['both_recorded_types'] for r in contexts),
            'scope': 'Descriptive overlap audit; recorded side is an additional context variable, not complete adjustment or proof that side determines technique.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/41_corner_side_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    names = list(dict.fromkeys(r['passer'] for r in evidence['deliveries']))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharex=True, sharey=True)
    colors = ['#24658a', '#b77516', '#446b57', '#969fa5']
    for ax, side in zip(axes, SIDES[:2]):
        totals = [0] * len(names)
        for label, color in zip(CATEGORIES, colors):
            counts = [next(g['deliveries'] for r in evidence['taker_sides'] if r['passer'] == name and r['corner_side'] == side
                           for g in r['groups'] if g['category'] == label) for name in names]
            ax.barh(range(len(names)), counts, left=totals, color=color, label=label)
            for i, n in enumerate(counts):
                if n:
                    ax.text(totals[i] + n / 2, i, str(n), ha='center', va='center', color='white', fontsize=10)
            totals = [a + b for a, b in zip(totals, counts)]
        ax.set_title(side)
        ax.set_xlabel('Recorded corner deliveries')
        ax.set_yticks(range(len(names)), names)
        ax.set_xlim(0, 22)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].invert_yaxis()
    fig.suptitle('Corner side changes the taker/technique comparison\nFrance · same five fixtures and 45 deliveries', fontsize=14)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5, .075), ncol=4, frameon=False)
    fig.text(.5, .02, 'Coordinate sides are normalized, not literal stadium left/right. All 45 locations have known sides.\nCounts describe delivery choice, not causal effectiveness. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .17, 1, .88])
    fig.savefig(ROOT / 'figures/44_corner_side_context.png', dpi=160)
    plt.show()
    print('Same taker, side and match contexts with both types:', evidence['contexts_with_both_types'])
    for row in evidence['taker_sides']:
        if row['deliveries']:
            print(row['passer'], row['corner_side'], [(g['category'], g['deliveries']) for g in row['groups']])


if __name__ == '__main__':
    main()
