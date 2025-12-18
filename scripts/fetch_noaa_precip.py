#!/usr/bin/env python3
import os
import sys
import csv
import datetime
import requests

# --- Configuration ---
TOKEN = os.environ.get("NOAA_CDO_TOKEN")
BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"
STATION = "GHCND:USW00024233"  # Sea-Tac Airport

# Fallbacks for manual runs or missing env vars
START = os.environ.get("NOAA_START_DATE") or "1991-01-01"
END   = os.environ.get("NOAA_END_DATE") or datetime.date.today().strftime("%Y-%m-%d")

# Ensure the 'docs' directory exists so the dashboard can find files
OUTPUT_DIR = "docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MONTHLY_FILE = os.path.join(OUTPUT_DIR, "seattle_monthly_rain.csv")
ANNUAL_FILE  = os.path.join(OUTPUT_DIR, "seattle_annual_rain.csv")

if not TOKEN:
    print("ERROR: NOAA_CDO_TOKEN is required.", file=sys.stderr)
    sys.exit(1)

HEADERS = {"token": TOKEN}

def fetch_cdo_data(datasetid, datatypeid):
    """Fetch data from NOAA CDO API with basic pagination."""
    results = []
    params = {
        "datasetid": datasetid,
        "datatypeid": datatypeid,
        "stationid": STATION,
        "startdate": START,
        "enddate": END,
        "units": "standard",
        "limit": 1000
    }
    
    try:
        response = requests.get(f"{BASE}/data", headers=HEADERS, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Error fetching {datatypeid}: {e}")
        return []

def save_csv(data, filename):
    """Write the NOAA json results to a CSV file."""
    if not data:
        print(f"No data found for {filename}, skipping write.")
        return
    
    keys = data[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Successfully saved: {filename}")

def main():
    print(f"Fetching data from {START} to {END}...")
    
    # GSOM = Global Summary of the Month (PRCP = Precipitation)
    monthly_data = fetch_cdo_data("GSOM", "PRCP")
    save_csv(monthly_data, MONTHLY_FILE)
