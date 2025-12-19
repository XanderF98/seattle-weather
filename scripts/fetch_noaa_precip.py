import os
import requests
import pandas as pd
from datetime import datetime

# Setup
TOKEN = os.getenv('NOAA_CDO_TOKEN')
STATION_ID = 'GHCND:USW00024233'
BASE_URL = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'
HEADERS = {'token': TOKEN}

def fetch_data(dataset_id, start_date, end_date):
    params = {
        'datasetid': dataset_id,
        'stationid': STATION_ID,
        'startdate': start_date,
        'enddate': end_date,
        'limit': 1000,
        'units': 'standard'
    }
    r = requests.get(BASE_URL, headers=HEADERS, params=params)
    return r.json().get('results', []) if r.status_code == 200 else []

def main():
    # Use dates from environment or defaults
    start = os.getenv('NOAA_START_DATE', '1991-01-01')
    end = os.getenv('NOAA_END_DATE', datetime.now().strftime('%Y-%m-%d'))

    # Fetch Monthly Data
    m_data = fetch_data('GSOM', start, end)
    if m_data:
        df = pd.DataFrame(m_data)
        df = df[df['datatype'] == 'PRCP']
        df[['date', 'value']].to_csv('seattle_rain_monthly.csv', index=False, header=['DATE', 'PRCP'])

    # Fetch Annual Data
    a_data = fetch_data('GSOY', start, end)
    if a_data:
        df = pd.DataFrame(a_data)
        df = df[df['datatype'] == 'PRCP']
        df[['date', 'value']].to_csv('seattle_rain_annual.csv', index=False, header=['DATE', 'PRCP'])

if __name__ == "__main__":
    main()
