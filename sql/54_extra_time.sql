-- Periods 3 and 4 are extra time; the source has already excluded shootouts.
SELECT match_id, corner_id, opponent, period, minute, second
FROM corners
WHERE period IN (3, 4)
ORDER BY match_date, period, minute, second, corner_id;
