# End of Watch
Tracking cases of law enforcement officers killed in the line of duty. 

## Process

This code in this repository collects, processes and stores information about more than 25,000 American peace officers killed in the line of duty. The data comes from the [Officer Down Memorial Page](https://www.odmp.org/info/about-odmp), a non-profit group that honors fallen law enforcement personnel.

#### Scripts

Information about the officers is fetched from [annual collection pages](https://www.odmp.org/search/year/2024) on the group's website using Python.

- `fetch_officers_historical.py`: A one-off script to fetch fallen officer information from 1900-2023. 
- `fetch_officers.py`: A script that fetches a list of officers from the current year and then combines it with the archive, removing any duplicates, and storing an updated version of the archive. 

*Scripts for analyzing trends by year, geography, department, officer type (including canines) and causes of death to come.*

#### Automation

The collection is kept current by adding new cases to a running archive with a Github Actions workflow. 

It's timed to run autotically at 6:29 pm Central Time on Sundays in memory of the late [Aubrey Hawkins](https://www.odmp.org/officer/15488-police-officer-aubrey-wright-hawkins), a police officer in Irving, Texas, who was shot and killed on Christmas Eve in 2000 while responding to a robbery-in-progress call at a sporting goods store.

## Outputs

The data are stored on Amazon S3 in CSV and JSON formats.

The json file is a list of dictionaries that contain the following items: 

```json
    {
        "officer_name":"Aubrey Wright Hawkins",
        "title":"Police",
        "department_name":"Irving Police Department",
        "state_abbreviation":"TX",
        "cause":"Gunfire",
        "date":"2000-12-24",
        "year":2000,
        "weekday":"Sunday",
        "canine":false,
        "url":"15488-police-officer-aubrey-wright-hawkins",
        "photo_url":"15488\/125\/15488.jpg"
    }
```

#### Slain officers, current year
Formats: [CSV](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_{current_year}.csv) | [JSON](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_{current_year}.json)

#### Slain officers archive, 1900-present
Formats: [CSV](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_archive_1900_present.csv) | [JSON](https://stilesdata.com/police-end-of-watch/us_slain_police_officers_archive_1900_present.json)

## Usage

To set up the project and run the data collection scripts, follow these steps:

1. Clone the repository to your local machine.

2. Install the necessary Python packages using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

3. Optional: To store data on S3, update `.github/workflows/fetch_officers.yml` with your path to S3: `s3://{YOUR_BUCKET_NAME}` and configure environment variables (passed in the workflow) in as Github secrets. S3 storage only happens when the workflow runs.
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

4. Execute scripts to fetch and process poll data and trend timeseries locally or by running the workflow:
   ```bash
   python fetch_officers.py
   ```

## Contributing

Please submit any issues or pull requests to contribute to this project.

## License

The code in this project is licensed under Creative Commons. See the [LICENSE](LICENSE) file for more details. Data usage subject to the ODMP's [terms](https://www.odmp.org/info/terms-of-use). 

## About 

The project, a work in progress, is a non-commercial exercise to analyze trends related to fallen officers and to demonstrate the process of building automated data pipelines. It is not affiliated with my employer.

Questions? [Holler](mailto:mattstiles@gmail.com)