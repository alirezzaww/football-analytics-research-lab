CREATE TABLE corners (
    match_id INTEGER NOT NULL,
    corner_id TEXT NOT NULL,
    match_date TEXT NOT NULL,
    opponent TEXT NOT NULL,
    period INTEGER NOT NULL CHECK (period BETWEEN 1 AND 4),
    minute INTEGER NOT NULL CHECK (minute >= 0),
    second INTEGER NOT NULL CHECK (second BETWEEN 0 AND 59),
    phase_shots INTEGER NOT NULL CHECK (phase_shots >= 0),
    phase_goals INTEGER NOT NULL CHECK (phase_goals BETWEEN 0 AND phase_shots),
    has_phase_shot INTEGER NOT NULL CHECK (has_phase_shot IN (0, 1)),
    CHECK (has_phase_shot = (phase_shots > 0)),
    PRIMARY KEY (match_id, corner_id)
);
