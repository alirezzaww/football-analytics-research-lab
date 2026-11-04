"""Protect period boundaries, parent counts and empty-group meaning."""
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('phase57', ROOT/'57_sql_match_phase_comparison.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def corner(identifier, period, minute):
    return dict(match_id=1, corner_id=identifier, match_date='2019-06-07',
                opponent='Example', period=period, minute=minute, second=0)


class MatchPhaseSqlTests(unittest.TestCase):
    def test_added_time_uses_period_and_multishot_corner_counts_once(self):
        corners = [corner('a',1,46),corner('b',1,10),corner('c',2,47)]
        shots = [dict(match_id=1,shot_id=s,corner_id='a',elapsed_seconds=2,goal=0)
                 for s in ('s1','s2')]
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.joins.create_database(con,corners,shots)
            rows = lesson.query_rates(con)
        self.assertEqual(rows[0],dict(match_phase='First half',phase_order=1,deliveries=2,
                                     corners_with_shot=1,phase_shots=2,corner_shot_rate_pct=50.0))
        self.assertEqual(rows[1],dict(match_phase='Second half',phase_order=2,deliveries=1,
                                     corners_with_shot=0,phase_shots=0,corner_shot_rate_pct=0.0))
        self.assertEqual(len(rows),2)  # No extra-time exposure: do not invent a 0% group.

    def test_both_extra_time_periods_share_one_group(self):
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.joins.create_database(con,[corner('a',3,100),corner('b',4,116)],[])
            rows = lesson.query_rates(con)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['match_phase'],'Extra time')
        self.assertEqual(rows[0]['deliveries'],2)

    def test_empty_sample_returns_no_groups(self):
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.joins.create_database(con,[],[])
            self.assertEqual(lesson.query_rates(con),[])
