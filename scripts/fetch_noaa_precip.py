"""Fetch Sea-Tac precipitation totals from NOAA's Climate Data Online (CDO) API.

Writes two CSVs to the repository root, each with DATE and PRCP columns (inches):
  seattle_rain_monthly.csv   monthly totals (dataset GSOM)
  seattle_rain_annual.csv    annual totals (dataset GSOY)

Requires a free CDO API token in the NOAA_CDO_TOKEN environment variable.
"""

import os
import sys
import time
from datetime import date

import pandas as pd
import requests

TOKEN = os.getenv("NOAA_CDO_TOKEN")
STATION_ID = "GHCND:USW00024233"  # Seattle-Tacoma International Airport
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
START_DATE = os.getenv("NOAA_START_DATE", "1991-01-01")
END_DATE = os.getenv("NOAA_END_DATE") or date.today().isoformat()

# The CDO API rejects monthly and annual requests that span more than ten years,
# so the full range is fetched in windows and stitched together.
WINDOW_YEARS = 9
PAGE_SIZE = 1000


def year_windows(start: str, end: str):
    """Yield (start, end) ISO date pairs covering start..end in WINDOW_YEARS chunks."""
    start_d, end_d = date.fromisoformat(start), date.fromisoformat(end)
    while start_d <= end_d:
        window_end = min(date(start_d.year + WINDOW_YEARS, 12, 31), end_d)
        yield start_d.isoformat(), window_end.isoformat()
        start_d = date(window_end.year + 1, 1, 1)


def fetch_window(dataset_id: str, start: str, end: str) -> list[dict]:
    """Fetch every PRCP record for one date window, following pagination."""
    records, offset = [], 1
    while True:
        params = {
            "datasetid": dataset_id,
            "datatypeid": "PRCP",
            "stationid": STATION_ID,
            "startdate": start,
            "enddate": end,
            "units": "standard",
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        response = requests.get(BASE_URL, headers={"token": TOKEN}, params=params, timeout=60)
        response.raise_for_status()
        page = response.json().get("results", [])
        records.extend(page)
        if len(page) < PAGE_SIZE:
            return records
        offset += PAGE_SIZE


def fetch_dataset(dataset_id: str) -> pd.DataFrame:
    """Fetch the full date range for a dataset as a DATE/PRCP table."""
    records = []
    for start, end in year_windows(START_DATE, END_DATE):
        records.extend(fetch_window(dataset_id, start, end))
        time.sleep(0.25)  # stay well under the API's five-requests-per-second limit
    if not records:
        raise RuntimeError(f"NOAA returned no {dataset_id} records for {START_DATE}..{END_DATE}")
    df = pd.DataFrame(records)
    df = df[df["datatype"] == "PRCP"]
    df = df.assign(DATE=df["date"].str[:10], PRCP=df["value"])[["DATE", "PRCP"]]
    return df.drop_duplicates("DATE").sort_values("DATE")


def main() -> int:
    if not TOKEN:
        print("NOAA_CDO_TOKEN is not set.", file=sys.stderr)
        return 1
    fetch_dataset("GSOM").to_csv("seattle_rain_monthly.csv", index=False)
    fetch_dataset("GSOY").to_csv("seattle_rain_annual.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
