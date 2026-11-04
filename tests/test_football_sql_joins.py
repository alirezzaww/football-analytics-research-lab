"""One-to-many fan-out, parent preservation and relational identity."""
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('football_sql_joins',ROOT/'55_football_sql_joins.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def corner(identifier,match_id=1):
    return {'match_id':match_id,'corner_id':identifier,'match_date':'2019-06-07','opponent':'Example',
            'period':1,'minute':10,'second':0}


def shot(identifier,parent='a',match_id=1):
    return {'match_id':match_id,'shot_id':identifier,'corner_id':parent,'elapsed_seconds':2.5,'goal':0}


class FootballJoinTests(unittest.TestCase):
    def test_multiple_shots_expand_rows_but_summary_preserves_corner_denominator(self):
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.create_database(con,[corner('a'),corner('b'),corner('c')],[shot('s1'),shot('s2')])
            q=lesson.query_results(con)
            self.assertEqual(q['diagnostic'][0]['joined_rows'],4)
            self.assertEqual(q['diagnostic'][0]['linked_shot_rows'],2)
            self.assertEqual(q['summary'][0]['deliveries'],3)
            self.assertEqual(q['summary'][0]['corners_with_shot'],1)
            self.assertAlmostEqual(q['summary'][0]['corner_shot_rate_pct'],100/3)

    def test_match_id_is_part_of_the_join_identity(self):
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.create_database(con,[corner('same',1),corner('same',2)],[shot('s1','same',1)])
            q=lesson.query_results(con)
            self.assertEqual(q['diagnostic'][0]['joined_rows'],2)
            self.assertEqual(q['summary'][0]['corners_with_shot'],1)

    def test_orphan_shot_is_rejected_by_foreign_key(self):
        with closing(sqlite3.connect(':memory:')) as con:
            with self.assertRaises(sqlite3.IntegrityError):
                lesson.create_database(con,[corner('a')],[shot('s1','missing')])

    def test_duplicate_shot_cannot_be_assigned_twice(self):
        with closing(sqlite3.connect(':memory:')) as con:
            with self.assertRaises(sqlite3.IntegrityError):
                lesson.create_database(con,[corner('a')],[shot('s1'),shot('s1')])
