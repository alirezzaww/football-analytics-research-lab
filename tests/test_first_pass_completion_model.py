"""Smoothing, empty cells, valid probability scoring and fixture separation."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_model', ROOT / '47_first_pass_completion_model.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CompletionModelTests(unittest.TestCase):
    def test_smoothing_moves_sparse_perfect_cell_toward_training_average(self):
        rows = [{'start_cell': 0, 'completed': 1}, {'start_cell': 1, 'completed': 0}]
        model = lesson.fit_zones(rows, 20)
        self.assertEqual(model['global_training_rate'], .5)
        self.assertAlmostEqual(model['zones'][0]['smoothed_probability'], 11 / 21)
        self.assertEqual(model['zones'][2]['smoothed_probability'], .5)
        self.assertIsNone(model['zones'][2]['raw_completion_rate'])

    def test_invalid_fit_and_scoring_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            lesson.fit_zones([], 20)
        with self.assertRaises(ValueError):
            lesson.fit_zones([{'start_cell': 0, 'completed': 1}], 0)
        with self.assertRaises(ValueError):
            lesson.score_probabilities([{'completed': 1, 'p': 2}], 'p')

    def test_probabilities_are_scored_against_actual_completion(self):
        good = [{'completed': 1, 'p': .9}, {'completed': 0, 'p': .1}]
        flat = [{'completed': 1, 'p': .5}, {'completed': 0, 'p': .5}]
        self.assertLess(lesson.score_probabilities(good, 'p')['log_loss'], lesson.score_probabilities(flat, 'p')['log_loss'])
        self.assertAlmostEqual(lesson.score_probabilities(good, 'p')['brier_score'], .01)

    def test_saved_fit_uses_only_training_rows_and_reproduces_cache_free(self):
        evidence = json.loads((ROOT / 'data/47_completion_model_evidence.json').read_text())
        train = [r for r in evidence['passes'] if r['split'] == 'train']
        check = [r for r in evidence['passes'] if r['split'] == 'exploratory_check']
        self.assertFalse({r['match_id'] for r in train} & {r['match_id'] for r in check})
        self.assertEqual(evidence['model'], lesson.fit_zones(train, evidence['model']['smoothing_strength']))
        self.assertEqual(evidence, lesson.build_evidence())
