"""Lesson 46: hypothetical pass decisions using probability-weighted value.

Grid values come from lesson 44. Completion probabilities and choices are assumed,
not estimated from tracking, observed passing options or a completion model.
"""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def expected_change(start_value, destination_value, completion_probability, failure_value=0):
    for value in (start_value, destination_value, completion_probability, failure_value):
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError('Values and probabilities must be finite and between zero and one')
    return completion_probability * destination_value + (1 - completion_probability) * failure_value - start_value


def build_evidence():
    path = ROOT / 'data/44_first_xt_evidence.json'
    source = json.loads(path.read_text())
    values = source['model']['zone_values']
    # Chosen grid locations for a hypothetical exercise, not observed choices at an event.
    start_cell, safe_cell, risky_cell = 8, 9, 11
    start, safe, risky = [values[i] for i in (start_cell, safe_cell, risky_cell)]
    options = []
    for name, destination, probability in [('Safer option', safe, .9), ('Riskier option at 15%', risky, .15), ('Riskier option at 20%', risky, .2)]:
        options.append({'name': name, 'destination_value': destination, 'assumed_completion_probability': probability,
                        'expected_value_change': expected_change(start, destination, probability)})
    return {'source_path': path.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'start_cell': start_cell, 'safe_destination_cell': safe_cell, 'risky_destination_cell': risky_cell,
            'start_value': start, 'safe_destination_value': safe, 'risky_destination_value': risky,
            'assumed_failure_value': 0, 'options': options,
            'riskier_probability_to_break_even_with_start': start / risky,
            'riskier_probability_to_match_safer_option': .9 * safe / risky,
            'scope': 'Hypothetical decision arithmetic, not observed passing alternatives or estimated completion probabilities. Zero failure continuation is assumed; grid values are training-only estimates. No real decision-quality judgment or live recommendation.'}


def main():
    evidence = build_evidence()
    (ROOT / 'data/46_pass_decision_evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    import matplotlib.pyplot as plt
    probabilities = [i / 200 for i in range(101)]
    curve = [expected_change(evidence['start_value'], evidence['risky_destination_value'], p) for p in probabilities]
    safer = evidence['options'][0]['expected_value_change']
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot([p * 100 for p in probabilities], curve, color='#b77516', label='Riskier destination: varying assumed completion chance')
    ax.axhline(safer, color='#24658a', linestyle='--', label='Safer destination: assumed 90% completion')
    ax.axhline(0, color='#85949c', linewidth=1)
    threshold = evidence['riskier_probability_to_match_safer_option'] * 100
    ax.axvline(threshold, color='#446b57', linestyle=':', label=f'Equal expected value at {threshold:.2f}%')
    for option in evidence['options'][1:]:
        ax.scatter(option['assumed_completion_probability'] * 100, option['expected_value_change'], color='#b77516', zorder=3)
    ax.set_xlabel('Assumed completion chance of the riskier option (%)')
    ax.set_ylabel('Hypothetical expected value change')
    ax.set_title('A more valuable destination can require a harder pass\nFitted grid values; completion chances are illustrative assumptions')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(fontsize=8, loc='upper left')
    fig.text(.5, .02, 'Failure continuation assumed zero. This exercise does not identify real available options or true completion chances.\nGrid data: StatsBomb Open Data; educational position-based xT model.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .1, 1, 1])
    fig.savefig(ROOT / 'figures/48_pass_decision_expected_value.png', dpi=160)
    plt.show()
    print('Options', evidence['options'])
    print('Riskier break-even', evidence['riskier_probability_to_break_even_with_start'])
    print('Riskier match safer', evidence['riskier_probability_to_match_safer_option'])


if __name__ == '__main__':
    main()
