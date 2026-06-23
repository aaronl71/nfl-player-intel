import pandas as pd
from sqlalchemy import create_engine, text

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)


def load_weekly_stats():
    query = """
        SELECT ws.*
        FROM weekly_stats ws
        JOIN players p ON ws.player_id = p.player_id
        WHERE p.position IN ('WR', 'TE')
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


def engineer_rolling_features(df):

    df = df.sort_values(['player_id', 'season', 'week'])

    df['targets_roll3'] = df.groupby('player_id')['targets'].transform(lambda x: x.shift(1).rolling(3).mean())
    df['rec_yards_roll3'] = df.groupby('player_id')['rec_yards'].transform(lambda x: x.shift(1).rolling(3).mean())
    df['target_share_roll3'] = df.groupby('player_id')['target_share'].transform(lambda x: x.shift(1).rolling(3).mean())

    df['targets_roll5'] = df.groupby('player_id')['targets'].transform(lambda x: x.shift(1).rolling(5).mean())
    df['rec_yards_roll5'] = df.groupby('player_id')['rec_yards'].transform(lambda x: x.shift(1).rolling(5).mean())
    df['target_share_roll5'] = df.groupby('player_id')['target_share'].transform(lambda x: x.shift(1).rolling(5).mean())
    return df


def build_feature_matrix(df):
    feature_cols = [
        'targets_roll3',
        'rec_yards_roll3',
        'target_share_roll3',
        'targets_roll5',
        'rec_yards_roll5',
        'target_share_roll5',
    ]

    label_col = 'rec_yards'

    df = df.dropna(subset=feature_cols)

    X = df[feature_cols]
    y = df[label_col]
    return X, y


if __name__ == "__main__":
    df = load_weekly_stats()
    df = engineer_rolling_features(df)
    X, y = build_feature_matrix(df)
    print(f"Feature matrix shape: {X.shape}")
    print(f"Label shape: {y.shape}")
    print(X.head())
