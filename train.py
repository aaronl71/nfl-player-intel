import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import shap
import joblib
from sqlalchemy import create_engine
from features import load_weekly_stats, engineer_rolling_features

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)

FEATURE_COLS = [
    'targets_roll3',
    'rec_yards_roll3',
    'target_share_roll3',
    'targets_roll5',
    'rec_yards_roll5',
    'target_share_roll5',
]
LABEL_COL = 'rec_yards'
TEST_SEASON = 2024


def split_by_season(df, test_season):
    train_df = df[df['season'] < test_season]
    test_df = df[df['season'] == test_season]
    return train_df, test_df
    
    


def train_model(X_train, y_train):
    # Create an XGBRegressor — start with these parameters:
    #   n_estimators=300, learning_rate=0.05, max_depth=4
    # Fit it on X_train and y_train
    # Return the trained model
    xgb = XGBRegressor(n_estimators=300, learning_rate=.05, max_depth=4)
    return xgb.fit(X_train,y_train)


def evaluate(model, X_test, y_test):
    # Generate predictions on X_test
    # Compute MAE against y_test using mean_absolute_error()
    # Print: "Test MAE: X.XX yards"
    
    pass


def compute_shap(model, X):
    # Create a shap.TreeExplainer using the trained model
    # Call explainer.shap_values(X) to get the values
    # Return shap_values
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    # Step 1: load and engineer features
    df = load_weekly_stats()
    df = engineer_rolling_features(df)
    df = df.dropna(subset=FEATURE_COLS)

    # Step 2: split by season
    train_df, test_df = split_by_season(df, TEST_SEASON)
    print(f"Train rows: {len(train_df)} | Test rows: {len(test_df)}")

    # Step 3: slice into X and y
    X_train = train_df[FEATURE_COLS]
    y_train = train_df[LABEL_COL]
    X_test = test_df[FEATURE_COLS]
    y_test = test_df[LABEL_COL]

    # Step 4: train
    model = train_model(X_train, y_train)

    # Step 5: evaluate
    evaluate(model, X_test, y_test)

    # Step 6: SHAP values on test set
    shap_values = compute_shap(model, X_test)
    print(f"SHAP values shape: {shap_values.shape}")

    # Step 7: save model to disk
    # Hint: joblib.dump(object, filepath)
    # YOUR CODE HERE
