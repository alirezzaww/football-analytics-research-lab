-- Keep every role-eligible row so exclusion reasons remain inspectable.
SELECT competition_id, season_id, team_id, player_id, player_name, team_name,
       side_group, role_starts, completed_per90, forward_per90, pressures_per90,
       team_passing_share_pct,
       completed_per90 >= :min_completed_per90 AS meets_passing_floor,
       forward_per90 >= :min_forward_per90 AS meets_forward_floor,
       (completed_per90 >= :min_completed_per90
        AND forward_per90 >= :min_forward_per90) AS meets_both
FROM fullback_metrics
WHERE side_group = :side_group AND role_starts >= :min_starts
ORDER BY meets_both DESC, forward_per90 DESC, completed_per90 DESC, team_id, player_id;
