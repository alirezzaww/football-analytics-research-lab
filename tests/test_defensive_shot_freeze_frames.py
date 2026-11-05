"""Closed goal-triangle geometry and frame metadata interpretation."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('frames62',ROOT/'62_defensive_shot_freeze_frames.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def frame_inputs():
    selected={'shot_id':'s','opponent':'Opponent','x':110,'y':40,'period':1,'provider_xg':.2}
    players=[{'location':[115,40],'teammate':False,'player':{'id':1,'name':'Defender'},'position':{'id':3}},
             {'location':[119,40],'teammate':False,'player':{'id':2,'name':'Keeper'},'position':{'id':1}},
             {'location':[116,40],'teammate':True,'player':{'id':3,'name':'Attacker'},'position':{'id':22}}]
    event={'id':'s','type':{'name':'Shot'},'team':{'name':'Opponent'},'location':[110,40],
           'period':1,'shot':{'statsbomb_xg':.2,'freeze_frame':players}}
    return selected,event


class ShotFrameTests(unittest.TestCase):
    def test_closed_triangle_boundaries_and_points_outside(self):
        for point in ([110,40],[110,38],[120,36],[120,44],[100,40]):
            with self.subTest(point=point):self.assertTrue(lesson.in_goal_triangle(point,[100,40]))
        for point in ([99,40],[110,43],[100,41]):
            with self.subTest(point=point):self.assertFalse(lesson.in_goal_triangle(point,[100,40]))
        self.assertTrue(lesson.in_goal_triangle([115,45],[110,50]))
        self.assertFalse(lesson.in_goal_triangle([115,40],[110,50]))

    def test_invalid_points_and_degenerate_triangle_rejected(self):
        for point in ([float('nan'),40],[121,40],[100,81],[True,40]):
            with self.subTest(point=point),self.assertRaises(ValueError):lesson.in_goal_triangle(point,[100,40])
        with self.assertRaises(ValueError):lesson.in_goal_triangle([120,40],[120,40])

    def test_teammate_is_shooting_team_and_keeper_is_counted_separately(self):
        selected,event=frame_inputs();original=copy.deepcopy((selected,event))
        row=lesson.enrich_frame(selected,event)
        self.assertEqual(row['recorded_players'],3)
        self.assertEqual(row['recorded_defending_outfield'],1)
        self.assertEqual(row['defending_outfield_in_triangle'],1)
        self.assertEqual(row['recorded_defending_keepers'],1)
        self.assertEqual(row['defending_keepers_in_triangle'],1)
        self.assertEqual((selected,event),original)

    def test_missing_or_empty_frame_has_undefined_counts(self):
        for value in (None,[]):
            selected,event=frame_inputs();event['shot']['freeze_frame']=value
            row=lesson.enrich_frame(selected,event)
            self.assertFalse(row['frame_available'])
            self.assertIsNone(row['defending_outfield_in_triangle'])
            self.assertIsNone(row['recorded_defending_outfield'])

    def test_duplicate_player_or_nonboolean_team_label_rejected(self):
        selected,event=frame_inputs();event['shot']['freeze_frame'].append(event['shot']['freeze_frame'][0].copy())
        with self.assertRaises(ValueError):lesson.enrich_frame(selected,event)
        selected,event=frame_inputs();event['shot']['freeze_frame'][0]['teammate']=0
        with self.assertRaises(ValueError):lesson.enrich_frame(selected,event)

    def test_changed_shot_identity_rejected(self):
        selected,event=frame_inputs();event['location']=[111,40]
        with self.assertRaises(ValueError):lesson.enrich_frame(selected,event)
