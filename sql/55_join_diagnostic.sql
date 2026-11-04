-- COUNT(*) counts JOINED ROWS here, not unique corner deliveries.
SELECT
    COUNT(*) AS joined_rows,
    COUNT(s.shot_id) AS linked_shot_rows,
    COALESCE(SUM(CASE WHEN s.shot_id IS NULL THEN 1 ELSE 0 END), 0) AS corners_without_phase_shot
FROM corners AS c
LEFT JOIN phase_shots AS s
    ON c.match_id = s.match_id AND c.corner_id = s.corner_id;
