"""Near-goal boundaries, fixed-rule retention and same-exposure comparisons."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('adaptive68',ROOT/'68_adaptive_forward_advancement.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def row(start,end,fixed=False):
    return dict(match_id=1,team_id=2,player_id=3,pass_id='p',x=start,y=40,end_x=end,end_y=40,qualifies=fixed)


class AdaptiveAdvancementTests(unittest.TestCase):
    def test_far_from_goal_uses_fixed_twenty(self):
        self.assertEqual(lesson.compare_pass(row(40,60,True))['required_x_gain'],20)
        self.assertFalse(lesson.compare_pass(row(40,59))['alternative_qualifies'])
        self.assertEqual(lesson.compare_pass(row(80,100,True))['required_x_gain'],20)

    def test_near_goal_half_distance_boundary_is_inclusive(self):
        result=lesson.compare_pass(row(110,115))
        self.assertEqual(result['required_x_gain'],5)
        self.assertTrue(result['alternative_qualifies']);self.assertTrue(result['newly_included'])
        self.assertFalse(lesson.compare_pass(row(110,114.999))['alternative_qualifies'])
        self.assertTrue(lesson.compare_pass(row(106.9,113.45))['alternative_qualifies'])
        self.assertFalse(lesson.compare_pass(row(106.9,113.449))['alternative_qualifies'])

    def test_no_backward_sideways_or_goal_line_zero_gain_qualifies(self):
        for start,end in ((110,109),(110,110),(120,120),(119,118)):
            with self.subTest(start=start,end=end):self.assertFalse(lesson.compare_pass(row(start,end))['alternative_qualifies'])

    def test_fixed_positives_are_retained_and_new_cases_start_beyond_eighty(self):
        for start in range(0,121,5):
            for end in range(start,121,5):
                result=lesson.compare_pass(row(start,end,end-start>=20))
                if result['fixed_qualifies']:self.assertTrue(result['alternative_qualifies'])
                if result['newly_included']:self.assertGreater(start,80)

    def test_parameters_and_inconsistent_original_label_rejected(self):
        for base,fraction in ((0,.5),(True,.5),(20,0),(20,1.1),(20,True),(20,float('nan'))):
            with self.subTest(base=base,fraction=fraction),self.assertRaises(ValueError):
                lesson.compare_pass(row(110,115),base,fraction)
        with self.assertRaises(ValueError):lesson.compare_pass(row(40,60,False))

    def test_summary_preserves_minutes_and_reconciles_additions(self):
        player={'eligible_completed':2,'qualifying_completions':1,'duration_ms':200*60000}
        rows=[lesson.compare_pass(row(40,60,True)),lesson.compare_pass(row(110,115))]
        result=lesson.summarize(player,rows)
        self.assertEqual(result['alternative_completions'],2)
        self.assertEqual(result['newly_included_completions'],1)
        self.assertEqual(result['alternative_per90'],.9)
        self.assertEqual(result['alternative_share_pct'],100)
        self.assertEqual(result['duration_ms'],player['duration_ms'])
        with self.assertRaises(ValueError):lesson.summarize(player,[])

    def test_zero_completion_share_is_undefined(self):
        result=lesson.summarize({'eligible_completed':0,'qualifying_completions':0,'duration_ms':60000},[])
        self.assertEqual(result['alternative_per90'],0)
        self.assertIsNone(result['alternative_share_pct'])
