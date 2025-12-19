import os
import requests
import csv
import datetime

# CONFIG
TOKEN = os.environ.get("NOAA_CDO_TOKEN")
STATION = "GHCND:USW00024233"
# DASHBOARD FILENAMES
MONTHLY_FILE = "seattle_rain_monthly.csv"
ANNUAL_FILE  = "seattle_rain_annual.csv"

def fetch_and_save(dataset, filename):
    print(f"--- Processing {dataset} ---")
    headers = {"token": TOKEN}
    params = {
        "datasetid": dataset,
        "datatypeid": "PRCP",
        "stationid": STATION,
        "startdate": "1991-01-01",
        "enddate": datetime.date.today().strftime("%Y-%m-%d"),
        "limit": 1000,
        "units": "standard"
    }
    
    response = requests.get("https://www.ncei.noaa.gov/cdo-web/api/v2/data", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json().get("results", [])
        if data:
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"SUCCESS: Saved {len(data)} rows to {filename}")
        else:
            print(f"WARNING: NOAA returned 0 results for {dataset}. Check your TOKEN or Date Range.")
    else:
        print(f"ERROR: API returned status {response.status_code}. Message: {response.text}")

if __name__ == "__main__":
    if not TOKEN:
        print("CRITICAL ERROR: NOAA_CDO_TOKEN not found in Secrets!")
    else:
        fetch_and_save("GSOM", MONTHLY_FILE)
        fetch_and_save("GSOY", ANNUAL_FILE)
