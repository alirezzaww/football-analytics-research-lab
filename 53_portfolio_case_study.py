"""Lesson 53: generate a concise analyst case study from audited project evidence."""
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_PATHS={
    'study':'data/38_france_corner_study_evidence.json',
    'windows':'data/37_corner_window_evidence.json',
    'profiles':'data/39_corner_delivery_profiles_evidence.json',
    'side':'data/41_corner_side_evidence.json',
    'review':'data/43_corner_review_queue_evidence.json',
}


def build_evidence():
    data={k:json.loads((ROOT/p).read_text()) for k,p in SOURCE_PATHS.items()}
    pooled=data['study']['pooled']
    goals_by_match=[{'opponent':r['opponent'],'phase_shot_goals':r['phase_shot_goals']} for r in data['study']['matches']]
    unknown=next(g for g in data['profiles']['groups'] if g['category']=='Other / unrecorded')
    rates=[{'seconds':r['window_seconds'],'corners_with_shot':r['teams'][0]['corners_with_shot'],'deliveries':r['teams'][0]['deliveries']} for r in data['windows']['results']]
    return {'source_files':{k:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k,p in SOURCE_PATHS.items()},
            'facts':{'matches':pooled['matches'],'deliveries':pooled['deliveries'],
                     'corners_with_shot':pooled['corners_with_phase_shot'],'corner_shot_rate':pooled['phase_shot_rate'],
                     'phase_shots':pooled['phase_shots'],'phase_shot_goals':pooled['phase_shot_goals'],
                     'goals_by_match':goals_by_match,'unrecorded_technique_deliveries':unknown['deliveries'],
                     'same_taker_side_match_contexts_with_both_types':data['side']['contexts_with_both_types'],
                     'review_examples':sum(r['example'] is not None for r in data['review']['review_queue']),
                     'korea_window_results':rates},
            'figure':{'path':'figures/41_france_corner_match_variation.png','sha256':hashlib.sha256((ROOT/'figures/41_france_corner_match_variation.png').read_bytes()).hexdigest()},
            'authorship':'Guided research and implementation prepared with AI assistance. Independent reproduction and interpretation remain separate milestones.',
            'video_status':'Review brief prepared; no footage reviewed.'}


