"""Lesson 40: audit taker and opponent overlap before comparing delivery tactics.

Uses saved reporting records only; no refitting, downloads or causal adjustment.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def has_both_types(groups):
    counts = {r['category']: r['deliveries'] for r in groups}
    return counts.get('Inswinging', 0) > 0 and counts.get('Outswinging', 0) > 0


def build_evidence():
    path = ROOT / 'data/39_corner_delivery_profiles_evidence.json'
    source = json.loads(path.read_text())
    spec = importlib.util.spec_from_file_location('taker_profile_helper', ROOT / '39_corner_delivery_profiles.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    rows = source['deliveries']
    takers = []
    for name in dict.fromkeys(r['passer'] for r in rows):
        groups = helper.summarize([r for r in rows if r['passer'] == name])
        takers.append({'passer': name, 'groups': groups, 'both_recorded_types': has_both_types(groups)})
    contexts = []
    for match_id, name in dict.fromkeys((r['match_id'], r['passer']) for r in rows):
        selected = [r for r in rows if (r['match_id'], r['passer']) == (match_id, name)]
        groups = helper.summarize(selected)
        contexts.append({'match_id': match_id, 'passer': name, 'opponent': selected[0]['opponent'],
                         'groups': groups, 'both_recorded_types': has_both_types(groups)})
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'takers': takers, 'taker_match_contexts': contexts,
            'contexts_with_both_types': sum(r['both_recorded_types'] for r in contexts),
            'scope': 'Descriptive overlap audit of the same 45 deliveries. Positive counts indicate observed overlap, not adequate sample size, full matching or causal adjustment.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/40_corner_taker_overlap_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    import numpy as np
    takers = evidence['takers']
    counts = np.array([[r['deliveries'] for r in taker['groups']] for taker in takers])
    fig, ax = plt.subplots(figsize=(10, 5))
    heat = ax.imshow(counts, cmap='Blues', vmin=0, vmax=max(1, counts.max()), aspect='auto')
    ax.set_yticks(range(len(takers)), [r['passer'] for r in takers])
    ax.set_xticks(range(4), ['Inswinging', 'Outswinging', 'Straight', 'Other / unrecorded'])
    for i in range(len(takers)):
        for j in range(4):
            ax.text(j, i, str(counts[i, j]), ha='center', va='center', color='white' if counts[i, j] > counts.max() / 2 else '#172d3b')
    ax.set_title('Who took each delivery type? · France, five matches\nCell numbers are corner counts, not success rates')
    fig.colorbar(heat, ax=ax, label='Recorded deliveries')
    fig.text(.5, .02, 'Different taker mixtures complicate the overall delivery-type comparison.\nSparse overlap is not a controlled comparison. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .10, 1, 1])
    fig.savefig(ROOT / 'figures/43_corner_taker_overlap.png', dpi=160)
    plt.show()
    print('Taker/opponent contexts with both recorded types:', evidence['contexts_with_both_types'])
    for taker in takers:
        print(taker['passer'], [(g['category'], g['corners_with_phase_shot'], g['deliveries']) for g in taker['groups'][:2]])


if __name__ == '__main__':
    main()
