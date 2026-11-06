"""Opponent identity, attempted failures, matched boundaries and exposure ratios."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('context74', ROOT/'74_fullback_opponent_pass_context.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def sample():
    def event(identifier, index, minute=10, team=2, outcome=None, kind=None):
        detail = {}
        if outcome: detail['outcome'] = {'name': outcome}
        if kind: detail['type'] = {'name': kind}
        return {'id': identifier, 'index': index, 'period': 1,
                'timestamp': f'00:{minute:02d}:00.000', 'type': {'name': 'Pass'},
                'team': {'id': team}, 'player': {'id': 7 if team == 1 else 22},
                'possession_team': {'id': team}, 'pass': detail}
    events = [{'id': 'start', 'index': 1, 'type': {'name': 'Starting XI'}, 'period': 1},
              event('own', 2, team=1), event('complete', 3),
              event('failed', 4, outcome='Incomplete'), event('restart', 5, kind='Goal Kick'),
              event('unknown', 6, outcome='Unknown'),
              {'id': 'sub', 'index': 7, 'type': {'name': 'Substitution'}, 'period': 1},
              event('same_clock_after_sub', 8, minute=20), event('later', 9, minute=30),
              {'id': 'end', 'index': 10, 'type': {'name': 'Half End'}, 'period': 1}]
    target = {'team_id': 1, 'player_id': 7, 'start_ms': 0, 'end_ms': 20*60000,
              'start_event_id': 'start', 'end_event_id': 'sub'}
    opponent = {**target, 'team_id': 2, 'player_id': 22, 'end_ms': 45*60000, 'end_event_id': 'end'}
    audit = {'match_id': 1, 'periods': [{'period': 1, 'length_ms': 45*60000}], 'intervals': [target, opponent]}
    return events, audit, target


def player():
    return {'team_id': 1, 'player_id': 7, 'qualifying_match_ids': [1],
            'duration_ms': 20*60000, 'minutes': 20, 'recorded_pressures': 4}


class OpponentPassContextTests(unittest.TestCase):
    def test_opponent_attempts_include_failure_and_exclude_own_restart_unknown_and_later(self):
        events, audit, target = sample()
        row = lesson.opponent_windows(events, audit, [target])[0]
        self.assertEqual(row['opponent_attempt_ids'], ['complete', 'failed'])
        self.assertEqual(row['opponent_team_id'], 2)
        result = lesson.summarize(player(), [row])
        self.assertEqual(result['pressures_per100_opponent_attempts'], 200)  # Not a probability.

    def test_clock_and_event_order_are_both_required(self):
        events, audit, target = sample()
        events[2]['timestamp'] = '00:21:00.000'  # Early index but outside clock.
        row = lesson.opponent_windows(events, audit, [target])[0]
        self.assertEqual(row['opponent_attempt_ids'], ['failed'])
        self.assertNotIn('same_clock_after_sub', row['opponent_attempt_ids'])

    def test_zero_exposure_is_undefined_and_duplicate_ids_rejected(self):
        events, audit, target = sample()
        row = lesson.opponent_windows(events, audit, [target])[0]
        self.assertIsNone(lesson.summarize(player(), [{**row, 'opponent_attempt_ids': []}])['pressures_per100_opponent_attempts'])
        with self.assertRaises(ValueError):
            lesson.summarize(player(), [{**row, 'opponent_attempt_ids': ['a', 'a']}])

    def test_mismatched_fixture_identity_minutes_or_opponent_rejected(self):
        events, audit, target = sample()
        row = lesson.opponent_windows(events, audit, [target])[0]
        for change in ({'match_id': 2}, {'player_id': 8}, {'end_ms': 10}, {'opponent_team_id': 1}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                lesson.summarize(player(), [{**row, **change}])
        with self.assertRaises(ValueError): lesson.summarize(player(), [row, row])

    def test_pool_counts_before_dividing(self):
        events, audit, target = sample()
        row = lesson.opponent_windows(events, audit, [target])[0]
        second = {**row, 'match_id': 2, 'opponent_attempt_ids': list(range(8))}
        p = {**player(), 'qualifying_match_ids': [1, 2], 'duration_ms': 40*60000, 'minutes': 40}
        self.assertEqual(lesson.summarize(p, [row, second])['pressures_per100_opponent_attempts'], 40)
