-- First produce one row per corner; then summarize those rows by opponent.
WITH shots_per_corner AS (
    SELECT match_id, corner_id, COUNT(*) AS phase_shots
    FROM phase_shots
    GROUP BY match_id, corner_id
)
SELECT c.opponent,
       COUNT(*) AS deliveries,
       SUM(CASE WHEN s.phase_shots > 0 THEN 1 ELSE 0 END) AS corners_with_shot,
       COALESCE(SUM(s.phase_shots), 0) AS phase_shots,
       100.0 * SUM(CASE WHEN s.phase_shots > 0 THEN 1 ELSE 0 END)
           / COUNT(*) AS corner_shot_rate_pct
FROM corners AS c
LEFT JOIN shots_per_corner AS s
    ON c.match_id = s.match_id AND c.corner_id = s.corner_id
GROUP BY c.opponent
ORDER BY corner_shot_rate_pct DESC, c.opponent;
