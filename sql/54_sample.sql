-- Retrieve a small, explicitly ordered preview.
SELECT opponent, period, minute, second, phase_shots, has_phase_shot
FROM corners
ORDER BY match_date, period, minute, second, corner_id
LIMIT 5;
