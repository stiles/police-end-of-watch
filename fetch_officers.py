#!/usr/bin/env python
# coding: utf-8

"""
Slain police officers in the US 
This script scrapes and processes an line-of-duty deaths 
among American police officers in the current year
from the [Officer Down Memorial Page: https://www.odmp.org.
"""

# Python tools & config
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

# Dates
current_year = int(pd.Timestamp("today").strftime("%Y"))

# Headers
headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

"""
Fetch
"""

# Get officers from current year
officer_data = []

url = f"https://www.odmp.org/search/year/{current_year}"
response = requests.get(url, headers=headers)
html_content = BeautifulSoup(response.text, "html.parser")

articles = html_content.find_all("article", class_="officer-profile-condensed")

for article in articles:
    # Get the officer's profile URL
    officer_page_url = article.find("a")["href"]

    # Get the officer's photo URL
    officer_image_url = article.find("img")["src"] if article.find("img") else None

    # Get the details
    details = article.find("div", class_="officer-short-details")
    if details:
        detail_text = details.find_all("p")

        name = detail_text[0].text if len(detail_text) > 0 else None
        agency = detail_text[1].text if len(detail_text) > 1 else None
        date = (
            detail_text[2].text.replace("EOW: ", "")
            if len(detail_text) > 2
            else None
        )
        cause = (
            detail_text[3].text.replace("Cause: ", "")
            if len(detail_text) > 3
            else None
        )

        # Store the data
        officer_data.append(
            {
                "name": name,
                "url": officer_page_url,
                "photo_url": officer_image_url,
                "agency": agency,
                "eow": date,
                "cause": cause,
            }
        )


# Convert list to a Pandas DataFrame
df = pd.DataFrame(officer_data)

"""
Process
"""

# Split the department name and location
df[["department_name", "state_abbreviation"]] = df["agency"].str.rsplit(
    ", ", n=1, expand=True
)

# Lighten dataframe by removing repeated characters from urls
df.loc[df['photo_url'].str.contains('no-photo'), 'photo_url'] = ''
df['photo_url'] = df['photo_url'].str.replace('https://www.odmp.org/media/image/officer/', '')

# Process the end-of-watch dates
df["date"] = pd.to_datetime(df["eow"]).dt.strftime('%Y-%m-%d')
df["year"] = pd.to_datetime(df["eow"]).dt.year
df["weekday"] = pd.to_datetime(df["eow"]).dt.day_name()

# Clean up stray characters
df["name"] = df["name"].str.strip()
df["department_name"] = df["department_name"].str.strip()

# Was the officer a police dog?
df["canine"] = df["name"].str.contains("K9")

# Read sample officer titles list to help split names/titles
with open("data/raw/titles.txt", "r") as file:
    titles = [line.strip() for line in file]

# Create a regex pattern to match the titles
pattern = r"\b(" + "|".join(titles) + r")\b"

# Extract the title using the pattern
df["title"] = df["name"].str.extract(pattern)

# Replace the title in the name with an empty string and strip any leading/trailing spaces
df["officer_name"] = df["name"].str.replace(pattern, "", regex=True).str.strip()

# Keep the columns we want, in the order we want
keep = [
    "name",
    "officer_name",
    "title",
    "department_name",
    "state_abbreviation",
    "cause",
    "date",
    "year",
    "weekday",
    "canine",
    "url",
    "photo_url",
]

# Drop columns we don't need
current_df = df.drop(["eow", "agency"], axis=1)[keep].copy()

# Create columns to store the new data
current_df["incident_description"] = ""
current_df["age"] = ""
current_df["tour"] = ""
current_df["badge"] = ""
current_df["cause"] = ""
current_df["weapon"] = ""
current_df["offender"] = ""
current_df["lat"] = ""
current_df["lon"] = ""

