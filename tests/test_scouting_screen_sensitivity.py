"""Scenario-grid validity, fixed pool/data and membership-count interpretation."""
from contextlib import closing
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sensitivity83',ROOT/'83_scouting_screen_sensitivity.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


class ScreenSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=json.loads((ROOT/lesson.SOURCE).read_text())
        cls.source=json.loads((ROOT/cls.baseline['source_path']).read_text())
        cls.grid=json.loads((ROOT/lesson.PROTOCOL).read_text())

    def test_grid_requires_baseline_unique_sorted_finite_cutoffs(self):
        for values in ([29,31],[30,30],[32,30],[30,float('nan')],[True,30],[]):
            with self.subTest(values=values),self.assertRaises(ValueError):
                lesson.validate_grid({**self.grid,'completed_per90_floors':values},self.baseline['parameters'])

    def test_canonical_case_reproduces_and_stricter_floors_cannot_add_profiles(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.screen_module.database.create_database(connection,self.source['rows'])
            cases=lesson.scenario_results(connection,self.baseline,self.grid)
        canonical=next(c for c in cases if c['parameters']==self.baseline['parameters'])
        self.assertEqual({tuple(k) for k in canonical['selected_keys']},{lesson.key(r) for r in self.baseline['selected_rows']})
        for strict in cases:
            for loose in cases:
                if all(strict['parameters'][p]>=loose['parameters'][p] for p in ('min_completed_per90','min_forward_per90')):
                    self.assertLessEqual({tuple(k) for k in strict['selected_keys']},{tuple(k) for k in loose['selected_keys']})

    def test_changed_baseline_values_or_selection_cannot_pass_as_same_experiment(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.screen_module.database.create_database(connection,self.source['rows'])
            changed=copy.deepcopy(self.baseline);changed['eligible_rows'][0]['completed_per90']+=1
            with self.assertRaises(ValueError):lesson.scenario_results(connection,changed,self.grid)
            changed=copy.deepcopy(self.baseline);changed['selected_rows']=[]
            with self.assertRaises(ValueError):lesson.scenario_results(connection,changed,self.grid)

    def test_memberships_keep_zeros_and_reject_invalid_case_counts(self):
        eligible=[{'team_id':1,'player_id':7},{'team_id':1,'player_id':8}]
        cases=[{'selected_keys':[[1,7]],'selected_count':1},{'selected_keys':[],'selected_count':0}]
        profiles=lesson.memberships(eligible,cases,[eligible[0]])
        self.assertEqual([p['selected_case_count'] for p in profiles],[1,0])
        self.assertEqual([p['case_count'] for p in profiles],[2,2])
        with self.assertRaises(ValueError):lesson.memberships(eligible,[{'selected_keys':[[1,7]],'selected_count':2}],[])
        with self.assertRaises(ValueError):lesson.memberships(eligible,[],[])
