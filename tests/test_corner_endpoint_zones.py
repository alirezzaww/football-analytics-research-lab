"""Disjoint zone boundaries and missing versus outside locations."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('endpoint_zones', ROOT / '42_corner_endpoint_zones.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CornerEndpointTests(unittest.TestCase):
    def test_nested_boxes_assign_boundary_to_most_specific_zone(self):
        for point in ([114, 30], [120, 50], [117, 40]):
            self.assertEqual(lesson.endpoint_zone(point), 'Six-yard box')
        for point in ([102, 18], [120, 62], [113.999, 40], [115, 29.999]):
            self.assertEqual(lesson.endpoint_zone(point), 'Rest of penalty area')

    def test_unknown_is_not_outside_and_off_pitch_is_retained(self):
        for point in (None, [], [114], [float('nan'), 30]):
            self.assertEqual(lesson.endpoint_zone(point), 'Endpoint unknown')
        for point in ([101.999, 40], [120, 80], [121, 40]):
            self.assertEqual(lesson.endpoint_zone(point), 'Outside penalty area')

    def test_group_keeps_failed_or_unproductive_deliveries_in_denominator(self):
        rows = [{'match_id': 1, 'corner_id': str(i), 'endpoint_zone': 'Six-yard box', 'phase_has_shot': i == 0} for i in range(3)]
        groups = lesson.summarize(rows)
        self.assertEqual(groups[0]['deliveries'], 3)
        self.assertAlmostEqual(groups[0]['phase_shot_rate'], 1 / 3)
        self.assertIsNone(groups[1]['phase_shot_rate'])
