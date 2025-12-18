#!/usr/bin/env python3

"""Auto-fetch NOAA monthly and annual precipitation for Sea-Tac via CDO API.
Requires env var NOAA_CDO_TOKEN. Writes seattle_rain_monthly.csv and seattle_rain_annual.csv.
Docs: https://www.ncei.noaa.gov/cdo-web/webservices/v2 (API v2) and token info.
"""
import os, sys, csv, datetime, requests

TOKEN = os.environ.get("NOAA_CDO_TOKEN")
BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"
STATION = "GHCND:USW00024233"  # Seattle Tacoma Airport (Sea-Tac)
HEADERS = {"token": TOKEN}
START = os.environ.get("NOAA_START_DATE", "1991-01-01")  # configurable
END   = os.environ.get("NOAA_END_DATE", datetime.date.today().strftime("%Y-%m-%d"))

def cdo_data(params):
    """Handle pagination; return full list of results."""
    out = []
    limit = 1000
    offset = 1
    while True:
        p = dict(params)
        p.update({"limit": limit, "offset": offset})
        r = requests.get(f"{BASE}/data", headers=HEADERS, params=p, timeout=60)
        r.raise_for_status()
        j = r.json()
        results = j.get("results", [])
        out.extend(results)
        meta = j.get("metadata", {}).get("resultset", {})
        count = meta.get("count")
        if not count or offset + limit > count:
            break
        offset += limit
    return out

def fetch_monthly():
    return cdo_data({
        "datasetid": "GSOM",
        "datatypeid": "PRCP",
        "stationid": STATION,
        "startdate": START,
        "enddate": END,
        "units": "standard"
    })

def fetch_annual():
    return cdo_data({
        "datasetid": "GSOY",
        "datatypeid": "PRCP",
        "stationid": STATION,
        "startdate": START,
        "enddate": END,
        "units": "standard"
    })

def write_monthly_csv(rows, out="seattle_rain_monthly.csv"):
    abbr = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    agg = {}
    for r in rows:
        dt = datetime.datetime.fromisoformat(r["date"].replace("Z",""))
        key = (dt.year, dt.month)
        agg[key] = agg.get(key, 0.0) + float(r["value"]) if r.get("value") is not None else agg.get(key, 0.0)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Year","Month","Precip_in","RainDays","Source"])
        for (year, month) in sorted(agg):
            w.writerow([year, abbr[month-1], round(agg[(year, month)], 3), "", "NOAA CDO (GSOM)"])

def write_annual_csv(rows, out="seattle_rain_annual.csv"):
    by_year = {}
    for r in rows:
        dt = datetime.datetime.fromisoformat(r["date"].replace("Z",""))
        by_year.setdefault(dt.year, 0.0)
        by_year[dt.year] += float(r["value"]) if r.get("value") is not None else 0.0
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Year","TotalPrecip_in","RainDays","WettestMonth","DriestMonth","Source"])
        for yr in sorted(by_year):
            w.writerow([yr, round(by_year[yr], 3), "", "", "", "NOAA CDO (GSOY)"])

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: set NOAA_CDO_TOKEN env var", file=sys.stderr)
        sys.exit(1)
    print(f"Fetching monthly GSOM PRCP for {STATION} from {START} to {END}...")
    monthly = fetch_monthly()
    print(f"Monthly rows: {len(monthly)}")
    print(f"Fetching annual GSOY PRCP for {STATION}...")
    annual = fetch_annual()
    print(f"Annual rows: {len(annual)}")
    write_monthly_csv(monthly)
    write_annual_csv(annual)
    print("CSV files written: seattle_rain_monthly.csv, seattle_rain_annual.csv")
