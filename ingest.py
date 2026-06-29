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

    df['draft_round'] = None

    # sort newest first so drop_duplicates keeps the most recent roster entry per player
    df = df.sort_values(['season', 'week'], ascending=[False, False])

    df = df[['player_id', 'name', 'position', 'team', 'age', 'years_exp',
            'height', 'weight', 'college', 'draft_year', 'draft_round', 'draft_pick']]

    df = df.drop_duplicates(subset='player_id', keep='first')

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
    
##ingest_players([2020, 2021, 2022, 2023, 2024, 2025])
##ingest_weekly_stats([2020, 2021, 2022, 2023, 2024, 2025])

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
#ingest_schedules([2020,2021,2022,2023,2024,2025])

def ingest_pbp_features(years):
    PBP_COLS = ['play_type', 'complete_pass', 'first_down', 'epa',
                'air_yards', 'yards_gained', 'yardline_100',
                'receiver_player_id', 'season', 'week']
    all_dfs = []

    for year in years:
        print(f"Loading {year} PBP...")
        url = f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.parquet'
        df = pd.read_parquet(url, columns=PBP_COLS)

        df = df[(df['play_type'] == 'pass') & df['receiver_player_id'].notna()].copy()
        df['yac'] = df['yards_gained'] - df['air_yards']

        # per-player per-week aggregations
        base = df.groupby(['receiver_player_id', 'season', 'week']).agg(
            targets_pbp     = ('epa',          'count'),
            epa_per_target  = ('epa',          'mean'),
            adot            = ('air_yards',     'mean'),
            red_zone_targets= ('yardline_100',  lambda x: (x <= 20).sum()),
            first_down_rate = ('first_down',    'mean'),
        ).reset_index()

        # yac only on completions
        comp = df[df['complete_pass'] == 1].groupby(
            ['receiver_player_id', 'season', 'week']
        ).agg(yac_per_reception=('yac', 'mean')).reset_index()

        merged = base.merge(comp, on=['receiver_player_id', 'season', 'week'], how='left')
        merged = merged.rename(columns={'receiver_player_id': 'player_id'})
        all_dfs.append(merged)
        print(f"  {year}: {len(merged)} player-week rows")

    final = pd.concat(all_dfs, ignore_index=True)
    final.to_sql('pbp_features', engine, if_exists='replace', index=False)
    print(f"Done — {len(final)} total rows written to pbp_features")

##ingest_pbp_features([2020, 2021, 2022, 2023, 2024, 2025])

def build_weekly_from_pbp(years):
    NEEDED_COLS = [
        'season', 'week', 'play_type', 'posteam',
        'passer_player_id', 'receiver_player_id', 'rusher_player_id',
        'complete_pass', 'pass_attempt', 'sack',
        'yards_gained', 'air_yards', 'epa',
        'pass_touchdown', 'rush_touchdown', 'interception',
        'yardline_100', 'first_down',
    ]

    all_years = []

    for year in years:
        print(f"Processing {year}...")
        url = f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.parquet'
        df = pd.read_parquet(url, columns=NEEDED_COLS)
        df = df[df['week'].between(1, 22)].copy()

        # ── RECEIVING ──────────────────────────────────────────────
        pass_plays = df[(df['play_type'] == 'pass') & df['receiver_player_id'].notna()].copy()
        pass_plays['rec_yards_play'] = pass_plays['yards_gained'].where(pass_plays['complete_pass'] == 1, 0)
        pass_plays['yac_play'] = (pass_plays['yards_gained'] - pass_plays['air_yards']).where(pass_plays['complete_pass'] == 1, 0)

        rec = pass_plays.groupby(['receiver_player_id', 'season', 'week', 'posteam']).agg(
            targets         = ('complete_pass',   'count'),
            receptions      = ('complete_pass',   'sum'),
            rec_yards       = ('rec_yards_play',  'sum'),
            rec_tds         = ('pass_touchdown',  'sum'),
            air_yards_rec   = ('air_yards',        'sum'),
            yac             = ('yac_play',         'sum'),
            epa_per_target  = ('epa',              'mean'),
            adot            = ('air_yards',        'mean'),
            red_zone_targets= ('yardline_100',     lambda x: (x <= 20).sum()),
            rec_first_down_rate = ('first_down',   'mean'),
        ).reset_index().rename(columns={'receiver_player_id': 'player_id'})

        team_targets = pass_plays.groupby(['posteam', 'season', 'week'])['receiver_player_id'].count().reset_index()
        team_targets.columns = ['posteam', 'season', 'week', 'team_targets']
        rec = rec.merge(team_targets, on=['posteam', 'season', 'week'])
        rec['target_share'] = rec['targets'] / rec['team_targets']
        rec.drop(columns='team_targets', inplace=True)

        # ── PASSING ────────────────────────────────────────────────
        qb_plays = df[(df['play_type'] == 'pass') & df['passer_player_id'].notna()].copy()
        qb_plays['pass_yards_play'] = qb_plays['yards_gained'].where(qb_plays['complete_pass'] == 1, 0)

        qb = qb_plays.groupby(['passer_player_id', 'season', 'week', 'posteam']).agg(
            pass_attempts   = ('sack',             lambda x: (x == 0).sum()),
            completions     = ('complete_pass',    'sum'),
            pass_yards      = ('pass_yards_play',  'sum'),
            pass_tds        = ('pass_touchdown',   'sum'),
            interceptions   = ('interception',     'sum'),
            epa_per_dropback= ('epa',              'mean'),
            sacks           = ('sack',             'sum'),
        ).reset_index().rename(columns={'passer_player_id': 'player_id'})

        # ── RUSHING ────────────────────────────────────────────────
        rush_plays = df[(df['play_type'] == 'run') & df['rusher_player_id'].notna()].copy()

        rush = rush_plays.groupby(['rusher_player_id', 'season', 'week', 'posteam']).agg(
            carries             = ('yards_gained',  'count'),
            rush_yards          = ('yards_gained',  'sum'),
            rush_tds            = ('rush_touchdown','sum'),
            epa_per_carry       = ('epa',           'mean'),
            rush_first_down_rate= ('first_down',    'mean'),
        ).reset_index().rename(columns={'rusher_player_id': 'player_id'})

        # ── MERGE ──────────────────────────────────────────────────
        keys = ['player_id', 'season', 'week', 'posteam']
        weekly = rec.merge(qb,   on=keys, how='outer')
        weekly = weekly.merge(rush, on=keys, how='outer')
        all_years.append(weekly)
        print(f"  {year}: {len(weekly)} player-week rows")

    final = pd.concat(all_years, ignore_index=True)
    final.rename(columns={'posteam': 'team'}, inplace=True)
    final.to_sql('pbp_weekly', engine, if_exists='replace', index=False)
    print(f"Done — {len(final)} total rows written to pbp_weekly")

##build_weekly_from_pbp([2020, 2021, 2022, 2023, 2024, 2025])