# Function to fetch details from an officer's page with error handling
def fetch_officer_details(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract name and incident description
        incident_description_section = soup.find("section", class_="officer-incident-description")
        if incident_description_section:
            incident_description = incident_description_section.find("p").text.strip()
        else:
            incident_description = None

        # Extract bio details with error handling
        bio_section = soup.find("section", class_="officer-bio")
        age, tour, badge = None, None, None

        if bio_section:
            bio_items = bio_section.find_all("li")
            for item in bio_items:
                label_span = item.find("span", class_="label")
                value_span = item.find("span", {"aria-describedby": label_span["id"]}) if label_span else None
                
                if label_span and value_span:
                    label = label_span.text.strip()
                    value = value_span.text.strip()
                    if label == "Age":
                        age = value
                    elif label == "Tour":
                        tour = value
                    elif label == "Badge":
                        badge = value
                else:
                    # Skip items like "Military Veteran" that don't have the label-value structure
                    continue
        
        # Extract incident details
        cause, weapon, offender = None, None, None
        if bio_section:
            incident_details_section = bio_section.find("div", class_="incident-details")
            if incident_details_section:
                incident_details = incident_details_section.find_all("li")
                for detail in incident_details:
                    label_span = detail.find("span", class_="label")
                    value_span = detail.find("span", {"aria-describedby": label_span["id"]}) if label_span else None
                    if label_span and value_span:
                        label = label_span.text.strip()
                        value = value_span.text.strip()
                        if label == "Cause":
                            cause = value
                        elif label == "Weapon":
                            weapon = value
                        elif label == "Offender":
                            offender = value

        # Extract lat/lon
        lat, lon = None, None
        map_data = soup.find("textarea", id="officer-map-data")
        if map_data:
            map_data = map_data.text.strip()
            lat = map_data.split('"lat":"')[1].split('"')[0]
            lon = map_data.split('"lon":"')[1].split('"')[0]

        return incident_description, age, tour, badge, cause, weapon, offender, lat, lon

    except Exception as e:
        print(f"Error fetching details for URL {url}: {e}")
        return None, None, None, None, None, None, None, None, None

# Loop through each officer's URL, fetch details, and use tqdm for progress bar
for index, row in tqdm(current_df.iterrows(), total=current_df.shape[0], desc="Processing officers"):
    details = fetch_officer_details(row["url"])
    current_df.at[index, "incident_description"] = details[0]
    current_df.at[index, "age"] = details[1]
    current_df.at[index, "tour"] = details[2]
    current_df.at[index, "badge"] = details[3]
    current_df.at[index, "cause"] = details[4]
    current_df.at[index, "weapon"] = details[5]
    current_df.at[index, "offender"] = details[6]
    current_df.at[index, "lat"] = details[7]
    current_df.at[index, "lon"] = details[8]

# Save the updated DataFrame to a JSON file
current_df['date'] = pd.to_datetime(current_df['date']).dt.strftime('%Y-%m-%d')

# Import archive and remove any from the current year
archive_src = pd.read_json('https://stilesdata.com/police-end-of-watch/us_slain_police_officers_archive_1900_present.json')
archive_src['date'] = pd.to_datetime(archive_src['date']).dt.strftime('%Y-%m-%d')
archive_df = archive_src.query(f'year!={current_year}').copy()

# Combine current year incidents with archive of those from previous years
combined_df = pd.concat([current_df, archive_df]).drop_duplicates(subset=['name', 'date']).sort_values('date')

"""
Export
"""

# Export to CSV
current_df.to_csv(
    f"data/processed/us_slain_police_officers_{current_year}.csv", index=False
)
combined_df.to_csv(
    "data/processed/us_slain_police_officers_archive_1900_present.csv", index=False
)

# Export to JSON
current_df.to_json(
    f"data/processed/us_slain_police_officers_{current_year}.json",
    indent=4,
    orient="records",
)
combined_df.to_json(
    "data/processed/us_slain_police_officers_archive_1900_present.json",
    indent=4,
    orient="records",
)