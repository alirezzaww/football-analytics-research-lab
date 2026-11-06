"""Lesson 69: generate a recruitment communication sample and unreviewed event queue."""
import hashlib
import html
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_FILES={
    'cohort':'data/63_fullback_cohort_evidence.json',
    'minutes':'data/64_fullback_playing_time_evidence.json',
    'passing':'data/65_fullback_passing_per90_evidence.json',
    'fixed':'data/66_fullback_advancement_evidence.json',
    'context':'data/67_fullback_starting_context_evidence.json',
    'alternative':'data/68_adaptive_advancement_evidence.json',
}
SELECTED=((865,10178),(861,15249))
SPEC=importlib.util.spec_from_file_location('raw60',ROOT/'60_france_defensive_corners.py')
raw=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(raw)


def find_player(rows,team_id,player_id):
    selected=[r for r in rows if (r['team_id'],r['player_id'])==(team_id,player_id)]
    if len(selected)!=1:
        raise ValueError('Expected exactly one player/team profile')
    return selected[0]


def compile_profiles(data):
    profiles=[]
    for team_id,player_id in SELECTED:
        cohort=find_player(data['cohort']['eligible_players'],team_id,player_id)
        passing=find_player(data['passing']['players'],team_id,player_id)
        fixed=find_player(data['fixed']['players'],team_id,player_id)
        context=find_player(data['context']['players'],team_id,player_id)
        alternative=find_player(data['alternative']['players'],team_id,player_id)
        profiles.append({'team_id':team_id,'player_id':player_id,'name':cohort['player_name'],
                         'team':cohort['team_name'],'position_starts':cohort['position_starts'],
                         'role_starts':cohort['role_starts'],'minutes':passing['minutes'],
                         'completed':passing['eligible_completed'],'attempted':passing['eligible_attempts'],
                         'completion_pct':passing['completion_pct'],'completed_per90':passing['completed_per90'],
                         'fixed_count':fixed['qualifying_completions'],'fixed_per90':fixed['qualifying_per90'],
                         'fixed_share_pct':fixed['qualifying_share_pct'],
                         'alternative_count':alternative['alternative_completions'],
                         'alternative_per90':alternative['alternative_per90'],
                         'no_room_count':context['no_coordinate_room_completions'],
                         'no_room_pct':context['no_coordinate_room_pct'],
                         'middle_third':{k:v for k,v in next(g for g in context['starting_thirds'] if g['third']=='Middle third').items() if k!='pass_keys'}})
    return profiles


def review_event(candidate,event,team_names,match_date,category):
    if (event['id']!=candidate['pass_id'] or event['type']['name']!='Pass'
            or event['team']['id']!=candidate['team_id'] or event['player']['id']!=candidate['player_id']
            or event['period'] not in (1,2,3,4) or 'outcome' in event['pass']
            or event['location']!=[candidate['x'],candidate['y']]
            or event['pass']['end_location']!=[candidate['end_x'],candidate['end_y']]):
        raise ValueError('Review event differs from the saved completion')
    opponents=[name for identifier,name in team_names.items() if identifier!=candidate['team_id']]
    if candidate['team_id'] not in team_names or len(opponents)!=1:
        raise ValueError('Review fixture does not identify both teams')
    return {'match_id':candidate['match_id'],'match_date':match_date,'team_id':candidate['team_id'],
            'player_id':candidate['player_id'],'player_name':event['player']['name'],
            'opponent':opponents[0],'pass_id':event['id'],'category':category,
            'period':event['period'],'minute':event['minute'],'second':event['second'],
            'period_timestamp':event['timestamp'],'recipient':event['pass'].get('recipient',{}).get('name'),
            'start':[candidate['x'],candidate['y']],'end':[candidate['end_x'],candidate['end_y']],
            'x_gain':candidate['x_gain'],'review_status':'Not reviewed','video_observation':None}


