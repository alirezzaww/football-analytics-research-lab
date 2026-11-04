"""Loss assumption, failed endpoints and unknown outcomes must stay explicit."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('failed_pass_value', ROOT / '45_failed_pass_value.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class FailedPassValueTests(unittest.TestCase):
    def test_completed_pass_uses_signed_destination_difference(self):
        self.assertAlmostEqual(lesson.score_pass(.03, .08, None)[1], .05)
        self.assertAlmostEqual(lesson.score_pass(.03, .01, None)[1], -.02)
        self.assertEqual(lesson.score_pass(.03, .03, None)[1], 0)

    def test_unsuccessful_pass_does_not_receive_endpoint_credit(self):
        for outcome in ('Incomplete', 'Out', 'Pass Offside'):
            self.assertEqual(lesson.score_pass(.03, .08, outcome)[1], -.03)
            self.assertEqual(lesson.score_pass(.03, None, outcome)[1], -.03)

    def test_unknown_or_injury_clearance_is_not_assumed_loss(self):
        for outcome in ('Unknown', 'Injury Clearance', 'Unexpected'):
            self.assertIsNone(lesson.score_pass(.03, .08, outcome)[1])
        self.assertIsNone(lesson.score_pass(.03, None, None)[1])

    def test_summary_separates_excluded_actions_from_zero_scores(self):
        rows = [{'score_status': 'Completed', 'scenario_value': 0},
                {'score_status': 'Completed', 'scenario_value': .05},
                {'score_status': 'Unsuccessful: assumed zero continuation', 'scenario_value': -.03},
                {'score_status': 'Excluded unknown or injury-clearance outcome', 'scenario_value': None}]
        summary = lesson.summarize(rows)
        self.assertEqual(summary['scored_completed'], 2)
        self.assertEqual(summary['excluded_or_unscorable'], 1)
        self.assertAlmostEqual(summary['combined_scenario_sum'], .02)
