import sys
sys.path.append('./code')

from scraping.scrap import scrape_list_lta_south
from scraping.scrap import scrape_matches_details

if __name__ == "__main__":
    # Scrape the match list from the LTA South BO1 phase
    URL = "https://gol.gg/tournament/tournament-matchlist/LTA%20South%202025%20Split%202/"
    scrape_list_lta_south(URL)

    # Scrape the match details from the past matches (of 2nd split)
    input_csv = "data/raw/lta_south_matches.csv"
    output_csv = "data/raw/detailed_matches.csv"
    scrape_matches_details(input_csv, output_csv)