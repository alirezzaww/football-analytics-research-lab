"""Lesson 79: join recorded Pressure links to opponent Pass outcomes."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {'minutes': 'data/64_fullback_playing_time_evidence.json',
           'pressure': 'data/73_fullback_pressure_activity_evidence.json'}
spec = importlib.util.spec_from_file_location('pressure73', ROOT/'73_fullback_pressure_activity.py')
pressure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pressure)
READING = 'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure'
SPECIFICATION = 'https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf'


def references(event):
    values = event.get('related_events', [])
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values) or len(set(values)) != len(values):
        raise ValueError('Related-event references must be a unique list of IDs')
    return values


def pass_category(event):
    detail = event['pass']
    if 'outcome' not in detail:
        return 'completed', None
    label = detail['outcome']['name']
    if label in {'Incomplete', 'Out', 'Pass Offside'}:
        return 'not_completed', label
    if label in {'Unknown', 'Injury Clearance'}:
        return 'unassessable', label
    raise ValueError('Unexpected pass outcome: '+str(label))


def link_match(events, rows):
    lookup = {e['id']: e for e in events}
    if len(lookup) != len(events):
        raise ValueError('Duplicate raw event ID')
    enriched = []
    links = []
    for row in rows:
        event = lookup[row['event_id']]
        if (event['type']['name'] != 'Pressure'
                or (event['team']['id'], event['player']['id']) != (row['team_id'], row['player_id'])
                or any(event[k] != row[k] for k in ('period', 'timestamp', 'index'))):
            raise ValueError('Pressure identity or timing differs')
        ids = references(event)
        kinds = {}
        opponent_pass_ids = []
        same_team_pass_ids = []
        for identifier in ids:
            target = lookup[identifier]  # Unresolved IDs stop the join instead of silently disappearing.
            kind = target['type']['name']
            kinds[kind] = kinds.get(kind, 0)+1
            if kind != 'Pass':
                continue
            if target['team']['id'] == row['team_id']:
                same_team_pass_ids.append(identifier)
                continue
            if target['period'] != row['period']:
                raise ValueError('Linked opponent pass crosses period boundary')
            category, outcome = pass_category(target)
            reciprocal = row['event_id'] in references(target)
            opponent_pass_ids.append(identifier)
            links.append({'match_id': row['match_id'], 'team_id': row['team_id'], 'player_id': row['player_id'],
                          'pressure_id': row['event_id'], 'pressure_timestamp': row['timestamp'],
                          'pass_id': identifier, 'pass_team_id': target['team']['id'],
                          'pass_team_name': target['team']['name'], 'pass_player_id': target['player']['id'],
                          'pass_player_name': target['player']['name'], 'period': target['period'],
                          'pass_index': target['index'], 'pass_timestamp': target['timestamp'],
                          'pass_start_minus_pressure_start_ms': pressure.time_module.cohort_module.raw.scanner.timestamp_milliseconds(target['timestamp'])-pressure.time_module.cohort_module.raw.scanner.timestamp_milliseconds(row['timestamp']),
                          'raw_outcome': outcome, 'category': category, 'reciprocal': reciprocal,
                          'pass_type': target['pass'].get('type', {}).get('name')})
        enriched.append({**row, 'related_event_ids': ids, 'related_event_type_counts': kinds,
                         'linked_opponent_pass_ids': opponent_pass_ids, 'linked_same_team_pass_ids': same_team_pass_ids})
    return enriched, links


def summarize(player, rows, links):
    key = (player['team_id'], player['player_id'])
    if len(rows) != player['recorded_pressures'] or len({(r['match_id'], r['event_id']) for r in rows}) != len(rows):
        raise ValueError('Pressure coverage differs')
    if any((r['team_id'], r['player_id']) != key or r['match_id'] not in player['qualifying_match_ids'] for r in rows+links):
        raise ValueError('Join identity or fixtures differ')
    expected = {(r['match_id'], r['event_id'], identifier) for r in rows for identifier in r['linked_opponent_pass_ids']}
    actual = [(r['match_id'], r['pressure_id'], r['pass_id']) for r in links]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError('Pressure-pass edge coverage differs')
    unique = {}
    for link in links:
        pass_key = (link['match_id'], link['pass_id'])
        fields = {k: link[k] for k in ('match_id', 'pass_id', 'pass_team_id', 'pass_team_name', 'pass_player_id',
                                       'pass_player_name', 'period', 'pass_index', 'pass_timestamp', 'raw_outcome', 'category', 'pass_type')}
        if pass_key not in unique:
            unique[pass_key] = {**fields, 'pressure_ids': []}
        elif any(unique[pass_key][k] != v for k, v in fields.items()):
            raise ValueError('Same pass has inconsistent metadata')
        unique[pass_key]['pressure_ids'].append(link['pressure_id'])
    counts = {label: sum(r['category'] == label for r in unique.values()) for label in ('completed', 'not_completed', 'unassessable')}
    assessed = counts['completed']+counts['not_completed']
    return {**player, 'pressures_with_linked_opponent_pass': sum(bool(r['linked_opponent_pass_ids']) for r in rows),
            'pressures_without_linked_opponent_pass': sum(not r['linked_opponent_pass_ids'] for r in rows),
            'opponent_pass_link_count': len(links), 'nonreciprocal_opponent_pass_links': sum(not r['reciprocal'] for r in links),
            'unique_linked_opponent_passes': list(unique.values()), 'linked_pass_category_counts': counts,
            'assessable_unique_linked_passes': assessed,
            'not_completed_share_of_assessable_linked_passes_pct': 100*counts['not_completed']/assessed if assessed else None}


def build_evidence(allow_download=True):
    data = {k: json.loads((ROOT/p).read_text()) for k, p in SOURCES.items()}
    rows = []
    links = []
    for audit in data['minutes']['match_audits']:
        selected = [r for r in data['pressure']['rows'] if r['match_id'] == audit['match_id']]
        if selected:
            events = pressure.time_module.cohort_module.raw.load_events(audit['raw_input'], allow_download)
            matched, edges = link_match(events, selected)
            rows.extend(matched); links.extend(edges)
    keyed = {(r['match_id'], r['event_id']): r for r in rows}
    if len(keyed) != len(rows) or len(rows) != len(data['pressure']['rows']):
        raise ValueError('Join does not preserve pressure membership')
    rows = [keyed[(r['match_id'], r['event_id'])] for r in data['pressure']['rows']]
    players = [summarize(p, [r for r in rows if (r['team_id'], r['player_id']) == (p['team_id'], p['player_id'])],
                         [r for r in links if (r['team_id'], r['player_id']) == (p['team_id'], p['player_id'])]) for p in data['pressure']['players']]
    examples = [next(r for r in links if r['player_id'] == identifier) for identifier in (10178, 15249)]
    return {'competition': data['pressure']['competition'], 'season': '2019', 'competition_id': 72, 'season_id': 30,
            'course_reading': {'lesson': 'Soccermatics Lesson 3: Statistical scouting', 'section': 'Context: what to measure', 'url': READING},
            'definition_url': SPECIFICATION,
            'source_files': {k: {'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k, p in SOURCES.items()},
            'rows': rows, 'links': links, 'players': players, 'examples': examples,
            'rule': 'Read directed related_events from each selected Pressure start; join IDs within fixture to opposite-team Pass events in the same period. Save all link types and reciprocity. No nearest-event, possession-label, timing-window, location or restart-delivery filter. Deduplicate passes by (match,pass_id) within player before counting outcomes. Completed=no outcome; Incomplete/Out/Pass Offside=not completed; Unknown/Injury Clearance=unassessable.',
            'scope': 'Observed outcomes of provider-linked opponent passes, not a causal pressure-success rate, official Pressure Regains or unique team outcomes. Pass and pressure starts can overlap rather than be strictly sequential. A missing pass link is not a failed pressure; it may link to another action or have no recorded link. Across different players the same pass can recur.'}


def render_report(evidence):
    lines = []
    for p in sorted(evidence['players'], key=lambda p: (p['team_name'], p['player_name'])):
        c = p['linked_pass_category_counts']
        lines.append(f"- **{p['team_name']} — {p['player_name']}**: {p['pressures_with_linked_opponent_pass']}/{p['recorded_pressures']} pressures link to an opponent pass; {len(p['unique_linked_opponent_passes'])} unique passes: {c['completed']} completed, {c['not_completed']} not completed, {c['unassessable']} unassessable. Nonreciprocal pass links: {p['nonreciprocal_opponent_pass_links']}.")
    examples = '\n'.join(f"- Match {r['match_id']}, period {r['period']}: pressure `{r['pressure_id']}` at {r['pressure_timestamp']} links to {r['pass_player_name']}'s pass `{r['pass_id']}` at {r['pass_timestamp']}. Recorded outcome: {r['raw_outcome'] or 'Completed (no outcome field)'}. Reciprocal: {r['reciprocal']}." for r in evidence['examples'])
    return f'''# Join pressure actions to linked opponent passes

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Context: what to measure]({READING}). Custom assisted extension.
Definition: [StatsBomb specification — related_events and Pass outcome]({SPECIFICATION}). Related-event IDs connect recorded observations; a relationship is not proof that pressure caused an outcome.

## Method and denominator

{evidence['rule']}

All original 2,034 pressure rows and 35 profiles are preserved, including missing locations. A pressure may link to no passes, one pass or more; other event types remain represented in link-type counts. Unresolved or duplicate IDs stop the join. Reciprocal references are recorded and checked, rather than silently presumed. Same-team passes are logged separately and excluded from opponent-pass results. Restart deliveries can remain because this is a distinct directly linked-event question, not lesson 65's eligible-passing denominator. A related pass need not start after pressure starts; no arbitrary five-second cutoff is applied.

Outcome counts use unique (fixture, pass ID) records within each player's links. Repeated links to the same pass do not increase that player's pass denominator. The saved non-completion share uses only unique linked passes with assessable outcomes; an empty assessable set means undefined. Unknown/Injury Clearance outcomes stay visible. Passes may still recur between different player profiles, so summing profiles does not yield unique team passes. Missing links are not an outcome observation.

## All profiles

{chr(10).join(lines)}

## First linked-pass examples for the two familiar players

{examples}

## Interpretation

This records what happened to the linked passes. It does not establish whether pressure caused incompletion or whether the pressure itself was effective. A completed pass might be backwards and helpful to the defending team; an incomplete pass might have gone wrong for another reason. Links do not cover every pressure or every on-ball action. Small, different selected subsets are not fair player-success comparisons, control groups or interchangeable recruitment recommendations. Earlier possession-proxy results remain unchanged.

## Reproduce

Run `python 79_pressure_linked_passes.py` in Spyder. [Evidence](../data/79_pressure_linked_passes_evidence.json) · [Lesson](../lessons/0061-pressure-linked-passes.html).
Source: StatsBomb Open Data. Assisted event-ID join; no footage review or independent mastery claimed.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/79_pressure_linked_passes_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/62_pressure_linked_passes.md').write_text(render_report(evidence))
    print('Pressure rows', len(evidence['rows']), 'opponent-pass edges', len(evidence['links']))
    for p in evidence['players']:
        if p['player_id'] in (10178, 15249):
            print(p['player_name'], p['pressures_with_linked_opponent_pass'], len(p['unique_linked_opponent_passes']), p['linked_pass_category_counts'])


if __name__ == '__main__':
    main()
