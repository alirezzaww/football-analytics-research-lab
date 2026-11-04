"""Grid boundaries, failed-move denominator and a known fixed-point solution."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('first_xt', ROOT / '44_first_expected_threat.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class FirstXTTests(unittest.TestCase):
    def test_grid_edges_do_not_wrap_or_clip_outside_points(self):
        self.assertEqual(lesson.cell([0, 0]), 0)
        self.assertEqual(lesson.cell([120, 80]), 23)
        self.assertEqual(lesson.cell([20, 20]), 7)
        for point in (None, [121, 40], [-1, 0], [0, float('nan')]):
            self.assertIsNone(lesson.cell(point))

    def test_failed_moves_stay_in_action_denominator(self):
        rows = [{'start_cell': 0, 'end_cell': 1, 'type': 'Pass', 'successful_move': True, 'goal': 0},
                {'start_cell': 0, 'end_cell': 1, 'type': 'Pass', 'successful_move': False, 'goal': 0},
                {'start_cell': 1, 'end_cell': None, 'type': 'Shot', 'successful_move': False, 'goal': 1},
                {'start_cell': 1, 'end_cell': None, 'type': 'Shot', 'successful_move': False, 'goal': 0}]
        model = lesson.fit_grid(rows)
        self.assertEqual(model['successful_transition_per_action'][0][1], .5)
        self.assertAlmostEqual(model['zone_values'][1], .5)
        self.assertAlmostEqual(model['zone_values'][0], .25)
        self.assertEqual(model['zone_values'][2], 0)  # Unobserved cell, not proof of zero true threat.

    def test_repeated_safe_moves_propagate_future_value_until_convergence(self):
        rows = [{'start_cell': 0, 'end_cell': 0, 'type': 'Carry', 'successful_move': True, 'goal': 0},
                {'start_cell': 0, 'end_cell': 1, 'type': 'Pass', 'successful_move': True, 'goal': 0},
                {'start_cell': 1, 'end_cell': None, 'type': 'Shot', 'successful_move': False, 'goal': 1}]
        model = lesson.fit_grid(rows)
        self.assertAlmostEqual(model['zone_values'][0], 1, places=10)
        self.assertLess(model['fixed_point_residual'], 1e-12)
