"""Lesson 37: vary only the corner-phase time limit, reporting every window."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_phase_helper():
    spec = importlib.util.spec_from_file_location('corner_window_phase', ROOT / '36_corner_phase_analysis.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    return helper


def build_evidence():
    phase_helper = load_phase_helper()
    source_path = ROOT / 'data/36_corner_phase_evidence.json'
    source = json.loads(source_path.read_text())
    assert phase_helper.build_evidence() == source
    protocol_path = ROOT / 'data/37_corner_window_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    base_rules = json.loads((ROOT / source['protocol_path']).read_text())
    corners = json.loads((ROOT / source['source_path']).read_text())
    match = json.loads((ROOT / corners['source_path']).read_text())
    events = sorted(json.loads((ROOT / source['raw_input']['relative_path']).read_text()), key=lambda r: r['index'])
    lookup = {r['id']: r for r in events}
    shot_lookup = {r['id']: r for r in match['shots']}
    results = []
    for window in protocol['windows_seconds_inclusive']:
        rules = copy.deepcopy(base_rules)
        rules['maximum_seconds_inclusive'] = window
        phases = []
        assigned = set()
        for corner in corners['corner_deliveries']:
            phase = phase_helper.phase_after(lookup[corner['id']], events, shot_lookup, rules)
            for shot in phase['shots']:
                if shot['shot_id'] in assigned:
                    raise ValueError('Duplicate corner assignment')
                assigned.add(shot['shot_id'])
            phases.append({'corner_id': corner['id'], 'team': corner['team'], **phase})
        summaries = []
        for team in corners['teams']:
            rows = [r for r in phases if r['team'] == team['team']]
            count = sum(bool(r['shots']) for r in rows)
            summaries.append({'team': team['team'], 'deliveries': len(rows),
                              'corners_with_shot': count, 'phase_shots': sum(len(r['shots']) for r in rows),
                              'phase_shot_goals': sum(s['goal'] for r in rows for s in r['shots']),
                              'corner_shot_rate': count / len(rows) if rows else None})
        results.append({'window_seconds': window, 'teams': summaries, 'phases': phases})
    reference = next(r for r in results if r['window_seconds'] == protocol['reference_window_seconds'])
    assert [r['shots'] for r in reference['phases']] == [r['shots'] for r in source['phases']]
    return {'source_path': source_path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
            'protocol_path': protocol_path.relative_to(ROOT).as_posix(),
            'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'fixture': source['fixture'], 'results': results,
            'scope': 'Same-match definition sensitivity, not new data, uncertainty intervals, causal evidence or model validation.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/37_corner_window_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    france = [r['teams'][0] for r in evidence['results']]
    windows = [r['window_seconds'] for r in evidence['results']]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(windows, [r['corner_shot_rate'] * 100 for r in france], marker='o', color='#24658a', linewidth=2)
    for window, row in zip(windows, france):
        ax.annotate(f'{row["corners_with_shot"]}/{row["deliveries"]}', (window, row['corner_shot_rate'] * 100),
                    xytext=(0, 10), textcoords='offset points', ha='center')
    ax.set_xticks(windows)
    ax.set_ylim(0, 65)
    ax.set_xlabel('Maximum seconds after the corner delivery (inclusive)')
    ax.set_ylabel('Corners associated with a shot (%)')
    ax.set_title('France: does the phase result depend on the time limit?\nSame 13 deliveries and boundary rules at every window')
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.5, .02, 'Definition sensitivity, not a confidence interval. A longer window is not automatically better.\nData: StatsBomb Open Data. Existing match and unchanged xG model.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, 1])
    fig.savefig(ROOT / 'figures/40_corner_window_sensitivity.png', dpi=160)
    plt.show()
    for result in evidence['results']:
        print(result['window_seconds'], result['teams'])


if __name__ == '__main__':
    main()
