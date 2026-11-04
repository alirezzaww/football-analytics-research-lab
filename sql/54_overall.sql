-- One row describes ALL recorded France deliveries in this database.
-- 100.0 preserves decimal division; NULLIF leaves a zero-denominator rate undefined.
SELECT
    COUNT(*) AS deliveries,
    COALESCE(SUM(has_phase_shot), 0) AS corners_with_shot,
    COALESCE(SUM(phase_shots), 0) AS phase_shots,
    COALESCE(SUM(phase_goals), 0) AS phase_goals,
    100.0 * SUM(has_phase_shot) / NULLIF(COUNT(*), 0) AS corner_shot_rate_pct
FROM corners;
