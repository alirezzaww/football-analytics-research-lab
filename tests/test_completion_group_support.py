"""Support groups and reference weights are descriptive, not confidence scores."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_support', ROOT / '51_completion_group_support.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CompletionSupportTests(unittest.TestCase):
    def test_support_boundaries_are_disjoint(self):
        for n, index in [(0,0),(1,1),(19,1),(20,2),(49,2),(50,3)]:
            self.assertEqual(lesson.support_band(n), lesson.BANDS[index])
        with self.assertRaises(ValueError):
            lesson.support_band(-1)

    def test_reference_weight_decreases_with_more_local_data(self):
        self.assertEqual(lesson.prior_weight(0,20), 1)
        self.assertEqual(lesson.prior_weight(20,20), .5)
        self.assertAlmostEqual(lesson.prior_weight(180,20), .1)
        for strength in (0,-1,float('nan')):
            with self.assertRaises(ValueError):
                lesson.prior_weight(10,strength)

    def test_weighted_form_equals_original_count_formula(self):
        n, completions, reference, strength = 10, 9, .9067617221822829, 20
        weight = lesson.prior_weight(n,strength)
        self.assertAlmostEqual((1-weight)*(completions/n)+weight*reference,
                               (completions+strength*reference)/(n+strength))
