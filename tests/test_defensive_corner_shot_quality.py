"""Provider values, preserved identities and correct rate denominators."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('quality61',ROOT/'61_defensive_corner_shot_quality.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def inputs():
    match={'fixture':{'match_id':1},'attacking_team':'Opponent','opponent':'Opponent',
           'phase_shots':1,'phases':[{'corner_id':'c','period':1,
           'shots':[{'shot_id':'s','goal':0,'elapsed_seconds':2}]}]}
    events=[{'id':'c','type':{'name':'Pass'},'team':{'name':'Opponent'},'period':1,
             'pass':{'type':{'name':'Corner'}}},
            {'id':'s','type':{'name':'Shot'},'team':{'name':'Opponent'},'period':1,
             'minute':10,'second':2,'location':[110,40],
             'shot':{'type':{'name':'Open Play'},'statsbomb_xg':.2,
                     'outcome':{'name':'Saved'},'body_part':{'name':'Head'}}}]
    return match,events


class DefensiveQualityTests(unittest.TestCase):
    def test_supplied_xg_retained_without_mutating_sources(self):
        match,events=inputs();original=copy.deepcopy((match,events))
        rows=lesson.enrich_match(match,events)
        self.assertEqual(rows[0]['provider_xg'],.2)
        self.assertEqual(rows[0]['shot_id'],'s')
        self.assertEqual((match,events),original)

    def test_missing_xg_is_not_silently_zero(self):
        match,events=inputs();del events[1]['shot']['statsbomb_xg']
        with self.assertRaises(KeyError):lesson.enrich_match(match,events)

    def test_invalid_probabilities_rejected_but_zero_is_valid(self):
        for value in (None,True,'0.2',float('nan'),float('inf'),-.1,1.1):
            with self.subTest(value=value),self.assertRaises(ValueError):lesson.probability(value)
        self.assertEqual(lesson.probability(0),0)
        self.assertEqual(lesson.probability(1),1)

    def test_wrong_team_or_duplicate_selected_shot_rejected(self):
        match,events=inputs();events[1]['team']['name']='France'
        with self.assertRaises(ValueError):lesson.enrich_match(match,events)
        match,events=inputs();match['phases'][0]['shots']*=2;match['phase_shots']=2
        with self.assertRaises(ValueError):lesson.enrich_match(match,events)

    def test_multishot_corner_counts_once_but_all_xg_is_summed(self):
        shots=[{'match_id':1,'corner_id':'a','provider_xg':.2,'goal':0},
               {'match_id':1,'corner_id':'a','provider_xg':.3,'goal':0}]
        result=lesson.summarize(shots,2)
        self.assertEqual(result['corners_with_shot'],1)
        self.assertEqual(result['corner_shot_rate'],.5)
        self.assertEqual(result['shots_per_corner'],1)
        self.assertEqual(result['provider_xg'],.5)
        self.assertEqual(result['provider_xg_per_shot'],.25)
        self.assertEqual(result['provider_xg_per_corner'],.25)

    def test_no_shots_is_zero_selected_xg_but_undefined_shot_average(self):
        result=lesson.summarize([],3)
        self.assertEqual(result['provider_xg'],0)
        self.assertEqual(result['provider_xg_per_corner'],0)
        self.assertIsNone(result['provider_xg_per_shot'])
        self.assertIsNone(lesson.summarize([],0)['provider_xg_per_corner'])
