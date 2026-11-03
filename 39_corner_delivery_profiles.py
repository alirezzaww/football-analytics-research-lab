"""Lesson 39: stratify existing corner phases by recorded delivery technique.

A descriptive join, not a fitted model or a causal comparison of tactics.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATEGORIES = ('Inswinging', 'Outswinging', 'Straight', 'Other / unrecorded')


def category(technique):
    return technique if technique in CATEGORIES[:3] else CATEGORIES[3]


def summarize(rows):
    output = []
    for label in CATEGORIES:
        selected = [r for r in rows if r['category'] == label]
        count = len(selected)
        with_shot = sum(r['phase_has_shot'] for r in selected)
        output.append({'category': label, 'deliveries': count, 'corners_with_phase_shot': with_shot,
                       'phase_shot_rate': with_shot / count if count else None,
                       'phase_shots': sum(r['phase_shots'] for r in selected),
                       'phase_shot_goals': sum(r['phase_shot_goals'] for r in selected),
                       'corner_keys': [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in selected]})
    return output


def build_evidence():
    path = ROOT / 'data/38_france_corner_study_evidence.json'
    source = json.loads(path.read_text())
    spec = importlib.util.spec_from_file_location('delivery_profile_source', ROOT / '38_france_tournament_corners.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    assert helper.build_evidence() == source  # Reuse hash-checked cache/download and phase validation.
    rows = []
    for match in source['matches']:
        events = {r['id']: r for r in json.loads((ROOT / match['raw_input']['relative_path']).read_text())}
        for phase in match['phases']:
            event = events[phase['corner_id']]
            technique = event['pass'].get('technique', {}).get('name')
            rows.append({'match_id': match['fixture']['match_id'], 'corner_id': phase['corner_id'],
                         'opponent': match['opponent'], 'passer': event['player']['name'],
                         'raw_technique': technique, 'category': category(technique),
                         'phase_has_shot': bool(phase['shots']), 'phase_shots': len(phase['shots']),
                         'phase_shot_goals': sum(r['goal'] for r in phase['shots'])})
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'grouping_rule': 'Use pass.technique.name only. Inswinging, Outswinging and Straight retained; other/missing labels remain Other / unrecorded. No inference from foot, side or short-pass length.',
            'deliveries': rows, 'groups': summarize(rows),
            'scope': 'Same five France fixtures and fixed 15-second corner-phase rule. Unadjusted descriptive groups, not evidence that changing technique improves outcomes.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/39_corner_delivery_profiles_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    groups = evidence['groups']
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, group in enumerate(groups):
        if group['phase_shot_rate'] is not None:
            height = group['phase_shot_rate'] * 100
            ax.bar(i, height, color='#24658a' if i < 3 else '#8c9397', width=.55)
            ax.text(i, height + 2, f'{group["corners_with_phase_shot"]}/{group["deliveries"]} · {height:.1f}%', ha='center')
    ax.set_xticks(range(4), ['Inswinging', 'Outswinging', 'Straight', 'Other /\nunrecorded'])
    ax.set_ylim(0, 100)
    ax.set_ylabel('Deliveries associated with a phase shot (%)')
    ax.set_title('France: recorded delivery technique and shot association\nFive fixtures · same 15-second phase rule')
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.5, .02, 'Small unadjusted groups; delivery choice is not randomized. Nine labels are absent.\nDo not interpret the highest bar as the best tactic. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, 1])
    fig.savefig(ROOT / 'figures/42_corner_delivery_profiles.png', dpi=160)
    plt.show()
    for group in groups:
        print(group['category'], group['deliveries'], group['corners_with_phase_shot'], group['phase_shot_rate'])


if __name__ == '__main__':
    main()
