"""Lesson 42: classify recorded corner pass endpoints into disjoint pitch zones."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZONES = ('Six-yard box', 'Rest of penalty area', 'Outside penalty area', 'Endpoint unknown')


def endpoint_zone(location):
    if not isinstance(location, list) or len(location) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in location[:2]):
        return ZONES[3]
    x, y = location[:2]
    if 114 <= x <= 120 and 30 <= y <= 50:
        return ZONES[0]
    if 102 <= x <= 120 and 18 <= y <= 62:
        return ZONES[1]
    return ZONES[2]


def summarize(rows):
    groups = []
    for zone in ZONES:
        selected = [r for r in rows if r['endpoint_zone'] == zone]
        n = len(selected); positive = sum(r['phase_has_shot'] for r in selected)
        groups.append({'zone': zone, 'deliveries': n, 'corners_with_phase_shot': positive,
                       'phase_shot_rate': positive / n if n else None,
                       'corner_keys': [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in selected]})
    return groups


def build_evidence():
    path = ROOT / 'data/41_corner_side_evidence.json'
    source = json.loads(path.read_text())
    spec = importlib.util.spec_from_file_location('endpoint_side_source', ROOT / '41_corner_side_context.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    assert helper.build_evidence() == source
    study = json.loads((ROOT / 'data/38_france_corner_study_evidence.json').read_text())
    lookups = {m['fixture']['match_id']: {r['id']: r for r in json.loads((ROOT / m['raw_input']['relative_path']).read_text())} for m in study['matches']}
    rows = []
    for row in source['deliveries']:
        event = lookups[row['match_id']][row['corner_id']]
        end = event['pass'].get('end_location')
        rows.append({**row, 'end_location': end, 'pass_outcome': event['pass'].get('outcome', {}).get('name'),
                     'endpoint_zone': endpoint_zone(end)})
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'zone_rule': 'StatsBomb coordinates; six-yard box x in [114,120], y in [30,50]; rest of penalty area x in [102,120], y in [18,62] excluding six-yard box; all other finite points outside; absent/nonfinite points unknown.',
            'deliveries': rows, 'groups': summarize(rows),
            'scope': 'Recorded pass endpoints, not intended targets, confirmed attacking control or causal effects of aiming at a zone. Existing phase outcomes unchanged.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/42_corner_endpoint_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    from mplsoccer import VerticalPitch
    located = [r for r in evidence['deliveries'] if r['endpoint_zone'] != ZONES[3]]
    # Do not silently crop an endpoint behind halfway.
    half = all(r['end_location'][0] >= 60 for r in located)
    pitch = VerticalPitch(pitch_type='statsbomb', half=half, line_color='#9ba7ad', line_zorder=1)
    fig, ax = pitch.draw(figsize=(8, 7))
    fig.set_layout_engine(None)
    colors = ['#b77516', '#24658a', '#446b57']
    for zone, color in zip(ZONES[:3], colors):
        selected = [r for r in located if r['endpoint_zone'] == zone]
        pitch.scatter([r['end_location'][0] for r in selected], [r['end_location'][1] for r in selected],
                      color=color, s=65, alpha=.75, edgecolors='white', linewidths=.5,
                      label=f'{zone}: {len(selected)}', zorder=3, ax=ax)
    fig.suptitle('Where did the recorded corner passes end?\nFrance · 45 deliveries across five matches · attacks upward', fontsize=14)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5, .075), frameon=False, fontsize=10)
    fig.text(.5, .02, 'One dot per recorded endpoint; overlapping points may obscure counts. No missing endpoints here.\nEndpoints are not verified intended targets or attacking control. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.subplots_adjust(top=.83, bottom=.26)
    fig.savefig(ROOT / 'figures/45_corner_endpoint_zones.png', dpi=160)
    plt.show()
    for group in evidence['groups']:
        print(group['zone'], group['deliveries'], group['corners_with_phase_shot'])


if __name__ == '__main__':
    main()
