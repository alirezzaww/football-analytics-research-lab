"""Lesson 63: establish a role-based profiling pool for a recruitment case study."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTOCOL_PATH = 'data/63_fullback_cohort_protocol.json'
SOURCE_FILES = ['data/source_manifest.json','data/27_frozen_evaluation_evidence.json',
                'data/27_evaluation_protocol.json']
SPEC = importlib.util.spec_from_file_location('raw60',ROOT/'60_france_defensive_corners.py')
raw = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(raw)


def starting_rows(events,fixture):
    starts = [e for e in events if e['type']['name']=='Starting XI' and e['period']==1]
    if len(starts)!=2 or len({e['team']['id'] for e in starts})!=2:
        raise ValueError('Expected two distinct period-1 starting lineups')
    rows=[]
    for event in sorted(starts,key=lambda e:e['team']['id']):
        lineup=event['tactics']['lineup']
        if len(lineup)!=11 or len({p['player']['id'] for p in lineup})!=11:
            raise ValueError('Starting lineup must contain 11 distinct players')
        for entry in lineup:
            rows.append({'match_id':fixture['match_id'],'match_date':fixture['match_date'],
                         'starting_event_id':event['id'],'team_id':event['team']['id'],
                         'team_name':event['team']['name'],'player_id':entry['player']['id'],
                         'player_name':entry['player']['name'],'position_id':entry['position']['id'],
                         'position_name':entry['position']['name'],
                         'starting_formation':event['tactics']['formation']})
    return rows


def profile_pool(starters,positions,minimum_starts):
    if type(minimum_starts) is not int or minimum_starts<1:
        raise ValueError('Minimum role starts must be a positive integer')
    identities=[(r['match_id'],r['team_id'],r['player_id']) for r in starters]
    if len(set(identities))!=len(identities):
        raise ValueError('Duplicate player start in match/team')
    groups={}
    for row in starters:
        if row['position_name'] not in positions:
            continue
        key=(row['team_id'],row['player_id'])
        groups.setdefault(key,[]).append(row)
    result=[]
    for (team_id,player_id),rows in sorted(groups.items()):
        names=sorted({r['player_name'] for r in rows})
        team_names=sorted({r['team_name'] for r in rows})
        counts=Counter(r['position_name'] for r in rows)
        result.append({'team_id':team_id,'player_id':player_id,'player_name':names[0],
                       'observed_player_names':names,'team_name':team_names[0],
                       'observed_team_names':team_names,'role_starts':len(rows),
                       'position_starts':{p:counts[p] for p in positions},
                       'qualifying_match_ids':[r['match_id'] for r in rows],
                       'eligible':len(rows)>=minimum_starts})
    return result


def build_evidence(allow_download=True):
    protocol=json.loads((ROOT/PROTOCOL_PATH).read_text())
    original,evaluation,old_protocol=[json.loads((ROOT/p).read_text()) for p in SOURCE_FILES]
    records=original['raw_inputs']+evaluation['raw_inputs']
    by_match={r['match_id']:r for r in records}
    if len(by_match)!=len(records):
        raise ValueError('Raw manifests overlap')
    metadata_record=old_protocol['metadata_source']
    fixtures=raw.load_events({**metadata_record,'source_url':metadata_record['url']},allow_download)
    if len(fixtures)!=len(by_match) or {m['match_id'] for m in fixtures}!=set(by_match):
        raise ValueError('Raw manifest coverage differs from tournament metadata')
    if any(m['competition']['competition_id']!=protocol['competition_id']
           or m['season']['season_id']!=protocol['season_id'] for m in fixtures):
        raise ValueError('Fixture is outside the specified competition/season')
    starters=[]
    for fixture in sorted(fixtures,key=lambda f:(f['match_date'],f['match_id'])):
        rows=starting_rows(raw.load_events(by_match[fixture['match_id']],allow_download),fixture)
        expected_teams={fixture['home_team']['home_team_id'],fixture['away_team']['away_team_id']}
        if {r['team_id'] for r in rows}!=expected_teams:
            raise ValueError('Starting teams differ from fixture metadata')
        starters.extend(rows)
    players=profile_pool(starters,protocol['starting_positions'],protocol['minimum_role_starts'])
    eligible=[p for p in players if p['eligible']]
    return {'protocol_path':PROTOCOL_PATH,
            'protocol_sha256':hashlib.sha256((ROOT/PROTOCOL_PATH).read_bytes()).hexdigest(),
            'sources':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in SOURCE_FILES],
            'metadata_input':metadata_record,'raw_inputs':[by_match[k] for k in sorted(by_match)],
            'starter_rows':starters,'players_with_role_starts':players,'eligible_players':eligible,
            'summary':{'matches':len(fixtures),'team_lineups':len(starters)//11,
                       'starter_records':len(starters),'players_with_role_starts':len(players),
                       'eligible_players':len(eligible),
                       'excluded_below_minimum':len(players)-len(eligible),
                       'qualifying_role_start_records':sum(p['role_starts'] for p in players)},
            'scope':protocol['scope']}


def render_report(evidence):
    protocol=json.loads((ROOT/PROTOCOL_PATH).read_text())
    summary=evidence['summary']
    players=sorted(evidence['eligible_players'],key=lambda p:(p['team_name'],p['player_name'],p['player_id']))
    rows='\n'.join(f"- {p['team_name']} — {p['player_name']} (player ID {p['player_id']}): "
                   f"{p['role_starts']} qualifying starts; left back {p['position_starts']['Left Back']}, "
                   f"right back {p['position_starts']['Right Back']}." for p in players)
    return f'''# Recruitment phase: a historical fullback profiling pool

Question: which players in this tournament meet a clearly defined starting-role filter for the next fullback profiling exercise?

Across **{summary['matches']} matches**, we checked **{summary['team_lineups']} starting lineups** and **{summary['starter_records']} starting-player records**. **{summary['players_with_role_starts']} player/team identities** started at left back or right back at least once. **{summary['eligible_players']}** met our minimum of **{protocol['minimum_role_starts']} starts** in those positions; **{summary['excluded_below_minimum']}** did not.

## Eligibility rules

Use the recorded period-1 Starting XI lineup, not event locations or player reputation. Left Back and Right Back qualify; wingback and other starting positions do not. Group by player ID and team ID; preserve name variants instead of treating names as unique identifiers. Count no more than one start per player/match/team.

The minimum of three is a fixed educational sample filter, not proof of enough observations for reliable performance estimates. A player can qualify through mixed left/right starts; we retain the split and will keep role/side context visible in later profiling. Starting position does not establish the role for every subsequent minute. Substitute appearances, later tactical shifts and wingback starts are outside this filter and must not be interpreted as missing appearances.

Team tournament length, rotation, injuries and formation choices affect eligibility. Excluded players are not judged worse. This pool is not ranked by ability and is not a signability or transfer shortlist. The 2019 tournament is a historical learning dataset, not evidence of current form, age, contract status, price or availability.

## Eligible profiling pool, alphabetical by team and name

{rows}

![Distribution of qualifying starts in the initial fullback pool](../figures/58_fullback_cohort_starts.png)

## Next measurements

Audit playing-time denominators, then build role-aware passing volume, progression and completion profiles. Three starts cannot be substituted for 270 actual minutes. No performance rates, percentiles, ability recommendations or video assessments are produced in this eligibility step.

## Reproduce

Run `python 63_fullback_recruitment_cohort.py` in Spyder or locally. Existing raw event snapshots and tournament metadata are hash checked; missing files are downloaded from their recorded URLs and checked before use. All existing 52 fixtures are retained. [Protocol](../data/63_fullback_cohort_protocol.json) · [Evidence](../data/63_fullback_cohort_evidence.json) · [Short lesson](../lessons/0045-recruitment-fullback-cohort.html).

Assisted worked exercise on already inspected data. Source: StatsBomb Open Data. This custom exercise applies ideas from [Soccermatics statistical scouting](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html); it is not a claim to reproduce the course's exact assignment or a preregistered experiment. [StatsBomb specification](https://raw.githubusercontent.com/statsbomb/open-data/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf) documents Starting XI and lineup positions.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    threshold=json.loads((ROOT/PROTOCOL_PATH).read_text())['minimum_role_starts']
    counts=Counter(p['role_starts'] for p in evidence['players_with_role_starts'])
    bins=list(range(1,max(counts)+1))
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(bins,[counts[n] for n in bins],color=['#24658a' if n>=threshold else '#969fa5' for n in bins])
    for n in bins:
        ax.text(n,counts[n]+.25,str(counts[n]),ha='center')
    ax.axvline(threshold-.5,color='#b77516',linestyle='--',label=f'Exercise filter: at least {threshold} role starts')
    ax.set_xticks(bins)
    ax.set_xlabel('Recorded starts at left back or right back')
    ax.set_ylabel('Player/team identities (count)')
    ax.set_title('Who enters the historical fullback profiling pool?\nAll 52 fixtures · 2019 Women’s World Cup')
    ax.spines[['top','right']].set_visible(False)
    ax.set_ylim(0,max(counts.values())+3)
    ax.legend(frameon=False)
    fig.text(.5,.025,'Grey: below the chosen filter. Blue: included. Starts are not minutes or ability scores.\nSource: StatsBomb Open Data, Starting XI positions. No current transfer recommendation.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.10,1,1])
    fig.savefig(ROOT/'figures/58_fullback_cohort_starts.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/63_fullback_cohort_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/46_fullback_recruitment_cohort.md').write_text(render_report(evidence))
    print(evidence['summary'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
