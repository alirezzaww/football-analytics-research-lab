"""Lesson 74: pressure activity relative to same-window opponent passing volume."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {'minutes': 'data/64_fullback_playing_time_evidence.json',
           'pressure': 'data/73_fullback_pressure_activity_evidence.json'}
spec = importlib.util.spec_from_file_location('passing65', ROOT/'65_fullback_passing_per90.py')
passing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(passing)


def opponent_windows(events, audit, targets):
    """Count eligible opponent attempts inside each target's time AND order bounds."""
    rows = passing.count_match(events, audit, audit['intervals'])
    teams = {r['team_id'] for r in audit['intervals']}
    if len(teams) != 2:
        raise ValueError('Expected exactly two teams')
    lookup = {e['id']: e for e in events}
    offsets = {p['period']: sum(q['length_ms'] for q in audit['periods'] if q['period'] < p['period'])
               for p in audit['periods']}
    result = []
    for target in targets:
        if target['team_id'] not in teams:
            raise ValueError('Target team is outside fixture')
        opponent = next(t for t in teams if t != target['team_id'])
        identifiers = [identifier for row in rows if row['team_id'] == opponent
                       for identifier in row['attempt_ids']]
        begin = lookup[target['start_event_id']]['index']
        end = lookup[target['end_event_id']]['index']
        selected = []
        for identifier in sorted(identifiers, key=lambda i: lookup[i]['index']):
            event = lookup[identifier]
            when = offsets[event['period']] + passing.time_module.cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])
            if target['start_ms'] <= when <= target['end_ms'] and begin <= event['index'] <= end:
                selected.append(identifier)
        result.append({'match_id': audit['match_id'], 'team_id': target['team_id'],
                       'player_id': target['player_id'], 'opponent_team_id': opponent,
                       'start_ms': target['start_ms'], 'end_ms': target['end_ms'],
                       'opponent_attempt_ids': selected})
    return result


def summarize(player, windows):
    keys = [(w['match_id'], w['team_id'], w['player_id']) for w in windows]
    expected = {(m, player['team_id'], player['player_id']) for m in player['qualifying_match_ids']}
    if len(set(keys)) != len(keys) or set(keys) != expected:
        raise ValueError('Opponent exposure windows differ from player fixtures/identity')
    if player['duration_ms'] <= 0 or sum(w['end_ms']-w['start_ms'] for w in windows) != player['duration_ms']:
        raise ValueError('Opponent exposure differs from registered minutes')
    for window in windows:
        if window['opponent_team_id'] == player['team_id']:
            raise ValueError('Own team cannot be opponent')
        ids = window['opponent_attempt_ids']
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate opponent attempt')
    attempts = sum(len(w['opponent_attempt_ids']) for w in windows)
    return {**player, 'opponent_eligible_attempts': attempts,
            'opponent_attempts_per90': attempts/player['minutes']*90,
            'pressures_per100_opponent_attempts': 100*player['recorded_pressures']/attempts if attempts else None}


def build_evidence(allow_download=True):
    data = {key: json.loads((ROOT/path).read_text()) for key, path in SOURCES.items()}
    players = data['pressure']['players']
    windows = []
    for audit in data['minutes']['match_audits']:
        keys = {(p['team_id'], p['player_id']) for p in players if audit['match_id'] in p['qualifying_match_ids']}
        if not keys:
            continue
        targets = [r for r in audit['intervals'] if (r['team_id'], r['player_id']) in keys]
        if len(targets) != len(keys):
            raise ValueError('Selected interval coverage differs')
        events = passing.time_module.cohort_module.raw.load_events(audit['raw_input'], allow_download)
        windows.extend(opponent_windows(events, audit, targets))
    profiles = [summarize(p, [w for w in windows if (w['team_id'], w['player_id']) == (p['team_id'], p['player_id'])]) for p in players]
    return {'competition': data['pressure']['competition'], 'season': '2019', 'competition_id': 72, 'season_id': 30,
            'course_reading': {'lesson': 'Soccermatics Lesson 3: Statistical scouting', 'section': 'Normalisation',
                               'url': 'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'},
            'source_files': {k: {'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k, p in SOURCES.items()},
            'players': profiles, 'windows': windows,
            'rule': 'Pool recorded player Pressure starts, divide by eligible opponent pass attempts during the same selected registered windows, multiply by 100. Opponent attempts use lesson 65 eligibility: possession-team passes, periods 1–4, excluding restart deliveries and Unknown/Injury Clearance; attempted failures remain. Restrict clock and event order. Zero pooled opponent attempts means undefined.',
            'scope': 'Custom descriptive exposure proxy, not an official StatsBomb metric, possession-time adjustment, probability, success rate or count of passes individually pressured. Pressure events need not coincide with pass events; multiple pressures can relate to one passage. Includes later role changes. No ability or causal inference.'}


def render_report(evidence):
    lines = []
    for p in sorted(evidence['players'], key=lambda p: (p['team_name'], p['player_name'])):
        rate = p['pressures_per100_opponent_attempts']
        text = f'{rate:.4f}' if rate is not None else 'undefined'
        lines.append(f"- {p['team_name']} — {p['player_name']}: {p['recorded_pressures']} pressures / {p['opponent_eligible_attempts']} opponent attempts ×100 = **{text}**; {p['pressures_per90']:.4f} pressures/90; {p['opponent_attempts_per90']:.4f} opponent attempts/90.")
    return '''# Pressure activity and opponent passing exposure

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Normalisation](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation).
This is a custom worked extension of the course's exposure/context idea, not a copied assignment or provider-standard metric.

## Question and calculation

Per 90 gives every player the same time denominator, but opponents can have very different passing volumes in that time. We add a second denominator:

**Recorded player pressures / eligible opponent pass attempts ×100.**

The same 35 players, 145 windows, minutes and pressure counts remain unchanged. Counts are pooled before division, not averaged match rates. Opponent attempts include completed and failed attempts under lesson 65's eligibility rules; restart deliveries, Unknown/Injury Clearance and non-possession-team passes are excluded. Subsequent passes after a restart can remain. Both event order and clock bounds exclude actions after a target leaves, even at an equal timestamp. All opponent players, including their goalkeeper, can contribute.

## All profiles (alphabetical)

''' + '\n'.join(lines) + '''

## Interpretation

This measures recorded pressure activity relative to selected opponent passing volume. It is not the percentage of passes pressured: pressures are separate events and are not linked one-to-one with pass attempts. A pressure can happen while an opponent carries the ball. Several pressures can occur during one passage, so the ratio is not bounded to 100. It does not measure possession duration, actual individual pressing opportunities, pressing success, ball wins or defensive ability. Our pressure numerator also includes actions outside the eligibility scope of the passing denominator. Keep both metrics visible; neither is a complete adjustment.

Zero opponent attempts means an undefined ratio, even with zero pressures. Shared opponent events can enter two fullbacks' separate windows; those lists must not be summed as unique tournament events. Source hashes and per-window event IDs support replay.

## Reproduce

Run `python 74_fullback_opponent_pass_context.py` in Spyder. [Saved evidence](../data/74_fullback_opponent_pass_context_evidence.json) · [Lesson](../lessons/0056-fullback-opponent-pass-context.html).
Assisted exercise using StatsBomb Open Data; no new model, footage observation or independent mastery claim.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/74_fullback_opponent_pass_context_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/57_fullback_opponent_pass_context.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178, 15249):
            print(p['player_name'], p['recorded_pressures'], p['opponent_eligible_attempts'], p['pressures_per90'], p['pressures_per100_opponent_attempts'])


if __name__ == '__main__':
    main()
