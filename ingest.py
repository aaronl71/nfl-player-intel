import nfl_data_py as nfl
import pandas as pd
from sqlalchemy import create_engine

CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
engine = create_engine(CONNECTION_STRING)

def test_connection():
    """Test that we can connect to the database"""
    with engine.connect():
        print("connection successful")
    pass

if __name__ == "__main__":
    test_connection()
