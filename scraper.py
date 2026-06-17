import requests
from bs4 import BeautifulSoup


def scrape_overthecap():
    response = requests.get('https://overthecap.com/contracts')
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table', class_='sortable controls-table')
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    
    print(f"Found {len(rows)} rows")
    print(rows[0])
    
scrape_overthecap()