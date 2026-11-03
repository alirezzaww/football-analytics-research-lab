"""Lesson 34: use explicit event IDs to inspect passes assisting three headers.

No nearest-pass inference. Missing links remain missing. No model changes.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def linked_pass(shot, events):
    key = shot['shot'].get('key_pass_id')
    if not key:
        return 'No key-pass link recorded', None
    if key not in events:
        return 'Linked event unavailable', None
    event = events[key]
    if (event['type']['name'] != 'Pass' or event['period'] != shot['period']
            or event['team']['id'] != shot['team']['id'] or event['index'] >= shot['index']
            or event['possession'] != shot['possession']
            or event['pass'].get('assisted_shot_id') != shot['id']):
        raise ValueError('Explicit shot/pass link fails reciprocal, order or context checks')
    return 'Verified reciprocal link', event


def build_evidence():
    path = ROOT / 'data/33_body_part_evidence.json'
    source = json.loads(path.read_text())
    spec = importlib.util.spec_from_file_location('header_raw_source', ROOT / '29_match_xg_summary.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    verified = helper.build_evidence()  # Ensures the one-fixture raw cache is present and hash-checked.
    assert verified['raw_input'] == source['raw_input']
    raw_path = ROOT / source['raw_input']['relative_path']
    events = {r['id']: r for r in json.loads(raw_path.read_text())}
    rows = []
    for shot in source['shots']:
        if shot['body_part'] != 'Head':
            continue
        event = events[shot['id']]
        status, assist = linked_pass(event, events)
        item = {'shot_id': shot['id'], 'team': shot['team'], 'period': shot['period'],
                'minute': shot['minute'], 'second': shot['second'], 'shooter': event['player']['name'],
                'shot_location': event['location'], 'shot_outcome': event['shot']['outcome']['name'],
                'shot_type': event['shot']['type']['name'], 'play_pattern': event['play_pattern']['name'],
                'model_probability_unchanged': shot['model_probability'], 'link_status': status, 'pass': None}
        if assist:
            p = assist['pass']
            item['pass'] = {'id': assist['id'], 'passer': assist['player']['name'],
                            'minute': assist['minute'], 'second': assist['second'],
                            'start': assist['location'], 'end': p['end_location'],
                            'type': p.get('type', {}).get('name'), 'cross_flag': p.get('cross'),
                            'height': p.get('height', {}).get('name'),
                            'assisted_shot_id': p['assisted_shot_id']}
        rows.append(item)
    return {'source_path': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'fixture': source['fixture'], 'raw_input': source['raw_input'], 'headers': rows,
            'scope': 'All headers in the existing 26-shot match ledger. Explicit assisting pass only, not a complete sequence, crossing-success rate, causal credit or fresh validation.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/34_header_assists_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    from mplsoccer import Pitch
    headers = evidence['headers']
    fig, axes = plt.subplots(1, len(headers), figsize=(15, 5), squeeze=False)
    pitch = Pitch(pitch_type='statsbomb', half=True, line_color='#98a5ad')
    for ax, row in zip(axes.flat, headers):
        pitch.draw(ax=ax)
        p = row['pass']
        label = row['link_status']
        if p:
            pitch.arrows(p['start'][0], p['start'][1], p['end'][0], p['end'][1],
                         color='#24658a', width=2, headwidth=4, headlength=4, ax=ax, zorder=2)
            pitch.scatter(p['end'][0], p['end'][1], s=35, color='#24658a', ax=ax, zorder=3)
            label = 'Corner pass' if p['type'] == 'Corner' else 'Cross flagged' if p['cross_flag'] is True else 'Other linked pass'
        pitch.scatter(row['shot_location'][0], row['shot_location'][1], marker='*', s=170, color='#b77516', ax=ax, zorder=4)
        ax.set_title(f"{row['minute']:02d}:{row['second']:02d} · {label}\n{row['shooter']} · {row['shot_outcome']}", fontsize=11)
    fig.suptitle('Trace the pass, then describe the header · France v Korea Republic\nAll three headers in the existing shot sample · teams attack right', fontsize=14)
    fig.text(.5, .03, 'Blue arrow: recorded pass start → end; blue dot: pass end; gold star: header location (not necessarily identical).\nExplicit linked events only; other actions omitted. 46:57 is first-half added time. Data: StatsBomb Open Data.', ha='center', fontsize=10)
    fig.subplots_adjust(top=.78, bottom=.17, wspace=.2)
    fig.savefig(ROOT / 'figures/37_header_assisting_passes.png', dpi=160)
    plt.show()
    for row in headers:
        print(row['minute'], row['second'], row['shooter'], row['pass']['passer'] if row['pass'] else row['link_status'])


if __name__ == '__main__':
    main()
