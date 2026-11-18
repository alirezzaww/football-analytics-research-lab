SELECT competition_id,season_id,team_id,player_id,score_state,
       SUM(duration_ms) AS duration_ms,
       SUM(duration_ms)/60000.0 AS registered_minutes,
       SUM(completed_passes) AS completed_passes,
       SUM(forward_passes) AS forward_passes,
       SUM(recorded_pressures) AS recorded_pressures,
       SUM(completed_passes)*5400000.0/NULLIF(SUM(duration_ms),0) AS completed_per90,
       SUM(forward_passes)*5400000.0/NULLIF(SUM(duration_ms),0) AS forward_per90,
       SUM(recorded_pressures)*5400000.0/NULLIF(SUM(duration_ms),0) AS pressures_per90
FROM score_state_activity
GROUP BY competition_id,season_id,team_id,player_id,score_state
ORDER BY team_id,player_id,
         CASE score_state WHEN 'Leading' THEN 1 WHEN 'Drawing' THEN 2 ELSE 3 END;
