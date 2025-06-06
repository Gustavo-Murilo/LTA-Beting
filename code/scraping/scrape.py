import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL for tournament data
base_url = "https://gol.gg/"


def get_match_list(base_url):
    """
    Scrapes the list of matches from the main tournament page.

    Args:
        base_url (str): The URL of the page containing the match list.

    Returns:
        dict: id, team1, team2, wins1, wins2, week, date, url.
    """
    
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Error accessing {base_url}: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the match table on the page
    match_table = soup.find('table', class_='table_list')
    if match_table is None:
        print("Match table not found!")
        return []
    
    rows = match_table.find_all('tr')[1:]  # Skip header row

    matches = []
    for i, row in enumerate(rows, 1):
        cols = row.find_all('td')
        if len(cols) < 5:
            continue

        # Extract match details from table columns
        raw_href = cols[0].find('a', href=True)['href']
        segments = raw_href.strip("/").split("/")[1:]
        url = base_url + '/'.join(segments) + '/'

        match = {
            "id":     i,
            "team1":  cols[1].text.strip(),
            "team2":  cols[3].text.strip(),
            "wins1":  cols[2].text.strip()[0],
            "wins2":  cols[2].text.strip()[-1],
            "week":   cols[4].text.strip()[-1],
            "date":   cols[6].text.strip(),
            "url":    url
        }
        matches.append(match)

    return matches


def scrape_list_lta_south(base_url):
    """
    Scrapes the list of matches and saves it to a CSV file.

    Args:
        base_url (str): The URL of the page containing the match list.
    """
    matches = get_match_list(base_url)
    print(f"{len(matches)} matches found.")

    # Save match data to a CSV file
    df = pd.DataFrame(matches)
    df.to_csv("data/raw/lta_south_matches.csv", index=False)
    print("Match list scraping completed.")


def scrape_match_details(match_url):
    """
    Scrapes detailed statistics for a single match from gol.gg.

    Args:
        match_url (str): URL of the match detail page.

    Returns:
        dict: Match data including duration, and for each team: kills, towers, dragons, barons, gold, bans, and picks.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(match_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to access {match_url}: {response.status_code}")
        return {}

    soup = BeautifulSoup(response.content, "html.parser")
    details = {}

    # Get match duration
    game_duration_divs = soup.find_all('div', class_='col-6 text-center')
    for div in game_duration_divs:
        if 'Game Time' in div.text:
            h1 = div.find('h1')
            details["duration"] = h1.text.strip() if h1 else "N/A"
            break

    # Get both teams' stat blocks
    team_blocks = soup.find_all('div', class_='col-12 col-sm-6')
    for index, block in enumerate(team_blocks[:2], start=1):
        stats = {
            "kills": "N/A",
            "towers": "N/A",
            "dragons": "N/A",
            "barons": "N/A",
            "gold": "N/A"
        }

        # Extract each stat using associated image alt text
        stat_spans = block.find_all("span", class_="score-box")
        for span in stat_spans:
            img = span.find("img")
            if not img:
                continue
            stat = img['alt'].lower()
            value = span.text.strip().split()[-1]
            if "kill" in stat:
                stats["kills"] = value
            elif "tower" in stat:
                stats["towers"] = value
            elif "dragon" in stat:
                stats["dragons"] = value
            elif "nashor" in stat or "baron" in stat:
                stats["barons"] = value
            elif "gold" in stat:
                stats["gold"] = value

        # Get bans and picks from their respective divs
        bans_div = next((div.find_next_sibling("div") for div in block.find_all("div", class_="col-2") if "Bans" in div.text), None)
        picks_div = next((div.find_next_sibling("div") for div in block.find_all("div", class_="col-2") if "Picks" in div.text), None)

        bans = [img['alt'] for img in bans_div.find_all('img')] if bans_div else []
        picks = [img['alt'] for img in picks_div.find_all('img')] if picks_div else []

        # Get dragon types by team
        dragon_types = []
        # Find the div containing the dragon stats
        stat_columns = block.find_all("div", class_="col-2")
        if len(stat_columns) >= 3:
            dragon_div = stat_columns[2]
            dragon_imgs = dragon_div.find_all("img", class_="champion_icon_XS")
            
            for img in dragon_imgs:
                alt_text = img.get('alt', '')
                if 'Drake' in alt_text or 'Dragon' in alt_text:
                    # Remove 'Drake', 'Dragon' and any extra spaces
                    dragon_type = alt_text.replace('Drake', '').replace('Dragon', '').strip()
                    if dragon_type:  # Add if isn't empty
                        dragon_types.append(dragon_type)

        # Determine first blood and first tower based on icon location
        first_blood_icon = soup.find("img", alt="First Blood")
        first_tower_icon = soup.find("img", alt="First Tower")

        details["fb"] = "N/A"
        details["ft"] = "N/A"

        if first_blood_icon:
            parent = first_blood_icon.find_parent("div", class_="col-12 col-sm-6")
            if parent == team_blocks[0]:
                details["fb"] = 1
            elif parent == team_blocks[1]:
                details["fb"] = 2

        if first_tower_icon:
            parent = first_tower_icon.find_parent("div", class_="col-12 col-sm-6")
            if parent == team_blocks[0]:
                details["ft"] = 1
            elif parent == team_blocks[1]:
                details["ft"] = 2

        # Add team-specific stats to the result dictionary
        details[f"team{index}_kills"] = stats["kills"]
        details[f"team{index}_towers"] = stats["towers"]
        details[f"team{index}_dragons"] = stats["dragons"]
        details[f"team{index}_barons"] = stats["barons"]
        details[f"team{index}_gold"] = stats["gold"]
        details[f"team{index}_bans"] = ", ".join(bans)
        details[f"team{index}_picks"] = ", ".join(picks)
        details[f"team{index}_dragon_types"] = ", ".join(dragon_types) if dragon_types else "N/A"

    return details


def scrape_matches_details(input_csv, output_csv):
    """
    Scrapes match details for each match in the input CSV and saves them to the output CSV.

    Args:
        input_csv (str): Path to the CSV containing the list of match URLs.
        output_csv (str): Path to the CSV where the match details will be saved.
    """
    df = pd.read_csv(input_csv)
    detailed_matches = []

    for index, row in df.iterrows():
        match_url = row["url"]
        if pd.isna(match_url) or match_url.strip() == "":
            print(f"Empty URL for match in row {index}")
            continue

        print(f"Processing match {index+1} - {match_url}")
        details = scrape_match_details(match_url)
        
        # Merge match details with the initial match data
        combined = row.to_dict()
        combined.update(details)
        detailed_matches.append(combined)
        time.sleep(1)  # Delay to avoid overloading the server

    df_details = pd.DataFrame(detailed_matches)
    df_details.to_csv(output_csv, index=False)
    print("Match details scraping completed. Data saved in", output_csv)


if __name__ == "__main__":
    input_csv = "data/raw/lta_south_matches.csv"
    output_csv = "data/raw/detailed_matches.csv"
    scrape_matches_details(input_csv, output_csv)
