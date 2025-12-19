import os
import requests
import pandas as pd
from datetime import datetime

# NOAA Settings
TOKEN = os.getenv('NOAA_CDO_TOKEN')
STATION_ID = 'GHCND:USW00024233'
BASE_URL = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'
HEADERS = {'token': TOKEN}

def fetch_data(dataset_id, start_date, end_date):
    params = {'datasetid': dataset_id, 'stationid': STATION_ID, 'startdate': start_date, 'enddate': end_date, 'limit': 1000, 'units': 'standard'}
    r = requests.get(BASE_URL, headers=HEADERS, params=params)
    return r.json().get('results', []) if r.status_code == 200 else []

def main():
    start = "1991-01-01"
    end = datetime.now().strftime('%Y-%m-%d')

    # Fetch and Save Monthly
    m_data = fetch_data('GSOM', start, end)
    if m_data:
        df = pd.DataFrame(m_data)
        df = df[df['datatype'] == 'PRCP']
        # Explicitly naming headers to match the HTML code
        df[['date', 'value']].to_csv('seattle_rain_monthly.csv', index=False, header=['DATE', 'PRCP'])

    # Fetch and Save Annual
    a_data = fetch_data('GSOY', start, end)
    if a_data:
        df = pd.DataFrame(a_data)
        df = df[df['datatype'] == 'PRCP']
        # Explicitly naming headers to match the HTML code
        df[['date', 'value']].to_csv('seattle_rain_annual.csv', index=False, header=['DATE', 'PRCP'])

if __name__ == "__main__":
    main()
