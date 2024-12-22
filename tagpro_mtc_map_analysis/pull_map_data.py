import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_tagpro_data(map_name, column_names):
    base_url = "https://tagpro.eu/?search=map&name={}&page={}"
    data = []
    page = 1

    while True:
        url = base_url.format(map_name, page)
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table or elements containing the match data
        table = soup.find('table')  # Adjust this selector based on actual page structure

        if not table or len(table.find_all('tr')) <= 3:  # Adjust for header and footer rows
            print(f"No match data found on page {page}. Ending scraping.")
            break

        # Extract rows and columns
        rows = table.find_all('tr')
        for row in rows[1:-1]:  # Skip header and footer rows
            cols = row.find_all('td')
            data.append([col.text.strip() for col in cols])

        print(f"Page {page} scraped successfully.")
        page += 1

        # Add a delay between requests
        time.sleep(5)

    # Convert to DataFrame using the provided column names
    if data:
        df = pd.DataFrame(data, columns=column_names)
        return df
    else:
        print("No data scraped.")
        return pd.DataFrame()


# Usage
map_name = "Polaris"
# Define your column names here
column_names = [
    "Match_ID", "Server_Flag", "Server_Name", "Map_NewestElements", "Map_Name", "Public_Private",
    "Player_Count", "Match_Datetime", "Match_Duration", "Score_Red", "Score_Blue", "Extra_Name"
]
df = scrape_tagpro_data(map_name, column_names)

# Save or analyze the DataFrame
df.to_csv(f"{map_name}_matches.csv", index=False)
print(df.head())
