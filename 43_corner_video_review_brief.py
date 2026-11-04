"""Lesson 43: translate event analysis into an auditable qualitative-review queue.

Selects examples and questions only. It performs no video review or tactical coding.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def select_examples(rows, protocol):
    """Deliberate zone/outcome coverage with fixture variety; not random sampling."""
    ordered = sorted(rows, key=lambda r: (r['match_date'], r['match_id'], r['event_index']))
    used_matches = set()
    selected = []
    for zone in protocol['zones']:
        for status in protocol['phase_outcome_order']:
            candidates = [r for r in ordered if r['endpoint_zone'] == zone and r['phase_has_shot'] == status]
            preferred = [r for r in candidates if r['match_id'] not in used_matches]
            chosen = (preferred or candidates)[0] if candidates else None
            if chosen:
                used_matches.add(chosen['match_id'])
            selected.append({'endpoint_zone': zone, 'phase_has_shot': status, 'example': chosen})
    return selected


def build_evidence():
    path = ROOT / 'data/42_corner_endpoint_evidence.json'
    source = json.loads(path.read_text())
    protocol_path = ROOT / 'data/43_review_queue_protocol.json'
    protocol = json.loads(protocol_path.read_text())
    study = json.loads((ROOT / 'data/38_france_corner_study_evidence.json').read_text())
    records = {}
    for match in study['matches']:
        raw = match['raw_input']; cached = ROOT / raw['relative_path']
        if not cached.exists():
            with urlopen(raw['source_url'], timeout=60) as response:
                payload = response.read()
            if hashlib.sha256(payload).hexdigest() != raw['sha256']:
                raise ValueError('Raw source changed')
            cached.parent.mkdir(parents=True, exist_ok=True); cached.write_bytes(payload)
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == raw['sha256']
        records[match['fixture']['match_id']] = (match['fixture'], {r['id']: r for r in json.loads(cached.read_text())})
    rows = []
    for row in source['deliveries']:
        fixture, events = records[row['match_id']]
        event = events[row['corner_id']]
        rows.append({**row, 'match_date': fixture['match_date'], 'event_index': event['index'],
                     'period': event['period'], 'minute': event['minute'], 'second': event['second'],
                     'event_timestamp': event['timestamp']})
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'protocol_path': protocol_path.relative_to(ROOT).as_posix(),
            'protocol_sha256': hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            'candidate_deliveries': rows, 'review_queue': select_examples(rows, protocol),
            'questions': protocol['questions'], 'video_status': protocol['video_status'],
            'scope': protocol['purpose']}


def render_brief(evidence):
    lines = ['# Lesson 43: corner video-review brief', '',
             '## Question for the review', '',
             'What observable first-contact, receiving and marking details help explain the event sequences behind the endpoint groups?', '',
             '## Data finding to investigate', '',
             'Across five France matches, 19 of 45 corner deliveries associate with a shot under the fixed phase rule. Recorded endpoints fall inside the six-yard box (15), elsewhere in the penalty area (19), or outside it (11). These counts describe events; they do not identify intended targets or controlled receptions.', '',
             '## Selected examples', '',
             'One example is selected for each zone and each phase-shot status, preferring fixtures not already selected. This deliberate selection supplies review contrasts; it cannot estimate overall rates or causal differences. All percentages remain calculated from the full 45 deliveries.', '']
    for i, cell in enumerate(evidence['review_queue'], 1):
        row = cell['example']
        status = 'phase shot recorded' if cell['phase_has_shot'] else 'no phase shot under the rule'
        if row is None:
            lines += [f'{i}. {cell["endpoint_zone"]}, {status}: no available example.', '']; continue
        period = {1: 'first half', 2: 'second half', 3: 'extra time, first period', 4: 'extra time, second period'}[row['period']]
        opponent = row['opponent'].replace(" Women's", '')
        lines += [f'{i}. **France v {opponent} · {row["match_date"]} · {row["minute"]:02d}:{row["second"]:02d} ({period})**',
                  f'   {row["passer"]}; {cell["endpoint_zone"]}; {status}.',
                  f'   Match `{row["match_id"]}`, corner `{row["corner_id"]}`, event index `{row["event_index"]}`.',
                  '   Review status: **not reviewed**. First contact: unknown. Attacking control: unknown. Video reference: unavailable.', '']
    lines += ['## Review questions', ''] + [f'- {q}' for q in evidence['questions']]
    lines += ['', 'Use unknown/unclear when an observation is not visible. Distinguish observable actions from a tactical interpretation. A camera cut or obscured player is missing evidence, not evidence of no action.', '',
              '## Locate the event correctly', '',
              'The times above are recorded match-clock labels, not positions in a video file. Use the period and opponent/date as well as the clock: first-half added time can overlap nominal second-half minutes. Find the delivery in the footage and record its actual video reference before coding. No footage has been accessed or reviewed for this assignment.', '',
              '## Reproduce and assignment status', '',
              'Run `python 43_corner_video_review_brief.py`. It saves `data/43_corner_review_queue_evidence.json` and regenerates this report from the recorded event candidates. Source/protocol hashes and all 45 candidates are preserved so the purposive selection can be reproduced and audited.', '',
              '**Completed assignment:** a sourced six-example review queue and observation questions. **Not performed:** video observation or tactical coding; those require footage. Preparing the brief does not establish independent user mastery.', '',
              'This complements the existing StatsBomb event analysis and Soccermatics learning project. No new model, causal effect or fresh validation is claimed.']
    return '\n'.join(lines) + '\n'


def main():
    evidence = build_evidence()
    (ROOT / 'data/43_corner_review_queue_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    (ROOT / 'reports/26_corner_video_review_brief.md').write_text(render_brief(evidence))
    for cell in evidence['review_queue']:
        row = cell['example']
        print(cell['endpoint_zone'], cell['phase_has_shot'], (row['opponent'], row['minute'], row['second']) if row else 'Unavailable')


if __name__ == '__main__':
    main()
