"""
Clean and join the raw sources from data/raw/ into final tables in data/processed/.

Outputs (see SCHEMA.md):
  - country_profile.csv : 1 row per country (total), the 5 time categories + income,
                          happiness, working hours, retirement age.
  - timeuse_by_sex.csv  : wide format, time per country x sex (F, M) for gender
                          comparisons.

Run after download_data.py:
    python3 scripts/build_dataset.py
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# Readable labels for the 5 OECD categories (minutes/day, sum to ~1440 = 24h).
ACTIVITY_LABELS = {
    "PCA": "Personal care",     # includes sleep, meals, hygiene
    "PAW": "Paid work/study",
    "UPW": "Unpaid work",       # housework, caring for others
    "LEI": "Leisure",
    "OTH": "Other",             # includes commuting and unclassified
}

# Country dimension: readable name + region, for the 35 countries in the OECD data.
COUNTRY_META = {
    "AUS": ("Australia", "Oceania"),      "AUT": ("Austria", "Europe"),
    "BEL": ("Belgium", "Europe"),         "BGR": ("Bulgaria", "Europe"),
    "CAN": ("Canada", "Americas"),        "CHN": ("China", "Asia"),
    "DEU": ("Germany", "Europe"),         "DNK": ("Denmark", "Europe"),
    "ESP": ("Spain", "Europe"),           "EST": ("Estonia", "Europe"),
    "FIN": ("Finland", "Europe"),         "FRA": ("France", "Europe"),
    "GBR": ("United Kingdom", "Europe"),  "GRC": ("Greece", "Europe"),
    "HRV": ("Croatia", "Europe"),         "HUN": ("Hungary", "Europe"),
    "IND": ("India", "Asia"),             "IRL": ("Ireland", "Europe"),
    "ITA": ("Italy", "Europe"),           "JPN": ("Japan", "Asia"),
    "KOR": ("South Korea", "Asia"),       "LTU": ("Lithuania", "Europe"),
    "LUX": ("Luxembourg", "Europe"),      "LVA": ("Latvia", "Europe"),
    "MEX": ("Mexico", "Americas"),        "NLD": ("Netherlands", "Europe"),
    "NOR": ("Norway", "Europe"),          "NZL": ("New Zealand", "Oceania"),
    "POL": ("Poland", "Europe"),          "PRT": ("Portugal", "Europe"),
    "SVN": ("Slovenia", "Europe"),        "SWE": ("Sweden", "Europe"),
    "TUR": ("Turkey", "Asia"),            "USA": ("United States", "Americas"),
    "ZAF": ("South Africa", "Africa"),
}


def load_oecd() -> pd.DataFrame:
    """OECD time use -> long: iso3, sex, activity, minutes, hours."""
    df = pd.read_csv(RAW / "oecd_time_use.csv")
    df = df[["REF_AREA", "MEASURE", "SEX", "OBS_VALUE"]].rename(
        columns={"REF_AREA": "iso3", "MEASURE": "activity_code",
                 "SEX": "sex", "OBS_VALUE": "minutes_per_day"}
    )
    df["activity"] = df["activity_code"].map(ACTIVITY_LABELS)
    df["hours_per_day"] = (df["minutes_per_day"] / 60).round(2)
    return df


def latest_by_country(filename: str, value_col: str, new_name: str) -> pd.DataFrame:
    """Take the most recent value per country (ISO3 code) from an OWID CSV."""
    df = pd.read_csv(RAW / filename)
    df = df[df["Code"].notna() & (df["Code"].str.len() == 3)]
    df = df.sort_values("Year").groupby("Code", as_index=False).last()
    out = df[["Code", value_col, "Year"]].rename(
        columns={"Code": "iso3", value_col: new_name, "Year": f"{new_name}_year"}
    )
    return out


def build_profile(oecd_long: pd.DataFrame) -> pd.DataFrame:
    total = oecd_long[oecd_long["sex"] == "_T"]
    wide = total.pivot_table(index="iso3", columns="activity_code",
                             values="minutes_per_day").reset_index()
    # rename columns to minutes
    wide = wide.rename(columns={c: f"{c.lower()}_min" for c in ACTIVITY_LABELS})

    # country + region
    wide["country"] = wide["iso3"].map(lambda c: COUNTRY_META.get(c, (c, "?"))[0])
    wide["region"] = wide["iso3"].map(lambda c: COUNTRY_META.get(c, (c, "?"))[1])

    # total minutes (should be ~1440) and hours per category
    cat_min = [f"{c.lower()}_min" for c in ACTIVITY_LABELS]
    wide["total_min"] = wide[cat_min].sum(axis=1).round(0)
    for c in cat_min:
        wide[c.replace("_min", "_h")] = (wide[c] / 60).round(2)

    # --- join supplementary metrics (most recent value per country) ---
    gdp = pd.read_csv(RAW / "worldbank_gdp_pcap_ppp.csv")[["iso3", "gdp_per_capita_ppp"]]
    happ = latest_by_country("owid_happiness.csv",
                             "Self-reported life satisfaction", "life_satisfaction")
    work = latest_by_country("owid_working_hours.csv",
                             "Working hours per worker", "annual_working_hours")
    retire = latest_by_country("owid_retirement_age_men.csv",
                               "Average effective age of retirement, men (OECD)",
                               "retirement_age_men")
    for extra in (gdp, happ, work, retire):
        wide = wide.merge(extra, on="iso3", how="left")

    # order columns
    front = ["iso3", "country", "region"]
    cols = front + [c for c in wide.columns if c not in front]
    return wide[cols].sort_values("country").reset_index(drop=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    oecd_long = load_oecd()

    # by-sex output in wide format: 1 row per country x sex (F, M),
    # one column per category (same layout as country_profile.csv).
    by_sex = oecd_long[oecd_long["sex"].isin(["F", "M"])].pivot_table(
        index=["iso3", "sex"], columns="activity_code", values="minutes_per_day"
    ).reset_index()
    by_sex = by_sex.rename(columns={c: f"{c.lower()}_min" for c in ACTIVITY_LABELS})
    by_sex["country"] = by_sex["iso3"].map(lambda c: COUNTRY_META.get(c, (c, "?"))[0])
    by_sex["region"] = by_sex["iso3"].map(lambda c: COUNTRY_META.get(c, (c, "?"))[1])

    cat_min = [f"{c.lower()}_min" for c in ACTIVITY_LABELS]
    by_sex["total_min"] = by_sex[cat_min].sum(axis=1).round(0)
    for c in cat_min:
        by_sex[c.replace("_min", "_h")] = (by_sex[c] / 60).round(2)

    cols = (["iso3", "country", "region", "sex"] + cat_min + ["total_min"]
            + [c.replace("_min", "_h") for c in cat_min])
    by_sex = by_sex[cols].sort_values(["country", "sex"]).reset_index(drop=True)
    by_sex.to_csv(OUT / "timeuse_by_sex.csv", index=False)

    profile = build_profile(oecd_long)
    profile.to_csv(OUT / "country_profile.csv", index=False)

    # --- validation ---
    bad = profile[(profile["total_min"] < 1380) | (profile["total_min"] > 1500)]
    print(f"country_profile.csv: {len(profile)} countries")
    print(f"timeuse_by_sex.csv : {len(by_sex)} rows")
    if len(bad):
        print("\n[WARNING] Countries whose categories do not sum to ~1440 min (24h):")
        print(bad[["country", "total_min"]].to_string(index=False))
    else:
        print("Validation OK: all categories sum to ~1440 min (24h).")
    miss = profile[profile[["gdp_per_capita_ppp", "life_satisfaction"]].isna().any(axis=1)]
    if len(miss):
        print(f"\nCountries missing income or happiness ({len(miss)}): "
              f"{', '.join(miss['country'])}")


if __name__ == "__main__":
    main()
