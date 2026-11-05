-- A violation count of zero means this particular check passed.
SELECT 'nonempty_corners' AS check_name,
       CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END AS violation_count
FROM staging_corners
UNION ALL
SELECT 'duplicate_corner_keys', COUNT(*) FROM (
    SELECT match_id, corner_id FROM staging_corners
    GROUP BY match_id, corner_id HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'duplicate_shot_keys', COUNT(*) FROM (
    SELECT match_id, shot_id FROM staging_shots
    GROUP BY match_id, shot_id HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'duplicate_taker_keys', COUNT(*) FROM (
    SELECT match_id, corner_id FROM staging_takers
    GROUP BY match_id, corner_id HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'missing_taker_records', COUNT(*) FROM staging_corners AS c
WHERE NOT EXISTS (
    SELECT 1 FROM staging_takers AS t
    WHERE t.match_id = c.match_id AND t.corner_id = c.corner_id
)
UNION ALL
SELECT 'unknown_taker_corners', COUNT(*) FROM staging_takers AS t
WHERE NOT EXISTS (
    SELECT 1 FROM staging_corners AS c
    WHERE c.match_id = t.match_id AND c.corner_id = t.corner_id
)
UNION ALL
SELECT 'unknown_shot_corners', COUNT(*) FROM staging_shots AS s
WHERE NOT EXISTS (
    SELECT 1 FROM staging_corners AS c
    WHERE c.match_id = s.match_id AND c.corner_id = s.corner_id
)
UNION ALL
SELECT 'blank_taker_names', COUNT(*) FROM staging_takers
WHERE passer IS NULL OR length(trim(passer)) = 0
UNION ALL
SELECT 'missing_identity_fields',
    (SELECT COUNT(*) FROM staging_corners
     WHERE match_id IS NULL OR corner_id IS NULL OR length(trim(corner_id)) = 0)
  + (SELECT COUNT(*) FROM staging_shots
     WHERE match_id IS NULL OR shot_id IS NULL OR corner_id IS NULL
        OR length(trim(shot_id)) = 0 OR length(trim(corner_id)) = 0)
  + (SELECT COUNT(*) FROM staging_takers
     WHERE match_id IS NULL OR corner_id IS NULL OR length(trim(corner_id)) = 0);
