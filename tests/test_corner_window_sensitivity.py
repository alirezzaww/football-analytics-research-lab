"""Window endpoints must use full precision rather than displayed clock rounding."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('window_sensitivity', ROOT / '37_corner_window_sensitivity.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CornerWindowTests(unittest.TestCase):
    def test_five_point_zero_zero_three_seconds_is_not_within_five(self):
        helper = lesson.load_phase_helper()
        corner = {'index': 1, 'timestamp': '00:08:00.000', 'period': 1, 'possession': 2, 'team': {'id': 1}}
        shot = {'id': 's', 'index': 2, 'timestamp': '00:08:05.003', 'period': 1, 'possession': 2,
                'team': {'id': 1}, 'type': {'name': 'Shot'}, 'shot': {'outcome': {'name': 'Saved'}}}
        included = {'s': {'goal': 0, 'model_probability': .2}}
        for window, expected in [(5, 0), (10, 1), (15, 1), (20, 1)]:
            rules = {'maximum_seconds_inclusive': window, 'restart_pass_types': ['Corner']}
            with self.subTest(window=window):
                self.assertEqual(len(helper.phase_after(corner, [shot], included, rules)['shots']), expected)
