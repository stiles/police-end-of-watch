# End of Watch
Tracking cases of law enforcement officers killed in the line of duty. 

## Process

This code in this repository collects, processes and stores information about more than 25,000 American peace officers killed in the line of duty. The data comes from the [Officer Down Memorial Page](https://www.odmp.org/info/about-odmp), a non-profit group that honors fallen law enforcement personnel.

The project, a work in progress, is a non-commercial exercise to analyze trends related to fallen officers and to demonstrate building automated data pipelines. 

#### Scripts

Information about the officers is fetched from [annual collection pages](https://www.odmp.org/search/year/2024) on the group's website using Python.

- `fetch_officers_historical.py`: A one-off script to fetch fallen officer information from 1900-2023. 
- `fetch_officers.py`: A script that fetches a list of officers from the current year and then combines it with the archive, removing any duplicates, and storing an updated version of the archive.

*Scripts for analyzing trends by year, geography, department, officer type (including canines) and causes of death to come.*

#### Automation

The collection is kept current by adding new cases to a running archive with a Github Actions workflow. 

It's set to run autotically at 6:29 pm Central Time on Sundays in memory of the late [Aubrey Hawkins](https://www.odmp.org/officer/15488-police-officer-aubrey-wright-hawkins), a police officer in Irving, Texas, who was shot and killed on Christmas Eve in 2000 while responding to a robbery-in-progress call at a sporting goods store.

## Outputs

The data are stored on Amazon S3 in CSV and JSON formats.

#### Slain officers, current year
Formats: [CSV](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_{current_year}.csv) | [JSON](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_{current_year}.json)

#### Slain officers archive, 1900-present
Formats: [CSV](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_archive_1900_present.csv) | [JSON](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_archive_1900_present.json)