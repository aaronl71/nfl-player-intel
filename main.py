from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET"],
)

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)

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


    