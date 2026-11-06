"""Stable player identities and honest, traceable review-event extraction."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('brief69',ROOT/'69_fullback_recruitment_brief.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def example():
    candidate=dict(match_id=1,team_id=2,player_id=3,pass_id='p',x=106.9,y=2.3,end_x=114.8,end_y=6,x_gain=7.9)
    event={'id':'p','type':{'name':'Pass'},'team':{'id':2},'player':{'id':3,'name':'Example'},
           'period':2,'minute':94,'second':48,'timestamp':'00:49:48.000',
           'location':[106.9,2.3],'pass':{'end_location':[114.8,6]}}
    return candidate,event


class RecruitmentBriefTests(unittest.TestCase):
    def test_lookup_uses_full_identity_instead_of_name(self):
        rows=[{'team_id':1,'player_id':3,'name':'Same'}, {'team_id':2,'player_id':3,'name':'Same'}]
        self.assertEqual(lesson.find_player(rows,2,3),rows[1])

    def test_duplicate_or_missing_profile_is_rejected(self):
        rows=[{'team_id':2,'player_id':3}]*2
        with self.assertRaises(ValueError):lesson.find_player(rows,2,3)
        with self.assertRaises(ValueError):lesson.find_player([],2,3)

    def test_review_clock_is_preserved_and_observations_remain_unknown(self):
        candidate,event=example();original=copy.deepcopy((candidate,event))
        result=lesson.review_event(candidate,event,{2:'Team',4:'Opponent'},'2019-06-17','Additional example')
        self.assertEqual(result['period_timestamp'],'00:49:48.000')
        self.assertEqual((result['period'],result['minute'],result['second']),(2,94,48))
        self.assertEqual(result['opponent'],'Opponent')
        self.assertIsNone(result['recipient'])
        self.assertIsNone(result['video_observation'])
        self.assertEqual(result['review_status'],'Not reviewed')
        self.assertEqual((candidate,event),original)

    def test_changed_coordinates_or_failed_pass_cannot_be_reviewed_as_saved_completion(self):
        candidate,event=example();event['location']=[100,2.3]
        with self.assertRaises(ValueError):lesson.review_event(candidate,event,{2:'Team',4:'Other'},'2019-06-17','Example')
        candidate,event=example();event['pass']['outcome']={'name':'Incomplete'}
        with self.assertRaises(ValueError):lesson.review_event(candidate,event,{2:'Team',4:'Other'},'2019-06-17','Example')
