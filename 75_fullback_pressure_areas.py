"""Lesson 75: where recorded pressure starts occurred, preserving unmapped events."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = 'data/73_fullback_pressure_activity_evidence.json'
spec = importlib.util.spec_from_file_location('pressure73', ROOT/'73_fullback_pressure_activity.py')
pressure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pressure)
AREAS = ('Own third', 'Middle third', 'Opponent third')
READING = 'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#context-what-to-measure'


def area_for(row):
    x, y = pressure.location_or_none([row['x'], row['y']])
    if row['location_valid']:
        if x is None:
            raise ValueError('Mapped pressure must have valid pitch coordinates')
        return AREAS[0] if x < 40 else AREAS[1] if x < 80 else AREAS[2]
    if row['x'] is not None or row['y'] is not None:
        raise ValueError('Unmapped source pressure must retain null coordinates')
    return None


def summarize(player, rows):
    if player['duration_ms'] <= 0 or player['minutes'] != player['duration_ms']/60000:
        raise ValueError('Pressure exposure must match registered minutes')
    if len(rows) != player['recorded_pressures'] or len({(r['match_id'], r['event_id']) for r in rows}) != len(rows):
        raise ValueError('Pressure membership differs or contains duplicates')
    if any((r['team_id'], r['player_id']) != (player['team_id'], player['player_id'])
           or r['match_id'] not in player['qualifying_match_ids'] for r in rows):
        raise ValueError('Pressure belongs to wrong player or fixture')
    classified = [(r, area_for(r)) for r in rows]
    mapped = sum(area is not None for _, area in classified)
    if mapped != player['mapped_pressures'] or len(rows)-mapped != player['unmapped_pressures']:
        raise ValueError('Mapped/unmapped source coverage differs')
    areas = []
    for label in AREAS:
        selected = [r for r, area in classified if area == label]
        areas.append({'area': label, 'count': len(selected),
                      'per90': len(selected)/player['minutes']*90,
                      'share_of_mapped_pressures_pct': 100*len(selected)/mapped if mapped else None,
                      'event_keys': [{'match_id': r['match_id'], 'event_id': r['event_id']} for r in selected]})
    return {**player, 'pressure_areas': areas}


def build_evidence():
    source = json.loads((ROOT/SOURCE).read_text())
    players = [summarize(p, [r for r in source['rows'] if (r['team_id'], r['player_id']) == (p['team_id'], p['player_id'])]) for p in source['players']]
    if sum(p['recorded_pressures'] for p in players) != len(source['rows']):
        raise ValueError('Not all source pressure events belong to profiles')
    return {'competition': source['competition'], 'season': '2019', 'competition_id': 72, 'season_id': 30,
            'course_reading': {'lesson': 'Soccermatics Lesson 3: Statistical scouting', 'section': 'Context: what to measure', 'url': READING},
            'source_path': SOURCE, 'source_sha256': hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
            'players': players,
            'rule': 'Classify recorded Pressure start locations in the event team attacking direction: own third 0<=x<40; middle 40<=x<80; opponent third 80<=x<=120. Share denominator is all mapped pressures for that player. Missing locations stay in original total but outside location shares. Rates per90 use original full registered minutes.',
            'scope': 'Custom spatial context extension. Thirds are equal pitch-length bins, not learned values or a pressing-height threshold validated against tactics. No pressure success, possession adjustment, time in each zone, team pressing shape or player ability inferred.'}


def render_report(evidence):
    lines = []
    for p in sorted(evidence['players'], key=lambda p: (p['team_name'], p['player_name'])):
        parts = []
        for a in p['pressure_areas']:
            share = f"{a['share_of_mapped_pressures_pct']:.2f}%" if a['share_of_mapped_pressures_pct'] is not None else 'undefined'
            parts.append(f"{a['area']}: {a['count']} ({share} of mapped; {a['per90']:.2f}/90)")
        lines.append(f"- **{p['team_name']} — {p['player_name']}**: "+'; '.join(parts)+f". Coverage: {p['mapped_pressures']}/{p['recorded_pressures']} mapped.")
    return f'''# Where did the fullbacks apply pressure?

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Context: what to measure]({READING}). Custom assisted assignment, applying the course's context principle.

## Definition

Split the 120-unit pitch length into three equal sections, from the event team's perspective: own goal at x=0, opponent goal at x=120. Own third: 0≤x<40; middle: 40≤x<80; opponent third: 80≤x≤120. Width y is not used to split the thirds, but valid two-dimensional locations are required. These are coordinate units, not metres. No second-half flip is applied to the already normalized event coordinates.

The original 35-player cohort, qualifying fixtures, registered minutes and all 2,034 recorded Pressure starts remain unchanged. We classify saved starts, not full pressure paths. Each mapped event enters exactly one third, with event keys retained. Unknown locations remain counted in the overall pressure total and are never placed in a guessed third.

## All profiles (alphabetical)

{chr(10).join(lines)}

![Pressure start distribution by pitch third](../figures/68_fullback_pressure_areas.png)

## Two questions, two denominators

Share in an area = area's pressures / all mapped pressures ×100. This describes the location mix of observed actions. Area pressures per90 = area's count / original registered minutes ×90. This describes location-specific activity per playing time, not per minute spent in that area. Do not average match percentages. With no mapped pressures the location shares are undefined; an empty area with other mapped pressures is a measured zero. Area counts plus unmapped counts reconcile to the original total.

More opponent-third pressures does not prove better defending, a coordinated high press, tactical instructions or pressing success. These coarse bins provide context for future review. No opponent passing-volume adjustment is applied to the area metrics, and no individual zone-exposure time is available. The two familiar examples are illustrations, not a ranking of interchangeable signing options.

## Reproduce

Run `python 75_fullback_pressure_areas.py` in Spyder. [Evidence](../data/75_fullback_pressure_areas_evidence.json) · [Lesson](../lessons/0057-fullback-pressure-areas.html).
Source: StatsBomb Open Data; [event specification and coordinate convention](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf).
No footage observation, model fitting or independent mastery claim.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    selected = [next(p for p in evidence['players'] if p['player_id'] == identifier) for identifier in (10178, 15249)]
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (label, color) in enumerate(zip(AREAS, ('#32658a', '#d6ad56', '#45866d'))):
        values = [p['pressure_areas'][i]['share_of_mapped_pressures_pct'] or 0 for p in selected]
        left = [sum(a['share_of_mapped_pressures_pct'] or 0 for a in p['pressure_areas'][:i]) for p in selected]
        ax.barh(range(2), values, left=left, color=color, label=label, height=.45)
        for j, (p, value) in enumerate(zip(selected, values)):
            if value >= 6:
                ax.text(left[j]+value/2, j, f"{p['pressure_areas'][i]['count']}\n{value:.1f}%", ha='center', va='center', color='white', fontsize=11)
    ax.set_yticks(range(2), [f"{p['player_name']}\n{p['mapped_pressures']}/{p['recorded_pressures']} mapped" for p in selected])
    ax.invert_yaxis(); ax.set_xlim(0, 100)
    ax.set_xlabel('Share of mapped pressure starts (%)')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.20), ncol=3, frameon=False)
    fig.suptitle('Where recorded pressure starts occurred\n2019 Women’s World Cup · selected fullback-start fixtures', fontsize=14)
    fig.text(.5, .025, 'Own goal x=0 → opponent goal x=120; boundaries x=40 and x=80.\nLocation mix is not pressing success or defensive quality. Source: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.subplots_adjust(left=.18, right=.97, top=.78, bottom=.30)
    fig.savefig(ROOT/'figures/68_fullback_pressure_areas.png', dpi=160)
    plt.show()


def main():
    evidence = build_evidence()
    (ROOT/'data/75_fullback_pressure_areas_evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    (ROOT/'reports/58_fullback_pressure_areas.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178, 15249):
            print(p['player_name'], [(a['area'], a['count'], round(a['share_of_mapped_pressures_pct'], 2)) for a in p['pressure_areas']])
    plot_evidence(evidence)


if __name__ == '__main__':
    main()
