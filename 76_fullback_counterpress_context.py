"""Lesson 76: provider-labelled counterpressing among the existing Pressure starts."""
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


def flag_state(event):
    if 'counterpress' not in event:
        return 'missing'
    value = event['counterpress']
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if value is None:
        return 'null'
    raise ValueError('Counterpress flag must be boolean, null or absent')


def enrich_rows(events, rows):
    lookup = {e['id']: e for e in events}
    if len(lookup) != len(events):
        raise ValueError('Duplicate raw event ID')
    if len({r['event_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate selected event ID in fixture')
    enriched = []
    for row in rows:
        event = lookup[row['event_id']]
        if (event['type']['name'] != 'Pressure'
                or (event['team']['id'], event['player']['id']) != (row['team_id'], row['player_id'])
                or any(event[k] != row[k] for k in ('index', 'period', 'timestamp'))):
            raise ValueError('Raw event differs from selected pressure identity or timing')
        state = flag_state(event)
        enriched.append({**row, 'counterpress_flag_state': state, 'counterpress_flagged': state == 'true'})
    return enriched


def summarize(player, rows):
    if player['duration_ms'] <= 0 or player['minutes'] != player['duration_ms']/60000:
        raise ValueError('Registered exposure differs')
    if len(rows) != player['recorded_pressures'] or len({(r['match_id'], r['event_id']) for r in rows}) != len(rows):
        raise ValueError('Pressure membership differs')
    if any((r['team_id'], r['player_id']) != (player['team_id'], player['player_id'])
           or r['match_id'] not in player['qualifying_match_ids'] for r in rows):
        raise ValueError('Pressure fixture or player differs')
    states = {state: 0 for state in ('true', 'false', 'null', 'missing')}
    for row in rows:
        state = row['counterpress_flag_state']
        if state not in states or row['counterpress_flagged'] is not (state == 'true'):
            raise ValueError('Inconsistent counterpress classification')
        states[state] += 1
    count = states['true']
    return {**player, 'counterpress_flag_states': states, 'flagged_counterpressures': count,
            'not_flagged_pressures': len(rows)-count,
            'flagged_counterpressures_per90': count/player['minutes']*90,
            'flagged_share_of_pressures_pct': 100*count/len(rows) if rows else None}


def build_evidence(allow_download=True):
    data = {k: json.loads((ROOT/p).read_text()) for k, p in SOURCES.items()}
    rows = []
    for audit in data['minutes']['match_audits']:
        selected = [r for r in data['pressure']['rows'] if r['match_id'] == audit['match_id']]
        if not selected:
            continue
        events = pressure.time_module.cohort_module.raw.load_events(audit['raw_input'], allow_download)
        rows.extend(enrich_rows(events, selected))
    # Keep the original source ordering to make preservation checks straightforward.
    lookup = {(r['match_id'], r['event_id']): r for r in rows}
    if len(lookup) != len(rows) or len(rows) != len(data['pressure']['rows']):
        raise ValueError('Counterpress enrichment does not cover source pressures')
    rows = [lookup[(r['match_id'], r['event_id'])] for r in data['pressure']['rows']]
    players = [summarize(p, [r for r in rows if (r['team_id'], r['player_id']) == (p['team_id'], p['player_id'])]) for p in data['pressure']['players']]
    return {'competition': data['pressure']['competition'], 'season': '2019', 'competition_id': 72, 'season_id': 30,
            'course_reading': {'lesson': 'Soccermatics Lesson 3: Statistical scouting', 'section': 'Context: what to measure', 'url': READING},
            'provider_definition_url': SPECIFICATION,
            'source_files': {k: {'path': p, 'sha256': hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k, p in SOURCES.items()},
            'rows': rows, 'players': players,
            'rule': 'Among the unchanged selected Pressure starts, count only raw top-level counterpress exactly true. Preserve false, null and absent states separately; collectively describe them as not flagged. Use all selected Pressure starts as share denominator and original registered minutes for per90. No turnover-time reconstruction or new event detection.',
            'scope': 'Provider-labelled pressing within five seconds of an open-play turnover. This is pressure context, not a pressure regain, a successful press, a unique turnover episode or a causal effect. Other event types can have counterpress flags but are outside this Pressure-only numerator. No adjustment for the number of team losses or pressing opportunities.'}


def render_report(evidence):
    lines = []
    for p in sorted(evidence['players'], key=lambda p: (p['team_name'], p['player_name'])):
        value = p['flagged_share_of_pressures_pct']
        share = f'{value:.2f}%' if value is not None else 'undefined'
        lines.append(f"- **{p['team_name']} — {p['player_name']}**: {p['flagged_counterpressures']}/{p['recorded_pressures']} pressures flagged ({share}); {p['flagged_counterpressures_per90']:.4f}/90. Raw flag states: {p['counterpress_flag_states']}.")
    return f'''# Pressure after losing the ball: counterpress context

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Context: what to measure]({READING}). This is our assisted context extension, not a separate numbered lesson from the course.

## Meaning and method

The [StatsBomb Open Data specification, Pressure → counterpress]({SPECIFICATION}) defines the flag as pressing within five seconds of an open-play turnover, recorded only when true. In football terms, a team loses the ball during play and promptly applies pressure. We read the provider flag; we do not independently reconstruct the lost-ball instant or apply a new five-second rule.

Select the unchanged 2,034 Pressure events from lesson 73. Match each to the hash-checked raw event by fixture and ID, verify player/team, type, period, timestamp and index, then inspect top-level counterpress. Only the actual Boolean true counts. False, null and absent states are retained separately and described collectively as not flagged. Unexpected non-Boolean values stop calculation. Missing coordinates do not exclude an action.

Flagged share = flagged Pressure starts / all selected Pressure starts ×100. Per90 = flagged starts / original registered minutes ×90. Counts are pooled across fixtures. Zero pressures gives an undefined share, rather than zero; positive time with no flagged actions gives zero per90. All 35 profiles retain the original cohort, pressure totals and minutes.

## Results (alphabetical)

{chr(10).join(lines)}

## Interpretation and limits

The flag describes when the pressing action happened relative to a turnover. It does not state that the player or her team recovered possession. Counterpressing and pressure regains are different concepts: one concerns pressure after a loss, the other concerns recovering the ball after pressure. We have not calculated regain outcomes here.

One lost-ball episode can have several Pressure events and several players involved, so these counts are not unique turnovers. Other defensive event types can also carry counterpress flags; this report deliberately covers Pressure starts only. Not flagged is not independently verified absence of counterpressing in footage. Shares depend on team losses, tactics and other pressure activity; no opportunity-adjusted ability ranking or success rate is claimed. A counterpress can happen in any pitch third: the time context and the spatial context answer different questions.

## Reproduce

Run `python 76_fullback_counterpress_context.py` in Spyder. [Evidence](../data/76_fullback_counterpress_context_evidence.json) · [Lesson](../lessons/0058-fullback-counterpress-context.html).
Source: StatsBomb Open Data. No footage reviewed or independent mastery demonstrated.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/76_fullback_counterpress_context_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/59_fullback_counterpress_context.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178, 15249):
            print(p['player_name'], p['flagged_counterpressures'], p['recorded_pressures'], p['flagged_share_of_pressures_pct'], p['flagged_counterpressures_per90'], p['counterpress_flag_states'])
    print('All profiles', len(evidence['players']), 'flagged pressures', sum(p['flagged_counterpressures'] for p in evidence['players']))


if __name__ == '__main__':
    main()
