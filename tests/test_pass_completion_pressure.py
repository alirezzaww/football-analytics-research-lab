"""Pressure flags, sparse groups and held-out outcome isolation."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_pressure', ROOT / '50_pass_completion_pressure_feature.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CompletionPressureTests(unittest.TestCase):
    def test_only_explicit_true_is_flagged_and_bad_types_are_rejected(self):
        self.assertTrue(lesson.recorded_pressure(True))
        self.assertFalse(lesson.recorded_pressure(False))
        self.assertFalse(lesson.recorded_pressure(None))
        for value in (1, 0, 'true', ''):
            with self.assertRaises(ValueError):
                lesson.recorded_pressure(value)

    def test_missing_subgroup_falls_back_to_training_origin_prior(self):
        rows = [{'start_cell': 0, 'completed': 1, 'pressure_flag': False},
                {'start_cell': 1, 'completed': 0, 'pressure_flag': True}]
        model = lesson.fit_pressure(rows)
        group = next(g for g in model['groups'] if g['cell'] == 0 and g['pressure_flag'])
        self.assertEqual(group['attempts'], 0)
        self.assertAlmostEqual(group['probability'], model['origin_model']['zones'][0]['smoothed_probability'])

    def test_smoothing_keeps_sparse_perfect_group_below_one(self):
        rows = [{'start_cell': 0, 'completed': 1, 'pressure_flag': True},
                {'start_cell': 0, 'completed': 0, 'pressure_flag': False}]
        model = lesson.fit_pressure(rows)
        group = next(g for g in model['groups'] if g['cell'] == 0 and g['pressure_flag'])
        self.assertAlmostEqual(group['probability'], 11/21)

    def test_held_out_labels_cannot_change_its_pressure_predictions(self):
        rows = [{'match_id': m, 'id': str(i), 'team': 'Example', 'start_cell': 0, 'completed': y, 'pressure_flag': bool(i)}
                for m, labels in [(1,[0,1]),(2,[1,1]),(3,[0,1]),(4,[0,1])] for i,y in enumerate(labels)]
        original = lesson.cross_validate(rows, [1,2,3,4], 20, 20)
        changed_rows = copy.deepcopy(rows)
        for row in changed_rows:
            if row['match_id'] == 1:
                row['completed'] = 1
        changed = lesson.cross_validate(changed_rows, [1,2,3,4], 20, 20)
        self.assertEqual(original['folds'][0]['model'], changed['folds'][0]['model'])
        self.assertEqual([r['pressure_probability'] for r in original['predictions'] if r['match_id']==1],
                         [r['pressure_probability'] for r in changed['predictions'] if r['match_id']==1])
