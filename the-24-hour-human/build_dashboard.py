"""
Gera dashboard.html (mockup VizCon 2026 — The 24-Hour Human) a partir dos CSVs
reais do repo da Nath. Reproduzível: se o CSV mudar, regenera com números certos.

Tema: DAYLIGHT (claro). Personas com avatares ilustrados (assets/avatars/<iso3>.svg).
Inclui quiz "Which human are you?", 4 telas objetivas, seção AI, acessibilidade, animações.

Uso:  python3 build_dashboard.py
"""
import csv, json, math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CP = ROOT / "data" / "country_profile.csv"
BS = ROOT / "data" / "timeuse_by_sex.csv"
OUT = ROOT / "dashboard.html"

cp = list(csv.DictReader(open(CP)))
bs = list(csv.DictReader(open(BS)))

NUM = ("pca_h", "paw_h", "upw_h", "lei_h", "oth_h",
       "gdp_per_capita_ppp", "life_satisfaction", "annual_working_hours", "retirement_age_men")
for r in cp:
    for k in NUM:
        r[k] = float(r[k])

ISO3_2 = {
    "AUS":"AU","AUT":"AT","BEL":"BE","BGR":"BG","CAN":"CA","CHN":"CN","HRV":"HR","DNK":"DK",
    "EST":"EE","FIN":"FI","FRA":"FR","DEU":"DE","GRC":"GR","HUN":"HU","IND":"IN","IRL":"IE",
    "ITA":"IT","JPN":"JP","LVA":"LV","LTU":"LT","LUX":"LU","MEX":"MX","NLD":"NL","NZL":"NZ",
    "NOR":"NO","POL":"PL","PRT":"PT","SVN":"SI","ZAF":"ZA","KOR":"KR","ESP":"ES","SWE":"SE",
    "TUR":"TR","GBR":"GB","USA":"US",
}
def flag(iso3):
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in ISO3_2.get(iso3, ""))

# centroides aproximados (lat, lng) para o mapa
COORDS = {
    "AUS":(-25.3,133.8),"AUT":(47.5,14.5),"BEL":(50.5,4.5),"BGR":(42.7,25.5),"CAN":(56.0,-106.0),
    "CHN":(35.0,105.0),"HRV":(45.1,15.2),"DNK":(56.0,9.5),"EST":(58.6,25.0),"FIN":(64.0,26.0),
    "FRA":(46.6,2.2),"DEU":(51.0,10.4),"GRC":(39.0,22.0),"HUN":(47.2,19.5),"IND":(21.0,78.0),
    "IRL":(53.4,-8.0),"ITA":(42.8,12.8),"JPN":(36.2,138.2),"LVA":(56.9,24.6),"LTU":(55.2,23.9),
    "LUX":(49.8,6.1),"MEX":(23.6,-102.5),"NLD":(52.1,5.3),"NZL":(-41.0,174.0),"NOR":(60.5,8.5),
    "POL":(52.0,19.0),"PRT":(39.4,-8.2),"SVN":(46.1,14.8),"ZAF":(-30.6,22.9),"KOR":(36.5,127.8),
    "ESP":(40.2,-3.7),"SWE":(62.0,15.0),"TUR":(39.0,35.0),"GBR":(54.0,-2.5),"USA":(39.8,-98.6),
}

# gap de gênero no trabalho não-pago (F/M) por país, pros textos da tela preditiva
gByIso = {}
for r in bs:
    gByIso.setdefault(r["iso3"], {})[r["sex"]] = float(r["upw_h"])

countries = [{
    "iso3": r["iso3"], "country": r["country"], "region": r["region"], "flag": flag(r["iso3"]),
    "iso2": ISO3_2.get(r["iso3"], "").lower(),
    "lat": COORDS.get(r["iso3"], (0, 0))[0], "lng": COORDS.get(r["iso3"], (0, 0))[1],
    "pca": r["pca_h"], "paw": r["paw_h"], "upw": r["upw_h"], "lei": r["lei_h"], "oth": r["oth_h"],
    "gdp": r["gdp_per_capita_ppp"], "life": r["life_satisfaction"],
    "wh": r["annual_working_hours"], "ret": r["retirement_age_men"],
    "upwF": gByIso.get(r["iso3"], {}).get("F", 0.0), "upwM": gByIso.get(r["iso3"], {}).get("M", 0.0),
} for r in cp]

by = defaultdict(dict)
for r in bs:
    by[r["country"]][r["sex"]] = {k: float(r[k]) for k in ("upw_h", "lei_h")}
gaps = []
for c, d in by.items():
    if "F" in d and "M" in d:
        gaps.append({"country": c, "f": d["F"]["upw_h"], "m": d["M"]["upw_h"],
                     "gap": d["F"]["upw_h"] - d["M"]["upw_h"],
                     "leiF": d["F"]["lei_h"], "leiM": d["M"]["lei_h"]})
gaps.sort(key=lambda x: -x["gap"])
gender = gaps[:5] + gaps[-5:]

PERS = [
    ("FRA", "Camille", "Europe", "The world's longest personal care",
     "Camille starts slow, with a warm croissant and a coffee that's in no hurry. In France the day makes room to live: the world's longest meals, unrushed mornings, and an early finish line, with most retiring by 61."),
    ("JPN", "Haruto", "Asia", "The most paid work per day",
     "Haruto's alarm wins every morning. Japan runs on work, so he logs more paid hours than anyone here, grabs a quick bowl of ramen between shifts, and stays on the job until about 71."),
    ("MEX", "Sofía", "Americas", "The least leisure of all 35",
     "Between paid work and a full house, Sofía barely gets to sit down. Mexico's day is the fullest of all, with the least downtime, so if anyone has earned a spa day it's her, and retirement still waits until her early 70s."),
    ("AUS", "Mia", "Oceania", "The most balanced day",
     "Work in the morning, waves at sunset. Australia keeps things in balance, so Mia splits her hours evenly across work, home and leisure, and clocks out for good around 65."),
    ("ZAF", "Thabo", "Africa", "The heaviest work-year here",
     "Thabo's year is the longest of the five, but he still makes time to gather with friends after hours. South Africa carries the heaviest annual workload here, on the lowest income, retiring by 63."),
]
# ── curiosidades da ficha da persona ────────────────────────────────────────
# Os NÚMEROS e as POSIÇÕES no ranking são calculados dos CSVs; só a frase em volta
# é escrita. Se o dado mudar, o número e o ranking mudam junto.
def _hm(h):
    m = int(round(h * 60))
    return f"{m // 60}h{m % 60:02d}"


def _ordinal(n):
    suf = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def _rank(iso, key, high_first=True):
    order = sorted(cp, key=lambda r: (-r[key] if high_first else r[key]))
    return [r["iso3"] for r in order].index(iso) + 1


def _edge(key, high=True):
    return sorted(cp, key=lambda r: (-r[key] if high else r[key]))[0]


def _sup(n, adj):
    """'the longest' quando é 1º, senão 'the 3rd longest'. O adjetivo vem de fora
    para a frase não sair com concordância quebrada."""
    return f"the {adj}" if n == 1 else f"the {_ordinal(n)} {adj}"


def _days(h):
    return h * 365 / 24


def build_trivia():
    g = {r["iso3"]: r for r in cp}
    fra, jpn, mex, aus, zaf = (g[k] for k in ("FRA", "JPN", "MEX", "AUS", "ZAF"))
    out = {}

    five = ["FRA", "JPN", "MEX", "AUS", "ZAF"]
    rank5 = lambda iso, key: [i for i in sorted(five, key=lambda k: -g[k][key])].index(iso) + 1
    avg_lei = sum(r["lei_h"] for r in cp) / len(cp)

    low_pca = _edge("pca_h", high=False)
    out["FRA"] = [
        ("&#127837;", f"Nobody lingers over the basics like France: <b>{_hm(fra['pca_h'])}</b> a day "
                      f"sleeping, eating and getting ready — {_sup(_rank('FRA', 'pca_h'), 'longest')} "
                      f"of the 35, and <b>{_hm(fra['pca_h'] - low_pca['pca_h'])}</b> more than "
                      f"Sof&iacute;a's {low_pca['country']} at the other end."),
        ("&#9749;", f"Her <b>{_hm(fra['lei_h'])}</b> of daily leisure piles up into "
                    f"<b>{_days(fra['lei_h']):.0f} entire 24-hour days</b> of free time a year."),
        ("&#128188;", f"Haruto does <b>{_hm(jpn['paw_h'] - fra['paw_h'])}</b> more paid work than her "
                      f"every single day — about <b>{_days(jpn['paw_h'] - fra['paw_h']):.0f} extra days</b> "
                      f"at work per year."),
        ("&#127958;", f"She stops working at <b>{fra['retirement_age_men']:.0f}</b>, "
                      f"<b>{jpn['retirement_age_men'] - fra['retirement_age_men']:.0f} years</b> "
                      f"before Haruto does."),
    ]

    gap_jpn = round((gByIso["JPN"]["F"] - gByIso["JPN"]["M"]) * 60)
    lei_gap_jpn = round((avg_lei - jpn["lei_h"]) * 60)
    out["JPN"] = [
        ("&#9200;", f"Japan works more paid hours than anywhere else in the data: "
                    f"<b>{_hm(jpn['paw_h'])}</b> a day, {_sup(_rank('JPN', 'paw_h'), 'most')} of the 35."),
        ("&#129529;", f"And the least unpaid work: <b>{_hm(jpn['upw_h'])}</b> a day, "
                      f"{_sup(_rank('JPN', 'upw_h', False), 'lowest')} of the 35. Someone is still doing it "
                      f"— Japanese women do <b>{gap_jpn} minutes more</b> of it a day than men."),
        ("&#127958;", f"He keeps working until about <b>{jpn['retirement_age_men']:.0f}</b>. "
                      f"Camille will have been retired for a decade by then."),
        ("&#127836;", f"His <b>{_hm(jpn['lei_h'])}</b> of daily downtime is <b>{lei_gap_jpn} minutes</b> "
                      f"below the 35-country average — the price of that workday."),
    ]

    work_mex = mex["paw_h"] + mex["upw_h"]
    r_work = [r["iso3"] for r in sorted(cp, key=lambda r: -(r["paw_h"] + r["upw_h"]))].index("MEX") + 1
    hi_lei = _edge("lei_h", high=True)
    out["MEX"] = [
        ("&#128336;", f"Paid work plus work at home adds up to <b>{_hm(work_mex)}</b> a day — "
                      f"{_sup(r_work, 'heaviest')} total workload of the 35."),
        ("&#128564;", f"Which leaves {_sup(_rank('MEX', 'lei_h', False), 'least')} downtime of the 35: "
                      f"<b>{_hm(mex['lei_h'])}</b>, while {hi_lei['country']} enjoys "
                      f"<b>{_hm(hi_lei['lei_h'] - mex['lei_h'])}</b> more."),
        ("&#128717;", f"Over a year that gap costs her "
                      f"<b>{_days(hi_lei['lei_h'] - mex['lei_h']):.0f} full days</b> of free time."),
        ("&#127958;", f"And retirement still waits until <b>{mex['retirement_age_men']:.0f}</b>, "
                      f"{_sup(_rank('MEX', 'retirement_age_men'), 'latest')} exit of the 35."),
    ]

    spread = lambda r: max(r["paw_h"], r["upw_h"], r["lei_h"]) - min(r["paw_h"], r["upw_h"], r["lei_h"])
    r_bal = [r["iso3"] for r in sorted(cp, key=spread)].index("AUS") + 1
    out["AUS"] = [
        ("&#9878;", f"Work, home and leisure sit closer together in Australia than almost anywhere: "
                    f"<b>{_hm(aus['paw_h'])}</b>, <b>{_hm(aus['upw_h'])}</b> and <b>{_hm(aus['lei_h'])}</b> "
                    f"— {_sup(r_bal, 'most balanced')} day of the 35."),
        ("&#127940;", f"Her <b>{_hm(aus['lei_h'])}</b> of daily leisure is "
                      f"<b>{_hm(aus['lei_h'] - mex['lei_h'])}</b> more than Sof&iacute;a gets."),
        ("&#127958;", f"She clocks out for good around <b>{aus['retirement_age_men']:.0f}</b>, "
                      f"almost exactly the 35-country average of "
                      f"<b>{sum(r['retirement_age_men'] for r in cp) / len(cp):.0f}</b>."),
        ("&#128176;", f"Balanced is not the same as idle: Australia still works "
                      f"<b>{aus['annual_working_hours']:.0f} hours</b> a year."),
    ]

    out["ZAF"] = [
        ("&#128197;", f"South Africa works <b>{zaf['annual_working_hours']:.0f} hours a year</b>, "
                      f"{_sup(_rank('ZAF', 'annual_working_hours'), 'longest')} work-year of the 35 — "
                      f"<b>{zaf['annual_working_hours'] - fra['annual_working_hours']:.0f} hours</b> "
                      f"more than France."),
        ("&#127881;", f"And yet he still keeps <b>{_hm(zaf['lei_h'])}</b> a day for himself, more than "
                      f"any of our other four. One of the longest work-years, and still time for friends."),
        ("&#128178;", f"He does it on {_sup(_rank('ZAF', 'gdp_per_capita_ppp', False), 'lowest')} income "
                      f"of the 35, about <b>${zaf['gdp_per_capita_ppp'] / 1000:.0f}k</b> a year per person."),
        ("&#127958;", f"He stops at <b>{zaf['retirement_age_men']:.0f}</b>, "
                      f"<b>{jpn['retirement_age_men'] - zaf['retirement_age_men']:.0f} years</b> "
                      f"earlier than Haruto."),
    ]
    assert rank5("ZAF", "lei_h") == 1, "Thabo já não tem o maior lazer dos cinco; revise a frase"
    return out


TRIVIA = build_trivia()

# médias dos 35 países, para a ficha da persona comparar "ela vs o mundo"
AVG_KEYS = {"pca_h": "pca", "paw_h": "paw", "upw_h": "upw", "lei_h": "lei", "oth_h": "oth",
            "annual_working_hours": "wh", "retirement_age_men": "ret",
            "life_satisfaction": "life", "gdp_per_capita_ppp": "gdp"}
avg = {short: sum(r[k] for r in cp) / len(cp) for k, short in AVG_KEYS.items()}

