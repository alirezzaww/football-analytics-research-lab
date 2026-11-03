"""Shot identity, denominators and saved match evidence reconciliation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('match_summary', ROOT / '29_match_xg_summary.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class MatchSummaryTests(unittest.TestCase):
    def test_volume_quality_and_empty_team(self):
        rows = [{'match_id': 1, 'id': str(i), 'team': 'A', 'goal': i, 'model_probability': p}
                for i, p in enumerate([.1, .3])]
        a, b = lesson.summarize(rows, ['A', 'B'])
        self.assertAlmostEqual(a['model_npxg'], .4)
        self.assertAlmostEqual(a['model_npxg_per_shot'], .2)
        self.assertEqual(a['shot_goals'], 1)
        self.assertEqual(b['model_npxg'], 0)
        self.assertIsNone(b['model_npxg_per_shot'])
        with self.assertRaises(ValueError):
            lesson.summarize(rows + rows[:1], ['A', 'B'])

    def test_saved_evidence_uses_each_frozen_shot_once(self):
        evidence = json.loads((ROOT / 'data/29_match_xg_evidence.json').read_text())
        source_path = ROOT / evidence['source_path']
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(), evidence['source_sha256'])
        source = json.loads(source_path.read_text())
        protocol = json.loads((ROOT / source['protocol_path']).read_text())
        self.assertEqual(evidence['fixture'], protocol['fixture_metadata'][0])
        match_id = evidence['fixture']['match_id']
        expected = {r['id']: r for r in source['shots'] if r['match_id'] == match_id}
        self.assertEqual(len(evidence['shots']), len(expected))
        self.assertEqual({r['id'] for r in evidence['shots']}, set(expected))
        for row in evidence['shots']:
            for key, value in expected[row['id']].items():
                self.assertEqual(row[key], value)
        teams = [evidence['fixture']['home_team'], evidence['fixture']['away_team']]
        self.assertEqual(evidence['teams'], lesson.summarize(evidence['shots'], teams))
        raw = evidence['raw_input']
        self.assertIn(raw, source['raw_inputs'])
        path = ROOT / raw['relative_path']
        if path.exists():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), raw['sha256'])
            events = {r['id']: r for r in json.loads(path.read_text())}
            for row in evidence['shots']:
                self.assertEqual(row['team'], events[row['id']]['team']['name'])
                for key in ['minute', 'second', 'period']:
                    self.assertEqual(row[key], events[row['id']][key])
