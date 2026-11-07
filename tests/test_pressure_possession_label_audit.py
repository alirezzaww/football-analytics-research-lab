"""Actor/sequence identity, context scope and unchanged unknown-case membership."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit78', ROOT/'78_pressure_possession_label_audit.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def sample():
    def event(identifier, index, second, actor, possession=1, owner=1, period=1, kind='Pass'):
        return {'id': identifier, 'index': index, 'period': period, 'timestamp': f'00:00:{second:02d}.000',
                'type': {'name': kind}, 'team': {'id': actor, 'name': f'Team {actor}'},
                'player': {'id': 7}, 'possession': possession,
                'possession_team': {'id': owner, 'name': f'Team {owner}'}}
    events = [event('start', 1, 0, 1), event('opponent_pass', 2, 1, 2),
              event('pressure', 3, 2, 1, kind='Pressure'),
              event('other_sequence', 4, 3, 2, possession=2, owner=2, kind='Carry'),
              event('next_period', 5, 0, 2, possession=3, owner=2, period=2)]
    row = {'match_id': 1, 'event_id': 'pressure', 'team_id': 1, 'player_id': 7,
           'period': 1, 'index': 3, 'timestamp': '00:00:02.000',
           'pressure_possession_id': 1, 'pressure_possession_team_id': 1,
           'outcome_status': 'already_own_possession'}
    return events, row


class PossessionLabelAuditTests(unittest.TestCase):
    def test_opponent_actor_in_own_sequence_is_retained_without_relabelling(self):
        events, row = sample()
        original = copy.deepcopy((events, row))
        result = lesson.audit_match(events, [row])[0]
        self.assertEqual(result['opponent_pass_or_carry_ids_in_labelled_sequence'], ['opponent_pass'])
        action = next(e for e in result['nearby_events'] if e['event_id'] == 'opponent_pass')
        self.assertEqual(action['team_id'], 2)
        self.assertEqual(action['possession_team_id'], 1)
        self.assertEqual(result['timing_relation'], 'pressure_after_start')
        self.assertEqual(result['pressure_minus_start_ms'], 2000)
        self.assertEqual((events, row), original)

    def test_context_does_not_cross_period_and_groups_do_not_merge_by_owner(self):
        events, row = sample()
        result = lesson.audit_match(events, [row])[0]
        self.assertNotIn('next_period', [e['event_id'] for e in result['nearby_events']])
        self.assertNotIn('other_sequence', result['opponent_pass_or_carry_ids_in_labelled_sequence'])
        events[3]['possession_team'] = {'id': 1, 'name': 'Team 1'}
        self.assertEqual(lesson.audit_match(events, [row])[0]['opponent_pass_or_carry_ids_in_labelled_sequence'], ['opponent_pass'])

    def test_timing_comparison_reports_reversal_without_inventing_correction(self):
        events, row = sample()
        events[0]['timestamp'] = '00:00:03.000'
        result = lesson.audit_match(events, [row])[0]
        self.assertEqual(result['timing_relation'], 'pressure_before_start')
        self.assertEqual(result['pressure_minus_start_ms'], -1000)

    def test_wrong_source_membership_and_duplicate_coverage_rejected(self):
        events, row = sample()
        for change in ({'outcome_status': 'next_own_within_window'}, {'player_id': 8}, {'pressure_possession_id': 9}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                lesson.audit_match(events, [{**row, **change}])
        result = lesson.audit_match(events, [row])
        player = {'team_id': 1, 'player_id': 7, 'qualifying_match_ids': [1],
                  'outcome_status_counts': {'already_own_possession': 1}}
        summary = lesson.summarize(player, result)
        self.assertEqual(summary['own_labelled_with_opponent_pass_or_carry_in_sequence'], 1)
        with self.assertRaises(ValueError): lesson.summarize(player, result*2)
        with self.assertRaises(ValueError): lesson.summarize({**player, 'qualifying_match_ids': [2]}, result)
