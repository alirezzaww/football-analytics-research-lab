-- Reduce shots to one row per corner BEFORE joining back to the delivery table.
WITH shots_per_corner AS (
    SELECT match_id, corner_id, COUNT(*) AS phase_shots, SUM(goal) AS phase_goals
    FROM phase_shots
    GROUP BY match_id, corner_id
)
SELECT
    COUNT(*) AS deliveries,
    COALESCE(SUM(CASE WHEN s.phase_shots > 0 THEN 1 ELSE 0 END), 0) AS corners_with_shot,
    COALESCE(SUM(s.phase_shots), 0) AS phase_shots,
    COALESCE(SUM(s.phase_goals), 0) AS phase_goals,
    100.0 * SUM(CASE WHEN s.phase_shots > 0 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0) AS corner_shot_rate_pct
FROM corners AS c
LEFT JOIN shots_per_corner AS s
    ON c.match_id = s.match_id AND c.corner_id = s.corner_id;
