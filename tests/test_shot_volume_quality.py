"""Ratio identity and undefined-denominator handling."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('volume_quality', ROOT / '32_shot_volume_quality.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class VolumeQualityTests(unittest.TestCase):
    def test_combined_changes_multiply_instead_of_add(self):
        r = lesson.compare_halves({'shots': 10, 'model_npxg': 2}, {'shots': 5, 'model_npxg': .5})
        self.assertEqual(r['second_over_first_shot_ratio'], .5)
        self.assertEqual(r['second_over_first_mean_quality_ratio'], .5)
        self.assertEqual(r['second_over_first_total_npxg_ratio'], .25)

    def test_no_shots_is_not_zero_mean_quality(self):
        r = lesson.compare_halves({'shots': 0, 'model_npxg': 0}, {'shots': 5, 'model_npxg': 1})
        self.assertIsNone(r['first_half']['model_npxg_per_shot'])
        self.assertIsNone(r['second_over_first_shot_ratio'])
        self.assertIsNone(r['second_over_first_mean_quality_ratio'])
        self.assertIsNone(r['second_over_first_total_npxg_ratio'])
        r = lesson.compare_halves({'shots': 5, 'model_npxg': 1}, {'shots': 0, 'model_npxg': 0})
        self.assertEqual(r['second_over_first_total_npxg_ratio'], 0)
        self.assertIsNone(r['second_over_first_mean_quality_ratio'])

    def test_saved_result_matches_source_ledger(self):
        saved = json.loads((ROOT / 'data/32_volume_quality_evidence.json').read_text())
        self.assertEqual(saved, lesson.build_evidence())
