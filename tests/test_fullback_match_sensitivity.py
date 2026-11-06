"""Remove matched exposures, preserve peers and avoid false uncertainty claims."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sensitivity72',ROOT/'72_fullback_match_sensitivity.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def sample():
    player={'team_id':1,'player_id':2,'duration_ms':120*60000,'eligible_completed':30,
            'team_completed_while_registered':300,'qualifying_match_ids':[1,2,3]}
    windows=[{'match_id':i,'team_id':1,'player_id':2,'start_ms':0,'end_ms':minutes*60000,
              'player_completed_ids':list(range(own)),'team_completed_ids':list(range(team))}
             for i,minutes,own,team in ((1,20,5,50),(2,40,5,100),(3,60,20,150))]
    return player,windows


class MatchSensitivityTests(unittest.TestCase):
    def test_remove_own_team_and_time_together_using_pooled_counts(self):
        player,windows=sample();original=copy.deepcopy((player,windows))
        lesson.validate_windows(player,windows)
        result=lesson.leave_out(player,windows[0])
        self.assertEqual(result['remaining_completed'],25)
        self.assertEqual(result['remaining_team_completed'],250)
        self.assertEqual(result['remaining_minutes'],100)
        self.assertEqual(result['completed_per90'],22.5)
        self.assertEqual(result['share_of_team_completions_pct'],10)
        self.assertNotEqual(result['completed_per90'],(5/40*90+20/60*90)/2)
        self.assertEqual((player,windows),original)

    def test_unknown_window_and_nonpositive_remaining_exposure_rejected(self):
        player,windows=sample()
        with self.assertRaises(ValueError):lesson.leave_out(player,{**windows[0],'match_id':99})
        with self.assertRaises(ValueError):lesson.leave_out({**player,'duration_ms':20*60000},windows[0])

    def test_duplicate_or_changed_baseline_windows_rejected(self):
        player,windows=sample()
        with self.assertRaises(ValueError):lesson.validate_windows(player,windows+[windows[0]])
        with self.assertRaises(ValueError):lesson.validate_windows({**player,'eligible_completed':31},windows)
        with self.assertRaises(ValueError):lesson.validate_windows({**player,'duration_ms':121*60000},windows)

    def test_only_target_metric_changes_in_fixed_peer_comparison(self):
        peers=[{'team_id':1,'player_id':i,'completed_per90':value,'share_of_team_completions_pct':value}
               for i,value in enumerate((10,20,30))]
        original=copy.deepcopy(peers)
        result=lesson.rank_variant(peers[1],{'completed_per90':35,'share_of_team_completions_pct':35},peers)
        self.assertEqual(result['completed_per90']['percentile'],100)
        self.assertEqual(result['completed_per90']['other_players'],2)
        self.assertEqual(peers,original)

    def test_original_three_start_membership_is_not_reselected(self):
        player,windows=sample();result=lesson.leave_out(player,windows[0])
        self.assertEqual(result['remaining_qualifying_starts'],2)
        self.assertEqual(result['remaining_match_ids'],[2,3])
        self.assertEqual(player['qualifying_match_ids'],[1,2,3])

    def test_observed_range_preserves_undefined_cases(self):
        self.assertEqual(lesson.observed_range([1,None,3]),{'minimum':1,'maximum':3,'defined_cases':2})
        result=lesson.observed_range([None,None])
        self.assertIsNone(result['minimum']);self.assertEqual(result['defined_cases'],0)
        self.assertEqual(lesson.range_text(result),'undefined')
