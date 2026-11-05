"""The defensive view must switch teams without changing phase definitions."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('defense60', ROOT/'60_france_defensive_corners.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)
PROTOCOL = {'maximum_seconds_inclusive':15, 'periods_included':[1,2,3,4],
            'restart_pass_types':['Corner','Free Kick','Throw-in','Goal Kick','Kick Off']}


def event(identifier, index, seconds, team='Opponent', period=1, kind='Shot', goal=False):
    row = dict(id=identifier,index=index,timestamp=f'00:00:{seconds:06.3f}',period=period,
               minute=0,second=int(seconds),possession=1,
               team={'id':2 if team=='Opponent' else 1,'name':team},type={'name':kind})
    if kind=='Pass':
        row['pass']={'type':{'name':'Corner'}}
    if kind=='Shot':
        row['shot']={'type':{'name':'Open Play'},'outcome':{'name':'Goal' if goal else 'Saved'}}
    return row


class DefensiveCornerTests(unittest.TestCase):
    def test_only_attacking_team_corners_and_shots_count(self):
        rows = [event('c',1,0,kind='Pass'),event('f',2,2,team='France'),event('s',3,3),
                event('fc',4,4,team='France',kind='Pass')]
        original = copy.deepcopy(rows)
        result = lesson.analyze_team(rows,'Opponent',PROTOCOL)
        self.assertEqual(result['deliveries'],1)
        self.assertEqual(result['phase_shots'],1)
        self.assertEqual(result['phases'][0]['shots'][0]['shot_id'],'s')
        self.assertEqual(rows,original)

    def test_goal_is_counted_and_stops_later_shots(self):
        rows = [event('c',1,0,kind='Pass'),event('g',2,2,goal=True),event('s',3,3)]
        result = lesson.analyze_team(rows,'Opponent',PROTOCOL)
        self.assertEqual(result['corners_with_phase_shot'],1)
        self.assertEqual(result['phase_shots'],1)
        self.assertEqual(result['phase_shot_goals'],1)
        self.assertEqual(result['phases'][0]['stop_reason'],'Goal')

    def test_extra_time_is_included_but_shootouts_and_penalties_are_not(self):
        for period,expected in ((3,1),(4,1),(5,0)):
            with self.subTest(period=period):
                rows=[event('c',1,0,period=period,kind='Pass'),event('s',2,2,period=period)]
                result=lesson.analyze_team(rows,'Opponent',PROTOCOL)
                self.assertEqual(result['deliveries'],expected)
                self.assertEqual(result['phase_shots'],expected)
                self.assertEqual(result['extra_time_deliveries'],expected)
        rows=[event('c',1,0,kind='Pass'),event('p',2,2)]
        rows[1]['shot']['type']['name']='Penalty'
        self.assertEqual(lesson.analyze_team(rows,'Opponent',PROTOCOL)['phase_shots'],0)

    def test_no_deliveries_has_undefined_rate(self):
        result=lesson.analyze_team([event('s',1,2)],'Opponent',PROTOCOL)
        self.assertEqual(result['deliveries'],0)
        self.assertIsNone(result['phase_shot_rate'])

    def test_duplicate_event_id_or_index_is_rejected(self):
        for field in ('id','index'):
            rows=[event('c',1,0,kind='Pass'),event('s',2,2)]
            rows[1][field]=rows[0][field]
            with self.subTest(field=field),self.assertRaises(ValueError):
                lesson.analyze_team(rows,'Opponent',PROTOCOL)
