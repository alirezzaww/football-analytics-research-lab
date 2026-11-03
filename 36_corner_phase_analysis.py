"""Lesson 36: compare explicit direct links with a bounded corner-phase proxy."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def timestamp_milliseconds(timestamp):
    h, m, s = timestamp.split(':')
    return int(h) * 3600000 + int(m) * 60000 + round(float(s) * 1000)


def phase_after(corner, events, included_shots, protocol):
    start = timestamp_milliseconds(corner['timestamp'])
    selected = []
    stop = 'End of available events'
    for event in events:
        if event['index'] <= corner['index']:
            continue
        if event['period'] != corner['period']:
            stop = 'Period changed'; break
        if event['possession'] != corner['possession']:
            stop = 'Possession changed'; break
        elapsed = (timestamp_milliseconds(event['timestamp']) - start) / 1000
        if elapsed < 0:
            raise ValueError('Nonmonotonic within-period event timestamps')
        if elapsed > protocol['maximum_seconds_inclusive']:
            stop = 'Time limit'; break
        if event['type']['name'] == 'Pass' and event['pass'].get('type', {}).get('name') in protocol['restart_pass_types']:
            stop = 'New restart'; break
        if event['id'] in included_shots and event['team']['id'] == corner['team']['id']:
            selected.append({'shot_id': event['id'], 'elapsed_seconds': elapsed,
                             'goal': included_shots[event['id']]['goal'],
                             'model_probability': included_shots[event['id']]['model_probability']})
        if event['type']['name'] == 'Shot' and event['shot']['outcome']['name'] == 'Goal':
            stop = 'Goal'; break
        if event['type']['name'] in ('Own Goal Against', 'Own Goal For'):
            stop = 'Own goal'; break
    return {'shots': selected, 'stop_reason': stop}


def build_evidence():
    protocol_path = ROOT / 'data/36_corner_phase_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    path = ROOT / 'data/35_corner_delivery_evidence.json'
    source = json.loads(path.read_text())
    spec = importlib.util.spec_from_file_location('phase_raw_source', ROOT / '29_match_xg_summary.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    match = helper.build_evidence()
    assert match['raw_input'] == source['raw_input']
    events = sorted(json.loads((ROOT / source['raw_input']['relative_path']).read_text()), key=lambda e: e['index'])
    lookup = {r['id']: r for r in events}
    shot_lookup = {r['id']: r for r in match['shots']}
    phases = []
    seen = set()
    for delivery in source['corner_deliveries']:
        result = phase_after(lookup[delivery['id']], events, shot_lookup, protocol)
        for shot in result['shots']:
            if shot['shot_id'] in seen:
                raise ValueError('Shot assigned to more than one corner')
            seen.add(shot['shot_id'])
        phases.append({'corner_id': delivery['id'], 'team': delivery['team'], 'period': delivery['period'],
                       'minute': delivery['minute'], 'second': delivery['second'],
                       'direct_shot_id': delivery['assisted_shot_id'], **result})
    teams = []
    for team in source['teams']:
        rows = [r for r in phases if r['team'] == team['team']]
        with_shot = sum(bool(r['shots']) for r in rows)
        shot_rows = [s for r in rows for s in r['shots']]
        teams.append({'team': team['team'], 'deliveries': len(rows),
                      'direct_linked_shots': team['direct_linked_shots'],
                      'corners_with_phase_shot': with_shot, 'phase_shots': len(shot_rows),
                      'phase_shot_goals': sum(r['goal'] for r in shot_rows),
                      'phase_shot_rate': with_shot / len(rows) if rows else None,
                      'direct_shot_link_rate': team['recorded_direct_shot_link_rate']})
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'protocol_path': protocol_path.relative_to(ROOT).as_posix(),
            'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'fixture': source['fixture'], 'raw_input': source['raw_input'], 'phases': phases, 'teams': teams,
            'scope': protocol['limitations']}


def main():
    evidence = build_evidence()
    (ROOT / 'data/36_corner_phase_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    france = evidence['teams'][0]
    fig, ax = plt.subplots(figsize=(9, 5))
    values = [france['direct_shot_link_rate'] * 100, france['phase_shot_rate'] * 100]
    ax.bar(['Recorded direct shot link', 'Shot in bounded corner phase'], values, color=['#24658a', '#b77516'], width=.5)
    for i, (value, count) in enumerate(zip(values, [france['direct_linked_shots'], france['corners_with_phase_shot']])):
        ax.text(i, value + 1, f'{count}/{france["deliveries"]} · {value:.1f}%', ha='center')
    ax.set_ylim(0, max(values) + 12)
    ax.set_ylabel('Percentage of the same 13 deliveries')
    ax.set_title('France: the definition changes what we count\nSame match and denominator · different shot-association rules')
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.5, .02, 'Phase proxy: same possession, ≤15 seconds, ends at restart/period/goal boundaries.\nAssociation, not causal attribution. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .10, 1, 1])
    fig.savefig(ROOT / 'figures/39_corner_phase_comparison.png', dpi=160)
    plt.show()
    for team in evidence['teams']:
        print(team)
    for row in evidence['phases']:
        if row['shots']:
            print(row['minute'], row['second'], row['direct_shot_id'], row['shots'])


if __name__ == '__main__':
    main()
