-- Filter before ranking: peer counts and ranks refer to the returned eligible pool.
-- Rank one means highest passing ACTIVITY, not best player.
WITH eligible AS (
    SELECT * FROM fullback_metrics
    WHERE (:side_group IS NULL OR side_group = :side_group)
      AND role_starts >= :min_starts
)
SELECT competition_id, season_id, team_id, player_id, team_name, player_name,
       side_group, role_starts, duration_ms, completed_passes,
       completed_per90, forward_per90, pressures_per90,
       completion_pct, team_passing_share_pct,
       COUNT(*) OVER (PARTITION BY side_group) AS eligible_peers,
       DENSE_RANK() OVER (
           PARTITION BY side_group ORDER BY completed_per90 DESC
       ) AS passing_activity_rank
FROM eligible
ORDER BY side_group, passing_activity_rank, team_name, player_name, team_id, player_id;
