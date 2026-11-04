-- LEFT JOIN retains corners with no phase shot. They have NULL shot fields.
SELECT c.opponent, c.corner_id, s.shot_id, s.elapsed_seconds, s.goal
FROM corners AS c
LEFT JOIN phase_shots AS s
    ON c.match_id = s.match_id AND c.corner_id = s.corner_id
ORDER BY c.match_date, c.period, c.minute, c.second, c.corner_id, s.shot_id
LIMIT 8;
