"""Player-match grain, pooled rates, ledger integrity and parent membership."""
from contextlib import closing
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('drill84',ROOT/'84_scouting_match_drilldown.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def sample():
    parent={'competition_id':72,'season_id':30,'team_id':1,'player_id':7,'team_name':'Team',
            'player_name':'Player','side_group':'right_only','role_starts':3,'duration_ms':180*60000,
            'completed_passes':30,'attempted_passes':30,'team_completed_passes':30,
            'forward_passes':9,'recorded_pressures':0,'qualifying_match_ids':[1,2,3]}
    matches=[{'competition_id':72,'season_id':30,'team_id':1,'player_id':7,'match_id':i,
              'match_date':f'2019-06-0{i}','opponent':'Opponent','duration_ms':minutes*60000,
              'completed_passes':10,'forward_passes':3,'recorded_pressures':0}
             for i,minutes in ((1,90),(2,45),(3,45))]
    return parent,matches


class ScoutingMatchDrilldownTests(unittest.TestCase):
    def test_pooled_rate_uses_total_time_not_mean_of_match_rates(self):
        parent,matches=sample()
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.database.create_database(connection,[parent]);lesson.create_match_table(connection,matches)
            totals=lesson.query_totals(connection);lesson.reconcile([parent],totals)
            self.assertEqual(totals[0]['forward_per90'],4.5)
            self.assertEqual(totals[0]['unweighted_mean_match_forward_per90'],5)
            self.assertEqual(len(lesson.query_matches(connection,1,7)),3)
            self.assertEqual(lesson.query_matches(connection,1,8),[])

    def test_fixture_membership_and_duplicate_match_grain_are_enforced(self):
        parent,matches=sample()
        for bad in ([*matches,matches[0]], [{**matches[0],'match_id':999}]):
            with self.subTest(bad=bad),closing(sqlite3.connect(':memory:')) as connection:
                lesson.database.create_database(connection,[parent])
                with self.assertRaises(sqlite3.IntegrityError):lesson.create_match_table(connection,bad)

    def test_aggregate_mismatch_or_missing_player_cannot_pass_reconciliation(self):
        parent,matches=sample()
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.database.create_database(connection,[parent]);lesson.create_match_table(connection,matches)
            totals=lesson.query_totals(connection)
        with self.assertRaises(ValueError):lesson.reconcile([parent],[{**totals[0],'forward_passes':10}])
        with self.assertRaises(ValueError):lesson.reconcile([parent],[])
        with self.assertRaises(ValueError):lesson.reconcile([parent],totals*2)

    def test_source_windows_and_completion_ledgers_require_exact_coverage(self):
        data={k:json.loads((ROOT/p).read_text()) for k,p in lesson.SOURCES.items()}
        for mode in ('duplicate_window','missing_completion','changed_time'):
            changed=copy.deepcopy(data)
            if mode=='duplicate_window':changed['passing']['windows'].append(changed['passing']['windows'][0].copy())
            elif mode=='missing_completion':changed['forward']['completions'].pop()
            else:changed['pressure']['windows'][0]['end_ms']+=1
            with self.subTest(mode=mode),self.assertRaises(ValueError):lesson.assemble_rows(changed)
