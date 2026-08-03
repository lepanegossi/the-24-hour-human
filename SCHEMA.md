# Data contract — outputs in `data/processed/`

This is the format the front-end (Let) and the AI layer (Nat) should consume.
Two tables: a **wide** one (1 country per row, for the clock and recommender) and a
**by-sex** one (for gender comparisons).

## 1. `country_profile.csv` — 1 row per country (35 countries)

Main use: radial 24h clock, ranking, "best country for you" recommender.

| Column | Type | Description |
|---|---|---|
| `iso3` | text | Country code (ISO 3166-1 alpha-3), e.g. `BRA` |
| `country` | text | Country name in English |
| `region` | text | Americas / Europe / Asia / Oceania / Africa |
| `pca_min` `pca_h` | number | **Personal care** (includes sleep, meals) — min/day and hours/day |
| `paw_min` `paw_h` | number | **Paid work / study** |
| `upw_min` `upw_h` | number | **Unpaid work** (housework, caring for others) |
| `lei_min` `lei_h` | number | **Leisure** |
| `oth_min` `oth_h` | number | **Other** (includes commuting) |
| `total_min` | number | Sum of the 5 categories (≈1440 = 24h validation) |
| `gdp_per_capita_ppp` | number | GDP per capita, PPP (international $) — income proxy |
| `life_satisfaction` | number | Life satisfaction (Cantril ladder, 0–10) |
| `annual_working_hours` | number | Working hours per year, per worker |
| `retirement_age_men` | number | Average effective retirement age (men) |
| `*_year` | number | Reference year for each supplementary metric |

The 5 categories (`*_h`) sum to 24h → use directly as slices of the radial clock.

## 2. `timeuse_by_sex.csv` — wide format (70 rows = 35 countries × 2)

Use: gender comparisons (e.g. unpaid work, women vs. men). Same layout as
`country_profile.csv`, with one row per country **and per sex** (F and M).
For the total value (both sexes), use `country_profile.csv`.

| Column | Type | Description |
|---|---|---|
| `iso3` `country` `region` | text | Country identification |
| `sex` | text | `F` (women), `M` (men) |
| `pca_min` … `oth_min` | number | The 5 categories in min/day (see table 1) |
| `total_min` | number | Sum of the 5 categories (≈1440 = 24h) |
| `pca_h` … `oth_h` | number | The 5 categories in hours/day |

## Quality notes (worth citing — scores under the Data Quality criterion)

- **Sleep is not isolated**: it sits inside "Personal care" (along with meals and
  hygiene). The narrative should say "personal care", not "pure sleep". For a
  sleep-specific breakdown, only via ATUS (US) — treat as an optional deep-dive.
- **Commuting/transit** is not an isolated category — it falls under "Other". The
  recommender should not promise "less commuting" with precision.
- **Cross-sectional, not a time series**: each country has a snapshot of the most
  recent available year (years vary across countries). Do not use for trends over time.
- Supplementary metrics use the most recent value per country (see `*_year` columns).
