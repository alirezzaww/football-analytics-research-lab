"""Boundary, censoring, possession-order and team-credit checks for custom proxy."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('next77', ROOT/'77_fullback_next_possession.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def sample():
    event = {'id': 'p', 'index': 2, 'type': {'name': 'Pressure'}, 'team': {'id': 1},
             'player': {'id': 7}, 'period': 1, 'timestamp': '00:00:10.000',
             'possession': 1, 'possession_team': {'id': 2}}
    row = {'match_id': 1, 'event_id': 'p', 'team_id': 1, 'player_id': 7,
           'period': 1, 'index': 2, 'timestamp': '00:00:10.000'}
    candidate = {'period': 1, 'possession': 2, 'team_id': 1, 'event_id': 'next',
                 'index': 3, 'timestamp': '00:00:15.000', 'time_ms': 15000}
    return event, row, candidate


class NextPossessionTests(unittest.TestCase):
    def test_five_second_boundary_is_inclusive_and_longer_is_negative(self):
        event, row, candidate = sample()
        for delay, expected in ((0, True), (4999, True), (5000, True), (5001, False)):
            with self.subTest(delay=delay):
                result = lesson.classify(row, event, {**candidate, 'time_ms': 10000+delay}, 45000)
                self.assertIs(result['next_own_within5s'], expected)

    def test_short_period_followup_is_unknown_unless_next_possession_is_observed(self):
        event, row, candidate = sample()
        result = lesson.classify(row, event, None, 12000)
        self.assertIsNone(result['next_own_within5s'])
        self.assertEqual(result['outcome_status'], 'period_end_before_full_window')
        result = lesson.classify(row, event, {**candidate, 'time_ms': 11000}, 12000)
        self.assertIs(result['next_own_within5s'], True)
        self.assertIs(lesson.classify(row, event, None, 15000)['next_own_within5s'], False)

    def test_already_own_or_backwards_start_time_is_unassessable(self):
        event, row, candidate = sample()
        self.assertIsNone(lesson.classify(row, {**event, 'possession_team': {'id': 1}}, candidate, 45000)['next_own_within5s'])
        self.assertIsNone(lesson.classify(row, event, {**candidate, 'time_ms': 9999}, 45000)['next_own_within5s'])

    def test_period_crossing_wrong_identity_and_order_are_rejected(self):
        event, row, candidate = sample()
        for change in ({'period': 2}, {'index': 1}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                lesson.classify(row, event, {**candidate, **change}, 45000)
        with self.assertRaises(ValueError):
            lesson.classify({**row, 'player_id': 8}, event, candidate, 45000)

    def test_first_following_possession_is_not_skipped_to_find_own_team(self):
        event, row, _ = sample()
        def start(identifier, index, timestamp, possession, team):
            return {'id': identifier, 'index': index, 'period': 1, 'timestamp': timestamp,
                    'possession': possession, 'possession_team': {'id': team}}
        events = [start('start', 1, '00:00:00.000', 1, 2), event,
                  start('other', 3, '00:00:11.000', 2, 2),
                  start('own', 4, '00:00:12.000', 3, 1)]
        audit = {'match_id': 1, 'periods': [{'period': 1, 'length_ms': 45000}]}
        result = lesson.match_outcomes(events, [row], audit)[0]
        self.assertIs(result['next_own_within5s'], False)
        self.assertEqual(result['next_possession']['event_id'], 'other')
        with self.assertRaises(ValueError): lesson.possession_starts(events+[events[0]])
        events[3]['possession'] = 1
        with self.assertRaises(ValueError): lesson.possession_starts(events)

    def test_unclear_rows_excluded_from_share_but_not_pressure_count(self):
        event, row, candidate = sample()
        positive = lesson.classify(row, event, candidate, 45000)
        unclear = {**lesson.classify(row, event, None, 12000), 'event_id': 'q'}
        player = {'team_id': 1, 'player_id': 7, 'qualifying_match_ids': [1],
                  'minutes': 90, 'recorded_pressures': 2}
        result = lesson.summarize(player, [positive, unclear])
        self.assertEqual(result['recorded_pressures'], 2)
        self.assertEqual(result['assessable_pressures'], 1)
        self.assertEqual(result['unassessable_pressures'], 1)
        self.assertEqual(result['next_own_within5s_share_pct'], 100)
        self.assertIsNone(lesson.summarize({**player, 'recorded_pressures': 1}, [unclear])['next_own_within5s_share_pct'])
        with self.assertRaises(ValueError): lesson.summarize(player, [positive, positive])
