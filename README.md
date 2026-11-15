# Seattle Rain Trends

An interactive dashboard of Seattle's rainfall, built on NOAA's official record for Seattle-Tacoma International Airport.

**Live dashboard:** https://xanderf98.github.io/seattle-weather/seattle_rain_dashboard.html

## What it shows

- **Annual totals:** how each year's rainfall compares over time.
- **Monthly breakdown:** rainfall by month for any year you pick.
- **Intensity heatmap:** every month of every year on one grid, so wet and dry stretches stand out.

All values are precipitation totals in inches.

## How it works

```
NOAA Climate Data Online API  -->  scripts/fetch_noaa_precip.py  -->  two CSV files  -->  seattle_rain_dashboard.html
```

1. A GitHub Actions workflow runs every Monday and calls `scripts/fetch_noaa_precip.py`.
2. The script pulls monthly and annual precipitation totals for the Sea-Tac station from NOAA and writes `seattle_rain_monthly.csv` and `seattle_rain_annual.csv`.
3. The workflow commits the refreshed CSVs to this repository.
4. The dashboard is a single static HTML page, served by GitHub Pages, that loads the two CSVs and draws the charts with Plotly.

There is no server and no database. The repository is the data store, and the schedule keeps it current.

## Files

| File | Purpose |
|---|---|
| `seattle_rain_dashboard.html` | The dashboard page |
| `scripts/fetch_noaa_precip.py` | Fetches the data from NOAA |
| `.github/workflows/noaa_rain_update.yml` | Weekly refresh schedule |
| `seattle_rain_monthly.csv`, `seattle_rain_annual.csv` | The data the dashboard reads |

## Data source

NOAA National Centers for Environmental Information, Climate Data Online API v2.

- Station: Seattle-Tacoma International Airport (`GHCND:USW00024233`)
- Datasets: Global Summary of the Month (GSOM) and Global Summary of the Year (GSOY)
- Data type: `PRCP`, in inches

NOAA limits monthly and annual requests to ten years at a time, so the script fetches the full range in windows and joins them.

## Run it yourself

1. Request a free API token from NOAA Climate Data Online.
2. Install the dependencies and run the script:

   ```
   pip install requests pandas
   NOAA_CDO_TOKEN=your_token python scripts/fetch_noaa_precip.py
   ```

3. Open `seattle_rain_dashboard.html` through a local web server, for example `python -m http.server`, since browsers block CSV loading from a plain file.

To run the scheduled refresh in your own copy, add the token as a repository secret named `NOAA_CDO_TOKEN`.
