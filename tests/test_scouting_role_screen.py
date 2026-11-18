"""Inclusive AND boundaries, exclusion coverage, precision and protocol validity."""
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('screen82',ROOT/'82_scouting_role_screen.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def protocol():
    return {'competition_id':72,'season_id':30,'season':'2019','side_group':'right_only',
            'min_starts':3,'min_completed_per90':30.0,'min_forward_per90':3.0}


def row(pid,completed,forward,side='right_only',duration=5400000):
    return {'competition_id':72,'season_id':30,'team_id':1,'player_id':pid,'team_name':'Team',
            'player_name':str(pid),'side_group':side,'role_starts':3,'duration_ms':duration,
            'completed_passes':completed,'attempted_passes':completed,'team_completed_passes':completed,
            'forward_passes':forward,'recorded_pressures':0,'qualifying_match_ids':[1,2,3]}


class ScoutingRoleScreenTests(unittest.TestCase):
    def test_inclusive_and_filter_and_role_scope(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.database.create_database(connection,[row(1,30,3),row(2,29,3),row(3,30,2),row(4,29,2),row(5,100,10,'left_only')])
            rows=lesson.screen(connection,protocol())
        flags={r['player_id']:(r['meets_passing_floor'],r['meets_forward_floor'],r['meets_both']) for r in rows}
        self.assertEqual(flags,{1:(1,1,1),2:(0,1,0),3:(1,0,0),4:(0,0,0)})
        counts=lesson.summarize(rows)
        self.assertEqual(counts['meet_both'],1)
        self.assertEqual([counts[k] for k in ('passing_only','forward_only','neither')],[1,1,1])

    def test_display_rounding_cannot_promote_a_below_threshold_profile(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.database.create_database(connection,[row(1,31,3,duration=5400001)])
            result=lesson.screen(connection,protocol())[0]
        self.assertEqual(f"{result['forward_per90']:.2f}",'3.00')
        self.assertEqual(result['meets_passing_floor'],1)
        self.assertEqual(result['meets_forward_floor'],0)
        self.assertEqual(result['meets_both'],0)

    def test_invalid_thresholds_filters_and_cohort_expansion_are_rejected(self):
        for change in ({'min_completed_per90':float('nan')},{'min_forward_per90':-1},
                       {'min_forward_per90':True},{'min_starts':2},{'side_group':'arbitrary'},
                       {'season':'2020'}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                lesson.parameters({**protocol(),**change})

    def test_empty_output_duplicate_rows_and_inconsistent_flags(self):
        self.assertEqual(lesson.summarize([])['eligible'],0)
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.database.create_database(connection,[row(1,30,3)])
            rows=lesson.screen(connection,protocol())
        with self.assertRaises(ValueError):lesson.summarize(rows*2)
        with self.assertRaises(ValueError):lesson.summarize([{**rows[0],'meets_both':0}])
