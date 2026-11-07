"""Lesson 77: next recorded possession after pressure; explicit educational proxy."""
from bisect import bisect_right
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
WINDOW_MS = 5000
READING = 'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'
GUIDANCE = 'https://hudl.my.site.com/support/s/article/pressure-regains?language=en_US&topic=Statsbomb_Global_Football_Data_Glossary'


def milliseconds(event):
    return pressure.time_module.cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])


def possession_starts(events):
    if len({e['id'] for e in events}) != len(events) or len({e['index'] for e in events}) != len(events):
        raise ValueError('Duplicate raw event ID or index')
    groups = {}
    last_key = None
    for event in sorted(events, key=lambda e: e['index']):
        if event['period'] not in (1, 2, 3, 4):
            continue
        key = (event['period'], event['possession'])
        if key not in groups:
            groups[key] = {'period': event['period'], 'possession': event['possession'],
                           'team_id': event['possession_team']['id'], 'event_id': event['id'],
                           'index': event['index'], 'timestamp': event['timestamp'], 'time_ms': milliseconds(event)}
        elif last_key != key:
            raise ValueError('Possession IDs are not contiguous within period')
        if groups[key]['team_id'] != event['possession_team']['id']:
            raise ValueError('Possession has inconsistent team identity')
        last_key = key
    return list(groups.values())


def classify(row, event, next_start, period_length_ms):
    if (event['id'] != row['event_id'] or event['type']['name'] != 'Pressure'
            or (event['team']['id'], event['player']['id']) != (row['team_id'], row['player_id'])
            or any(event[k] != row[k] for k in ('period', 'index', 'timestamp'))):
        raise ValueError('Pressure source identity/timing differs')
    when = milliseconds(event)
    if when > period_length_ms:
        raise ValueError('Pressure is after recorded period end')
    next_info = None
    if next_start is not None:
        if next_start['period'] != event['period'] or next_start['index'] <= event['index']:
            raise ValueError('Next possession must follow pressure in the same period')
        next_info = {**next_start, 'delay_ms': next_start['time_ms']-when}
    if event['possession_team']['id'] == row['team_id']:
        outcome, status = None, 'already_own_possession'
    elif next_info is not None and next_info['delay_ms'] < 0:
        outcome, status = None, 'nonmonotonic_start_time'
    elif next_info is not None and next_info['delay_ms'] <= WINDOW_MS:
        outcome = next_info['team_id'] == row['team_id']
        status = 'next_own_within_window' if outcome else 'next_not_own_within_window'
    elif period_length_ms-when < WINDOW_MS:
        outcome, status = None, 'period_end_before_full_window'
    else:
        outcome, status = False, 'no_new_possession_within_window'
    return {**row, 'pressure_possession_id': event['possession'],
            'pressure_possession_team_id': event['possession_team']['id'],
            'next_possession': next_info, 'next_own_within5s': outcome, 'outcome_status': status}


def match_outcomes(events, rows, audit):
    starts = possession_starts(events)
    lookup = {e['id']: e for e in events}
    periods = {p['period']: p['length_ms'] for p in audit['periods']}
    output = []
    for row in rows:
        if row['match_id'] != audit['match_id']:
            raise ValueError('Pressure fixture differs')
        period_starts = [s for s in starts if s['period'] == row['period']]
        position = bisect_right([s['index'] for s in period_starts], row['index'])
        next_start = period_starts[position] if position < len(period_starts) else None
        output.append(classify(row, lookup[row['event_id']], next_start, periods[row['period']]))
    return output


def summarize(player, rows):
    if (len(rows) != player['recorded_pressures'] or player['minutes'] <= 0
            or len({(r['match_id'], r['event_id']) for r in rows}) != len(rows)):
        raise ValueError('Pressure coverage/exposure differs')
    if any((r['team_id'], r['player_id']) != (player['team_id'], player['player_id'])
           or r['match_id'] not in player['qualifying_match_ids'] for r in rows):
        raise ValueError('Pressure player or fixture differs')
    statuses = {}
    for row in rows:
        statuses[row['outcome_status']] = statuses.get(row['outcome_status'], 0)+1
    assessable = sum(r['next_own_within5s'] is not None for r in rows)
    positive = sum(r['next_own_within5s'] is True for r in rows)
    return {**player, 'next_own_within5s_count': positive, 'assessable_pressures': assessable,
            'unassessable_pressures': len(rows)-assessable, 'outcome_status_counts': statuses,
            'next_own_within5s_share_pct': 100*positive/assessable if assessable else None,
            'observed_next_own_within5s_per90': positive/player['minutes']*90}


