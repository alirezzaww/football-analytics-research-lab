"""Observed overlap requires positive exposure to both specified techniques."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('taker_overlap', ROOT / '40_corner_taker_overlap.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class TakerOverlapTests(unittest.TestCase):
    def test_both_types_require_observed_deliveries(self):
        self.assertTrue(lesson.has_both_types([{'category': 'Inswinging', 'deliveries': 1}, {'category': 'Outswinging', 'deliveries': 2}]))
        self.assertFalse(lesson.has_both_types([{'category': 'Inswinging', 'deliveries': 1}, {'category': 'Outswinging', 'deliveries': 0}]))
        self.assertFalse(lesson.has_both_types([{'category': 'Other / unrecorded', 'deliveries': 20}]))

    def test_saved_audit_reproduces_without_raw_cache(self):
        saved = json.loads((ROOT / 'data/40_corner_taker_overlap_evidence.json').read_text())
        self.assertEqual(saved, lesson.build_evidence())
