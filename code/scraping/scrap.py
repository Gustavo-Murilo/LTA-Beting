import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def get_match_links(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = []
    for a in soup.find_all('a', href=True):
        if "game-stats" in a['href']:
            links.append("https://gol.gg" + a['href'])
    return list(set(links))  # remove duplicados


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
    match_links = get_match_links(base_url)
    all_matches = []

    for link in match_links:
        try:
            match_data = parse_match_page(link)
            all_matches.append(match_data)
            time.sleep(1)  # pausa para não sobrecarregar o site
        except Exception as e:
            print(f"Erro ao processar {link}: {e}")
    
    df = pd.DataFrame(all_matches)
    df.to_csv("data/raw/lta_south_matches.csv", index=False)
    print("Scraping finalizado. Dados salvos em CSV.")