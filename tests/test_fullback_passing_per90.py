"""Pass eligibility and matched registered-time rates."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('passing65',ROOT/'65_fullback_passing_per90.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def sample():
    events=[{'id':'start','index':1,'type':{'name':'Starting XI'},'period':1},
            {'id':'end','index':1000,'type':{'name':'Half End'},'period':2}]
    audit={'match_id':1,'periods':[{'period':1,'length_ms':45*60000},{'period':2,'length_ms':45*60000}]}
    interval={'team_id':1,'player_id':7,'start_ms':0,'end_ms':90*60000,
              'start_event_id':'start','end_event_id':'end'}
    return events,audit,[interval]


def pass_event(identifier,index=10,outcome=None,pass_type=None,possessor=1):
    detail={}
    if outcome is not None:detail['outcome']={'name':outcome}
    if pass_type is not None:detail['type']={'name':pass_type}
    return {'id':identifier,'index':index,'type':{'name':'Pass'},'period':1,
            'timestamp':'00:10:00.000','team':{'id':1},'player':{'id':7},
            'possession_team':{'id':possessor},'pass':detail}


class FullbackPassingTests(unittest.TestCase):
    def test_known_outcomes_and_exclusions_reconcile(self):
        events,audit,intervals=sample()
        events += [pass_event('complete'),pass_event('incomplete',11,'Incomplete'),
                   pass_event('out',12,'Out'),pass_event('offside',13,'Pass Offside'),
                   pass_event('unknown',14,'Unknown'),pass_event('injury',15,'Injury Clearance'),
                   pass_event('corner',16,pass_type='Corner'),pass_event('loose',17,possessor=2)]
        original=copy.deepcopy(events)
        row=lesson.count_match(events,audit,intervals)[0]
        self.assertEqual(row['candidate_passes'],8)
        self.assertEqual(row['attempt_ids'],['complete','incomplete','out','offside'])
        self.assertEqual(row['completed_ids'],['complete'])
        self.assertEqual(row['excluded'],{'restart':1,'not_possession_team':1,'unknown_or_injury':2})
        self.assertEqual(events,original)

    def test_other_player_and_shootout_passes_are_outside_scope(self):
        events,audit,intervals=sample()
        other=pass_event('other');other['player']['id']=8
        shootout=pass_event('shootout',1001);shootout['period']=5
        events += [other,shootout]
        row=lesson.count_match(events,audit,intervals)[0]
        self.assertEqual(row['candidate_passes'],0)

    def test_outside_time_or_event_order_is_rejected(self):
        for case in ('time','order'):
            events,audit,intervals=sample();event=pass_event('bad')
            if case=='time':event['period']=2;event['timestamp']='00:46:00.000'
            else:event['index']=1001
            events.append(event)
            with self.subTest(case=case),self.assertRaises(ValueError):lesson.count_match(events,audit,intervals)

    def test_unrecognized_outcome_and_duplicate_ids_are_rejected(self):
        events,audit,intervals=sample();events.append(pass_event('bad',outcome='Unexpected'))
        with self.assertRaises(ValueError):lesson.count_match(events,audit,intervals)
        events,audit,intervals=sample();events += [pass_event('same'),pass_event('same',11)]
        with self.assertRaises(ValueError):lesson.count_match(events,audit,intervals)

    def test_per90_uses_minutes_and_percentage_uses_attempts(self):
        player={'team_id':1,'player_id':7,'player_name':'Example','team_name':'Team',
                'role_starts':3,'qualifying_match_ids':[1,2,3],'duration_ms':200*60000}
        rows=[{'attempt_ids':list(range(10)),'completed_ids':list(range(8))}]
        result=lesson.player_summary(player,rows)
        self.assertEqual(result['attempts_per90'],4.5)
        self.assertEqual(result['completed_per90'],3.6)
        self.assertEqual(result['completion_pct'],80)

    def test_zero_attempts_have_undefined_percentage_and_zero_exposure_is_rejected(self):
        player={'team_id':1,'player_id':7,'player_name':'Example','team_name':'Team',
                'role_starts':3,'qualifying_match_ids':[1,2,3],'duration_ms':200*60000}
        self.assertIsNone(lesson.player_summary(player,[])['completion_pct'])
        player['duration_ms']=0
        with self.assertRaises(ValueError):lesson.player_summary(player,[])
