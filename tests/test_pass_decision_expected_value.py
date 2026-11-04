"""Probability weighting and failure continuation in hypothetical decisions."""
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('decision_value', ROOT / '46_pass_decision_expected_value.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class PassDecisionTests(unittest.TestCase):
    def test_probability_endpoints_reproduce_observed_outcome_scores(self):
        self.assertAlmostEqual(lesson.expected_change(.03, .08, 0), -.03)
        self.assertAlmostEqual(lesson.expected_change(.03, .08, 1), .05)
        self.assertAlmostEqual(lesson.expected_change(.03, .08, .4), .002)

    def test_failure_continuation_is_an_explicit_assumption(self):
        self.assertAlmostEqual(lesson.expected_change(.03, .08, .4, .01), .008)

    def test_invalid_probabilities_and_values_are_rejected(self):
        for p in [-.1, 1.1, math.nan, math.inf]:
            with self.subTest(p=p), self.assertRaises(ValueError):
                lesson.expected_change(.03, .08, p)

    def test_saved_source_thresholds_have_equal_expected_values(self):
        evidence = lesson.build_evidence()
        start = evidence['start_value']; target = evidence['risky_destination_value']
        self.assertAlmostEqual(lesson.expected_change(start, target, evidence['riskier_probability_to_break_even_with_start']), 0)
        self.assertAlmostEqual(lesson.expected_change(start, target, evidence['riskier_probability_to_match_safer_option']), evidence['options'][0]['expected_value_change'])
