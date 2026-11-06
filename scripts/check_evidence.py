"""Offline consistency checks for the saved research artifacts (standard library only)."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((ROOT / 'data' / name).read_text())

def ids(rows):
    values = {(r['match_id'], r['id']) for r in rows}
    assert len(values) == len(rows), 'Duplicate selected pass identity'
    return values

base = read('11_tournament_passes_evidence.json')
timed = read('13_minutes_and_quality_evidence.json')
sensitivity = read('14_threshold_sensitivity_evidence.json')
profile = read('15_kirby_profile_evidence.json')
variation = read('16_match_variation_evidence.json')
volume = read('17_passing_volume_evidence.json')
model = read('18_first_xg_model_evidence.json')
manifest = read('source_manifest.json')

assert base['games'] == len(set(base['match_ids'])) == 7
assert len(base['selected_passes']) == base['total_qualifying_passes'] == 200
assert sum(base['per_match_counts'].values()) == 200
assert sum(map(sum, base['raw_zone_counts'])) == 200
assert math.isclose(sum(map(sum, base['zone_rates_per_game'])), 200 / 7)
counts = Counter(str(p['match_id']) for p in base['selected_passes'])
assert all(counts[k] == value for k, value in base['per_match_counts'].items())
assert ids(base['selected_passes']) == ids(timed['all_qualifying_passes'])

low = sensitivity['selected_passes']['0.07']
high = sensitivity['selected_passes']['0.10']
assert len(low) == 113 and len(high) == 98
assert ids(high) <= ids(low) <= ids(base['selected_passes'])
assert ids(low) == ids(timed['passes_before_shots_above_threshold'])
for rows, threshold in [(low, 0.07), (high, 0.10)]:
    assert all(p['shot_xg'] > threshold and 0 <= p['seconds_before_shot'] <= 15 for p in rows)

interval_minutes = defaultdict(float)
match_minutes = defaultdict(float)
for interval in timed['player_intervals']:
    value = (interval['end_seconds'] - interval['start_seconds']) / 60
    assert value > 0 and math.isclose(value, interval['minutes'])
    interval_minutes[interval['player_id']] += value
    match_minutes[interval['match_id']] += value
for audit in timed['match_audits']:
    expected = 11 * audit['match_minutes'] - audit['sending_off_or_permanent_departure_seconds_lost'] / 60
    assert math.isclose(match_minutes[audit['match_id']], expected)
for p in timed['players']:
    assert p['minutes'] > 0 and math.isclose(p['minutes'], interval_minutes[p['player_id']])
    assert math.isclose(p['all_qualifying_per90'], p['all_qualifying'] / p['minutes'] * 90)
assert sum(p['all_qualifying'] for p in timed['players']) == 200
for suffix, rows in [('007', low), ('010', high)]:
    per_player = Counter(p['player_id'] for p in rows)
    for p in sensitivity['players']:
        assert p[f'count_{suffix}'] == per_player[p['player_id']]
        assert math.isclose(p[f'per90_{suffix}'], p[f'count_{suffix}'] / p['minutes'] * 90)

rows = profile['selected_passes']
assert len(rows) == 12
assert ids(rows) == ids([p for p in high if p['player_name'] == profile['player']])
assert profile['forward'] == sum(p['end_x'] > p['x'] for p in rows) == 10
assert profile['backward'] == sum(p['end_x'] < p['x'] for p in rows) == 2
assert profile['final_third_starts'] == sum(p['x'] >= 80 for p in rows) == 9
assert profile['final_third_entries'] == sum(p['x'] < 80 <= p['end_x'] for p in rows) == 2

match_rows = variation['matches']
assert {r['match_id'] for r in match_rows} == set(base['match_ids'])
assert sum(r['qualifying_passes'] for r in match_rows) == variation['total_passes'] == 12
player_intervals = [r for r in timed['player_intervals'] if r['player_name'] == variation['player']]
for row in match_rows:
    expected_minutes = sum(r['minutes'] for r in player_intervals if r['match_id'] == row['match_id'])
    expected_count = sum(r['match_id'] == row['match_id'] and r['player_name'] == variation['player'] for r in high)
    assert row['qualifying_passes'] == expected_count
    assert math.isclose(row['minutes'], expected_minutes)
    if row['minutes'] == 0:
        assert row['per90'] is None and row['qualifying_passes'] == 0
    else:
        assert math.isclose(row['per90'], expected_count / expected_minutes * 90)
assert math.isclose(sum(r['minutes'] for r in match_rows), variation['total_minutes'])
assert math.isclose(variation['tournament_per90'], 12 / variation['total_minutes'] * 90)
for row in variation['leave_one_appearance_out']:
    omitted = next(r for r in match_rows if r['match_id'] == row['omitted_match_id'])
    assert omitted['minutes'] > 0
    assert row['remaining_passes'] == 12 - omitted['qualifying_passes']
    assert math.isclose(row['remaining_minutes'], variation['total_minutes'] - omitted['minutes'])
    assert math.isclose(row['per90'], row['remaining_passes'] / row['remaining_minutes'] * 90)

assert set(volume['match_ids']) == set(base['match_ids'])
assert sum(p['qualifying_passes'] for p in volume['players']) == volume['qualifying_passes_total'] == 98
assert sum(p['eligible_completed_passes'] for p in volume['players']) == volume['eligible_passes_total'] == 2837
selected_counts = Counter(p['player_id'] for p in high)
for row in volume['players']:
    assert row['qualifying_passes'] == selected_counts[row['player_id']]
    assert row['eligible_completed_passes'] >= row['qualifying_passes']
    assert math.isclose(row['eligible_passes_per90'], row['eligible_completed_passes'] / row['minutes'] * 90)
    if row['eligible_completed_passes']:
        assert math.isclose(row['qualifying_share_pct'], row['qualifying_passes'] / row['eligible_completed_passes'] * 100)
        assert math.isclose(row['qualifying_per90'], row['eligible_passes_per90'] * row['qualifying_share_pct'] / 100)
    else:
        assert row['qualifying_share_pct'] is None

# Check a genuinely held-out match split and recompute saved model predictions/scores.
train_ids, test_ids = set(model['training_match_ids']), set(model['test_match_ids'])
assert len(train_ids) == 5 and len(test_ids) == 2 and train_ids.isdisjoint(test_ids)
assert train_ids | test_ids == set(base['match_ids'])
train = [r for r in model['shots'] if r['split'] == 'train']
test = [r for r in model['shots'] if r['split'] == 'test']
assert len(train) == model['training_shots'] == 114
assert len(test) == model['test_shots'] == 36
assert sum(r['goal'] for r in train) == model['training_goals'] == 11
assert sum(r['goal'] for r in test) == model['test_goals'] == 6
assert all(r['match_id'] in train_ids for r in train)
assert all(r['match_id'] in test_ids for r in test)
ids(model['shots'])
mean_distance = sum(r['distance'] for r in train) / len(train)
scale = math.sqrt(sum((r['distance'] - mean_distance) ** 2 for r in train) / len(train))
assert math.isclose(model['training_mean_distance'], mean_distance)
assert math.isclose(model['training_scale_distance'], scale)
assert math.isclose(model['baseline_training_goal_rate'], 11 / 114)
assert model['optimisation_success']
for row in model['shots']:
    assert row['goal'] in [0, 1]
    assert math.isclose(row['distance'], math.hypot(120 - row['x'], 40 - row['y']))
    z = model['intercept_scaled'] + model['distance_coefficient_scaled'] * (row['distance'] - mean_distance) / scale
    predicted = 1 / (1 + math.exp(-z))
    assert 0 < row['predicted_xg'] < 1 and math.isclose(row['predicted_xg'], predicted)
for key, probabilities in [
        ('model_test_metrics', [r['predicted_xg'] for r in test]),
        ('baseline_test_metrics', [11 / 114] * len(test))]:
    brier = sum((p - r['goal']) ** 2 for p, r in zip(probabilities, test)) / len(test)
    log_loss = -sum(r['goal'] * math.log(p) + (1 - r['goal']) * math.log(1 - p)
                    for p, r in zip(probabilities, test)) / len(test)
    assert math.isclose(model[key]['brier_score'], brier)
    assert math.isclose(model[key]['log_loss'], log_loss)
    assert math.isclose(model[key]['predicted_goal_total'], sum(probabilities))

# Lesson 19: reconcile every time window, not only headline totals.
window_study = read('19_time_window_evidence.json')
assert window_study['windows_seconds_inclusive'] == [5, 10, 15]
assert window_study['xg_threshold_strictly_greater_than'] == 0.10
previous_ids = set()
for window, expected_total in [(5, 38), (10, 68), (15, 98)]:
    result = window_study['windows'][str(window)]
    expected_rows = [p for p in high if 0 <= p['seconds_before_shot'] <= window]
    assert result['selected_passes'] == expected_rows
    current_ids = ids(result['selected_passes'])
    assert previous_ids <= current_ids
    previous_ids = current_ids
    assert result['total'] == len(current_ids) == expected_total
    by_player = Counter(p['player_id'] for p in expected_rows)
    assert len(result['players']) == len(sensitivity['players'])
    assert len({p['player_id'] for p in result['players']}) == len(result['players'])
    original_players = {p['player_id']: p for p in sensitivity['players']}
    for player in result['players']:
        original = original_players[player['player_id']]
        assert player['player_name'] == original['player_name']
        assert player['minutes'] == original['minutes']
        assert player['count'] == by_player[player['player_id']]
        assert math.isclose(player['per90'], player['count'] / player['minutes'] * 90)
    assert sum(p['count'] for p in result['players']) == result['total']
assert previous_ids == ids(high)

# Independently reconstruct from raw events when available. This verifies that
# filtering the saved nearest-shot gaps gives the full shorter-window selections.
raw_window_matches = 0
for match_id in base['match_ids']:
    path = ROOT / f'data/cache_2019_events/{match_id}.json'
    if not path.exists():
        continue
    events = json.loads(path.read_text())
    team_events = [e for e in events if e['team']['name'] == "England Women's"]
    shots = [e for e in team_events if e['type']['name'] == 'Shot' and e['shot']['statsbomb_xg'] > 0.10]
    passes = [e for e in team_events if e['type']['name'] == 'Pass'
              and 'outcome' not in e['pass']
              and e['possession_team']['id'] == e['team']['id']
              and e['pass'].get('type', {}).get('name') not in
              ['Throw-in', 'Corner', 'Free Kick', 'Kick Off', 'Goal Kick']]
    for window in [5, 10, 15]:
        expected = set()
        for event in passes:
            if any(shot['period'] == event['period'] and shot['possession'] == event['possession']
                   and shot['index'] > event['index']
                   and 0 <= (shot['minute'] - event['minute']) * 60 + shot['second'] - event['second'] <= window
                   for shot in shots):
                expected.add((match_id, event['id']))
        saved = [p for p in window_study['windows'][str(window)]['selected_passes'] if p['match_id'] == match_id]
        assert ids(saved) == expected, f'Raw window reconstruction differs: {match_id}, {window}'
    raw_window_matches += 1

# Lesson 20: denominator and numerator must come from the same starting third.
context = read('20_pass_location_evidence.json')
zone_names = ['Defensive third', 'Middle third', 'Attacking third']
assert context['match_ids'] == base['match_ids']
assert context['windows_seconds_inclusive'] == 15
assert context['xg_threshold_strictly_greater_than'] == 0.10
assert context['zones'] == [
    {'name': name, 'lower_x_inclusive': low, 'upper_x': upper, 'upper_inclusive': upper == 120}
    for name, low, upper in zip(zone_names, [0, 40, 80], [40, 80, 120])]
ledger = context['passes']
assert len(ledger) == len(ids(ledger)) == context['eligible_completed_passes'] == volume['eligible_passes_total']
assert ids([p for p in ledger if p['qualifying']]) == ids(high)
assert context['qualifying_passes'] == len(high)
assert all(type(p['qualifying']) is bool for p in ledger)
assert all(p['match_id'] in base['match_ids'] for p in ledger)
for row in ledger:
    assert math.isfinite(row['x']) and 0 <= row['x'] <= 120
    assert row['zone'] == zone_names[min(int(row['x'] // 40), 2)]
zone_denominators = Counter((p['player_id'], p['zone']) for p in ledger)
zone_numerators = Counter((p['player_id'], p['zone']) for p in ledger if p['qualifying'])
assert len({p['player_id'] for p in context['players']}) == len(context['players'])
original_players = {p['player_id']: p for p in volume['players']}
assert {p['player_id'] for p in context['players']} == set(original_players)
assert {p['player_id'] for p in ledger} <= set(original_players)
for player in context['players']:
    original = original_players[player['player_id']]
    assert player['player_name'] == original['player_name']
    assert player['eligible_completed_passes'] == original['eligible_completed_passes']
    assert player['qualifying_passes'] == original['qualifying_passes']
    assert [row['zone'] for row in player['zones']] == zone_names
    total = player['eligible_completed_passes']
    assert sum(r['eligible_completed_passes'] for r in player['zones']) == total
    assert sum(r['qualifying_passes'] for r in player['zones']) == player['qualifying_passes']
    overall = player['overall_qualifying_share_pct']
    if total:
        assert math.isclose(overall, player['qualifying_passes'] / total * 100)
        assert math.isclose(sum(r['pass_start_mix_pct'] for r in player['zones']), 100)
    else:
        assert overall is None
    for row in player['zones']:
        key = (player['player_id'], row['zone'])
        n, k = zone_denominators[key], zone_numerators[key]
        assert row['eligible_completed_passes'] == n and row['qualifying_passes'] == k
        assert 0 <= k <= n
        if n:
            assert math.isclose(row['qualifying_share_pct'], k / n * 100)
        else:
            assert row['qualifying_share_pct'] is None
        if total:
            assert math.isclose(row['pass_start_mix_pct'], n / total * 100)
        else:
            assert row['pass_start_mix_pct'] is None

raw_context_matches = 0
for match_id in base['match_ids']:
    path = ROOT / f'data/cache_2019_events/{match_id}.json'
    if not path.exists():
        continue
    expected = {}
    for event in json.loads(path.read_text()):
        if (event['type']['name'] == 'Pass' and event['team']['name'] == "England Women's"
                and 'outcome' not in event['pass']
                and event['possession_team']['id'] == event['team']['id']
                and event['pass'].get('type', {}).get('name') not in
                ['Throw-in', 'Corner', 'Free Kick', 'Kick Off', 'Goal Kick']):
            expected[event['id']] = (event['player']['id'], event['location'][0])
    actual = {p['id']: (p['player_id'], p['x']) for p in ledger if p['match_id'] == match_id}
    assert actual == expected, f'Pass-location denominator differs from raw input: {match_id}'
    raw_context_matches += 1

# Lesson 21: rebuild fixture counts and replay every paired match draw offline.
bootstrap = read('21_match_bootstrap_evidence.json')
assert bootstrap['source'] == '20_pass_location_evidence.json'
assert bootstrap['zone'] == 'Attacking third'
assert bootstrap['xg_threshold_strictly_greater_than'] == 0.10
assert bootstrap['time_window_seconds_inclusive'] == 15
assert [p['player_name'] for p in bootstrap['player_order']] == ['Francesca Kirby', 'Lucy Bronze']
expected_players = [next(p for p in context['players'] if p['player_name'] == name)
                    for name in ['Francesca Kirby', 'Lucy Bronze']]
assert bootstrap['player_order'] == [{'player_id': p['player_id'], 'player_name': p['player_name']} for p in expected_players]
fixture_rows = []
for match_id in base['match_ids']:
    cells = []
    for player in bootstrap['player_order']:
        passes = [p for p in ledger if p['match_id'] == match_id and p['player_id'] == player['player_id'] and p['x'] >= 80]
        cells.append({'qualifying_passes': sum(p['qualifying'] for p in passes), 'eligible_completed_passes': len(passes)})
    fixture_rows.append({'match_id': match_id, 'players': cells})
assert bootstrap['match_counts'] == fixture_rows
for j, expected_share in enumerate(bootstrap['observed_shares_pct']):
    k = sum(row['players'][j]['qualifying_passes'] for row in fixture_rows)
    n = sum(row['players'][j]['eligible_completed_passes'] for row in fixture_rows)
    assert math.isclose(expected_share, 100 * k / n)
assert math.isclose(bootstrap['observed_difference_percentage_points'], bootstrap['observed_shares_pct'][0] - bootstrap['observed_shares_pct'][1])
import random
rng = random.Random(bootstrap['seed'])
assert bootstrap['n_resamples'] == 10000 and bootstrap['seed'] == 20261030
replayed, invalid = [], 0
for draw in range(bootstrap['n_resamples']):
    indices = [rng.randrange(len(fixture_rows)) for _ in fixture_rows]
    if draw == 0:
        assert bootstrap['example_match_ids'] == [fixture_rows[i]['match_id'] for i in indices]
    totals = [[sum(fixture_rows[i]['players'][j][key] for i in indices)
               for key in ['qualifying_passes', 'eligible_completed_passes']] for j in range(2)]
    if any(n == 0 for k, n in totals):
        invalid += 1
    else:
        replayed.append(100 * totals[0][0] / totals[0][1] - 100 * totals[1][0] / totals[1][1])
assert bootstrap['valid_resamples'] == len(replayed)
assert bootstrap['zero_denominator_resamples'] == invalid
assert len(replayed) + invalid == bootstrap['n_resamples']
assert bootstrap['differences_percentage_points'] == replayed
assert bootstrap['percentiles'] == [0.025, 0.975]
assert bootstrap['percentile_method'] == 'linear interpolation at (n - 1) * q'
ordered = sorted(replayed)
for quantile, endpoint in zip(bootstrap['percentiles'], bootstrap['illustrative_interval_percentage_points']):
    position = quantile * (len(ordered) - 1)
    fraction = position % 1
    expected = (1 - fraction) * ordered[math.floor(position)] + fraction * ordered[math.ceil(position)]
    assert math.isclose(expected, endpoint)

# Lesson 22: use the score before each pass, not the final result or future goals.
score_context = read('22_score_state_evidence.json')
assert score_context['match_ids'] == base['match_ids']
assert score_context['time_window_seconds_inclusive'] == 15
assert score_context['xg_threshold_strictly_greater_than'] == 0.10
state_ledger = score_context['passes']
assert ids(state_ledger) == ids(ledger)
original_passes = {(p['match_id'], p['id']): p for p in ledger}
state_names = ['Leading', 'Drawing', 'Trailing']
audit_by_match = {a['match_id']: a for a in score_context['match_audits']}
assert len(audit_by_match) == len(score_context['match_audits']) == 7
assert set(audit_by_match) == set(base['match_ids'])

def check_state_summary(saved, passes):
    assert [r['state'] for r in saved] == state_names
    for row in saved:
        group = [p for p in passes if p['state'] == row['state']]
        k, n = sum(p['qualifying'] for p in group), len(group)
        assert row['eligible_completed_passes'] == n and row['qualifying_passes'] == k
        if n:
            assert math.isclose(row['qualifying_share_pct'], 100 * k / n)
        else:
            assert row['qualifying_share_pct'] is None

for match_id, audit in audit_by_match.items():
    tally = [0, 0]
    last_index = -1
    for goal in audit['goals']:
        assert goal['index'] > last_index
        assert goal['score_before'] == tally
        credited = goal['credited_team_id']
        assert credited in [audit['england_team_id'], audit['opponent_team_id']]
        tally[0 if credited == audit['england_team_id'] else 1] += 1
        assert goal['score_after'] == tally
        last_index = goal['index']
    assert tally == audit['provider_final_score_england_opponent'] == audit['reconstructed_final_score_england_opponent']
    rows = [p for p in state_ledger if p['match_id'] == match_id]
    for row in rows:
        original = original_passes[(match_id, row['id'])]
        assert row['player_id'] == original['player_id'] and row['qualifying'] == original['qualifying']
        prior = [g for g in audit['goals'] if g['index'] < row['index']]
        before = prior[-1]['score_after'] if prior else [0, 0]
        assert [row['england_goals_before'], row['opponent_goals_before']] == before
        expected_state = 'Leading' if before[0] > before[1] else 'Trailing' if before[0] < before[1] else 'Drawing'
        assert row['state'] == expected_state
    check_state_summary(audit['states'], rows)
check_state_summary(score_context['team_states'], state_ledger)
assert sum(r['qualifying_passes'] for r in score_context['team_states']) == 98
assert sum(r['eligible_completed_passes'] for r in score_context['team_states']) == 2837
assert {p['match_id'] for p in state_ledger if p['state'] == 'Trailing'} == {69258, 69301}
assert {p['player_id'] for p in score_context['players']} == set(original_players)
assert len(score_context['players']) == len(original_players)
for player in score_context['players']:
    assert player['player_name'] == original_players[player['player_id']]['player_name']
    check_state_summary(player['states'], [p for p in state_ledger if p['player_id'] == player['player_id']])
metadata_source = score_context['metadata_source']
assert metadata_source['url'] == 'https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/72/30.json'
metadata_path = ROOT / metadata_source['relative_path']
if metadata_path.exists():
    assert hashlib.sha256(metadata_path.read_bytes()).hexdigest() == metadata_source['sha256']
    metadata = {m['match_id']: m for m in json.loads(metadata_path.read_text())}
    for match_id, audit in audit_by_match.items():
        match = metadata[match_id]
        home = match['home_team']['home_team_name'] == "England Women's"
        expected = [match['home_score'], match['away_score']] if home else [match['away_score'], match['home_score']]
        assert expected == audit['provider_final_score_england_opponent']

raw_score_matches = 0
for match_id, audit in audit_by_match.items():
    path = ROOT / f'data/cache_2019_events/{match_id}.json'
    if not path.exists():
        continue
    rows = {p['id']: p for p in state_ledger if p['match_id'] == match_id}
    tally = [0, 0]
    raw_goal_ids = []
    for event in sorted(json.loads(path.read_text()), key=lambda e: e['index']):
        if event['period'] == 5:
            continue
        if event['id'] in rows:
            saved = rows[event['id']]
            assert saved['index'] == event['index']
            assert [saved['england_goals_before'], saved['opponent_goals_before']] == tally
        kind = event['type']['name']
        if kind == 'Shot' and event['shot']['outcome']['name'] == 'Goal':
            tally[0 if event['team']['id'] == audit['england_team_id'] else 1] += 1
            raw_goal_ids.append(event['id'])
        elif kind == 'Own Goal Against':
            tally[1 if event['team']['id'] == audit['england_team_id'] else 0] += 1
            raw_goal_ids.append(event['id'])
    assert raw_goal_ids == [g['id'] for g in audit['goals']]
    assert tally == audit['provider_final_score_england_opponent']
    raw_score_matches += 1

# Lesson 23: a within-match comparison needs observations in both states.
within = read('23_within_match_evidence.json')
assert within['source'] == '22_score_state_evidence.json'
assert within['match_ids'] == base['match_ids']
assert within['time_window_seconds_inclusive'] == 15
assert within['xg_threshold_strictly_greater_than'] == 0.10
assert [m['match_id'] for m in within['coverage']] == base['match_ids']
for match in within['coverage']:
    assert match['opponent'] == audit_by_match[match['match_id']]['opponent']
    check_state_summary(match['states'], [p for p in state_ledger if p['match_id'] == match['match_id']])
assert set(within['comparisons']) == {'drawing_vs_trailing', 'leading_vs_trailing'}
for name, comparison in within['comparisons'].items():
    first, second = comparison['states']
    assert name == f'{first.lower()}_vs_{second.lower()}'
    observed = {state: {p['match_id'] for p in state_ledger if p['state'] == state} for state in [first, second]}
    expected_common = [m for m in base['match_ids'] if m in observed[first] & observed[second]]
    assert comparison['common_match_ids'] == expected_common
    for key, rows in [('all_fixture_pool', state_ledger),
                      ('common_fixture_pool', [p for p in state_ledger if p['match_id'] in expected_common])]:
        assert [c['state'] for c in comparison[key]] == [first, second]
        for cell in comparison[key]:
            group = [p for p in rows if p['state'] == cell['state']]
            k, n = sum(p['qualifying'] for p in group), len(group)
            assert cell['qualifying_passes'] == k and cell['eligible_completed_passes'] == n
            if n:
                assert math.isclose(cell['qualifying_share_pct'], 100 * k / n)
            else:
                assert cell['qualifying_share_pct'] is None
        shares = [c['qualifying_share_pct'] for c in comparison[key]]
        difference_key = ('all' if key == 'all_fixture_pool' else 'common') + '_difference_second_minus_first_pp'
        if any(value is None for value in shares):
            assert comparison[difference_key] is None
        else:
            assert math.isclose(comparison[difference_key], shares[1] - shares[0], abs_tol=1e-12)
    assert [row['match_id'] for row in comparison['per_common_fixture']] == expected_common
    for fixture in comparison['per_common_fixture']:
        original = {r['state']: r for r in audit_by_match[fixture['match_id']]['states']}
        assert fixture['states'] == [original[state] for state in [first, second]]
assert within['comparisons']['leading_vs_trailing']['common_match_ids'] == []
assert within['comparisons']['drawing_vs_trailing']['common_match_ids'] == [69258, 69301]

# Lesson 24: pass rows, represented shots and possessions are distinct units.
units = read('24_shot_units_evidence.json')
assert units['sources'] == ['14_threshold_sensitivity_evidence.json', '22_score_state_evidence.json']
assert units['time_window_seconds_inclusive'] == 15 and units['xg_threshold_strictly_greater_than'] == 0.10
expected_ids = ids([p for p in state_ledger if p['state'] == 'Trailing' and p['qualifying']])
expected_passes = [p for p in high if (p['match_id'], p['id']) in expected_ids]
flattened = [p for group in units['groups'] for p in group['selected_passes']]
assert ids(flattened) == expected_ids
assert {(p['match_id'], p['id']): p for p in flattened} == {(p['match_id'], p['id']): p for p in expected_passes}
shot_keys = {(p['match_id'], p['shot_id']) for p in expected_passes}
assert {(g['match_id'], g['shot']['id']) for g in units['groups']} == shot_keys
assert len(units['groups']) == len(shot_keys)
for group in units['groups']:
    shot = group['shot']
    rows = group['selected_passes']
    assert group['opponent'] == audit_by_match[group['match_id']]['opponent']
    assert rows == sorted(rows, key=lambda p: p['index'])
    for row in rows:
        assert row['match_id'] == group['match_id'] and row['shot_id'] == shot['id']
        assert row['shot_xg'] == shot['xg'] > 0.10
        assert row['possession'] == shot['possession'] and row['period'] == shot['period']
        assert row['index'] < shot['index']
        assert shot['minute'] * 60 + shot['second'] - row['clock'] == row['seconds_before_shot']
    prior = [g for g in audit_by_match[group['match_id']]['goals'] if g['index'] < shot['index']]
    assert shot['score_before_england_opponent'] == (prior[-1]['score_after'] if prior else [0, 0])
    path = ROOT / f"data/cache_2019_events/{group['match_id']}.json"
    if path.exists():
        original = next(e for e in json.loads(path.read_text()) if e['id'] == shot['id'])
        assert original['type']['name'] == 'Shot' and original['team']['name'] == "England Women's"
        for key in ['index', 'period', 'possession', 'minute', 'second']:
            assert shot[key] == original[key]
        assert shot['player_name'] == original['player']['name']
        assert shot['xg'] == original['shot']['statsbomb_xg']
        assert shot['outcome'] == original['shot']['outcome']['name']
summary = units['summary']
assert summary['qualifying_passes'] == len(expected_passes) == 12
assert summary['distinct_assigned_shots'] == len(shot_keys) == 3
assert summary['distinct_possessions'] == len({(p['match_id'], p['period'], p['possession']) for p in expected_passes}) == 3
assert summary['goals_from_represented_shots'] == sum(g['shot']['outcome'] == 'Goal' for g in units['groups']) == 2
unique_xg = sum(g['shot']['xg'] for g in units['groups'])
repeated_xg = sum(p['shot_xg'] for p in expected_passes)
assert math.isclose(summary['assigned_shot_xg_counted_once'], unique_xg)
assert math.isclose(summary['incorrect_repeated_shot_xg_sum_for_demonstration'], repeated_xg)

# Lesson 25: geometry, grouped training-only validation and fold-local scaling.
angle_study = read('25_shot_angle_evidence.json')
assert angle_study['source'] == '18_first_xg_model_evidence.json'
assert angle_study['training_match_ids'] == model['training_match_ids']
assert angle_study['reused_test_match_ids'] == model['test_match_ids']
assert set(angle_study['training_match_ids']).isdisjoint(angle_study['reused_test_match_ids'])
assert angle_study['primary_selection_metric'] == 'pooled training-only leave-one-match-out log loss'
angle_rows = angle_study['shots']
assert ids(angle_rows) == ids(model['shots'])
source_shots = {(r['match_id'], r['id']): r for r in model['shots']}
for row in angle_rows:
    original = source_shots[(row['match_id'], row['id'])]
    for key in ['x', 'y', 'goal', 'split', 'body_part']:
        assert row[key] == original[key]
    dx, lateral = (120 - row['x']) * 105 / 120, (row['y'] - 40) * 68 / 80
    # Independent angle check from the dot product of vectors to each goalpost.
    a, b = -3.66 - lateral, 3.66 - lateral
    cosine = (dx * dx + a * b) / (math.hypot(dx, a) * math.hypot(dx, b))
    expected_angle = math.acos(max(-1, min(1, cosine)))
    assert math.isclose(row['distance_template_m'], math.hypot(dx, lateral))
    assert math.isclose(row['angle_radians'], expected_angle, abs_tol=1e-10)
angle_train = [r for r in angle_rows if r['split'] == 'train']
angle_test = [r for r in angle_rows if r['split'] == 'test']
assert len(angle_train) == 114 and len(angle_test) == 36
expected_features = {'constant': [], 'distance': ['distance_template_m'],
                     'distance_angle': ['distance_template_m', 'angle_radians']}
assert set(angle_study['candidates']) == set(expected_features)

def angle_prediction(fit, row):
    z = fit['coefficients'][0] + sum(fit['coefficients'][j + 1] * (row[f] - fit['means'][j]) / fit['scales'][j]
                                    for j, f in enumerate(fit['features']))
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    exponent = math.exp(z)
    return exponent / (1 + exponent)

def check_angle_fit(fit, fitting_rows, features):
    assert fit['features'] == features and fit['converged']
    assert len(fit['coefficients']) == len(features) + 1
    assert len(fit['means']) == len(fit['scales']) == len(features)
    assert all(math.isfinite(v) for v in fit['coefficients'])
    for j, f in enumerate(features):
        mean = sum(r[f] for r in fitting_rows) / len(fitting_rows)
        scale = math.sqrt(sum((r[f] - mean) ** 2 for r in fitting_rows) / len(fitting_rows))
        assert math.isclose(fit['means'][j], mean)
        assert scale > 0 and math.isclose(fit['scales'][j], scale)
    predictions = [angle_prediction(fit, r) for r in fitting_rows]
    if not features:
        rate = sum(r['goal'] for r in fitting_rows) / len(fitting_rows)
        assert all(math.isclose(p, rate) for p in predictions)
    # Check the stored fit satisfies the logistic likelihood gradient tolerance.
    residuals = [p - r['goal'] for p, r in zip(predictions, fitting_rows)]
    assert abs(sum(residuals) / len(residuals)) < 1e-5
    for j, f in enumerate(features):
        gradient = sum(error * (r[f] - fit['means'][j]) / fit['scales'][j]
                       for error, r in zip(residuals, fitting_rows)) / len(fitting_rows)
        assert abs(gradient) < 1e-5

def check_angle_scores(saved, rows, predictions):
    assert len(rows) == len(predictions) and rows
    assert all(math.isfinite(p) and 0 <= p <= 1 for p in predictions)
    brier = sum((p - r['goal']) ** 2 for p, r in zip(predictions, rows)) / len(rows)
    clipped = [max(1e-12, min(1 - 1e-12, p)) for p in predictions]
    loss = -sum(r['goal'] * math.log(p) + (1 - r['goal']) * math.log(1 - p)
                for r, p in zip(rows, clipped)) / len(rows)
    assert math.isclose(saved['brier_score'], brier)
    assert math.isclose(saved['log_loss'], loss)
    assert math.isclose(saved['predicted_goal_total'], sum(predictions))

for name, candidate in angle_study['candidates'].items():
    features = expected_features[name]
    assert candidate['features'] == features
    folds = candidate['validation_folds']
    assert [f['validation_match_id'] for f in folds] == angle_study['training_match_ids']
    validation_rows, validation_predictions = [], []
    for fold in folds:
        held_id = fold['validation_match_id']
        expected_fit_ids = [m for m in angle_study['training_match_ids'] if m != held_id]
        assert fold['fitting_match_ids'] == expected_fit_ids
        assert held_id not in expected_fit_ids
        fitting = [r for r in angle_train if r['match_id'] in expected_fit_ids]
        held = [r for r in angle_train if r['match_id'] == held_id]
        assert fold['validation_shot_ids'] == [r['id'] for r in held]
        check_angle_fit(fold['fit'], fitting, features)
        assert len(fold['predictions']) == len(held)
        assert all(math.isclose(p, angle_prediction(fold['fit'], r)) for p, r in zip(fold['predictions'], held))
        validation_rows.extend(held); validation_predictions.extend(fold['predictions'])
    assert ids(validation_rows) == ids(angle_train)
    check_angle_scores(candidate['validation_metrics'], validation_rows, validation_predictions)
    check_angle_fit(candidate['fit_all_training'], angle_train, features)
    assert candidate['reused_test_shot_ids'] == [r['id'] for r in angle_test]
    assert len(candidate['reused_test_predictions']) == len(angle_test)
    assert all(math.isclose(p, angle_prediction(candidate['fit_all_training'], r))
               for p, r in zip(candidate['reused_test_predictions'], angle_test))
    check_angle_scores(candidate['reused_test_metrics'], angle_test, candidate['reused_test_predictions'])
winner = min(angle_study['candidates'], key=lambda n: angle_study['candidates'][n]['validation_metrics']['log_loss'])
assert angle_study['selected_candidate'] == winner

# Lesson 26: use each out-of-fold training prediction once; never the reused test set.
calibration = read('26_calibration_evidence.json')
assert calibration['source'] == '25_shot_angle_evidence.json'
assert calibration['selected_candidate'] == angle_study['selected_candidate']
assert calibration['match_ids'] == angle_study['training_match_ids']
assert calibration['bin_edges'] == [0, 0.05, 0.10, 0.20, 1]
shot_lookup = {(r['match_id'], r['id']): r for r in angle_train}
expected_predictions = []
for fold in angle_study['candidates'][angle_study['selected_candidate']]['validation_folds']:
    for identity, probability in zip(fold['validation_shot_ids'], fold['predictions']):
        original = shot_lookup[(fold['validation_match_id'], identity)]
        expected_predictions.append({'match_id': original['match_id'], 'id': identity,
                                     'goal': original['goal'], 'predicted_probability': probability})
assert calibration['predictions'] == expected_predictions
assert ids(expected_predictions) == ids(angle_train)
assert all(p['match_id'] not in angle_study['reused_test_match_ids'] for p in expected_predictions)
assert len(calibration['bins']) == 4
binned_ids = []
for j, cell in enumerate(calibration['bins']):
    lower, upper = calibration['bin_edges'][j:j + 2]
    assert cell['bin_index'] == j and cell['lower_inclusive'] == lower and cell['upper'] == upper
    assert cell['upper_inclusive'] == (j == 3)
    rows = [r for r in expected_predictions if lower <= r['predicted_probability'] < upper
            or j == 3 and r['predicted_probability'] == 1]
    assert cell['shot_ids'] == [{'match_id': r['match_id'], 'id': r['id']} for r in rows]
    binned_ids.extend(rows)
    n, goals = len(rows), sum(r['goal'] for r in rows)
    predicted = sum(r['predicted_probability'] for r in rows)
    assert cell['shots'] == n and cell['goals'] == goals
    assert math.isclose(cell['predicted_goal_sum'], predicted, abs_tol=1e-12)
    if n:
        assert math.isclose(cell['mean_predicted_probability'], predicted / n)
        assert math.isclose(cell['observed_goal_fraction'], goals / n, abs_tol=1e-12)
    else:
        assert cell['mean_predicted_probability'] is None and cell['observed_goal_fraction'] is None
assert ids(binned_ids) == ids(expected_predictions)
summary = calibration['summary']
assert summary['shots'] == len(expected_predictions) == 114
assert summary['goals'] == sum(r['goal'] for r in expected_predictions) == 11
assert math.isclose(summary['predicted_goal_sum'], sum(r['predicted_probability'] for r in expected_predictions))
assert math.isclose(summary['mean_predicted_probability'], summary['predicted_goal_sum'] / summary['shots'])
assert math.isclose(summary['observed_goal_fraction'], summary['goals'] / summary['shots'])
assert sum(b['shots'] for b in calibration['bins']) == summary['shots']
assert sum(b['goals'] for b in calibration['bins']) == summary['goals']
assert math.isclose(sum(b['predicted_goal_sum'] for b in calibration['bins']), summary['predicted_goal_sum'])

# Lesson 27: a committed frozen model is checked on all other tournament fixtures.
protocol_path = ROOT / 'data/27_evaluation_protocol.json'
protocol = json.loads(protocol_path.read_text())
evaluation = read('27_frozen_evaluation_evidence.json')
assert evaluation['protocol_path'] == 'data/27_evaluation_protocol.json'
assert evaluation['protocol_sha256'] == hashlib.sha256(protocol_path.read_bytes()).hexdigest()
assert protocol['excluded_previously_used_match_ids'] == base['match_ids']
assert len(protocol['evaluation_match_ids']) == len(set(protocol['evaluation_match_ids'])) == 45
assert set(protocol['evaluation_match_ids']).isdisjoint(base['match_ids'])
assert [m['match_id'] for m in protocol['fixture_metadata']] == protocol['evaluation_match_ids']
assert protocol['no_refitting'] and protocol['no_ready_for_use_threshold']
assert protocol['training_shots'] == evaluation['training_shots_unchanged'] == 114
assert protocol['training_goals'] == 11 and protocol['selected_candidate'] == 'distance'
assert protocol['calibration_bin_edges'] == [0, 0.05, 0.10, 0.20, 1]
assert protocol['bootstrap'] == {'unit': 'whole match, paired for model and baseline', 'n_resamples': 5000,
                                'seed': 20261031, 'percentiles': [0.025, 0.975], 'percentile_method': 'linear interpolation'}
assert hashlib.sha256((ROOT / protocol['source_model_code']).read_bytes()).hexdigest() == protocol['source_model_code_sha256']
check_angle_fit(protocol['frozen_fit'], angle_train, ['distance_template_m'])
check_angle_fit(protocol['frozen_baseline_fit'], angle_train, [])
assert evaluation['evaluation_match_ids'] == protocol['evaluation_match_ids']
evaluation_rows = evaluation['shots']
assert len(evaluation_rows) == evaluation['evaluation_shots']
ids(evaluation_rows)
assert all(r['match_id'] in protocol['evaluation_match_ids'] for r in evaluation_rows)
assert set((r['match_id'], r['id']) for r in evaluation_rows).isdisjoint(ids(angle_rows))
assert evaluation['evaluation_goals'] == sum(r['goal'] for r in evaluation_rows)
for row in evaluation_rows:
    assert row['goal'] in [0, 1] and 0 <= row['x'] <= 120 and 0 <= row['y'] <= 80
    dx, lateral = (120 - row['x']) * 105 / 120, (row['y'] - 40) * 68 / 80
    assert math.isclose(row['distance_template_m'], math.hypot(dx, lateral))
    assert math.isclose(row['angle_radians'], math.atan2(7.32 * dx, dx * dx + lateral * lateral - 3.66 ** 2), abs_tol=1e-12)
    assert math.isclose(row['model_probability'], angle_prediction(protocol['frozen_fit'], row))
    assert math.isclose(row['baseline_probability'], angle_prediction(protocol['frozen_baseline_fit'], row))
    assert math.isclose(row['baseline_probability'], 11 / 114)
for name in ['model', 'baseline']:
    check_angle_scores(evaluation[f'{name}_metrics'], evaluation_rows, [r[f'{name}_probability'] for r in evaluation_rows])
for metric in ['log_loss', 'brier_score']:
    expected = evaluation['model_metrics'][metric] - evaluation['baseline_metrics'][metric]
    assert math.isclose(evaluation['model_minus_baseline'][metric], expected, abs_tol=1e-12)
assert [r['match_id'] for r in evaluation['match_summaries']] == protocol['evaluation_match_ids']
for saved in evaluation['match_summaries']:
    rows = [r for r in evaluation_rows if r['match_id'] == saved['match_id']]
    assert saved['shots'] == len(rows) and saved['goals'] == sum(r['goal'] for r in rows)
    for name in ['model', 'baseline']:
        squared, log_losses = [], []
        for row in rows:
            raw_p, y = row[f'{name}_probability'], row['goal']
            clipped = max(1e-12, min(1 - 1e-12, raw_p))
            squared.append((raw_p - y) ** 2)
            log_losses.append(-y * math.log(clipped) - (1 - y) * math.log(1 - clipped))
        assert math.isclose(saved[f'{name}_loss_sums']['brier_score'], sum(squared), abs_tol=1e-12)
        assert math.isclose(saved[f'{name}_loss_sums']['log_loss'], sum(log_losses), abs_tol=1e-12)
# Replay the paired match bootstrap from the frozen seed and aggregate losses.
rng = random.Random(protocol['bootstrap']['seed'])
match_summaries = evaluation['match_summaries']
replicates = {'log_loss': [], 'brier_score': []}
invalid = 0
for _ in range(protocol['bootstrap']['n_resamples']):
    draw = [match_summaries[rng.randrange(len(match_summaries))] for _ in match_summaries]
    n = sum(row['shots'] for row in draw)
    if not n:
        invalid += 1
        continue
    for metric in replicates:
        replicates[metric].append(sum(row['model_loss_sums'][metric] - row['baseline_loss_sums'][metric] for row in draw) / n)
assert evaluation['bootstrap_valid_draws'] == len(replicates['log_loss'])
assert evaluation['bootstrap_invalid_draws'] == invalid
for metric, values in replicates.items():
    ordered = sorted(values)
    for q, endpoint in zip(protocol['bootstrap']['percentiles'], evaluation['paired_match_bootstrap_intervals'][metric]):
        position = (len(ordered) - 1) * q
        fraction = position % 1
        expected = (1 - fraction) * ordered[math.floor(position)] + fraction * ordered[math.ceil(position)]
        assert math.isclose(endpoint, expected, abs_tol=1e-12)
# Rebuild fixed calibration bins from the new-fixture predictions.
assert len(evaluation['calibration_bins']) == 4
for j, cell in enumerate(evaluation['calibration_bins']):
    lower, upper = protocol['calibration_bin_edges'][j:j + 2]
    rows = [r for r in evaluation_rows if lower <= r['model_probability'] < upper or j == 3 and r['model_probability'] == 1]
    assert cell['bin_index'] == j and cell['lower_inclusive'] == lower and cell['upper'] == upper
    assert cell['upper_inclusive'] == (j == 3)
    assert cell['shot_ids'] == [{'match_id': r['match_id'], 'id': r['id']} for r in rows]
    assert cell['shots'] == len(rows) and cell['goals'] == sum(r['goal'] for r in rows)
    expected = sum(r['model_probability'] for r in rows)
    assert math.isclose(cell['predicted_goal_sum'], expected, abs_tol=1e-12)
    if rows:
        assert math.isclose(cell['mean_predicted_probability'], expected / len(rows))
        assert math.isclose(cell['observed_goal_fraction'], cell['goals'] / len(rows), abs_tol=1e-12)
    else:
        assert cell['mean_predicted_probability'] is None and cell['observed_goal_fraction'] is None
assert sum(r['shots'] for r in evaluation['calibration_bins']) == len(evaluation_rows)
assert sum(r['goals'] for r in evaluation['calibration_bins']) == evaluation['evaluation_goals']
excluded = evaluation['excluded_shots']
ids(excluded)
assert ids(excluded).isdisjoint(ids(evaluation_rows))
assert all(r['reason'] in ['shootout', 'penalty', 'missing_location', 'invalid_geometry'] for r in excluded)
assert dict(Counter(r['reason'] for r in excluded)) == evaluation['exclusion_counts']
raw_evaluation_checked = 0
assert [r['match_id'] for r in evaluation['raw_inputs']] == protocol['evaluation_match_ids']
for record in evaluation['raw_inputs']:
    mid = record['match_id']
    assert record['relative_path'] == f'data/cache_2019_events/{mid}.json'
    assert record['source_url'] == f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{mid}.json'
    path = ROOT / record['relative_path']
    if not path.exists():
        continue
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
    events = json.loads(path.read_text())
    fixture = next(m for m in protocol['fixture_metadata'] if m['match_id'] == mid)
    assert {e['team']['name'] for e in events} == {fixture['home_team'], fixture['away_team']}
    expected_included, expected_excluded = {}, {}
    for event in events:
        if event['type']['name'] != 'Shot':
            continue
        reason = None
        if event['period'] >= 5:
            reason = 'shootout'
        elif event['shot'].get('type', {}).get('name') == 'Penalty':
            reason = 'penalty'
        elif 'location' not in event or len(event['location']) < 2:
            reason = 'missing_location'
        else:
            x, y = event['location'][:2]
            if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in [x, y]) or not (0 <= x <= 120 and 0 <= y <= 80):
                reason = 'invalid_geometry'
            else:
                dx, lateral = (120 - x) * 105 / 120, (y - 40) * 68 / 80
                if dx == 0 and abs(dx * dx + lateral * lateral - 3.66 ** 2) < 1e-12:
                    reason = 'invalid_geometry'
        if reason:
            expected_excluded[event['id']] = reason
        else:
            expected_included[event['id']] = (event['location'][0], event['location'][1], int(event['shot']['outcome']['name'] == 'Goal'))
    actual = {r['id']: (r['x'], r['y'], r['goal']) for r in evaluation_rows if r['match_id'] == mid}
    assert actual == expected_included
    assert {r['id']: r['reason'] for r in excluded if r['match_id'] == mid} == expected_excluded
    raw_evaluation_checked += 1
metadata_path = ROOT / protocol['metadata_source']['relative_path']
if metadata_path.exists():
    assert hashlib.sha256(metadata_path.read_bytes()).hexdigest() == protocol['metadata_source']['sha256']
    metadata = json.loads(metadata_path.read_text())
    assert {m['match_id'] for m in metadata} - set(base['match_ids']) == set(protocol['evaluation_match_ids'])

# Lesson 28: describe training counts and audit, without excluding, evaluation distances.
support = read('28_distance_support_evidence.json')
assert support['sources'] == ['25_shot_angle_evidence.json', '27_evaluation_protocol.json', '27_frozen_evaluation_evidence.json']
assert support['protocol_sha256'] == evaluation['protocol_sha256']
low = min(r['distance_template_m'] for r in angle_train)
high_distance = max(r['distance_template_m'] for r in angle_train)
assert support['training_distance_range_template_m'] == [low, high_distance]
assert support['training_shots'] == len(angle_train) == 114
assert support['evaluation_shots'] == len(evaluation_rows) == 1131

def check_support_group(saved, rows):
    n, goals = len(rows), sum(r['goal'] for r in rows)
    assert saved['shots'] == n and saved['goals'] == goals
    assert saved['shot_ids'] == [{'match_id': r['match_id'], 'id': r['id']} for r in rows]
    if n:
        assert math.isclose(saved['observed_goal_fraction'], goals / n, abs_tol=1e-12)
        assert math.isclose(saved['mean_distance_template_m'], sum(r['distance_template_m'] for r in rows) / n)
        assert saved['min_distance_template_m'] == min(r['distance_template_m'] for r in rows)
        assert saved['max_distance_template_m'] == max(r['distance_template_m'] for r in rows)
    else:
        assert all(saved[key] is None for key in ['observed_goal_fraction', 'mean_distance_template_m',
                                                 'min_distance_template_m', 'max_distance_template_m'])
assert len(support['training_bands']) == 4
training_partition = []
for band, lower, upper in zip(support['training_bands'], [0, 10, 20, 30], [10, 20, 30, None]):
    assert band['lower_inclusive_m'] == lower and band['upper_exclusive_m'] == upper
    rows = [r for r in angle_train if r['distance_template_m'] >= lower and (upper is None or r['distance_template_m'] < upper)]
    check_support_group(band, rows)
    training_partition.extend(rows)
assert ids(training_partition) == ids(angle_train)
assert [g['category'] for g in support['evaluation_coverage']] == ['Closer than training range', 'Inside training range', 'Farther than training range']
partitions = [[r for r in evaluation_rows if r['distance_template_m'] < low],
              [r for r in evaluation_rows if low <= r['distance_template_m'] <= high_distance],
              [r for r in evaluation_rows if r['distance_template_m'] > high_distance]]
for group, rows in zip(support['evaluation_coverage'], partitions):
    check_support_group(group, rows)
assert ids([r for rows in partitions for r in rows]) == ids(evaluation_rows)
assert [r['distance_template_m'] for r in support['example_predictions']] == [10, 20, 30]
for example in support['example_predictions']:
    assert math.isclose(example['frozen_probability'], angle_prediction(protocol['frozen_fit'], example))
assert math.isclose(support['frozen_baseline_probability'], 11 / 114)

assert {p['match_id'] for p in manifest['raw_inputs']} == set(base['match_ids'])
checked = 0
for record in manifest['raw_inputs']:
    path = ROOT / record['relative_path']
    if path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], 'Raw input changed: ' + path.name
        checked += 1
print('PASS: passing evidence, xG, calibration and the frozen 45-fixture evaluation reconcile.')
print(f'Unused-fixture shot records and raw hashes checked: {raw_evaluation_checked}/45 matches.')
print(f'Pre-pass scores independently reconstructed from raw events: {raw_score_matches}/7 matches.')
print(f'Location denominators independently reconstructed from raw events: {raw_context_matches}/7 matches.')
print(f'Time-window selections independently reconstructed from raw events: {raw_window_matches}/7 matches.')
print(f'Raw input hashes checked locally: {checked}/7 (cache is optional and not committed).')

# Lesson 31 is a visual extension of the same match ledger, not a new model.
location = json.loads((ROOT / 'data/31_shot_location_evidence.json').read_text())
match_path = ROOT / location['source_path']
assert hashlib.sha256(match_path.read_bytes()).hexdigest() == location['source_sha256']
match = json.loads(match_path.read_text())
assert location['fixture'] == match['fixture']
timeline = json.loads((ROOT / 'data/30_cumulative_xg_evidence.json').read_text())
expected_keys = {(r['team'], h) for r in match['teams'] for h in (1, 2)}
assert len(location['panels']) == len(expected_keys)
assert {(p['team'], p['period']) for p in location['panels']} == expected_keys
seen = []
for panel in location['panels']:
    rows = [r for r in match['shots'] if r['team'] == panel['team'] and r['period'] == panel['period']]
    assert panel['shot_ids'] == [r['id'] for r in rows]
    seen.extend(panel['shot_ids'])
    assert panel['shots'] == len(rows)
    assert all(60 <= r['x'] <= 120 and 0 <= r['y'] <= 80 for r in rows)
    assert math.isclose(panel['model_npxg'], sum(r['model_probability'] for r in rows))
    if rows:
        assert math.isclose(panel['mean_distance_template_m'], sum(r['distance_template_m'] for r in rows) / len(rows))
    else:
        assert panel['mean_distance_template_m'] is None
    group = next(r for r in timeline['timelines'] if r['team'] == panel['team'] and r['period'] == panel['period'])
    assert math.isclose(panel['model_npxg'], group['half_npxg'], abs_tol=1e-12)
assert len(seen) == len(set(seen)) == len(match['shots'])
assert set(seen) == {r['id'] for r in match['shots']}
print('PASS: shot-map membership, display bounds and half summaries reconcile with the existing ledger and timeline.')

volume_quality = json.loads((ROOT / 'data/32_volume_quality_evidence.json').read_text())
assert volume_quality['source_path'] == location['source_path']
assert volume_quality['source_sha256'] == location['source_sha256']
assert volume_quality['fixture'] == match['fixture']
assert [r['team'] for r in volume_quality['comparisons']] == [r['team'] for r in match['teams']]
for comparison in volume_quality['comparisons']:
    for half, key in [(1, 'first_half'), (2, 'second_half')]:
        panel = next(r for r in location['panels'] if r['team'] == comparison['team'] and r['period'] == half)
        group = comparison[key]
        assert group['shots'] == panel['shots']
        assert group['shot_ids'] == panel['shot_ids']
        assert math.isclose(group['model_npxg'], panel['model_npxg'])
        assert math.isclose(group['model_npxg_per_shot'], panel['model_npxg'] / panel['shots'])
    first, second = comparison['first_half'], comparison['second_half']
    for field, value in [('second_over_first_shot_ratio', second['shots'] / first['shots']),
                         ('second_over_first_mean_quality_ratio', second['model_npxg_per_shot'] / first['model_npxg_per_shot']),
                         ('second_over_first_total_npxg_ratio', second['model_npxg'] / first['model_npxg'])]:
        assert math.isclose(comparison[field], value)
    assert math.isclose(comparison['second_over_first_shot_ratio'] * comparison['second_over_first_mean_quality_ratio'], comparison['second_over_first_total_npxg_ratio'])
print('PASS: volume-quality factors reconcile to the same half-specific shots and xG.')

body = json.loads((ROOT / 'data/33_body_part_evidence.json').read_text())
assert body['source_path'] == location['source_path']
assert body['source_sha256'] == location['source_sha256']
assert body['fixture'] == match['fixture']
assert body['raw_input'] == match['raw_input']
assert len(body['shots']) == len(match['shots'])
for tagged, original in zip(body['shots'], match['shots']):
    assert {k: v for k, v in tagged.items() if k != 'body_part'} == original
assert len(body['panels']) == 4
assert {(r['team'], r['period']) for r in body['panels']} == expected_keys
for panel in body['panels']:
    rows = [r for r in body['shots'] if r['team'] == panel['team'] and r['period'] == panel['period']]
    assert panel['total_shots'] == len(rows)
    assert [g['category'] for g in panel['groups']] == ['Foot', 'Head', 'Other / unknown']
    for group in panel['groups']:
        selected = [r for r in rows if ('Foot' if r['body_part'] in ('Left Foot', 'Right Foot') else 'Head' if r['body_part'] == 'Head' else 'Other / unknown') == group['category']]
        assert group['shot_ids'] == [r['id'] for r in selected]
        assert group['shots'] == len(selected)
        assert group['shot_goals'] == sum(r['goal'] for r in selected)
        total = sum(r['model_probability'] for r in selected)
        assert math.isclose(group['model_npxg'], total, abs_tol=1e-12)
        assert math.isclose(group['share_of_half_shots'], len(selected) / len(rows))
        if selected:
            assert math.isclose(group['mean_model_npxg'], total / len(selected))
        else:
            assert group['mean_model_npxg'] is None
raw_path = ROOT / body['raw_input']['relative_path']
if raw_path.exists():
    assert hashlib.sha256(raw_path.read_bytes()).hexdigest() == body['raw_input']['sha256']
    raw_events = {r['id']: r for r in json.loads(raw_path.read_text())}
    for row in body['shots']:
        assert row['body_part'] == raw_events[row['id']]['shot'].get('body_part', {}).get('name')
print('PASS: body-part tags, group membership and unchanged probabilities reconcile.')

header = json.loads((ROOT / 'data/34_header_assists_evidence.json').read_text())
header_source_path = ROOT / header['source_path']
assert header['source_path'] == 'data/33_body_part_evidence.json'
assert hashlib.sha256(header_source_path.read_bytes()).hexdigest() == header['source_sha256']
assert header['fixture'] == body['fixture']
assert header['raw_input'] == body['raw_input']
expected_headers = [r for r in body['shots'] if r['body_part'] == 'Head']
assert [r['shot_id'] for r in header['headers']] == [r['id'] for r in expected_headers]
for row, original in zip(header['headers'], expected_headers):
    assert (row['team'], row['period'], row['minute'], row['second']) == (original['team'], original['period'], original['minute'], original['second'])
    assert row['shot_location'][:2] == [original['x'], original['y']]
    assert row['model_probability_unchanged'] == original['model_probability']
    assert (row['shot_outcome'] == 'Goal') == bool(original['goal'])
    assert row['link_status'] == 'Verified reciprocal link'
    assert row['pass']['assisted_shot_id'] == row['shot_id']
    if raw_path.exists():
        shot_event = raw_events[row['shot_id']]
        pass_event = raw_events[shot_event['shot']['key_pass_id']]
        p = pass_event['pass']
        assert pass_event['type']['name'] == 'Pass'
        assert pass_event['index'] < shot_event['index']
        assert pass_event['team']['id'] == shot_event['team']['id']
        assert pass_event['period'] == shot_event['period']
        assert pass_event['possession'] == shot_event['possession']
        assert row['shooter'] == shot_event['player']['name']
        assert row['shot_type'] == shot_event['shot']['type']['name']
        assert row['play_pattern'] == shot_event['play_pattern']['name']
        assert row['pass'] == {'id': pass_event['id'], 'passer': pass_event['player']['name'],
            'minute': pass_event['minute'], 'second': pass_event['second'], 'start': pass_event['location'],
            'end': p['end_location'], 'type': p.get('type', {}).get('name'), 'cross_flag': p.get('cross'),
            'height': p.get('height', {}).get('name'), 'assisted_shot_id': p['assisted_shot_id']}
print('PASS: header identities, reciprocal assisting-pass links and raw context reconcile.')

corner = json.loads((ROOT / 'data/35_corner_delivery_evidence.json').read_text())
assert corner['source_path'] == location['source_path']
assert corner['source_sha256'] == location['source_sha256']
assert corner['fixture'] == match['fixture']
assert corner['raw_input'] == match['raw_input']
corner_rows = corner['corner_deliveries']
assert len({r['id'] for r in corner_rows}) == len(corner_rows)
assert [r['team'] for r in corner['teams']] == [r['team'] for r in match['teams']]
for team in corner['teams']:
    team_rows = [r for r in corner_rows if r['team'] == team['team']]
    assert [h['period'] for h in team['halves']] == [1, 2]
    for summary, selected in [(team, team_rows)] + [(h, [r for r in team_rows if r['period'] == h['period']]) for h in team['halves']]:
        n = len(selected)
        linked = sum(r['link_status'] == 'Verified reciprocal link' for r in selected)
        goals = sum(r['linked_shot_goal'] is True for r in selected)
        assert summary['delivery_ids'] == [r['id'] for r in selected]
        assert (summary['deliveries'], summary['direct_linked_shots'], summary['direct_linked_goals']) == (n, linked, goals)
        assert 0 <= goals <= linked <= n
        for key, count in [('recorded_direct_shot_link_rate', linked), ('recorded_direct_goal_link_rate', goals)]:
            if n:
                assert math.isclose(summary[key], count / n)
            else:
                assert summary[key] is None
for row in corner_rows:
    assert row['team'] in {r['team'] for r in match['teams']}
    if row['assisted_shot_id']:
        assert row['link_status'] == 'Verified reciprocal link'
        assert row['linked_shot_goal'] in (True, False)
    else:
        assert row['link_status'] == 'No assisted-shot link recorded'
        assert row['linked_shot_goal'] is None
if raw_path.exists():
    raw_corners = [r for r in raw_events.values() if r['period'] in (1, 2) and r['type']['name'] == 'Pass' and r['pass'].get('type', {}).get('name') == 'Corner']
    assert [r['id'] for r in corner_rows] == [r['id'] for r in raw_corners]
    for row, event in zip(corner_rows, raw_corners):
        assert row['team'] == event['team']['name']
        assert row['passer'] == event['player']['name']
        for key in ['period', 'minute', 'second']:
            assert row[key] == event[key]
        assert row['pass_outcome'] == event['pass'].get('outcome', {}).get('name')
        assert row['assisted_shot_id'] == event['pass'].get('assisted_shot_id')
        if row['assisted_shot_id']:
            shot = raw_events[row['assisted_shot_id']]
            assert shot['type']['name'] == 'Shot'
            assert shot['shot']['key_pass_id'] == row['id']
            assert shot['team']['id'] == event['team']['id']
            assert shot['period'] == event['period']
            assert shot['possession'] == event['possession']
            assert shot['index'] > event['index']
            assert row['linked_shot_goal'] == (shot['shot']['outcome']['name'] == 'Goal')
print('PASS: every corner delivery, direct shot links and explicit rate denominators reconcile.')

phase = json.loads((ROOT / 'data/36_corner_phase_evidence.json').read_text())
assert phase['source_path'] == 'data/35_corner_delivery_evidence.json'
assert hashlib.sha256((ROOT / phase['source_path']).read_bytes()).hexdigest() == phase['source_sha256']
phase_protocol_path = ROOT / phase['protocol_path']
assert hashlib.sha256(phase_protocol_path.read_bytes()).hexdigest() == phase['protocol_sha256']
phase_protocol = json.loads(phase_protocol_path.read_text())
assert phase_protocol['maximum_seconds_inclusive'] == 15
assert phase['raw_input'] == corner['raw_input']
assert phase['fixture'] == corner['fixture']
assert [r['corner_id'] for r in phase['phases']] == [r['id'] for r in corner_rows]
phase_shot_source = {r['id']: r for r in match['shots']}
assigned = []
for row, delivery in zip(phase['phases'], corner_rows):
    for key in ['team', 'period', 'minute', 'second']:
        assert row[key] == delivery[key]
    assert row['direct_shot_id'] == delivery['assisted_shot_id']
    for shot in row['shots']:
        original = phase_shot_source[shot['shot_id']]
        assert original['team'] == row['team']
        assert original['period'] == row['period']
        assert 0 <= shot['elapsed_seconds'] <= 15
        assert shot['goal'] == original['goal']
        assert shot['model_probability'] == original['model_probability']
        assigned.append(shot['shot_id'])
assert len(assigned) == len(set(assigned))
assert [r['team'] for r in phase['teams']] == [r['team'] for r in corner['teams']]
for team, direct in zip(phase['teams'], corner['teams']):
    rows = [r for r in phase['phases'] if r['team'] == team['team']]
    with_shot = sum(bool(r['shots']) for r in rows)
    assert team['deliveries'] == direct['deliveries'] == len(rows)
    assert team['direct_linked_shots'] == direct['direct_linked_shots']
    assert team['direct_shot_link_rate'] == direct['recorded_direct_shot_link_rate']
    assert team['corners_with_phase_shot'] == with_shot
    assert team['phase_shots'] == sum(len(r['shots']) for r in rows)
    assert team['phase_shot_goals'] == sum(s['goal'] for r in rows for s in r['shots'])
    assert math.isclose(team['phase_shot_rate'], with_shot / len(rows))
if raw_path.exists():
    ordered_raw = sorted(raw_events.values(), key=lambda e: e['index'])
    def phase_ms(e):
        h, m, s = e['timestamp'].split(':')
        return int(h) * 3600000 + int(m) * 60000 + round(float(s) * 1000)
    for row in phase['phases']:
        start_event = raw_events[row['corner_id']]
        expected_shots = []
        reason = 'End of available events'
        for event in ordered_raw:
            if event['index'] <= start_event['index']:
                continue
            if event['period'] != start_event['period']:
                reason = 'Period changed'; break
            if event['possession'] != start_event['possession']:
                reason = 'Possession changed'; break
            elapsed = (phase_ms(event) - phase_ms(start_event)) / 1000
            assert elapsed >= 0
            if elapsed > 15:
                reason = 'Time limit'; break
            if event['type']['name'] == 'Pass' and event['pass'].get('type', {}).get('name') in phase_protocol['restart_pass_types']:
                reason = 'New restart'; break
            if event['id'] in phase_shot_source and event['team']['id'] == start_event['team']['id']:
                source_shot = phase_shot_source[event['id']]
                expected_shots.append({'shot_id': event['id'], 'elapsed_seconds': elapsed, 'goal': source_shot['goal'], 'model_probability': source_shot['model_probability']})
            if event['type']['name'] == 'Shot' and event['shot']['outcome']['name'] == 'Goal':
                reason = 'Goal'; break
            if event['type']['name'] in ('Own Goal Against', 'Own Goal For'):
                reason = 'Own goal'; break
        assert row['shots'] == expected_shots
        assert row['stop_reason'] == reason
print('PASS: corner-phase membership, unique shot assignments, boundaries and rates reconcile.')

window = json.loads((ROOT / 'data/37_corner_window_evidence.json').read_text())
assert window['source_path'] == 'data/36_corner_phase_evidence.json'
assert hashlib.sha256((ROOT / window['source_path']).read_bytes()).hexdigest() == window['source_sha256']
window_protocol_path = ROOT / window['protocol_path']
assert hashlib.sha256(window_protocol_path.read_bytes()).hexdigest() == window['protocol_sha256']
window_protocol = json.loads(window_protocol_path.read_text())
assert window_protocol['windows_seconds_inclusive'] == [5, 10, 15, 20]
assert window['fixture'] == phase['fixture']
assert [r['window_seconds'] for r in window['results']] == window_protocol['windows_seconds_inclusive']
previous_ids = set()
if raw_path.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location('audit_phase_windows', ROOT / '36_corner_phase_analysis.py')
    window_helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(window_helper)
for result in window['results']:
    limit = result['window_seconds']
    assert [r['corner_id'] for r in result['phases']] == [r['corner_id'] for r in phase['phases']]
    current_ids = []
    for row, reference_phase in zip(result['phases'], phase['phases']):
        assert row['team'] == reference_phase['team']
        for shot in row['shots']:
            original = phase_shot_source[shot['shot_id']]
            assert original['team'] == row['team']
            assert shot['goal'] == original['goal']
            assert shot['model_probability'] == original['model_probability']
            assert 0 <= shot['elapsed_seconds'] <= limit
            current_ids.append(shot['shot_id'])
        if limit == 15:
            assert row['shots'] == reference_phase['shots']
            assert row['stop_reason'] == reference_phase['stop_reason']
        if raw_path.exists():
            rules = dict(phase_protocol, maximum_seconds_inclusive=limit)
            replay = window_helper.phase_after(raw_events[row['corner_id']], ordered_raw, phase_shot_source, rules)
            assert row['shots'] == replay['shots']
            assert row['stop_reason'] == replay['stop_reason']
    assert len(current_ids) == len(set(current_ids))
    assert previous_ids <= set(current_ids)
    previous_ids = set(current_ids)
    assert [r['team'] for r in result['teams']] == [r['team'] for r in phase['teams']]
    for summary, original_team in zip(result['teams'], phase['teams']):
        rows = [r for r in result['phases'] if r['team'] == summary['team']]
        count = sum(bool(r['shots']) for r in rows)
        assert summary['deliveries'] == original_team['deliveries'] == len(rows)
        assert summary['corners_with_shot'] == count
        assert summary['phase_shots'] == sum(len(r['shots']) for r in rows)
        assert summary['phase_shot_goals'] == sum(s['goal'] for r in rows for s in r['shots'])
        assert math.isclose(summary['corner_shot_rate'], count / len(rows))
print('PASS: all corner-window definitions, nested shot memberships and reference-window results reconcile.')

study = json.loads((ROOT / 'data/38_france_corner_study_evidence.json').read_text())
study_protocol_path = ROOT / study['protocol_path']
assert hashlib.sha256(study_protocol_path.read_bytes()).hexdigest() == study['protocol_sha256']
study_protocol = json.loads(study_protocol_path.read_text())
manifest_path = ROOT / study['raw_manifest_path']
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == study['raw_manifest_sha256']
study_manifest = json.loads(manifest_path.read_text())
fixture_metadata = json.loads((ROOT / 'data/27_evaluation_protocol.json').read_text())['fixture_metadata']
expected_fixtures = [r for r in fixture_metadata if study_protocol['team'] in (r['home_team'], r['away_team'])]
assert study_protocol['fixtures'] == expected_fixtures
assert [r['fixture'] for r in study['matches']] == expected_fixtures
assert study_protocol['periods_included'] == [1, 2, 3, 4]
assert study_protocol['maximum_seconds_inclusive'] == 15
import importlib.util
spec = importlib.util.spec_from_file_location('tournament_phase_audit', ROOT / '36_corner_phase_analysis.py')
study_helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(study_helper)
for record in study['matches']:
    assert record['raw_input'] in study_manifest['raw_inputs']
    assert record['raw_input']['match_id'] == record['fixture']['match_id']
    fixture = record['fixture']
    assert record['opponent'] == (fixture['away_team'] if fixture['home_team'] == study_protocol['team'] else fixture['home_team'])
    rows = record['phases']
    assert len({r['corner_id'] for r in rows}) == record['deliveries'] == len(rows)
    shot_ids = [s['shot_id'] for r in rows for s in r['shots']]
    assert len(set(shot_ids)) == len(shot_ids) == record['phase_shots']
    assert record['corners_with_phase_shot'] == sum(bool(r['shots']) for r in rows)
    assert record['phase_shot_goals'] == sum(s['goal'] for r in rows for s in r['shots'])
    assert record['direct_linked_shots'] == sum(r['direct_shot_id'] is not None for r in rows)
    assert record['extra_time_deliveries'] == sum(r['period'] in (3, 4) for r in rows)
    assert math.isclose(record['phase_shot_rate'], record['corners_with_phase_shot'] / record['deliveries'])
    cached = ROOT / record['raw_input']['relative_path']
    if cached.exists():
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == record['raw_input']['sha256']
        events = sorted(json.loads(cached.read_text()), key=lambda r: r['index'])
        event_lookup = {r['id']: r for r in events}
        corners_raw = [r for r in events if r['type']['name'] == 'Pass' and r['period'] in study_protocol['periods_included'] and r['team']['name'] == study_protocol['team'] and r['pass'].get('type', {}).get('name') == 'Corner']
        assert [r['corner_id'] for r in rows] == [r['id'] for r in corners_raw]
        included = {r['id']: {'goal': int(r['shot']['outcome']['name'] == 'Goal'), 'model_probability': None} for r in events if r['type']['name'] == 'Shot' and r['period'] in study_protocol['periods_included'] and r['team']['name'] == study_protocol['team'] and r['shot']['type']['name'] != 'Penalty'}
        for row, event in zip(rows, corners_raw):
            for key in ['period', 'minute', 'second']:
                assert row[key] == event[key]
            assert row['direct_shot_id'] == event['pass'].get('assisted_shot_id')
            replay = study_helper.phase_after(event, events, included, study_protocol)
            for shot in replay['shots']:
                del shot['model_probability']
            assert row['shots'] == replay['shots']
            assert row['stop_reason'] == replay['stop_reason']
            if row['direct_shot_id']:
                shot_event = event_lookup[row['direct_shot_id']]
                assert shot_event['type']['name'] == 'Shot'
                assert shot_event['shot']['key_pass_id'] == event['id']
                assert shot_event['team']['id'] == event['team']['id']
                assert shot_event['period'] == event['period']
                assert shot_event['possession'] == event['possession']
                assert shot_event['index'] > event['index']
pooled = study['pooled']
assert pooled['matches'] == len(study['matches'])
for field in ['deliveries', 'corners_with_phase_shot', 'phase_shots', 'phase_shot_goals']:
    assert pooled[field] == sum(r[field] for r in study['matches'])
assert math.isclose(pooled['phase_shot_rate'], pooled['corners_with_phase_shot'] / pooled['deliveries'])
original_fixture = next(r for r in study['matches'] if r['fixture']['match_id'] == phase['fixture']['match_id'])
assert [[s['shot_id'] for s in r['shots']] for r in original_fixture['phases']] == [[s['shot_id'] for s in r['shots']] for r in phase['phases'] if r['team'] == study_protocol['team']]
print('PASS: five-fixture France selection, corner-phase replay, extra time and pooled delivery rates reconcile.')

profiles = json.loads((ROOT / 'data/39_corner_delivery_profiles_evidence.json').read_text())
assert profiles['source_path'] == 'data/38_france_corner_study_evidence.json'
assert hashlib.sha256((ROOT / profiles['source_path']).read_bytes()).hexdigest() == profiles['source_sha256']
profile_rows = profiles['deliveries']
expected_profile_keys = [(m['fixture']['match_id'], p['corner_id']) for m in study['matches'] for p in m['phases']]
assert [(r['match_id'], r['corner_id']) for r in profile_rows] == expected_profile_keys
assert len(set(expected_profile_keys)) == len(expected_profile_keys)
category_labels = ['Inswinging', 'Outswinging', 'Straight', 'Other / unrecorded']
assert [g['category'] for g in profiles['groups']] == category_labels
for record in study['matches']:
    selected = [r for r in profile_rows if r['match_id'] == record['fixture']['match_id']]
    for row, phase_row in zip(selected, record['phases']):
        assert row['opponent'] == record['opponent']
        assert row['phase_has_shot'] == bool(phase_row['shots'])
        assert row['phase_shots'] == len(phase_row['shots'])
        assert row['phase_shot_goals'] == sum(s['goal'] for s in phase_row['shots'])
        assert row['category'] == (row['raw_technique'] if row['raw_technique'] in category_labels[:3] else category_labels[3])
    cached = ROOT / record['raw_input']['relative_path']
    if cached.exists():
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == record['raw_input']['sha256']
        events_by_id = {r['id']: r for r in json.loads(cached.read_text())}
        for row in selected:
            event = events_by_id[row['corner_id']]
            assert row['raw_technique'] == event['pass'].get('technique', {}).get('name')
            assert row['passer'] == event['player']['name']
for group in profiles['groups']:
    rows = [r for r in profile_rows if r['category'] == group['category']]
    assert group['corner_keys'] == [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in rows]
    assert group['deliveries'] == len(rows)
    count = sum(r['phase_has_shot'] for r in rows)
    assert group['corners_with_phase_shot'] == count
    assert group['phase_shots'] == sum(r['phase_shots'] for r in rows)
    assert group['phase_shot_goals'] == sum(r['phase_shot_goals'] for r in rows)
    if rows:
        assert math.isclose(group['phase_shot_rate'], count / len(rows))
    else:
        assert group['phase_shot_rate'] is None
assert sum(g['deliveries'] for g in profiles['groups']) == pooled['deliveries']
assert sum(g['corners_with_phase_shot'] for g in profiles['groups']) == pooled['corners_with_phase_shot']
print('PASS: delivery-technique labels, unknown coverage and unchanged corner-phase groups reconcile.')

overlap = json.loads((ROOT / 'data/40_corner_taker_overlap_evidence.json').read_text())
assert overlap['source_path'] == 'data/39_corner_delivery_profiles_evidence.json'
assert hashlib.sha256((ROOT / overlap['source_path']).read_bytes()).hexdigest() == overlap['source_sha256']
assert [r['passer'] for r in overlap['takers']] == list(dict.fromkeys(r['passer'] for r in profile_rows))
assert [(r['match_id'], r['passer']) for r in overlap['taker_match_contexts']] == list(dict.fromkeys((r['match_id'], r['passer']) for r in profile_rows))
for collection, by_match in [(overlap['takers'], False), (overlap['taker_match_contexts'], True)]:
    for record in collection:
        rows = [r for r in profile_rows if r['passer'] == record['passer'] and (not by_match or r['match_id'] == record['match_id'])]
        if by_match:
            assert all(r['opponent'] == record['opponent'] for r in rows)
        assert [g['category'] for g in record['groups']] == category_labels
        for group in record['groups']:
            selected = [r for r in rows if r['category'] == group['category']]
            n = len(selected)
            count = sum(r['phase_has_shot'] for r in selected)
            assert group['corner_keys'] == [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in selected]
            assert group['deliveries'] == n
            assert group['corners_with_phase_shot'] == count
            assert group['phase_shots'] == sum(r['phase_shots'] for r in selected)
            assert group['phase_shot_goals'] == sum(r['phase_shot_goals'] for r in selected)
            if n:
                assert math.isclose(group['phase_shot_rate'], count / n)
            else:
                assert group['phase_shot_rate'] is None
        assert record['both_recorded_types'] == all(next(g['deliveries'] for g in record['groups'] if g['category'] == label) > 0 for label in ['Inswinging', 'Outswinging'])
assert overlap['contexts_with_both_types'] == sum(r['both_recorded_types'] for r in overlap['taker_match_contexts'])
for collection in [overlap['takers'], overlap['taker_match_contexts']]:
    assert sum(g['deliveries'] for r in collection for g in r['groups']) == pooled['deliveries']
    assert sum(g['corners_with_phase_shot'] for r in collection for g in r['groups']) == pooled['corners_with_phase_shot']
print('PASS: taker mixtures, match-context overlap, empty groups and original corner outcomes reconcile.')

side_audit = json.loads((ROOT / 'data/41_corner_side_evidence.json').read_text())
assert side_audit['source_path'] == 'data/39_corner_delivery_profiles_evidence.json'
assert hashlib.sha256((ROOT / side_audit['source_path']).read_bytes()).hexdigest() == side_audit['source_sha256']
side_rows = side_audit['deliveries']
assert len(side_rows) == len(profile_rows)
side_labels = ['Near y=0 touchline', 'Near y=80 touchline', 'Side unknown']
for row, original in zip(side_rows, profile_rows):
    assert {k: v for k, v in row.items() if k not in ('start_location', 'corner_side')} == original
    point = row['start_location']
    valid = isinstance(point, list) and len(point) >= 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in point[:2]) and 0 <= point[0] <= 120 and 0 <= point[1] <= 80
    expected = side_labels[0] if valid and point[1] < 40 else side_labels[1] if valid and point[1] > 40 else side_labels[2]
    assert row['corner_side'] == expected
for record in study['matches']:
    cached = ROOT / record['raw_input']['relative_path']
    if cached.exists():
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == record['raw_input']['sha256']
        lookup = {r['id']: r for r in json.loads(cached.read_text())}
        for row in side_rows:
            if row['match_id'] == record['fixture']['match_id']:
                assert row['start_location'] == lookup[row['corner_id']].get('location')
expected_taker_sides = [(name, side) for name in dict.fromkeys(r['passer'] for r in side_rows) for side in side_labels]
assert [(r['passer'], r['corner_side']) for r in side_audit['taker_sides']] == expected_taker_sides
for record in side_audit['taker_sides']:
    rows = [r for r in side_rows if r['passer'] == record['passer'] and r['corner_side'] == record['corner_side']]
    assert record['deliveries'] == len(rows)
    assert [g['category'] for g in record['groups']] == category_labels
    for group in record['groups']:
        selected = [r for r in rows if r['category'] == group['category']]
        n = len(selected); positive = sum(r['phase_has_shot'] for r in selected)
        assert group['corner_keys'] == [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in selected]
        assert group['deliveries'] == n
        assert group['corners_with_phase_shot'] == positive
        assert group['phase_shots'] == sum(r['phase_shots'] for r in selected)
        assert group['phase_shot_goals'] == sum(r['phase_shot_goals'] for r in selected)
        if n:
            assert math.isclose(group['phase_shot_rate'], positive / n)
        else:
            assert group['phase_shot_rate'] is None
    assert record['both_recorded_types'] == all(any(r['category'] == label for r in rows) for label in ['Inswinging', 'Outswinging'])
context_keys = list(dict.fromkeys((r['match_id'], r['passer'], r['corner_side']) for r in side_rows))
assert [(r['match_id'], r['passer'], r['corner_side']) for r in side_audit['taker_side_match_contexts']] == context_keys
for context in side_audit['taker_side_match_contexts']:
    rows = [r for r in side_rows if (r['match_id'], r['passer'], r['corner_side']) == (context['match_id'], context['passer'], context['corner_side'])]
    assert context['corner_keys'] == [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in rows]
    assert all(r['opponent'] == context['opponent'] for r in rows)
    assert context['both_recorded_types'] == all(any(r['category'] == label for r in rows) for label in ['Inswinging', 'Outswinging'])
assert side_audit['contexts_with_both_types'] == sum(r['both_recorded_types'] for r in side_audit['taker_side_match_contexts'])
assert sum(r['deliveries'] for r in side_audit['taker_sides']) == pooled['deliveries']
print('PASS: recorded corner sides, taker/side groups and exact-context comparison support reconcile.')

endpoint = json.loads((ROOT / 'data/42_corner_endpoint_evidence.json').read_text())
assert endpoint['source_path'] == 'data/41_corner_side_evidence.json'
assert hashlib.sha256((ROOT / endpoint['source_path']).read_bytes()).hexdigest() == endpoint['source_sha256']
endpoint_rows = endpoint['deliveries']
assert len(endpoint_rows) == len(side_rows)
zone_labels = ['Six-yard box', 'Rest of penalty area', 'Outside penalty area', 'Endpoint unknown']
assert [g['zone'] for g in endpoint['groups']] == zone_labels
for row, original in zip(endpoint_rows, side_rows):
    assert {k: v for k, v in row.items() if k not in ('end_location', 'pass_outcome', 'endpoint_zone')} == original
    point = row['end_location']
    finite = isinstance(point, list) and len(point) >= 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in point[:2])
    if not finite:
        expected_zone = zone_labels[3]
    elif 114 <= point[0] <= 120 and 30 <= point[1] <= 50:
        expected_zone = zone_labels[0]
    elif 102 <= point[0] <= 120 and 18 <= point[1] <= 62:
        expected_zone = zone_labels[1]
    else:
        expected_zone = zone_labels[2]
    assert row['endpoint_zone'] == expected_zone
for record in study['matches']:
    cached = ROOT / record['raw_input']['relative_path']
    if cached.exists():
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == record['raw_input']['sha256']
        lookup = {r['id']: r for r in json.loads(cached.read_text())}
        for row in endpoint_rows:
            if row['match_id'] == record['fixture']['match_id']:
                p = lookup[row['corner_id']]['pass']
                assert row['end_location'] == p.get('end_location')
                assert row['pass_outcome'] == p.get('outcome', {}).get('name')
for group in endpoint['groups']:
    rows = [r for r in endpoint_rows if r['endpoint_zone'] == group['zone']]
    assert group['corner_keys'] == [{'match_id': r['match_id'], 'corner_id': r['corner_id']} for r in rows]
    assert group['deliveries'] == len(rows)
    count = sum(r['phase_has_shot'] for r in rows)
    assert group['corners_with_phase_shot'] == count
    if rows:
        assert math.isclose(group['phase_shot_rate'], count / len(rows))
    else:
        assert group['phase_shot_rate'] is None
assert sum(g['deliveries'] for g in endpoint['groups']) == pooled['deliveries']
assert sum(g['corners_with_phase_shot'] for g in endpoint['groups']) == pooled['corners_with_phase_shot']
print('PASS: recorded corner endpoints, disjoint spatial bins and unchanged phase outcomes reconcile.')

review = json.loads((ROOT / 'data/43_corner_review_queue_evidence.json').read_text())
assert review['source_path'] == 'data/42_corner_endpoint_evidence.json'
assert hashlib.sha256((ROOT / review['source_path']).read_bytes()).hexdigest() == review['source_sha256']
review_protocol_path = ROOT / review['protocol_path']
assert hashlib.sha256(review_protocol_path.read_bytes()).hexdigest() == review['protocol_sha256']
review_protocol = json.loads(review_protocol_path.read_text())
assert review['questions'] == review_protocol['questions']
assert review['video_status'] == review_protocol['video_status']
assert review['scope'] == review_protocol['purpose']
candidates = review['candidate_deliveries']
assert len(candidates) == len(endpoint_rows)
fixtures_by_id = {r['fixture']['match_id']: r for r in study['matches']}
for row, original in zip(candidates, endpoint_rows):
    assert {k: v for k, v in row.items() if k not in ('match_date', 'event_index', 'period', 'minute', 'second', 'event_timestamp')} == original
    match_record = fixtures_by_id[row['match_id']]
    assert row['match_date'] == match_record['fixture']['match_date']
    cached = ROOT / match_record['raw_input']['relative_path']
    if cached.exists():
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == match_record['raw_input']['sha256']
        lookup = {r['id']: r for r in json.loads(cached.read_text())}
        event = lookup[row['corner_id']]
        assert row['event_index'] == event['index']
        assert row['event_timestamp'] == event['timestamp']
        for key in ['period', 'minute', 'second']:
            assert row[key] == event[key]
expected_cells = [(zone, status) for zone in review_protocol['zones'] for status in review_protocol['phase_outcome_order']]
assert [(r['endpoint_zone'], r['phase_has_shot']) for r in review['review_queue']] == expected_cells
used_matches = set()
selected_keys = []
ordered = sorted(candidates, key=lambda r: (r['match_date'], r['match_id'], r['event_index']))
for cell in review['review_queue']:
    eligible = [r for r in ordered if r['endpoint_zone'] == cell['endpoint_zone'] and r['phase_has_shot'] == cell['phase_has_shot']]
    preferred = [r for r in eligible if r['match_id'] not in used_matches]
    expected_example = (preferred or eligible)[0] if eligible else None
    assert cell['example'] == expected_example
    if expected_example:
        used_matches.add(expected_example['match_id'])
        selected_keys.append((expected_example['match_id'], expected_example['corner_id']))
assert len(set(selected_keys)) == len(selected_keys)
print('PASS: review queue candidates, source timing, deliberate example selection and unreviewed status reconcile.')

xt = json.loads((ROOT / 'data/44_first_xt_evidence.json').read_text())
assert xt['source_path'] == 'data/38_france_corner_study_evidence.json'
assert hashlib.sha256((ROOT / xt['source_path']).read_bytes()).hexdigest() == xt['source_sha256']
assert xt['raw_inputs'] == [m['raw_input'] for m in study['matches']]
assert xt['grid'] == {'nx': 6, 'ny': 4, 'row_direction': 'y=0 to y=80', 'attack_direction': 'x=0 to x=120'}
def xt_cell(point):
    if not isinstance(point, list) or len(point) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in point[:2]):
        return None
    x, y = point[:2]
    return min(int(y / 20), 3) * 6 + min(int(x / 20), 5) if 0 <= x <= 120 and 0 <= y <= 80 else None
actions = xt['actions']
assert len({(r['match_id'], r['id']) for r in actions}) == len(actions)
counts = [0] * 24; goals = [0] * 24; transition_counts = [[0] * 24 for _ in range(24)]
for row in actions:
    i = row['start_cell']; counts[i] += 1; goals[i] += row['goal']
    assert i == xt_cell(row['start']) and i is not None
    assert row['end_cell'] == xt_cell(row['end'])
    assert row['type'] in ['Pass', 'Carry', 'Shot']
    assert row['goal'] in (0, 1)
    if row['type'] != 'Shot':
        assert row['goal'] == 0
    if row['successful_move']:
        assert row['type'] != 'Shot' and row['end_cell'] is not None
        transition_counts[i][row['end_cell']] += 1
model = xt['model']; values = model['zone_values']
assert model['action_counts'] == counts
assert model['goal_counts'] == goals
assert model['successful_move_counts'] == transition_counts
assert len(values) == 24 and all(0 <= v <= 1 for v in values)
for i in range(24):
    reward = goals[i] / counts[i] if counts[i] else 0
    assert math.isclose(model['immediate_goal_per_action'][i], reward, abs_tol=1e-15)
    for j in range(24):
        expected = transition_counts[i][j] / counts[i] if counts[i] else 0
        assert math.isclose(model['successful_transition_per_action'][i][j], expected, abs_tol=1e-15)
    assert reward + sum(model['successful_transition_per_action'][i]) <= 1 + 1e-12
residual = max(abs(values[i] - model['immediate_goal_per_action'][i] - sum(model['successful_transition_per_action'][i][j] * values[j] for j in range(24))) for i in range(24))
assert math.isclose(residual, model['fixed_point_residual'], abs_tol=1e-15) and residual < 1e-12
assert 1 <= model['iterations'] <= 10000 and model['max_update'] <= 1e-12
assert [r['label'] for r in xt['examples']] == ['Positive', 'Zero', 'Negative']
for example in xt['examples']:
    original = next(r for r in actions if (r['match_id'], r['id']) == (example['match_id'], example['id']))
    assert {k: v for k, v in example.items() if k not in ['label', 'start_xt', 'end_xt', 'added_xt']} == original
    assert original['type'] == 'Pass' and original['successful_move']
    assert example['start_xt'] == values[original['start_cell']]
    assert example['end_xt'] == values[original['end_cell']]
    assert math.isclose(example['added_xt'], example['end_xt'] - example['start_xt'], abs_tol=1e-15)
    sign = 'Positive' if example['added_xt'] > 1e-12 else 'Negative' if example['added_xt'] < -1e-12 else 'Zero'
    assert example['label'] == sign
all_raw_available = all((ROOT / record['relative_path']).exists() for record in xt['raw_inputs'])
if all_raw_available:
    reconstructed = []; excluded_counts = {}
    for record in xt['raw_inputs']:
        raw = ROOT / record['relative_path']
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == record['sha256']
        for event in sorted(json.loads(raw.read_text()), key=lambda r: r['index']):
            kind = event['type']['name']
            if kind not in ['Pass', 'Carry', 'Shot']:
                continue
            reason = None
            if event['period'] not in (1, 2, 3, 4): reason = 'shootout_or_other_period'
            elif event['team']['id'] != event['possession_team']['id']: reason = 'event_team_not_possession_team'
            elif kind == 'Pass' and event['pass'].get('type', {}).get('name') in ['Corner', 'Free Kick', 'Throw-in', 'Goal Kick', 'Kick Off']: reason = 'restart_pass'
            elif kind == 'Shot' and event['shot']['type']['name'] == 'Penalty': reason = 'penalty_shot'
            elif xt_cell(event.get('location')) is None: reason = 'invalid_or_outside_start'
            if reason:
                excluded_counts[reason] = excluded_counts.get(reason, 0) + 1; continue
            end = event.get(kind.lower(), {}).get('end_location') if kind != 'Shot' else None
            destination = xt_cell(end)
            reconstructed.append({'match_id': record['match_id'], 'id': event['id'], 'index': event['index'],
                'team': event['team']['name'], 'player': event['player']['name'], 'type': kind,
                'start': event['location'][:2], 'end': end[:2] if isinstance(end, list) else None,
                'start_cell': xt_cell(event['location']), 'end_cell': destination,
                'successful_move': kind != 'Shot' and destination is not None and (kind == 'Carry' or 'outcome' not in event['pass']),
                'goal': int(kind == 'Shot' and event['shot']['outcome']['name'] == 'Goal')})
    assert reconstructed == actions
    assert excluded_counts == xt['excluded_action_counts']
print('PASS: first xT action selection, failed-move denominators, transition counts, fixed point and pass examples reconcile.')

pass_value = json.loads((ROOT / 'data/45_failed_pass_value_evidence.json').read_text())
assert pass_value['source_path'] == 'data/44_first_xt_evidence.json'
assert hashlib.sha256((ROOT / pass_value['source_path']).read_bytes()).hexdigest() == pass_value['source_sha256']
source_passes = [r for r in xt['actions'] if r['type'] == 'Pass']
scored_passes = pass_value['passes']
assert len(scored_passes) == len(source_passes)
for row, original in zip(scored_passes, source_passes):
    assert {k: v for k, v in row.items() if k not in ['pass_outcome', 'start_xt', 'recorded_endpoint_xt', 'score_status', 'scenario_value']} == original
    start = values[row['start_cell']]
    end = values[row['end_cell']] if row['end_cell'] is not None else None
    assert row['start_xt'] == start and row['recorded_endpoint_xt'] == end
    if row['pass_outcome'] is None:
        status = 'Completed' if end is not None else 'Unscorable completed endpoint'
        score = end - start if end is not None else None
    elif row['pass_outcome'] in ['Incomplete', 'Out', 'Pass Offside']:
        status = 'Unsuccessful: assumed zero continuation'; score = -start
    else:
        status = 'Excluded unknown or injury-clearance outcome'; score = None
    assert row['score_status'] == status
    assert row['scenario_value'] == score
for key, rows in [('all_selected_teams_summary', scored_passes), ('france_summary', [r for r in scored_passes if r['team'] == "France Women's"])]:
    summary = pass_value[key]
    completed = [r for r in rows if r['score_status'] == 'Completed']
    failed = [r for r in rows if r['score_status'] == 'Unsuccessful: assumed zero continuation']
    assert summary['pass_attempts'] == len(rows)
    assert summary['scored_completed'] == len(completed)
    assert summary['scored_unsuccessful'] == len(failed)
    assert summary['excluded_or_unscorable'] == sum(r['scenario_value'] is None for r in rows)
    assert math.isclose(summary['completed_pass_xt_sum'], sum(r['scenario_value'] for r in completed))
    assert math.isclose(summary['assumed_failure_cost_sum'], sum(r['scenario_value'] for r in failed))
    assert math.isclose(summary['combined_scenario_sum'], summary['completed_pass_xt_sum'] + summary['assumed_failure_cost_sum'])
for record in xt['raw_inputs']:
    cached = ROOT / record['relative_path']
    if cached.exists():
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == record['sha256']
        lookup = {r['id']: r for r in json.loads(cached.read_text())}
        for row in scored_passes:
            if row['match_id'] == record['match_id']:
                assert row['pass_outcome'] == lookup[row['id']]['pass'].get('outcome', {}).get('name')
expected_failure_example = next((r for r in scored_passes if r['team'] == "France Women's" and r['pass_outcome'] in ['Incomplete', 'Out', 'Pass Offside'] and r['recorded_endpoint_xt'] is not None and r['recorded_endpoint_xt'] > r['start_xt']), None)
assert pass_value['illustrative_failed_pass'] == expected_failure_example
print('PASS: completed-pass xT, raw outcomes, excluded coverage and explicit failure-cost scenario reconcile.')

decision = json.loads((ROOT / 'data/46_pass_decision_evidence.json').read_text())
assert decision['source_path'] == 'data/44_first_xt_evidence.json'
assert hashlib.sha256((ROOT / decision['source_path']).read_bytes()).hexdigest() == decision['source_sha256']
assert (decision['start_cell'], decision['safe_destination_cell'], decision['risky_destination_cell']) == (8, 9, 11)
assert decision['start_value'] == values[8]
assert decision['safe_destination_value'] == values[9]
assert decision['risky_destination_value'] == values[11]
assert decision['assumed_failure_value'] == 0
assert [r['assumed_completion_probability'] for r in decision['options']] == [.9, .15, .2]
for i, option in enumerate(decision['options']):
    destination = values[9] if i == 0 else values[11]
    assert option['destination_value'] == destination
    p = option['assumed_completion_probability']
    expected = p * destination + (1 - p) * decision['assumed_failure_value'] - values[8]
    assert math.isclose(option['expected_value_change'], expected, abs_tol=1e-15)
assert math.isclose(decision['riskier_probability_to_break_even_with_start'], values[8] / values[11])
assert math.isclose(decision['riskier_probability_to_match_safer_option'], .9 * values[9] / values[11])
print('PASS: hypothetical pass-choice probabilities, fitted source values, expected changes and equality thresholds reconcile.')

completion = json.loads((ROOT / 'data/47_completion_model_evidence.json').read_text())
assert completion['source_path'] == 'data/45_failed_pass_value_evidence.json'
assert hashlib.sha256((ROOT / completion['source_path']).read_bytes()).hexdigest() == completion['source_sha256']
completion_protocol_path = ROOT / completion['protocol_path']
assert hashlib.sha256(completion_protocol_path.read_bytes()).hexdigest() == completion['protocol_sha256']
completion_protocol = json.loads(completion_protocol_path.read_text())
assert completion_protocol['training_match_ids'] == [r['fixture']['match_id'] for r in study['matches'][:4]]
assert completion_protocol['exploratory_check_match_ids'] == [study['matches'][4]['fixture']['match_id']]
train_ids = set(completion_protocol['training_match_ids']); check_ids = set(completion_protocol['exploratory_check_match_ids'])
assert not train_ids & check_ids
expected_completion_rows = []; expected_excluded = []
for row in scored_passes:
    outcome = row['pass_outcome']
    if outcome is not None and outcome not in ['Incomplete', 'Out', 'Pass Offside']:
        expected_excluded.append({'match_id': row['match_id'], 'id': row['id'], 'outcome': outcome}); continue
    expected_completion_rows.append({'match_id': row['match_id'], 'id': row['id'], 'team': row['team'], 'start_cell': row['start_cell'], 'completed': int(outcome is None), 'split': 'train' if row['match_id'] in train_ids else 'exploratory_check'})
assert completion['excluded'] == expected_excluded
assert [{k: v for k, v in r.items() if k not in ['zone_probability', 'baseline_probability']} for r in completion['passes']] == expected_completion_rows
fit_rows = [r for r in completion['passes'] if r['split'] == 'train']
check_rows = [r for r in completion['passes'] if r['split'] == 'exploratory_check']
assert {r['match_id'] for r in fit_rows} == train_ids
assert {r['match_id'] for r in check_rows} == check_ids
completion_fit = completion['model']
reference_rate = sum(r['completed'] for r in fit_rows) / len(fit_rows)
assert completion_fit['training_attempts'] == len(fit_rows)
assert completion_fit['training_completions'] == sum(r['completed'] for r in fit_rows)
assert completion_fit['global_training_rate'] == reference_rate
assert completion_fit['smoothing_strength'] == completion_protocol['smoothing_strength'] == 20
assert [z['cell'] for z in completion_fit['zones']] == list(range(24))
for zone in completion_fit['zones']:
    rows = [r for r in fit_rows if r['start_cell'] == zone['cell']]
    n = len(rows); successes = sum(r['completed'] for r in rows)
    assert zone['attempts'] == n and zone['completions'] == successes
    assert zone['raw_completion_rate'] == (successes / n if n else None)
    assert math.isclose(zone['smoothed_probability'], (successes + 20 * reference_rate) / (n + 20))
for row in completion['passes']:
    assert row['zone_probability'] == completion_fit['zones'][row['start_cell']]['smoothed_probability']
    assert row['baseline_probability'] == reference_rate
for metric_key, prediction_key in [('zone_model_check_metrics', 'zone_probability'), ('constant_baseline_check_metrics', 'baseline_probability')]:
    metrics = completion[metric_key]
    assert metrics['passes'] == len(check_rows)
    assert metrics['completions'] == sum(r['completed'] for r in check_rows)
    ll = sum(-(r['completed'] * math.log(r[prediction_key]) + (1 - r['completed']) * math.log1p(-r[prediction_key])) for r in check_rows) / len(check_rows)
    brier = sum((r[prediction_key] - r['completed']) ** 2 for r in check_rows) / len(check_rows)
    assert math.isclose(metrics['log_loss'], ll)
    assert math.isclose(metrics['brier_score'], brier)
print('PASS: training-only completion counts, excluded outcomes, smoothing, fixture split and probability errors reconcile.')

completion_cv = json.loads((ROOT / 'data/48_completion_match_cv_evidence.json').read_text())
assert completion_cv['source_path'] == 'data/47_completion_model_evidence.json'
assert hashlib.sha256((ROOT / completion_cv['source_path']).read_bytes()).hexdigest() == completion_cv['source_sha256']
cv_ids = completion_protocol['training_match_ids'] + completion_protocol['exploratory_check_match_ids']
assert completion_cv['match_ids'] == cv_ids
assert completion_cv['smoothing_strength'] == completion_fit['smoothing_strength']
assert [f['held_out_match_id'] for f in completion_cv['folds']] == cv_ids
cv_predictions = completion_cv['predictions']
original_completion = {(r['match_id'], r['id']): r for r in completion['passes']}
assert len(cv_predictions) == len(original_completion)
assert len({(r['match_id'], r['id']) for r in cv_predictions}) == len(original_completion)
assert {(r['match_id'], r['id']) for r in cv_predictions} == set(original_completion)
for row in cv_predictions:
    original = original_completion[(row['match_id'], row['id'])]
    assert {k: row[k] for k in ['match_id', 'id', 'team', 'start_cell', 'completed']} == {k: original[k] for k in ['match_id', 'id', 'team', 'start_cell', 'completed']}
for fold in completion_cv['folds']:
    omitted = fold['held_out_match_id']
    assert fold['training_match_ids'] == [m for m in cv_ids if m != omitted]
    train_rows = [r for r in completion['passes'] if r['match_id'] != omitted]
    predicted = [r for r in cv_predictions if r['match_id'] == omitted]
    fitted = fold['model']
    baseline = sum(r['completed'] for r in train_rows) / len(train_rows)
    assert fitted['training_attempts'] == len(train_rows)
    assert fitted['training_completions'] == sum(r['completed'] for r in train_rows)
    assert fitted['global_training_rate'] == baseline
    assert fitted['smoothing_strength'] == 20
    assert [z['cell'] for z in fitted['zones']] == list(range(24))
    for zone in fitted['zones']:
        selected = [r for r in train_rows if r['start_cell'] == zone['cell']]
        n = len(selected); count = sum(r['completed'] for r in selected)
        assert zone['attempts'] == n and zone['completions'] == count
        assert zone['raw_completion_rate'] == (count / n if n else None)
        assert math.isclose(zone['smoothed_probability'], (count + 20 * baseline) / (n + 20))
    for row in predicted:
        assert row['baseline_probability'] == baseline
        assert row['zone_probability'] == fitted['zones'][row['start_cell']]['smoothed_probability']
    for metrics_key, prediction_key in [('zone_metrics', 'zone_probability'), ('baseline_metrics', 'baseline_probability')]:
        metrics = fold[metrics_key]
        assert metrics['passes'] == len(predicted)
        assert metrics['completions'] == sum(r['completed'] for r in predicted)
        ll = sum(-(r['completed'] * math.log(r[prediction_key]) + (1-r['completed']) * math.log1p(-r[prediction_key])) for r in predicted) / len(predicted)
        bs = sum((r[prediction_key] - r['completed'])**2 for r in predicted) / len(predicted)
        assert math.isclose(metrics['log_loss'], ll) and math.isclose(metrics['brier_score'], bs)
    if omitted == completion_protocol['exploratory_check_match_ids'][0]:
        assert fitted == completion['model']
        assert fold['zone_metrics'] == completion['zone_model_check_metrics']
        assert fold['baseline_metrics'] == completion['constant_baseline_check_metrics']
for metrics_key, prediction_key in [('pooled_zone_metrics', 'zone_probability'), ('pooled_baseline_metrics', 'baseline_probability')]:
    metrics = completion_cv[metrics_key]
    assert metrics['passes'] == len(cv_predictions)
    assert metrics['completions'] == sum(r['completed'] for r in cv_predictions)
    ll = sum(-(r['completed'] * math.log(r[prediction_key]) + (1-r['completed']) * math.log1p(-r[prediction_key])) for r in cv_predictions) / len(cv_predictions)
    bs = sum((r[prediction_key] - r['completed'])**2 for r in cv_predictions) / len(cv_predictions)
    assert math.isclose(metrics['log_loss'], ll) and math.isclose(metrics['brier_score'], bs)
print('PASS: whole-match completion folds, fold-local baselines, unique predictions and pooled probability errors reconcile.')

completion_calibration = json.loads((ROOT / 'data/49_completion_calibration_evidence.json').read_text())
assert completion_calibration['source_path'] == 'data/48_completion_match_cv_evidence.json'
assert hashlib.sha256((ROOT / completion_calibration['source_path']).read_bytes()).hexdigest() == completion_calibration['source_sha256']
assert completion_calibration['bin_edges'] == [0, .6, .7, .8, .9, 1]
calibration_edges = completion_calibration['bin_edges']
assert len(completion_calibration['groups']) == len(calibration_edges) - 1
calibration_seen = []
def check_completion_group(group, rows):
    n = len(rows); count = sum(r['completed'] for r in rows); predicted_sum = sum(r['zone_probability'] for r in rows)
    assert group['passes'] == n and group['completions'] == count
    assert math.isclose(group['predicted_completion_sum'], predicted_sum, abs_tol=1e-12)
    assert group['pass_keys'] == [{'match_id': r['match_id'], 'id': r['id']} for r in rows]
    if n:
        assert math.isclose(group['mean_prediction'], predicted_sum / n)
        assert math.isclose(group['observed_completion_rate'], count / n)
    else:
        assert group['mean_prediction'] is None and group['observed_completion_rate'] is None
for i, group in enumerate(completion_calibration['groups']):
    lower, upper = calibration_edges[i], calibration_edges[i+1]
    assert (group['lower_inclusive'], group['upper'], group['upper_inclusive']) == (lower, upper, i == len(calibration_edges)-2)
    rows = [r for r in cv_predictions if lower <= r['zone_probability'] and (r['zone_probability'] < upper or (group['upper_inclusive'] and r['zone_probability'] == upper))]
    check_completion_group(group, rows)
    calibration_seen.extend((r['match_id'], r['id']) for r in rows)
assert len(calibration_seen) == len(set(calibration_seen)) == len(cv_predictions)
assert set(calibration_seen) == {(r['match_id'], r['id']) for r in cv_predictions}
check_completion_group(completion_calibration['overall'], cv_predictions)
print('PASS: completion calibration group boundaries, unique membership, prediction averages and actual frequencies reconcile.')

pressure = json.loads((ROOT / 'data/50_pressure_feature_evidence.json').read_text())
assert pressure['source_path'] == 'data/48_completion_match_cv_evidence.json'
assert hashlib.sha256((ROOT / pressure['source_path']).read_bytes()).hexdigest() == pressure['source_sha256']
pressure_protocol_path = ROOT / pressure['protocol_path']
assert hashlib.sha256(pressure_protocol_path.read_bytes()).hexdigest() == pressure['protocol_sha256']
pressure_protocol = json.loads(pressure_protocol_path.read_text())
assert pressure_protocol['origin_smoothing_strength'] == pressure_protocol['pressure_group_smoothing_strength'] == 20
assert pressure['raw_manifest_path'] == 'data/44_first_xt_evidence.json'
assert hashlib.sha256((ROOT / pressure['raw_manifest_path']).read_bytes()).hexdigest() == pressure['raw_manifest_sha256']
assert pressure['match_ids'] == cv_ids
pressure_rows = pressure['predictions']
cv_lookup = {(r['match_id'], r['id']): r for r in cv_predictions}
assert len(pressure_rows) == len(cv_lookup)
assert len({(r['match_id'], r['id']) for r in pressure_rows}) == len(cv_lookup)
for row in pressure_rows:
    original = cv_lookup[(row['match_id'], row['id'])]
    for key in ['match_id', 'id', 'team', 'start_cell', 'completed']:
        assert row[key] == original[key]
    assert row['raw_pressure_value'] is None or type(row['raw_pressure_value']) is bool
    assert row['pressure_flag'] == (row['raw_pressure_value'] is True)
    assert row['origin_probability'] == original['zone_probability']
for record in xt['raw_inputs']:
    cached = ROOT / record['relative_path']
    if cached.exists():
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == record['sha256']
        lookup = {r['id']: r for r in json.loads(cached.read_text())}
        for row in pressure_rows:
            if row['match_id'] == record['match_id']:
                event = lookup[row['id']]
                assert row['raw_pressure_value'] == event.get('under_pressure')
                assert row['pressure_field_present'] == ('under_pressure' in event)
assert [r['held_out_match_id'] for r in pressure['folds']] == cv_ids
for fold, reference_fold in zip(pressure['folds'], completion_cv['folds']):
    omitted = fold['held_out_match_id']
    assert fold['training_match_ids'] == reference_fold['training_match_ids']
    fitted = fold['model']
    assert fitted['origin_model'] == reference_fold['model']
    assert fitted['pressure_strength'] == 20
    train = [r for r in pressure_rows if r['match_id'] != omitted]
    predicted = [r for r in pressure_rows if r['match_id'] == omitted]
    assert [(g['cell'], g['pressure_flag']) for g in fitted['groups']] == [(z, flag) for z in range(24) for flag in (False, True)]
    for group in fitted['groups']:
        selected = [r for r in train if r['start_cell'] == group['cell'] and r['pressure_flag'] == group['pressure_flag']]
        n = len(selected); count = sum(r['completed'] for r in selected)
        prior = fitted['origin_model']['zones'][group['cell']]['smoothed_probability']
        assert group['attempts'] == n and group['completions'] == count
        assert group['origin_prior'] == prior
        assert math.isclose(group['probability'], (count + 20 * prior) / (n + 20))
    for row in predicted:
        group = next(g for g in fitted['groups'] if (g['cell'], g['pressure_flag']) == (row['start_cell'], row['pressure_flag']))
        assert row['pressure_probability'] == group['probability']
    for metric_key, prediction_key in [('origin_metrics', 'origin_probability'), ('pressure_metrics', 'pressure_probability')]:
        metric = fold[metric_key]
        assert metric['passes'] == len(predicted) and metric['completions'] == sum(r['completed'] for r in predicted)
        ll = sum(-(r['completed']*math.log(r[prediction_key])+(1-r['completed'])*math.log1p(-r[prediction_key])) for r in predicted)/len(predicted)
        bs = sum((r[prediction_key]-r['completed'])**2 for r in predicted)/len(predicted)
        assert math.isclose(metric['log_loss'], ll) and math.isclose(metric['brier_score'], bs)
    assert fold['origin_metrics'] == reference_fold['zone_metrics']
for metric_key, prediction_key in [('pooled_origin_metrics','origin_probability'),('pooled_pressure_metrics','pressure_probability')]:
    metric = pressure[metric_key]
    assert metric['passes'] == len(pressure_rows) and metric['completions'] == sum(r['completed'] for r in pressure_rows)
    ll = sum(-(r['completed']*math.log(r[prediction_key])+(1-r['completed'])*math.log1p(-r[prediction_key])) for r in pressure_rows)/len(pressure_rows)
    bs = sum((r[prediction_key]-r['completed'])**2 for r in pressure_rows)/len(pressure_rows)
    assert math.isclose(metric['log_loss'], ll) and math.isclose(metric['brier_score'], bs)
assert pressure['pooled_origin_metrics'] == completion_cv['pooled_zone_metrics']
print('PASS: recorded-pressure tags, fold-local hierarchical counts, origin reproduction and candidate errors reconcile.')

support_audit = json.loads((ROOT / 'data/51_completion_group_support_evidence.json').read_text())
assert support_audit['source_path'] == 'data/50_pressure_feature_evidence.json'
assert hashlib.sha256((ROOT / support_audit['source_path']).read_bytes()).hexdigest() == support_audit['source_sha256']
support_rows = support_audit['predictions']
assert [(r['match_id'], r['id']) for r in support_rows] == [(r['match_id'], r['id']) for r in pressure_rows]
support_labels = ['No fitting passes','1–19 fitting passes','20–49 fitting passes','50+ fitting passes']
pressure_fold_lookup = {f['held_out_match_id']: f for f in pressure['folds']}
for row, original in zip(support_rows, pressure_rows):
    fold = pressure_fold_lookup[row['match_id']]
    group = next(g for g in fold['model']['groups'] if (g['cell'],g['pressure_flag']) == (original['start_cell'],original['pressure_flag']))
    n = group['attempts']; count = group['completions']; strength = fold['model']['pressure_strength']
    band = support_labels[0] if n==0 else support_labels[1] if n<20 else support_labels[2] if n<50 else support_labels[3]
    assert row['pressure_flag'] == original['pressure_flag']
    assert row['training_group_attempts'] == n and row['training_group_completions'] == count
    assert row['support_band'] == band and row['smoothing_strength'] == strength
    assert row['raw_group_completion_rate'] == (count/n if n else None)
    assert row['origin_prior'] == group['origin_prior']
    weight = strength/(n+strength)
    assert math.isclose(row['prior_weight'], weight)
    assert row['pressure_probability'] == original['pressure_probability']
    expected = (1-weight)*(count/n) + weight*group['origin_prior'] if n else group['origin_prior']
    assert math.isclose(row['pressure_probability'], expected)
assert [g['support_band'] for g in support_audit['support_groups']] == support_labels
for group in support_audit['support_groups']:
    selected = [r for r in support_rows if r['support_band']==group['support_band']]
    assert group['predictions'] == len(selected)
    assert group['pressure_flagged_predictions'] == sum(r['pressure_flag'] for r in selected)
    assert group['pass_keys'] == [{'match_id': r['match_id'],'id': r['id']} for r in selected]
    if selected:
        assert math.isclose(group['mean_prior_weight'], sum(r['prior_weight'] for r in selected)/len(selected))
    else:
        assert group['mean_prior_weight'] is None
usa_fold = pressure_fold_lookup[69202]
expected_examples = [g for g in usa_fold['model']['groups'] if g['cell']==8]
assert len(support_audit['usa_cell_8_examples']) == len(expected_examples)
for example, original in zip(support_audit['usa_cell_8_examples'],expected_examples):
    assert {k:v for k,v in example.items() if k!='prior_weight'} == original
    assert math.isclose(example['prior_weight'],20/(original['attempts']+20))
print('PASS: fitting-group support, smoothing weights, complete membership and unchanged probabilities reconcile.')

grid_study = json.loads((ROOT / 'data/52_completion_grid_evidence.json').read_text())
assert grid_study['source_path'] == 'data/45_failed_pass_value_evidence.json'
assert hashlib.sha256((ROOT / grid_study['source_path']).read_bytes()).hexdigest() == grid_study['source_sha256']
assert grid_study['reference_path'] == 'data/48_completion_match_cv_evidence.json'
assert hashlib.sha256((ROOT / grid_study['reference_path']).read_bytes()).hexdigest() == grid_study['reference_sha256']
grid_protocol_path=ROOT/grid_study['protocol_path']
assert hashlib.sha256(grid_protocol_path.read_bytes()).hexdigest() == grid_study['protocol_sha256']
grid_protocol=json.loads(grid_protocol_path.read_text())
assert grid_protocol['grids']==[[1,1],[3,2],[6,4],[12,8]] and grid_protocol['smoothing_strength']==20
expected_input=[{'match_id':r['match_id'],'id':r['id'],'start':r['start'],'completed':int(r['pass_outcome'] is None)} for r in scored_passes if r['pass_outcome'] is None or r['pass_outcome'] in ['Incomplete','Out','Pass Offside']]
assert grid_study['input_passes']==expected_input
assert grid_study['match_ids']==cv_ids
assert [(c['nx'],c['ny']) for c in grid_study['candidates']]==[(1,1),(3,2),(6,4),(12,8)]
for candidate in grid_study['candidates']:
    nx,ny=candidate['nx'],candidate['ny'];nc=nx*ny
    assert candidate['cells']==nc
    mapped=[{**r,'cell':min(int(r['start'][1]/80*ny),ny-1)*nx+min(int(r['start'][0]/120*nx),nx-1)} for r in expected_input]
    input_lookup={(r['match_id'],r['id']):r for r in mapped}
    predicted=candidate['predictions']
    assert len(predicted)==len(input_lookup)
    assert len({(r['match_id'],r['id']) for r in predicted})==len(input_lookup)
    for row in predicted:
        original=input_lookup[(row['match_id'],row['id'])]
        assert row['cell']==original['cell'] and row['completed']==original['completed']
    assert [f['held_out_match_id'] for f in candidate['folds']]==cv_ids
    for fold in candidate['folds']:
        omitted=fold['held_out_match_id']
        assert fold['training_match_ids']==[m for m in cv_ids if m!=omitted]
        train=[r for r in mapped if r['match_id']!=omitted]
        n=[0]*nc;success=[0]*nc
        for row in train:
            n[row['cell']]+=1;success[row['cell']]+=row['completed']
        reference=sum(success)/len(train)
        fitted=fold['model']
        assert fitted['training_attempts']==len(train) and fitted['global_training_rate']==reference
        assert fitted['attempts_by_cell']==n and fitted['completions_by_cell']==success
        assert len(fitted['probabilities'])==nc
        for i,p in enumerate(fitted['probabilities']):
            assert math.isclose(p,(success[i]+20*reference)/(n[i]+20))
        check=[r for r in predicted if r['match_id']==omitted]
        for row in check:
            assert row['probability']==fitted['probabilities'][row['cell']]
            if (nx,ny)==(6,4):
                assert row['probability']==cv_lookup[(row['match_id'],row['id'])]['zone_probability']
            if (nx,ny)==(1,1):
                assert math.isclose(row['probability'],cv_lookup[(row['match_id'],row['id'])]['baseline_probability'])
        metric=fold['metrics']
        assert metric['passes']==len(check) and metric['completions']==sum(r['completed'] for r in check)
        ll=sum(-(r['completed']*math.log(r['probability'])+(1-r['completed'])*math.log1p(-r['probability'])) for r in check)/len(check)
        bs=sum((r['probability']-r['completed'])**2 for r in check)/len(check)
        assert math.isclose(metric['log_loss'],ll) and math.isclose(metric['brier_score'],bs)
    metric=candidate['pooled_metrics']
    assert metric['passes']==len(predicted) and metric['completions']==sum(r['completed'] for r in predicted)
    ll=sum(-(r['completed']*math.log(r['probability'])+(1-r['completed'])*math.log1p(-r['probability'])) for r in predicted)/len(predicted)
    bs=sum((r['probability']-r['completed'])**2 for r in predicted)/len(predicted)
    assert math.isclose(metric['log_loss'],ll) and math.isclose(metric['brier_score'],bs)
    if (nx,ny)==(6,4):
        assert metric==completion_cv['pooled_zone_metrics']
    if (nx,ny)==(1,1):
        assert math.isclose(metric['log_loss'],completion_cv['pooled_baseline_metrics']['log_loss'])
print('PASS: all grid resolutions, identical pass coverage, fold-local counts and baseline/original-model reproduction reconcile.')

portfolio_case = json.loads((ROOT / 'data/53_portfolio_case_study_evidence.json').read_text())
for source_record in portfolio_case['source_files'].values():
    assert hashlib.sha256((ROOT / source_record['path']).read_bytes()).hexdigest() == source_record['sha256']
case_facts = portfolio_case['facts']
assert case_facts['matches'] == study['pooled']['matches']
for output_key, source_key in [('deliveries','deliveries'),('corners_with_shot','corners_with_phase_shot'),('corner_shot_rate','phase_shot_rate'),('phase_shots','phase_shots'),('phase_shot_goals','phase_shot_goals')]:
    assert case_facts[output_key] == study['pooled'][source_key]
assert case_facts['goals_by_match'] == [{'opponent':r['opponent'],'phase_shot_goals':r['phase_shot_goals']} for r in study['matches']]
assert [(r['opponent'],r['phase_shot_goals']) for r in case_facts['goals_by_match'] if r['phase_shot_goals']] == [("Korea Republic Women's",2)]
assert case_facts['unrecorded_technique_deliveries'] == next(g['deliveries'] for g in profiles['groups'] if g['category']=='Other / unrecorded')
assert case_facts['same_taker_side_match_contexts_with_both_types'] == side_audit['contexts_with_both_types']
assert case_facts['review_examples'] == sum(r['example'] is not None for r in review['review_queue'])
assert case_facts['korea_window_results'] == [{'seconds':r['window_seconds'],'corners_with_shot':r['teams'][0]['corners_with_shot'],'deliveries':r['teams'][0]['deliveries']} for r in window['results']]
assert hashlib.sha256((ROOT / portfolio_case['figure']['path']).read_bytes()).hexdigest() == portfolio_case['figure']['sha256']
spec=importlib.util.spec_from_file_location('portfolio_case_render',ROOT/'53_portfolio_case_study.py')
case_renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(case_renderer)
assert portfolio_case == case_renderer.build_evidence()
assert (ROOT/'reports/36_france_corner_portfolio_case_study.html').read_text() == case_renderer.render_report(portfolio_case)
from html.parser import HTMLParser
class CaseLinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        self.links.extend(v for k,v in attrs if k in ('href','src') and v)
for relative in ['reports/36_france_corner_portfolio_case_study.html','lessons/0035-employer-facing-case-study.html']:
    page_path=ROOT/relative;parser=CaseLinkParser();parser.feed(page_path.read_text())
    for link in parser.links:
        if link.startswith(('http://','https://','#')):
            continue
        assert (page_path.parent/link.split('#',1)[0]).exists(), 'Missing case-study link: '+link
assert (ROOT/'assets/report.css').exists() and (ROOT/'assets/lesson.css').exists()
print('PASS: portfolio case-study facts, source references, generated report and local resource links reconcile.')

assert (ROOT/'reports/36_france_corner_portfolio_case_study.md').read_text() == case_renderer.render_markdown(portfolio_case)
print('PASS: GitHub-readable case-study version reproduces from the same evidence.')

first_sql=json.loads((ROOT/'data/54_first_sql_evidence.json').read_text())
assert first_sql['source_path']=='data/38_france_corner_study_evidence.json'
assert hashlib.sha256((ROOT/first_sql['source_path']).read_bytes()).hexdigest()==first_sql['source_sha256']
for record in first_sql['sql_files'].values():
    assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256']
expected_sql_rows=[]
for match_record in study['matches']:
    for phase_record in match_record['phases']:
        expected_sql_rows.append({'match_id':match_record['fixture']['match_id'],'corner_id':phase_record['corner_id'],
            'match_date':match_record['fixture']['match_date'],'opponent':match_record['opponent'],
            'period':phase_record['period'],'minute':phase_record['minute'],'second':phase_record['second'],
            'phase_shots':len(phase_record['shots']),'phase_goals':sum(s['goal'] for s in phase_record['shots']),
            'has_phase_shot':int(bool(phase_record['shots']))})
assert first_sql['rows']==expected_sql_rows
assert len({(r['match_id'],r['corner_id']) for r in first_sql['rows']})==len(first_sql['rows'])
first_sql_total=first_sql['queries']['overall'][0]
assert first_sql_total['deliveries']==study['pooled']['deliveries']
assert first_sql_total['corners_with_shot']==study['pooled']['corners_with_phase_shot']
assert first_sql_total['phase_shots']==study['pooled']['phase_shots']
assert first_sql_total['phase_goals']==study['pooled']['phase_shot_goals']
assert math.isclose(first_sql_total['corner_shot_rate_pct'],study['pooled']['phase_shot_rate']*100)
assert len(first_sql['queries']['by_opponent'])==len(study['matches'])
for row,match_record in zip(first_sql['queries']['by_opponent'],study['matches']):
    assert row['opponent']==match_record['opponent']
    assert row['deliveries']==match_record['deliveries']
    assert row['corners_with_shot']==match_record['corners_with_phase_shot']
    assert row['phase_shots']==match_record['phase_shots']
    assert row['phase_goals']==match_record['phase_shot_goals']
    assert math.isclose(row['corner_shot_rate_pct'],match_record['phase_shot_rate']*100)
expected_extra=[{k:r[k] for k in ['match_id','corner_id','opponent','period','minute','second']} for r in sorted(expected_sql_rows,key=lambda r:(r['match_date'],r['period'],r['minute'],r['second'],r['corner_id'])) if r['period'] in (3,4)]
assert first_sql['queries']['extra_time']==expected_extra
spec=importlib.util.spec_from_file_location('football_sql_audit',ROOT/'54_first_football_sql.py')
sql_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(sql_module)
assert first_sql==sql_module.build_evidence()
import sqlite3
from contextlib import closing
local_database=ROOT/first_sql['generated_database']
if local_database.exists():
    with closing(sqlite3.connect(local_database.as_uri()+'?mode=ro',uri=True)) as con:
        assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert sql_module.query_results(con)==first_sql['queries']
        assert [dict(r) for r in con.execute('SELECT * FROM corners ORDER BY match_id,corner_id')] == sorted(expected_sql_rows,key=lambda r:(r['match_id'],r['corner_id']))
print('PASS: SQL schema/query hashes, corner row grain, grouped denominators and optional local database reconcile.')

join_evidence=json.loads((ROOT/'data/55_sql_join_evidence.json').read_text())
assert join_evidence['source_path']=='data/38_france_corner_study_evidence.json'
assert hashlib.sha256((ROOT/join_evidence['source_path']).read_bytes()).hexdigest()==join_evidence['source_sha256']
for record in join_evidence['sql_files'].values():
    assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256']
expected_join_corners=[{k:r[k] for k in ['match_id','corner_id','match_date','opponent','period','minute','second']} for r in expected_sql_rows]
expected_join_shots=[{'match_id':m['fixture']['match_id'],'shot_id':s['shot_id'],'corner_id':p['corner_id'],'elapsed_seconds':s['elapsed_seconds'],'goal':s['goal']} for m in study['matches'] for p in m['phases'] for s in p['shots']]
assert join_evidence['corner_rows']==expected_join_corners
assert join_evidence['shot_rows']==expected_join_shots
assert len({(r['match_id'],r['corner_id']) for r in join_evidence['corner_rows']})==len(expected_join_corners)
assert len({(r['match_id'],r['shot_id']) for r in join_evidence['shot_rows']})==len(expected_join_shots)
diagnostic=join_evidence['queries']['diagnostic'][0]
assert diagnostic['joined_rows']==sum(max(1,len(p['shots'])) for m in study['matches'] for p in m['phases'])
assert diagnostic['linked_shot_rows']==study['pooled']['phase_shots']
assert diagnostic['corners_without_phase_shot']==study['pooled']['deliveries']-study['pooled']['corners_with_phase_shot']
assert join_evidence['queries']['summary']==first_sql['queries']['overall']
spec=importlib.util.spec_from_file_location('football_join_audit',ROOT/'55_football_sql_joins.py')
join_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(join_module)
assert join_evidence==join_module.build_evidence()
join_database=ROOT/join_evidence['generated_database']
if join_database.exists():
    with closing(sqlite3.connect(join_database.as_uri()+'?mode=ro',uri=True)) as con:
        assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
        assert join_module.query_results(con)==join_evidence['queries']
        assert [dict(r) for r in con.execute('SELECT * FROM corners ORDER BY match_id,corner_id')]==sorted(expected_join_corners,key=lambda r:(r['match_id'],r['corner_id']))
        assert [dict(r) for r in con.execute('SELECT * FROM phase_shots ORDER BY match_id,shot_id')]==sorted(expected_join_shots,key=lambda r:(r['match_id'],r['shot_id']))
print('PASS: related corner/shot tables, composite keys, join expansion and preserved delivery denominator reconcile.')

opponent_sql=json.loads((ROOT/'data/56_sql_opponent_evidence.json').read_text())
spec=importlib.util.spec_from_file_location('opponent_sql_audit',ROOT/'56_sql_opponent_comparison.py')
opponent_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(opponent_module)
assert opponent_sql==opponent_module.build_evidence()
expected_opponents={m['opponent']:m for m in study['matches']}
assert len(opponent_sql['rows'])==len(expected_opponents)
for row in opponent_sql['rows']:
    match_record=expected_opponents[row['opponent']]
    assert row['deliveries']==match_record['deliveries']
    assert row['corners_with_shot']==match_record['corners_with_phase_shot']
    assert row['phase_shots']==match_record['phase_shots']
    assert math.isclose(row['corner_shot_rate_pct'],100*match_record['phase_shot_rate'])
assert sum(r['deliveries'] for r in opponent_sql['rows'])==45
assert sum(r['corners_with_shot'] for r in opponent_sql['rows'])==19
print('PASS: join-safe SQL opponent groups reproduce all five football match summaries.')

phase_sql=json.loads((ROOT/'data/57_sql_match_phase_evidence.json').read_text())
spec=importlib.util.spec_from_file_location('phase_sql_audit',ROOT/'57_sql_match_phase_comparison.py')
phase_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(phase_module)
assert phase_sql==phase_module.build_evidence()
assert (ROOT/'reports/40_sql_match_phase_comparison.md').read_text()==phase_module.render_report(phase_sql)
expected_phase_groups={}
for match_record in study['matches']:
    for corner_phase in match_record['phases']:
        phase_order=min(corner_phase['period'],3)
        counts=expected_phase_groups.setdefault(phase_order,[0,0,0])
        counts[0]+=1
        counts[1]+=int(bool(corner_phase['shots']))
        counts[2]+=len(corner_phase['shots'])
assert len(phase_sql['rows'])==len(expected_phase_groups)
for row in phase_sql['rows']:
    assert [row['deliveries'],row['corners_with_shot'],row['phase_shots']]==expected_phase_groups[row['phase_order']]
    assert math.isclose(row['corner_shot_rate_pct'],100*row['corners_with_shot']/row['deliveries'])
assert sum(r['deliveries'] for r in phase_sql['rows'])==study['pooled']['deliveries']
assert sum(r['corners_with_shot'] for r in phase_sql['rows'])==study['pooled']['corners_with_phase_shot']
assert sum(r['phase_shots'] for r in phase_sql['rows'])==study['pooled']['phase_shots']
print('PASS: period-based SQL match phases reconcile to raw study memberships and pooled corner counts.')

taker_sql=json.loads((ROOT/'data/58_sql_corner_taker_evidence.json').read_text())
spec=importlib.util.spec_from_file_location('taker_sql_audit',ROOT/'58_sql_corner_taker_report.py')
taker_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(taker_module)
assert taker_sql==taker_module.build_evidence()
assert (ROOT/'reports/41_sql_corner_taker_report.md').read_text()==taker_module.render_report(taker_sql)
taker_profiles=json.loads((ROOT/'data/39_corner_delivery_profiles_evidence.json').read_text())
expected_taker_rows=[{k:r[k] for k in ('match_id','corner_id','passer')} for r in taker_profiles['deliveries']]
assert taker_sql['taker_rows']==expected_taker_rows
expected_taker_counts={}
for delivery in taker_profiles['deliveries']:
    counts=expected_taker_counts.setdefault(delivery['passer'],[0,0,0,0])
    counts[0]+=1
    counts[1]+=int(delivery['phase_has_shot'])
    counts[2]+=delivery['phase_shots']
    counts[3]+=delivery['phase_shot_goals']
assert len(taker_sql['all_takers'])==len(expected_taker_counts)
for row in taker_sql['all_takers']:
    assert [row[k] for k in ('deliveries','corners_with_shot','phase_shots','phase_goals')]==expected_taker_counts[row['passer']]
    assert math.isclose(row['corner_shot_rate_pct'],100*row['corners_with_shot']/row['deliveries'])
assert taker_sql['filtered_takers']==[r for r in taker_sql['all_takers'] if r['deliveries']>=taker_sql['display_min_deliveries']]
assert sum(r['deliveries'] for r in taker_sql['all_takers'])==study['pooled']['deliveries']
assert sum(r['corners_with_shot'] for r in taker_sql['all_takers'])==study['pooled']['corners_with_phase_shot']
assert sum(r['phase_shots'] for r in taker_sql['all_takers'])==study['pooled']['phase_shots']
assert sum(r['phase_goals'] for r in taker_sql['all_takers'])==study['pooled']['phase_shot_goals']
print('PASS: complete taker metadata, player groups, HAVING display filter and pooled corner counts reconcile.')

audit_evidence=json.loads((ROOT/'data/59_corner_data_quality_evidence.json').read_text())
spec=importlib.util.spec_from_file_location('corner_quality_audit',ROOT/'59_corner_data_quality.py')
audit_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit_module)
assert audit_evidence==audit_module.build_evidence()
assert (ROOT/'reports/42_corner_data_quality.md').read_text()==audit_module.render_report(audit_evidence)
assert audit_evidence['input_counts']=={'corners':len(expected_join_corners),'shots':len(expected_join_shots),'taker_records':len(expected_taker_rows)}
assert audit_evidence['passed']
assert len(audit_evidence['checks'])==9
assert all(r['passed'] and r['violation_count']==0 for r in audit_evidence['checks'])
print('PASS: corner relationship audit reproduces, all nine structural checks pass, report matches evidence.')

defensive=read('60_france_defensive_corner_evidence.json')
assert defensive['source_path']=='data/38_france_corner_study_evidence.json'
assert hashlib.sha256((ROOT/defensive['source_path']).read_bytes()).hexdigest()==defensive['source_sha256']
assert defensive['protocol_path']==study['protocol_path']
assert hashlib.sha256((ROOT/defensive['protocol_path']).read_bytes()).hexdigest()==defensive['protocol_sha256']
assert defensive['france_attacking_reference']==study['pooled']
spec=importlib.util.spec_from_file_location('defensive_corner_audit',ROOT/'60_france_defensive_corners.py')
defensive_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(defensive_module)
assert (ROOT/'reports/43_france_defensive_corners.md').read_text()==defensive_module.render_report(defensive)
assert len(defensive['matches'])==len(study['matches'])
for row,old in zip(defensive['matches'],study['matches']):
    assert row['fixture']==old['fixture'] and row['raw_input']==old['raw_input']
    assert row['defending_team']=="France Women's"
    assert row['attacking_team']==row['opponent']==old['opponent']
    assert row['deliveries']==len(row['phases'])
    assert len({p['corner_id'] for p in row['phases']})==row['deliveries']
    assert row['corners_with_phase_shot']==sum(bool(p['shots']) for p in row['phases'])
    shots=[s for p in row['phases'] for s in p['shots']]
    assert row['phase_shots']==len(shots)==len({s['shot_id'] for s in shots})
    assert row['phase_shot_goals']==sum(s['goal'] for s in shots)
    assert row['extra_time_deliveries']==sum(p['period'] in (3,4) for p in row['phases'])
    assert all(p['period'] in (1,2,3,4) for p in row['phases'])
    assert all(0<=s['elapsed_seconds']<=15 for s in shots)
    if row['deliveries']:
        assert math.isclose(row['phase_shot_rate'],row['corners_with_phase_shot']/row['deliveries'])
    else:
        assert row['phase_shot_rate'] is None
assert defensive['pooled']==defensive_module.study_helper.pool(defensive['matches'])
if all((ROOT/r['raw_input']['relative_path']).exists() for r in defensive['matches']):
    assert defensive==defensive_module.build_evidence(allow_download=False)
    protocol=json.loads((ROOT/defensive['protocol_path']).read_text())
    for old in study['matches']:
        events=defensive_module.load_events(old['raw_input'],allow_download=False)
        replay=defensive_module.analyze_team(events,"France Women's",protocol)
        for key in ('deliveries','corners_with_phase_shot','phase_shots','phase_shot_goals','phase_shot_rate','extra_time_deliveries'):
            assert replay[key]==old[key]
        assert [(p['corner_id'],p['shots'],p['stop_reason']) for p in replay['phases']]==[(p['corner_id'],p['shots'],p['stop_reason']) for p in old['phases']]
print('PASS: defensive-team selection, phase memberships, pooled counts and optional raw replay reconcile.')

quality=read('61_defensive_corner_quality_evidence.json')
assert quality['source_path']=='data/60_france_defensive_corner_evidence.json'
assert hashlib.sha256((ROOT/quality['source_path']).read_bytes()).hexdigest()==quality['source_sha256']
spec=importlib.util.spec_from_file_location('defensive_quality_audit',ROOT/'61_defensive_corner_shot_quality.py')
quality_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality_module)
assert (ROOT/'reports/44_defensive_corner_shot_quality.md').read_text()==quality_module.render_report(quality)
expected_quality_keys=[(m['fixture']['match_id'],p['corner_id'],s['shot_id']) for m in defensive['matches'] for p in m['phases'] for s in p['shots']]
assert [(s['match_id'],s['corner_id'],s['shot_id']) for s in quality['shots']]==expected_quality_keys
assert len({(s['match_id'],s['shot_id']) for s in quality['shots']})==len(quality['shots'])
assert all(0<=s['provider_xg']<=1 and 0<=s['x']<=120 and 0<=s['y']<=80 for s in quality['shots'])
assert len(quality['matches'])==len(defensive['matches'])
for row,source_match in zip(quality['matches'],defensive['matches']):
    assert row['fixture']==source_match['fixture'] and row['raw_input']==source_match['raw_input']
    assert row['opponent']==source_match['opponent']
    selected=[s for s in quality['shots'] if s['match_id']==row['fixture']['match_id']]
    expected=quality_module.summarize(selected,source_match['deliveries'])
    assert all(row[k]==v for k,v in expected.items())
assert quality['pooled']==quality_module.summarize(quality['shots'],defensive['pooled']['deliveries'])
assert quality['pooled']['corners_with_shot']==defensive['pooled']['corners_with_phase_shot']
assert quality['pooled']['shots']==defensive['pooled']['phase_shots']
assert quality['pooled']['shot_goals']==defensive['pooled']['phase_shot_goals']
if all((ROOT/m['raw_input']['relative_path']).exists() for m in defensive['matches']):
    assert quality==quality_module.build_evidence(allow_download=False)
print('PASS: defensive shot membership, raw supplied xG, per-shot/per-corner denominators and report reconcile.')

frames=read('62_defensive_freeze_frame_evidence.json')
assert frames['source_path']=='data/61_defensive_corner_quality_evidence.json'
assert hashlib.sha256((ROOT/frames['source_path']).read_bytes()).hexdigest()==frames['source_sha256']
spec=importlib.util.spec_from_file_location('shot_frames_audit',ROOT/'62_defensive_shot_freeze_frames.py')
frame_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame_module)
assert frames['goal_posts']==[[120.0,36.0],[120.0,44.0]]
assert frames['raw_inputs']==[m['raw_input'] for m in quality['matches']]
assert (ROOT/'reports/45_defensive_shot_freeze_frames.md').read_text()==frame_module.render_report(frames)
assert len(frames['shots'])==len(quality['shots'])
for row,old in zip(frames['shots'],quality['shots']):
    assert all(row[k]==v for k,v in old.items())
    if not row['frame_available']:
        assert row['players']==[]
        assert all(row[k] is None for k in ('recorded_players','recorded_defending_outfield','defending_outfield_in_triangle','recorded_defending_keepers','defending_keepers_in_triangle'))
        continue
    assert row['recorded_players']==len(row['players'])
    assert len({p['player_id'] for p in row['players']})==row['recorded_players']
    for player in row['players']:
        assert type(player['teammate']) is bool and type(player['is_goalkeeper']) is bool
        assert player['in_goal_triangle']==frame_module.in_goal_triangle([player['x'],player['y']],[row['x'],row['y']])
    outfield=[p for p in row['players'] if not p['teammate'] and not p['is_goalkeeper']]
    keepers=[p for p in row['players'] if not p['teammate'] and p['is_goalkeeper']]
    assert row['recorded_defending_outfield']==len(outfield)
    assert row['defending_outfield_in_triangle']==sum(p['in_goal_triangle'] for p in outfield)
    assert row['recorded_defending_keepers']==len(keepers)
    assert row['defending_keepers_in_triangle']==sum(p['in_goal_triangle'] for p in keepers)
if all((ROOT/r['relative_path']).exists() for r in frames['raw_inputs']):
    assert frames==frame_module.build_evidence(allow_download=False)
print('PASS: selected shot snapshots, player roles, goal-triangle memberships and optional raw replay reconcile.')

cohort=read('63_fullback_cohort_evidence.json')
cohort_protocol=read('63_fullback_cohort_protocol.json')
assert hashlib.sha256((ROOT/cohort['protocol_path']).read_bytes()).hexdigest()==cohort['protocol_sha256']
for source in cohort['sources']:
    assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
expected_cohort_raw=read('source_manifest.json')['raw_inputs']+read('27_frozen_evaluation_evidence.json')['raw_inputs']
assert cohort['raw_inputs']==sorted(expected_cohort_raw,key=lambda r:r['match_id'])
assert cohort['metadata_input']==read('27_evaluation_protocol.json')['metadata_source']
spec=importlib.util.spec_from_file_location('fullback_cohort_audit',ROOT/'63_fullback_recruitment_cohort.py')
cohort_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(cohort_module)
assert cohort['players_with_role_starts']==cohort_module.profile_pool(cohort['starter_rows'],cohort_protocol['starting_positions'],cohort_protocol['minimum_role_starts'])
assert cohort['eligible_players']==[p for p in cohort['players_with_role_starts'] if p['eligible']]
start_groups=defaultdict(list)
for starter in cohort['starter_rows']:
    start_groups[(starter['match_id'],starter['team_id'])].append(starter)
assert len(start_groups)==104
assert all(len(rows)==len({r['player_id'] for r in rows})==11 for rows in start_groups.values())
assert {r['match_id'] for r in cohort['starter_rows']}=={r['match_id'] for r in cohort['raw_inputs']}
assert all(len([key for key in start_groups if key[0]==record['match_id']])==2 for record in cohort['raw_inputs'])
summary=cohort['summary']
assert summary=={'matches':len(cohort['raw_inputs']),'team_lineups':len(start_groups),'starter_records':len(cohort['starter_rows']),
                 'players_with_role_starts':len(cohort['players_with_role_starts']),'eligible_players':len(cohort['eligible_players']),
                 'excluded_below_minimum':sum(not p['eligible'] for p in cohort['players_with_role_starts']),
                 'qualifying_role_start_records':sum(r['position_name'] in cohort_protocol['starting_positions'] for r in cohort['starter_rows'])}
assert (ROOT/'reports/46_fullback_recruitment_cohort.md').read_text()==cohort_module.render_report(cohort)
if all((ROOT/r['relative_path']).exists() for r in cohort['raw_inputs']+[cohort['metadata_input']]):
    assert cohort==cohort_module.build_evidence(allow_download=False)
print('PASS: full-tournament starting-lineup coverage, stable player identities and fullback eligibility rules reconcile.')

playing_time=read('64_fullback_playing_time_evidence.json')
assert playing_time['competition_id']==cohort_protocol['competition_id']==72
assert playing_time['season_id']==cohort_protocol['season_id']==30
assert playing_time['season']=='2019'
assert playing_time['source_path']=='data/63_fullback_cohort_evidence.json'
assert hashlib.sha256((ROOT/playing_time['source_path']).read_bytes()).hexdigest()==playing_time['source_sha256']
assert playing_time['course_reading']['url']=='https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'
spec=importlib.util.spec_from_file_location('playing_time_audit',ROOT/'64_fullback_playing_time.py')
time_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(time_module)
assert [m['raw_input'] for m in playing_time['match_audits']]==cohort['raw_inputs']
assert playing_time['players']==time_module.aggregate_players(cohort['eligible_players'],playing_time['match_audits'])
for match in playing_time['match_audits']:
    assert [p['period'] for p in match['periods']] in ([1,2],[1,2,3,4])
    assert match['match_duration_ms']==sum(p['length_ms'] for p in match['periods'])
    assert len(match['team_audits'])==len({r['team_id'] for r in match['team_audits']})==2
    assert len({(r['team_id'],r['player_id']) for r in match['intervals']})==len(match['intervals'])
    for interval in match['intervals']:
        assert 0<=interval['start_ms']<=interval['end_ms']<=match['match_duration_ms']
        assert interval['duration_ms']==interval['end_ms']-interval['start_ms']
        assert math.isclose(interval['minutes'],interval['duration_ms']/60000)
    for audit in match['team_audits']:
        intervals=[r for r in match['intervals'] if r['team_id']==audit['team_id']]
        assert audit['interval_count']==len(intervals)
        assert audit['registered_player_ms']==sum(r['duration_ms'] for r in intervals)
        assert audit['permanent_absence_ms']==sum(match['match_duration_ms']-r['elapsed_ms'] for r in audit['departures'] if r['changed_active_registration'])
        assert audit['registered_player_ms']==audit['expected_player_ms']==11*match['match_duration_ms']-audit['permanent_absence_ms']
assert playing_time['summary']=={'matches_audited':len(playing_time['match_audits']),
    'teams_audited':sum(len(m['team_audits']) for m in playing_time['match_audits']),
    'players':len(playing_time['players']),'selected_starts':sum(p['role_starts'] for p in playing_time['players']),
    'selected_duration_ms':sum(p['duration_ms'] for p in playing_time['players'])}
assert (ROOT/'reports/47_fullback_playing_time.md').read_text()==time_module.render_report(playing_time)
if all((ROOT/r['relative_path']).exists() for r in cohort['raw_inputs']):
    assert playing_time==time_module.build_evidence(allow_download=False)
print('PASS: registered playing intervals, team time balances, selected fixture denominators and season/course references reconcile.')

passing_profile=read('65_fullback_passing_per90_evidence.json')
assert passing_profile['source_path']=='data/64_fullback_playing_time_evidence.json'
assert hashlib.sha256((ROOT/passing_profile['source_path']).read_bytes()).hexdigest()==passing_profile['source_sha256']
assert passing_profile['competition_id']==72 and passing_profile['season_id']==30 and passing_profile['season']=='2019'
assert passing_profile['course_reading']==playing_time['course_reading']
spec=importlib.util.spec_from_file_location('passing_per90_audit',ROOT/'65_fullback_passing_per90.py')
passing_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(passing_module)
assert len(passing_profile['players'])==len(playing_time['players'])
ledger=passing_profile['pass_ledger']
assert len({(r['match_id'],r['team_id'],r['player_id']) for r in ledger})==len(ledger)
assert len(ledger)==playing_time['summary']['selected_starts']
all_pass_keys=[]
for row in ledger:
    assert len(set(row['attempt_ids']))==len(row['attempt_ids'])
    assert len(set(row['completed_ids']))==len(row['completed_ids'])
    assert set(row['completed_ids'])<=set(row['attempt_ids'])
    assert row['candidate_passes']==len(row['attempt_ids'])+sum(row['excluded'].values())
    all_pass_keys.extend((row['match_id'],identifier) for identifier in row['attempt_ids'])
assert len(set(all_pass_keys))==len(all_pass_keys)
for player,source_player in zip(passing_profile['players'],playing_time['players']):
    rows=[r for r in ledger if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id'])]
    assert {r['match_id'] for r in rows}==set(source_player['qualifying_match_ids'])
    assert player==passing_module.player_summary(source_player,rows)
    assert player['eligible_completed']<=player['eligible_attempts']
assert (ROOT/'reports/48_fullback_passing_per90.md').read_text()==passing_module.render_report(passing_profile)
if all((ROOT/m['raw_input']['relative_path']).exists() for m in playing_time['match_audits']):
    assert passing_profile==passing_module.build_evidence(allow_download=False)
print('PASS: matched-scope pass event ledgers, exclusion reconciliation, per-90 rates and completion denominators reproduce.')

advancement=read('66_fullback_advancement_evidence.json')
advancement_protocol=read('66_forward_advancement_protocol.json')
assert advancement['source_path']=='data/65_fullback_passing_per90_evidence.json'
assert hashlib.sha256((ROOT/advancement['source_path']).read_bytes()).hexdigest()==advancement['source_sha256']
assert hashlib.sha256((ROOT/advancement['protocol_path']).read_bytes()).hexdigest()==advancement['protocol_sha256']
assert advancement['season']=='2019' and advancement['competition_id']==72 and advancement['season_id']==30
assert advancement['minimum_x_gain']==advancement_protocol['minimum_x_gain']==20
spec=importlib.util.spec_from_file_location('forward_advancement_audit',ROOT/'66_fullback_forward_advancement.py')
advance_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(advance_module)
expected_completion_keys=[(r['match_id'],r['team_id'],r['player_id'],identifier) for r in passing_profile['pass_ledger'] for identifier in r['completed_ids']]
assert [(r['match_id'],r['team_id'],r['player_id'],r['pass_id']) for r in advancement['completions']]==expected_completion_keys
assert len(set(expected_completion_keys))==len(expected_completion_keys)
for row in advancement['completions']:
    gain,qualifies=advance_module.advancement([row['x'],row['y']],[row['end_x'],row['end_y']],advancement['minimum_x_gain'])
    assert row['x_gain']==gain and row['qualifies']==qualifies
assert len(advancement['players'])==len(passing_profile['players'])
for player,old in zip(advancement['players'],passing_profile['players']):
    rows=[r for r in advancement['completions'] if (r['team_id'],r['player_id'])==(old['team_id'],old['player_id'])]
    assert player==advance_module.summarize(old,rows)
    assert player['qualifying_completions']<=player['eligible_completed']
assert advancement['illustrative_ledger_examples']==[next(r for r in advancement['completions'] if r['player_id']==identifier and r['qualifies']) for identifier in (10178,15249)]
assert (ROOT/'reports/49_fullback_forward_advancement.md').read_text()==advance_module.render_report(advancement)
if all((ROOT/m['raw_input']['relative_path']).exists() for m in playing_time['match_audits']):
    assert advancement==advance_module.build_evidence(allow_download=False)
print('PASS: full completion coverage, exact forward-gain threshold, unchanged minute denominators and maps/report memberships reconcile.')

starting_context=read('67_fullback_starting_context_evidence.json')
assert starting_context['source_path']=='data/66_fullback_advancement_evidence.json'
assert hashlib.sha256((ROOT/starting_context['source_path']).read_bytes()).hexdigest()==starting_context['source_sha256']
assert starting_context['season']=='2019' and starting_context['competition_id']==72 and starting_context['season_id']==30
assert starting_context['minimum_x_gain']==advancement['minimum_x_gain']==20
assert starting_context['course_reading']==advancement['course_reading']
spec=importlib.util.spec_from_file_location('starting_context_audit',ROOT/'67_fullback_starting_area_context.py')
context_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(context_module)
assert starting_context==context_module.build_evidence()
assert len(starting_context['players'])==len(advancement['players'])
for player,old in zip(starting_context['players'],advancement['players']):
    assert all(player[k]==v for k,v in old.items())
    rows=[r for r in advancement['completions'] if (r['team_id'],r['player_id'])==(old['team_id'],old['player_id'])]
    expected={(r['match_id'],r['pass_id']) for r in rows}
    grouped=[(k['match_id'],k['pass_id']) for g in player['starting_thirds'] for k in g['pass_keys']]
    assert len(grouped)==len(set(grouped))==len(rows) and set(grouped)==expected
    assert sum(g['completions'] for g in player['starting_thirds'])==old['eligible_completed']
    assert sum(g['qualifying_completions'] for g in player['starting_thirds'])==old['qualifying_completions']
    impossible=[r for r in rows if r['x']>100]
    assert player['no_coordinate_room_completions']==len(impossible)
    assert not any(r['qualifies'] for r in impossible)
assert (ROOT/'reports/50_fullback_starting_area_context.md').read_text()==context_module.render_report(starting_context)
print('PASS: disjoint starting thirds, geometric ceiling, conditional denominators and unchanged source profiles reconcile.')

adaptive=read('68_adaptive_advancement_evidence.json')
adaptive_protocol=read('68_adaptive_advancement_protocol.json')
for source in adaptive['sources']:
    assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
assert hashlib.sha256((ROOT/adaptive['protocol_path']).read_bytes()).hexdigest()==adaptive['protocol_sha256']
assert adaptive['season']=='2019' and adaptive['competition_id']==72 and adaptive['season_id']==30
assert adaptive['course_reading']==advancement['course_reading']
assert adaptive['base_x_gain']==adaptive_protocol['base_x_gain']==advancement['minimum_x_gain']==20
assert adaptive['remaining_x_fraction']==adaptive_protocol['remaining_x_fraction']==.5
spec=importlib.util.spec_from_file_location('adaptive_advancement_audit',ROOT/'68_adaptive_forward_advancement.py')
adaptive_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(adaptive_module)
assert adaptive==adaptive_module.build_evidence()
assert len(adaptive['comparisons'])==len(advancement['completions'])
for comparison,old in zip(adaptive['comparisons'],advancement['completions']):
    assert (comparison['match_id'],comparison['pass_id'],comparison['team_id'],comparison['player_id'])==(old['match_id'],old['pass_id'],old['team_id'],old['player_id'])
    assert comparison['fixed_qualifies']==old['qualifies']
    assert not comparison['fixed_qualifies'] or comparison['alternative_qualifies']
    if comparison['newly_included']:
        assert old['x']>80 and old['end_x']>old['x']
assert len(adaptive['players'])==len(advancement['players'])
for player,old in zip(adaptive['players'],advancement['players']):
    assert all(player[k]==v for k,v in old.items())
    assert player['alternative_completions']==old['qualifying_completions']+player['newly_included_completions']
assert adaptive['summary']=={'completed_passes':len(adaptive['comparisons']),
    'fixed_qualifying':sum(r['fixed_qualifies'] for r in adaptive['comparisons']),
    'alternative_qualifying':sum(r['alternative_qualifies'] for r in adaptive['comparisons']),
    'newly_included':sum(r['newly_included'] for r in adaptive['comparisons'])}
assert adaptive['summary']['alternative_qualifying']==adaptive['summary']['fixed_qualifying']+adaptive['summary']['newly_included']
assert (ROOT/'reports/51_adaptive_forward_advancement.md').read_text()==adaptive_module.render_report(adaptive)
print('PASS: near-goal alternative, fixed-positive retention, unchanged exposures and definition-change counts reconcile.')

recruitment_brief=read('69_fullback_recruitment_brief_evidence.json')
for source in recruitment_brief['source_files'].values():
    assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
assert recruitment_brief['season']=='2019' and recruitment_brief['competition_id']==72 and recruitment_brief['season_id']==30
assert recruitment_brief['course_reading']['url']=='https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#modesty'
spec=importlib.util.spec_from_file_location('recruitment_brief_audit',ROOT/'69_fullback_recruitment_brief.py')
brief_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(brief_module)
brief_sources={k:json.loads((ROOT/r['path']).read_text()) for k,r in recruitment_brief['source_files'].items()}
assert recruitment_brief['profiles']==brief_module.compile_profiles(brief_sources)
assert recruitment_brief['cohort_size']==len(cohort['eligible_players'])
assert len(recruitment_brief['review_queue'])==4
assert len({(r['match_id'],r['pass_id']) for r in recruitment_brief['review_queue']})==4
expected_review_candidates={}
for category,rows in [('Fixed-rule example',advancement['illustrative_ledger_examples']),('Additional alternative-rule example',adaptive['illustrative_new_passes'])]:
    for row in rows:expected_review_candidates[(row['match_id'],row['pass_id'])]=(category,row)
assert {(r['match_id'],r['pass_id']) for r in recruitment_brief['review_queue']}==set(expected_review_candidates)
for row in recruitment_brief['review_queue']:
    category,candidate=expected_review_candidates[(row['match_id'],row['pass_id'])]
    assert row['category']==category
    assert row['player_id']==candidate['player_id'] and row['team_id']==candidate['team_id']
    assert row['start']==[candidate['x'],candidate['y']] and row['end']==[candidate['end_x'],candidate['end_y']]
    assert row['review_status']=='Not reviewed' and row['video_observation'] is None
assert hashlib.sha256((ROOT/recruitment_brief['figure']['path']).read_bytes()).hexdigest()==recruitment_brief['figure']['sha256']
assert (ROOT/'reports/52_fullback_recruitment_brief.md').read_text()==brief_module.render_markdown(recruitment_brief)
assert (ROOT/'reports/52_fullback_recruitment_brief.html').read_text()==brief_module.render_html(recruitment_brief)
if all((ROOT/r['relative_path']).exists() for r in recruitment_brief['raw_inputs']):
    assert recruitment_brief==brief_module.build_evidence(allow_download=False)
print('PASS: recruitment-brief facts, player roles, four unreviewed event references and generated reports reconcile.')

team_share=read('70_fullback_team_passing_share_evidence.json')
for source in team_share['source_files'].values():
    assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
assert team_share['season']=='2019' and team_share['competition_id']==72 and team_share['season_id']==30
assert team_share['course_reading']['url']=='https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'
spec=importlib.util.spec_from_file_location('team_passing_share_audit',ROOT/'70_fullback_team_passing_share.py')
share_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(share_module)
assert len(team_share['players'])==len(passing_profile['players'])
assert len(team_share['windows'])==playing_time['summary']['selected_starts']
assert len({(w['match_id'],w['team_id'],w['player_id']) for w in team_share['windows']})==len(team_share['windows'])
original_pass_windows={(r['match_id'],r['team_id'],r['player_id']):r for r in passing_profile['pass_ledger']}
for window in team_share['windows']:
    key=(window['match_id'],window['team_id'],window['player_id'])
    assert window['player_completed_ids']==original_pass_windows[key]['completed_ids']
    assert len(set(window['team_completed_ids']))==len(window['team_completed_ids'])
    assert set(window['player_completed_ids'])<=set(window['team_completed_ids'])
    match=next(m for m in playing_time['match_audits'] if m['match_id']==window['match_id'])
    interval=next(r for r in match['intervals'] if (r['team_id'],r['player_id'])==(window['team_id'],window['player_id']))
    assert window['start_ms']==interval['start_ms'] and window['end_ms']==interval['end_ms']
for player,old in zip(team_share['players'],passing_profile['players']):
    assert all(player[k]==v for k,v in old.items())
    windows=[w for w in team_share['windows'] if (w['team_id'],w['player_id'])==(player['team_id'],player['player_id'])]
    assert player==share_module.summarize(old,windows)
    if player['share_of_team_completions_pct'] is not None:
        assert math.isclose(player['completed_per90'],player['team_completions_per_player90']*player['share_of_team_completions_pct']/100)
assert (ROOT/'reports/53_fullback_team_passing_share.md').read_text()==share_module.render_report(team_share)
if all((ROOT/m['raw_input']['relative_path']).exists() for m in playing_time['match_audits']):
    assert team_share==share_module.build_evidence(allow_download=False)
print('PASS: same-window team denominators, player subsets, unchanged numerators and involvement shares reconcile.')

percentiles=read('71_fullback_percentile_evidence.json')
for source in percentiles['source_files'].values():
    assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
assert percentiles['season']=='2019' and percentiles['competition_id']==72 and percentiles['season_id']==30
assert percentiles['course_reading']['url']=='https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#comparison-percentile-rankings'
spec=importlib.util.spec_from_file_location('fullback_percentiles_audit',ROOT/'71_fullback_percentile_comparisons.py')
percentile_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(percentile_module)
assert percentiles==percentile_module.build_evidence()
assert len(percentiles['players'])==len(team_share['players'])
assert len(percentiles['peer_pools']['all_fullbacks'])==35
assert len(percentiles['peer_pools']['left_only'])==17 and len(percentiles['peer_pools']['right_only'])==14
assert sum(p['starting_side_group']=='mixed' for p in percentiles['players'])==4
for player,old in zip(percentiles['players'],team_share['players']):
    assert all(player[k]==v for k,v in old.items())
    if player['starting_side_group']=='mixed':assert player['percentiles_same_side'] is None
    for scope in ('percentiles_all_fullbacks','percentiles_same_side'):
        if player[scope] is None:continue
        for metric,result in player[scope].items():
            assert result['value']==old[metric]
            if result['percentile'] is None:continue
            assert result['lower_count']+result['tied_other_count']+result['higher_count']==result['other_players']==result['valid_pool_size']-1
            assert math.isclose(result['percentile'],100*(result['lower_count']+.5*result['tied_other_count'])/result['other_players'])
            assert 0<=result['percentile']<=100
assert (ROOT/'reports/54_fullback_percentile_comparisons.md').read_text()==percentile_module.render_report(percentiles)
print('PASS: unchanged metric values, explicit peer pools, percentile tie handling and rank-count evidence reconcile.')

match_sensitivity=read('72_fullback_match_sensitivity_evidence.json')
for source in match_sensitivity['source_files'].values():
    assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
assert match_sensitivity['season']=='2019' and match_sensitivity['competition_id']==72 and match_sensitivity['season_id']==30
assert match_sensitivity['course_reading']==percentiles['course_reading']
spec=importlib.util.spec_from_file_location('fullback_sensitivity_audit',ROOT/'72_fullback_match_sensitivity.py')
sensitivity_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(sensitivity_module)
assert match_sensitivity==sensitivity_module.build_evidence()
assert len(match_sensitivity['players'])==len(team_share['players'])
assert match_sensitivity['cases']==sum(len(p['cases']) for p in match_sensitivity['players'])==playing_time['summary']['selected_starts']
for player,old in zip(match_sensitivity['players'],team_share['players']):
    assert player['baseline']==old
    assert [c['omitted_match_id'] for c in player['cases']]==old['qualifying_match_ids']
    for case in player['cases']:
        window=next(w for w in team_share['windows'] if (w['match_id'],w['team_id'],w['player_id'])==(case['omitted_match_id'],old['team_id'],old['player_id']))
        assert case['remaining_duration_ms']+window['end_ms']-window['start_ms']==old['duration_ms']
        assert case['remaining_completed']+len(window['player_completed_ids'])==old['eligible_completed']
        assert case['remaining_team_completed']+len(window['team_completed_ids'])==old['team_completed_while_registered']
        assert case['remaining_qualifying_starts']==len(old['qualifying_match_ids'])-1
        assert case['remaining_match_ids']==[m for m in old['qualifying_match_ids'] if m!=case['omitted_match_id']]
        for metric in percentile_module.METRICS:
            result=case['percentiles_fixed_peers'][metric]
            assert result['value']==case[metric]
            if result['percentile'] is not None:assert result['other_players']==34
assert (ROOT/'reports/55_fullback_match_sensitivity.md').read_text()==sensitivity_module.render_report(match_sensitivity)
print('PASS: own-match deletions remove matched counts/exposure, preserve fixed peers and reproduce observed sensitivity ranges.')

pressure_activity=read('73_fullback_pressure_activity_evidence.json')
assert pressure_activity['source_path']=='data/64_fullback_playing_time_evidence.json'
assert hashlib.sha256((ROOT/pressure_activity['source_path']).read_bytes()).hexdigest()==pressure_activity['source_sha256']
assert pressure_activity['season']=='2019' and pressure_activity['competition_id']==72 and pressure_activity['season_id']==30
assert pressure_activity['course_reading']['url']=='https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#counts-of-actions'
spec=importlib.util.spec_from_file_location('fullback_pressure_audit',ROOT/'73_fullback_pressure_activity.py')
pressure_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(pressure_module)
assert len(pressure_activity['players'])==len(playing_time['players'])
assert len(pressure_activity['windows'])==playing_time['summary']['selected_starts']
assert len({(w['match_id'],w['team_id'],w['player_id']) for w in pressure_activity['windows']})==len(pressure_activity['windows'])
assert len({(r['match_id'],r['event_id']) for r in pressure_activity['rows']})==len(pressure_activity['rows'])
for row in pressure_activity['rows']:
    assert row['period'] in (1,2,3,4)
    assert (row['x'],row['y'])==pressure_module.location_or_none([row['x'],row['y']])
    assert row['location_valid']==(row['x'] is not None)
for player,old in zip(pressure_activity['players'],playing_time['players']):
    rows=[r for r in pressure_activity['rows'] if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id'])]
    assert player==pressure_module.summarize(old,rows)
    windows=[w for w in pressure_activity['windows'] if (w['team_id'],w['player_id'])==(player['team_id'],player['player_id'])]
    assert {w['match_id'] for w in windows}==set(old['qualifying_match_ids'])
    assert sum(w['end_ms']-w['start_ms'] for w in windows)==old['duration_ms']
    assert player['recorded_pressures']==player['mapped_pressures']+player['unmapped_pressures']
    for window in windows:
        selected=[r['event_id'] for r in rows if r['match_id']==window['match_id']]
        assert selected==window['pressure_ids']
        assert all(window['start_ms']<=r['elapsed_ms']<=window['end_ms'] for r in rows if r['match_id']==window['match_id'])
assert (ROOT/'reports/56_fullback_pressure_activity.md').read_text()==pressure_module.render_report(pressure_activity)
if all((ROOT/m['raw_input']['relative_path']).exists() for m in playing_time['match_audits']):
    assert pressure_activity==pressure_module.build_evidence(allow_download=False)
print('PASS: recorded Pressure identity/scope, unchanged exposures, location coverage and per-90 activity reconcile.')

opponent_context=read('74_fullback_opponent_pass_context_evidence.json')
for source in opponent_context['source_files'].values():
    assert hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()==source['sha256']
assert opponent_context['season']=='2019' and opponent_context['competition_id']==72 and opponent_context['season_id']==30
spec=importlib.util.spec_from_file_location('opponent_context_audit',ROOT/'74_fullback_opponent_pass_context.py')
context_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(context_module)
assert len(opponent_context['players'])==35 and len(opponent_context['windows'])==145
assert len({(w['match_id'],w['team_id'],w['player_id']) for w in opponent_context['windows']})==145
pressure_windows={(w['match_id'],w['team_id'],w['player_id']):w for w in pressure_activity['windows']}
for w in opponent_context['windows']:
    old=pressure_windows[(w['match_id'],w['team_id'],w['player_id'])]
    assert w['start_ms']==old['start_ms'] and w['end_ms']==old['end_ms']
for player,old in zip(opponent_context['players'],pressure_activity['players']):
    assert all(player[k]==v for k,v in old.items())
    windows=[w for w in opponent_context['windows'] if (w['team_id'],w['player_id'])==(player['team_id'],player['player_id'])]
    assert player==context_module.summarize(old,windows)
    if player['opponent_eligible_attempts']:
        assert math.isclose(player['pressures_per90'],player['opponent_attempts_per90']*player['pressures_per100_opponent_attempts']/100)
assert (ROOT/'reports/57_fullback_opponent_pass_context.md').read_text()==context_module.render_report(opponent_context)
if all((ROOT/m['raw_input']['relative_path']).exists() for m in playing_time['match_audits']):
    assert opponent_context==context_module.build_evidence(allow_download=False)
print('PASS: same-window opponent attempts, preserved pressure counts and contextual exposure ratios reconcile.')

pressure_areas=read('75_fullback_pressure_areas_evidence.json')
assert hashlib.sha256((ROOT/pressure_areas['source_path']).read_bytes()).hexdigest()==pressure_areas['source_sha256']
assert pressure_areas['season']=='2019' and pressure_areas['competition_id']==72 and pressure_areas['season_id']==30
spec=importlib.util.spec_from_file_location('pressure_areas_audit',ROOT/'75_fullback_pressure_areas.py')
area_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(area_module)
assert pressure_areas==area_module.build_evidence()
assert len(pressure_areas['players'])==35
for player,old in zip(pressure_areas['players'],pressure_activity['players']):
    assert all(player[k]==v for k,v in old.items())
    assert sum(a['count'] for a in player['pressure_areas'])==player['mapped_pressures']
    keys=[(k['match_id'],k['event_id']) for a in player['pressure_areas'] for k in a['event_keys']]
    expected={(r['match_id'],r['event_id']) for r in pressure_activity['rows'] if (r['team_id'],r['player_id'])==(player['team_id'],player['player_id']) and r['location_valid']}
    assert len(keys)==len(set(keys)) and set(keys)==expected
    if player['mapped_pressures']:
        assert math.isclose(sum(a['share_of_mapped_pressures_pct'] for a in player['pressure_areas']),100)
assert (ROOT/'reports/58_fullback_pressure_areas.md').read_text()==area_module.render_report(pressure_areas)
print('PASS: pressure thirds partition mapped starts, preserve source profiles and reconcile location denominators.')
