"""Coordinate-side assignment and overlap without assuming missing labels."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('corner_side', ROOT / '41_corner_side_context.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CornerSideTests(unittest.TestCase):
    def test_valid_touchlines_and_ambiguous_or_invalid_locations(self):
        self.assertEqual(lesson.corner_side([120, 0]), lesson.SIDES[0])
        self.assertEqual(lesson.corner_side([120, 80]), lesson.SIDES[1])
        for location in (None, [], [120], [120, 40], [120, -1], [120, 81], [float('nan'), 0]):
            with self.subTest(location=location):
                self.assertEqual(lesson.corner_side(location), lesson.SIDES[2])

    def test_unknown_technique_does_not_supply_both_type_overlap(self):
        self.assertFalse(lesson.both_types([{'category': 'Other / unrecorded'}]))
        self.assertTrue(lesson.both_types([{'category': 'Inswinging'}, {'category': 'Outswinging'}]))

    def test_saved_result_reproduces_when_raw_caches_are_present(self):
        # The main evidence checker reconciles this ledger cache-free as well.
        study = json.loads((ROOT / 'data/38_france_corner_study_evidence.json').read_text())
        if not all((ROOT / r['raw_input']['relative_path']).exists() for r in study['matches']):
            self.skipTest('Optional raw caches absent; do not download in unit tests')
        saved = json.loads((ROOT / 'data/41_corner_side_evidence.json').read_text())
        self.assertEqual(saved, lesson.build_evidence())
