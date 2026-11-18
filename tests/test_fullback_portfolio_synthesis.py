"""A synthesis must not mix identities, cohorts or exposure windows."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('synthesis80', ROOT/'80_fullback_portfolio_synthesis.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class PortfolioSynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {k: json.loads((ROOT/p).read_text()) for k,p in lesson.SOURCES.items()}

    def test_duplicate_identity_cannot_silently_overwrite_source_profile(self):
        row = {'team_id': 1, 'player_id': 7}
        with self.assertRaises(ValueError): lesson.indexed([row, row.copy()])

    def test_source_cohort_mismatch_is_rejected(self):
        changed = {**self.data, 'areas': {**self.data['areas'], 'players': self.data['areas']['players'][:-1]}}
        with self.assertRaises(ValueError): lesson.compile_profiles(changed)

    def test_equal_minutes_with_different_fixture_scope_is_rejected(self):
        changed = copy.deepcopy(self.data)
        changed['proxy']['players'][0]['qualifying_match_ids'] = [999999]
        with self.assertRaises(ValueError): lesson.compile_profiles(changed)
        changed = copy.deepcopy(self.data)
        changed['proxy']['players'][0]['duration_ms'] += 1
        with self.assertRaises(ValueError): lesson.compile_profiles(changed)

    def test_changed_pressure_numerator_is_rejected_even_when_exposure_matches(self):
        changed = copy.deepcopy(self.data)
        target = next(p for p in changed['counterpress']['players'] if p['player_id'] == 10178)
        target['recorded_pressures'] += 1
        with self.assertRaises(ValueError): lesson.compile_profiles(changed)
