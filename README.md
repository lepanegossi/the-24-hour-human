# VizCon 2026 — "The World's 24 Hours"

How different countries spend the same 24 hours (personal care, paid work, unpaid
work, leisure, other) — and how that relates to income, happiness, and quality of life.

Entry for the Analyticon Viz Contest 2026. Theme: *"How the world lives, thrives, and connects"*.

## Structure

```
data/
  raw/          # files downloaded from the sources (do not edit by hand)
  processed/    # final, clean tables ready for visualization
scripts/
  download_data.py   # downloads all sources (reproducible)
  build_dataset.py   # cleans + joins everything into single tables
SCHEMA.md            # data contract: columns and format of the outputs
sources.md           # all cited sources (contest requirement)
```

## How to run

```bash
python3 scripts/download_data.py   # populates data/raw/
python3 scripts/build_dataset.py   # generates data/processed/
```

## Sources (summary — details in sources.md)

- **OECD Time Use Database** (via SDMX API) — the core data: 5 categories that sum
  to 24h, 35 countries, by sex.
- **World Bank** (API) — GDP per capita PPP (income).
- **Our World in Data** — life satisfaction (Cantril ladder), annual working hours,
  retirement age, vacation days.
