"""Lesson 83: vary only the two activity floors in the existing SQL screen."""
from contextlib import closing
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parent
SOURCE='data/82_scouting_role_screen_evidence.json'
PROTOCOL='data/83_screen_sensitivity_protocol.json'
spec=importlib.util.spec_from_file_location('screen82',ROOT/'82_scouting_role_screen.py')
screen_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(screen_module)
READING='https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html'


def key(row):
    return row['team_id'],row['player_id']


def validate_grid(grid,baseline):
    for field,base_field in (('completed_per90_floors','min_completed_per90'),('forward_per90_floors','min_forward_per90')):
        values=grid[field]
        if (not isinstance(values,list) or not values
                or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in values)
                or values!=sorted(set(values)) or baseline[base_field] not in values):
            raise ValueError('Scenario grid must be sorted, unique, finite, nonnegative and include baseline')


def scenario_results(connection,baseline_evidence,grid):
    base=baseline_evidence['parameters'];validate_grid(grid,base)
    eligible={key(r):r for r in baseline_evidence['eligible_rows']}
    if len(eligible)!=len(baseline_evidence['eligible_rows']):raise ValueError('Duplicate baseline identity')
    baseline_keys={key(r) for r in baseline_evidence['selected_rows']}
    results=[]
    for completed in grid['completed_per90_floors']:
        for forward in grid['forward_per90_floors']:
            parameters={**base,'min_completed_per90':completed,'min_forward_per90':forward}
            protocol={'competition_id':72,'season_id':30,'season':'2019',**parameters}
            rows=screen_module.screen(connection,protocol)
            if {key(r) for r in rows}!=set(eligible) or len(rows)!=len(eligible):raise ValueError('Scenario changed eligible pool')
            for r in rows:
                if any(r[field]!=eligible[key(r)][field] for field in ('completed_per90','forward_per90','role_starts','side_group')):
                    raise ValueError('Scenario changed underlying data or scope')
            selected={key(r) for r in rows if r['meets_both']}
            if completed==base['min_completed_per90'] and forward==base['min_forward_per90'] and selected!=baseline_keys:
                raise ValueError('Baseline screen did not reproduce')
            results.append({'parameters':parameters,'selected_count':len(selected),
                            'selected_keys':[list(k) for k in sorted(selected)],
                            'added_vs_baseline':[list(k) for k in sorted(selected-baseline_keys)],
                            'removed_vs_baseline':[list(k) for k in sorted(baseline_keys-selected)]})
    return results


def memberships(eligible,cases,baseline_selected):
    keys={key(r) for r in eligible}
    if len(keys)!=len(eligible) or not cases:raise ValueError('Unique eligible profiles and scenarios required')
    for case in cases:
        selected=[tuple(k) for k in case['selected_keys']]
        if len(selected)!=len(set(selected)) or not set(selected)<=keys or len(selected)!=case['selected_count']:
            raise ValueError('Scenario membership/count is inconsistent')
    baseline={key(r) for r in baseline_selected}
    if not baseline<=keys:raise ValueError('Baseline selection outside pool')
    profiles=[]
    for row in eligible:
        selected=[key(row) in {tuple(k) for k in case['selected_keys']} for case in cases]
        profiles.append({**row,'baseline_selected':key(row) in baseline,'case_membership':selected,
                         'selected_case_count':sum(selected),'case_count':len(cases)})
    if sum(p['selected_case_count'] for p in profiles)!=sum(c['selected_count'] for c in cases):
        raise ValueError('Scenario and profile totals disagree')
    return profiles


def build_evidence():
    baseline=json.loads((ROOT/SOURCE).read_text());grid=json.loads((ROOT/PROTOCOL).read_text())
    source_path=ROOT/baseline['source_path']
    if hashlib.sha256(source_path.read_bytes()).hexdigest()!=baseline['source_sha256']:raise ValueError('Database source changed')
    if hashlib.sha256((ROOT/baseline['query_path']).read_bytes()).hexdigest()!=baseline['query_sha256']:raise ValueError('Screen query changed')
    source=json.loads(source_path.read_text())
    for record in source['sql_files'].values():
        if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Database SQL changed')
    with closing(sqlite3.connect(':memory:')) as connection:
        screen_module.database.create_database(connection,source['rows'])
        cases=scenario_results(connection,baseline,grid)
    return {'competition':baseline['competition'],'season':'2019','competition_id':72,'season_id':30,
            'course_reading':baseline['course_reading'],
            'source_path':SOURCE,'source_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
            'protocol_path':PROTOCOL,'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL).read_bytes()).hexdigest(),
            'baseline_parameters':baseline['parameters'],'grid':grid,'cases':cases,
            'profiles':memberships(baseline['eligible_rows'],cases,baseline['selected_rows']),
            'scope':'Sensitivity to two chosen activity cutoffs only. Same 14 right-sided profiles, minimum three starts, same data and fixed forward-pass definition. Scenario inclusion counts are not probabilities, confidence intervals, future reliability or evidence of player quality. No optimal cutoff is selected; original screen unchanged.'}


