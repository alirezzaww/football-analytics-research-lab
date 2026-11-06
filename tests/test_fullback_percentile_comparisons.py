"""Explicit percentile convention, changing peer pools and side identities."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('percentiles71',ROOT/'71_fullback_percentile_comparisons.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def peers(values):
    return [{'team_id':1,'player_id':i,'metric':value} for i,value in enumerate(values)]


class PercentileComparisonTests(unittest.TestCase):
    def test_unique_extremes_and_middle(self):
        group=peers([10,20,30])
        self.assertEqual([lesson.percentile_for((1,i),group,'metric')['percentile'] for i in range(3)],[0,50,100])

    def test_ties_get_half_weight_and_all_ties_are_fifty(self):
        result=lesson.percentile_for((1,1),peers([10,20,20,30]),'metric')
        self.assertEqual((result['lower_count'],result['tied_other_count'],result['higher_count']),(1,1,1))
        self.assertEqual(result['percentile'],50)
        self.assertEqual(lesson.percentile_for((1,0),peers([20,20,20]),'metric')['percentile'],50)

    def test_unrounded_values_determine_rank(self):
        self.assertEqual(lesson.percentile_for((1,0),peers([10.001,10.002]),'metric')['percentile'],0)

    def test_singleton_or_missing_target_is_undefined(self):
        self.assertIsNone(lesson.percentile_for((1,0),peers([10]),'metric')['percentile'])
        result=lesson.percentile_for((1,0),peers([None,20,30]),'metric')
        self.assertIsNone(result['percentile']);self.assertEqual(result['valid_pool_size'],2)

    def test_changing_pool_changes_rank_without_changing_target(self):
        before=lesson.percentile_for((1,1),peers([10,20,30]),'metric')
        after=lesson.percentile_for((1,1),peers([10,20,30,40]),'metric')
        self.assertEqual(before['value'],after['value'])
        self.assertEqual(before['percentile'],50)
        self.assertAlmostEqual(after['percentile'],100/3)

    def test_duplicate_missing_identity_and_invalid_metric_rejected(self):
        duplicate=peers([10,20]);duplicate[1]['player_id']=0
        with self.assertRaises(ValueError):lesson.percentile_for((1,0),duplicate,'metric')
        with self.assertRaises(ValueError):lesson.percentile_for((1,99),peers([10,20]),'metric')
        for value in (True,'20',float('nan'),float('inf')):
            with self.subTest(value=value),self.assertRaises(ValueError):lesson.percentile_for((1,0),peers([10,value]),'metric')

    def test_side_filters_preserve_mixed_start_category(self):
        def role(left,right):return {'position_starts':{'Left Back':left,'Right Back':right},'role_starts':left+right}
        self.assertEqual(lesson.side_group(role(3,0)),'left_only')
        self.assertEqual(lesson.side_group(role(0,3)),'right_only')
        self.assertEqual(lesson.side_group(role(2,1)),'mixed')
        with self.assertRaises(ValueError):lesson.side_group(role(0,0))
