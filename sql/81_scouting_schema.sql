PRAGMA foreign_keys = ON;
CREATE TABLE fullbacks (
    competition_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_name TEXT NOT NULL,
    player_name TEXT NOT NULL,
    side_group TEXT NOT NULL CHECK(side_group IN ('left_only','right_only','mixed')),
    role_starts INTEGER NOT NULL CHECK(role_starts >= 3),
    duration_ms INTEGER NOT NULL CHECK(duration_ms > 0),
    completed_passes INTEGER NOT NULL CHECK(completed_passes >= 0),
    attempted_passes INTEGER NOT NULL CHECK(attempted_passes >= completed_passes),
    team_completed_passes INTEGER NOT NULL CHECK(team_completed_passes >= completed_passes),
    forward_passes INTEGER NOT NULL CHECK(forward_passes BETWEEN 0 AND completed_passes),
    recorded_pressures INTEGER NOT NULL CHECK(recorded_pressures >= 0),
    PRIMARY KEY (competition_id,season_id,team_id,player_id)
);
CREATE TABLE qualifying_fixtures (
    competition_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    PRIMARY KEY (competition_id,season_id,team_id,player_id,match_id),
    FOREIGN KEY (competition_id,season_id,team_id,player_id)
      REFERENCES fullbacks(competition_id,season_id,team_id,player_id)
);
CREATE VIEW fullback_metrics AS
SELECT *,
       completed_passes * 5400000.0 / duration_ms AS completed_per90,
       forward_passes * 5400000.0 / duration_ms AS forward_per90,
       recorded_pressures * 5400000.0 / duration_ms AS pressures_per90,
       completed_passes * 100.0 / NULLIF(attempted_passes,0) AS completion_pct,
       completed_passes * 100.0 / NULLIF(team_completed_passes,0) AS team_passing_share_pct
FROM fullbacks;
