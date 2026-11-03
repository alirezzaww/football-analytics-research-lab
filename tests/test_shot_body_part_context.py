"""Keep unknown contacts separate and distinguish empty from zero-goal groups."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('body_part_context', ROOT / '33_shot_body_part_context.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class BodyPartContextTests(unittest.TestCase):
    def test_only_explicit_foot_contacts_are_foot_shots(self):
        for value in ('Left Foot', 'Right Foot'):
            self.assertEqual(lesson.category(value), 'Foot')
        self.assertEqual(lesson.category('Head'), 'Head')
        for value in (None, 'Other', 'Chest', 'Unknown'):
            self.assertEqual(lesson.category(value), 'Other / unknown')

    def test_missing_group_is_not_evidence_of_zero_conversion(self):
        rows = [{'id': 'a', 'body_part': 'Left Foot', 'goal': 0, 'model_probability': .2},
                {'id': 'b', 'body_part': None, 'goal': 0, 'model_probability': .1}]
        foot, head, other = lesson.summarize(rows)
        self.assertEqual(foot['share_of_half_shots'], .5)
        self.assertEqual(foot['shot_goals'], 0)
        self.assertEqual(head['shots'], 0)
        self.assertIsNone(head['mean_model_npxg'])
        self.assertEqual(other['shot_ids'], ['b'])
        self.assertEqual(sum(g['shots'] for g in (foot, head, other)), len(rows))
