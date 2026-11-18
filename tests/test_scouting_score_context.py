"""Own-goal accounting, clock splitting, event-order ties and zero exposure."""
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('score85',ROOT/'85_scouting_score_context.py')
lesson=importlib.util.module_from_spec(spec);spec.loader.exec_module(lesson)


def fixture():return {'home_team':{'home_team_id':1},'away_team':{'away_team_id':2},'home_score':1,'away_score':1}


def goals():
    return [{'index':10,'elapsed_ms':30000,'score_after':[1,0]},
            {'index':20,'elapsed_ms':60000,'score_after':[1,1]}]


class ScoutingScoreContextTests(unittest.TestCase):
    def test_own_goal_counted_once_and_shootout_ignored(self):
        events=[{'id':'g','index':10,'period':1,'timestamp':'00:00:30.000','type':{'name':'Shot'},'team':{'id':1},'shot':{'outcome':{'name':'Goal'}}},
                {'id':'og','index':20,'period':1,'timestamp':'00:01:00.000','type':{'name':'Own Goal Against'},'team':{'id':1}},
                {'id':'pair','index':21,'period':1,'timestamp':'00:01:00.000','type':{'name':'Own Goal For'},'team':{'id':2}},
                {'id':'pen','index':30,'period':5,'timestamp':'00:00:10.000','type':{'name':'Shot'},'team':{'id':1},'shot':{'outcome':{'name':'Goal'}}}]
        audit={'periods':[{'period':1,'length_ms':90000}]}
        home,away,timeline,final=lesson.goal_timeline(events,audit,fixture())
        self.assertEqual((home,away,final),(1,2,[1,1]))
        self.assertEqual([g['credited_team_id'] for g in timeline],[1,2])
        self.assertEqual([g['elapsed_ms'] for g in timeline],[30000,60000])
        with self.assertRaises(ValueError):lesson.goal_timeline(events,audit,{**fixture(),'home_score':2})
        with self.assertRaises(ValueError):lesson.goal_timeline(events+[events[0]],audit,fixture())
        changed=[{**events[0],'timestamp':'00:01:10.000'},*events[1:]]
        with self.assertRaises(ValueError):lesson.goal_timeline(changed,audit,fixture())

    def test_registered_time_is_clipped_and_team_perspective_reversed(self):
        self.assertEqual(lesson.state_durations(goals(),0,90000,1,1,2),{'Leading':30000,'Drawing':60000,'Trailing':0})
        self.assertEqual(lesson.state_durations(goals(),0,90000,2,1,2),{'Leading':0,'Drawing':60000,'Trailing':30000})
        self.assertEqual(lesson.state_durations(goals(),20000,50000,1,1,2),{'Leading':20000,'Drawing':10000,'Trailing':0})
        self.assertEqual(lesson.state_durations([],0,90000,1,1,2),{'Leading':0,'Drawing':90000,'Trailing':0})
        with self.assertRaises(ValueError):lesson.state_durations(goals(),0,0,1,1,2)

    def test_action_uses_pre_event_score_not_post_goal_score(self):
        self.assertEqual(lesson.event_state(goals(),10,1,1,2),'Drawing')
        self.assertEqual(lesson.event_state(goals(),11,1,1,2),'Leading')
        self.assertEqual(lesson.event_state(goals(),20,1,1,2),'Leading')
        self.assertEqual(lesson.event_state(goals(),21,1,1,2),'Drawing')

    def test_same_timestamp_actions_are_split_by_index_without_losing_counts(self):
        events=[{'id':'start','index':1}, {'id':'end','index':99}]
        for identifier,index in (('before',9),('after',11)):
            events.append({'id':identifier,'index':index,'period':1,'timestamp':'00:00:30.000',
                           'type':{'name':'Pass'},'team':{'id':1},'player':{'id':7}})
        interval={'start_ms':0,'end_ms':90000,'start_event_id':'start','end_event_id':'end'}
        row={'competition_id':72,'season_id':30,'team_id':1,'player_id':7,'match_id':1,'duration_ms':90000,
             'completed_pass_ids':['before','after'],'forward_pass_ids':['after'],'pressure_ids':[],
             'completed_passes':2,'forward_passes':1,'recorded_pressures':0}
        rows=lesson.split_match_row(row,interval,events,goals()[:1],1,2,[{'period':1,'length_ms':90000}])
        lookup={r['score_state']:r for r in rows}
        self.assertEqual(lookup['Drawing']['completed_pass_ids'],['before'])
        self.assertEqual(lookup['Leading']['forward_pass_ids'],['after'])
        self.assertEqual(sum(r['duration_ms'] for r in rows),90000)
        with self.assertRaises(ValueError):lesson.split_match_row({**row,'player_id':8},interval,events,goals()[:1],1,2,[{'period':1,'length_ms':90000}])

    def test_sql_keeps_zero_exposure_undefined(self):
        source=json.loads((ROOT/lesson.SOURCES['drilldown']).read_text())
        base=json.loads((ROOT/source['source_files']['database']['path']).read_text())
        row=source['rows'][0]
        states=[{**row,'score_state':label,'duration_ms':row['duration_ms'] if label=='Drawing' else 0,
                 'completed_passes':row['completed_passes'] if label=='Drawing' else 0,
                 'forward_passes':row['forward_passes'] if label=='Drawing' else 0,
                 'recorded_pressures':row['recorded_pressures'] if label=='Drawing' else 0} for label in lesson.STATES]
        with closing(sqlite3.connect(':memory:')) as connection:
            lesson.drill.database.create_database(connection,base['rows']);lesson.drill.create_match_table(connection,source['rows'])
            lesson.create_state_table(connection,states)
            rates={r['score_state']:r for r in lesson.query_rates(connection)}
        self.assertIsNone(rates['Leading']['forward_per90'])
        self.assertIsNone(rates['Trailing']['completed_per90'])
        self.assertIsNotNone(rates['Drawing']['forward_per90'])
