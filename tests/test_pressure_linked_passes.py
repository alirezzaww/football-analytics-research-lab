"""Event-ID joins, link coverage, pass outcome uncertainty and duplicate inflation."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('links79', ROOT/'79_pressure_linked_passes.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def sample():
    row = {'match_id': 1, 'event_id': 'pressure', 'team_id': 1, 'player_id': 7,
           'period': 1, 'index': 2, 'timestamp': '00:00:10.000'}
    event = {'id': 'pressure', 'index': 2, 'period': 1, 'timestamp': row['timestamp'],
             'type': {'name': 'Pressure'}, 'team': {'id': 1}, 'player': {'id': 7},
             'related_events': ['pass', 'carry', 'ownpass']}
    target = {'id': 'pass', 'index': 1, 'period': 1, 'timestamp': '00:00:09.000',
              'type': {'name': 'Pass'}, 'team': {'id': 2, 'name': 'Opponent'},
              'player': {'id': 8, 'name': 'Passer'}, 'pass': {}, 'related_events': ['pressure']}
    carry = {**target, 'id': 'carry', 'index': 3, 'type': {'name': 'Carry'}}
    ownpass = {**target, 'id': 'ownpass', 'index': 4, 'team': {'id': 1, 'name': 'Own'}}
    player = {'team_id': 1, 'player_id': 7, 'qualifying_match_ids': [1], 'recorded_pressures': 1}
    return [event, target, carry, ownpass], row, player


class PressureLinkedPassTests(unittest.TestCase):
    def test_join_uses_type_and_actor_not_nearest_time_and_preserves_other_links(self):
        events, row, player = sample()
        original = copy.deepcopy((events, row, player))
        rows, links = lesson.link_match(events, [row])
        self.assertEqual(rows[0]['linked_opponent_pass_ids'], ['pass'])
        self.assertEqual(rows[0]['linked_same_team_pass_ids'], ['ownpass'])
        self.assertEqual(rows[0]['related_event_type_counts'], {'Pass': 2, 'Carry': 1})
        self.assertEqual(links[0]['pass_start_minus_pressure_start_ms'], -1000)
        self.assertTrue(links[0]['reciprocal'])
        self.assertEqual((events, row, player), original)

    def test_two_pressures_linked_to_same_pass_count_once_in_outcomes(self):
        events, row, player = sample()
        second = {**events[0], 'id': 'pressure2', 'index': 5, 'related_events': ['pass']}
        rows, links = lesson.link_match(events+[second], [row, {**row, 'event_id': 'pressure2', 'index': 5}])
        result = lesson.summarize({**player, 'recorded_pressures': 2}, rows, links)
        self.assertEqual(result['opponent_pass_link_count'], 2)
        self.assertEqual(len(result['unique_linked_opponent_passes']), 1)
        self.assertEqual(result['linked_pass_category_counts']['completed'], 1)
        self.assertEqual(result['nonreciprocal_opponent_pass_links'], 1)
        self.assertEqual(result['unique_linked_opponent_passes'][0]['pressure_ids'], ['pressure', 'pressure2'])

    def test_known_failure_unknown_and_empty_denominators(self):
        events, row, player = sample()
        for label, category in (('Incomplete', 'not_completed'), ('Out', 'not_completed'),
                                ('Pass Offside', 'not_completed'), ('Unknown', 'unassessable'),
                                ('Injury Clearance', 'unassessable')):
            events[1]['pass'] = {'outcome': {'name': label}}
            rows, links = lesson.link_match(events, [row])
            result = lesson.summarize(player, rows, links)
            with self.subTest(label=label):
                self.assertEqual(result['linked_pass_category_counts'][category], 1)
                if category == 'unassessable':
                    self.assertIsNone(result['not_completed_share_of_assessable_linked_passes_pct'])
        with self.assertRaises(ValueError): lesson.pass_category({'pass': {'outcome': {'name': 'New Label'}}})

    def test_no_pass_link_is_not_a_failed_pass_observation(self):
        events, row, player = sample()
        events[0]['related_events'] = ['carry']
        rows, links = lesson.link_match(events, [row])
        result = lesson.summarize(player, rows, links)
        self.assertEqual(result['pressures_without_linked_opponent_pass'], 1)
        self.assertEqual(result['linked_pass_category_counts']['not_completed'], 0)
        self.assertIsNone(result['not_completed_share_of_assessable_linked_passes_pct'])

    def test_invalid_references_duplicate_ids_and_period_mismatch_stop_join(self):
        events, row, _ = sample()
        for ids in (['pass', 'pass'], 'pass', None):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                lesson.link_match([{**events[0], 'related_events': ids}]+events[1:], [row])
        with self.assertRaises(KeyError):
            lesson.link_match([{**events[0], 'related_events': ['missing']}]+events[1:], [row])
        with self.assertRaises(ValueError): lesson.link_match(events+[events[1]], [row])
        events[1]['period'] = 2
        with self.assertRaises(ValueError): lesson.link_match(events, [row])

    def test_edge_coverage_and_identity_must_match_pressure_rows(self):
        events, row, player = sample()
        rows, links = lesson.link_match(events, [row])
        with self.assertRaises(ValueError): lesson.summarize(player, rows, [])
        with self.assertRaises(ValueError): lesson.summarize(player, rows, links*2)
        with self.assertRaises(ValueError): lesson.summarize({**player, 'player_id': 99}, rows, links)
