from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, text
import joblib
import json
import shap
import numpy as np
import pandas as pd
import anthropic
from dotenv import load_dotenv
from features import engineer_rolling_features, ALL_FEATURE_COLS

load_dotenv(override=True)

app = FastAPI()

FEATURE_COLS = ALL_FEATURE_COLS

FEATURE_LABELS = {
    'targets_roll3':          'Targets (3-wk avg)',
    'rec_yards_roll3':        'Rec yards (3-wk avg)',
    'target_share_roll3':     'Target share (3-wk avg)',
    'targets_roll5':          'Targets (5-wk avg)',
    'rec_yards_roll5':        'Rec yards (5-wk avg)',
    'target_share_roll5':     'Target share (5-wk avg)',
    'receptions_roll3':       'Receptions (3-wk avg)',
    'receptions_roll5':       'Receptions (5-wk avg)',
    'rec_tds_roll3':          'Receiving TDs (3-wk avg)',
    'rec_tds_roll5':          'Receiving TDs (5-wk avg)',
    'epa_per_target_roll3':   'EPA per target (3-wk avg)',
    'epa_per_target_roll5':   'EPA per target (5-wk avg)',
    'adot_roll3':             'Target depth (3-wk avg)',
    'adot_roll5':             'Target depth (5-wk avg)',
    'red_zone_targets_roll3': 'Red zone targets (3-wk avg)',
    'red_zone_targets_roll5': 'Red zone targets (5-wk avg)',
    'yac_per_rec_roll3':      'Yards after catch (3-wk avg)',
    'yac_per_rec_roll5':      'Yards after catch (5-wk avg)',
    'first_down_rate_roll3':  'First down rate (3-wk avg)',
    'first_down_rate_roll5':  'First down rate (5-wk avg)',
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)

# load once at startup — not per-request
model_yards = joblib.load("model_rec_yards.pkl")
model_rec   = joblib.load("model_receptions.pkl")
model_tds   = joblib.load("model_rec_tds.pkl")
explainer   = shap.TreeExplainer(model_yards)


@app.get("/players/")
def search_players(search: str = ""):
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM players WHERE name ILIKE :search"), {"search": f"%{search}%"})
        return [dict(row._mapping) for row in rows]


@app.get("/players/{player_id}/full")
def get_player_full(player_id: str):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT p.*, c.aav, c.total_value, c.guaranteed_money
            FROM players p
            LEFT JOIN contracts c ON p.player_id = c.player_id
            WHERE p.player_id = :player_id
        """), {"player_id": player_id}).fetchone()
        return dict(row._mapping)


@app.get("/players/{player_id}")
def get_player(player_id):
    with engine.connect() as conn:
        player = conn.execute(text("SELECT * FROM players where player_id = :player_id"), {"player_id": player_id}).fetchone()
        return dict(player._mapping)


@app.get("/projections/{player_id}")
def get_predictions(player_id):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT *
            FROM pbp_weekly
            WHERE player_id = :player_id
            ORDER BY season DESC, week DESC
            LIMIT 6
        """), {"player_id": player_id}).fetchall()

    df = pd.DataFrame(rows)
    df = engineer_rolling_features(df)
    latest = df.iloc[-1]
    X = pd.DataFrame([latest[FEATURE_COLS]], columns=FEATURE_COLS)

    shap_values = explainer.shap_values(X)[0]
    pairs = sorted(zip(FEATURE_COLS, shap_values), key=lambda x: abs(x[1]), reverse=True)[:5]
    max_abs = max(abs(v) for _, v in pairs) or 1.0

    def fmt_feature(feat, raw):
        if raw is None or (isinstance(raw, float) and np.isnan(raw)):
            return "N/A"
        if 'target_share' in feat or 'first_down_rate' in feat:
            return f"{raw * 100:.1f}%"
        elif 'rec_yards' in feat or 'adot' in feat or 'yac' in feat:
            return f"{raw:.1f} yds"
        elif 'epa' in feat:
            return f"{raw:.2f} EPA"
        elif 'rec_tds' in feat:
            return f"{raw:.2f} TDs"
        elif 'red_zone' in feat:
            return f"{raw:.1f}/gm"
        elif 'receptions' in feat:
            return f"{raw:.1f} rec"
        else:
            return f"{raw:.1f}/gm"

    top_factors = [
        {
            "label":       FEATURE_LABELS.get(feat, feat),
            "direction":   "up" if val > 0 else "down",
            "magnitude":   round(abs(val) / max_abs * 100),
            "value":       round(float(val), 1),
            "feature_val": fmt_feature(feat, X[feat].iloc[0]),
        }
        for feat, val in pairs
    ]

    return {
        "player_id": player_id,
        "projected_rec_yards":  round(float(model_yards.predict(X)[0]), 1),
        "projected_receptions": round(float(model_rec.predict(X)[0]), 1),
        "projected_rec_tds":    round(float(model_tds.predict(X)[0]), 2),
        "top_factors": top_factors,
    }


