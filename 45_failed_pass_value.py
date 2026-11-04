"""Lesson 45: completed-pass xT versus an explicit zero-continuation loss scenario.

The failure score is a project diagnostic extension, not standard successful-move xT.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAILURES = {'Incomplete', 'Out', 'Pass Offside'}


def score_pass(start_value, end_value, outcome):
    if outcome is None:
        return ('Completed', end_value - start_value) if end_value is not None else ('Unscorable completed endpoint', None)
    if outcome in FAILURES:
        return 'Unsuccessful: assumed zero continuation', -start_value
    return 'Excluded unknown or injury-clearance outcome', None


def summarize(rows):
    completed = [r for r in rows if r['score_status'] == 'Completed']
    failures = [r for r in rows if r['score_status'] == 'Unsuccessful: assumed zero continuation']
    complete_sum = sum(r['scenario_value'] for r in completed)
    loss = sum(r['scenario_value'] for r in failures)
    return {'pass_attempts': len(rows), 'scored_completed': len(completed), 'scored_unsuccessful': len(failures),
            'excluded_or_unscorable': sum(r['scenario_value'] is None for r in rows),
            'completed_pass_xt_sum': complete_sum, 'assumed_failure_cost_sum': loss,
            'combined_scenario_sum': complete_sum + loss}


def build_evidence():
    path = ROOT / 'data/44_first_xt_evidence.json'
    source = json.loads(path.read_text())
    spec = importlib.util.spec_from_file_location('failed_pass_grid_source', ROOT / '44_first_expected_threat.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    assert helper.build_evidence() == source  # Verify fitted source and raw cache; no new model version.
    lookup = {record['match_id']: {e['id']: e for e in json.loads((ROOT / record['relative_path']).read_text())}
              for record in source['raw_inputs']}
    values = source['model']['zone_values']
    rows = []
    for action in source['actions']:
        if action['type'] != 'Pass':
            continue
        outcome = lookup[action['match_id']][action['id']]['pass'].get('outcome', {}).get('name')
        start = values[action['start_cell']]
        end = values[action['end_cell']] if action['end_cell'] is not None else None
        status, score = score_pass(start, end, outcome)
        rows.append({**action, 'pass_outcome': outcome, 'start_xt': start, 'recorded_endpoint_xt': end,
                     'score_status': status, 'scenario_value': score})
    france = [r for r in rows if r['team'] == "France Women's"]
    example = next((r for r in france if r['pass_outcome'] in FAILURES and r['recorded_endpoint_xt'] is not None
                    and r['recorded_endpoint_xt'] > r['start_xt']), None)
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'rule': 'Completed pass: end minus start. Incomplete/Out/Pass Offside: assume zero own-team continuation, score minus start. Unknown and Injury Clearance excluded. This failure scenario is not the standard successful-move xT metric or verified possession loss.',
            'passes': rows, 'all_selected_teams_summary': summarize(rows), 'france_summary': summarize(france),
            'illustrative_failed_pass': example,
            'scope': 'In-sample diagnostic using the same fitted grid. An unsuccessful outcome does not always imply zero actual future value; restarts, loose balls and opponent threat are not modelled. No player ranking or tactical decision-quality claim.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/45_failed_pass_value_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    summary = evidence['france_summary']
    values = [summary[k] for k in ['completed_pass_xt_sum', 'assumed_failure_cost_sum', 'combined_scenario_sum']]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(['Completed-pass\nxT sum', 'Assumed cost of\nunsuccessful passes', 'Combined\nscenario sum'], values, color=['#24658a', '#b77516', '#446b57'], width=.55)
    ax.axhline(0, color='#657b88', linewidth=1)
    for i, value in enumerate(values):
        ax.annotate(f'{value:+.3f}', (i, value), xytext=(0, 8 if value >= 0 else -15), textcoords='offset points', ha='center')
    ax.set_ylim(min(values) - 1, max(values) + 1)
    ax.set_ylabel('Sum of assigned model-value changes')
    ax.set_title('France: what changes when we assume a cost for failed passes?\nExisting five-match pass sample · same fitted xT grid')
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.5, .02, 'Failure cost assumes zero own-team continuation. This is a diagnostic extension, not standard xT.\nThe sum is not a match-performance rating or a goal forecast. Data: StatsBomb Open Data.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .10, 1, 1])
    fig.savefig(ROOT / 'figures/47_failed_pass_value.png', dpi=160)
    plt.show()
    print('All selected teams', evidence['all_selected_teams_summary'])
    print('France', summary)
    r = evidence['illustrative_failed_pass']
    if r:
        print('Example', r['player'], r['pass_outcome'], r['start_xt'], r['recorded_endpoint_xt'], r['scenario_value'])


if __name__ == '__main__':
    main()
