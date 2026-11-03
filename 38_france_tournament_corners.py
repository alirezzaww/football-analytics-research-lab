"""Lesson 38: a five-match set-piece study with a fixed phase definition."""
import hashlib
import importlib.util
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def pool(matches):
    deliveries = sum(r['deliveries'] for r in matches)
    with_shot = sum(r['corners_with_phase_shot'] for r in matches)
    return {'matches': len(matches), 'deliveries': deliveries, 'corners_with_phase_shot': with_shot,
            'phase_shots': sum(r['phase_shots'] for r in matches),
            'phase_shot_goals': sum(r['phase_shot_goals'] for r in matches),
            'phase_shot_rate': with_shot / deliveries if deliveries else None}


def helper(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def build_evidence():
    protocol_path = ROOT / 'data/38_france_corner_study_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    raw_manifest_path = ROOT / 'data/27_frozen_evaluation_evidence.json'
    manifest = json.loads(raw_manifest_path.read_text())
    raw_records = {r['match_id']: r for r in manifest['raw_inputs']}
    scanner = helper('france_corner_phase', '36_corner_phase_analysis.py')
    linker = helper('france_corner_links', '34_header_assisting_passes.py')
    matches = []
    for fixture in protocol['fixtures']:
        record = raw_records[fixture['match_id']]
        path = ROOT / record['relative_path']
        if not path.exists():
            with urlopen(record['source_url'], timeout=60) as response:
                payload = response.read()
            if hashlib.sha256(payload).hexdigest() != record['sha256']:
                raise ValueError('Downloaded raw events differ from recorded source')
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
        events = sorted(json.loads(path.read_text()), key=lambda r: r['index'])
        lookup = {r['id']: r for r in events}
        included = {r['id']: {'goal': int(r['shot']['outcome']['name'] == 'Goal'), 'model_probability': None}
                    for r in events if r['type']['name'] == 'Shot' and r['period'] in protocol['periods_included']
                    and r['team']['name'] == protocol['team'] and r['shot']['type']['name'] != 'Penalty'}
        corners = [r for r in events if r['type']['name'] == 'Pass' and r['period'] in protocol['periods_included']
                   and r['team']['name'] == protocol['team'] and r['pass'].get('type', {}).get('name') == 'Corner']
        phases = []
        assigned = set()
        direct = 0
        for corner in corners:
            phase = scanner.phase_after(corner, events, included, protocol)
            for shot in phase['shots']:
                if shot['shot_id'] in assigned:
                    raise ValueError('Duplicate corner-phase assignment')
                assigned.add(shot['shot_id'])
                del shot['model_probability']  # No xG model inference is used in this counting study.
            target = corner['pass'].get('assisted_shot_id')
            if target:
                status, linked = linker.linked_pass(lookup[target], lookup)
                assert status == 'Verified reciprocal link' and linked['id'] == corner['id']
                direct += 1
            phases.append({'corner_id': corner['id'], 'period': corner['period'], 'minute': corner['minute'],
                           'second': corner['second'], 'direct_shot_id': target, **phase})
        with_shot = sum(bool(r['shots']) for r in phases)
        matches.append({'fixture': fixture, 'opponent': fixture['away_team'] if fixture['home_team'] == protocol['team'] else fixture['home_team'],
                        'raw_input': record, 'deliveries': len(corners), 'direct_linked_shots': direct,
                        'corners_with_phase_shot': with_shot, 'phase_shots': sum(len(r['shots']) for r in phases),
                        'phase_shot_goals': sum(s['goal'] for r in phases for s in r['shots']),
                        'phase_shot_rate': with_shot / len(corners) if corners else None,
                        'extra_time_deliveries': sum(r['period'] in (3, 4) for r in phases), 'phases': phases})
    # The original fixture must reproduce the existing 15-second phase memberships.
    previous = json.loads((ROOT / 'data/36_corner_phase_evidence.json').read_text())
    original = next(r for r in matches if r['fixture']['match_id'] == previous['fixture']['match_id'])
    reference = [r for r in previous['phases'] if r['team'] == protocol['team']]
    assert [[s['shot_id'] for s in r['shots']] for r in original['phases']] == [[s['shot_id'] for s in r['shots']] for r in reference]
    return {'protocol_path': protocol_path.relative_to(ROOT).as_posix(),
            'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'raw_manifest_path': raw_manifest_path.relative_to(ROOT).as_posix(),
            'raw_manifest_sha256': hashlib.sha256(raw_manifest_path.read_bytes()).hexdigest(),
            'matches': matches, 'pooled': pool(matches), 'scope': protocol['scope']}


def main():
    evidence = build_evidence()
    (ROOT / 'data/38_france_corner_study_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    rows = evidence['matches']
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, row in enumerate(rows):
        if row['phase_shot_rate'] is not None:
            ax.bar(i, row['phase_shot_rate'] * 100, color='#24658a', width=.55)
            ax.text(i, row['phase_shot_rate'] * 100 + 2, f'{row["corners_with_phase_shot"]}/{row["deliveries"]}', ha='center')
    overall = evidence['pooled']['phase_shot_rate'] * 100
    ax.axhline(overall, color='#b77516', linestyle='--', label=f'Pooled delivery rate: {overall:.1f}%')
    ax.set_xticks(range(len(rows)), [r['opponent'].replace(" Women's", '') + ('\n(includes extra time)' if r['extra_time_deliveries'] else '') for r in rows])
    ax.set_ylim(0, 100)
    ax.set_ylabel('Corner deliveries associated with a phase shot (%)')
    ax.set_title('France corner-phase shot association across five matches\nSame 15-second phase rule; match-specific denominators shown')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False)
    fig.text(.5, .02, 'Descriptive within-tournament variation, not an opponent-strength adjustment or causal comparison.\nData: StatsBomb Open Data. Phases 1–4 included; shootouts excluded.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, 1])
    fig.savefig(ROOT / 'figures/41_france_corner_match_variation.png', dpi=160)
    plt.show()
    for row in rows:
        print(row['opponent'], row['deliveries'], row['corners_with_phase_shot'], row['phase_shots'], row['phase_shot_goals'], row['extra_time_deliveries'])
    print('Pooled', evidence['pooled'])


if __name__ == '__main__':
    main()
