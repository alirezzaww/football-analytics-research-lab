-- One row per corner delivery.
CREATE TABLE corners (
    match_id INTEGER NOT NULL,
    corner_id TEXT NOT NULL,
    match_date TEXT NOT NULL,
    opponent TEXT NOT NULL,
    period INTEGER NOT NULL CHECK (period BETWEEN 1 AND 4),
    minute INTEGER NOT NULL CHECK (minute >= 0),
    second INTEGER NOT NULL CHECK (second BETWEEN 0 AND 59),
    PRIMARY KEY (match_id, corner_id)
);
-- One row per shot assigned to a corner phase under the existing study rule.
CREATE TABLE phase_shots (
    match_id INTEGER NOT NULL,
    shot_id TEXT NOT NULL,
    corner_id TEXT NOT NULL,
    elapsed_seconds REAL NOT NULL CHECK (elapsed_seconds BETWEEN 0 AND 15),
    goal INTEGER NOT NULL CHECK (goal IN (0, 1)),
    PRIMARY KEY (match_id, shot_id),
    FOREIGN KEY (match_id, corner_id) REFERENCES corners (match_id, corner_id)
);
