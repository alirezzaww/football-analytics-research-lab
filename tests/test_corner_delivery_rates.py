"""Denominator must retain deliveries without shots; absent exposure is undefined."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('corner_rates', ROOT / '35_corner_delivery_rates.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class CornerRateTests(unittest.TestCase):
    def test_unlinked_deliveries_stay_in_denominator(self):
        rows = [{'id': 'a', 'link_status': 'Verified reciprocal link', 'linked_shot_goal': True},
                {'id': 'b', 'link_status': 'Verified reciprocal link', 'linked_shot_goal': False},
                {'id': 'c', 'link_status': 'No assisted-shot link recorded', 'linked_shot_goal': None}]
        result = lesson.summarize(rows)
        self.assertEqual(result['deliveries'], 3)
        self.assertAlmostEqual(result['recorded_direct_shot_link_rate'], 2 / 3)
        self.assertAlmostEqual(result['recorded_direct_goal_link_rate'], 1 / 3)
        self.assertEqual(result['delivery_ids'], ['a', 'b', 'c'])

    def test_no_deliveries_differs_from_observed_zero_links(self):
        self.assertIsNone(lesson.summarize([])['recorded_direct_shot_link_rate'])
        result = lesson.summarize([{'id': 'a', 'link_status': 'No assisted-shot link recorded', 'linked_shot_goal': None}])
        self.assertEqual(result['recorded_direct_shot_link_rate'], 0)
        self.assertEqual(result['recorded_direct_goal_link_rate'], 0)