cp_by = {r["iso3"]: r for r in cp}
personas = []
for iso, name, cont, sig, bio in PERS:
    r = cp_by[iso]
    personas.append({
        "iso3": iso, "name": name, "emoji": flag(iso), "continent": cont, "sig": sig, "bio": bio,
        "country": r["country"],
        "upwF": gByIso.get(iso, {}).get("F", 0.0), "upwM": gByIso.get(iso, {}).get("M", 0.0),
        "trivia": [{"ic": ic, "t": t} for ic, t in TRIVIA[iso]],
        # Slot de vídeo: o personagem falando sobre o próprio dia. Enquanto o
        # arquivo não existir, a ficha mostra um placeholder no lugar.
        # O poster é o primeiro quadro do próprio vídeo, em 16:9 — usar o avatar
        # quadrado aqui fazia o navegador cortar o centro e dar zoom no rosto.
        # Para gerar o de um vídeo novo:
        #   ffmpeg -i fra.mp4 -frames:v 1 -vf scale=1280:-2 frame.png
        #   cwebp -q 82 frame.png -o assets/video/fra-poster.webp
        "video": f"assets/video/{iso.lower()}.mp4",
        "videoPoster": f"assets/video/{iso.lower()}-poster.webp",
        # os retratos novos entram como .png/.webp; enquanto não existirem, o
        # onerror no <img> cai de volta no .svg antigo e nada quebra
        "avatar": f"assets/avatars/{iso.lower()}.webp",
        "avatarAlt": f"assets/avatars/{iso.lower()}.svg",
        "clock": [r["pca_h"], r["paw_h"], r["upw_h"], r["lei_h"], r["oth_h"]],
        "gdp": r["gdp_per_capita_ppp"], "life": r["life_satisfaction"],
        "wh": r["annual_working_hours"], "ret": r["retirement_age_men"],
    })

# --- modelo preditivo: regressão de cada categoria de tempo vs ln(GDP) entre os 35 países ---
def _ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b
_lng = [math.log(r["gdp_per_capita_ppp"]) for r in cp]
model = {}
for _cat in ("paw_h", "lei_h", "upw_h"):
    a, b = _ols(_lng, [r[_cat] for r in cp])
    model[_cat] = {"a": a, "b": b}
print("Slopes vs ln(GDP) [h per +1 log-income]:", {k: round(v["b"], 3) for k, v in model.items()})

DATA = json.dumps({"countries": countries, "gender": gender, "personas": personas,
                   "model": model, "avg": avg})


def _clock_ticks(cx=60.0, cy=60.0, r=49.0, minor=3.5, major=7.5, n=24):
    """Marcas do relógio do hero: 24 horas, as de 6 em 6 mais longas.
    Gerado aqui em vez de um círculo tracejado no CSS, que virava tracinhos soltos."""
    parts = []
    for i in range(n):
        a = math.radians(i * 360.0 / n - 90.0)
        ln = major if i % 6 == 0 else minor
        x1, y1 = cx + math.cos(a) * (r - ln), cy + math.sin(a) * (r - ln)
        x2, y2 = cx + math.cos(a) * r, cy + math.sin(a) * r
        parts.append(f"M{x1:.2f} {y1:.2f}L{x2:.2f} {y2:.2f}")
    return "".join(parts)


CLOCK_TICKS = _clock_ticks()

GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3'/%3E"
         "%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)' opacity='.42'/%3E%3C/svg%3E")

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
CSS = r"""
/* ─────────────────────────── design tokens ─────────────────────────── */
:root{
 /* the five time categories */
 --pca:#4f5bd5; --paw:#e04b5f; --upw:#f08a24; --lei:#0fa598; --oth:#9aa5b8;
 /* brand accents */
 --accent:#8b5cf6; --hot:#fd297b; --warm:#b8600f;
 --women:#e0459b; --men:#4f5bd5;
 /* surfaces & ink (light act) */
 --ink:#141a33; --muted:#5a6285;
 --card:#ffffff; --card-2:#f7f9ff; --line:rgba(20,26,51,.10);
 --shadow:0 10px 28px -14px rgba(20,26,51,.24);
 --shadow-lg:0 28px 64px -24px rgba(20,26,51,.36);
 --r:22px; --r-sm:14px; --maxw:1160px;
 --display:"Fraunces",Georgia,"Times New Roman",serif;
 --sans:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;
 /* sky stops, animated from JS as you scroll */
 --s0:#e9eeff; --s1:#fdf1e6; --s2:#ffe3d0;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--sans);font-size:16px;line-height:1.62;color:var(--ink);
 background:#eef2ff;overflow-x:clip;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;}
img{max-width:100%}
button{font:inherit}
/* the UA rule for [hidden] is display:none at the lowest specificity, so any
   author display declaration silently beats it (e.g. .pgrid{display:grid}) */
[hidden]{display:none!important}
::selection{background:rgba(139,92,246,.22)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:6px}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}

.skip{position:absolute;left:-999px;top:0;background:var(--accent);color:#fff;padding:12px 18px;
 border-radius:0 0 10px 0;z-index:99;font-weight:600;}
.skip:focus{left:0}

/* ─────────────────────── the sky: scroll = time of day ─────────────────────── */
.sky{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
/* base gradient: a full day-to-night arc on its own, so the page still reads
   correctly before (or without) the illustrated sky images */
.sky .grad{position:absolute;inset:0;
 background:linear-gradient(180deg,var(--s0) 0%,var(--s1) 54%,var(--s2) 100%)}
/* illustrated sky: one fixed layer per keyframe, crossfaded by scroll */
.sky .lyr{position:absolute;inset:-4% 0;opacity:0;background-repeat:no-repeat;
 background-size:cover;background-position:50% calc(50% + var(--drift,0px));
 will-change:opacity}
.sky .clouds{position:absolute;inset:-6% -12%;opacity:0;background-repeat:repeat-x;
 background-size:auto 100%;background-position:var(--cloudX,0px) 50%}
.sky.has-img .sun,.sky.has-img .rays{display:none}
.sky .sun{position:absolute;left:var(--sunX,50%);bottom:var(--sunY,-16%);width:min(54vw,580px);aspect-ratio:1;
 transform:translate(-50%,50%);border-radius:50%;opacity:var(--sunO,.5);filter:blur(2px);
 background:radial-gradient(circle,rgba(255,232,146,.92),rgba(255,164,60,.42) 44%,transparent 70%)}
.sky .rays{position:absolute;left:var(--sunX,50%);bottom:var(--sunY,-16%);width:210vmax;aspect-ratio:1;
 transform:translate(-50%,50%);opacity:var(--rayO,.1)}
.sky .rays i{display:block;width:100%;height:100%;border-radius:50%;
 background:repeating-conic-gradient(from 0deg,rgba(255,190,105,.15) 0 2.4deg,transparent 2.4deg 16deg);
 animation:spin 200s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.grain{position:fixed;inset:0;z-index:1;pointer-events:none;opacity:.55;mix-blend-mode:soft-light;
 background-image:url("__GRAIN__")}
@media(prefers-reduced-motion:reduce){.sky .rays i{animation:none}}

/* ───────────────────── the day bar: a sun crossing the top ───────────────────── */
.daybar{position:fixed;top:0;left:0;right:0;height:3px;z-index:60;background:rgba(20,26,51,.09)}
.daybar i{position:absolute;inset:0 auto 0 0;width:var(--p,0%);
 background:linear-gradient(90deg,#7c6ce8,#ffb428 55%,#fd297b)}
.daybar b{position:absolute;top:50%;left:var(--p,0%);width:15px;height:15px;margin:-7.5px 0 0 -7.5px;
 border-radius:50%;background:radial-gradient(circle,#fff8d4,#ffb428 70%);
 box-shadow:0 0 16px 5px rgba(255,180,40,.5)}

/* chapter rail */
.rail{position:fixed;right:20px;top:50%;transform:translateY(-50%);z-index:55;
 display:flex;flex-direction:column;gap:14px}
.rail a{width:9px;height:9px;border-radius:50%;background:rgba(120,130,175,.42);
 box-shadow:0 0 0 1px rgba(255,255,255,.55);transition:transform .3s,background .3s;position:relative}
.rail a:hover,.rail a.on{background:var(--accent);transform:scale(1.55)}
.rail a span{position:absolute;right:20px;top:50%;transform:translateY(-50%);white-space:nowrap;
 font-size:11px;letter-spacing:.09em;text-transform:uppercase;font-weight:600;color:#fff;
 background:rgba(16,20,44,.92);padding:5px 10px;border-radius:8px;opacity:0;pointer-events:none;transition:opacity .25s}
.rail a:hover span{opacity:1}
@media(max-width:960px){.rail{display:none}}

.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px;position:relative;z-index:2}
.wrap.tail{padding-bottom:110px}
section{margin-top:112px}
.reveal{opacity:0;transform:translateY(30px);transition-delay:var(--d,0s);
 transition:opacity .8s cubic-bezier(.2,.7,.2,1),transform .8s cubic-bezier(.2,.7,.2,1)}
.reveal.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none}}

/* ───────────────────────────── the night acts ───────────────────────────── */
/* ───────── feature bands: full-bleed emphasis for the two key chapters ─────────
   These used to carry their own opaque night background plus a CSS starfield,
   from before the illustrated sky existed. That fought the sky and cut a hard
   seam across it. Now they only lay a soft veil over whatever sky is behind,
   feathered at both edges so there is no seam, and they no longer override the
   ink — the global mood does that, in step with the sky. */
.act{position:relative;z-index:2;padding:80px 0 84px;margin-top:112px}
.act::before{content:"";position:absolute;left:50%;top:0;bottom:0;width:100vw;
 transform:translateX(-50%);z-index:-1;pointer-events:none;
 background:linear-gradient(180deg,transparent 0%,rgba(12,16,42,.18) 15%,
  rgba(12,16,42,.18) 85%,transparent 100%)}
.act>.inner{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.act section{margin-top:0}
.act section+section{margin-top:88px}

/* ───────── night mood: the ink inverts once the sky goes dark ───────── */
html[data-mood="dark"]{
 --ink:#f3f5ff; --muted:#a8afd2;
 --card:rgba(255,255,255,.075); --card-2:rgba(255,255,255,.045);
 --line:rgba(255,255,255,.14);
 --shadow:0 18px 44px -20px rgba(0,0,0,.6);
 --shadow-lg:0 34px 80px -26px rgba(0,0,0,.72);
 --warm:#ffc37a}
html[data-mood="dark"] .daybar{background:rgba(255,255,255,.15)}
html[data-mood="dark"] .grain{opacity:.32}
html[data-mood="dark"] .road{background:linear-gradient(180deg,#3a4250,#222832)}
/* the mood flip changes custom properties; these transitions carry it smoothly */
body,.panel,.quiz,.pcard,.legend,.mappanel,.ai,.note,.pollopt,.predkpis .k,
.predquick button,.predctrl select,.chapno,.phalo .hrs,.matchbody,.road,
.grain,.daybar{
 transition:background-color .9s ease,border-color .9s ease,color .9s ease,
  box-shadow .9s ease,opacity .9s ease,background .9s ease}
@media(prefers-reduced-motion:reduce){
 body,.panel,.quiz,.pcard,.legend,.mappanel,.ai,.note,.pollopt,.predkpis .k,
 .predquick button,.predctrl select,.chapno,.phalo .hrs,.matchbody,.road,
 .grain,.daybar{transition:none}}
"""

# ── typography, hero and section furniture ──
CSS_TYPE = r"""
/* ─────────────────────────────── hero ─────────────────────────────── */
.hero{min-height:100svh;display:flex;flex-direction:column;align-items:center;justify-content:center;
 text-align:center;position:relative;padding:84px 0 40px}
/* a real, legible clock on a frosted disc — the old version was a faint ring
   behind the title and just read as scattered dashes over the clouds */
.heroclock{width:152px;height:152px;margin:0 auto 24px;border-radius:50%;flex:0 0 auto;
 background:rgba(255,255,255,.5);backdrop-filter:blur(6px) saturate(1.15);
 box-shadow:0 0 0 1px rgba(255,255,255,.8),0 20px 44px -20px rgba(20,26,51,.45),
  inset 0 1px 0 rgba(255,255,255,.9)}
.heroclock svg{width:100%;height:100%;display:block}
.heroclock .ticks{stroke:#59618a;stroke-width:1.7;stroke-linecap:round;opacity:.75}
.heroclock .hh{stroke:var(--pca);stroke-width:4.2;stroke-linecap:round}
.heroclock .mh{stroke:var(--accent);stroke-width:3.1;stroke-linecap:round}
.heroclock .sh2{stroke:var(--upw);stroke-width:1.7;stroke-linecap:round}
.heroclock .pin{fill:var(--ink)}
.kicker{font-size:11.5px;letter-spacing:.28em;text-transform:uppercase;color:var(--warm);
 font-weight:700;margin-bottom:18px}
/* heavier weight and a darker gradient: at 116px the old 300 weight was hairline,
   and the warm end (#f08a24) had almost no contrast against a pale sky */
.hero h1{font-family:var(--display);font-weight:600;font-size:clamp(46px,9.6vw,116px);
 line-height:.92;letter-spacing:-.03em;font-variation-settings:"SOFT" 24,"WONK" 1;
 background:linear-gradient(104deg,#232c5e 0%,#3f4bc4 28%,#8b3fa8 54%,#b32f57 78%,#c2551a 100%);
 -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
 padding-bottom:.06em;filter:drop-shadow(0 3px 12px rgba(20,26,51,.2))}
.hero .lead{font-size:clamp(16px,1.6vw,19.5px);color:var(--muted);max-width:66ch;margin:22px auto 0}
.hero .lead b{color:var(--ink);font-weight:600}

/* the stat rail needs a real surface: hairline rules alone vanished on the clouds */
.stats{display:flex;flex-wrap:wrap;justify-content:center;margin-top:46px;overflow:hidden;
 background:rgba(255,255,255,.55);backdrop-filter:blur(9px) saturate(1.1);
 border:1px solid rgba(255,255,255,.8);border-radius:var(--r);
 box-shadow:0 22px 52px -26px rgba(20,26,51,.42)}
.stat{padding:22px 34px;min-width:168px;position:relative}
.stat+.stat::before{content:"";position:absolute;left:0;top:20%;bottom:20%;width:1px;
 background:linear-gradient(180deg,transparent,rgba(20,26,51,.18),transparent)}
.stat .n{font-family:var(--display);font-weight:600;font-size:clamp(32px,4.2vw,46px);line-height:1;
 color:var(--ac,var(--pca));font-variant-numeric:tabular-nums}
.stat .l{font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:#4c5375;
 margin-top:10px;font-weight:700}
html[data-mood="dark"] .stats,html[data-mood="dark"] .heroclock{
 background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.22)}
html[data-mood="dark"] .stat .l{color:var(--muted)}
.stat .ki{width:22px;height:22px;margin-bottom:12px;opacity:.7;fill:none;
 stroke:var(--ac,var(--pca));stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.scrollcue{margin-top:54px;display:flex;flex-direction:column;align-items:center;gap:10px;
 font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);font-weight:600}
.scrollcue i{width:1px;height:44px;background:linear-gradient(180deg,var(--muted),transparent);
 animation:drop 2.4s ease-in-out infinite}
@keyframes drop{0%,100%{opacity:.25;transform:scaleY(.55)}50%{opacity:1;transform:scaleY(1)}}
@media(prefers-reduced-motion:reduce){.scrollcue i{animation:none}}

/* ─────────────────────── section headers ─────────────────────── */
.shead{display:flex;align-items:center;gap:13px;flex-wrap:wrap;margin-bottom:6px}
.chapno{font-family:var(--display);font-size:13px;font-weight:600;color:var(--accent);
 border:1px solid var(--line);background:var(--card);border-radius:999px;padding:3px 11px}
.sh{font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);font-weight:600}
.tchip{font-size:11px;letter-spacing:.12em;color:var(--muted);border-left:1px solid var(--line);
 padding-left:13px;font-variant-numeric:tabular-nums;text-transform:uppercase;font-weight:600}
h2{font-family:var(--display);font-weight:400;font-size:clamp(30px,4.6vw,50px);line-height:1.05;
 letter-spacing:-.022em;margin:6px 0 14px;font-variation-settings:"SOFT" 30,"WONK" 1}
h2 em{font-style:italic;font-variation-settings:"WONK" 1}
.sub{font-size:16.5px;color:var(--muted);max-width:74ch;margin-bottom:28px}
.sub b{color:var(--ink);font-weight:600}
.aha{color:var(--warm);font-weight:600;box-shadow:inset 0 -.48em 0 rgba(240,138,36,.18)}
html[data-mood="dark"] .aha{box-shadow:inset 0 -.48em 0 rgba(255,195,122,.15)}

.legend{display:flex;gap:12px 22px;flex-wrap:wrap;margin-top:36px;padding:18px 22px;
 background:var(--card);border:1px solid var(--line);border-radius:var(--r-sm);box-shadow:var(--shadow)}
.legend span{display:flex;align-items:center;gap:9px;font-size:12.5px;color:var(--muted);font-weight:500}
.dot{width:11px;height:11px;border-radius:3px;flex:0 0 auto}

.panel{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:28px;
 box-shadow:var(--shadow);backdrop-filter:blur(8px)}
.note{margin-top:72px;font-size:12.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:22px;line-height:1.75}
.note b{color:var(--ink);font-weight:600}
.ai{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:28px;box-shadow:var(--shadow)}
.ai ul{margin:6px 0 0 20px;color:var(--muted);font-size:14.5px}
.ai li{margin:8px 0}
"""