def render_report(evidence):
    names={key(p):p['player_name'] for p in evidence['profiles']}
    def names_for(keys):return ', '.join(names[tuple(k)] for k in keys) or 'None'
    base=evidence['baseline_parameters']
    original=next(c for c in evidence['cases'] if c['parameters']==base)
    higher=max(evidence['grid']['forward_per90_floors'])
    strict=next(c for c in evidence['cases'] if c['parameters']['min_completed_per90']==base['min_completed_per90'] and c['parameters']['min_forward_per90']==higher)
    removed={tuple(k) for k in original['selected_keys']}-{tuple(k) for k in strict['selected_keys']}
    detail=(f"At the original completed-pass floor {base['min_completed_per90']:g}, raising the forward floor from {base['min_forward_per90']:g} to {higher:g} changes the list from {original['selected_count']} to {strict['selected_count']}; removed profiles: {names_for(sorted(removed))}." if higher>base['min_forward_per90'] else 'The scenario grid contains no higher forward floor than the baseline.')
    passing_changes=any(len({tuple(tuple(k) for k in c['selected_keys']) for c in evidence['cases'] if c['parameters']['min_forward_per90']==f})>1 for f in evidence['grid']['forward_per90_floors'])
    if not passing_changes:detail+=' Changing the completed-pass floor within the tested range does not change membership at any fixed tested forward floor.'
    cases='\n'.join(f"- Completed≥{c['parameters']['min_completed_per90']:g}, forward≥{c['parameters']['min_forward_per90']:g}: **{c['selected_count']} profiles**; added: {names_for(c['added_vs_baseline'])}; removed: {names_for(c['removed_vs_baseline'])}." for c in evidence['cases'])
    profiles='\n'.join(f"- **{p['player_name']}**: {p['completed_per90']:.2f} completed/90, {p['forward_per90']:.2f} fixed-rule forward/90; selected in **{p['selected_case_count']}/{p['case_count']} tested scenarios**; original selection {'yes' if p['baseline_selected'] else 'no'}." for p in sorted(evidence['profiles'],key=lambda p:(-p['selected_case_count'],p['player_name'])))
    return f'''# Does a small cutoff change alter the scouting screen?

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Case study: spreadsheet scouting]({READING}). This is a custom sensitivity extension of our SQL tool.

We keep the original 14 right-sided profiles, minimum 3 starts, all player data and metric definitions fixed. Only completed-pass floors 28/30/32 per 90 and fixed-rule forward floors 2.8/3.0/3.2 per 90 vary, giving nine scenarios. The original 30/3 case is included and checked against lesson82. These are illustrative neighbourhood choices; changing to another grid can change scenario inclusion counts.

## Results by scenario

{detail}

{cases}

![Shortlist sizes under nine cutoff combinations](../figures/69_scouting_screen_sensitivity.png)

## Membership across the chosen scenarios

{profiles}

## Interpretation

A profile can sit close to a chosen line without a meaningful football difference from one just below it. Assess the actual values and circumstances rather than interpreting binary membership as ability. Inclusion in all tested cases means only that the selected floors did not remove the profile. Six of nine cases is not a two-thirds probability of suitability, and these cases are not independent samples or fresh validation.

The original shortlist and data remain unchanged. The exercise does not test sensitivity to the three-start rule, starting-role classification, minutes reconstruction, forward-pass definition, match composition, missing events, opponent strength or future seasons. It neither picks an optimal cutoff nor confirms signings. All comparisons use unrounded values; the chart reports counts, not uncertainty.

## Reproduce

Run `python 83_scouting_screen_sensitivity.py` in Spyder. [Scenario protocol](../{PROTOCOL}) · [Evidence, memberships and source hashes](../data/83_scouting_screen_sensitivity_evidence.json) · [Lesson](../lessons/0065-scouting-screen-sensitivity.html).
Source: StatsBomb Open Data. Assisted implementation; independent user mastery and footage review remain separate milestones.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    grid=evidence['grid'];xs=grid['forward_per90_floors'];ys=grid['completed_per90_floors']
    lookup={(c['parameters']['min_completed_per90'],c['parameters']['min_forward_per90']):c['selected_count'] for c in evidence['cases']}
    values=[[lookup[(y,x)] for x in xs] for y in ys]
    fig,ax=plt.subplots(figsize=(7,5));im=ax.imshow(values,vmin=0,vmax=len(evidence['profiles']),cmap='Blues')
    for i,y in enumerate(ys):
        for j,x in enumerate(xs):ax.text(j,i,str(values[i][j]),ha='center',va='center',fontsize=20,color='#14374b')
    ax.set_xticks(range(len(xs)),[f'{x:g}' for x in xs]);ax.set_yticks(range(len(ys)),[f'{y:g}' for y in ys])
    ax.set_xlabel('Minimum fixed-rule forward passes per 90');ax.set_ylabel('Minimum completed passes per 90')
    ax.set_title('How many profiles meet both cutoffs?\n2019 Women’s World Cup · same 14 right-sided profiles',fontsize=12)
    fig.colorbar(im,ax=ax,label='Selected profiles',ticks=[0,2,4,6,8,10,12,14])
    fig.text(.5,.025,'Nine illustrative scenarios, not probabilities or validated player-quality thresholds.\nThe original 30/3 screen is preserved. Source: StatsBomb Open Data.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.10,1,1]);fig.savefig(ROOT/'figures/69_scouting_screen_sensitivity.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/83_scouting_screen_sensitivity_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/66_scouting_screen_sensitivity.md').write_text(render_report(evidence))
    for p in evidence['profiles']:
        if p['selected_case_count']:print(p['player_name'],p['selected_case_count'],'/',p['case_count'])
    print('Scenario sizes',[c['selected_count'] for c in evidence['cases']])
    plot_evidence(evidence)


if __name__=='__main__':main()
