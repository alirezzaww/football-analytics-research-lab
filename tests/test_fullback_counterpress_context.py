"""Provider flag types, source identity and denominator reconciliation."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('counterpress76', ROOT/'76_fullback_counterpress_context.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def sample():
    row = {'match_id': 1, 'event_id': 'a', 'team_id': 1, 'player_id': 7,
           'index': 5, 'period': 1, 'timestamp': '00:10:00.000',
           'x': None, 'y': None, 'location_valid': False}
    event = {'id': 'a', 'team': {'id': 1}, 'player': {'id': 7},
             'type': {'name': 'Pressure'}, 'index': 5, 'period': 1,
             'timestamp': '00:10:00.000', 'counterpress': True}
    player = {'team_id': 1, 'player_id': 7, 'qualifying_match_ids': [1],
              'duration_ms': 45*60000, 'minutes': 45, 'recorded_pressures': 1}
    return event, row, player


class CounterpressContextTests(unittest.TestCase):
    def test_true_false_null_and_absence_remain_distinct(self):
        for event, expected in (({}, 'missing'), ({'counterpress': True}, 'true'),
                                ({'counterpress': False}, 'false'), ({'counterpress': None}, 'null')):
            with self.subTest(event=event):
                self.assertEqual(lesson.flag_state(event), expected)
        for value in (1, 0, 'true', 'false', [], {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                lesson.flag_state({'counterpress': value})

    def test_unmapped_pressure_stays_counted_and_inputs_unchanged(self):
        event, row, player = sample()
        before = copy.deepcopy((event, row, player))
        rows = lesson.enrich_rows([event], [row])
        result = lesson.summarize(player, rows)
        self.assertEqual(result['flagged_counterpressures'], 1)
        self.assertEqual(result['flagged_share_of_pressures_pct'], 100)
        self.assertEqual(result['flagged_counterpressures_per90'], 2)
        self.assertEqual(result['not_flagged_pressures'], 0)
        self.assertEqual((event, row, player), before)

    def test_nonpressure_wrong_player_or_timing_rejected(self):
        event, row, _ = sample()
        for change in ({'type': {'name': 'Duel'}}, {'player': {'id': 8}},
                       {'period': 2}, {'index': 6}, {'timestamp': '00:11:00.000'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                lesson.enrich_rows([{**event, **change}], [row])

    def test_duplicate_and_missing_source_ids_rejected(self):
        event, row, _ = sample()
        with self.assertRaises(ValueError): lesson.enrich_rows([event, event], [row])
        with self.assertRaises(ValueError): lesson.enrich_rows([event], [row, row])
        with self.assertRaises(KeyError): lesson.enrich_rows([], [row])

    def test_missing_flag_is_not_flagged_not_a_regain_outcome(self):
        event, row, player = sample()
        del event['counterpress']
        result = lesson.summarize(player, lesson.enrich_rows([event], [row]))
        self.assertEqual(result['flagged_counterpressures'], 0)
        self.assertEqual(result['counterpress_flag_states']['missing'], 1)
        self.assertEqual(result['not_flagged_pressures'], 1)
        self.assertEqual(result['flagged_share_of_pressures_pct'], 0)

    def test_zero_actions_undefined_share_and_bad_membership_rejected(self):
        event, row, player = sample()
        result = lesson.summarize({**player, 'recorded_pressures': 0}, [])
        self.assertIsNone(result['flagged_share_of_pressures_pct'])
        self.assertEqual(result['flagged_counterpressures_per90'], 0)
        rows = lesson.enrich_rows([event], [row])
        for change in ({'qualifying_match_ids': [2]}, {'player_id': 8}, {'minutes': 90}, {'recorded_pressures': 2}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                lesson.summarize({**player, **change}, rows)
        with self.assertRaises(ValueError):
            lesson.summarize(player, [{**rows[0], 'counterpress_flagged': False}])
