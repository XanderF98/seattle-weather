
# Seattle Rain Trends — Ready-to-use Repo Kit

This kit auto-fetches **Seattle (Sea-Tac) precipitation** from NOAA's **Climate Data Online (CDO)** API and renders an interactive dashboard.

## What’s included
- `seattle_rain_dashboard.html` — Plotly dashboard (loads two CSVs)
- `seattle_rain_annual_template.csv` / `seattle_rain_monthly_template.csv` — CSV formats
- `scripts/fetch_noaa_precip.py` — Pulls monthly (GSOM) & annual (GSOY) precipitation for Sea-Tac (station `GHCND:USW00024233`)
- `.github/workflows/noaa_rain_update.yml` — GitHub Actions to refresh CSVs on a schedule

## Setup
1. **Create repo** and add these files to the root (preserve folder structure).
2. **Set secret**: In GitHub → *Settings → Secrets and variables → Actions* → `NOAA_CDO_TOKEN` (your CDO API token).
3. Optional: set `NOAA_START_DATE` and `NOAA_END_DATE` env vars in the workflow (or leave defaults).
4. Run workflow manually (Actions tab) or wait for the schedule. It will write:
   - `seattle_rain_monthly.csv`
   - `seattle_rain_annual.csv`
5. **Enable GitHub Pages**: Settings → Pages → Source: `main` and `/root`.
6. View: `https://<username>.github.io/<repo>/seattle_rain_dashboard.html`

## Notes
- Data source: NOAA/NCEI CDO API v2 (`/data` endpoint; datasets **GSOM** and **GSOY**, datatype `PRCP`, station `GHCND:USW00024233`).
- Units are **inches** (`units=standard`).
- CDO rate limits are generous (5 req/sec, 10,000/day). The workflow stays well under limits.

## References
- NOAA CDO API v2 docs and token request.
- Sea-Tac station detail (GHCND:USW00024233).

## Embed (Wix example)
```html
<iframe src="https://<username>.github.io/<repo>/seattle_rain_dashboard.html" width="100%" height="1200" frameborder="0"></iframe>
```
