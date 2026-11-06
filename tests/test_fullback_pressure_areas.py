"""Spatial boundaries, missing locations, identity coverage and share denominators."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('areas75', ROOT/'75_fullback_pressure_areas.py')
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def row(identifier, x, y=40):
    return {'match_id': 1, 'team_id': 1, 'player_id': 7, 'event_id': identifier,
            'x': x, 'y': y if x is not None else None, 'location_valid': x is not None}


def player(total=4, mapped=3):
    return {'team_id': 1, 'player_id': 7, 'qualifying_match_ids': [1],
            'duration_ms': 45*60000, 'minutes': 45, 'recorded_pressures': total,
            'mapped_pressures': mapped, 'unmapped_pressures': total-mapped}


class PressureAreaTests(unittest.TestCase):
    def test_thirds_partition_exact_boundaries(self):
        for x, expected in ((0, 'Own third'), (39.9, 'Own third'), (40, 'Middle third'),
                            (79.9, 'Middle third'), (80, 'Opponent third'), (120, 'Opponent third')):
            with self.subTest(x=x):
                self.assertEqual(lesson.area_for(row('a', x)), expected)

    def test_missing_location_is_retained_but_outside_share_denominator(self):
        result = lesson.summarize(player(), [row('a', 10), row('b', 40), row('c', 90), row('d', None)])
        self.assertEqual(result['recorded_pressures'], 4)
        self.assertEqual(result['unmapped_pressures'], 1)
        for area in result['pressure_areas']:
            self.assertAlmostEqual(area['share_of_mapped_pressures_pct'], 100/3)
            self.assertEqual(area['per90'], 2)
        self.assertEqual(sum(a['count'] for a in result['pressure_areas']), 3)

    def test_no_mapped_actions_is_undefined_but_empty_area_with_coverage_is_zero(self):
        result = lesson.summarize(player(1, 0), [row('a', None)])
        self.assertTrue(all(a['share_of_mapped_pressures_pct'] is None for a in result['pressure_areas']))
        result = lesson.summarize(player(1, 1), [row('a', 10)])
        self.assertEqual(result['pressure_areas'][2]['share_of_mapped_pressures_pct'], 0)

    def test_invalid_mapped_coordinates_and_unmapped_nonnull_are_rejected(self):
        for action in (row('a', 121), row('a', -1), row('a', 10, 81),
                       row('a', float('nan')), row('a', True),
                       {**row('a', 20), 'location_valid': False}):
            with self.subTest(action=action), self.assertRaises(ValueError):
                lesson.area_for(action)

    def test_wrong_identity_fixture_duplicate_or_incomplete_membership_rejected(self):
        for rows in ([row('a', 10), row('a', 20)],
                     [{**row('a', 10), 'team_id': 2}, row('b', 20)],
                     [{**row('a', 10), 'match_id': 2}, row('b', 20)], [row('a', 10)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                lesson.summarize(player(2, 2), rows)

    def test_duration_and_source_location_coverage_must_match(self):
        with self.assertRaises(ValueError):
            lesson.summarize({**player(1, 1), 'minutes': 90}, [row('a', 10)])
        with self.assertRaises(ValueError):
            lesson.summarize(player(1, 0), [row('a', 10)])
