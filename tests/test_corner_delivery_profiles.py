"""Unknown delivery technique must not become an inferred straight corner."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('corner_profiles', ROOT / '39_corner_delivery_profiles.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class DeliveryProfileTests(unittest.TestCase):
    def test_missing_and_unexpected_techniques_remain_separate(self):
        for label in ('Inswinging', 'Outswinging', 'Straight'):
            self.assertEqual(lesson.category(label), label)
        for label in (None, '', 'Through Ball'):
            self.assertEqual(lesson.category(label), 'Other / unrecorded')

    def test_category_denominator_keeps_deliveries_without_shots(self):
        rows = [{'match_id': 1, 'corner_id': str(i), 'category': 'Inswinging',
                 'phase_has_shot': i == 0, 'phase_shots': 2 if i == 0 else 0,
                 'phase_shot_goals': 0} for i in range(3)]
        groups = lesson.summarize(rows)
        self.assertEqual(groups[0]['deliveries'], 3)
        self.assertAlmostEqual(groups[0]['phase_shot_rate'], 1 / 3)
        self.assertEqual(groups[0]['phase_shots'], 2)
        self.assertIsNone(groups[1]['phase_shot_rate'])
        self.assertEqual(sum(r['deliveries'] for r in groups), 3)
