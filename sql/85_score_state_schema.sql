CREATE TABLE score_state_activity (
    competition_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    score_state TEXT NOT NULL CHECK(score_state IN ('Leading','Drawing','Trailing')),
    duration_ms INTEGER NOT NULL CHECK(duration_ms >= 0),
    completed_passes INTEGER NOT NULL CHECK(completed_passes >= 0),
    forward_passes INTEGER NOT NULL CHECK(forward_passes BETWEEN 0 AND completed_passes),
    recorded_pressures INTEGER NOT NULL CHECK(recorded_pressures >= 0),
    PRIMARY KEY (competition_id,season_id,team_id,player_id,match_id,score_state),
    FOREIGN KEY (competition_id,season_id,team_id,player_id,match_id)
      REFERENCES match_activity(competition_id,season_id,team_id,player_id,match_id)
);
