import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_match_list(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    match_table = soup.find('table', class_='list_match')
    rows = match_table.find_all('tr')[1:]  # Pula o cabeçalho

    matches = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 5:
            continue

        match = {
            "date": cols[0].text.strip(),
            "team1": cols[1].text.strip(),
            "team2": cols[3].text.strip(),
            "result": cols[2].text.strip(),  # Pode ser "vs", ou "W", etc.
            "game_url": "https://gol.gg" + cols[2].find('a')['href'] if cols[2].find('a') else None
        }
        matches.append(match)

    return matches


def parse_match_page(match_url):
    response = requests.get(match_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Exemplo de extração simples (ajustar conforme estrutura real da página)
    game_info = {
        "url": match_url,
        "team1": soup.find_all("div", class_="teamtext")[0].text.strip(),
        "team2": soup.find_all("div", class_="teamtext")[1].text.strip(),
        "winner": soup.find("div", class_="victory").text.strip(),
    }

    return game_info


def scrape_lta_south(base_url):
    matches = get_match_list(base_url)
    print(f"{len(matches)} partidas encontradas.")

    df = pd.DataFrame(matches)
    df.to_csv("data/raw/lta_south_matches.csv", index=False)
    print("Scraping finalizado.")