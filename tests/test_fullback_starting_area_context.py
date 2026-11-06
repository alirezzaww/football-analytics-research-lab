"""Disjoint starting areas, exact ceiling and preserved source counts."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('starting67',ROOT/'67_fullback_starting_area_context.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def row(identifier,x,qualifies=False,match=1):
    return dict(match_id=match,pass_id=identifier,team_id=1,player_id=2,x=x,qualifies=qualifies)


def player(total,qualifies=0):
    return dict(team_id=1,player_id=2,eligible_completed=total,qualifying_completions=qualifies)


class StartingAreaTests(unittest.TestCase):
    def test_third_boundaries_are_disjoint_and_include_pitch_edges(self):
        expected={0:'Defensive third',39.9:'Defensive third',40:'Middle third',79.9:'Middle third',
                  80:'Attacking third',100:'Attacking third',120:'Attacking third'}
        for x,label in expected.items():
            with self.subTest(x=x):self.assertEqual(lesson.third(x),label)

    def test_coordinate_room_boundary_includes_exactly_one_hundred(self):
        self.assertTrue(lesson.has_coordinate_room(100,20))
        self.assertFalse(lesson.has_coordinate_room(100.0001,20))
        self.assertTrue(lesson.has_coordinate_room(99.9,20))

    def test_invalid_coordinates_and_thresholds_rejected(self):
        for x in (None,True,float('nan'),-1,121):
            with self.subTest(x=x),self.assertRaises(ValueError):lesson.third(x)
        for threshold in (0,-1,True,float('inf')):
            with self.subTest(threshold=threshold),self.assertRaises(ValueError):lesson.has_coordinate_room(50,threshold)

    def test_partition_counts_and_no_room_subset_preserve_all_completions(self):
        rows=[row('a',20,True),row('b',40,True),row('c',100),row('d',110)]
        result=lesson.group_player(player(4,2),rows,20)
        self.assertEqual([g['completions'] for g in result['starting_thirds']],[1,1,2])
        self.assertEqual([g['qualifying_completions'] for g in result['starting_thirds']],[1,1,0])
        self.assertEqual(result['no_coordinate_room_completions'],1)
        self.assertEqual(result['no_coordinate_room_pct'],25)
        self.assertEqual(sum(g['share_of_player_completions_pct'] for g in result['starting_thirds']),100)

    def test_duplicate_wrong_player_and_impossible_qualification_rejected(self):
        with self.assertRaises(ValueError):lesson.group_player(player(2),[row('same',20),row('same',30)],20)
        wrong=row('a',50);wrong['player_id']=99
        with self.assertRaises(ValueError):lesson.group_player(player(1),[wrong],20)
        with self.assertRaises(ValueError):lesson.group_player(player(1,1),[row('a',110,True)],20)
        # A pass ID reused in another match is a distinct composite identity.
        self.assertEqual(lesson.group_player(player(2),[row('a',20),row('a',20,match=2)],20)['eligible_completed'],2)

    def test_empty_groups_have_undefined_rates(self):
        result=lesson.group_player(player(0),[],20)
        self.assertIsNone(result['no_coordinate_room_pct'])
        self.assertTrue(all(g['within_third_qualifying_share_pct'] is None for g in result['starting_thirds']))