def build_evidence(allow_download=True):
    data={k:json.loads((ROOT/p).read_text()) for k,p in SOURCE_FILES.items()}
    profiles=compile_profiles(data)
    records={m['match_id']:m['raw_input'] for m in data['minutes']['match_audits']}
    dates={r['match_id']:r['match_date'] for r in data['cohort']['starter_rows']}
    queue=[];inputs={};cache={}
    for team_id,player_id in SELECTED:
        selections=[('Fixed-rule example',data['fixed']['illustrative_ledger_examples']),
                    ('Additional alternative-rule example',data['alternative']['illustrative_new_passes'])]
        for category,candidates in selections:
            matches=[r for r in candidates if (r['team_id'],r['player_id'])==(team_id,player_id)]
            if len(matches)!=1:
                raise ValueError('Expected one existing illustrative example per player/category')
            candidate=matches[0];match_id=candidate['match_id']
            if category.startswith('Fixed') and not candidate['qualifies']:
                raise ValueError('Fixed-rule example is not positive')
            if category.startswith('Additional') and not candidate['newly_included']:
                raise ValueError('Additional example does not change classification')
            if match_id not in cache:
                events=raw.load_events(records[match_id],allow_download)
                cache[match_id]=({e['id']:e for e in events},
                                 {e['team']['id']:e['team']['name'] for e in events if e['type']['name']=='Starting XI' and e['period']==1})
                if len(cache[match_id][0])!=len(events):raise ValueError('Duplicate raw event ID')
            lookup,teams=cache[match_id]
            queue.append(review_event(candidate,lookup[candidate['pass_id']],teams,dates[match_id],category))
            inputs[match_id]=records[match_id]
    if len({(r['match_id'],r['pass_id']) for r in queue})!=len(queue):
        raise ValueError('Repeated review example')
    figure=ROOT/'figures/61_fullback_forward_advancement.png'
    return {'competition':'FIFA Women’s World Cup','season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3: Statistical scouting','section':'Modesty',
                             'url':'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#modesty'},
            'source_files':{k:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k,p in SOURCE_FILES.items()},
            'selection':'Two familiar examples selected for communication practice, not top-ranked candidates. They have different starting sides. Review examples reuse the first fixed-positive and first newly included ledger examples per player, not representative samples.',
            'cohort_size':len(data['cohort']['eligible_players']),'profiles':profiles,
            'review_queue':queue,'raw_inputs':[inputs[k] for k in sorted(inputs)],
            'figure':{'path':figure.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(figure.read_bytes()).hexdigest()},
            'authorship':'Guided analysis and report prepared with AI assistance. Independent reproduction, explanation and video observation remain separate milestones.',
            'scope':'Historical descriptive fullback profiles and a prepared video-review queue. No footage watched, marking/pressure claim, ability ranking, current signability assessment or signing recommendation.'}


def role_text(profile):
    return ', '.join(f'{count} {label.lower()} starts' for label,count in profile['position_starts'].items() if count)


