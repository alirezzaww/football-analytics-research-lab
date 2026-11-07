"""Lesson 78: action team versus possession-sequence label in unclear cases."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {'minutes': 'data/64_fullback_playing_time_evidence.json',
           'outcomes': 'data/77_fullback_next_possession_evidence.json'}
spec = importlib.util.spec_from_file_location('next77', ROOT/'77_fullback_next_possession.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
SPECIFICATION = 'https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf'
READING = 'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'


def event_summary(event):
    return {'event_id': event['id'], 'index': event['index'], 'period': event['period'],
            'timestamp': event['timestamp'], 'type': event['type']['name'],
            'team_id': event.get('team', {}).get('id'), 'team_name': event.get('team', {}).get('name'),
            'possession_id': event['possession'], 'possession_team_id': event['possession_team']['id'],
            'possession_team_name': event['possession_team']['name']}


def audit_match(events, rows):
    starts = {(s['period'], s['possession']): s for s in previous.possession_starts(events)}
    ordered = sorted(events, key=lambda e: e['index'])
    lookup = {e['id']: (i, e) for i, e in enumerate(ordered)}
    output = []
    for row in rows:
        position, event = lookup[row['event_id']]
        if (row['outcome_status'] != 'already_own_possession' or event['type']['name'] != 'Pressure'
                or (event['team']['id'], event['player']['id']) != (row['team_id'], row['player_id'])
                or event['possession_team']['id'] != row['team_id']
                or event['possession'] != row['pressure_possession_id']
                or event['possession_team']['id'] != row['pressure_possession_team_id']
                or any(event[k] != row[k] for k in ('period', 'index', 'timestamp'))):
            raise ValueError('Selected own-labelled pressure differs from source')
        key = (event['period'], event['possession'])
        start = starts[key]
        group = [e for e in ordered if (e['period'], e['possession']) == key]
        opponent_actions = [e for e in group if e['type']['name'] in ('Pass', 'Carry')
                            and e['team']['id'] != event['possession_team']['id']]
        nearby = [event_summary(e) for e in ordered[max(0, position-3):position+4] if e['period'] == event['period']]
        delay = previous.milliseconds(event)-start['time_ms']
        output.append({'match_id': row['match_id'], 'team_id': row['team_id'], 'player_id': row['player_id'],
                       'event_id': row['event_id'], 'pressure': event_summary(event),
                       'labelled_possession_start': start, 'pressure_minus_start_ms': delay,
                       'timing_relation': 'pressure_after_start' if delay > 0 else 'same_time' if delay == 0 else 'pressure_before_start',
                       'opponent_pass_or_carry_ids_in_labelled_sequence': [e['id'] for e in opponent_actions],
                       'nearby_events': nearby})
    return output


def summarize(player, rows):
    expected = player['outcome_status_counts'].get('already_own_possession', 0)
    if len(rows) != expected or len({(r['match_id'], r['event_id']) for r in rows}) != len(rows):
        raise ValueError('Own-labelled pressure coverage differs')
    if any((r['team_id'], r['player_id']) != (player['team_id'], player['player_id'])
           or r['match_id'] not in player['qualifying_match_ids'] for r in rows):
        raise ValueError('Audit player or fixture differs')
    return {**player, 'audited_own_labelled_pressures': len(rows),
            'own_labelled_with_opponent_pass_or_carry_in_sequence': sum(bool(r['opponent_pass_or_carry_ids_in_labelled_sequence']) for r in rows),
            'timing_relation_counts': {label: sum(r['timing_relation'] == label for r in rows)
                                      for label in ('pressure_after_start', 'same_time', 'pressure_before_start')}}


def build_evidence(allow_download=True):
    data = {k: json.loads((ROOT/p).read_text()) for k, p in SOURCES.items()}
    selected = [r for r in data['outcomes']['rows'] if r['outcome_status'] == 'already_own_possession']
    rows = []
    for audit in data['minutes']['match_audits']:
        own = [r for r in selected if r['match_id'] == audit['match_id']]
        if own:
            events = previous.pressure.time_module.cohort_module.raw.load_events(audit['raw_input'], allow_download)
            rows.extend(audit_match(events, own))
    if {(r['match_id'], r['event_id']) for r in rows} != {(r['match_id'], r['event_id']) for r in selected} or len(rows) != len(selected):
        raise ValueError('Full audit membership differs')
    players = [summarize(p, [r for r in rows if (r['team_id'], r['player_id']) == (p['team_id'], p['player_id'])]) for p in data['outcomes']['players']]
    examples = [next(r for r in rows if r['player_id'] == identifier) for identifier in (10178, 15249)]
    return {'competition': data['outcomes']['competition'], 'season': '2019', 'competition_id': 72, 'season_id': 30,
            'course_reading': {'lesson': 'Soccermatics Lesson 3: Statistical scouting', 'section': 'Normalisation → Pressure Regains', 'url': READING},
            'definition_url': SPECIFICATION,
            'source_files': {k: {'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k, p in SOURCES.items()},
            'players': players, 'rows': rows, 'examples': examples,
            'rule': 'Audit only lesson 77 already_own_possession rows. Compare pressure time with first-index event time of its same-period possession ID; list opponent Pass/Carry events anywhere in that same labelled sequence; show up to three adjacent indexed events on each side in the same period. Do not change any lesson 77 result.',
            'scope': 'team identifies the event actor side; possession_team identifies the side that started the recorded sequence in control. Opponent Pass/Carry occurrence is a property of that labelled sequence, not proof of a specific pressure outcome, an annotation error or a continuously controlled interval. Nearby rows are illustrative, not full footage. Audit counts are pressures, not unique possession sequences.'}


def render_report(evidence):
    rows = evidence['rows']
    after = sum(r['timing_relation'] == 'pressure_after_start' for r in rows)
    mixed = sum(bool(r['opponent_pass_or_carry_ids_in_labelled_sequence']) for r in rows)
    examples = []
    for example in evidence['examples']:
        player = next(p for p in evidence['players'] if p['player_id'] == example['player_id'] and p['team_id'] == example['team_id'])
        timeline = '\n'.join(f"{e['index']:>4}  {e['timestamp']}  {e['type']:<15} actor={e['team_name']} | possession={e['possession_id']} ({e['possession_team_name']})" for e in example['nearby_events'])
        examples.append(f"### {player['player_name']} — match {example['match_id']}, period {example['pressure']['period']}\n\n```text\n{timeline}\n```\n\nPressure ID: `{example['event_id']}`. Its sequence's first-index event precedes pressure start by {example['pressure_minus_start_ms']/1000:.3f} seconds. Opponent Pass/Carry records in that complete labelled sequence: {len(example['opponent_pass_or_carry_ids_in_labelled_sequence'])}.")
    profiles = '\n'.join(f"- {p['team_name']} — {p['player_name']}: {p['audited_own_labelled_pressures']} audited own-labelled pressures; {p['own_labelled_with_opponent_pass_or_carry_in_sequence']} have an opponent Pass/Carry somewhere in their labelled sequence." for p in sorted(evidence['players'], key=lambda p: (p['team_name'], p['player_name'])))
    return f'''# Action team is not the possession-sequence label

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Normalisation, Pressure Regains]({READING}). This audit is our custom extension.
Primary field definitions: [StatsBomb specification — team, possession and possession_team]({SPECIFICATION}). The specification identifies possession_team as the team that started the sequence in control; new possession sequences require established control, and consecutive sequences can belong to the same team.

## Finding

Lesson 77 kept 240 own-labelled pressure cases unclear, plus one separate period-end case. We audited all 240 own-labelled cases: **{after}** occur after their own labelled sequence's first event timestamp; **{mixed}** belong to sequences containing at least one opponent Pass or Carry. The latter is a sequence-level observation; the opponent action may be before or after the particular pressure and need not be adjacent. Several pressure rows can share the same sequence and opponent events, so these counts are not unique sequences or independent samples.

We found no pressure-before-sequence-start case in this selected subset. That check does not prove all match timestamps are correctly ordered or that every label has been validated. The initial idea that these cases might be clock-order anomalies was not supported by this specific comparison.

## The field distinction

- team: the side performing the recorded event.
- possession_team: the side that started the labelled sequence in control.

A Scotland pass can therefore sit inside a sequence labelled England. Do not treat the sequence label as a frame-by-frame statement of who touches the ball or proof of continuous control. Equally, an opponent touch does not alone establish that a new controlled possession should have been labelled. We have not reviewed footage or demonstrated a provider error.

## Two indexed context examples

{chr(10).join(examples)}

## All profiles (alphabetical)

{profiles}

## What changes?

Nothing in lesson 77's results. Bronze's 21 and Majri's 18 own-labelled pressure cases remain unclear for that narrowly defined proxy. This audit gives a reason to inspect the label semantics rather than count all unclear rows as failures, relabel events by guesswork or claim exact official Pressure Regains. We do not infer individual ball-winning credit, actual recovery times or pressure causation from adjacent event rows.

## Reproduce

Run `python 78_pressure_possession_label_audit.py` in Spyder. [Evidence](../data/78_pressure_possession_label_audit_evidence.json) · [Lesson](../lessons/0060-pressure-possession-labels.html).
Assisted code/data audit; no independent mastery or video observation claimed.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/78_pressure_possession_label_audit_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/61_pressure_possession_label_audit.md').write_text(render_report(evidence))
    print('Audited', len(evidence['rows']))
    print('Sequences with opponent Pass/Carry, counted per pressure:', sum(bool(r['opponent_pass_or_carry_ids_in_labelled_sequence']) for r in evidence['rows']))
    for p in evidence['players']:
        if p['player_id'] in (10178, 15249):
            print(p['player_name'], p['audited_own_labelled_pressures'], p['own_labelled_with_opponent_pass_or_carry_in_sequence'], p['timing_relation_counts'])


if __name__ == '__main__':
    main()
