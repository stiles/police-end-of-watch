#!/usr/bin/env python
# coding: utf-8

"""
Slain police officers in the US
This script scrapes and processes an unofficial directory of more than 25,000 
line-of-duty deaths among American police officers since 1900 
from the [Officer Down Memorial Page: https://www.odmp.org.
"""

# Python tools

import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

# Dates
start_year = 1900
current_year = int(pd.Timestamp("today").strftime("%Y"))
years = [y for y in range(start_year, current_year)]

# Headers
headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

# Loop through year, extracting officer details into a list of dictionaries
officer_data = []

for year in tqdm(years):
    url = f"https://www.odmp.org/search/year/{year}"
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

df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

officers_df = df.drop(["eow", "agency"], axis=1)[keep].copy()

# Export to CSV
officers_df.to_csv(
    "data/processed/us_slain_police_officers_archive_1900_2023.csv", index=False
)

# Export to JSON
officers_df.to_json(
    "data/processed/us_slain_police_officers_archive_1900_2023.json",
    indent=4,
    orient="records",
)