def render_report(evidence):
    f=evidence['facts']
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>France corner phases · Alireza Erfanian</title><link rel="stylesheet" href="../assets/report.css"></head><body><main class="report">
<p class="eyebrow">Football Analytics Research Lab · Portfolio case study</p><h1>France’s corner phases across five World Cup matches</h1>
<p class="byline">Alireza Erfanian · 2019 Women’s World Cup · Published 4 November 2026 · Guided research</p>
<p><strong>Question:</strong> How often were France’s corner deliveries associated with a shot, and what evidence should a coach review next?</p>
<div class="stats"><div class="stat"><strong>{f['deliveries']}</strong><span>recorded deliveries · {f['matches']} fixtures</span></div><div class="stat"><strong>{f['corners_with_shot']}/{f['deliveries']} · {f['corner_shot_rate']:.1%}</strong><span>corners associated with a phase shot</span></div><div class="stat"><strong>{f['phase_shots']} shots · {f['phase_shot_goals']} goals</strong><span>inside the defined phases</span></div></div>
<div class="columns"><figure><img src="../{evidence['figure']['path']}" alt="France corner-phase shot association by opponent, with each match denominator and the pooled rate."><figcaption>Same 15-second phase rule across fixtures. Brazil includes extra time. Small match denominators limit comparisons.</figcaption></figure>
<section><h2>Three findings to carry forward</h2><ul><li>Shot-associated phases occur across all five fixtures, but <strong>both observed phase goals came against Korea Republic</strong>.</li><li>Delivery-type groups mix takers and sides. There are <strong>{f['same_taker_side_match_contexts_with_both_types']} same-taker/side/match groups with both recorded inswingers and outswingers</strong>; this limits direct comparison.</li><li><strong>{f['unrecorded_technique_deliveries']} of {f['deliveries']} technique labels are unrecorded</strong>. Missing labels stay visible instead of being guessed.</li></ul></section></div>
<div class="decision"><h2>Decision supported: prioritize targeted review</h2><p>Use the <a href="26_corner_video_review_brief.md">{f['review_examples']}-example review queue</a> to inspect first contact, receiving control and defensive marking. The present evidence supports review priorities; it does not establish a preferred delivery technique or target zone. Footage has not yet been reviewed.</p></div>
<h2>Definition and limits</h2><p>Count every recorded corner Pass event, including incomplete deliveries. Associate same-team non-penalty shots within 15 seconds in the same possession, ending at a new restart, period/possession change or goal. Periods 1–4 are included and each shot is assigned once. This is a descriptive phase proxy, not causal corner value or a measurement of intended targets.</p>
<p>The time-window check on the Korea Republic fixture changes from 4/13 corners at five seconds to 6/13 at 10, 15 and 20 seconds. That sensitivity check has not been repeated across all five matches. The pooled rate weights deliveries equally: sum positive corners, then divide by all deliveries.</p>
<footer><p><strong>Inspect and reproduce:</strong> <a href="21_france_tournament_corner_study.md">full study</a> · <a href="24_corner_side_context.md">comparison support</a> · <a href="../38_france_tournament_corners.py">analysis code</a> · <a href="../README.md">project setup</a>.</p><p>Data: <a href="https://github.com/statsbomb/open-data">StatsBomb Open Data</a>. Course foundation: <a href="https://soccermatics.readthedocs.io/en/latest/">Soccermatics</a>. {html.escape(evidence['authorship'])} No club impact, scouting recommendation or independently completed video analysis is claimed.</p></footer>
</main></body></html>'''


def render_markdown(evidence):
    f=evidence['facts']
    return f"""# France’s corner phases across five World Cup matches

**Alireza Erfanian · Football Analytics Research Lab · Guided research · 4 November 2026**

**Question:** How often were France’s corners associated with a shot, and what should a coach review next?

- **{f['matches']} fixtures, {f['deliveries']} recorded corner deliveries.**
- **{f['corners_with_shot']}/{f['deliveries']} ({f['corner_shot_rate']:.1%})** associated with at least one shot under the defined phase rule.
- **{f['phase_shots']} associated shots, {f['phase_shot_goals']} goals.** Both goals came against Korea Republic.

![France corner-phase shot association by opponent](../{evidence['figure']['path']})

## Findings

The match-by-match denominators are small. The Korea Republic goal outcome alone gives an incomplete view of the campaign; shot-associated phases occur in all five fixtures.

Delivery-type comparisons mix takers and corner sides. No same-taker/side/match group contains both recorded inswingers and outswingers, limiting a direct like-for-like comparison. Nine technique labels are unrecorded and remain visible.

## Practical next action

Use the [six-event review brief](26_corner_video_review_brief.md) to inspect first contact, receiving control and defensive marking. Footage has not yet been reviewed. These data support review priorities rather than a recommendation to switch delivery technique or target zone.

## Method and limits

Count every recorded corner Pass event, including incomplete deliveries. Associate same-team non-penalty shots within 15 seconds in the same possession, stopping at a new restart, period/possession change or goal. Include extra time and assign each shot once. This is a descriptive phase proxy, not causal corner value.

Pool counts before division to weight each delivery equally. The Korea Republic window check yields 4/13 at five seconds and 6/13 at 10, 15 and 20 seconds; it has not been repeated across every match. Recorded endpoints do not establish intended targets or controlled receptions.

[Full study](21_france_tournament_corner_study.md) · [Comparison support](24_corner_side_context.md) · [Reproduce the analysis](../38_france_tournament_corners.py) · [Styled local/print view](36_france_corner_portfolio_case_study.html)

Data: [StatsBomb Open Data](https://github.com/statsbomb/open-data). Course foundation: [Soccermatics](https://soccermatics.readthedocs.io/en/latest/). {evidence['authorship']} No club impact, completed video scouting or independent mastery is claimed.
"""


def main():
    evidence=build_evidence()
    (ROOT/'data/53_portfolio_case_study_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/36_france_corner_portfolio_case_study.html').write_text(render_report(evidence))
    (ROOT/'reports/36_france_corner_portfolio_case_study.md').write_text(render_markdown(evidence))
    print('Generated portfolio case study from verified source references:',evidence['facts']['deliveries'],'deliveries')


if __name__=='__main__':
    main()
