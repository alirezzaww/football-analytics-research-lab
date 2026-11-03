"""Explicit linking must not fall back to a nearby or unrelated pass."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('header_links', ROOT / '34_header_assisting_passes.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


class HeaderLinkTests(unittest.TestCase):
    def setUp(self):
        self.shot = {'id': 's', 'shot': {'key_pass_id': 'p'}, 'period': 1,
                     'team': {'id': 1}, 'index': 20, 'possession': 3}
        self.p = {'id': 'p', 'type': {'name': 'Pass'}, 'period': 1, 'team': {'id': 1},
                  'index': 18, 'possession': 3, 'pass': {'assisted_shot_id': 's'}}

    def test_reciprocal_link_not_nearest_event(self):
        status, p = lesson.linked_pass(self.shot, {'p': self.p})
        self.assertEqual(status, 'Verified reciprocal link')
        self.assertEqual(p['id'], 'p')

    def test_missing_or_unavailable_links_stay_unresolved(self):
        shot = copy.deepcopy(self.shot); shot['shot'] = {}
        self.assertIsNone(lesson.linked_pass(shot, {'p': self.p})[1])
        self.assertEqual(lesson.linked_pass(self.shot, {})[0], 'Linked event unavailable')

    def test_reject_mismatched_context_or_reciprocal_identity(self):
        for key, value in [('period', 2), ('index', 21), ('possession', 4), ('team', {'id': 2}),
                           ('type', {'name': 'Carry'}), ('pass', {'assisted_shot_id': 'another-shot'})]:
            p = copy.deepcopy(self.p); p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                lesson.linked_pass(self.shot, {'p': p})
