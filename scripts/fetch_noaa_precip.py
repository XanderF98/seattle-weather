import os
import requests
import csv
import datetime
import time

# CONFIG
TOKEN = os.environ.get("NOAA_CDO_TOKEN")
STATION = "GHCND:USW00024233"
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
    
    for attempt in range(3):
        response = requests.get("https://www.ncei.noaa.gov/cdo-web/api/v2/data", headers=headers, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                # CLEAN DATA FOR DASHBOARD
                cleaned_data = []
                for row in results:
                    cleaned_data.append({
                        "date": row["date"].split("T")[0], # Fixes the T00:00:00 issue
                        "value": row["value"]
                    })
                
                with open(filename, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "value"])
                    writer.writeheader()
                    writer.writerows(cleaned_data)
                print(f"SUCCESS: Saved {len(cleaned_data)} cleaned rows to {filename}")
                return
            else:
                print(f"WARNING: No data for {dataset}")
                return
        elif response.status_code == 503:
            time.sleep(5)
        else:
            print(f"ERROR: {response.status_code}")
            return

if __name__ == "__main__":
    if not TOKEN:
        print("CRITICAL ERROR: TOKEN missing")
    else:
        # Fetching last 9 years to stay under 10-year limit
        fetch_and_save("GSOM", MONTHLY_FILE, "2016-01-01")
        fetch_and_save("GSOY", ANNUAL_FILE, "2016-01-01")
