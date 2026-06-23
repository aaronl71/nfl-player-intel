import requests
from bs4 import BeautifulSoup
import pandas as pd

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

def scrape_overthecap():
    response = requests.get('https://overthecap.com/contracts')
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table', class_='sortable controls-table')
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    
    data = []
    
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 6:
            continue
        cols = row.find_all('td')
        name = cols[0].text.strip()
        position = cols[1].text
        team = cols[2].text
        total_value = cols[3].text
        aav = cols[4].text
        guaranteed  = cols[5].text
        
        data.append({
            'name': name,
            'position': position,
            'team': team,
            'total_value': total_value,
            'aav': aav,
            'guaranteed_money': guaranteed
        })
        
    df = pd.DataFrame(data)
    
    for col in ['total_value', 'aav', 'guaranteed_money']:
        df[col] = df[col].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(df.head())
    print(df.shape)
    
    CONNECTION_STRING = "postgresql://aaronlevy@localhost:5432/nfl_intel"
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        players_df = pd.read_sql(text("SELECT player_id, name FROM players"), conn)
    df = df.merge(players_df, on='name', how='left')
    df.to_sql('contracts', engine, if_exists='replace', index=False)
    
    print("Loaded to contracts table")
    
scrape_overthecap()