# ── data-viz components ──
CSS_VIZ = r"""
/* ───────────────────────── personas: the 24h halo ───────────────────────── */
/* 3 on the first row, 2 centred on the second. auto-fit was fitting 4 and
   leaving the fifth persona orphaned; flex lets the last row centre itself.
   Capping the row width (not the card) is what keeps the tiles slim: with the
   full 1112px available, three cards would stretch to ~357px each. */
.pgrid{display:flex;flex-wrap:wrap;gap:20px;justify-content:center;
 max-width:840px;margin:0 auto}
.pgrid>.pcard{flex:0 1 calc((100% - 40px)/3)}
@media(max-width:900px){.pgrid>.pcard{flex:0 1 calc((100% - 20px)/2)}}
@media(max-width:560px){.pgrid>.pcard{flex:0 1 100%}}
/* the card is a real <button>: keyboard, focus and Enter/Space come for free */
.pcard{position:relative;overflow:hidden;background:var(--card);border:1px solid var(--line);
 border-radius:var(--r);padding:28px 20px 22px;text-align:center;box-shadow:var(--shadow);
 font:inherit;color:inherit;width:auto;display:block;cursor:pointer;
 transition:transform .4s cubic-bezier(.2,.7,.2,1),box-shadow .4s}
.pcard::before{content:"";position:absolute;inset:0 0 auto;height:3px;
 background:linear-gradient(90deg,var(--pca),var(--paw),var(--upw),var(--lei))}
.pcard:hover{transform:translateY(-8px);box-shadow:var(--shadow-lg)}
.cont{font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);font-weight:600}
.phalo{position:relative;width:180px;height:180px;margin:10px auto 12px}
.phalo canvas{position:absolute;inset:0}
.phalo .avatar{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
 width:112px;height:112px;border-radius:50%;background:#eef1ff;object-fit:cover;
 box-shadow:0 10px 26px -10px rgba(20,26,51,.45)}
/* hover caption under the ring. Chart.js paints its tooltip inside the canvas,
   where the portrait covered the middle of it and the 180px canvas clipped the
   ends. A line we control is never covered and never cut. */
.phov{min-height:34px;display:flex;align-items:center;justify-content:center;gap:8px;
 font-size:12.5px;font-weight:600;color:var(--ink);line-height:1.3;padding:0 6px}
.phov i{width:9px;height:9px;border-radius:2px;flex:0 0 auto}
.phov.idle{color:var(--muted);font-weight:500;font-style:italic}
.phalo .hrs{position:absolute;left:50%;bottom:-6px;transform:translateX(-50%);
 font-size:9.5px;letter-spacing:.18em;text-transform:uppercase;font-weight:700;color:var(--muted);
 background:var(--card);border:1px solid var(--line);border-radius:999px;padding:3px 10px}
.pname{font-family:var(--display);font-size:23px;font-weight:500;letter-spacing:-.01em}
.pflag{font-size:16px}
.sig{color:var(--warm);font-size:12.5px;font-weight:700;margin:8px 0}
.bio{color:var(--muted);font-size:12.5px;line-height:1.62;margin-bottom:16px;min-height:116px}
.pstats{display:flex;justify-content:space-around;font-size:10.5px;letter-spacing:.1em;
 text-transform:uppercase;color:var(--muted);font-weight:600;border-top:1px solid var(--line);padding-top:14px}
.pstats b{display:block;font-family:var(--display);font-size:19px;font-weight:500;
 letter-spacing:0;text-transform:none;color:var(--ink);margin-bottom:2px}

/* ──────────────── persona detail: inline, replaces the grid in place ──────────────── */
.phint{margin-top:12px;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
 font-weight:700;color:var(--accent);opacity:.75;transition:opacity .3s}
.pcard:hover .phint,.pcard:focus-visible .phint{opacity:1}
/* the grid steps aside instead of a popup opening over it */
.pgrid{transition:opacity .45s ease,transform .45s ease}
.pgrid.out{opacity:0;transform:scale(.97);pointer-events:none}
.pdetail:focus{outline:none}
.pdcols{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start;margin-top:22px}
.pdcol{display:flex;flex-direction:column;gap:22px}
.pdetail>.panel{margin-top:22px}
.pdetail h4{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);
 font-weight:700;margin-bottom:14px}
.pdback{display:inline-flex;align-items:center;gap:8px;background:var(--card);
 border:1px solid var(--line);border-radius:999px;padding:10px 20px;cursor:pointer;
 font:inherit;font-size:13px;font-weight:600;color:var(--ink);box-shadow:var(--shadow);
 margin-bottom:22px;transition:border-color .25s,color .25s,transform .25s}
.pdback:hover{border-color:var(--accent);color:var(--accent);transform:translateX(-3px)}
/* one thing at a time: every .st block waits its turn */
.st{opacity:0;transform:translateY(20px);
 transition:opacity .6s cubic-bezier(.2,.7,.2,1),transform .6s cubic-bezier(.2,.7,.2,1);
 transition-delay:calc(var(--i,0) * 85ms)}
.go .st{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){
 .st{opacity:1;transform:none;transition:none;transition-delay:0s}
 .pgrid{transition:none}}
@media(max-width:820px){.pdcols{grid-template-columns:1fr}}
.pmhead{display:flex;align-items:center;gap:20px;padding:24px 26px;position:relative;
 background:var(--card);border:1px solid var(--line);border-radius:var(--r);
 box-shadow:var(--shadow);
 background-image:linear-gradient(120deg,rgba(79,91,213,.1),rgba(240,138,36,.1))}
.pmhead img{width:88px;height:88px;border-radius:50%;object-fit:cover;flex:0 0 auto;
 background:#eef1ff;box-shadow:0 10px 24px -10px rgba(20,26,51,.45)}
.pmhead h3{font-family:var(--display);font-size:30px;font-weight:600;line-height:1.1}
.pmwho{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);
 font-weight:700;margin-bottom:4px}
.pmsig{color:var(--warm);font-size:13.5px;font-weight:700;margin-top:5px}
.pmbio{font-size:15.5px;color:var(--muted);line-height:1.68}
/* video slot */
.pmvid{position:relative;border-radius:16px;overflow:hidden;background:#0d1128;
 aspect-ratio:16/9;border:1px solid var(--line)}
.pmvid video{width:100%;height:100%;display:block;object-fit:cover}
.pmvidsoon{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
 justify-content:center;gap:10px;text-align:center;padding:20px;
 background:radial-gradient(circle at 50% 40%,#1c2350,#0b0f28)}
.pmvidsoon .ic{width:52px;height:52px;border-radius:50%;display:flex;align-items:center;
 justify-content:center;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
 color:#fff;font-size:19px;padding-left:4px}
.pmvidsoon b{color:#eef1ff;font-size:14px;font-weight:600}
.pmvidsoon span{color:#9aa2cc;font-size:12.5px;max-width:34ch;line-height:1.55}
/* the day, broken down */
.pmday{display:flex;gap:24px;align-items:center;flex-wrap:wrap}
.pmbars{flex:1 1 260px;min-width:240px}
/* trivia: the fun facts, all of them computed from the CSVs */
.pdtriv{list-style:none;display:flex;flex-direction:column;gap:15px}
.pdtriv li{display:flex;gap:13px;align-items:flex-start;font-size:14.5px;line-height:1.62;
 color:var(--muted)}
.pdtriv .ic{flex:0 0 auto;width:36px;height:36px;border-radius:11px;display:flex;
 align-items:center;justify-content:center;font-size:17px;
 background:var(--card-2);border:1px solid var(--line)}
html[data-mood="dark"] .pdtriv .ic{background:rgba(255,255,255,.06)}
.pdtriv b{color:var(--ink);font-weight:700}
.pmbar{display:grid;grid-template-columns:1fr auto;gap:2px 10px;margin-bottom:11px;font-size:13px}
.pmbar .nm{color:var(--ink);font-weight:500}
.pmbar .vl{font-variant-numeric:tabular-nums;font-weight:700;color:var(--ink)}
.pmbar .tr{grid-column:1/3;height:7px;border-radius:99px;background:var(--line);overflow:hidden}
.pmbar .tr i{display:block;height:100%;border-radius:99px;background:var(--bc)}
/* numbers + comparison */
.pmnums{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px}
.pmnum{background:var(--card-2);border:1px solid var(--line);border-radius:14px;
 padding:14px;text-align:center}
html[data-mood="dark"] .pmnum{background:rgba(255,255,255,.05)}
.pmnum .n{font-family:var(--display);font-size:24px;font-weight:600;line-height:1;
 font-variant-numeric:tabular-nums}
.pmnum .l{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
 font-weight:700;margin-top:7px}
.pmnum .d{font-size:11px;font-weight:700;margin-top:5px}
.pmnum .d.up{color:#0f8f7f}.pmnum .d.dn{color:#d1445c}.pmnum .d.eq{color:var(--muted)}
html[data-mood="dark"] .pmnum .d.up{color:#31d3bd}
html[data-mood="dark"] .pmnum .d.dn{color:#ff8095}
.pmnote{margin-top:16px;font-size:13px;line-height:1.6;color:var(--muted);
 border-left:2px solid var(--women);padding-left:14px}
.pmnote b{color:var(--ink);font-weight:700}
@media(max-width:560px){
 .pmhead{flex-direction:column;text-align:center;padding:22px 20px}
 .pmday{justify-content:center}
}

/* ─────────────────────────────── quiz ─────────────────────────────── */
.quiz{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:32px;
 box-shadow:var(--shadow);position:relative;overflow:hidden}
.quiz::before{content:"";position:absolute;inset:0;pointer-events:none;
 background:radial-gradient(680px 320px at 100% 0%,rgba(253,41,123,.07),transparent 62%)}
.qrow{display:flex;align-items:center;gap:18px;margin:16px 0;flex-wrap:wrap;position:relative}
.qrow label{flex:1 1 220px;font-size:14.5px;font-weight:500}
.qrow input[type=range]{flex:2 1 300px;accent-color:var(--accent);height:6px}
.qval{width:70px;text-align:right;font-family:var(--display);font-size:21px;font-weight:500;
 font-variant-numeric:tabular-nums;color:var(--pca)}
.qtotal{font-size:13px;color:var(--muted);margin-top:10px;padding-top:14px;border-top:1px solid var(--line)}
.qtotal b{color:var(--ink);font-weight:600}
.qbtn{margin-top:20px;background:linear-gradient(95deg,var(--hot),#ff6b52);color:#fff;border:0;
 border-radius:999px;padding:15px 32px;font-size:15.5px;font-weight:700;cursor:pointer;
 box-shadow:0 12px 28px -10px rgba(253,41,123,.6);transition:transform .25s,box-shadow .25s}
.qbtn:hover{transform:translateY(-2px);box-shadow:0 18px 36px -12px rgba(253,41,123,.7)}
.qresult{display:none;margin-top:26px}
.qresult.show{display:block;animation:pop .55s cubic-bezier(.2,.8,.3,1.2)}
@keyframes pop{from{opacity:0;transform:scale(.94)}to{opacity:1;transform:none}}
.matchbanner{background:linear-gradient(95deg,var(--hot),#ff6b52);color:#fff;text-align:center;
 font-family:var(--display);font-size:25px;font-weight:500;padding:16px;border-radius:18px 18px 0 0}
.matchbanner .hearts{display:inline-block;animation:beat 1s ease-in-out infinite}
@keyframes beat{0%,100%{transform:scale(1)}50%{transform:scale(1.3)}}
.matchbody{display:flex;align-items:center;gap:26px;flex-wrap:wrap;background:var(--card-2);
 border:1px solid var(--line);border-top:0;border-radius:0 0 18px 18px;padding:26px}
.matchface{font-size:62px;line-height:1;width:106px;height:106px;flex:0 0 auto;border-radius:50%;
 display:flex;align-items:center;justify-content:center;border:4px solid transparent;
 background:linear-gradient(var(--card),var(--card)) padding-box,linear-gradient(135deg,var(--hot),#ff6b52) border-box;
 box-shadow:0 10px 26px -10px rgba(253,41,123,.55)}
.matchinfo{flex:1 1 220px}
.matchinfo h3{font-family:var(--display);font-size:25px;font-weight:500;margin-bottom:9px}
.matchpct{display:inline-block;background:linear-gradient(95deg,var(--hot),#ff6b52);color:#fff;
 font-size:11.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
 padding:5px 13px;border-radius:999px;margin-bottom:11px}
.matchinfo p{color:var(--muted);font-size:13.5px}
.qbars{flex:1 1 100%;margin-top:4px;padding-top:20px;border-top:1px solid var(--line)}
.qafter{display:none;margin-top:20px;color:var(--muted);font-size:14.5px;font-style:italic;
 border-left:2px solid var(--accent);padding-left:16px}
@media(prefers-reduced-motion:reduce){.qresult.show{animation:none}.matchbanner .hearts{animation:none}}

/* ─────────── the 24h bar: a day read left to right ───────────
   Replaces the doughnuts that were repeating in the quiz, the globe panel and
   the 2050 section. A ring is fine for one portrait; four identical ones across
   the page stop carrying information. A bar also reads as a timeline, which is
   what a day is, and fits a narrow column where a circle does not. */
.dbwrap{margin-top:6px}
.dblab{display:flex;justify-content:space-between;gap:10px;font-size:10.5px;
 letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:7px}
.dblab b{color:var(--ink);font-variant-numeric:tabular-nums;letter-spacing:0}
.daybar24{display:flex;height:26px;border-radius:8px;overflow:hidden;
 box-shadow:inset 0 0 0 1px rgba(255,255,255,.4),0 4px 12px -6px rgba(20,26,51,.4)}
.daybar24 i{height:100%;transition:width .6s cubic-bezier(.2,.7,.2,1)}
.dbticks{display:flex;justify-content:space-between;font-size:10px;color:var(--muted);
 font-variant-numeric:tabular-nums;margin-top:6px}
/* hover readout: the bar showed proportion but never the value, so you could see
   one block was bigger without knowing what share of the 24h it was */
.dbhov{min-height:22px;margin-top:9px;display:flex;align-items:center;gap:8px;
 font-size:12px;font-weight:600;color:var(--ink)}
.dbhov i{width:9px;height:9px;border-radius:2px;flex:0 0 auto}
.dbhov.idle{color:var(--muted);font-weight:500;font-style:italic}
.daybar24 i{cursor:default}
.dbkey{display:flex;flex-wrap:wrap;gap:7px 14px;margin-top:12px;font-size:11.5px;color:var(--muted)}
.dbkey span{display:flex;align-items:center;gap:6px}
.dbkey i{width:9px;height:9px;border-radius:2px;flex:0 0 auto}

/* ─────────── change chart: today against the projection ───────────
   Two rings side by side made you eyeball the difference. This states it: the
   translucent bar is today, the solid one is 2050, and the tail that sticks out
   is what was gained or lost. */
.chg{display:flex;flex-direction:column;gap:13px}
.chgrow{display:grid;grid-template-columns:120px 1fr 96px;gap:14px;align-items:center;font-size:13.5px}
.chgrow .nm{font-weight:500;color:var(--ink)}
.chgtrack{position:relative;height:24px;border-radius:7px;background:var(--line);overflow:hidden}
.chgtrack i{position:absolute;top:0;bottom:0;left:0;border-radius:7px;background:var(--bc)}
.chgtrack i.now{opacity:.34}
.chgtrack i.fut{opacity:1;transition:width .7s cubic-bezier(.2,.7,.2,1)}
.chgval{text-align:right;font-variant-numeric:tabular-nums}
.chgval b{display:block;font-weight:700;color:var(--ink)}
.chgval span{font-size:11.5px;font-weight:700}
.chgval span.up{color:#0f8f7f}.chgval span.dn{color:#d1445c}.chgval span.eq{color:var(--muted)}
html[data-mood="dark"] .chgval span.up{color:#31d3bd}
html[data-mood="dark"] .chgval span.dn{color:#ff8095}
.chglegend{margin-top:16px;font-size:12px;color:var(--muted);display:flex;gap:18px;flex-wrap:wrap}
.chglegend span{display:flex;align-items:center;gap:7px}
.chglegend i{width:22px;height:11px;border-radius:3px;background:var(--pca)}
.chglegend i.faint{opacity:.34}
@media(max-width:620px){.chgrow{grid-template-columns:96px 1fr 82px;gap:10px;font-size:12.5px}}

/* ───────────────────────── globe ───────────────────────── */
.mapwrap{display:grid;grid-template-columns:1.85fr 1fr;gap:22px}
@media(max-width:880px){.mapwrap{grid-template-columns:1fr}}
#globe{height:560px;border-radius:var(--r);overflow:hidden;position:relative;
 display:flex;align-items:center;justify-content:center;
 background:radial-gradient(circle at 50% 34%,#1b2455,#080c22 72%);
 border:1px solid rgba(255,255,255,.1);box-shadow:var(--shadow-lg)}
#globe::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:inherit;
 background:radial-gradient(circle at 50% 38%,transparent 52%,rgba(5,8,24,.5))}
.mappanel{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:24px;
 box-shadow:var(--shadow);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.mappanel .hint{color:var(--muted);font-size:14.5px;line-height:1.7}
.mpflag{font-size:46px;line-height:1}
.mpname{font-family:var(--display);font-size:23px;font-weight:500;margin-top:6px}
.mpstats{width:100%;font-size:12.5px;color:var(--muted)}
.mpstats div{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line)}
.mpstats div:last-child{border-bottom:0}
.mpstats b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
.maplegend{display:flex;align-items:center;gap:12px;font-size:11.5px;letter-spacing:.08em;
 text-transform:uppercase;font-weight:600;color:var(--muted);margin-top:16px}
.maplegend .bar{height:8px;width:180px;border-radius:999px;
 background:linear-gradient(90deg,#ffd60a,#ff8c1a,#d61440)}

/* ──────────── topic picker: pick a slice of the day, see who leads ────────────
   The cards stay on screen and act as a selector: the ranking below swaps in
   place. Hiding them on click would make comparing two categories a round trip.
   Each card has a gradient fallback behind the image, so a missing file still
   reads as a card instead of a blank box. */
.tgrid{display:flex;flex-wrap:wrap;gap:18px;justify-content:center}
.tgrid>.tcard{flex:0 1 calc((100% - 36px)/3)}
@media(max-width:900px){.tgrid>.tcard{flex:0 1 calc((100% - 18px)/2)}}
@media(max-width:560px){.tgrid>.tcard{flex:0 1 100%}}
.tcard{position:relative;aspect-ratio:4/3;border-radius:18px;overflow:hidden;cursor:pointer;
 border:1px solid var(--line);padding:0;font:inherit;color:#fff;box-shadow:var(--shadow);
 background-image:var(--img),var(--fb);background-size:cover;background-position:center;
 transition:transform .35s cubic-bezier(.2,.7,.2,1),box-shadow .35s}
.tcard:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg)}
.tcard::after{content:"";position:absolute;inset:0;
 background:linear-gradient(180deg,rgba(10,14,36,0) 34%,rgba(10,14,36,.8))}
.tcard b{position:absolute;left:0;right:0;bottom:0;z-index:1;padding:18px 18px 20px;
 font-family:var(--display);font-size:24px;font-weight:600;line-height:1.15;
 text-align:center;text-shadow:0 2px 14px rgba(0,0,0,.65)}

.tcard.on{outline:3px solid var(--accent);outline-offset:3px}
.tcard.on::after{background:linear-gradient(180deg,rgba(10,14,36,0) 26%,rgba(10,14,36,.86))}
.trank{margin-top:28px}
.trankcap{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:6px}
.trankcap h3{font-family:var(--display);font-size:26px;font-weight:600}
.trankcap span{font-size:13.5px;color:var(--muted)}
.tnote{margin-top:20px;padding-top:18px;border-top:1px solid var(--line);
 font-size:13.5px;color:var(--muted);line-height:1.6}
.tnote b{color:var(--ink);font-weight:700}

/* ──────────────── ranking bubbles: flags sized by value ──────────────── */
.bubbles{display:flex;flex-wrap:wrap;gap:30px 26px;align-items:flex-end;justify-content:center;padding:16px 0}
.bub{text-align:center;transition:transform .35s cubic-bezier(.2,.7,.2,1)}
.bub:hover{transform:translateY(-6px)}
.bub .circ{border-radius:50%;overflow:hidden;margin:0 auto 12px;
 box-shadow:0 0 0 3px var(--card),0 0 0 6px var(--ringc,var(--paw)),0 16px 30px -14px rgba(20,26,51,.5)}
.bub .circ img{width:100%;height:100%;object-fit:cover;display:block}
.bub .bnm{font-size:12.5px;font-weight:600}
.bub .bvl{font-family:var(--display);font-size:16px;font-weight:500;color:var(--ringc,var(--paw));
 font-variant-numeric:tabular-nums}

/* ──────────────── the twin charts (double shift) ──────────────── */
.twinwrap{display:grid;grid-template-columns:1fr 1fr;gap:22px}
@media(max-width:780px){.twinwrap{grid-template-columns:1fr}}
.tcap{text-align:center;font-size:15px;font-weight:700;margin-bottom:6px}
.tcap span{display:block;font-size:11.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
 color:var(--muted);margin-top:5px}
.chartbox{position:relative;height:440px}
.chartbox.twin{height:430px}

/* ──────────────── retirement road ──────────────── */
.road-panel{overflow:hidden}
.rsigns{position:relative;height:78px}
.rsign{position:absolute;top:0;background:linear-gradient(180deg,#35995a,#237343);color:#fff;
 border:2px solid rgba(255,255,255,.9);border-radius:10px;padding:11px 17px;font-weight:800;
 letter-spacing:.06em;font-size:16px;box-shadow:0 10px 22px -10px rgba(0,0,0,.55)}
.rsign small{display:block;font-size:10.5px;font-weight:600;letter-spacing:.04em;opacity:.9;margin-top:2px}
.rsign.left{left:2px}
.rsign.right{right:2px;text-align:right}
.rfield{position:relative;width:100%;height:340px}
.rmk{position:absolute;transform:translateX(-50%);transition:transform .25s cubic-bezier(.2,.7,.2,1)}
.rmk:hover{transform:translateX(-50%) scale(1.35);z-index:5}
.rmk img{width:40px;height:40px;border-radius:50%;object-fit:cover;display:block;
 border:2px solid var(--card);box-shadow:0 6px 14px -6px rgba(20,26,51,.6);background:#eef1ff}
.rmk.p img{border-color:#ffcf33;border-width:3px;box-shadow:0 0 0 3px rgba(255,207,51,.28),0 6px 14px -6px rgba(20,26,51,.6)}
.road{position:relative;height:64px;border-radius:12px;margin-top:6px;
 background:linear-gradient(180deg,#48525f,#2c333f);
 box-shadow:inset 0 2px 0 rgba(255,255,255,.13),inset 0 -3px 0 rgba(0,0,0,.32)}
.road .lane{position:absolute;top:50%;left:2%;right:2%;height:4px;transform:translateY(-50%);border-radius:2px;
 background:repeating-linear-gradient(90deg,#ffd83b 0 28px,transparent 28px 56px)}
.rtick{position:absolute;transform:translateX(-50%);top:12px;font-size:12px;color:rgba(255,255,255,.92);
 font-weight:700;font-variant-numeric:tabular-nums}

/* ──────────────── predictive: the day of 2050 ──────────────── */
.predctrl{display:flex;gap:28px;flex-wrap:wrap;align-items:center;margin-bottom:22px;
 padding-bottom:22px;border-bottom:1px solid var(--line)}
.predctrl label{font-size:14px;display:flex;gap:9px;align-items:center;flex-wrap:wrap;font-weight:500}
.predctrl select{padding:9px 12px;border-radius:10px;border:1px solid var(--line);
 background:var(--card-2);color:var(--ink);font:inherit;font-size:14px}
.predctrl input[type=range]{accent-color:var(--accent);min-width:220px}
.predquick{display:flex;gap:9px;flex-wrap:wrap}
.predquick button{background:var(--card-2);border:1px solid var(--line);border-radius:999px;
 padding:8px 16px;cursor:pointer;font-size:13px;font-weight:600;color:var(--ink);transition:background .25s,border-color .25s}
.predquick button:hover{border-color:var(--accent)}
.predkpis{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:28px}
.predkpis .k{flex:1 1 160px;background:var(--card-2);border:1px solid var(--line);
 border-radius:var(--r-sm);padding:18px;text-align:center}
.predkpis .k .n{font-family:var(--display);font-size:30px;font-weight:500;font-variant-numeric:tabular-nums}
.predkpis .k .l{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
 margin-top:6px;font-weight:600}
.predtext{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:30px}
@media(max-width:700px){.predtext{grid-template-columns:1fr}}
.ptcard{border-radius:var(--r-sm);padding:20px 22px}
.ptcard h4{font-size:14.5px;margin-bottom:8px;letter-spacing:.02em}
.ptcard p{font-size:13.5px;color:var(--muted);line-height:1.68}
.ptcard b{color:var(--ink);font-weight:600}
.ptcard.up{background:rgba(15,165,152,.14);border:1px solid rgba(15,165,152,.34)}
.ptcard.up h4{color:#31d3bd}
.ptcard.catch{background:rgba(240,138,36,.14);border:1px solid rgba(240,138,36,.34)}
.ptcard.catch h4{color:#ffb45c}

/* ──────────────── closing poll ──────────────── */
.poll{max-width:640px;margin:28px auto 0}
.pollq{text-align:center;font-family:var(--display);font-size:20px;font-weight:500;margin-bottom:16px}
.pollopt{display:block;width:100%;text-align:left;background:var(--card);border:1px solid var(--line);
 border-radius:var(--r-sm);padding:16px 18px;margin:10px 0;cursor:pointer;font-size:15px;
 color:var(--ink);position:relative;overflow:hidden;box-shadow:var(--shadow);
 transition:border-color .25s,transform .12s}
.pollopt:hover{border-color:var(--accent)}
.pollopt:active{transform:scale(.99)}
.pollopt .fill{position:absolute;left:0;top:0;bottom:0;width:0;z-index:0;
 background:linear-gradient(90deg,rgba(139,92,246,.22),rgba(240,138,36,.16));
 transition:width .8s cubic-bezier(.2,.8,.3,1)}
.pollopt .lbl,.pollopt .pct{position:relative;z-index:1}
.pollopt .pct{float:right;font-family:var(--display);font-weight:600;color:var(--accent);display:none}
.poll.voted .pct{display:inline}
.poll.voted .pollopt{cursor:default}
.pollopt.mine{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent),var(--shadow)}
.pollnote{font-size:12px;color:var(--muted);margin-top:16px;text-align:center}
@media(prefers-reduced-motion:reduce){.pollopt .fill{transition:none}}

@media(max-width:640px){
 .wrap{padding:0 18px 80px}
 section{margin-top:82px}
 .act{margin-top:82px;padding:60px 0 64px}
 .panel,.quiz{padding:22px}
 .stat{padding:20px 24px;min-width:50%}
 .stat+.stat::before{display:none}
}
"""

