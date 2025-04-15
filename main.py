from src.scraping.scraper import scrape_lta_south

if __name__ == "__main__":
    URL = "https://gol.gg/tournament/tournament-matchlist/LTA%20South%202024/"
    scrape_lta_south(URL)