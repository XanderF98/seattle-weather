import os
import requests
import csv
import datetime
import time

# CONFIG
TOKEN = os.environ.get("NOAA_CDO_TOKEN")
STATION = "GHCND:USW00024233"
# DASHBOARD FILENAMES
MONTHLY_FILE = "seattle_rain_monthly.csv"
ANNUAL_FILE  = "seattle_rain_annual.csv"

def fetch_and_save(dataset, filename, start_date):
    print(f"--- Processing {dataset} ---")
    headers = {"token": TOKEN}
    params = {
        "datasetid": dataset,
        "datatypeid": "PRCP",
        "stationid": STATION,
        "startdate": start_date,
        "enddate": datetime.date.today().strftime("%Y-%m-%d"),
        "limit": 1000,
        "units": "standard"
    }
    
    # Simple retry logic for 503 errors
    for attempt in range(3):
        response = requests.get("https://www.ncei.noaa.gov/cdo-web/api/v2/data", headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get("results", [])
            if data:
                with open(filename, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                print(f"SUCCESS: Saved {len(data)} rows to {filename}")
                return
            else:
                print(f"WARNING: No data for {dataset}")
                return
        elif response.status_code == 503:
            print(f"Server busy (503), retrying in 5s... (Attempt {attempt+1})")
            time.sleep(5)
        else:
            print(f"ERROR: API returned {response.status_code}. {response.text}")
            return

if __name__ == "__main__":
    if not TOKEN:
        print("CRITICAL ERROR: NOAA_CDO_TOKEN not found!")
    else:
        # GSOM has a 10-year limit per request
        fetch_and_save("GSOM", MONTHLY_FILE, "2016-01-01")
        # GSOY has a 10-year limit per request
        fetch_and_save("GSOY", ANNUAL_FILE, "2016-01-01")