# ══════════════════════════════════════════════════════════════════════════════
# BODY
# ══════════════════════════════════════════════════════════════════════════════
BODY = r"""
<a href="#main" class="skip">Skip to main content</a>

<div class="sky" id="sky" aria-hidden="true">
  <div class="grad"></div>
  <!-- illustrated sky layers are injected here, before the drifting clouds -->
  <div class="clouds" id="skyClouds"></div>
  <div class="sun"></div>
  <div class="rays"><i></i></div>
</div>
<div class="grain" aria-hidden="true"></div>
<div class="daybar" aria-hidden="true"><i></i><b></b></div>
<nav class="rail" id="rail" aria-label="Chapters"></nav>

<div class="wrap" id="main">

<header class="hero reveal">
  <div class="heroclock">
    <svg viewBox="0 0 120 120" role="img" aria-label="A clock counting the hours of a day">
      <path class="ticks" fill="none" d="__TICKS__"/>
      <g fill="none">
        <line class="hh" x1="60" y1="60" x2="60" y2="36">
          <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="720s" repeatCount="indefinite"/></line>
        <line class="mh" x1="60" y1="60" x2="60" y2="24">
          <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="60s" repeatCount="indefinite"/></line>
        <line class="sh2" x1="60" y1="65" x2="60" y2="18">
          <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="4s" repeatCount="indefinite"/></line>
      </g>
      <circle class="pin" cx="60" cy="60" r="2.8"/>
    </svg>
  </div>
  <div class="kicker">An interactive data story &middot; VizCon 2026</div>
  <h1>The 24-Hour Human</h1>
  <p class="lead">What can you do in 24 hours? And what does the rest of the world do with theirs? Discover how many hours we work, how much time we keep for leisure, and how the place you live shapes what your day looks like. All inside the same <b>1,440 minutes</b> each of us is given, every single day.</p>
  <div class="stats">
    <div class="stat" style="--ac:#f08a24">
      <svg class="ki" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 1.8"/></svg>
      <div class="n" data-target="1440">0</div><div class="l">Minutes everyone gets</div></div>
    <div class="stat" style="--ac:#4f5bd5">
      <svg class="ki" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c3.4 3 3.4 15 0 18c-3.4-3-3.4-15 0-18z"/></svg>
      <div class="n" data-target="35">0</div><div class="l">Countries</div></div>
    <div class="stat" style="--ac:#0fa598">
      <svg class="ki" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 3 8l9 5 9-5-9-5z"/><path d="M4 12l8 4.5L20 12"/><path d="M4 16l8 4.5L20 16"/></svg>
      <div class="n" data-target="5">0</div><div class="l">Continents</div></div>
    <div class="stat" style="--ac:#e0459b">
      <svg class="ki" viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3.2"/><circle cx="16.5" cy="9" r="2.6"/><path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><path d="M14.6 19c.2-2.2 1.8-3.7 4-3.7s3.8 1.5 3.9 3.7"/></svg>
      <div class="n" data-target="2">0</div><div class="l">Genders compared</div></div>
  </div>
  <div class="scrollcue">Scroll to walk through the day<i></i></div>
</header>

<div class="legend reveal">
  <span><i class="dot" style="background:var(--pca)"></i>Personal care (sleep, meals, hygiene)</span>
  <span><i class="dot" style="background:var(--paw)"></i>Paid work / study</span>
  <span><i class="dot" style="background:var(--upw)"></i>Unpaid work (home, care)</span>
  <span><i class="dot" style="background:var(--lei)"></i>Leisure</span>
  <span><i class="dot" style="background:var(--oth)"></i>Other</span>
</div>

<section class="reveal" id="ch-personas" data-nav="Five lives">
  <div class="shead"><span class="chapno">01</span><span class="sh">Meet our humans</span><span class="tchip">07:00 &middot; Morning</span></div>
  <h2>One day, <em>five lives</em></h2>
  <p class="sub">Meet our neighbors from around the world, one from each continent. Here's where you'll see how a single day can look completely different depending on where you stand, and how that everyday routine really plays out across the globe. What could each place add to your own day? (Each ring is one real 24-hour day; hover to explore the hours.)</p>
  <div class="pgrid" id="personaGrid"></div>
  <div class="pdetail" id="personaDetail" tabindex="-1" hidden></div>
</section>

<section class="reveal" id="ch-topics" data-nav="Who does it most">
  <div class="shead"><span class="chapno">02</span><span class="sh">The first surprise</span><span class="tchip">09:00 &middot; Morning</span></div>
  <h2>Who does it <em>most?</em></h2>
  <p class="sub">The same 1,440 minutes, split five ways &mdash; and every one of those slices has a world champion. <span class="aha">Pick a piece of the day</span> to see which countries spend the most of it, and which one sits at the other end. Some rankings are exactly what you would guess. One of them is the first real surprise in this data.</p>
  <div class="tgrid" id="topicGrid"></div>
  <div class="trank" id="topicRank"></div>
</section>

<section class="reveal" id="ch-quiz" data-nav="Your match">
  <div class="shead"><span class="chapno">03</span><span class="sh">Now your turn</span><span class="tchip">11:00</span></div>
  <h2>Which human <em>are you?</em></h2>
  <p class="sub">Now that you've met them, let's figure out your ideal day. Slide each bar to what feels best for you: give more time to what matters most, and less to what matters least. Think about what motivates you and makes you happiest. Then, <span class="aha">just like Tinder, we'll reveal your perfect match:</span> which of the 35 countries around the world would give you your 'perfect day'. So... who's your match?</p>
  <div class="quiz">
    <div class="qrow"><label for="q_pca">Sleep, meals &amp; self-care</label>
      <input type="range" id="q_pca" min="0" max="16" step="0.5" value="10" aria-label="Hours on sleep, meals and self-care"><span class="qval" id="v_pca">10h</span></div>
    <div class="qrow"><label for="q_paw">Paid work / study</label>
      <input type="range" id="q_paw" min="0" max="14" step="0.5" value="5" aria-label="Hours on paid work or study"><span class="qval" id="v_paw">5h</span></div>
    <div class="qrow"><label for="q_upw">Unpaid work (chores, care)</label>
      <input type="range" id="q_upw" min="0" max="10" step="0.5" value="3" aria-label="Hours on unpaid work"><span class="qval" id="v_upw">3h</span></div>
    <div class="qrow"><label for="q_lei">Leisure</label>
      <input type="range" id="q_lei" min="0" max="12" step="0.5" value="4" aria-label="Hours on leisure"><span class="qval" id="v_lei">4h</span></div>
    <div class="qtotal" id="qtotal"></div>
    <button class="qbtn" id="qbtn">Who's my match? &#128156;</button>
    <div class="qresult" id="qresult" aria-live="polite">
      <div class="matchbanner">It's a match! <span class="hearts">&#128150;</span></div>
      <div class="matchbody">
        <div class="matchface" id="rflag"></div>
        <div class="matchinfo"><h3 id="rname"></h3><div class="matchpct" id="rpct"></div><p id="rdesc"></p></div>
        <div class="qbars" id="qbars"></div>
      </div>
    </div>
    <p class="qafter" id="qafter">Your day isn't just yours. Millions of people half a world away wake to almost the same rhythm. Time use is personal, but it's also deeply cultural. Keep that in mind as we zoom out.</p>
  </div>
</section>

<section class="reveal" id="ch-globe" data-nav="The globe">
  <div class="shead"><span class="chapno">04</span><span class="sh">Explore all 35</span><span class="tchip">12:00 &middot; Midday</span></div>
  <h2>Where people <em>spend their time</em></h2>
  <p class="sub">So, how's the world out there? Each dot is a country we mapped, <span class="aha">colored from yellow (fewer work hours) to red (more) across the year</span>. Spin it and a pattern shows up: the busy red dots cluster where incomes are lower, while the calmer yellow ones sit among the wealthy. Find the country you're curious about and dive deep: click it to open its 24-hour day. (It's a little sad, but you'll spot a gap over South America. The honest limit of our data.)</p>
  <div class="mapwrap">
    <div id="globe"></div>
    <div class="mappanel" id="mapPanel">
      <div class="hint">&#128070; Click a country on the map to reveal its day.</div>
    </div>
  </div>
  <div class="maplegend"><span>Fewer work hours/yr</span><span class="bar"></span><span>More work hours/yr</span></div>
</section>

</div><!-- /wrap -->

<div class="act" id="ch-shift" data-nav="The double shift"><div class="inner">
<section class="reveal">
  <div class="shead"><span class="chapno">05</span><span class="sh">The heart of the story</span><span class="tchip">20:00 &middot; Night</span></div>
  <h2>The <em>double shift</em></h2>
  <p class="sub">The double shift, and one stubborn question: why is it almost always women? There's a second shift, the invisible one: cooking, cleaning, raising children, caring for elders. It never shows on a payslip, it sits outside policy indicators, and it stays out of the conversation. Around the world it lands overwhelmingly on women. <span class="aha">In India, women do about five more hours of unpaid work every single day than men.</span> Turkey, Portugal and Mexico aren't far behind, while only the Nordics come close to sharing it evenly. And the penalty is double: those same women also get less time to rest. In Portugal and Italy, men enjoy almost an hour and a half more leisure every single day. Calling women strong and empowered doesn't erase those extra hours. This is the part of the day the economy never counts, the part that shapes millions of lives most, and it's long past time we talked about it as a society.</p>
  <div class="twinwrap">
    <div class="panel"><div class="tcap">&#127968; Unpaid work / day <span>women do more</span></div><div class="chartbox twin"><canvas id="genderChart"></canvas></div></div>
    <div class="panel"><div class="tcap">&#128715; Leisure / day <span>men get more</span></div><div class="chartbox twin"><canvas id="leisureChart"></canvas></div></div>
  </div>
</section>
</div></div>

<div class="wrap">

<section class="reveal" id="ch-tradeoff" data-nav="The trade-off">
  <div class="shead"><span class="chapno">06</span><span class="sh">The trade-off</span><span class="tchip">21:30 &middot; Evening</span></div>
  <h2>Work vs. <em>free time</em></h2>
  <p class="sub">Remember our five friends? Here's where each of them lands when we weigh a whole year of work against their daily free time. <span class="aha">The more a country works across the year, the less it plays each day.</span> Camille takes it slow, Sof&iacute;a barely catches a break, and the others fall somewhere in between. Same 24 hours, very different lives.</p>
  <div class="panel"><div class="chartbox"><canvas id="scatterChart"></canvas></div></div>
</section>

<section class="reveal" id="ch-retire" data-nav="Working until when">
  <div class="shead"><span class="chapno">07</span><span class="sh">A lifetime of days</span><span class="tchip">22:30</span></div>
  <h2>Working <em>until when?</em></h2>
  <p class="sub">Do you already know when you'll stop working? With day after day of work piling up over the years, at some point that question arrives. Every choice in your day leads to the moment you'll have to decide between two worlds. <span class="aha">Or the blend of both?</span> Across the world, that exit comes nearly twelve years apart: South Korea keeps going until 72, while Luxembourg and France stop at barely 60.</p>
  <div class="panel road-panel">
    <div class="rsigns">
      <div class="rsign left">&#8592; RETIRE<small>as early as 60</small></div>
      <div class="rsign right">WORK &#8594;<small>past 72</small></div>
    </div>
    <div class="rfield" id="retireField"></div>
    <div class="road" id="retireRoad"><div class="lane"></div></div>
  </div>
</section>

</div><!-- /wrap -->

<div class="act" id="ch-2050" data-nav="The day of 2050"><div class="inner">
<section class="reveal">
  <div class="shead"><span class="chapno">08</span><span class="sh">Predictive model</span><span class="tchip">23:00 &middot; Tomorrow</span></div>
  <h2>&#129302; The day of <em>2050</em></h2>
  <p class="sub">So what happens if the world grows richer? A simple model learns, from the link between income and time use across all 35 countries, how a nation's day shifts as it grows wealthier, then projects a country's 24-hour day into a more prosperous future. The good news: prosperity tends to hand back free time. The catch: it barely touches the second shift. <span class="aha">Pick a country and a growth scenario.</span> <b>Illustrative model</b>, not a time forecast; the data is a single snapshot, not a time series.</p>
  <div class="panel">
    <div class="predctrl">
      <label>Country <select id="predCountry"></select></label>
      <label>Economic growth by 2050: <b id="predGrowthLbl">+60%</b>
        <input type="range" id="predGrowth" min="0" max="150" step="5" value="60" aria-label="Projected economic growth by 2050"></label>
      <div class="predquick">
        <button data-g="25">Modest +25%</button>
        <button data-g="60">Strong +60%</button>
        <button data-g="120">Boom +120%</button>
      </div>
    </div>
    <div class="predkpis" id="predKpis"></div>
    <div class="chg" id="predChange"></div>
    <div class="chglegend">
      <span><i class="faint"></i>Today</span>
      <span><i></i>Projected 2050</span>
    </div>
    <div class="predtext" id="predText"></div>
  </div>
</section>
</div></div>

<div class="wrap tail">

<section class="reveal" id="ch-takeaway" data-nav="The takeaway">
  <div class="shead"><span class="chapno">09</span><span class="sh">The takeaway</span><span class="tchip">23:59 &middot; Day's end</span></div>
  <h2>At the end of the day, <em>how do you feel?</em></h2>
  <p class="sub" style="font-size:17px;max-width:70ch">When your day ends, is it a feeling of a job well done, or of pure exhaustion? Your gender, your culture, and the country you live in can tip that balance, for better or worse. A single day is such a short thing next to a whole life. For the life you want now, and the one you want later, have you ever stopped to think about what really matters? <b>How do you live your day?</b></p>
  <div class="poll" id="poll">
    <div class="pollq">When your day ends, how do you usually feel?</div>
    <button class="pollopt" data-k="acc"><span class="fill"></span><span class="lbl">&#128524; Accomplished</span><span class="pct"></span></button>
    <button class="pollopt" data-k="exh"><span class="fill"></span><span class="lbl">&#128558;&#8205;&#128168; Exhausted</span><span class="pct"></span></button>
    <button class="pollopt" data-k="both"><span class="fill"></span><span class="lbl">&#129335; A bit of both</span><span class="pct"></span></button>
    <button class="pollopt" data-k="busy"><span class="fill"></span><span class="lbl">&#8987; Too busy to notice</span><span class="pct"></span></button>
    <div class="pollnote">Tap to cast your vote. Results are tallied on this device.</div>
  </div>
</section>

<section class="reveal">
  <div class="shead"><span class="sh">Behind the scenes</span></div>
  <h2>How we used <em>AI</em></h2>
  <div class="ai">
    <ul>
      <li>Data discovery &amp; validation of the OECD / World Bank / OWID sources</li>
      <li>Exploratory analysis to surface the strongest, most objective findings (correlations &amp; rankings)</li>
      <li>Code generation for this reproducible dashboard (Python builder + Chart.js)</li>
      <li>Narrative drafting and accessibility review</li>
    </ul>
  </div>
</section>

<p class="note">
  <b>Sources:</b> OECD Time Use Database &middot; World Bank (GDP per capita, PPP) &middot; Our World in Data.
  All public &amp; free. <b>Method:</b> five activity categories sum to 24h; "personal care" includes sleep, meals
  and hygiene (not separable in this data); reference years vary by country. <b>Coverage:</b> 35 OECD/partner
  countries (no South American country available in the dataset). <b>Accessibility:</b> keyboard skip link,
  color legend with labels, live-updating quiz result. <b>VizCon 2026</b> &middot; "How the world lives, thrives, and connects".
</p>

</div><!-- /wrap -->
"""

