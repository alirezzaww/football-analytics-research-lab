"""Whole-match exclusion must protect fitted probabilities from check labels."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_match_cv', ROOT / '48_completion_match_cross_validation.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CompletionMatchCVTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{'match_id': m, 'id': str(i), 'team': 'Example', 'start_cell': 0, 'completed': y}
                     for m, labels in [(1, [0, 1]), (2, [1, 1]), (3, [0, 1]), (4, [0, 1])] for i, y in enumerate(labels)]

    def test_changing_check_labels_does_not_change_its_fitted_predictions(self):
        initial = lesson.leave_match_out(self.rows, [1, 2, 3, 4], 20)
        changed_rows = copy.deepcopy(self.rows)
        for row in changed_rows:
            if row['match_id'] == 1:
                row['completed'] = 1
        changed = lesson.leave_match_out(changed_rows, [1, 2, 3, 4], 20)
        self.assertEqual(initial['folds'][0]['model'], changed['folds'][0]['model'])
        p1 = [r['zone_probability'] for r in initial['predictions'] if r['match_id'] == 1]
        p2 = [r['zone_probability'] for r in changed['predictions'] if r['match_id'] == 1]
        self.assertEqual(p1, p2)
        self.assertNotEqual(initial['folds'][0]['zone_metrics']['log_loss'], changed['folds'][0]['zone_metrics']['log_loss'])

    def test_each_pass_predicted_once_and_each_fixture_excluded_from_its_fit(self):
        result = lesson.leave_match_out(self.rows, [1, 2, 3, 4], 20)
        self.assertEqual(len(result['predictions']), len(self.rows))
        self.assertEqual(len({(r['match_id'], r['id']) for r in result['predictions']}), len(self.rows))
        for fold in result['folds']:
            self.assertNotIn(fold['held_out_match_id'], fold['training_match_ids'])
            self.assertEqual(fold['model']['training_attempts'], 6)

    def test_missing_or_duplicate_fixture_list_is_rejected(self):
        for ids in ([1, 2], [1, 2, 3, 4, 4]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                lesson.leave_match_out(self.rows, ids, 20)
