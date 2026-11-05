"""Elapsed-period clocks, registration changes and matched fixture exposure."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('minutes64',ROOT/'64_fullback_playing_time.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def event(identifier,index,kind,period=1,timestamp='00:00:00.000',team=1,player=100):
    return {'id':identifier,'index':index,'type':{'name':kind},'period':period,'timestamp':timestamp,
            'team':{'id':team,'name':f'Team {team}'},'player':{'id':player,'name':str(player)}}


def match_events(extra=False):
    events=[]
    for team in (1,2):
        row=event(f'xi{team}',team,'Starting XI',team=team)
        row['tactics']={'lineup':[{'player':{'id':team*100+i,'name':str(team*100+i)}} for i in range(11)]}
        events.append(row)
    ends=[(1,'00:47:00.000'),(2,'00:48:00.000')] if not extra else [(p,'00:45:00.000' if p<3 else '00:15:00.000') for p in range(1,5)]
    events.extend(event(f'end{p}',p*100,'Half End',p,clock) for p,clock in ends)
    return events


class FullbackMinutesTests(unittest.TestCase):
    def test_period_clock_and_halftime_substitution(self):
        events=match_events()
        sub=event('sub',150,'Substitution',2,'00:15:00.000')
        sub['substitution']={'replacement':{'id':999,'name':'Replacement'}};events.append(sub)
        result=lesson.reconstruct_match(events,1)
        rows={r['player_id']:r for r in result['intervals']}
        self.assertEqual(result['match_duration_ms'],95*60000)
        self.assertEqual(rows[100]['minutes'],62)  # First-half 47 + second-half 15.
        self.assertEqual(rows[999]['minutes'],33)
        self.assertEqual(rows[101]['minutes'],95)
        self.assertTrue(all(a['registered_player_ms']==a['expected_player_ms'] for a in result['team_audits']))

    def test_extra_time_counts_but_shootout_does_not(self):
        events=match_events(extra=True)
        events.append(event('shootout',500,'Half End',5,'00:10:00.000'))
        result=lesson.reconstruct_match(events,1)
        self.assertEqual(result['match_duration_ms'],120*60000)
        self.assertEqual(len(result['periods']),4)

    def test_duplicate_dismissal_signal_does_not_remove_player_time_twice(self):
        events=match_events()
        for index in (30,31):
            red=event(f'red{index}',index,'Bad Behaviour',timestamp='00:30:00.000')
            red['bad_behaviour']={'card':{'name':'Red Card'}};events.append(red)
        result=lesson.reconstruct_match(events,1)
        audit=result['team_audits'][0]
        self.assertEqual(audit['permanent_absence_ms'],65*60000)
        self.assertEqual([r['changed_active_registration'] for r in audit['departures']],[True,False])

    def test_temporary_absences_retained_and_permanent_departure_closes_interval(self):
        events=match_events()
        events.extend([event('off',20,'Player Off',timestamp='00:20:00.000'),
                       event('on',25,'Player On',timestamp='00:25:00.000')])
        permanent=event('permanent',160,'Player Off',2,'00:20:00.000',player=101)
        permanent['player_off']={'permanent':True};events.append(permanent)
        result=lesson.reconstruct_match(events,1)
        rows={r['player_id']:r for r in result['intervals']}
        self.assertEqual(rows[100]['minutes'],95)
        self.assertEqual(rows[101]['minutes'],67)
        self.assertEqual(len(result['team_audits'][0]['temporary_absence_events_retained']),2)

    def test_missing_or_early_period_end_is_rejected(self):
        events=match_events();events[-1]['half_end']={'early_video_end':True}
        with self.assertRaises(ValueError):lesson.reconstruct_match(events,1)
        events=match_events();events[-1]['type']['name']='Half Start'
        with self.assertRaises(ValueError):lesson.reconstruct_match(events,1)

    def test_invalid_substitution_is_rejected(self):
        events=match_events();sub=event('sub',50,'Substitution',player=999)
        sub['substitution']={'replacement':{'id':888,'name':'Replacement'}};events.append(sub)
        with self.assertRaises(ValueError):lesson.reconstruct_match(events,1)

    def test_selected_minutes_use_only_qualifying_start_fixtures(self):
        events=match_events();original=copy.deepcopy(events)
        matches=[lesson.reconstruct_match(events,match_id) for match_id in (1,2)]
        player={'team_id':1,'player_id':100,'player_name':'Example','team_name':'Team 1',
                'role_starts':1,'qualifying_match_ids':[1]}
        result=lesson.aggregate_players([player],matches)
        self.assertEqual(result[0]['minutes'],95)
        self.assertEqual(events,original)
