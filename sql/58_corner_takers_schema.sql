-- One taker label for each corner, using the complete corner identity.
CREATE TABLE corner_takers (
    match_id INTEGER NOT NULL,
    corner_id TEXT NOT NULL,
    passer TEXT NOT NULL CHECK (length(trim(passer)) > 0),
    PRIMARY KEY (match_id, corner_id),
    FOREIGN KEY (match_id, corner_id) REFERENCES corners (match_id, corner_id)
);
