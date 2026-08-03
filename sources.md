# Data sources

All sources are public and free. The contest requires sources to be cited and
accessible. (Camila: expand with citation text for the submission.)

## OECD Time Use Database
- **What**: average time per day across 5 categories (personal care, paid work/study,
  unpaid work, leisure, other), by sex, population aged 15–64. 35 countries.
- **Unit**: minutes per day.
- **Access**: OECD SDMX API (dataflow `DSD_TIME_USE@DF_TIME_USE`).
- **Link**: https://www.oecd.org/en/data/datasets/time-use-database.html
- **Note**: data from different years per country; see the database for the reference year.

## World Bank — GDP per capita, PPP
- **What**: income per person adjusted for purchasing power parity.
- **Indicator**: `NY.GDP.PCAP.PP.CD`
- **Access**: World Bank API.
- **Link**: https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD

## Our World in Data (OWID)
All downloaded via the grapher CSV (`https://ourworldindata.org/grapher/<slug>.csv`).

| Metric | Slug | Original source |
|---|---|---|
| Life satisfaction (Cantril ladder) | `happiness-cantril-ladder` | World Happiness Report / Gallup |
| Annual working hours | `annual-working-hours-per-worker` | PWT / OWID |
| Vacation days per year | `days-of-vacation-and-holidays` | OWID |
| Average effective retirement age (men) | `average-effective-retirement-men` | OECD |
| Leisure by sex | `time-women-and-men-spend-on-leisure` | OECD |

- **Link**: https://ourworldindata.org/time-use

## License / use
- World Bank and OWID: open data (CC BY).
- OECD: use permitted with attribution; check OECD terms before publishing.
