"""Same-window team denominators, substitution boundaries and pooled shares."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('share70',ROOT/'70_fullback_team_passing_share.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def pass_event(identifier,index,minute,player,team=1,kind=None):
    detail={} if kind is None else {'type':{'name':kind}}
    return {'id':identifier,'index':index,'period':1,'timestamp':f'00:{minute:02d}:00.000',
            'type':{'name':'Pass'},'team':{'id':team},'player':{'id':player},
            'possession_team':{'id':team},'pass':detail}


def sample():
    events=[{'id':'start','index':1,'period':1,'type':{'name':'Starting XI'}},
            {'id':'otherstart','index':2,'period':1,'type':{'name':'Starting XI'}},
            pass_event('own',3,10,7),pass_event('keeper',4,15,9),
            pass_event('opponent',5,18,22,team=2),
            {'id':'sub','index':6,'period':1,'type':{'name':'Substitution'}},
            pass_event('same_clock_after_sub',7,20,9),pass_event('replacement',8,25,8),
            pass_event('restart',9,30,9,kind='Goal Kick'),
            {'id':'end','index':100,'period':2,'type':{'name':'Half End'}}]
    def interval(player,begin=0,start='start',end=90,end_id='end',team=1):
        return {'team_id':team,'player_id':player,'start_ms':begin*60000,'end_ms':end*60000,
                'start_event_id':start,'end_event_id':end_id}
    intervals=[interval(7,end=20,end_id='sub'),interval(9),interval(8,20,'sub'),
               interval(22,start='otherstart',team=2)]
    audit={'match_id':1,'periods':[{'period':1,'length_ms':45*60000},{'period':2,'length_ms':45*60000}],
           'intervals':intervals}
    return events,audit


class TeamPassingShareTests(unittest.TestCase):
    def test_target_window_excludes_other_team_and_passes_after_substitution(self):
        events,audit=sample()
        row=lesson.count_windows(events,audit,[audit['intervals'][0]])[0]
        self.assertEqual(row['player_completed_ids'],['own'])
        self.assertEqual(row['team_completed_ids'],['own','keeper'])
        self.assertNotIn('same_clock_after_sub',row['team_completed_ids'])

    def test_team_total_includes_goalkeeper_and_target_player(self):
        events,audit=sample()
        row=lesson.count_windows(events,audit,[audit['intervals'][1]])[0]
        self.assertEqual(row['player_completed_ids'],['keeper','same_clock_after_sub'])
        self.assertEqual(row['team_completed_ids'],['own','keeper','same_clock_after_sub','replacement'])
        self.assertNotIn('restart',row['team_completed_ids'])

    def test_inconsistent_target_window_cannot_lose_own_passes_silently(self):
        events,audit=sample();target={**audit['intervals'][0],'end_ms':5*60000}
        with self.assertRaises(ValueError):lesson.count_windows(events,audit,[target])

    def test_pool_counts_instead_of_averaging_match_percentages(self):
        player={'eligible_completed':14,'duration_ms':120*60000,'qualifying_match_ids':[1,2]}
        windows=[{'match_id':1,'player_completed_ids':list(range(5)),'team_completed_ids':list(range(10))},
                 {'match_id':2,'player_completed_ids':list(range(9)),'team_completed_ids':list(range(90))}]
        result=lesson.summarize(player,windows)
        self.assertEqual(result['share_of_team_completions_pct'],14)
        self.assertEqual(result['team_completions_per_player90'],75)
        self.assertNotEqual(result['share_of_team_completions_pct'],30)  # Mean of 50% and 10%.

    def test_zero_team_exposure_is_undefined(self):
        player={'eligible_completed':0,'duration_ms':90*60000,'qualifying_match_ids':[1]}
        result=lesson.summarize(player,[{'match_id':1,'player_completed_ids':[],'team_completed_ids':[]}])
        self.assertIsNone(result['share_of_team_completions_pct'])

    def test_different_fixtures_or_numerator_count_are_rejected(self):
        player={'eligible_completed':1,'duration_ms':90*60000,'qualifying_match_ids':[1]}
        with self.assertRaises(ValueError):lesson.summarize(player,[{'match_id':2,'player_completed_ids':['p'],'team_completed_ids':['p']}])
        with self.assertRaises(ValueError):lesson.summarize(player,[{'match_id':1,'player_completed_ids':[],'team_completed_ids':['p']}])
