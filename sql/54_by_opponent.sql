-- Group every delivery by opponent; retain corners without a shot in the denominator.
SELECT
    opponent,
    COUNT(*) AS deliveries,
    SUM(has_phase_shot) AS corners_with_shot,
    SUM(phase_shots) AS phase_shots,
    SUM(phase_goals) AS phase_goals,
    100.0 * SUM(has_phase_shot) / COUNT(*) AS corner_shot_rate_pct
FROM corners
GROUP BY opponent
ORDER BY MIN(match_date), opponent;
