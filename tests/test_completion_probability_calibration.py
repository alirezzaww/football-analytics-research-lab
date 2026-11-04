"""Probability-group boundaries, missing exposure and observed frequencies."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_calibration', ROOT / '49_completion_probability_calibration.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CompletionCalibrationTests(unittest.TestCase):
    def test_edges_are_included_once_and_one_is_in_last_band(self):
        for probability, expected in [(0, 0), (.5999, 0), (.6, 1), (.7, 2), (.8, 3), (.9, 4), (1, 4)]:
            self.assertEqual(lesson.probability_band(probability), expected)
        for invalid in (-.01, 1.01, float('nan')):
            with self.assertRaises(ValueError):
                lesson.probability_band(invalid)

    def test_empty_group_is_not_an_observed_zero_rate(self):
        self.assertIsNone(lesson.summarize([])['observed_completion_rate'])
        row = {'match_id': 1, 'id': 'a', 'completed': 0, 'zone_probability': .6}
        self.assertEqual(lesson.summarize([row])['observed_completion_rate'], 0)

    def test_mean_prediction_and_observed_fraction_use_different_inputs(self):
        rows = [{'match_id': 1, 'id': str(i), 'completed': y, 'zone_probability': p}
                for i, (y, p) in enumerate([(1, .8), (0, .9)])]
        result = lesson.summarize(rows)
        self.assertAlmostEqual(result['mean_prediction'], .85)
        self.assertEqual(result['observed_completion_rate'], .5)
        self.assertEqual(result['completions'], 1)
