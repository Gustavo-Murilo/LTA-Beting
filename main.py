import sys
sys.path.append('./code')

from scraping.scrap import scrape_lta_south

import sys
sys.path.append('./code')

from scraping.scraper import scrape_lta_south

if __name__ == "__main__":
    URL = "https://gol.gg/tournament/tournament-matchlist/LTA%20South%202025%20Split%202/"
    scrape_lta_south(URL)