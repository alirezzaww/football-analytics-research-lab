"""Lesson 70: player involvement within same-window team passing activity."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE_FILES={'minutes':'data/64_fullback_playing_time_evidence.json',
              'passing':'data/65_fullback_passing_per90_evidence.json'}
SPEC=importlib.util.spec_from_file_location('passing65',ROOT/'65_fullback_passing_per90.py')
passing=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(passing)


def count_windows(events,audit,targets):
    # Apply the earlier eligibility rule to all registered team players first.
    all_players=passing.count_match(events,audit,audit['intervals'])
    own={(r['team_id'],r['player_id']):r for r in all_players}
    lookup={e['id']:e for e in events}
    offsets={p['period']:sum(q['length_ms'] for q in audit['periods'] if q['period']<p['period']) for p in audit['periods']}
    teams={}
    for player in all_players:
        teams.setdefault(player['team_id'],[]).extend(player['completed_ids'])
    for team_id in teams:
        teams[team_id].sort(key=lambda identifier:lookup[identifier]['index'])
    rows=[]
    for interval in targets:
        begin=lookup[interval['start_event_id']]['index'];end=lookup[interval['end_event_id']]['index']
        selected=[]
        for identifier in teams[interval['team_id']]:
            event=lookup[identifier]
            when=offsets[event['period']]+passing.time_module.cohort_module.raw.scanner.timestamp_milliseconds(event['timestamp'])
            if interval['start_ms']<=when<=interval['end_ms'] and begin<=event['index']<=end:
                selected.append(identifier)
        player_ids=own[(interval['team_id'],interval['player_id'])]['completed_ids']
        if not set(player_ids)<=set(selected):
            raise ValueError('Player completions are not a subset of the same-window team completions')
        rows.append({'match_id':audit['match_id'],'team_id':interval['team_id'],'player_id':interval['player_id'],
                     'start_ms':interval['start_ms'],'end_ms':interval['end_ms'],
                     'player_completed_ids':player_ids,'team_completed_ids':selected})
    return rows


def summarize(player,windows):
    own=sum(len(w['player_completed_ids']) for w in windows)
    team=sum(len(w['team_completed_ids']) for w in windows)
    if own!=player['eligible_completed'] or own>team or player['duration_ms']<=0:
        raise ValueError('Own count or playing-time exposure differs from source')
    if {w['match_id'] for w in windows}!=set(player['qualifying_match_ids']):
        raise ValueError('Team denominator fixtures do not match player numerator fixtures')
    return {**player,'team_completed_while_registered':team,
            'share_of_team_completions_pct':100*own/team if team else None,
            'team_completions_per_player90':team/(player['duration_ms']/60000)*90}


def build_evidence(allow_download=True):
    data={k:json.loads((ROOT/p).read_text()) for k,p in SOURCE_FILES.items()}
    players=data['passing']['players'];windows=[]
    for audit in data['minutes']['match_audits']:
        keys={(p['team_id'],p['player_id']) for p in players if audit['match_id'] in p['qualifying_match_ids']}
        if not keys:continue
        targets=[r for r in audit['intervals'] if (r['team_id'],r['player_id']) in keys]
        if len(targets)!=len(keys):raise ValueError('Selected registration windows differ')
        events=passing.time_module.cohort_module.raw.load_events(audit['raw_input'],allow_download)
        windows.extend(count_windows(events,audit,targets))
    profiles=[]
    for player in players:
        selected=[w for w in windows if (w['team_id'],w['player_id'])==(player['team_id'],player['player_id'])]
        profiles.append(summarize(player,selected))
    return {'competition':data['passing']['competition'],'season':'2019','competition_id':72,'season_id':30,
            'course_reading':{'lesson':'Soccermatics Lesson 3: Statistical scouting','section':'Normalisation',
                             'url':'https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation'},
            'source_files':{k:{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for k,p in SOURCE_FILES.items()},
            'windows':windows,'players':profiles,
            'rule':'Player completed eligible passes / all same-team completed eligible passes during that player’s selected registered intervals ×100. Includes the player and goalkeeper in team counts. Same non-restart, possession-team eligibility as lesson 65. Restrict both clock and event order to the selected interval.',
            'scope':'Descriptive involvement share, not possession percentage, time in possession, fully possession-adjusted ability or causation. Original player counts and minutes unchanged. A team pass may legitimately enter both fullbacks’ separate window denominators; do not sum them as unique tournament passes.'}


def render_report(evidence):
    lines=[]
    for p in sorted(evidence['players'],key=lambda p:(p['team_name'],p['player_name'])):
        share=f"{p['share_of_team_completions_pct']:.2f}%" if p['share_of_team_completions_pct'] is not None else 'undefined'
        lines.append(f"- {p['team_name']} — {p['player_name']}: {p['eligible_completed']}/{p['team_completed_while_registered']} same-window team completions = {share}; own completions {p['completed_per90']:.2f}/90, team completions {p['team_completions_per_player90']:.2f} per selected-player 90.")
    results='\n'.join(lines)
    examples=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    worked='\n'.join(f"- {p['player_name']}: {p['eligible_completed']} / {p['team_completed_while_registered']} ×100 = {p['share_of_team_completions_pct']:.2f}%." for p in examples)
    return f'''# Fullback involvement in team passing

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30. Reading: [Soccermatics Lesson 3 — Statistical scouting, Normalisation](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation).

Question: what fraction of her team's eligible completed passes did a player make while she was registered on the pitch in the selected fixtures?

{worked}

![Activity per 90 and team passing involvement](../figures/64_fullback_team_passing_share.png)

## All 35 profiles

{results}

## Matching the denominator

The original qualifying fullback-start fixtures and registered intervals remain unchanged. We apply lesson 65's eligibility filter to all registered teammates, including the goalkeeper and the player herself. Only team completions within the target player's clock interval and event-order bounds enter her denominator. A teammate's pass after the target player was substituted off is excluded from that target's window. Player completions are checked as a subset of the corresponding team completions. Each window retains both ID lists for audit.

Counts are pooled across the player's selected windows before division; we do not average match percentages. The share is not pass completion percentage: the denominator is completed team passes, not the player's attempts. A zero-team-completion window does not create a 0% rate; if pooled exposure is zero, the share is undefined.

The identity is own completions per 90 = team completions per selected-player 90 × own share as a fraction. It decomposes observed activity; it does not prove how much opportunity or ability caused the result. A team event may appear in both fullbacks' denominators because each has a separate, valid involvement question. Summing these denominators does not give a unique tournament pass total.

## Interpretation

Per 90 standardizes playing time. This extra measure places that activity within recorded team passing volume. It is not a provider possession percentage, an estimate of minutes in possession, or a fully adjusted player ability score. Role, side, game state, passing difficulty, teammates and team style remain relevant. We have not demonstrated that higher involvement is tactically better. Registered time still includes added/extra time and temporary absences, excludes halftime and shootouts, and is not verified fullback-position time.

## Reproduce

Run `python 70_fullback_team_passing_share.py` in Spyder or locally. [Evidence](../data/70_fullback_team_passing_share_evidence.json) · [Lesson](../lessons/0052-fullback-team-passing-share.html). Source: StatsBomb Open Data, **2019 Women's World Cup**, via the existing hash-checked match snapshots. Assisted historical exercise; no ability ranking or new model.
'''


def plot_evidence(evidence):
    import matplotlib.pyplot as plt
    players=[next(p for p in evidence['players'] if p['player_id']==identifier) for identifier in (10178,15249)]
    fig,axes=plt.subplots(1,2,figsize=(11,5))
    for ax,field,title,label in (
        (axes[0],'completed_per90','Completed eligible passes per 90','Own completions per 90'),
        (axes[1],'share_of_team_completions_pct','Share of team completions while registered','Own / same-window team completions (%)')):
        values=[p[field] for p in players]
        ax.bar(range(2),values,color=['#24658a','#b77516'],width=.55)
        for i,p in enumerate(players):
            text=f"{p[field]:.2f}" if field=='completed_per90' else f"{p[field]:.2f}%\n{p['eligible_completed']}/{p['team_completed_while_registered']}"
            ax.text(i,p[field]+max(values)*.025,text,ha='center',fontsize=10)
        ax.set_xticks(range(2),[p['player_name'] for p in players])
        ax.set_ylim(0,max(values)*1.3);ax.set_title(title,fontsize=10);ax.set_ylabel(label,fontsize=9)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Passing activity and team involvement answer different questions\n2019 Women’s World Cup · unchanged selected fixtures',fontsize=14)
    fig.text(.5,.025,'Same eligibility filter and registered windows. Team totals include the player and goalkeeper.\nInvolvement is descriptive, not a possession percentage or ability grade. Source: StatsBomb Open Data.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.12,1,.88])
    fig.savefig(ROOT/'figures/64_fullback_team_passing_share.png',dpi=160)
    plt.show()


def main():
    evidence=build_evidence()
    (ROOT/'data/70_fullback_team_passing_share_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'reports/53_fullback_team_passing_share.md').write_text(render_report(evidence))
    for p in evidence['players']:
        if p['player_id'] in (10178,15249):print(p['player_name'],p['eligible_completed'],p['team_completed_while_registered'],p['share_of_team_completions_pct'])
    plot_evidence(evidence)


if __name__=='__main__':
    main()
