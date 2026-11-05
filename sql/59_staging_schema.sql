-- Temporary inspection tables intentionally allow duplicates and missing links.
-- The final reporting database still uses its strict keys and constraints.
CREATE TABLE staging_corners (match_id INTEGER, corner_id TEXT);
CREATE TABLE staging_shots (match_id INTEGER, shot_id TEXT, corner_id TEXT);
CREATE TABLE staging_takers (match_id INTEGER, corner_id TEXT, passer TEXT);
