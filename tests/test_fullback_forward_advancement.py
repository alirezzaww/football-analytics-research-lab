"""Threshold precision, direction and complete source coverage."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('advance66',ROOT/'66_fullback_forward_advancement.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def inputs():
    ledger={'match_id':1,'team_id':2,'player_id':3,'completed_ids':['p']}
    event={'id':'p','type':{'name':'Pass'},'team':{'id':2},'player':{'id':3},'period':1,
           'possession_team':{'id':2},'location':[84.6,20],
           'pass':{'end_location':[104.6,30]}}
    return ledger,[event]


def player(completions=3):
    return dict(team_id=2,player_id=3,player_name='Example',team_name='Team',
                qualifying_match_ids=[1],duration_ms=200*60000,eligible_completed=completions)


class ForwardAdvancementTests(unittest.TestCase):
    def test_exact_decimal_boundary_is_inclusive(self):
        self.assertEqual(lesson.advancement([84.6,20],[104.6,30],20),(20.0,True))
        self.assertFalse(lesson.advancement([84.6,20],[104.599,30],20)[1])

    def test_sideways_backward_and_short_near_goal_do_not_qualify(self):
        for start,end in (([20,0],[20,80]),([70,40],[40,40]),([110,40],[119,40])):
            with self.subTest(start=start,end=end):self.assertFalse(lesson.advancement(start,end,20)[1])

    def test_missing_nonfinite_and_outside_coordinates_are_not_zero(self):
        for point in (None,[float('nan'),20],[121,20],[50,81],[True,20]):
            with self.subTest(point=point),self.assertRaises(ValueError):lesson.advancement(point,[100,40],20)
        ledger,events=inputs();del events[0]['pass']['end_location']
        with self.assertRaises(KeyError):lesson.enrich_completions(ledger,events,20)

    def test_enrichment_preserves_pass_and_does_not_modify_source(self):
        ledger,events=inputs();original=copy.deepcopy((ledger,events))
        row=lesson.enrich_completions(ledger,events,20)[0]
        self.assertEqual(row['pass_id'],'p');self.assertEqual(row['x_gain'],20)
        self.assertTrue(row['qualifies']);self.assertEqual((ledger,events),original)

    def test_failed_or_duplicate_selected_pass_rejected(self):
        ledger,events=inputs();events[0]['pass']['outcome']={'name':'Incomplete'}
        with self.assertRaises(ValueError):lesson.enrich_completions(ledger,events,20)
        ledger,events=inputs();ledger['completed_ids']*=2
        with self.assertRaises(ValueError):lesson.enrich_completions(ledger,events,20)

    def test_share_and_per90_use_different_denominators(self):
        result=lesson.summarize(player(),[{'qualifies':True},{'qualifies':False},{'qualifies':False}])
        self.assertEqual(result['qualifying_completions'],1)
        self.assertEqual(result['qualifying_per90'],.45)
        self.assertAlmostEqual(result['qualifying_share_pct'],100/3)
        with self.assertRaises(ValueError):lesson.summarize(player(),[])

    def test_zero_completions_have_undefined_share(self):
        result=lesson.summarize(player(0),[])
        self.assertEqual(result['qualifying_per90'],0)
        self.assertIsNone(result['qualifying_share_pct'])
