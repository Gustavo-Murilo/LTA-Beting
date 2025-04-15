import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin

base_url = "https://gol.gg/"

def get_match_list(base_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(base_url, headers=headers)
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Debug: veja se há conteúdo
    with open("page_debug.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    match_table = soup.find('table', class_='table_list')
    if match_table is None:
        print("Tabela de partidas não encontrada!")
        return []
    
    rows = match_table.find_all('tr')[1:]  # Pula o cabeçalho

    matches = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue

        base_url = "https://gol.gg/"

        # Extrai o atributo href da tag <a> da coluna desejada
        raw_href = cols[0].find('a', href=True)['href']
        segments = raw_href.strip("/").split("/")
        desired_segments = segments[1:]

        url = base_url + '/'.join(desired_segments) + '/'

        match = {
            "team1":  cols[1].text.strip(),
            "team2":  cols[3].text.strip(),
            "wins1": cols[2].text.strip()[0],
            "wins2": cols[2].text.strip()[-1],
            "week":   cols[4].text.strip()[-1],
            "date":   cols[6].text.strip(),
            "url":    url
        }
        matches.append(match)

    return matches

def scrape_lta_south(base_url):
    matches = get_match_list(base_url)
    print(f"{len(matches)} partidas encontradas.")

    df = pd.DataFrame(matches)
    df.to_csv("data/raw/lta_south_matches.csv", index=False)
    print("Scraping finalizado.")