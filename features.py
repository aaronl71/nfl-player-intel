import pandas as pd
from sqlalchemy import create_engine, text

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)


def load_weekly_stats():
    query = """
        SELECT w.*
        FROM pbp_weekly w
        JOIN players p ON w.player_id = p.player_id
        WHERE p.position IN ('WR', 'TE')
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


def engineer_rolling_features(df):
    df = df.sort_values(['player_id', 'season', 'week'])

    def roll(col, n):
        return df.groupby('player_id')[col].transform(lambda x: x.shift(1).rolling(n).mean())

    # existing features
    df['targets_roll3']      = roll('targets', 3)
    df['rec_yards_roll3']    = roll('rec_yards', 3)
    df['target_share_roll3'] = roll('target_share', 3)
    df['targets_roll5']      = roll('targets', 5)
    df['rec_yards_roll5']    = roll('rec_yards', 5)
    df['target_share_roll5'] = roll('target_share', 5)
    df['receptions_roll3']   = roll('receptions', 3)
    df['receptions_roll5']   = roll('receptions', 5)
    df['rec_tds_roll3']      = roll('rec_tds', 3)
    df['rec_tds_roll5']      = roll('rec_tds', 5)

    # new PBP-derived features
    df['epa_per_target_roll3']   = roll('epa_per_target', 3)
    df['epa_per_target_roll5']   = roll('epa_per_target', 5)
    df['adot_roll3']             = roll('adot', 3)
    df['adot_roll5']             = roll('adot', 5)
    df['red_zone_targets_roll3'] = roll('red_zone_targets', 3)
    df['red_zone_targets_roll5'] = roll('red_zone_targets', 5)
    df['yac_per_rec_roll3']      = roll('yac', 3)
    df['yac_per_rec_roll5']      = roll('yac', 5)
    df['first_down_rate_roll3']  = roll('rec_first_down_rate', 3)
    df['first_down_rate_roll5']  = roll('rec_first_down_rate', 5)

    return df


CORE_FEATURE_COLS = [
    'targets_roll3', 'rec_yards_roll3', 'target_share_roll3',
    'targets_roll5', 'rec_yards_roll5', 'target_share_roll5',
    'receptions_roll3', 'receptions_roll5',
    'rec_tds_roll3', 'rec_tds_roll5',
]

ALL_FEATURE_COLS = CORE_FEATURE_COLS + [
    'epa_per_target_roll3', 'epa_per_target_roll5',
    'adot_roll3', 'adot_roll5',
    'red_zone_targets_roll3', 'red_zone_targets_roll5',
    'yac_per_rec_roll3', 'yac_per_rec_roll5',
    'first_down_rate_roll3', 'first_down_rate_roll5',
]

def build_feature_matrix(df):
    label_col = 'rec_yards'
    df = df.dropna(subset=CORE_FEATURE_COLS + [label_col])

    X = df[ALL_FEATURE_COLS]
    y = df[label_col]
    return X, y


if __name__ == "__main__":
    df = load_weekly_stats()
    df = engineer_rolling_features(df)
    X, y = build_feature_matrix(df)
    print(f"Feature matrix shape: {X.shape}")
    print(f"Label shape: {y.shape}")
    print(X.head())