def build_evidence(allow_download=True):
    data = {k: json.loads((ROOT/p).read_text()) for k, p in SOURCES.items()}
    output = []
    for audit in data['minutes']['match_audits']:
        rows = [r for r in data['pressure']['rows'] if r['match_id'] == audit['match_id']]
        if rows:
            events = pressure.time_module.cohort_module.raw.load_events(audit['raw_input'], allow_download)
            output.extend(match_outcomes(events, rows, audit))
    keyed = {(r['match_id'], r['event_id']): r for r in output}
    if len(keyed) != len(output) or len(output) != len(data['pressure']['rows']):
        raise ValueError('Outcome coverage differs from pressure source')
    rows = [keyed[(r['match_id'], r['event_id'])] for r in data['pressure']['rows']]
    players = [summarize(p, [r for r in rows if (r['team_id'], r['player_id']) == (p['team_id'], p['player_id'])]) for p in data['pressure']['players']]
    return {'competition': data['pressure']['competition'], 'season': '2019', 'competition_id': 72, 'season_id': 30,
            'course_reading': {'lesson': 'Soccermatics Lesson 3: Statistical scouting', 'section': 'Normalisation → Pressure Regains', 'url': READING},
            'provider_guidance_url': GUIDANCE, 'window_ms': WINDOW_MS,
            'source_files': {k: {'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k, p in SOURCES.items()},
            'rows': rows, 'players': players,
            'rule': 'Pressure-only custom proxy: the first following new recorded possession in the SAME period belongs to the pressing team and starts 0–5000 ms inclusive after pressure START. Possession start is first event index in each (period,possession) group; its possession_team defines the side. Do not skip an intervening possession. Already-own possession, backwards candidate time and insufficient period-end observation without a timely candidate are unassessable. Observe the team outcome even if the player is substituted during follow-up. No other event-type or play-pattern entry filter.',
            'scope': 'Not an exact reconstruction of official StatsBomb Pressure Regains: their IQ possession definition differs from Event Data. A recorded possession label is a proxy for control, not video-verified recovery. Association after pressure is not causation or individual credit. Several pressures can share one next-possession start; counts are not unique regains. Zero observed proxy outcome is not a proven unsuccessful pressure.'}


def render_report(evidence):
    lines = []
    for p in sorted(evidence['players'], key=lambda p: (p['team_name'], p['player_name'])):
        value = p['next_own_within5s_share_pct']
        share = f'{value:.2f}%' if value is not None else 'undefined'
        lines.append(f"- **{p['team_name']} — {p['player_name']}**: {p['next_own_within5s_count']}/{p['assessable_pressures']} assessable pressures ({share}); {p['unassessable_pressures']} unassessable of {p['recorded_pressures']} total; observed {p['observed_next_own_within5s_per90']:.4f}/90. Statuses: {p['outcome_status_counts']}.")
    return f'''# What followed the pressure? Next-possession check

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Normalisation, Pressure Regains]({READING}). This is our assisted educational extension.

## Why use an explicitly named proxy?

[Hudl's Pressure Regains guidance]({GUIDANCE}) describes a team's recovery within five seconds after pressure, with conditions on the following possession. It also says IQ's possession definition does not translate cleanly to Event Data. We therefore do **not** label this result the official Pressure Regains metric.

Our bounded question is: does the **first following new recorded possession** belong to the pressing team and begin within five seconds of the pressure start? This uses event-data possession labels, not a newly trained detector or video observation. We do not apply the provider's possession-entry filters, so it is intentionally a different, transparent rule.

## Fixed rule

{evidence['rule']}

All 2,034 selected pressures and the original 35 profiles/minutes stay intact. Each row retains pressure identity, the candidate start event, team, possession ID, timestamp, delay and outcome status. Unassessable rows are excluded only from the outcome-share denominator, never erased from original counts. A full five-second window without a timely new possession is an observed negative for this rule. A next possession by the other side is negative even if another change follows within five seconds. We do not cross halftime/extra-time boundaries or infer a positive from a period restart.

Share = positive rows / assessable rows ×100; zero assessable rows means undefined. Observed positives per90 use original registered minutes, including exposure associated with unassessable rows, so they are observed-event rates rather than corrected complete-follow-up estimates. Outcome observation follows the team, even after a player's substitution; pressure membership itself remains restricted to the original player windows. Multiple player actions can share the same outcome, and should not be summed as unique team regains.

## Results (alphabetical)

{chr(10).join(lines)}

## Interpretation

The pressing team was assigned the next recorded possession quickly after these actions. This does not prove the pressing player caused it or recovered the ball herself. Next-possession labels can include restarts and are not guaranteed to identify the instant of controlled possession. No confirmed success percentage, causal effect, ability ranking or provider equivalence is claimed. An observed negative does not prove poor pressing: an action might force a backward pass, delay an attack or produce a benefit outside this rule.

## Reproduce

Run `python 77_fullback_next_possession.py` in Spyder. [Evidence](../data/77_fullback_next_possession_evidence.json) · [Lesson](../lessons/0059-fullback-next-possession.html).
Source: StatsBomb Open Data, hash-checked raw fixtures. Assisted work, no footage review or independent mastery demonstrated.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/77_fullback_next_possession_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/60_fullback_next_possession.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178, 15249):
            print(p['player_name'], p['next_own_within5s_count'], p['assessable_pressures'], p['next_own_within5s_share_pct'], p['outcome_status_counts'])


if __name__ == '__main__':
    main()