def render_markdown(evidence):
    sections=[]
    for p in evidence['profiles']:
        g=p['middle_third']
        sections.append(f"""## {p['name']} · {p['team']}

{role_text(p)}; {p['minutes']:.1f} reconstructed registered minutes in those qualifying fixtures.

- Passing activity: {p['completed']}/{p['attempted']} eligible attempts completed ({p['completion_pct']:.1f}%); **{p['completed_per90']:.2f} completions per 90**.
- Fixed forward rule: {p['fixed_count']} completions; **{p['fixed_per90']:.2f}/90**, {p['fixed_share_pct']:.1f}% of eligible completions. Near-goal alternative: {p['alternative_count']}; **{p['alternative_per90']:.2f}/90**.
- Context: {p['no_room_count']} starts beyond x=100 ({p['no_room_pct']:.1f}% of completions). Within the middle third, {g['qualifying_completions']}/{g['completions']} meet the fixed rule ({g['within_third_qualifying_share_pct']:.1f}%).
""")
    profiles='\n'.join(sections)
    queue='\n'.join(f"- {r['player_name']} vs {r['opponent']}, {r['match_date']}, period {r['period']} at {r['minute']:02d}:{r['second']:02d}: {r['category']}; {r['start']} → {r['end']}, gain {r['x_gain']}. Recipient: {r['recipient'] or 'not recorded'}. Match {r['match_id']}, event {r['pass_id']}. **Not reviewed.**" for r in evidence['review_queue'])
    return f'''# Two historical fullback profiles: what should a scout review next?

**Alireza Erfanian · Football Analytics Research Lab · 6 November 2026 · Guided portfolio work**

**Data:** FIFA Women's World Cup, **2019** (StatsBomb competition 72 / season 30). **Reading:** [Soccermatics Lesson 3 — Statistical scouting, Modesty](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#modesty).

**Question:** What passing patterns are visible for these two fullback examples, and what observations would help interpret them? The full profiling pool contains {evidence['cohort_size']} players. Bronze and Majri were selected as familiar communication examples, not as the top two candidates. Their starting sides differ, so do not treat them as interchangeable recruitment options.

{profiles}

![Fixed-rule pass patterns in the selected fixtures](../{evidence['figure']['path']})

## What the figures support

Bronze recorded more eligible completions per 90 in her selected matches. Majri had a slightly higher fraction meeting the fixed forward rule, while the two middle-third fractions were close. These describe observed activity and starting-area context; they do not isolate passing ability. The alternative definition adds two Bronze passes and one Majri pass, without validating either rule as an action-value measure.

## Next action: review these four examples

{queue}

The four examples deliberately illustrate the two definitions; they are not representative samples of player performance. Event clocks are recorded match/period references, not video-file timestamps. No footage has been accessed or watched for this brief; observations are unfilled. The full statistical results above use all eligible events, not just these examples.

For each review, ask: which passing options were available, how much pressure did the passer face, did the recipient control the ball, and what happened next? Record observable answers before judging a decision. Then check whether patterns recur across additional matches and comparable role contexts.

## Limits and definitions

Eligible passes are non-restart, possession-team passes with known outcomes in each player's qualifying starting-role fixtures and registered intervals. Registered minutes include recorded added/extra time and retain temporary absences; halftime and shootouts are excluded. These are not independently checked official minute totals or verified fullback-position minutes. The initial pool required three qualifying starts, an exercise filter rather than a reliability guarantee.

Fixed rule: completed end_x − start_x ≥20 on the 0–120 length scale. Alternative: strictly positive gain ≥min(20, half the remaining x distance). Both ignore defender lines, pressure, lateral value and realistic options. Per-90 rates do not adjust for possession, opponent or later role changes. No ability ranking or signing recommendation follows from this brief. Current form, availability, contract and price are outside this historical dataset.

## Inspect and reproduce

Run `python 69_fullback_recruitment_brief.py` in Spyder or locally. [Styled brief](52_fullback_recruitment_brief.html) · [Evidence and source hashes](../data/69_fullback_recruitment_brief_evidence.json) · [Lesson 69](../lessons/0051-fullback-recruitment-brief.html) · [Full 35-player activity report](48_fullback_passing_per90.md).

Data: [StatsBomb Open Data](https://github.com/statsbomb/open-data), **2019 Women's World Cup**. {evidence['authorship']}
'''


