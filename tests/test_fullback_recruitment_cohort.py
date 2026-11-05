"""Starting-role selection, stable identities and explicit sample thresholds."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cohort63',ROOT/'63_fullback_recruitment_cohort.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)
POSITIONS=['Left Back','Right Back']


def starter(match,player=1,team=1,name='Example',position='Right Back'):
    return dict(match_id=match,team_id=team,player_id=player,player_name=name,
                team_name=f'Team {team}',position_name=position)


class FullbackCohortTests(unittest.TestCase):
    def test_three_start_boundary_and_mixed_sides_preserved(self):
        rows=[starter(1),starter(2),starter(3,position='Left Back'),
              starter(1,player=2),starter(2,player=2)]
        players=lesson.profile_pool(rows,POSITIONS,3)
        self.assertTrue(players[0]['eligible'])
        self.assertEqual(players[0]['position_starts'],{'Left Back':1,'Right Back':2})
        self.assertFalse(players[1]['eligible'])

    def test_wingbacks_do_not_count_toward_fullback_filter(self):
        rows=[starter(1,position='Right Wing Back'),starter(2,position='Left Wing Back')]
        self.assertEqual(lesson.profile_pool(rows,POSITIONS,1),[])

    def test_names_do_not_replace_player_and_team_ids(self):
        rows=[starter(1,name='Alias A'),starter(2,name='Alias B'),
              starter(1,player=2,name='Alias A'),starter(1,team=2,name='Alias A')]
        players=lesson.profile_pool(rows,POSITIONS,1)
        self.assertEqual(len(players),3)
        self.assertEqual(players[0]['role_starts'],2)
        self.assertEqual(players[0]['observed_player_names'],['Alias A','Alias B'])

    def test_duplicate_start_is_rejected(self):
        with self.assertRaises(ValueError):lesson.profile_pool([starter(1),starter(1)],POSITIONS,1)

    def test_invalid_threshold_is_rejected(self):
        for value in (0,-1,True,1.5):
            with self.subTest(value=value),self.assertRaises(ValueError):lesson.profile_pool([],POSITIONS,value)

    def test_starting_lineups_are_distinct_and_complete(self):
        def xi(team):
            return {'type':{'name':'Starting XI'},'period':1,'id':f'xi{team}',
                    'team':{'id':team,'name':f'Team {team}'},
                    'tactics':{'formation':442,'lineup':[
                        {'player':{'id':team*100+n,'name':str(n)},
                         'position':{'id':2,'name':'Right Back'}} for n in range(11)]}}
        fixture={'match_id':1,'match_date':'2019-06-07'}
        events=[xi(1),xi(2),{'type':{'name':'Tactical Shift'},'period':1}]
        self.assertEqual(len(lesson.starting_rows(events,fixture)),22)
        events[0]['tactics']['lineup'].pop()
        with self.assertRaises(ValueError):lesson.starting_rows(events,fixture)
