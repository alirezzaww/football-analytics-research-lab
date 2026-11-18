SELECT competition_id, season_id, team_id, player_id,
       COUNT(*) AS qualifying_matches,
       SUM(duration_ms) AS duration_ms,
       SUM(completed_passes) AS completed_passes,
       SUM(forward_passes) AS forward_passes,
       SUM(recorded_pressures) AS recorded_pressures,
       SUM(completed_passes)*5400000.0/SUM(duration_ms) AS completed_per90,
       SUM(forward_passes)*5400000.0/SUM(duration_ms) AS forward_per90,
       AVG(forward_passes*5400000.0/duration_ms) AS unweighted_mean_match_forward_per90,
       MIN(forward_passes*5400000.0/duration_ms) AS observed_min_match_forward_per90,
       MAX(forward_passes*5400000.0/duration_ms) AS observed_max_match_forward_per90
FROM match_activity
GROUP BY competition_id,season_id,team_id,player_id
ORDER BY team_id,player_id;