# ══════════════════════════════════════════════════════════════════════════════
# JS
# ══════════════════════════════════════════════════════════════════════════════
JS = r"""
const D = __DATA__;
const CATS=['Personal care','Paid work','Unpaid work','Leisure','Other'];
const COL=['#4f5bd5','#e04b5f','#f08a24','#0fa598','#9aa5b8'];
const TX='#5a6285',TXD='#141a33',GRID='rgba(20,26,51,.08)';
const NTX='#a8afd2',NTXD='#eef1ff',NGRID='rgba(255,255,255,.10)';
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const hm=h=>`${Math.floor(h)}h${String(Math.round((h-Math.floor(h))*60)).padStart(2,'0')}`;
const personaISO=D.personas.map(p=>p.iso3);

/* ── Chart.js house style ── */
Chart.defaults.font.family='"Inter",system-ui,-apple-system,sans-serif';
Chart.defaults.font.size=12;
Chart.defaults.color=TX;
Chart.defaults.animation.duration=reduce?0:900;
Chart.defaults.animation.easing='easeOutQuart';
const TT=Chart.defaults.plugins.tooltip;
TT.backgroundColor='rgba(13,17,40,.95)';TT.padding=12;TT.cornerRadius=11;TT.boxPadding=6;
TT.borderColor='rgba(255,255,255,.15)';TT.borderWidth=1;TT.usePointStyle=true;
TT.titleFont={family:'"Inter",sans-serif',size:12.5,weight:'700'};
TT.bodyFont={family:'"Inter",sans-serif',size:12.5};

/* the 24h ring, now only the persona portraits. The tooltip is off: it drew
   inside the canvas, under the portrait, and got clipped by the 180px box.
   onHover feeds a caption below the ring instead. */
const ring=(data,cut='68%',onHover=null)=>({type:'doughnut',
  data:{labels:CATS,datasets:[{data,backgroundColor:COL,borderWidth:0,spacing:2,borderRadius:5,hoverOffset:9}]},
  options:{cutout:cut,onHover:onHover,
    plugins:{legend:{display:false},tooltip:{enabled:false}}}});

/* a day as a 24h bar. Plain HTML, no Chart.js: lighter, and it reads as the
   timeline a day actually is. Used where a fourth identical ring would have
   stopped meaning anything. */
const dayKey=()=>`<div class="dbkey">${CATS.map((c,i)=>
  `<span><i style="background:${COL[i]}"></i>${c}</span>`).join('')}</div>`;
const DB_IDLE='Hover a block for its hours';
function dayStrip(vals,o){
  o=o||{};
  const seg=vals.map((v,i)=>`<i style="width:${(v/24*100).toFixed(2)}%;background:${COL[i]}"
     data-c="${i}" data-v="${hm(v)}" data-p="${(v/24*100).toFixed(1)}"></i>`).join('');
  return `<div class="dbwrap">
    ${o.label?`<div class="dblab"><span>${o.label}</span>${o.right?`<b>${o.right}</b>`:''}</div>`:''}
    <div class="daybar24" role="img" aria-label="${o.label||'A 24 hour day'}: ${
      CATS.map((c,i)=>c+' '+hm(vals[i])).join(', ')}">${seg}</div>
    ${o.ticks?`<div class="dbticks"><span>0h</span><span>6h</span><span>12h</span><span>18h</span><span>24h</span></div>`:''}
    <div class="dbhov idle">${DB_IDLE}</div>
    ${o.key?dayKey():''}
  </div>`;
}
/* delegated, because the bars are rebuilt on every quiz match, country click and
   growth-slider move */
function dbCap(e,on){
  const seg=e.target.closest('.daybar24 i');if(!seg)return;
  const cap=seg.closest('.dbwrap').querySelector('.dbhov');if(!cap)return;
  if(!on){cap.className='dbhov idle';cap.textContent=DB_IDLE;return;}
  const i=+seg.dataset.c;
  cap.className='dbhov';
  cap.innerHTML=`<i style="background:${COL[i]}"></i>${CATS[i]}
    &middot; <b>${seg.dataset.v}</b> &middot; ${seg.dataset.p}% of the day`;
}
document.addEventListener('mouseover',e=>dbCap(e,true));
document.addEventListener('mouseout',e=>dbCap(e,false));

/* ── the sky: scroll is the passage of a day ──────────────────────────────────
   Seven keyframes across the page. Each carries a CSS gradient (always drawn)
   and an illustrated layer (drawn only when the artwork exists). The closing
   keyframe reuses the dawn artwork, so the day comes full circle.
   Artwork lives in assets/sky/ under these exact names:
     01-morning  02-midday  03-afternoon  04-golden
     05-sunset   06-dusk    07-night      08-midnight
     (.webp, 2752x1536, q80)   plus optional clouds-overlay.png (transparent).
   All of them must share the SAME composition and cloud positions — only the
   lighting changes — otherwise the crossfade ghosts. Measured edge-correlation
   between adjacent pairs: 0.89 0.85 0.87 0.76 0.87 0.85 0.92. The 0.76 link
   (golden -> sunset) is the weakest and the one to watch for ghosting; if it
   shows, tighten that segment by moving the sunset stop from 0.65 down to ~0.62
   so the 50/50 blend is on screen for less scroll distance.

   Stops are anchored to where each chapter actually sits in the scroll, so an
   image has fully arrived when its chapter is on screen. Re-measured after the
   chapters were reordered (topics moved from 4th to 2nd), which shifted every
   position below it:
     0.00 morning    hero + "five lives"        (07:00, chapter at 0.12)
     0.34 midday     "who does it most" + quiz  (09:00 / 11:00, at 0.27 / 0.36)
     0.47 afternoon  the globe                  (12:00, at 0.43)
     0.57 golden     "the double shift"         (20:00, at 0.53)
     0.66 sunset     "work vs. free time"       (21:30, at 0.65)
     0.74 dusk       "working until when"       (22:30, at 0.74)
     0.86 night      "the day of 2050"          (23:00, at 0.82)
     1.00 midnight   "the takeaway"             (23:59, at 0.97, the day ends)
   The story closes on deep night, matching its own closing line ("when your day
   ends..."). One single ink flip, to light at p=0.70, which falls between
   chapters 6 (0.65) and 7 (0.74) so nobody watches text change colour mid-read.
   Gradient stops are sampled from the artwork, so the no-image fallback tracks
   the same arc. */
const SKY=[
 {p:0.00,img:'01-morning',  dark:false,c:['#e1eae3','#e0ebe6','#cee6eb']},
 {p:0.34,img:'02-midday',   dark:false,c:['#a6d7df','#9fe2ee','#79e2fb']},
 {p:0.47,img:'03-afternoon',dark:false,c:['#b8c9c3','#d0d5bc','#eecf91']},
 {p:0.57,img:'04-golden',   dark:false,c:['#efaf7d','#dca686','#e8b578']},
 {p:0.66,img:'05-sunset',   dark:false,c:['#ac9d8d','#e6a26e','#e99a75']},
 {p:0.74,img:'06-dusk',     dark:true, c:['#4a4373','#75699c','#7b87b5']},
 {p:0.86,img:'07-night',    dark:true, c:['#36355f','#3e3b6b','#49286f']},
 {p:1.00,img:'08-midnight', dark:true, c:['#222544','#242c4e','#041031']}];
const SKY_DIR='assets/sky/',SKY_EXT='.webp';
const hx=s=>[1,3,5].map(i=>parseInt(s.substr(i,2),16));
const mix=(a,b,t)=>{const A=hx(a),B=hx(b);return `rgb(${A.map((v,i)=>Math.round(v+(B[i]-v)*t)).join(',')})`;};
const skyEl=document.getElementById('sky'),cloudsEl=document.getElementById('skyClouds'),
      dayBar=document.querySelector('.daybar');

/* Charts with axes sit on panels that change with the sky, so their labels have
   to follow the mood too. Register one here and it gets retinted on every flip. */
const themed=[];
function retint(ch,dark){
  if(!ch)return;
  const tx=dark?NTX:TX,txd=dark?NTXD:TXD,gr=dark?NGRID:GRID;
  const s=ch.options.scales||{},isBar=ch.config.type==='bar';
  Object.keys(s).forEach(k=>{
    const ax=s[k];if(!ax)return;
    if(ax.ticks)ax.ticks.color=(isBar&&k==='y')?txd:tx;   // category names stay strong
    if(ax.grid&&ax.grid.color!==undefined)ax.grid.color=gr;
    if(ax.border&&ax.border.color!==undefined)ax.border.color=gr;
    if(ax.title)ax.title.color=tx;
  });
  const lg=ch.options.plugins&&ch.options.plugins.legend;
  if(lg&&lg.labels)lg.labels.color=txd;
  ch.update('none');
}
function retintAll(dark){themed.forEach(c=>retint(c,dark));}
let mood=null,lastP=0;
function setMood(dark){
  if(mood===dark)return;
  mood=dark;document.documentElement.dataset.mood=dark?'dark':'light';
  retintAll(dark);
}

/* one fixed layer per keyframe; the lower one stays opaque while the next
   fades in over it, so the gradient never bleeds through mid-transition */
let skyLyrs=[];
function initSky(){
  skyLyrs=SKY.map(s=>{
    const d=document.createElement('div');d.className='lyr';
    d.style.backgroundImage=`url("${SKY_DIR}${s.img}${SKY_EXT}")`;
    skyEl.insertBefore(d,cloudsEl);return d;});
  const probe=new Image();
  probe.onload=()=>{skyEl.classList.add('has-img');paint(lastP);};
  probe.onerror=()=>{skyLyrs.forEach(d=>d.remove());skyLyrs=[];};  // no artwork yet: gradient carries it
  probe.src=SKY_DIR+SKY[0].img+SKY_EXT;
  const cl=new Image();
  cl.onload=()=>{cloudsEl.style.backgroundImage=`url("${SKY_DIR}clouds-overlay.png")`;
                 cloudsEl.style.opacity='.5';};
  cl.src=SKY_DIR+'clouds-overlay.png';
}

function paint(p){
  lastP=p;
  let i=0;while(i<SKY.length-2 && p>SKY[i+1].p) i++;
  const a=SKY[i],b=SKY[i+1];
  const t=Math.min(1,Math.max(0,(p-a.p)/(b.p-a.p))),rs=document.documentElement.style;
  a.c.forEach((c,k)=>rs.setProperty('--s'+k,mix(c,b.c[k],t)));
  skyLyrs.forEach((d,k)=>{
    const op=k<i?0:k===i?1:k===i+1?t:0;
    d.style.opacity=op;d.style.visibility=op>0?'visible':'hidden';});
  setMood(t<0.5?a.dark:b.dark);
}

/* ── chapter rail ── */
const chapters=[...document.querySelectorAll('[data-nav]')],rail=document.getElementById('rail');
chapters.forEach(s=>{
  const a=document.createElement('a');a.href='#'+s.id;
  a.innerHTML=`<span>${s.dataset.nav}</span>`;a.setAttribute('aria-label',s.dataset.nav);rail.appendChild(a);});
const dots=[...rail.children];
function railSync(){
  let idx=-1;
  chapters.forEach((s,i)=>{if(s.getBoundingClientRect().top<=window.innerHeight*0.45)idx=i;});
  dots.forEach((d,i)=>d.classList.toggle('on',i===idx));
}

function onScroll(){
  const max=(document.documentElement.scrollHeight-window.innerHeight)||1;
  const p=Math.min(1,Math.max(0,window.scrollY/max)),arc=Math.sin(p*Math.PI);
  paint(p);
  skyEl.style.setProperty('--drift',(p*44).toFixed(1)+'px');
  skyEl.style.setProperty('--cloudX',(-p*280).toFixed(0)+'px');
  skyEl.style.setProperty('--sunX',(8+p*80).toFixed(1)+'%');
  skyEl.style.setProperty('--sunY',(-16+arc*76).toFixed(1)+'%');
  skyEl.style.setProperty('--sunO',(0.34+arc*0.46).toFixed(2));
  skyEl.style.setProperty('--rayO',(0.06+arc*0.42).toFixed(2));
  dayBar.style.setProperty('--p',(p*100).toFixed(2)+'%');
  railSync();
}
initSky();
window.addEventListener('scroll',onScroll,{passive:true});
window.addEventListener('resize',onScroll);onScroll();

/* ── reveal on scroll ── */
const io=new IntersectionObserver(es=>es.forEach(e=>{
  if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));

/* ── hero stats count up when they come into view ── */
const cio=new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting)return;cio.unobserve(e.target);
  const el=e.target,t=+el.dataset.target;
  if(reduce){el.textContent=t.toLocaleString('en-US');return;}
  const dur=1400,st=performance.now();
  (function step(now){const p=Math.min(1,(now-st)/dur);
    el.textContent=Math.round(t*(1-Math.pow(1-p,3))).toLocaleString('en-US');
    if(p<1)requestAnimationFrame(step);})(st);}),{threshold:.6});
document.querySelectorAll('.stat .n').forEach(el=>cio.observe(el));

if(reduce){const r=document.querySelector('.heroclock svg');if(r&&r.pauseAnimations)r.pauseAnimations();}

/* ── end-of-day poll (tallied per device via localStorage) ── */
const POLL_KEY='tfhh_poll_v1',POLL_MINE='tfhh_poll_mine';
function pollData(){try{return JSON.parse(localStorage.getItem(POLL_KEY))||{};}catch(e){return {};}}
function renderPoll(show){
  const d=pollData(),total=Object.values(d).reduce((a,b)=>a+b,0),mine=localStorage.getItem(POLL_MINE);
  document.querySelectorAll('.pollopt').forEach(b=>{
    const k=b.dataset.k,v=d[k]||0,pct=total?Math.round(v/total*100):0;
    b.querySelector('.fill').style.width=(show?pct:0)+'%';
    b.querySelector('.pct').textContent=pct+'%';
    b.classList.toggle('mine',mine===k);});
  if(show)document.getElementById('poll').classList.add('voted');
}
document.querySelectorAll('.pollopt').forEach(b=>b.addEventListener('click',()=>{
  const poll=document.getElementById('poll');
  if(poll.classList.contains('voted'))return;
  const d=pollData(),k=b.dataset.k;d[k]=(d[k]||0)+1;
  localStorage.setItem(POLL_KEY,JSON.stringify(d));localStorage.setItem(POLL_MINE,k);
  renderPoll(true);}));
if(localStorage.getItem(POLL_MINE))renderPoll(true);

/* ── personas: the 24h ring becomes a halo around the portrait ── */
const grid=document.getElementById('personaGrid');
D.personas.forEach((p,i)=>{
  const el=document.createElement('button');el.className='pcard reveal';el.type='button';
  el.setAttribute('aria-label',`Open details about ${p.name} from ${p.continent}`);
  el.addEventListener('click',()=>openPersona(i));
  el.style.setProperty('--d',(i*0.09)+'s');
  el.innerHTML=`<div class="cont">${p.continent}</div>
    <div class="phalo">
      <canvas id="clk${i}"></canvas>
      <img class="avatar" src="${p.avatar}" loading="lazy"
           onerror="this.onerror=null;this.src='${p.avatarAlt}'"
           alt="Illustrated portrait of ${p.name} from ${p.continent}">
      <span class="hrs">24h</span>
    </div>
    <div class="phov idle" id="phov${i}">Hover the ring</div>
    <div class="pname">${p.name} <span class="pflag">${p.emoji}</span></div>
    <div class="sig">${p.sig}</div>
    <div class="bio">${p.bio}</div>
    <div class="pstats"><div><b>${p.ret.toFixed(0)}</b>Retires</div>
      <div><b>${Math.round(p.wh)}h</b>Work / yr</div></div>
    <div class="phint">Open their day &rarr;</div>`;
  grid.appendChild(el);io.observe(el);
  const cap=el.querySelector('#phov'+i),idle='Hover the ring';
  const setCap=n=>{
    if(n<0){cap.className='phov idle';cap.textContent=idle;return;}
    cap.className='phov';
    cap.innerHTML=`<i style="background:${COL[n]}"></i>${CATS[n]} &middot; ${hm(p.clock[n])}`;
  };
  const cv=document.getElementById('clk'+i);
  new Chart(cv,ring(p.clock,'70%',(ev,els)=>setCap(els.length?els[0].index:-1)));
  cv.addEventListener('mouseleave',()=>setCap(-1));   // onHover does not fire on leave
});

/* ── persona detail modal ──
   Opened from a card. Everything shown here is real data: the five categories,
   the country's supplementary metrics, and the delta against the 35-country
   average. The video slot degrades to a placeholder until the file exists. */
const pgrid=document.getElementById('personaGrid'),pdet=document.getElementById('personaDetail');
let openedFrom=null;
const A=D.avg;
function delta(v,ref,unit,invert){
  const d=v-ref;
  if(Math.abs(d)<(unit==='h'?0.09:0.5))return '<div class="d eq">on the average</div>';
  const better=invert?d<0:d>0;
  const txt=unit==='h'?`${d>0?'+':'-'}${Math.round(Math.abs(d)*60)} min`
                      :`${d>0?'+':'-'}${Math.abs(d).toFixed(unit==='y'?1:0)}${unit==='y'?' yrs':'h'}`;
  return `<div class="d ${better?'up':'dn'}">${txt} vs average</div>`;
}
function openPersona(i){
  const p=D.personas[i];
  openedFrom=pgrid.children[i]||null;
  // every .st block carries its place in the queue, so the panel assembles
  // one piece at a time instead of landing all at once
  // one helper builds class + style together: emitting two style attributes on the
  // same element silently drops the second one, which would kill the bar colours
  let k=0;
  const st=(cls,vars)=>`class="${cls?cls+' st':'st'}" style="--i:${k++}${vars?';'+vars:''}"`;
  // rows() and num() must be called from inside the template, never precomputed:
  // the queue index comes from call order, so precomputing would reveal the bars
  // before the header that introduces them
  const rows=()=>CATS.map((c,n)=>`<div ${st('pmbar','--bc:'+COL[n])}>
      <span class="nm">${c}</span><span class="vl">${hm(p.clock[n])}</span>
      <span class="tr"><i style="width:${(p.clock[n]/24*100).toFixed(1)}%"></i></span></div>`).join('');
  const num=(color,val,label,d)=>`<div ${st('pmnum')}>
      <div class="n"${color?` style="color:${color}"`:''}>${val}</div>
      <div class="l">${label}</div>${d||''}</div>`;
  const gapMin=Math.round((p.upwF-p.upwM)*60);
  pdet.innerHTML=`
    <button ${st('pdback')} type="button" id="pdback">&larr; Back to all five</button>
    <div ${st('pmhead')}>
      <img src="${p.avatar}" onerror="this.onerror=null;this.src='${p.avatarAlt}'"
           alt="Illustrated portrait of ${p.name}">
      <div>
        <div class="pmwho">${p.continent} &middot; ${p.country}</div>
        <h3 id="pdtitle">${p.name} ${p.emoji}</h3>
        <div class="pmsig">${p.sig}</div>
      </div>
    </div>
    <div ${st('panel')}><h4>In their own words</h4><div class="pmvid" id="pmvid"></div></div>
    <div class="pdcols">
      <div class="pdcol">
        <div ${st('panel')}><h4>Their story</h4><p class="pmbio">${p.bio}</p></div>
        <div ${st('panel')}><h4>One day, hour by hour</h4>${rows()}</div>
      </div>
      <div class="pdcol">
        <div ${st('panel')}><h4>Things you would not guess</h4>
          <ul class="pdtriv">${p.trivia.map(f=>`<li ${st()}>
            <span class="ic">${f.ic}</span><span>${f.t}</span></li>`).join('')}</ul></div>
      </div>
    </div>
    <div ${st('panel')}><h4>${p.country} vs the 35 countries</h4>
      <div class="pmnums">
        ${num(COL[1],hm(p.clock[1]),'Paid work / day',delta(p.clock[1],A.paw,'h',true))}
        ${num(COL[3],hm(p.clock[3]),'Leisure / day',delta(p.clock[3],A.lei,'h',false))}
        ${num(COL[2],hm(p.clock[2]),'Unpaid work / day',delta(p.clock[2],A.upw,'h',true))}
        ${num(COL[0],hm(p.clock[0]),'Personal care / day',delta(p.clock[0],A.pca,'h',false))}
        ${num('',Math.round(p.wh)+'h','Work per year',delta(p.wh,A.wh,'H',true))}
        ${num('',p.ret.toFixed(0),'Retires (men)',delta(p.ret,A.ret,'y',true))}
        ${num('',p.life.toFixed(1),'Life satisfaction /10','')}
        ${num('','$'+Math.round(p.gdp/1000)+'k','GDP/capita PPP','')}
      </div>
      ${gapMin>0?`<p ${st('pmnote')}>The second shift, at home: in ${p.country} women do about
        <b>${gapMin} minutes more unpaid work a day</b> than men
        (<b>${hm(p.upwF)}</b> against <b>${hm(p.upwM)}</b>).</p>`:``}
    </div>`;
  document.getElementById('pdback').addEventListener('click',closePersona);
  setupPersonaVideo(p);
  pgrid.classList.add('out');
  // wait for the grid to fade before the panel takes its place
  setTimeout(()=>{
    pgrid.hidden=true;pdet.hidden=false;
    // read a layout property to flush the opacity:0 start state, then flip the
    // class. Doing this in a rAF is unreliable when no frames are being produced.
    void pdet.offsetHeight;
    pdet.classList.add('go');
    pdet.focus({preventScroll:true});
    document.getElementById('ch-personas').scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'});
  },reduce?0:430);
}
function closePersona(){
  pdet.classList.remove('go');
  setTimeout(()=>{
    pdet.hidden=true;pdet.innerHTML='';
    pgrid.hidden=false;
    void pgrid.offsetHeight;
    pgrid.classList.remove('out');
    if(openedFrom)openedFrom.focus({preventScroll:true});
    document.getElementById('ch-personas').scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'});
  },reduce?0:280);
}
/* Esc closes the detail view, same reflex the modal had */
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!pdet.hidden)closePersona();});
/* the video is optional: if the file is not there yet, show a "coming soon" panel */
function setupPersonaVideo(p){
  const box=document.getElementById('pmvid');
  const soon=()=>{box.innerHTML=`<div class="pmvidsoon">
      <span class="ic">&#9654;</span><b>${p.name} tells you about her day</b>
      <span>Video coming soon. Drop the file at <code>${p.video}</code> and it appears here.</span>
    </div>`;};
  const v=document.createElement('video');
  v.controls=true;v.preload='metadata';v.playsInline=true;
  v.setAttribute('poster',p.videoPoster);
  v.addEventListener('error',soon,true);   // catches the <source> failing too
  const s=document.createElement('source');s.src=p.video;s.type='video/mp4';
  s.addEventListener('error',soon);
  v.appendChild(s);box.innerHTML='';box.appendChild(v);
}


/* ── quiz ── */
const ids=['pca','paw','upw','lei'];
function readQuiz(){const o={};ids.forEach(k=>o[k]=parseFloat(document.getElementById('q_'+k).value));return o;}
function updTotals(){
  const q=readQuiz();ids.forEach(k=>document.getElementById('v_'+k).textContent=hm(q[k]));
  const sum=q.pca+q.paw+q.upw+q.lei,oth=Math.max(0,24-sum);
  document.getElementById('qtotal').innerHTML=`Accounted: <b>${hm(Math.min(24,sum))}</b> &middot; Other/leftover: <b>${hm(oth)}</b>`
    +(sum>24?` &middot; <span class="aha">over 24h, we'll rescale</span>`:``);
}
ids.forEach(k=>document.getElementById('q_'+k).addEventListener('input',updTotals));
updTotals();
document.getElementById('qbtn').addEventListener('click',()=>{
  const q=readQuiz();let v=[q.pca,q.paw,q.upw,q.lei],sum=v.reduce((a,b)=>a+b,0);
  let oth=Math.max(0,24-sum);if(sum>24){const f=24/sum;v=v.map(x=>x*f);oth=0;}
  const user=[v[0],v[1],v[2],v[3],oth];let best=null,bd=1e9;
  D.countries.forEach(c=>{const cv=[c.pca,c.paw,c.upw,c.lei,c.oth];
    const d=Math.sqrt(cv.reduce((s,x,i)=>s+(x-user[i])**2,0));if(d<bd){bd=d;best=c;}});
  const pct=Math.max(80,Math.min(99,Math.round(100-bd*6)));
  document.getElementById('rflag').textContent=best.flag;
  document.getElementById('rname').textContent=`You matched with ${best.country}!`;
  document.getElementById('rpct').textContent=`${pct}% in sync`;
  document.getElementById('rdesc').innerHTML=`Paid work ${hm(best.paw)}/day &middot; leisure ${hm(best.lei)}/day &middot; retires at ${best.ret.toFixed(0)}.`;
  document.getElementById('qresult').classList.add('show');
  document.getElementById('qafter').style.display='block';
  // two bars instead of one ring: the point of a match is the comparison, and a
  // ring of the country alone never showed you what you asked for
  document.getElementById('qbars').innerHTML=
    dayStrip(user,{label:'Your ideal day',right:'24h'})+
    dayStrip([best.pca,best.paw,best.upw,best.lei,best.oth],
           {label:best.country+"'s real day",right:'24h',key:true});
});

/* ── topic picker: one ranking per slice of the day ──
   Artwork goes in assets/topics/<img>.webp (4:3). Until a file exists the
   card falls back to its gradient, so nothing looks broken. */
const TOPICS=[
  {k:'pca',img:'personal-care',col:COL[0],unit:'h',
   name:'Sleep &amp; self-care',
   what:'Sleeping, eating, washing, getting ready. Not pure sleep &mdash; the data does not separate it.',
   fb:'linear-gradient(150deg,#5a67d8,#8b5cf6)'},
  {k:'paw',img:'paid-work',col:COL[1],unit:'h',
   name:'Paid work',
   what:'Time on the job or studying, per day, averaged across the week.',
   fb:'linear-gradient(150deg,#e04b5f,#c2551a)'},
  // "Housework" reads better but the OECD category also covers caring for
  // children and elders, which is the half the double-shift chapter turns on.
  // "Home & care" keeps both without going dry.
  {k:'upw',img:'housework',col:COL[2],unit:'h',
   name:'Home &amp; care',
   what:'Cooking, cleaning, raising children, caring for elders. The shift no payslip counts.',
   fb:'linear-gradient(150deg,#f08a24,#e0459b)'},
  {k:'lei',img:'leisure',col:COL[3],unit:'h',
   name:'Leisure',
   what:'Everything you do because you want to: friends, sport, screens, doing nothing.',
   fb:'linear-gradient(150deg,#0fa598,#4f5bd5)'},
  {k:'oth',img:'getting-around',col:COL[4],unit:'h',
   name:'Getting around',
   what:'Commuting and everything the survey could not file anywhere else.',
   fb:'linear-gradient(150deg,#7b8398,#4a5170)'},
  // "The whole year" named a unit of time while the other five name an activity,
  // so it read as an odd one out. This names the thing and the timeframe, and the
  // point is telling it apart from the daily "Paid work" card.
  {k:'wh',img:'work-year',col:'#8b5cf6',unit:'H',
   name:'A year of work',
   what:'Not a day but a year: hours worked per worker, all twelve months of it.',
   fb:'linear-gradient(150deg,#8b5cf6,#e0459b)'},
];
const heat=t=>mix('#f0a824','#d61440',Math.max(0,Math.min(1,t)));
const fmt=(v,unit)=>unit==='h'?hm(v):Math.round(v)+'h/yr';
const tgrid=document.getElementById('topicGrid'),trank=document.getElementById('topicRank');
tgrid.innerHTML=TOPICS.map((t,i)=>`<button class="tcard" type="button" data-i="${i}"
   style="--img:url('assets/topics/${t.img}.webp');--fb:${t.fb}"
   aria-label="Ranking for ${t.name.replace(/&amp;/g,'and')}">
   <b>${t.name}</b></button>`).join('');

function showTopic(i){
  const t=TOPICS[i];
  [...tgrid.children].forEach((el,n)=>{
    el.classList.toggle('on',n===i);el.setAttribute('aria-pressed',n===i);});
  const sorted=[...D.countries].sort((a,b)=>b[t.k]-a[t.k]);
  const hi=sorted[0][t.k],lo=sorted[sorted.length-1][t.k],last=sorted[sorted.length-1];
  const top=sorted.slice(0,10);
  // size across the range of the ten actually shown, not of all 35: the top ten
  // bunch up near the maximum, so a global scale made every circle the same size
  const hi10=top[0][t.k],lo10=top[top.length-1][t.k];
  let k=0;const st=(cls,vars)=>`class="${cls?cls+' st':'st'}" style="--i:${k++}${vars?';'+vars:''}"`;
  const bubbles=top.map(c=>{
    const f=(c[t.k]-lo10)/((hi10-lo10)||1),dia=Math.round(72+f*84);
    return `<div ${st('bub','--ringc:'+heat(f))}>
      <div class="circ" style="width:${dia}px;height:${dia}px">
        <img src="assets/flags/${c.iso2}.png" alt="${c.country} flag" loading="lazy"></div>
      <div class="bnm">${c.country}</div>
      <div class="bvl">${fmt(c[t.k],t.unit)}</div></div>`;}).join('');
  trank.classList.remove('go');
  trank.innerHTML=`
    <div ${st('trankcap')}><h3>${t.name}</h3><span>${t.what}</span></div>
    <div ${st('panel')}><div class="bubbles">${bubbles}</div>
      <p class="tnote">Top ten of 35, biggest circle first. At the other end sits
        <b>${last.country}</b> with <b>${fmt(lo,t.unit)}</b> &mdash;
        <b>${t.unit==='h'?hm(hi-lo):Math.round(hi-lo)+'h'}</b> less than
        ${sorted[0].country}.${t.k==='paw'?` And here is the surprise: this ranking flips the
        usual assumption. The countries at the top are not the richest ones &mdash; wealth is
        what lets a nation ease off the clock.`:''}${t.k==='wh'?` Stretched over a year the
        gap stops being abstract: that is nearly <b>${Math.round((hi-lo)/8)} working days</b>
        of difference between the top and the bottom of this list.`:''}</p>
    </div>`;
  void trank.offsetHeight;trank.classList.add('go');
}
tgrid.addEventListener('click',e=>{
  const b=e.target.closest('.tcard');if(!b)return;
  showTopic(+b.dataset.i);
  // the ranking lands below the cards; nudge it into view without a jump
  requestAnimationFrame(()=>trank.scrollIntoView({behavior:reduce?'auto':'smooth',block:'nearest'}));
});
// nothing is selected up front: the ranking only appears once a card is clicked

/* ── the double shift: twin charts (retinted with the sky) ── */
const g=D.gender;
const hBars=title=>({indexAxis:'y',responsive:true,maintainAspectRatio:false,
  plugins:{legend:{labels:{color:TXD,usePointStyle:true,pointStyle:'circle',boxWidth:8,padding:16}},
    tooltip:{callbacks:{label:c=>` ${c.dataset.label}: ${hm(c.parsed.x)}`}}},
  scales:{x:{ticks:{color:TX,callback:v=>v+'h'},grid:{color:GRID},border:{color:GRID},
      title:{display:true,text:title,color:TX,font:{size:11.5,weight:'600'}}},
    y:{ticks:{color:TXD,font:{weight:'500'}},grid:{display:false},border:{display:false}}}});
const barSet=(label,data,color)=>({label,data,backgroundColor:color,borderRadius:5,
  barPercentage:.82,categoryPercentage:.74});
themed.push(new Chart(document.getElementById('genderChart'),{type:'bar',
  data:{labels:g.map(x=>x.country),datasets:[
    barSet('Women',g.map(x=>x.f),'#e0459b'),barSet('Men',g.map(x=>x.m),'#6b78e8')]},
  options:hBars('Unpaid work per day')}));
themed.push(new Chart(document.getElementById('leisureChart'),{type:'bar',
  data:{labels:g.map(x=>x.country),datasets:[
    barSet('Women',g.map(x=>x.leiF),'#e0459b'),barSet('Men',g.map(x=>x.leiM),'#6b78e8')]},
  options:hBars('Leisure per day')}));
retintAll(mood);

/* ── work vs free time ── */
const pts=D.countries.map(c=>({x:c.wh,y:c.lei,c:c.country,iso:c.iso3}));
themed.push(new Chart(document.getElementById('scatterChart'),{type:'scatter',
  data:{datasets:[
    {label:'Countries',data:pts.filter(p=>!personaISO.includes(p.iso)),
      backgroundColor:'rgba(79,91,213,.42)',borderColor:'rgba(79,91,213,.85)',borderWidth:1.5,
      pointRadius:7,pointHoverRadius:10},
    {label:'Our five humans',data:pts.filter(p=>personaISO.includes(p.iso)),
      backgroundColor:'#f08a24',borderColor:'#fff',borderWidth:2,
      pointRadius:11,pointHoverRadius:14,pointStyle:'triangle'}]},
  options:{plugins:{legend:{labels:{color:TXD,usePointStyle:true,boxWidth:9,padding:16}},
    tooltip:{callbacks:{label:c=>` ${c.raw.c}: ${Math.round(c.raw.x)}h/yr, ${hm(c.raw.y)} leisure`}}},
    scales:{x:{ticks:{color:TX},grid:{color:GRID},border:{color:GRID},
        title:{display:true,text:'Hours worked per year',color:TX,font:{size:11.5,weight:'600'}}},
      y:{ticks:{color:TX,callback:v=>v+'h'},grid:{color:GRID},border:{color:GRID},
        title:{display:true,text:'Leisure per day',color:TX,font:{size:11.5,weight:'600'}}}}}}));
retintAll(mood);   // the trade-off chapter can already be in night mood

/* ── retirement road (re-laid out on resize) ── */
const rMIN=59.5,rMAX=73,rSize=46;
const rField=document.getElementById('retireField'),rRoad=document.getElementById('retireRoad');
function drawRoad(){
  rField.innerHTML='';rRoad.querySelectorAll('.rtick').forEach(t=>t.remove());
  const rW=rField.clientWidth||900,lanes=[];
  const xp=a=>((a-rMIN)/(rMAX-rMIN))*(rW-rSize)+rSize/2;
  [...D.countries].sort((a,b)=>a.ret-b.ret).forEach(c=>{
    const x=xp(c.ret);let lane=0;
    while(lanes[lane]!==undefined && x-lanes[lane]<rSize*0.86) lane++;
    lanes[lane]=x;
    const el=document.createElement('div');
    el.className='rmk'+(personaISO.includes(c.iso3)?' p':'');
    el.style.left=x+'px';el.style.bottom=(lane*46)+'px';
    el.title=c.country+' — retires at '+c.ret.toFixed(1);
    el.innerHTML=`<img src="assets/flags/${c.iso2}.png" alt="${c.country} flag" loading="lazy">`;
    rField.appendChild(el);});
  for(let a=60;a<=72;a+=2){
    const t=document.createElement('div');t.className='rtick';t.style.left=xp(a)+'px';t.textContent=a;rRoad.appendChild(t);}
}
drawRoad();
let rT;window.addEventListener('resize',()=>{clearTimeout(rT);rT=setTimeout(drawRoad,180);});
"""

