import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_info(base_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Erro ao acessar {base_url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Busca pela duração da partida
    game_duration_divs = soup.find_all('div', class_='col-6 text-center')
    game_duration = None

    for div in game_duration_divs:
        if 'Game Time' in div.text:
            h1 = div.find('h1')
            if h1:
                game_duration = h1.text.strip()
                break

    return game_duration


if __name__ == "__main__":
    URL = "https://gol.gg/game/stats/65719/page-game/"
    info = get_info(URL)
    print(f"Duração da partida: {info}")
