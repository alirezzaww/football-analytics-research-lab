"""Purposive review selection must stay reproducible and retain empty cells."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_brief', ROOT / '43_corner_video_review_brief.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class ReviewBriefTests(unittest.TestCase):
    def test_prefer_unused_fixture_without_changing_cell(self):
        protocol = {'zones': ['A'], 'phase_outcome_order': [False, True]}
        rows = [{'match_id': m, 'match_date': d, 'event_index': i, 'endpoint_zone': 'A', 'phase_has_shot': shot}
                for m, d, i, shot in [(1, '2019-01-01', 1, False), (1, '2019-01-01', 2, True), (2, '2019-01-02', 1, True)]]
        selected = lesson.select_examples(list(reversed(rows)), protocol)
        self.assertEqual([r['example']['match_id'] for r in selected], [1, 2])
        self.assertEqual([r['phase_has_shot'] for r in selected], [False, True])

    def test_missing_cell_remains_explicit(self):
        selected = lesson.select_examples([], {'zones': ['A'], 'phase_outcome_order': [False, True]})
        self.assertEqual(len(selected), 2)
        self.assertTrue(all(r['example'] is None for r in selected))

    def test_committed_report_reproduces_without_network(self):
        evidence = json.loads((ROOT / 'data/43_corner_review_queue_evidence.json').read_text())
        report = (ROOT / 'reports/26_corner_video_review_brief.md').read_text()
        self.assertEqual(report, lesson.render_brief(evidence))
        self.assertIn('not reviewed', report)
