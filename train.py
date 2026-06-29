import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import shap
import joblib
from sqlalchemy import create_engine
from features import load_weekly_stats, engineer_rolling_features, ALL_FEATURE_COLS

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)

FEATURE_COLS = ALL_FEATURE_COLS
LABEL_COL = 'rec_yards'
TEST_SEASON = 2025


def split_by_season(df, test_season):
    train_df = df[df['season'] < test_season]
    test_df = df[df['season'] == test_season]
    return train_df, test_df
    
    


def train_model(X_train, y_train):
    xgb = XGBRegressor(n_estimators=600, learning_rate=0.02, max_depth=4, subsample=0.8, colsample_bytree=0.8)
    return xgb.fit(X_train,y_train)


def evaluate(model, X_test, y_test):
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"Test MAE: {mae:.2f} yards")



def compute_shap(model, X):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    return shap_values
    



if __name__ == "__main__":
    # Step 1: load and engineer features
    df = load_weekly_stats()
    df = engineer_rolling_features(df)
    df = df.dropna(subset=FEATURE_COLS + ['rec_yards', 'receptions', 'rec_tds'])

    # Step 2: split by season
    train_df, test_df = split_by_season(df, TEST_SEASON)
    print(f"Train rows: {len(train_df)} | Test rows: {len(test_df)}")

    X_train = train_df[FEATURE_COLS]
    X_test = test_df[FEATURE_COLS]

    for label, filename in [
        ('rec_yards', 'model_rec_yards.pkl'),
        ('receptions', 'model_receptions.pkl'),
        ('rec_tds', 'model_rec_tds.pkl'),
    ]:
        y_train = train_df[label]
        y_test = test_df[label]
        model = train_model(X_train, y_train)
        evaluate(model, X_test, y_test)
        joblib.dump(model, filename)
        print(f"Saved {filename}")
