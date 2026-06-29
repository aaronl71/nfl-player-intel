import joblib
import pandas as pd
from sqlalchemy import create_engine, text
from features import load_weekly_stats, engineer_rolling_features, ALL_FEATURE_COLS

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)

FEATURE_COLS = ALL_FEATURE_COLS
TEST_SEASON = 2025


def load_player_names():
    with engine.connect() as conn:
        return pd.read_sql(text("SELECT player_id, name FROM players"), conn)


if __name__ == "__main__":
    df = load_weekly_stats()
    df = engineer_rolling_features(df)
    df = df.dropna(subset=FEATURE_COLS + ['rec_yards', 'receptions', 'rec_tds'])

    test_df = df[df['season'] == TEST_SEASON].copy()
    X_test = test_df[FEATURE_COLS]

    model_yards = joblib.load('model_rec_yards.pkl')
    model_rec = joblib.load('model_receptions.pkl')
    model_tds = joblib.load('model_rec_tds.pkl')

    test_df['pred_rec_yards'] = model_yards.predict(X_test)
    test_df['pred_receptions'] = model_rec.predict(X_test)
    test_df['pred_rec_tds'] = model_tds.predict(X_test)
    test_df['yards_error'] = test_df['pred_rec_yards'] - test_df['rec_yards']

    test_df = test_df.merge(load_player_names(), on='player_id', how='left')

    overall_mae = test_df['yards_error'].abs().mean()
    print(f"Overall 2025 rec_yards MAE: {overall_mae:.1f} yards across {len(test_df)} player-weeks\n")

    sample = test_df.sort_values('targets', ascending=False).head(15)
    for _, row in sample.iterrows():
        print(
            f"{row['name']:<20} Wk{int(row['week']):<3}  "
            f"Predicted: {row['pred_rec_yards']:5.0f} yds / {row['pred_receptions']:.1f} rec   "
            f"Actual: {row['rec_yards']:5.0f} yds / {row['receptions']:.0f} rec   "
            f"Miss: {row['yards_error']:+.1f} yds"
        )
