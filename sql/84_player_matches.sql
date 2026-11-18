SELECT m.match_id, m.match_date, m.opponent, p.player_name, p.team_name,
       m.duration_ms, m.duration_ms/60000.0 AS registered_minutes,
       m.completed_passes, m.forward_passes, m.recorded_pressures,
       m.completed_passes*5400000.0/m.duration_ms AS completed_per90,
       m.forward_passes*5400000.0/m.duration_ms AS forward_per90,
       m.recorded_pressures*5400000.0/m.duration_ms AS pressures_per90
FROM match_activity AS m
JOIN fullbacks AS p
  ON p.competition_id=m.competition_id AND p.season_id=m.season_id
 AND p.team_id=m.team_id AND p.player_id=m.player_id
WHERE m.competition_id=72 AND m.season_id=30
  AND m.team_id=:team_id AND m.player_id=:player_id
ORDER BY m.match_date,m.match_id;
