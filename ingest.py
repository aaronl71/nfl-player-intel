import nfl_data_py as nfl
import pandas as pd
from sqlalchemy import create_engine

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)

def ingest_players(years):
    df = nfl.import_weekly_rosters(years)
    
    df = df.rename(columns={
        "player_name": "name",
        "entry_year": "draft_year",
        "draft_number": "draft_pick",
    })
    
    # position, team, age, years_exp, height, weight, college, player_id already match
    df['draft_round'] = None
    
    df = df[['player_id', 'name', 'position', 'team', 'age', 'years_exp', 
            'height', 'weight', 'college', 'draft_year', 'draft_round', 'draft_pick']]
    
    df = df.drop_duplicates(subset='player_id')
    
    df.to_sql('players', engine, if_exists='replace', index=False)
    


def ingest_weekly_stats(years):
    df = nfl.import_weekly_data(years)
    
    df = df.rename(columns={
    'recent_team': 'team',
    'opponent_team': 'opponent',
    'attempts': 'pass_attempts',
    'passing_yards': 'pass_yards',
    'passing_tds': 'pass_tds',
    'passing_epa': 'epa_per_play',
    'carries': 'carries',
    'rushing_yards': 'rush_yards',
    'rushing_tds': 'rush_tds',
    'receiving_yards': 'rec_yards',
    'receiving_tds': 'rec_tds',
    'receiving_air_yards': 'air_yards',
    'receiving_yards_after_catch': 'yards_after_catch',
    })
    
    df['game_id'] = None
    df['home_away'] = None
    df['snap_count'] = None
    df['snap_pct'] = None
    df['routes_run'] = None
    df['route_participation'] = None
    df['yards_per_carry'] = None

    df = df[['player_id', 'season', 'week', 'game_id', 'opponent', 'home_away',
        'targets', 'receptions', 'rec_yards', 'rec_tds', 'air_yards',
        'yards_after_catch', 'target_share', 'carries', 'rush_yards',
        'rush_tds', 'yards_per_carry', 'pass_attempts', 'completions',
        'pass_yards', 'pass_tds', 'interceptions', 'epa_per_play',
        'snap_count', 'snap_pct', 'routes_run', 'route_participation']]
    df.to_sql('weekly_stats', engine, if_exists='replace', index=False)
    
##ingest_players([2020, 2021, 2022, 2023, 2024])
##ingest_weekly_stats([2020, 2021, 2022, 2023, 2024])

def ingest_schedules(years):
    df = nfl.import_schedules(years)
    df = df.rename(columns={
    'temp': 'weather_temp',
    'wind': 'weather_wind',
    'div_game': 'divisional_flag'
    })
    
    df['weather_precip'] = None
    df['primetime_flag'] = None
    
    df =df[['game_id', 'season', 'week', 'home_team', 'away_team', 
        'stadium', 'surface', 'weather_temp', 'weather_wind', 
        'weather_precip', 'primetime_flag', 'divisional_flag']]
    
    df.to_sql('schedules', engine, if_exists='replace', index=False)
#ingest_schedules([2020,2021,2022,2023,2024])

