"""Pressure-event identity, off-ball scope, coordinates and registered exposure."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pressure73',ROOT/'73_fullback_pressure_activity.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def sample():
    events=[{'id':'start','index':1,'period':1,'type':{'name':'Starting XI'}},
            {'id':'end','index':100,'period':2,'type':{'name':'Half End'}}]
    audit={'match_id':1,'periods':[{'period':1,'length_ms':45*60000},{'period':2,'length_ms':45*60000}]}
    intervals=[{'team_id':1,'player_id':7,'start_ms':0,'end_ms':90*60000,
                'start_event_id':'start','end_event_id':'end'}]
    return events,audit,intervals


def pressure(identifier='p',index=10):
    return {'id':identifier,'index':index,'period':1,'timestamp':'00:10:00.000',
            'minute':10,'second':0,'type':{'name':'Pressure'},'team':{'id':1},
            'player':{'id':7},'possession_team':{'id':2},'location':[50,40]}


def player():
    return {'team_id':1,'player_id':7,'qualifying_match_ids':[1],'duration_ms':90*60000}


class PressureActivityTests(unittest.TestCase):
    def test_pressure_against_opponent_possession_counts_but_pass_flag_does_not(self):
        events,audit,intervals=sample();events.append(pressure())
        flag=pressure('flag',11);flag['type']['name']='Pass';flag['under_pressure']=True;events.append(flag)
        original=copy.deepcopy(events)
        rows=lesson.pressure_rows(events,audit,intervals)
        self.assertEqual([r['event_id'] for r in rows],['p'])
        self.assertEqual(events,original)

    def test_missing_or_invalid_locations_remain_counted_and_unmapped(self):
        for location in (None,[121,40],[50,float('nan')],[True,40]):
            events,audit,intervals=sample();event=pressure();event['location']=location;events.append(event)
            rows=lesson.pressure_rows(events,audit,intervals)
            result=lesson.summarize(player(),rows)
            with self.subTest(location=location):
                self.assertEqual(result['recorded_pressures'],1)
                self.assertEqual(result['pressures_per90'],1)
                self.assertEqual(result['unmapped_pressures'],1)
                self.assertIsNone(rows[0]['x'])

    def test_other_player_and_shootout_are_outside_scope(self):
        events,audit,intervals=sample();other=pressure();other['player']['id']=8
        shootout=pressure('shootout',101);shootout['period']=5
        self.assertEqual(lesson.pressure_rows(events+[other,shootout],audit,intervals),[])

    def test_outside_time_or_event_order_is_rejected(self):
        for kind in ('time','order'):
            events,audit,intervals=sample();event=pressure()
            if kind=='time':event['period']=2;event['timestamp']='00:46:00.000'
            else:event['index']=101
            with self.subTest(kind=kind),self.assertRaises(ValueError):lesson.pressure_rows(events+[event],audit,intervals)

    def test_duplicate_event_or_interval_identity_is_rejected(self):
        events,audit,intervals=sample()
        with self.assertRaises(ValueError):lesson.pressure_rows(events+[pressure(),pressure(index=11)],audit,intervals)
        with self.assertRaises(ValueError):lesson.pressure_rows(events,audit,intervals*2)

    def test_per90_and_empty_activity_use_positive_exposure(self):
        events,audit,intervals=sample();rows=lesson.pressure_rows(events+[pressure(),pressure('q',11)],audit,intervals)
        self.assertEqual(lesson.summarize(player(),rows)['pressures_per90'],2)
        self.assertEqual(lesson.summarize(player(),[])['pressures_per90'],0)
        with self.assertRaises(ValueError):lesson.summarize({**player(),'duration_ms':0},[])
        with self.assertRaises(ValueError):lesson.summarize({**player(),'qualifying_match_ids':[2]},rows)