JS_2 = r"""
/* ── predictive: the day of 2050 ── */
const M=D.model,selC=document.getElementById('predCountry');
D.countries.slice().sort((a,b)=>a.country.localeCompare(b.country)).forEach(c=>{
  const o=document.createElement('option');o.value=c.iso3;o.textContent=`${c.flag} ${c.country}`;selC.appendChild(o);});
selC.value='MEX';
const findC=iso=>D.countries.find(c=>c.iso3===iso);
function project(c,growth){
  // convergence: the country moves toward what the income trend predicts for its
  // NEW GDP level; the share of convergence grows with the growth scenario.
  const conv=Math.min(1,growth/100),ng=Math.log(c.gdp*(1+growth/100)),tgt=m=>m.a+m.b*ng;
  const paw=Math.max(0,c.paw+(tgt(M.paw_h)-c.paw)*conv);
  const lei=Math.max(0,c.lei+(tgt(M.lei_h)-c.lei)*conv);
  const upw=Math.max(0,c.upw+(tgt(M.upw_h)-c.upw)*conv);
  const v=[c.pca,paw,upw,lei,c.oth],s=v.reduce((a,b)=>a+b,0);
  return v.map(x=>x*24/s);
}
/* per-category change: translucent bar is today, solid is the projection, and
   the tail sticking out is the gain or loss. Two rings made you eyeball it. */
function drawChange(now,fut){
  const span=Math.max(...now,...fut)*1.08;
  document.getElementById('predChange').innerHTML=CATS.map((c,i)=>{
    const d=Math.round((fut[i]-now[i])*60),sg=d>0?'+':'';
    const cls=Math.abs(d)<1?'eq':(d>0?'up':'dn');
    return `<div class="chgrow" style="--bc:${COL[i]}">
      <span class="nm">${c}</span>
      <span class="chgtrack">
        <i class="now" style="width:${(now[i]/span*100).toFixed(1)}%"></i>
        <i class="fut" style="width:${(fut[i]/span*100).toFixed(1)}%"></i>
      </span>
      <span class="chgval"><b>${hm(fut[i])}</b>
        <span class="${cls}">${cls==='eq'?'no change':sg+d+' min'}</span></span>
    </div>`;}).join('');
}
function renderPred(){
  const c=findC(selC.value),gv=parseInt(document.getElementById('predGrowth').value);
  document.getElementById('predGrowthLbl').textContent='+'+gv+'%';
  const now=[c.pca,c.paw,c.upw,c.lei,c.oth],fut=project(c,gv);
  drawChange(now,fut);
  const dLei=Math.round((fut[3]-c.lei)*60),dPaw=Math.round((fut[1]-c.paw)*60),sg=v=>(v>=0?'+':'')+v;
  document.getElementById('predKpis').innerHTML=`
    <div class="k"><div class="n" style="color:#2fd3bd">${hm(fut[3])}</div><div class="l">Leisure/day (${sg(dLei)} min)</div></div>
    <div class="k"><div class="n" style="color:#ff7f8f">${hm(fut[1])}</div><div class="l">Paid work/day (${sg(dPaw)} min)</div></div>
    <div class="k"><div class="n" style="color:#8fa0ff">$${Math.round(c.gdp*(1+gv/100)/1000)}k</div><div class="l">Projected GDP/capita (PPP)</div></div>
    <div class="k"><div class="n" style="color:#ffb45c">+${gv}%</div><div class="l">Growth scenario</div></div>`;
  const yearH=Math.round(Math.abs(dLei)*365/60);
  const avgLei=D.countries.reduce((s,x)=>s+x.lei,0)/D.countries.length;
  const restPos=c.lei>=avgLei?`already one of the more rested nations`:`below the 35-country average for free time`;
  let up;
  if(gv<=0){
    up=`Today ${c.country} enjoys <b>${hm(c.lei)}</b> of leisure a day (${restPos}). Slide the growth up to see how prosperity could reshape the day.`;
  }else if(dLei>=1){
    up=`From <b>${hm(c.lei)}</b> today, leisure climbs <b>+${dLei} min/day</b> (~${yearH}h a year) as paid work eases by <b>${Math.abs(dPaw)} min</b>, and ${c.country} drifts toward the rhythm of wealthier nations.`;
  }else if(dLei<=-1){
    up=`${c.country} already rests <b>${hm(c.lei)}</b> a day, more than its income alone would predict. Growth won't add free time here; that leisure springs from other forces, not wealth.`;
  }else{
    up=`${c.country} already sits right where its income predicts (<b>${hm(c.lei)}</b> of leisure), so growth alone barely shifts the day.`;
  }
  const gapMin=Math.round((c.upwF-c.upwM)*60);
  const genderLine=gapMin>0
    ? `In ${c.country}, women already do about <b>${gapMin} min more unpaid work a day</b> than men, and income barely moves that gap in our data.`
    : `Even where the gender gap is small, income alone doesn't close it in our data.`;
  const catchTxt=`${genderLine} <b>Prosperity won't split the second shift</b>: that needs policy, not just a bigger economy. And this is a <b>pattern, not a promise</b>: freed-up hours can quietly become screen time, and shorter workdays usually take deliberate choices (4-day weeks, paid leave).`;
  document.getElementById('predText').innerHTML=`
    <div class="ptcard up"><h4>&#127793; The bright side</h4><p>${up}</p></div>
    <div class="ptcard catch"><h4>&#9888;&#65039; The catch</h4><p>${catchTxt}</p></div>`;
}
selC.addEventListener('change',renderPred);
document.getElementById('predGrowth').addEventListener('input',renderPred);
document.querySelectorAll('.predquick button').forEach(b=>b.addEventListener('click',()=>{
  document.getElementById('predGrowth').value=b.dataset.g;renderPred();}));
renderPred();

/* ── interactive globe ── */
const whs=D.countries.map(c=>c.wh),whMin=Math.min(...whs),whMax=Math.max(...whs);
const whColor=v=>{const t=Math.max(0,Math.min(1,(v-whMin)/(whMax-whMin)));
  const a=[255,214,10],b=[214,20,64];
  return `rgb(${a.map((x,i)=>Math.round(x+(b[i]-x)*t)).join(',')})`;};

function selectCountry(c){
  const p=document.getElementById('mapPanel');
  p.innerHTML=`<div class="mpflag">${c.flag}</div><div class="mpname">${c.country}</div>
    ${dayStrip([c.pca,c.paw,c.upw,c.lei,c.oth],{label:'Their 24 hours',ticks:true})}
    <div class="mpstats">
      <div><span>Paid work</span><b>${hm(c.paw)}/day</b></div>
      <div><span>Unpaid work</span><b>${hm(c.upw)}/day</b></div>
      <div><span>Leisure</span><b>${hm(c.lei)}/day</b></div>
      <div><span>Personal care</span><b>${hm(c.pca)}/day</b></div>
      <div><span>Work per year</span><b>${Math.round(c.wh)}h</b></div>
      <div><span>Retires (men)</span><b>${c.ret.toFixed(0)} yrs</b></div>
    </div>`;
}
const gEl=document.getElementById('globe');
if(typeof Globe==='undefined'){
  gEl.innerHTML='<div style="color:#a8afd2;padding:30px;text-align:center">Globe library failed to load. Check that assets/lib/globe.gl.min.js exists.</div>';
}else{
  const globe=Globe()(gEl)
    .globeImageUrl('assets/img/earth-day.jpg')
    .backgroundColor('rgba(0,0,0,0)')
    .showAtmosphere(true).atmosphereColor('#9fc6ff').atmosphereAltitude(0.26)
    .pointsData(D.countries).pointLat('lat').pointLng('lng')
    .pointColor(d=>whColor(d.wh)).pointAltitude(0.014).pointRadius(0.92)
    .pointResolution(28)
    .pointLabel(d=>`${d.flag} ${d.country} · ${Math.round(d.wh)}h/yr`)
    .onPointClick(d=>selectCountry(d))
    .onPointHover(d=>{gEl.style.cursor=d?'pointer':'default';});
  try{globe.scene().children.filter(o=>o.isLight).forEach(l=>l.intensity*=1.45);}catch(e){}
  const sizeGlobe=()=>globe.width(gEl.clientWidth).height(gEl.clientHeight);
  requestAnimationFrame(sizeGlobe);window.addEventListener('resize',sizeGlobe);
  globe.pointOfView({lat:15,lng:-20,altitude:2.35});
  const ctr=globe.controls();ctr.autoRotate=!reduce;ctr.autoRotateSpeed=0.62;ctr.enableZoom=true;
}
"""

