"""Guard grouped rates against fan-out and disappearance of zero-shot groups."""
from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('opponent56', ROOT/'56_sql_opponent_comparison.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def corner(match, identifier, opponent):
    return dict(match_id=match, corner_id=identifier, match_date='2019-06-07',
                opponent=opponent, period=1, minute=10, second=0)


class OpponentSqlTests(unittest.TestCase):
    def test_grouping_preserves_zero_shot_opponents_and_complete_corner_keys(self):
        corners = [corner(1,'same','Alpha'),corner(1,'b','Alpha'),corner(2,'same','Beta')]
        shots = [dict(match_id=1,shot_id=s,corner_id='same',elapsed_seconds=2,goal=0)
                 for s in ('s1','s2')]
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.joins.create_database(con,corners,shots)
            result = lesson.query_rates(con)
        self.assertEqual(result[0],dict(opponent='Alpha',deliveries=2,corners_with_shot=1,
                                       phase_shots=2,corner_shot_rate_pct=50.0))
        self.assertEqual(result[1],dict(opponent='Beta',deliveries=1,corners_with_shot=0,
                                       phase_shots=0,corner_shot_rate_pct=0.0))

    def test_empty_database_has_no_opponent_groups(self):
        with closing(sqlite3.connect(':memory:')) as con:
            lesson.joins.create_database(con,[],[])
            self.assertEqual(lesson.query_rates(con),[])
