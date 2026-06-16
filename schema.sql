CREATE TABLE players (
    player_id TEXT PRIMARY KEY,
    name TEXT,
    position TEXT,
    team TEXT,
    age INTEGER,
    years_exp INTEGER,
    height INTEGER,
    weight INTEGER,
    college TEXT,
    draft_year INTEGER,
    draft_round INTEGER,
    draft_pick INTEGER
);
CREATE TABLE weekly_stats (
    player_id TEXT,
    season INTEGER,
    week INTEGER,
    game_id TEXT,
    opponent TEXT,
    home_away TEXT,
    targets INTEGER,
    receptions INTEGER,
    rec_yards INTEGER,
    rec_tds INTEGER,
    air_yards INTEGER,
    yards_after_catch INTEGER,
    target_share REAL,
    carries INTEGER,
    rush_yards INTEGER,
    rush_tds INTEGER,
    yards_per_carry REAL,
    pass_attempts INTEGER,
    completions INTEGER,
    pass_yards INTEGER,
    pass_tds INTEGER,
    interceptions INTEGER,
    epa_per_play REAL,
    snap_count INTEGER,
    snap_pct REAL,
    routes_run INTEGER,
    route_participation REAL,
    PRIMARY KEY (player_id, season, week)
);

CREATE TABLE pff_grades (
    player_id TEXT,
    season INTEGER,
    week INTEGER,
    overall_grade REAL,
    receiving_grade REAL,
    run_blocking_grade REAL,
    pass_blocking_grade REAL,
    rushing_grade REAL,
    coverage_grade REAL,
    pass_rush_grade REAL,
    run_defense_grade REAL,
    tackling_grade REAL,
    pressure_rate REAL,
    missed_tackle_rate REAL,
    PRIMARY KEY (player_id, season, week)
);

CREATE TABLE contracts (
    player_id TEXT,
    season INTEGER,
    team TEXT,
    cap_hit REAL,
    aav REAL,
    total_value REAL,
    guaranteed_money REAL,
    years_remaining INTEGER,
    dead_cap REAL,
    cap_hit_pct_of_team_cap REAL,
    PRIMARY KEY (player_id, season)
);

CREATE TABLE team_defense (
    team TEXT,
    season INTEGER,
    week INTEGER,
    pass_yards_allowed_rank INTEGER,
    rush_yards_allowed_rank INTEGER,
    pts_allowed_rank INTEGER,
    pressure_rate_allowed REAL,
    yards_per_route_allowed REAL,
    epa_allowed_per_play REAL,
    coverage_grade_rank INTEGER,
    run_defense_grade_rank INTEGER,
    PRIMARY KEY (team, season, week)
);

CREATE TABLE schedules (
    game_id TEXT PRIMARY KEY,
    season INTEGER,
    week INTEGER,
    home_team TEXT,
    away_team TEXT,
    stadium TEXT,
    surface TEXT,
    weather_temp INTEGER,
    weather_wind INTEGER,
    weather_precip REAL,
    primetime_flag BOOLEAN,
    divisional_flag BOOLEAN
);

CREATE TABLE projections (
    player_id TEXT,
    season INTEGER,
    week INTEGER,
    position TEXT,
    projected_receiving_yards REAL,
    projected_targets REAL,
    projected_rec_tds REAL,
    projected_rush_yards REAL,
    projected_carries REAL,
    projected_pass_yards REAL,
    confidence_interval_low REAL,
    confidence_interval_high REAL,
    model_version TEXT,
    generated_at TIMESTAMP,
    PRIMARY KEY (player_id, season, week)
);

CREATE TABLE valuations (
    player_id TEXT,
    season INTEGER,
    production_score REAL,
    positional_z_score REAL,
    value_per_cap_dollar REAL,
    value_rating REAL,
    positional_percentile REAL,
    war_score REAL,
    PRIMARY KEY (player_id, season)
);