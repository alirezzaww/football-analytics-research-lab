"""Phase boundaries, exact time endpoints and multiple shots per delivery."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('corner_phase', ROOT / '36_corner_phase_analysis.py')
lesson = importlib.util.module_from_spec(spec); spec.loader.exec_module(lesson)


class CornerPhaseTests(unittest.TestCase):
    def setUp(self):
        self.protocol = {'maximum_seconds_inclusive': 15, 'restart_pass_types': ['Corner', 'Free Kick', 'Throw-in', 'Goal Kick', 'Kick Off']}
        self.corner = {'index': 1, 'timestamp': '00:46:00.123', 'period': 1, 'possession': 3, 'team': {'id': 1}}
        self.shot = {'id': 's', 'index': 2, 'timestamp': '00:46:15.123', 'period': 1, 'possession': 3,
                     'team': {'id': 1}, 'type': {'name': 'Shot'}, 'shot': {'outcome': {'name': 'Saved'}}}
        self.included = {'s': {'goal': 0, 'model_probability': .1}}

    def test_exact_fifteen_seconds_and_added_time_are_included(self):
        result = lesson.phase_after(self.corner, [self.shot], self.included, self.protocol)
        self.assertEqual(result['shots'][0]['elapsed_seconds'], 15)
        late = copy.deepcopy(self.shot); late['timestamp'] = '00:46:15.124'
        self.assertEqual(lesson.phase_after(self.corner, [late], self.included, self.protocol)['shots'], [])

    def test_restart_possession_and_period_end_the_phase(self):
        for key, value, reason in [('possession', 4, 'Possession changed'), ('period', 2, 'Period changed')]:
            event = copy.deepcopy(self.shot); event[key] = value
            result = lesson.phase_after(self.corner, [event], self.included, self.protocol)
            self.assertEqual(result['shots'], [])
            self.assertEqual(result['stop_reason'], reason)
        restart = copy.deepcopy(self.shot)
        restart.update({'index': 2, 'timestamp': '00:46:05.123', 'type': {'name': 'Pass'}, 'pass': {'type': {'name': 'Corner'}}})
        shot = copy.deepcopy(self.shot); shot['index'] = 3
        self.assertEqual(lesson.phase_after(self.corner, [restart, shot], self.included, self.protocol)['stop_reason'], 'New restart')

    def test_one_delivery_can_have_two_shots_but_a_goal_stops_it(self):
        early = copy.deepcopy(self.shot); early.update(id='a', timestamp='00:46:05.123', index=2)
        later = copy.deepcopy(self.shot); later['index'] = 3
        included = {**self.included, 'a': {'goal': 0, 'model_probability': .2}}
        result = lesson.phase_after(self.corner, [early, later], included, self.protocol)
        self.assertEqual(len(result['shots']), 2)
        early['shot']['outcome']['name'] = 'Goal'; included['a']['goal'] = 1
        result = lesson.phase_after(self.corner, [early, later], included, self.protocol)
        self.assertEqual(len(result['shots']), 1)
        self.assertEqual(result['stop_reason'], 'Goal')

    def test_own_goal_ends_phase(self):
        event = copy.deepcopy(self.shot); event['type']['name'] = 'Own Goal Against'
        self.assertEqual(lesson.phase_after(self.corner, [event], {}, self.protocol)['stop_reason'], 'Own goal')
