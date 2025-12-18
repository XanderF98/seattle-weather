
#!/usr/bin/env python3
"""
Auto-fetch NOAA monthly and annual precipitation for Sea-Tac via CDO API.
Writes: seattle_rain_monthly.csv and seattle_rain_annual.csv

Requirements:
- Env var NOAA_CDO_TOKEN (your CDO API token)
- Python 3.11+ and 'requests' library

References:
- CDO API v2 docs & required parameters:
  https://www.ncei.noaa.gov/cdo-web/webservices/v2
- Sea-Tac station (GHCND:USW00024233) in CDO:
  https://www.ncdc.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND:USW00024233/detail
"""
import os
import sys
import csv
import datetime
import requests

# --- Configuration & env handling (blank-safe) ---
TOKEN = os.environ.get("NOAA_CDO_TOKEN")
BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"
STATION = "GHCND:USW00024233"  # Seattle Tacoma Airport (Sea-Tac)

# If env var is missing or set to "", fall back to defaults
START = os.environ.get("NOAA_START_DATE") or "1991-01-01"
END   = os.environ.get("NOAA_END_DATE") or datetime.date.today().strftime("%Y-%m-%d")

HEADERS = {"token": TOKEN}

# --- Guards ---
if not TOKEN:
    print("ERROR: set NOAA_CDO_TOKEN env var (CDO API token required).", file=sys.stderr)
    sys.exit(1)

# --- Helper: robust request with better error visibility & pagination ---
def cdo_data(params: dict) -> list:
    """Fetch CDO /data with pagination and improved error messages."""
    out = []
    limit = 1000
    offset = 1

    while True:
        p = dict(params)
        p.update({"limit": limit, "offset": offset})
        try:
            r = requests.get(f"{BASE}/data", headers=HEADERS, params=p, timeout=60)
        except requests.RequestException as e:
            print(f"HTTP transport error: {e}", file=sys.stderr)
            raise

