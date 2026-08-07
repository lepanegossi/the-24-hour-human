# The 24-Hour Human — VizCon 2026

An interactive data story about how the world spends the same **1,440 minutes** a day, across 35 countries.
Theme: *"How the world lives, thrives, and connects."*

**Live:** <https://lepanegossi.github.io/the-24-hour-human/>

Every push to `redesign-visuals` that touches this folder rebuilds and republishes
it. The workflow lives at the repository root, in `.github/workflows/`, runs
`build_dashboard.py` itself, and serves this folder as the site root with the built
`dashboard.html` renamed on the way out. So the page in the air is always what the
CSVs produce, and the dashboard's name is what shows up in the address.

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
make_captions.py          # transcribes a persona video into the .vtt beside it
dashboard.html            # the generated dashboard (do not edit: it is overwritten)
data/
  country_profile.csv     # 35 countries: 5 time categories + income, happiness, work hours, retirement
  timeuse_by_sex.csv      # same, split by sex (F/M), used for the gender screen
assets/
  avatars/                # the five persona portraits (WebP, 512px; .svg kept as fallback)
  video/                  # one .mp4, .vtt and poster per persona
  team/                   # the three credit photos (optional: initials show if absent)
  flags/                  # circular flags (PNG) for the flag charts
  sky/                    # the eight illustrated skies, morning to midnight
  topics/                 # the six topic card illustrations
  img/                    # earth textures for the globe, and the closing night scene
  lib/globe.gl.min.js     # 3D globe library, vendored so the page needs no CDN for it
```

Everything on the page lives inside `build_dashboard.py`: the CSS, the HTML and the
JS are string constants there, assembled into `dashboard.html`. Editing
`dashboard.html` is pointless, the next build overwrites it, and the Pages workflow
rebuilds on every push.

## The story (sections)

The page runs on a clock: each chapter carries the hour it belongs to, and the
illustrated sky behind it moves from morning to deep night as you scroll.

| # | Chapter | Hour | What it is |
|---|---|---|---|
| — | The 24-Hour Human | — | Hero: the 1,440 minutes everyone gets, and the thesis |
| 01 | One day, five lives | 07:00 | Five personas, one per continent. Click one for their video, their day hour by hour, and four things you would not guess |
| 02 | Who does it most? | 09:00 | Six slices of the day; pick one for its top ten as sized flag bubbles |
| 03 | Which human are you? | 11:00 | Slide your ideal day and get matched to one of the 35 countries |
| 04 | Where people spend their time | 12:00 | Interactive 3D globe, or the same countries from a keyboard list |
| 05 | The double shift | 20:00 | Unpaid work and leisure, women against men. The climax |
| 06 | Work vs. free time | 21:30 | 35 flags placed by paid work against leisure, r = −0.66 |
| 07 | Working until when? | 22:30 | Retirement as a road, 35 flags between 60 and 72 |
| 08 | The day of 2050 | 23:00 | An illustrative model, not a forecast |
| 09 | At the end of the day | 23:59 | Reflection and a poll, tallied per device |
| 10 | An hour is a policy choice | 00:00 | What the data can say about where the hours come back from, then the closing question over the night image |
| — | How this was made | — | Credits, the stack, and how AI was used |

## Data sources (public & free)
- OECD Time Use Database
- World Bank — GDP per capita, PPP
- Our World in Data

## Notes
- **Every "per day" figure is a population average**, over the whole adult population and all seven days. Paid work per day is not the length of a working day. The footer says so on the page itself.
- **Predictive model**: illustrative only, since the data is a snapshot and not a time series. The coefficients are printed by the build.
- **Poll**: tallies votes per device (localStorage). Aggregating across visitors would need a backend.
- Coverage is 35 OECD and partner countries. No South American country is in the dataset, which is why the globe has a hole over the continent.
- **Numbers in the copy are computed, not typed.** Anything that could go stale if a CSV changed is derived in the builder, and the build prints the headline figures so a shift is visible.

## Docs
- `narrative.md` — the original narrative script. It predates the current build and diverges from it in places (chapter order, and the ending), so treat the page as the source of truth for copy.
- `../SCHEMA.md` — the data contract for the two processed CSVs, and the quality caveats.
- `../sources.md` — every source, with the indicator or slug used.
