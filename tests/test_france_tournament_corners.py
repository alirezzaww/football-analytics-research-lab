"""Pooled delivery exposure must not be replaced by an unweighted match mean."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('france_corner_study', ROOT / '38_france_tournament_corners.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class TournamentCornerTests(unittest.TestCase):
    def test_pooled_rate_weights_each_delivery_equally(self):
        rows = [{'deliveries': 10, 'corners_with_phase_shot': 10, 'phase_shots': 12, 'phase_shot_goals': 1},
                {'deliveries': 1, 'corners_with_phase_shot': 0, 'phase_shots': 0, 'phase_shot_goals': 0}]
        result = lesson.pool(rows)
        self.assertAlmostEqual(result['phase_shot_rate'], 10 / 11)
        self.assertNotEqual(result['phase_shot_rate'], .5)
        self.assertEqual(result['phase_shots'], 12)

    def test_empty_exposure_has_no_defined_rate(self):
        self.assertIsNone(lesson.pool([])['phase_shot_rate'])
        self.assertEqual(lesson.pool([])['deliveries'], 0)
