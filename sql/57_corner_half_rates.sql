-- Use recorded periods, not minute <= 45: first-half added time is still period 1.
WITH shots_per_corner AS (
    SELECT match_id, corner_id, COUNT(*) AS phase_shots
    FROM phase_shots
    GROUP BY match_id, corner_id
), corner_facts AS (
    SELECT c.match_id, c.corner_id,
           CASE WHEN c.period = 1 THEN 'First half'
                WHEN c.period = 2 THEN 'Second half'
                ELSE 'Extra time' END AS match_phase,
           CASE WHEN c.period IN (1, 2) THEN c.period ELSE 3 END AS phase_order,
           COALESCE(s.phase_shots, 0) AS phase_shots
    FROM corners AS c
    LEFT JOIN shots_per_corner AS s
        ON c.match_id = s.match_id AND c.corner_id = s.corner_id
)
SELECT match_phase, phase_order, COUNT(*) AS deliveries,
       SUM(CASE WHEN phase_shots > 0 THEN 1 ELSE 0 END) AS corners_with_shot,
       SUM(phase_shots) AS phase_shots,
       100.0 * SUM(CASE WHEN phase_shots > 0 THEN 1 ELSE 0 END)
           / COUNT(*) AS corner_shot_rate_pct
FROM corner_facts
GROUP BY match_phase, phase_order
ORDER BY phase_order;
