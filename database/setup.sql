-- Sumo Wrestling Database Schema
-- Complete data model for 1958-present professional sumo

-- Core entities
CREATE TABLE wrestlers (
    id INTEGER PRIMARY KEY,
    shikona TEXT NOT NULL,
    real_name TEXT,
    birth_date DATE,
    debut_date DATE,
    retirement_date DATE,
    height_cm INTEGER,
    weight_kg INTEGER,
    shusshin TEXT,  -- birthplace
    heya TEXT,      -- stable
    foreign_born BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tournaments (
    id TEXT PRIMARY KEY,  -- format: YYYYMM
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month IN (1,3,5,7,9,11)),
    location TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE banzuke (
    tournament_id TEXT,
    wrestler_id INTEGER,
    division TEXT NOT NULL,
    rank TEXT NOT NULL,
    rank_number INTEGER,
    east_west TEXT CHECK (east_west IN ('east', 'west')),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id),
    PRIMARY KEY (tournament_id, wrestler_id)
);

CREATE TABLE bouts (
    id INTEGER PRIMARY KEY,
    tournament_id TEXT NOT NULL,
    day INTEGER NOT NULL CHECK (day BETWEEN 1 AND 15),
    division TEXT NOT NULL,
    east_wrestler_id INTEGER NOT NULL,
    west_wrestler_id INTEGER NOT NULL,
    winner_id INTEGER NOT NULL,
    kimarite TEXT,
    match_time_seconds INTEGER,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    FOREIGN KEY (east_wrestler_id) REFERENCES wrestlers(id),
    FOREIGN KEY (west_wrestler_id) REFERENCES wrestlers(id),
    FOREIGN KEY (winner_id) REFERENCES wrestlers(id)
);

CREATE TABLE injuries (
    id INTEGER PRIMARY KEY,
    wrestler_id INTEGER NOT NULL,
    tournament_id TEXT NOT NULL,
    injury_type TEXT, -- kyujo, fusen, etc
    days_absent INTEGER DEFAULT 0,
    description TEXT,
    source TEXT,
    FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);

-- Performance aggregations
CREATE TABLE wrestler_tournaments (
    wrestler_id INTEGER,
    tournament_id TEXT,
    division TEXT,
    rank TEXT,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    absences INTEGER DEFAULT 0,
    FOREIGN KEY (wrestler_id) REFERENCES wrestlers(id),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
    PRIMARY KEY (wrestler_id, tournament_id)
);

-- Indexes for performance
CREATE INDEX idx_bouts_tournament_day ON bouts(tournament_id, day);
CREATE INDEX idx_bouts_wrestler_east ON bouts(east_wrestler_id);
CREATE INDEX idx_bouts_wrestler_west ON bouts(west_wrestler_id);
CREATE INDEX idx_bouts_winner ON bouts(winner_id);
CREATE INDEX idx_wrestlers_debut ON wrestlers(debut_date);
CREATE INDEX idx_wrestlers_heya ON wrestlers(heya);
CREATE INDEX idx_banzuke_division ON banzuke(division, rank);

-- Views for analysis
CREATE VIEW wrestler_stats AS
SELECT 
    w.id,
    w.shikona,
    w.heya,
    w.foreign_born,
    COUNT(DISTINCT wt.tournament_id) as tournaments_participated,
    SUM(wt.wins) as total_wins,
    SUM(wt.losses) as total_losses,
    SUM(wt.absences) as total_absences,
    ROUND(SUM(wt.wins) * 1.0 / (SUM(wt.wins) + SUM(wt.losses)), 3) as career_win_rate,
    MIN(wt.tournament_id) as first_tournament,
    MAX(wt.tournament_id) as last_tournament
FROM wrestlers w
LEFT JOIN wrestler_tournaments wt ON w.id = wt.wrestler_id
GROUP BY w.id, w.shikona, w.heya, w.foreign_born;

CREATE VIEW tournament_summary AS
SELECT 
    t.id,
    t.year,
    t.month,
    t.location,
    COUNT(DISTINCT b.id) as total_bouts,
    COUNT(DISTINCT b.east_wrestler_id) + COUNT(DISTINCT b.west_wrestler_id) as unique_wrestlers,
    COUNT(DISTINCT b.kimarite) as unique_kimarite
FROM tournaments t
LEFT JOIN bouts b ON t.id = b.tournament_id
GROUP BY t.id, t.year, t.month, t.location;