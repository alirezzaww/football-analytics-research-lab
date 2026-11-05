"""Fault injection on synthetic records, preserving the real source ledgers."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit59', ROOT/'59_corner_data_quality.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def records():
    return ([dict(match_id=1,corner_id='a'),dict(match_id=1,corner_id='b')],
            [dict(match_id=1,shot_id='s',corner_id='a')],
            [dict(match_id=1,corner_id='a',passer='A'),dict(match_id=1,corner_id='b',passer='B')])


def failures(corners, shots, takers):
    return {r['check_name']:r['violation_count'] for r in lesson.audit_records(corners,shots,takers)
            if not r['passed']}


class CornerDataQualityTests(unittest.TestCase):
    def test_zero_shot_corner_is_valid_and_inputs_are_not_changed(self):
        data = records()
        original = copy.deepcopy(data)
        self.assertEqual(failures(*data),{})
        self.assertEqual(data,original)

    def test_duplicate_corner_shot_and_taker_keys_detected(self):
        c,s,t = records()
        c.append(c[0].copy());s.append(s[0].copy());t.append(t[0].copy())
        self.assertEqual(failures(c,s,t),{'duplicate_corner_keys':1,'duplicate_shot_keys':1,
                                        'duplicate_taker_keys':1})

    def test_missing_taker_stops_report_validation(self):
        c,s,t = records();t.pop()
        self.assertEqual(failures(c,s,t),{'missing_taker_records':1})
        with self.assertRaisesRegex(ValueError,'missing_taker_records'):
            lesson.require_valid_relationships(c,s,t)

    def test_unknown_references_use_complete_match_corner_key(self):
        c,s,t = records()
        s[0]['match_id']=2
        t.append(dict(match_id=2,corner_id='a',passer='A'))
        self.assertEqual(failures(c,s,t),{'unknown_taker_corners':1,'unknown_shot_corners':1})

    def test_repeated_ids_in_different_matches_are_not_duplicates(self):
        c,s,t = records()
        c.append(dict(match_id=2,corner_id='a'))
        s.append(dict(match_id=2,corner_id='a',shot_id='s'))
        t.append(dict(match_id=2,corner_id='a',passer='Other'))
        self.assertEqual(failures(c,s,t),{})

    def test_blank_names_and_missing_identity_are_reported(self):
        c,s,t = records();t[0]['passer']='  ';s[0].pop('shot_id')
        self.assertEqual(failures(c,s,t),{'blank_taker_names':1,'missing_identity_fields':1})

    def test_empty_input_is_not_an_all_clear(self):
        self.assertEqual(failures([],[],[]),{'nonempty_corners':1})
        with self.assertRaisesRegex(ValueError,'nonempty_corners'):
            lesson.require_valid_relationships([],[],[])