# ══════════════════════════════════════════════════════════════════════════════
# assemble
# ══════════════════════════════════════════════════════════════════════════════
HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 24-Hour Human · VizCon 2026</title>
<meta name="description" content="How the world spends the same 1,440 minutes a day. An interactive time-use story across 35 countries.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..700&family=Inter:wght@300..800&display=swap">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="assets/lib/globe.gl.min.js"></script>
<style>{CSS}{CSS_TYPE}{CSS_VIZ}</style>
</head>
<body>
{BODY}
<script>
{JS}
{JS_2}
</script>
</body>
</html>
"""

def check_assets(html):
    """Avisa sobre imagem/vídeo referenciado que não existe na pasta.

    Todo asset aqui tem fallback (gradiente no card, gradiente no céu, SVG antigo
    no avatar, placeholder no vídeo). Isso é bom em produção e ruim no
    desenvolvimento: um arquivo renomeado simplesmente não aparece, sem erro
    nenhum. Este check torna a falta visível na hora do build.
    """
    import re as _re
    missing = []
    for name in _re.findall(r"img:'([\w-]+)'", html):
        if not any((ROOT / "assets" / d / f"{name}.webp").exists() for d in ("sky", "topics")):
            missing.append(f"assets/{{sky,topics}}/{name}.webp")
    for p in personas:
        iso = p["iso3"].lower()
        if not (ROOT / "assets" / "avatars" / f"{iso}.webp").exists():
            missing.append(f"assets/avatars/{iso}.webp (cai no .svg antigo)")
        if not (ROOT / p["video"]).exists():
            missing.append(f"{p['video']} (mostra placeholder)")
        elif not (ROOT / p["videoPoster"]).exists():
            missing.append(f"{p['videoPoster']} (video sem thumbnail)")
    if missing:
        print(f"AVISO: {len(missing)} asset(s) ausente(s), usando fallback:")
        for m in missing:
            print(f"   - {m}")


FINAL = HTML.replace("__GRAIN__", GRAIN).replace("__TICKS__", CLOCK_TICKS).replace("__DATA__", DATA)
check_assets(FINAL)
OUT.write_text(FINAL, encoding="utf-8")
print(f"OK -> {OUT}  ({len(countries)} countries, {len(gender)} gender bars, {len(personas)} personas)")
