"""Lesson 80: assemble an evidence-backed portfolio brief from existing profiles."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {
    'passing': 'data/70_fullback_team_passing_share_evidence.json',
    'opponent': 'data/74_fullback_opponent_pass_context_evidence.json',
    'areas': 'data/75_fullback_pressure_areas_evidence.json',
    'proxy': 'data/77_fullback_next_possession_evidence.json',
    'linked_passes': 'data/79_pressure_linked_passes_evidence.json',
    'original_brief': 'data/69_fullback_recruitment_brief_evidence.json',
    'counterpress': 'data/76_fullback_counterpress_context_evidence.json',
}
SELECTED = ((865, 10178), (861, 15249))
READING = 'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#modesty'


def indexed(rows):
    result = {(p['team_id'], p['player_id']): p for p in rows}
    if len(result) != len(rows):
        raise ValueError('Duplicate player/team identity in report source')
    return result


def compile_profiles(data):
    tables = {key: indexed(value['players']) for key, value in data.items() if key != 'original_brief'}
    base = indexed(data['original_brief']['profiles'])
    expected = set(tables['passing'])
    for key, table in tables.items():
        if set(table) != expected:
            raise ValueError('Source cohorts differ: '+key)
        for identity, p in table.items():
            reference = tables['passing'][identity]
            if any(p[field] != reference[field] for field in ('qualifying_match_ids', 'duration_ms', 'minutes')):
                raise ValueError('Source fixtures or exposure differ: '+key)
    profiles = []
    for identity in SELECTED:
        p = tables['passing'][identity]
        old = base[identity]
        if old['minutes'] != p['minutes'] or old['completed'] != p['eligible_completed'] or old['attempted'] != p['eligible_attempts']:
            raise ValueError('Original brief differs from current passing scope')
        d = tables['opponent'][identity]
        areas = tables['areas'][identity]
        counter = tables['counterpress'][identity]
        proxy = tables['proxy'][identity]
        linked = tables['linked_passes'][identity]
        if any(source['recorded_pressures'] != d['recorded_pressures'] for source in (areas, counter, proxy, linked)):
            raise ValueError('Pressure totals differ across report sources')
        third = next(a for a in areas['pressure_areas'] if a['area'] == 'Opponent third')
        profiles.append({
            'team_id': identity[0], 'player_id': identity[1], 'player_name': p['player_name'], 'team_name': p['team_name'],
            'qualifying_match_ids': p['qualifying_match_ids'], 'role_starts': p['role_starts'],
            'starting_roles': old['position_starts'], 'duration_ms': p['duration_ms'], 'minutes': p['minutes'],
            'completed': p['eligible_completed'], 'attempted': p['eligible_attempts'], 'completed_per90': p['completed_per90'],
            'completion_pct': p['completion_pct'], 'team_completed': p['team_completed_while_registered'],
            'team_passing_share_pct': p['share_of_team_completions_pct'],
            'fixed_forward_count': old['fixed_count'], 'fixed_forward_per90': old['fixed_per90'],
            'alternative_forward_count': old['alternative_count'], 'alternative_forward_per90': old['alternative_per90'],
            'pressures': d['recorded_pressures'], 'pressures_per90': d['pressures_per90'],
            'opponent_pass_attempts': d['opponent_eligible_attempts'], 'pressures_per100_opponent_attempts': d['pressures_per100_opponent_attempts'],
            'mapped_pressures': areas['mapped_pressures'], 'opponent_third_pressures': third['count'],
            'opponent_third_share_pct': third['share_of_mapped_pressures_pct'],
            'counterpress_flagged': counter['flagged_counterpressures'], 'counterpress_flagged_share_pct': counter['flagged_share_of_pressures_pct'],
            'next_possession_positive': proxy['next_own_within5s_count'], 'next_possession_assessable': proxy['assessable_pressures'],
            'next_possession_unclear': proxy['unassessable_pressures'],
            'linked_pressure_count': linked['pressures_with_linked_opponent_pass'],
            'linked_unique_pass_count': len(linked['unique_linked_opponent_passes']),
            'linked_pass_outcomes': linked['linked_pass_category_counts'],
        })
    return profiles


def build_evidence():
    data = {key: json.loads((ROOT/path).read_text()) for key, path in SOURCES.items()}
    for source in data.values():
        if source['season'] != '2019' or source['competition_id'] != 72 or source['season_id'] != 30:
            raise ValueError('Competition/season mismatch in report source')
    return {'competition': 'FIFA Women’s World Cup', 'season': '2019', 'competition_id': 72, 'season_id': 30,
            'prepared_on': '2026-11-18', 'course_reading': {'lesson': 'Soccermatics Lesson 3: Statistical scouting', 'section': 'Modesty', 'url': READING},
            'cohort_size': len(data['passing']['players']), 'profiles': compile_profiles(data),
            'review_queue': data['original_brief']['review_queue'],
            'linked_event_examples': data['linked_passes']['examples'],
            'source_files': {key: {'path': path, 'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for key, path in SOURCES.items()},
            'selection': 'Bronze and Majri are familiar historical communication examples, not the best two candidates. Their starting sides differ. No composite score or signing ranking.',
            'authorship': 'Prepared with AI assistance as guided portfolio work. Independent reproduction, interpretation and footage review have not been demonstrated.',
            'scope': 'Synthesis of previously inspected evidence, not new validation, a fresh season, official Pressure Regains or proof of player ability. Earlier reports and numbers remain unchanged.'}


def role_text(p):
    return ', '.join(f'{count} {role.lower()} starts' for role, count in p['starting_roles'].items() if count)


def render_markdown(evidence):
    bronze, majri = evidence['profiles']
    sections = []
    for p in evidence['profiles']:
        c = p['linked_pass_outcomes']
        sections.append(f'''## {p['player_name']} — {p['team_name']}

{role_text(p)}; {p['minutes']:.1f} reconstructed registered minutes in those qualifying fixtures. These include later role changes, not verified time spent solely at fullback.

- **Passing involvement:** {p['completed']}/{p['attempted']} eligible passes completed ({p['completion_pct']:.1f}%); **{p['completed_per90']:.2f} completions per 90**. Her {p['completed']} completions represent **{p['team_passing_share_pct']:.2f}%** of {p['team_completed']} same-window eligible team completions. [1]
- **Forward movement:** {p['fixed_forward_count']} completed passes advanced at least 20 x-coordinate units ({p['fixed_forward_per90']:.2f}/90). The near-goal alternative includes {p['alternative_forward_count']} ({p['alternative_forward_per90']:.2f}/90). These are project definitions, not measured action value. [6]
- **Pressure context:** {p['pressures']} recorded pressures, **{p['pressures_per90']:.2f}/90**; **{p['pressures_per100_opponent_attempts']:.2f} per 100** eligible opponent pass attempts ({p['opponent_pass_attempts']} attempts). This ratio is a volume proxy, not the percentage of passes she pressured. [2]
- **Where and when:** {p['opponent_third_pressures']}/{p['mapped_pressures']} mapped starts in the opponent third ({p['opponent_third_share_pct']:.1f}%); {p['counterpress_flagged']}/{p['pressures']} pressures flagged as counterpressing ({p['counterpress_flagged_share_pct']:.1f}%). Location and post-turnover timing do not establish success. [3, 7]
- **Outcome coverage:** the custom next-possession check matches {p['next_possession_positive']}/{p['next_possession_assessable']} assessable pressures, with {p['next_possession_unclear']} unclear cases. Separately, {p['linked_pressure_count']}/{p['pressures']} pressures link to {p['linked_unique_pass_count']} unique opponent passes: {c['completed']} completed, {c['not_completed']} not completed, {c['unassessable']} unassessable. The two outcome measures have different populations and are not combined into a success score. [4, 5]
''')
    queue = '\n'.join(f"- **{r['player_name']} vs {r['opponent']}**, {r['match_date']}, period {r['period']}, {r['period_timestamp']}: {r['category']}. Match {r['match_id']}, event `{r['pass_id']}`. **Not reviewed**; observation unfilled." for r in evidence['review_queue'])
    links = '\n'.join(f"- Match {r['match_id']}, period {r['period']}: pressure `{r['pressure_id']}` at {r['pressure_timestamp']} → {r['pass_player_name']} pass `{r['pass_id']}` at {r['pass_timestamp']}; outcome {r['raw_outcome'] or 'Completed (no outcome field)'}. **Not reviewed**; event-data association only." for r in evidence['linked_event_examples'])
    sources = '\n'.join(f"{i}. **{key.replace('_', ' ').title()}**: [saved evidence](../{record['path']}); SHA-256 `{record['sha256']}`." for i, (key, record) in enumerate(evidence['source_files'].items(), 1))
    return f'''# Fullback profiles: activity needs football context

**Alireza Erfanian · Football Analytics Research Lab · Prepared 18 November 2026 · Guided portfolio work**

**Study:** FIFA Women's World Cup, **2019** (StatsBomb competition 72 / season 30). **Question:** What behaviours should a scout investigate in these two historical profiles? The full profiling pool has {evidence['cohort_size']} players; this brief uses two familiar examples with different starting sides, not ranked or interchangeable recruitment candidates.

## Executive Summary

- Bronze recorded **{bronze['completed_per90']:.2f} completed eligible passes per 90**, versus **{majri['completed_per90']:.2f}** for Majri. Their shares of same-window team completions were **{bronze['team_passing_share_pct']:.2f}%** and **{majri['team_passing_share_pct']:.2f}%**. These identify different observed involvement, without isolating ability from role or team context. [1]
- Bronze's pressure rate was higher per 90 (**{bronze['pressures_per90']:.2f} vs {majri['pressures_per90']:.2f}**), but the figures were close per 100 eligible opponent attempts (**{bronze['pressures_per100_opponent_attempts']:.2f} vs {majri['pressures_per100_opponent_attempts']:.2f}**). Majri made a larger share of her pressures in the opponent third (**{majri['opponent_third_share_pct']:.1f}% vs {bronze['opponent_third_share_pct']:.1f}%**). The denominator and location change the question, not the original actions. [2, 3]
- Use these findings to focus further observation. The outcome proxies contain unclear cases and limited pass-link coverage; they do **not** support an overall defensive-quality ranking or a signing decision. Neither footage review nor current availability assessment has been performed. [4, 5]

{chr(10).join(sections)}

## What should a scout investigate?

For Bronze, check whether the higher passing involvement repeatedly reflects useful progression or predominantly safe circulation in her right-sided role. For Majri, check which situations produce the greater opponent-third share of pressure starts in her left-sided role. For both, inspect the options available, teammates' support and the opponent's response before attributing value to an action. These are questions suggested by the profiles, not observations already established.

The existing queue below gives six deliberately chosen event references: four pass-definition examples and two first linked-pressure/pass examples. They are starting points for inspection, not a representative performance sample. Match/period clocks need aligning to available footage; no video-file offsets are supplied. Review these cases when footage is available, then check whether observations recur across comparable situations before making a player judgement.

### Passing examples already queued

{queue}

### Pressure/pass examples

{links}

## Definitions and practical limits

The cohort requires at least three Left Back/Right Back starts; actions and minutes use only qualifying starting fixtures and reconstructed registered windows. Added/extra time is included; halftime and shootouts are excluded. Later changes of role remain included. Eligible passing excludes restart deliveries, non-possession-team passes and Unknown/Injury Clearance outcomes; later passes after restarts can remain. Team shares include the player and goalkeeper and pool counts before division. [1, 6]

Opponent-pass exposure uses the same eligibility concept for the other team in each player's window; it is not possession duration or a count of personal pressing opportunities. Opponent-third shares use mapped pressure locations, with x≥80 on the normalized 0–120 pitch. Counterpress flags describe pressure within five seconds of an open-play turnover, not regaining possession. [2, 3, 7]

The next-possession proxy follows the first new same-period possession within five seconds of pressure start and reports unclear rows separately. It is not official StatsBomb Pressure Regains. Related-pass results instead use directed event links, without a five-second or restart filter, and deduplicate passes within player. Unknown pass outcomes remain visible. A missing link is not a failed pressure; several players can be linked to the same pass, and a linked incompletion does not establish pressure causation. Do not compare these two outcome denominators as if they describe the same test. [4, 5]

This historical tournament sample does not establish current form, fitness, contract status, availability or transfer suitability. The two players have different starting sides and team contexts. No composite score, causal adjustment or new model validation has been introduced.

## Sources and reproducibility

{sources}

Reading: [Soccermatics Lesson 3 — Statistical scouting, Modesty]({READING}); definitions: [StatsBomb Open Data specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf). Data source: [StatsBomb Open Data](https://github.com/hudl/open-data).

Run `python 80_fullback_portfolio_synthesis.py` in Spyder or locally to rebuild this brief from the saved evidence; no downloads or new estimation are needed. [Synthesis evidence](../data/80_fullback_portfolio_synthesis_evidence.json) · [Lesson 80](../lessons/0062-fullback-portfolio-synthesis.html). Earlier reports remain available, including the [first passing brief](52_fullback_recruitment_brief.md).

**Contribution statement:** {evidence['authorship']} The event queue remains unreviewed; independent reproduction and interpretation are next learning milestones.
'''


def main():
    evidence = build_evidence()
    (ROOT/'data/80_fullback_portfolio_synthesis_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/63_fullback_profile_portfolio_brief.md').write_text(render_markdown(evidence))
    print('Generated portfolio brief:', len(evidence['profiles']), 'profiles;', len(evidence['source_files']), 'hashed evidence sources')


if __name__ == '__main__':
    main()
