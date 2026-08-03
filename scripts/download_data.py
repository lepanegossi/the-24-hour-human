"""
Download all raw data sources into data/raw/.

Reproducible: uses only the standard library (urllib). Run with:
    python3 scripts/download_data.py

All sources are public and accessible via API/HTTP (no manual downloads).
See sources.md for the full citation of each source.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# --- Confirmed endpoints ----------------------------------------------------

# OECD Time Use Database (SDMX API, CSV). Categories in minutes/day:
# PCA=personal care (includes sleep), PAW=paid work/study, UPW=unpaid work,
# LEI=leisure, OTH=other. Sex breakdown: F, M, _T (total).
OECD_TIME_USE = (
    "https://sdmx.oecd.org/public/rest/data/"
    "OECD.WISE.INE,DSD_TIME_USE@DF_TIME_USE,1.0/all"
    "?format=csvfile&dimensionAtObservation=AllDimensions"
)

# Our World in Data (grapher CSV). Each slug becomes a file.
OWID_GRAPHERS = {
    "happiness": "happiness-cantril-ladder",
    "working_hours": "annual-working-hours-per-worker",
    "vacation_days": "days-of-vacation-and-holidays",
    "retirement_age_men": "average-effective-retirement-men",
    "leisure_by_sex": "time-women-and-men-spend-on-leisure",
}
OWID_BASE = "https://ourworldindata.org/grapher/{slug}.csv"

# World Bank (JSON API). Income: GDP per capita PPP, most recent value per country.
WB_GDP_PCAP_PPP = (
    "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.CD"
    "?format=json&mrv=1&per_page=400"
)


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "vizcon2026-dataprep"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def download_oecd() -> None:
    print("Downloading OECD Time Use (SDMX)...")
    data = _fetch(OECD_TIME_USE)
    (RAW / "oecd_time_use.csv").write_bytes(data)
    print(f"  -> data/raw/oecd_time_use.csv ({len(data):,} bytes)")


def download_owid() -> None:
    for name, slug in OWID_GRAPHERS.items():
        print(f"Downloading OWID: {slug}...")
        data = _fetch(OWID_BASE.format(slug=slug))
        (RAW / f"owid_{name}.csv").write_bytes(data)
        print(f"  -> data/raw/owid_{name}.csv ({len(data):,} bytes)")


def download_worldbank() -> None:
    print("Downloading World Bank: GDP per capita PPP...")
    raw = _fetch(WB_GDP_PCAP_PPP)
    payload = json.loads(raw)
    rows = payload[1] if len(payload) > 1 and payload[1] else []
    # Normalize to a simple CSV: iso3, country, year, gdp_per_capita_ppp
    lines = ["iso3,country,year,gdp_per_capita_ppp"]
    for r in rows:
        if r.get("value") is None:
            continue
        iso3 = r.get("countryiso3code", "")
        country = r["country"]["value"].replace(",", " ")
        year = r["date"]
        val = r["value"]
        lines.append(f"{iso3},{country},{year},{val}")
    out = "\n".join(lines) + "\n"
    (RAW / "worldbank_gdp_pcap_ppp.csv").write_text(out, encoding="utf-8")
    print(f"  -> data/raw/worldbank_gdp_pcap_ppp.csv ({len(rows)} countries)")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    download_oecd()
    download_owid()
    download_worldbank()
    print("\nDone. Files in data/raw/")


if __name__ == "__main__":
    main()
