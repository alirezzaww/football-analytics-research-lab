"""Timing boundaries and independent running-total reconciliation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('timeline', ROOT / '30_cumulative_xg_timeline.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class TimelineTests(unittest.TestCase):
    def test_added_time_stays_before_second_half_and_totals_carry(self):
        rows = [dict(match_id=1, id='later', team='A', period=2, minute=45, second=10, model_probability=.2, goal=0),
                dict(match_id=1, id='earlier', team='A', period=1, minute=47, second=0, model_probability=.3, goal=1)]
        first, second, empty_first, empty_second = lesson.build_timelines(rows, ['A', 'B'])
        self.assertEqual(first['points'][0]['id'], 'earlier')
        self.assertEqual(first['points'][0]['half_clock_minute'], 47)
        self.assertAlmostEqual(second['points'][0]['half_clock_minute'], 10 / 60)
        self.assertEqual(second['start_npxg'], .3)
        self.assertEqual(second['end_npxg'], .5)
        self.assertEqual(empty_second['end_npxg'], 0)
        with self.assertRaises(ValueError):
            lesson.build_timelines(rows + rows[:1], ['A', 'B'])

    def test_saved_timeline_reconciles_each_shot_and_half(self):
        evidence = json.loads((ROOT / 'data/30_cumulative_xg_evidence.json').read_text())
        path = ROOT / evidence['source_path']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), evidence['source_sha256'])
        source = json.loads(path.read_text())
        self.assertEqual(evidence['fixture'], source['fixture'])
        for team in source['teams']:
            total = 0
            groups = [r for r in evidence['timelines'] if r['team'] == team['team']]
            self.assertEqual([r['period'] for r in groups], [1, 2])
            for group in groups:
                expected = sorted([r for r in source['shots'] if r['team'] == team['team'] and r['period'] == group['period']],
                                  key=lambda r: (r['minute'], r['second']))
                self.assertEqual(group['start_npxg'], total)
                self.assertEqual(group['shots'], len(expected))
                self.assertEqual([r['id'] for r in group['points']], [r['id'] for r in expected])
                start = total
                for point, shot in zip(group['points'], expected):
                    total += shot['model_probability']
                    self.assertEqual(point['shot_xg'], shot['model_probability'])
                    self.assertEqual(point['goal'], shot['goal'])
                    self.assertEqual(point['minute'], shot['minute'])
                    self.assertEqual(point['second'], shot['second'])
                    self.assertEqual(point['half_clock_minute'], shot['minute'] - (45 if group['period'] == 2 else 0) + shot['second'] / 60)
                    self.assertEqual(point['cumulative_npxg'], total)
                self.assertAlmostEqual(group['half_npxg'], total - start)
                self.assertEqual(group['end_npxg'], total)
            self.assertAlmostEqual(total, team['model_npxg'])