def render_html(evidence):
    esc=html.escape
    cards=[]
    for p in evidence['profiles']:
        cards.append(f'''<section><h2>{esc(p['name'])}</h2><p>{esc(p['team'])}<br>{esc(role_text(p))} · {p['minutes']:.1f} registered minutes</p><ul><li><strong>{p['completed_per90']:.2f} completed passes /90</strong>; {p['completed']}/{p['attempted']} eligible attempts ({p['completion_pct']:.1f}%).</li><li>Fixed advancement: <strong>{p['fixed_count']} · {p['fixed_per90']:.2f}/90</strong>. Alternative: {p['alternative_count']} · {p['alternative_per90']:.2f}/90.</li><li>Starts beyond x=100: {p['no_room_count']} ({p['no_room_pct']:.1f}%).</li></ul></section>''')
    cards=''.join(cards)
    queue=''.join(f"<li><strong>{esc(r['player_name'])} vs {esc(r['opponent'])}</strong> · {esc(r['match_date'])}, P{r['period']} {r['minute']:02d}:{r['second']:02d}<br>{esc(r['category'])}; x={r['start'][0]} → {r['end'][0]}. Recipient: {esc(r['recipient'] or 'not recorded')}. <em>Not reviewed.</em></li>" for r in evidence['review_queue'])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Historical fullback profiles · Alireza Erfanian</title><link rel="stylesheet" href="../assets/report.css"></head><body><main class="report"><p class="eyebrow">Football Analytics Research Lab · Recruitment communication sample</p><h1>Two fullback profiles: what to review next</h1><p class="byline">Alireza Erfanian · FIFA Women's World Cup, <strong>2019</strong> · 6 November 2026 · Guided portfolio work</p><p><strong>Question:</strong> What passing activity is visible, and what observations would help interpret it? These familiar examples have different starting sides; they are not top-ranked candidates or interchangeable recruitment options.</p><div class="stats"><div class="stat"><strong>{evidence['cohort_size']}</strong><span>players in the historical profiling pool</span></div><div class="stat"><strong>2</strong><span>purposeful player examples</span></div><div class="stat"><strong>4</strong><span>events prepared for review · no footage watched</span></div></div><div class="columns">{cards}</div><figure><img src="../{esc(evidence['figure']['path'])}" alt="All fixed-rule qualifying completions for Bronze and Majri, showing their different starting sides."><figcaption>Every completion meeting the fixed 20-unit rule for these players. Both teams attack right; arrows join recorded starts and ends. <a href="../{esc(evidence['figure']['path'])}">Open full-size maps</a>.</figcaption></figure><h2>What the figures support</h2><p>Bronze recorded higher completed-pass activity per 90 in her selected matches. Majri's fixed-rule share was slightly higher (10.5% versus 9.7%); middle-third shares were close (12.5% versus 12.1%). These observations do not isolate ability. Changing the rule adds two Bronze passes and one Majri pass without validating either metric as action value.</p><div class="decision"><p><strong>Next action:</strong> review the examples below, record observations and check recurring patterns in additional comparable matches. No signing recommendation is supported by this brief alone.</p></div><h2>Prepared review events</h2><ol>{queue}</ol><p>Ask: what options and pressure were present, did the recipient control the ball, and what happened next? These examples illustrate definitions and are not representative samples. Match/period clocks are not video-file timestamps. Full event IDs and source hashes are in the evidence.</p><h2>Definitions and limits</h2><p>Eligible non-restart, possession-team passes with known outcomes; qualifying starting-role fixtures only. Registered minutes include recorded added/extra time and temporary absences, excluding halftime and shootouts. Later role changes are not split into position-specific time.</p><p>Fixed advancement: completed x gain ≥20 on the 0–120 scale. Alternative: positive gain ≥min(20, half the remaining x distance). Possession, opponents, pressure and difficulty are not adjusted for. The initial three-start filter does not guarantee reliability. This historical dataset does not establish current form, availability or transfer value.</p><footer><p><strong>Inspect:</strong> <a href="52_fullback_recruitment_brief.md">GitHub-readable brief</a> · <a href="../data/69_fullback_recruitment_brief_evidence.json">evidence and source hashes</a> · <a href="../69_fullback_recruitment_brief.py">reproduction code</a> · <a href="../lessons/0051-fullback-recruitment-brief.html">lesson</a>.</p><p>Data: <a href="https://github.com/statsbomb/open-data">StatsBomb Open Data</a>, <strong>2019 Women's World Cup</strong>. Reading: <a href="https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#modesty">Soccermatics Lesson 3 — Statistical scouting, Modesty</a>. {esc(evidence['authorship'])} No video observations or club impact are claimed.</p></footer></main></body></html>'''


def main():
    evidence=build_evidence()
    (ROOT/'data/69_fullback_recruitment_brief_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/52_fullback_recruitment_brief.md').write_text(render_markdown(evidence))
    (ROOT/'reports/52_fullback_recruitment_brief.html').write_text(render_html(evidence))
    print('Prepared',len(evidence['profiles']),'profiles and',len(evidence['review_queue']),'unreviewed examples')
    for row in evidence['review_queue']:print(row['player_name'],row['opponent'],row['period'],row['minute'],row['second'],row['recipient'])


if __name__=='__main__':
    main()
