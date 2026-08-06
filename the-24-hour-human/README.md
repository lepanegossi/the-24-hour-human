# The 24-Hour Human — VizCon 2026

An interactive data story about how the world spends the same **1,440 minutes** a day, across 35 countries.
Theme: *"How the world lives, thrives, and connects."*

**Live:** <https://lepanegossi.github.io/the-24-hour-human/>

Every push to `redesign-visuals` that touches this folder rebuilds and republishes
it (`.github/workflows/pages.yml`). The workflow runs `build_dashboard.py` itself
and serves this folder as the site root with `dashboard.html` as `index.html`, so
the page in the air is always what the CSVs produce and the dashboard's name is
what shows up in the address.

## Run it

The dashboard uses a 3D globe (globe.gl) and local assets, so it must be served over HTTP (not opened as `file://`):

```bash
python3 build_dashboard.py          # regenerates dashboard.html from data/
python3 -m http.server 8777         # serve the folder
# open http://localhost:8777/dashboard.html
```

> Tip: when you regenerate, open with a cache-buster (`?v=123`) or hard-refresh (Cmd+Shift+R). The browser caches aggressively.

The build prints a warning for every asset it could not find, including a video
without captions. Nothing breaks — each missing asset has a fallback — so that
warning is the only way to notice a file that was never added or was named wrong.

### Captions for a persona video

Captions are a WCAG 1.2.2 (level A) requirement for recorded speech. Each video
needs a `.vtt` next to it, transcribed from that video's own audio:

```bash
python3 -m venv /tmp/vtt-venv
/tmp/vtt-venv/bin/pip install faster-whisper
/tmp/vtt-venv/bin/python make_captions.py assets/video/jpn.mp4
```

Read the result against the audio before committing — the transcription is good,
not perfect. Afterwards the venv and the model cache (`~/.cache/huggingface`) can
be deleted.

## Structure

```
build_dashboard.py        # generator: reads data/, writes dashboard.html (source of truth)
dashboard.html            # the generated dashboard (served output)
data/
  country_profile.csv     # 35 countries: 5 time categories + income, happiness, work hours, retirement
  timeuse_by_sex.csv      # same, split by sex (F/M) — used for the gender screen
assets/
  avatars/                # persona illustrations (SVG)
  flags/                  # circular flags (PNG) for the flag charts
  lib/globe.gl.min.js     # 3D globe library (local)
  img/                    # earth textures for the globe
```

## The story (sections)
1. Hero — the gift of 1,440 minutes (spinning clock; sun rises as you scroll)
2. Which human are you? — a Tinder-style quiz that matches your day to a country
3. One day, five lives — five personas, one per continent, with 24h clocks
4. Where people spend their time — interactive 3D globe (click a country)
5. Who works the most? — top 10 as sized flag bubbles
6. The double shift — unpaid work, women vs men (the climax)
7. Work vs. free time — scatter, our five friends highlighted
8. Working until when? — retirement as a road with WORK/RETIRE signs
9. The day of 2050 — a simple predictive model (illustrative, not a forecast)
10. At the end of the day — reflection + an interactive poll

## Data sources (public & free)
- OECD Time Use Database
- World Bank — GDP per capita, PPP
- Our World in Data

## Notes
- **Predictive model**: illustrative only — the data is a snapshot, not a time series. Method documented in `predictive_screen_handoff.md`.
- **Poll**: tallies votes per device (localStorage). Global aggregation across all visitors needs a small backend.
- Coverage is 35 OECD/partner countries — no South American country is available in the dataset.

## Docs
- `narrative.md` — full narrative script (all section texts)
- `predictive_screen_handoff.md` — spec of the 2050 model for the front-end
- `data_inventory.md`, `aha_findings.md`, `objective_topics.md` — data context & findings
- `competitor_analysis.md` — study of past winning dashboards
- `project_baseline.md` — locked scope
