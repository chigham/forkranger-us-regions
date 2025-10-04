import pprint
import time
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def season_starts_and_ends(months, months_list):
    """
    Given a list of available months (strings), return a dict mapping
    month -> label ("Prime Time", "Starting Now", "Last Chance", or "").
    Handles wraparound (Dec→Jan) and full-year cases.
    """
    if not months:
        return {m: "" for m in months_list}

    # Convert to indices (0 = January, ..., 11 = December)
    month_indices = sorted(months_list.index(m) for m in months)

    # Full year
    if len(month_indices) == 12:
        return {m: "Prime Time" for m in months_list}

    # --- Find contiguous blocks with wraparound support ---
    blocks = []
    block = [month_indices[0]]

    for idx in month_indices[1:]:
        if idx == block[-1] + 1:
            block.append(idx)
        else:
            blocks.append(block)
            block = [idx]
    blocks.append(block)

    # Wraparound case: if first block starts at 0 (Jan) and last ends at 11 (Dec), merge them
    if blocks[0][0] == 0 and blocks[-1][-1] == 11:
        merged = blocks[-1] + blocks[0]
        blocks = [merged] + blocks[1:-1]

    # --- Label months ---
    labels = {i: "Prime Time" for i in month_indices}

    for b in blocks:
        if len(b) == 1:
            continue  # single month stays "Prime Time"
        start, end = b[0], b[-1]
        labels[start] = "Starting Now"
        labels[end] = "Last Chance"

    # Return dict with proper month names
    return {month: labels.get(i, "") for i, month in enumerate(months_list)}

# Setup headless browser only once
options = Options()
options.add_argument("--headless=new")  # "new" avoids some deprecation warnings
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), 
    options=options
)

start = datetime.now()

content = {}
states = ["alabama", "alaska", "arizona", "arkansas", "northern-california", "southern-california", "colorado", "connecticut", "delaware", "north-florida", "south-florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada", "new-hampshire", "new-jersey", "new-mexico", "new-york", "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode-island", "south-carolina", "south-dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "washington-dc", "west-virginia", "wisconsin", "wyoming"]
base_url = "https://www.seasonalfoodguide.org"

for state in states:
    state_dict = {}
    state_home_url = f"{base_url}/state/{state}"
    print(f"Scraping from {state_home_url} ...")

    driver.get(state_home_url)
    time.sleep(0.25)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    veg_cards = soup.find_all("div", class_="vegCard") # Works
    for card in veg_cards:
        a_tag = card.find("a", class_="btn-outline-primary")
        if not a_tag:
            continue

        veg_url = base_url + a_tag["href"]
        driver.get(veg_url)
        time.sleep(0.1)

        veg_soup = BeautifulSoup(driver.page_source, "html.parser")

        veg_name = veg_url.split("/")[-2]

        card_div = veg_soup.find("div", class_="card")
        months = None
        if card_div:
            div_children = card_div.find_all("div", recursive=False)
            if len(div_children) >= 2:
                p_tag = div_children[1].find("p")
                if p_tag:
                    months = [m.strip() for m in p_tag.get_text(strip=True).split(",")]

        if veg_name and months:
            state_dict[veg_name] = months

    content[state] = state_dict

driver.quit()

#!pprint.pprint(content)

months_list = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

rows = []
for state, vegs in content.items():
    for veg, months in vegs.items():
        row = {"state": state, "vegetable": veg}
        month_labels = season_starts_and_ends(months, months_list)
        row.update(month_labels)
        #for month in months_list:
        #    row[month] = "Prime time" if month in months else ""
        rows.append(row)

df = pd.DataFrame(rows, columns=["state", "vegetable"] + months_list)

# Ensure all are string (object)
df = df.astype(str)

# Save to CSV without index
df.to_csv(r"C:\Users\chigham\Downloads\fork-ranger-seasonalfoodguide-source.csv", index=False)

print(datetime.now() - start)