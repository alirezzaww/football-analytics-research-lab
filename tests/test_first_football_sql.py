"""Database grain, parameter binding, integrity constraints and empty exposure."""
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('first_football_sql',ROOT/'54_first_football_sql.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def row(identifier,shots=0,goals=0):
    return {'match_id':1,'corner_id':identifier,'match_date':'2019-06-07',
            'opponent':"O'Example Women's",'period':1,'minute':10,'second':0,
            'phase_shots':shots,'phase_goals':goals,'has_phase_shot':int(shots>0)}


class FootballSQLTests(unittest.TestCase):
    def test_counts_corners_once_even_with_multiple_shots_and_apostrophes(self):
        rows=[row('a',2,1),row('b'),row('c')]
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.create_database(con,rows)
            result=lesson.query_results(con)
            overall=result['overall'][0]
            self.assertEqual(overall['deliveries'],3)
            self.assertEqual(overall['corners_with_shot'],1)
            self.assertEqual(overall['phase_shots'],2)
            self.assertAlmostEqual(overall['corner_shot_rate_pct'],100/3)
            self.assertEqual(result['by_opponent'][0]['opponent'],"O'Example Women's")

    def test_duplicate_delivery_identity_is_rejected(self):
        with closing(sqlite3.connect(':memory:')) as con:
            with self.assertRaises(sqlite3.IntegrityError):
                lesson.create_database(con,[row('a'),row('a')])

    def test_inconsistent_shot_indicator_is_rejected(self):
        bad=row('a',1);bad['has_phase_shot']=0
        with closing(sqlite3.connect(':memory:')) as con:
            with self.assertRaises(sqlite3.IntegrityError):
                lesson.create_database(con,[bad])

    def test_empty_table_has_undefined_rate_and_zero_counts(self):
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.create_database(con,[])
            overall=lesson.query_results(con)['overall'][0]
            self.assertEqual(overall['deliveries'],0)
            self.assertEqual(overall['corners_with_shot'],0)
            self.assertIsNone(overall['corner_shot_rate_pct'])
