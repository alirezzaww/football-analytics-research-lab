"""SQL grain, foreign keys, ranks/ties, parameter scope and derived denominators."""
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('scouting81', ROOT/'81_scouting_database.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def profile(pid, completed=10, side='left_only', starts=3, team=1):
    return {'competition_id':72,'season_id':30,'team_id':team,'player_id':pid,
            'team_name':"Team's name",'player_name':"O'Brien",'side_group':side,
            'role_starts':starts,'duration_ms':90*60000,'completed_passes':completed,
            'attempted_passes':completed,'team_completed_passes':completed,
            'forward_passes':0,'recorded_pressures':5,'qualifying_match_ids':list(range(starts))}


class ScoutingDatabaseTests(unittest.TestCase):
    def test_dense_rank_preserves_ties_and_separates_role_pools(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.create_database(connection,[profile(1),profile(2),profile(3,8),profile(4,100,'right_only')])
            rows=lesson.query_players(connection)
            ranks={r['player_id']:(r['passing_activity_rank'],r['eligible_peers']) for r in rows}
            self.assertEqual(ranks,{1:(1,3),2:(1,3),3:(2,3),4:(1,1)})

    def test_minimum_filter_applies_before_rank_and_can_return_empty(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.create_database(connection,[profile(1,20),profile(2,8,starts=4)])
            rows=lesson.query_players(connection,'left_only',4)
            self.assertEqual([(r['player_id'],r['passing_activity_rank'],r['eligible_peers']) for r in rows],[(2,1,1)])
            self.assertEqual(lesson.query_players(connection,'left_only',5),[])

    def test_compound_key_preserves_same_player_id_in_different_team(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.create_database(connection,[profile(1),profile(1,team=2)])
            self.assertEqual(len(lesson.query_players(connection)),2)
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute('INSERT INTO qualifying_fixtures VALUES (72,30,999,999,1)')
        with closing(sqlite3.connect(':memory:')) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                lesson.create_database(connection,[profile(1),profile(1)])

    def test_zero_pass_exposure_is_null_percentage_not_zero_accuracy(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.create_database(connection,[profile(1,0)])
            row=lesson.query_players(connection)[0]
            self.assertEqual(row['completed_per90'],0)
            self.assertEqual(row['pressures_per90'],5)
            self.assertIsNone(row['completion_pct'])
            self.assertIsNone(row['team_passing_share_pct'])

    def test_invalid_filters_cannot_be_interpolated_as_sql(self):
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.create_database(connection,[profile(1)])
            for side,minimum in (("left_only'; DROP TABLE fullbacks;--",3),(None,True),(None,2)):
                with self.subTest(side=side,minimum=minimum),self.assertRaises(ValueError):
                    lesson.query_players(connection,side,minimum)
            self.assertEqual(len(lesson.query_players(connection)),1)

    def test_source_identity_fixture_and_count_mismatches_rejected(self):
        data={k:json.loads((ROOT/p).read_text()) for k,p in lesson.SOURCES.items()}
        import copy
        for mode in ('duplicate','fixture','completed'):
            changed=copy.deepcopy(data)
            if mode=='duplicate':changed['pressure']['players'].append(changed['pressure']['players'][0].copy())
            elif mode=='fixture':changed['forward']['players'][0]['qualifying_match_ids']=[999]
            else:changed['forward']['players'][0]['eligible_completed']+=1
            with self.subTest(mode=mode),self.assertRaises(ValueError):lesson.profile_rows(changed)
