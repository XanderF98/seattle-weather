#!/usr/bin/env python3
import os
import sys
import csv
import datetime
import requests

# --- Config ---
TOKEN = os.environ.get("NOAA_CDO_TOKEN")
BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"
STATION = "GHCND:USW00024233"
START = os.environ.get("NOAA_START_DATE") or "1991-01-01"
END = os.environ.get("NOAA_END_DATE") or datetime.date.today().strftime("%Y-%m-%d")

# EXACT FILENAMES (No 'docs/' prefix)
MONTHLY_FILE = "seattle_monthly_rain.csv"
ANNUAL_FILE  = "seattle_annual_rain.csv"

if not TOKEN:
    print("ERROR: NOAA_CDO_TOKEN is missing!")
    sys.exit(1)

HEADERS = {"token": TOKEN}

def fetch_data(datasetid, datatypeid):
    params = {
        "datasetid": datasetid,
        "datatypeid": datatypeid,
        "stationid": STATION,
        "startdate": START,
        "enddate": END,
        "units": "standard",
        "limit": 1000
    }
    print(f"Fetching {datasetid}...")
    try:
        r = requests.get(f"{BASE}/data", headers=HEADERS, params=params, timeout=60)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        print(f"  ! Error or no data for {datasetid}: {e}")
        return []

def save_csv(data, filename):
    if not data:
        print(f"  ! Skipping {filename} (no data to save)")
        return
    keys = data[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"  > Successfully saved to root: {filename}")

def main():
    print(f"Range: {START} to {END}")
    
    # 1. Monthly
    m_data = fetch_data("GSOM", "PRCP")
    save_csv(m_data, MONTHLY_FILE)
    
    # 2. Annual
    a_data = fetch_data("GSOY", "PRCP")
    save_csv(a_data, ANNUAL_FILE)

if __name__ == "__main__":
    main()
