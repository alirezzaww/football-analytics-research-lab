"""Guard metadata coverage, fan-out, filtering and bound name values."""
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('takers58', ROOT/'58_sql_corner_taker_report.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def corner(identifier, match=1):
    return dict(match_id=match, corner_id=identifier, match_date='2019-06-07',
                opponent='Example', period=1, minute=10, second=0)


def taker(identifier, name, match=1):
    return dict(match_id=match, corner_id=identifier, passer=name)


class CornerTakerSqlTests(unittest.TestCase):
    def test_multishot_corners_count_once_and_having_does_not_change_rates(self):
        corners = [corner('a'),corner('b'),corner('a',2)]
        takers = [taker('a',"O'Neil"),taker('b',"O'Neil"),taker('a','Other',2)]
        shots = [dict(match_id=1,shot_id=s,corner_id='a',elapsed_seconds=2,goal=0)
                 for s in ('s1','s2')]
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.create_database(con,corners,shots,takers)
            all_rows = lesson.query_report(con)
            filtered = lesson.query_report(con,2)
        self.assertEqual(all_rows[0],dict(passer="O'Neil",deliveries=2,corners_with_shot=1,
                                         phase_shots=2,phase_goals=0,corner_shot_rate_pct=50.0))
        self.assertEqual(all_rows[1]['corners_with_shot'],0)
        self.assertEqual(filtered,[all_rows[0]])

    def test_missing_duplicate_and_extra_metadata_are_rejected(self):
        for rows in ([],[taker('a','A'),taker('a','A')],
                     [taker('a','A'),taker('extra','A')]):
            with self.subTest(rows=rows), closing(sqlite3.connect(':memory:')) as con:
                with self.assertRaises(ValueError):
                    lesson.create_database(con,[corner('a')],[],rows)

    def test_invalid_threshold_is_rejected(self):
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.create_database(con,[],[],[])
            self.assertEqual(lesson.query_report(con),[])
            for value in (-1,1.5,True,'10'):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    lesson.query_report(con,value)