@app.get("/players/{player_id}/season_stats")
def get_season_stats(player_id: str, season: int = 2025):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT *
            FROM pbp_weekly
            WHERE player_id = :player_id AND season = :season
            ORDER BY week
        """), {"player_id": player_id, "season": season}).fetchall()

    if not rows:
        return {"season": season, "games": 0}

    df = pd.DataFrame(rows)

    def total(col):
        return float(df[col].sum()) if col in df.columns else 0.0

    targets    = total('targets')
    receptions = total('receptions')
    rec_yards  = total('rec_yards')
    rec_tds    = total('rec_tds')

    return {
        "season":      season,
        "games":       len(df),
        "targets":     int(targets),
        "receptions":  int(receptions),
        "rec_yards":   int(rec_yards),
        "rec_tds":     int(rec_tds),
        "yards_per_rec": round(rec_yards / receptions, 1) if receptions > 0 else None,
        "catch_rate":    round(receptions / targets * 100, 1) if targets > 0 else None,
    }


@app.get("/scouting/{player_id}")
def get_scouting_report(player_id: str):
    with engine.connect() as conn:
        player_row = conn.execute(text("""
            SELECT p.*, c.aav
            FROM players p
            LEFT JOIN contracts c ON p.player_id = c.player_id
            WHERE p.player_id = :player_id
        """), {"player_id": player_id}).fetchone()

    if not player_row:
        return {"error": "Player not found"}

    player = dict(player_row._mapping)
    projections = get_predictions(player_id)

    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT *
            FROM pbp_weekly
            WHERE player_id = :player_id
            ORDER BY season DESC, week DESC
            LIMIT 6
        """), {"player_id": player_id}).fetchall()

    df = pd.DataFrame(rows)
    df = engineer_rolling_features(df)
    latest = df.iloc[-1]

    def safe(val, decimals=1):
        try:
            return round(float(val), decimals) if not pd.isna(val) else "N/A"
        except Exception:
            return "N/A"

    name = player.get("name", "Unknown")

    prompt = f"""You are an NFL analyst on a network broadcast explaining a player projection to a fan who enjoys football but doesn't dig into advanced stats. The model projects {name} at {projections['projected_rec_yards']} receiving yards, {projections['projected_receptions']} receptions, and {projections['projected_rec_tds']} TDs.

Here is the underlying data — the viewer cannot see any of this, so you need to surface it as new information and explain what it means in plain terms:
- Over the last 3 games: {safe(latest.get('rec_yards_roll3'))} receiving yards/game, {safe(latest.get('targets_roll3'))} targets/game, {safe(latest.get('target_share_roll3'))}% of team targets, {safe(latest.get('receptions_roll3'))} receptions/game
- Over the last 5 games: {safe(latest.get('rec_yards_roll5'))} receiving yards/game, {safe(latest.get('targets_roll5'))} targets/game, {safe(latest.get('target_share_roll5'))}% of team targets

Write exactly 2 short paragraphs. Paragraph 1: share the recent usage and production numbers and explain in plain English what they tell you — present the stats as information the reader is learning for the first time, then connect them to why the projection lands where it does. Paragraph 2: what could realistically push the actual number above or below the projection. Keep the numbers in but explain what they mean. Conversational tone, confident, 2-3 sentences each."""

    def stream_report():
        with anthropic.Anthropic().messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text_chunk in stream.text_stream:
                yield f"data: {json.dumps(text_chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream_report(), media_type="text/event-stream")
