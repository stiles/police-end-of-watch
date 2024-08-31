import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm

# Load the existing DataFrame
df = pd.read_json('data/processed/us_slain_police_officers_archive_1900_present.json')

# df['url'] = df['url'].apply(lambda x: "https://www.odmp.org/officer/" + x)

# Create columns to store the new data
df["incident_description"] = ""
df["age"] = ""
df["tour"] = ""
df["badge"] = ""
df["cause"] = ""
df["weapon"] = ""
df["offender"] = ""
df["lat"] = ""
df["lon"] = ""

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
for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing officers"):
    details = fetch_officer_details(row["url"])
    df.at[index, "incident_description"] = details[0]
    df.at[index, "age"] = details[1]
    df.at[index, "tour"] = details[2]
    df.at[index, "badge"] = details[3]
    df.at[index, "cause"] = details[4]
    df.at[index, "weapon"] = details[5]
    df.at[index, "offender"] = details[6]
    df.at[index, "lat"] = details[7]
    df.at[index, "lon"] = details[8]

    # Pause for 1 second to avoid overloading the server
    # time.sleep(1)

# Save the updated DataFrame to a JSON file
df['date'] = df['date'].astype(str)
df.to_json('data/processed/officer_details.json', indent=4, orient='records')