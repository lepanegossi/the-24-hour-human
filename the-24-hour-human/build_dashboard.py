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
cp_by = {r["iso3"]: r for r in cp}
personas = []
for iso, name, cont, sig, bio in PERS:
    r = cp_by[iso]
    personas.append({
        "iso3": iso, "name": name, "emoji": flag(iso), "continent": cont, "sig": sig, "bio": bio,
        "avatar": f"assets/avatars/{iso.lower()}.svg",
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

DATA = json.dumps({"countries": countries, "gender": gender, "personas": personas, "model": model})

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The 24-Hour Human · VizCon 2026</title>
<meta name="description" content="How the world spends the same 1,440 minutes a day. An interactive time-use story across 35 countries.">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="assets/lib/globe.gl.min.js"></script>
<style>
:root{--pca:#5a67d8;--paw:#e05265;--upw:#ed8936;--lei:#9b5de5;--oth:#a0aec0;
 --ink:#1e2749;--muted:#5a6285;--card:#ffffff;--line:#e6e9f2;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Segoe UI',system-ui,sans-serif;color:var(--ink);line-height:1.55;
 background:linear-gradient(180deg,#e7f1ff 0%,#f4f0ea 55%,#fdeadd 100%);
 background-attachment:fixed;}
.skip{position:absolute;left:-999px;top:0;background:#ed8936;color:#fff;padding:10px 16px;border-radius:0 0 8px 0;z-index:99;}
.skip:focus{left:0;}
.wrap{max-width:1200px;margin:0 auto;padding:40px 20px 80px;position:relative;z-index:1;}
/* sol nascendo conforme o scroll */
.sunfx{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden;}
.sunfx .glow{position:absolute;right:0;bottom:var(--sunY,-14%);width:520px;height:520px;
 transform:translate(30%,50%);border-radius:50%;filter:blur(4px);opacity:var(--sunO,.5);
 background:radial-gradient(circle,rgba(255,214,10,.85),rgba(255,150,30,.45) 42%,transparent 70%);}
.sunfx .rays{position:absolute;right:0;bottom:var(--sunY,-14%);width:2000px;height:2000px;
 transform:translate(30%,50%);opacity:var(--rayO,.12);}
.sunfx .rays i{display:block;width:100%;height:100%;border-radius:50%;
 background:repeating-conic-gradient(from 0deg,rgba(255,196,110,.13) 0 3deg,transparent 3deg 15deg);
 animation:sunspin 170s linear infinite;}
@keyframes sunspin{to{transform:rotate(360deg)}}
@media(prefers-reduced-motion:reduce){.sunfx .rays i{animation:none;}}
.hero{text-align:center;padding:44px 0 20px;}
.hero h1{font-size:58px;font-weight:800;letter-spacing:-1.5px;
 background:linear-gradient(90deg,#5a67d8,#9b5de5,#ed8936);-webkit-background-clip:text;
 -webkit-text-fill-color:transparent;background-clip:text;}
.hero .lead{font-size:19px;color:var(--muted);max-width:760px;margin:14px auto 0;font-style:italic;}
.kicker{font-size:12px;letter-spacing:3px;text-transform:uppercase;color:#c96a1b;font-weight:700;margin-bottom:8px;}
.clock{width:114px;height:114px;display:block;margin:0 auto 12px;filter:drop-shadow(0 6px 14px rgba(30,39,73,.18));}
.kpis{display:flex;gap:18px;justify-content:center;flex-wrap:wrap;margin:34px 0 10px;}
.kpi{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--ac,#5a67d8);border-radius:16px;
 padding:20px 28px;min-width:168px;box-shadow:0 6px 20px rgba(30,39,73,.06);transition:transform .2s,box-shadow .2s;}
.kpi:hover{transform:translateY(-4px);box-shadow:0 14px 30px rgba(30,39,73,.13);}
.kpi .ki{width:26px;height:26px;stroke:var(--ac,#5a67d8);fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;margin-bottom:6px;}
.kpi .n{font-size:40px;font-weight:800;color:var(--ac,#5a67d8);font-variant-numeric:tabular-nums;line-height:1;}
.kpi .l{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-top:6px;}
section{margin-top:56px;}
.reveal{opacity:0;transform:translateY(26px);transition:opacity .7s ease,transform .7s ease;}
.reveal.in{opacity:1;transform:none;}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none;}}
.sh{font-size:13px;letter-spacing:3px;text-transform:uppercase;color:#9aa0c0;}
h2{font-size:30px;font-weight:800;margin:4px 0 6px;}
.sub{color:var(--muted);font-size:15px;margin-bottom:22px;max-width:820px;}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:10px 0 24px;}
.legend span{display:flex;align-items:center;gap:7px;font-size:13px;color:var(--muted);}
.dot{width:12px;height:12px;border-radius:3px;display:inline-block;}
/* quiz */
.quiz{background:linear-gradient(135deg,#eef1ff,#fff4ea);
 border:1px solid var(--line);border-radius:22px;padding:30px;box-shadow:0 8px 26px rgba(30,39,73,.07);}
.qrow{display:flex;align-items:center;gap:16px;margin:14px 0;flex-wrap:wrap;}
.qrow label{flex:1 1 220px;font-size:15px;color:var(--ink);}
.qrow input[type=range]{flex:2 1 300px;accent-color:#9b5de5;}
.qval{width:64px;text-align:right;font-weight:700;font-variant-numeric:tabular-nums;color:#5a67d8;}
.qbtn{margin-top:16px;background:linear-gradient(90deg,#fd297b,#ff655b);color:#fff;border:0;border-radius:24px;
 padding:13px 28px;font-size:16px;font-weight:700;cursor:pointer;box-shadow:0 6px 18px rgba(253,41,123,.3);}
.qbtn:hover{filter:brightness(1.06);transform:translateY(-1px);}
.qtotal{font-size:13px;color:var(--muted);margin-top:6px;}
.qresult{display:none;margin-top:24px;}
.qresult.show{display:block;animation:matchpop .5s cubic-bezier(.2,.8,.3,1.25);}
@keyframes matchpop{0%{opacity:0;transform:scale(.92)}100%{opacity:1;transform:none}}
.matchbanner{background:linear-gradient(90deg,#fd297b,#ff655b);color:#fff;font-size:22px;font-weight:800;
 text-align:center;padding:14px;border-radius:16px 16px 0 0;letter-spacing:.5px;}
.matchbanner .hearts{display:inline-block;animation:beat 1s ease-in-out infinite;}
@keyframes beat{0%,100%{transform:scale(1)}50%{transform:scale(1.28)}}
.matchbody{display:flex;align-items:center;gap:24px;flex-wrap:wrap;background:#fff;border:1px solid var(--line);
 border-top:0;border-radius:0 0 16px 16px;padding:24px;box-shadow:0 12px 34px rgba(253,41,123,.16);}
.matchface{font-size:64px;line-height:1;width:104px;height:104px;flex:0 0 auto;display:flex;align-items:center;justify-content:center;
 border-radius:50%;border:4px solid transparent;background:linear-gradient(#fff,#fff) padding-box,linear-gradient(135deg,#fd297b,#ff655b) border-box;
 box-shadow:0 6px 18px rgba(253,41,123,.25);}
.matchinfo{flex:1 1 220px;}
.matchinfo h3{font-size:23px;color:var(--ink);margin-bottom:6px;}
.matchpct{display:inline-block;background:linear-gradient(90deg,#fd297b,#ff655b);color:#fff;font-weight:700;
 font-size:13px;padding:4px 12px;border-radius:20px;margin-bottom:10px;}
.matchinfo p{color:var(--muted);font-size:13.5px;}
.qclock{position:relative;width:150px;height:150px;flex:0 0 auto;}
.qafter{display:none;margin-top:16px;color:var(--muted);font-style:italic;font-size:14px;line-height:1.55;}
@media(prefers-reduced-motion:reduce){.qresult.show{animation:none;}.matchbanner .hearts{animation:none;}}
/* personas */
.pgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:18px;}
.pcard{background:var(--card);border:1px solid var(--line);border-radius:18px;
 padding:20px;text-align:center;box-shadow:0 6px 20px rgba(30,39,73,.06);transition:transform .2s,box-shadow .2s;}
.pcard:hover{transform:translateY(-5px);box-shadow:0 14px 30px rgba(30,39,73,.13);}
.cont{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#9aa0c0;}
.avatar{width:96px;height:96px;border-radius:50%;margin:8px auto 6px;display:block;
 border:3px solid #fff;box-shadow:0 4px 14px rgba(30,39,73,.15);background:#eef1ff;}
.pname{font-size:19px;font-weight:700;}
.pflag{font-size:16px;}
.sig{color:#c96a1b;font-size:13px;font-weight:700;margin:6px 0 6px;}
.bio{color:var(--muted);font-size:12px;line-height:1.5;margin-bottom:12px;min-height:112px;}
.clockbox{position:relative;height:170px;}
.clabel{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;pointer-events:none;}
.clabel .b{font-size:20px;font-weight:800;color:var(--ink);}.clabel .s{font-size:10px;color:var(--muted);}
.pstats{display:flex;justify-content:space-around;font-size:11px;color:var(--muted);margin-top:8px;}
.pstats b{color:var(--ink);font-size:13px;display:block;}
.panel{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:0 6px 20px rgba(30,39,73,.06);}
.bubbles{display:flex;flex-wrap:wrap;gap:26px;align-items:flex-end;justify-content:center;padding:12px 0;}
.bub{text-align:center;}
.bub .circ{border-radius:50%;overflow:hidden;border:3px solid #fff;box-shadow:0 6px 18px rgba(30,39,73,.2);margin:0 auto 8px;background:#eef1ff;}
.bub .circ img{width:100%;height:100%;object-fit:cover;display:block;}
.bub .bnm{font-size:13px;font-weight:700;color:var(--ink);}
.bub .bvl{font-size:12px;color:#e05265;font-weight:700;}
/* Screen 3 road */
.road-panel{overflow:hidden;}
.rsigns{position:relative;height:70px;}
.rsign{position:absolute;top:0;background:#2f8f4e;border:2px solid #fff;border-radius:10px;color:#fff;padding:10px 16px;
 font-weight:800;letter-spacing:1px;box-shadow:0 5px 12px rgba(0,0,0,.22);outline:3px solid #2f8f4e;outline-offset:3px;font-size:17px;}
.rsign small{display:block;font-size:11px;font-weight:600;opacity:.9;letter-spacing:0;}
.rsign.left{left:2px;}.rsign.right{right:2px;text-align:right;}
.rfield{position:relative;width:100%;height:340px;}
.rmk{position:absolute;transform:translateX(-50%);transition:transform .15s;cursor:default;}
.rmk:hover{transform:translateX(-50%) scale(1.3);z-index:5;}
.rmk img{width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #fff;box-shadow:0 3px 9px rgba(30,39,73,.3);background:#eef1ff;display:block;}
.rmk.p img{border-color:#ffcf33;border-width:3px;}
.road{position:relative;height:54px;background:#3a4250;border-radius:6px;margin-top:2px;}
.road .lane{position:absolute;top:50%;left:2%;right:2%;height:4px;transform:translateY(-50%);
 background:repeating-linear-gradient(90deg,#ffd83b 0 26px,transparent 26px 52px);}
.rtick{position:absolute;transform:translateX(-50%);top:16px;font-size:12px;color:#fff;font-weight:700;}
.chartbox{position:relative;height:440px;}
.chartbox.tall{height:560px;}
.chartbox.twin{height:420px;}
.mapwrap{display:flex;gap:20px;flex-wrap:wrap;}
#globe{flex:2 1 520px;height:500px;border-radius:18px;overflow:hidden;display:flex;align-items:center;justify-content:center;
 background:radial-gradient(circle at 50% 40%,#eaf3ff,#dbe8fb);border:1px solid var(--line);box-shadow:0 6px 20px rgba(30,39,73,.06);}
.mappanel{flex:1 1 260px;background:var(--card);border:1px solid var(--line);border-radius:18px;
 padding:22px;box-shadow:0 6px 20px rgba(30,39,73,.06);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;}
.mappanel .hint{color:var(--muted);font-size:14px;}
.mpflag{font-size:44px;}.mpname{font-size:20px;font-weight:700;margin-top:4px;}
.mpclock{position:relative;width:170px;height:170px;margin:10px 0;}
.mpstats{width:100%;font-size:13px;color:var(--muted);}
.mpstats div{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed var(--line);}
.mpstats b{color:var(--ink);}
.maplegend{display:flex;align-items:center;gap:10px;font-size:12px;color:var(--muted);margin-top:12px;}
.maplegend .bar{height:10px;width:160px;border-radius:5px;background:linear-gradient(90deg,#ffd60a,#ff8c1a,#d61440);}
.predctrl{display:flex;gap:26px;flex-wrap:wrap;align-items:center;margin-bottom:18px;}
.predctrl label{font-size:14px;color:var(--ink);display:flex;gap:8px;align-items:center;flex-wrap:wrap;}
.predctrl select{padding:7px 10px;border-radius:8px;border:1px solid var(--line);font-size:14px;background:#fff;color:var(--ink);}
.predctrl input[type=range]{accent-color:#9b5de5;min-width:220px;}
.predquick{display:flex;gap:8px;flex-wrap:wrap;}
.predquick button{background:#eef1ff;border:1px solid #d7dcf5;border-radius:20px;padding:7px 14px;cursor:pointer;font-size:13px;color:#5a67d8;font-weight:600;}
.predquick button:hover{background:#e0e6ff;}
.predkpis{display:flex;gap:14px;flex-wrap:wrap;margin:6px 0 22px;}
.predkpis .k{flex:1 1 160px;background:#f7f9ff;border:1px solid var(--line);border-radius:14px;padding:16px;text-align:center;}
.predkpis .k .n{font-size:26px;font-weight:800;}
.predkpis .k .l{font-size:12px;color:var(--muted);margin-top:3px;}
.predclocks{display:flex;align-items:center;justify-content:center;gap:26px;flex-wrap:wrap;}
.clockbox2{position:relative;width:200px;height:200px;}
.clab{text-align:center;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;}
.predclocks .arrow{font-size:34px;color:#9b5de5;}
.predtext{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px;}
.ptcard{border-radius:14px;padding:18px 20px;}
.ptcard h4{font-size:15px;margin-bottom:6px;}
.ptcard p{font-size:13.5px;color:var(--muted);line-height:1.55;}
.ptcard b{color:var(--ink);}
.ptcard.up{background:#eafaf1;border:1px solid #bfe8cf;}
.ptcard.up h4{color:#1f8a53;}
.ptcard.catch{background:#fff4ea;border:1px solid #ffd9b3;}
.ptcard.catch h4{color:#c96a1b;}
@media(max-width:700px){.predtext{grid-template-columns:1fr;}}
.twinwrap{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
.tcap{font-weight:700;font-size:15px;color:var(--ink);text-align:center;margin-bottom:12px;}
.tcap span{display:block;font-size:12px;font-weight:600;color:var(--muted);}
@media(max-width:760px){.twinwrap{grid-template-columns:1fr;}}
.poll{max-width:620px;margin:24px auto 0;text-align:left;}
.pollq{font-weight:700;font-size:16px;color:var(--ink);margin-bottom:12px;text-align:center;}
.pollopt{display:block;width:100%;text-align:left;background:#fff;border:1px solid var(--line);border-radius:12px;
 padding:14px 16px;margin:9px 0;cursor:pointer;font-size:15px;color:var(--ink);position:relative;overflow:hidden;transition:border-color .2s,transform .1s;}
.pollopt:hover{border-color:#9b5de5;}
.pollopt:active{transform:scale(.99);}
.pollopt .fill{position:absolute;left:0;top:0;bottom:0;width:0;background:linear-gradient(90deg,rgba(155,93,229,.20),rgba(237,137,54,.16));transition:width .7s cubic-bezier(.2,.8,.3,1);z-index:0;}
.pollopt .lbl,.pollopt .pct{position:relative;z-index:1;}
.pollopt .pct{float:right;font-weight:800;color:#9b5de5;display:none;}
.poll.voted .pct{display:inline;}
.poll.voted .pollopt{cursor:default;}
.pollopt.mine{border-color:#9b5de5;border-width:2px;}
.pollnote{font-size:12px;color:#8288b4;margin-top:12px;text-align:center;}
@media(prefers-reduced-motion:reduce){.pollopt .fill{transition:none;}}
.ai{background:#eef1ff;border:1px solid #d7dcf5;border-radius:18px;padding:26px;}
.ai ul{margin:10px 0 0 20px;color:var(--muted);font-size:14px;}
.ai li{margin:6px 0;}
.note{margin-top:60px;font-size:12px;color:#8288b4;border-top:1px solid var(--line);padding-top:18px;}
.note b{color:var(--muted);}
.aha{color:#c96a1b;font-weight:600;}
</style></head>
<body>
<a href="#main" class="skip">Skip to main content</a>
<div class="sunfx" aria-hidden="true"><div class="glow"></div><div class="rays"><i></i></div></div>
<div class="wrap" id="main">

<div class="hero reveal">
  <svg class="clock" viewBox="0 0 120 120" role="img" aria-label="A clock counting the hours">
    <circle cx="60" cy="60" r="54" fill="#ffffff" stroke="#e6c9a0" stroke-width="3"/>
    <circle cx="60" cy="60" r="49" fill="none" stroke="#d9b981" stroke-width="7" stroke-dasharray="2 24.18"/>
    <line x1="60" y1="60" x2="60" y2="38" stroke="#5a67d8" stroke-width="4.5" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="720s" repeatCount="indefinite"/>
    </line>
    <line x1="60" y1="60" x2="60" y2="26" stroke="#9b5de5" stroke-width="3.5" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="60s" repeatCount="indefinite"/>
    </line>
    <line x1="60" y1="66" x2="60" y2="16" stroke="#ed8936" stroke-width="2" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="4s" repeatCount="indefinite"/>
    </line>
    <circle cx="60" cy="60" r="3.5" fill="#1e2749"/>
  </svg>
  <div class="kicker">An interactive data story &middot; VizCon 2026</div>
  <h1>The 24-Hour Human</h1>
  <p class="lead">What can you do in 24 hours? And what does the rest of the world do with theirs? Discover how many hours we work, how much time we keep for leisure, and how the place you live shapes what your day looks like. All inside the same <b>1,440 minutes</b> each of us is given, every single day.</p>
  <div class="kpis">
    <div class="kpi" style="--ac:#ed8936">
      <svg class="ki" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 1.8"/></svg>
      <div class="n" data-target="1440">0</div><div class="l">Minutes everyone gets</div></div>
    <div class="kpi" style="--ac:#5a67d8">
      <svg class="ki" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c3.4 3 3.4 15 0 18c-3.4-3-3.4-15 0-18z"/></svg>
      <div class="n" data-target="35">0</div><div class="l">Countries</div></div>
    <div class="kpi" style="--ac:#9b5de5">
      <svg class="ki" viewBox="0 0 24 24"><path d="M12 3 3 8l9 5 9-5-9-5z"/><path d="M4 12l8 4.5L20 12"/><path d="M4 16l8 4.5L20 16"/></svg>
      <div class="n" data-target="5">0</div><div class="l">Continents</div></div>
    <div class="kpi" style="--ac:#e0528f">
      <svg class="ki" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.2"/><circle cx="16.5" cy="9" r="2.6"/><path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><path d="M14.6 19c.2-2.2 1.8-3.7 4-3.7s3.8 1.5 3.9 3.7"/></svg>
      <div class="n" data-target="2">0</div><div class="l">Genders compared</div></div>
  </div>
</div>

<div class="legend reveal">
  <span><i class="dot" style="background:var(--pca)"></i>Personal care (sleep, meals, hygiene)</span>
  <span><i class="dot" style="background:var(--paw)"></i>Paid work / study</span>
  <span><i class="dot" style="background:var(--upw)"></i>Unpaid work (home, care)</span>
  <span><i class="dot" style="background:var(--lei)"></i>Leisure</span>
  <span><i class="dot" style="background:var(--oth)"></i>Other</span>
</div>

<section class="reveal">
  <div class="sh">Meet our humans</div>
  <h2>One day, five lives</h2>
  <p class="sub">Meet our neighbors from around the world, one from each continent. Here's where you'll see how a single day can look completely different depending on where you stand, and how that everyday routine really plays out across the globe. What could each place add to your own day? (Each ring is one real 24-hour day; hover to explore the hours.)</p>
  <div class="pgrid" id="personaGrid"></div>
</section>

<section class="reveal">
  <div class="sh">Now your turn</div>
  <h2>Which human are you?</h2>
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
    <button class="qbtn" id="qbtn">Who's my match? 💘</button>
    <div class="qresult" id="qresult" aria-live="polite">
      <div class="matchbanner">It's a match! <span class="hearts">💖</span></div>
      <div class="matchbody">
        <div class="matchface" id="rflag"></div>
        <div class="matchinfo"><h3 id="rname"></h3><div class="matchpct" id="rpct"></div><p id="rdesc"></p></div>
        <div class="qclock"><canvas id="qclock"></canvas></div>
      </div>
    </div>
    <p class="qafter" id="qafter">Your day isn't just yours. Millions of people half a world away wake to almost the same rhythm. Time use is personal, but it's also deeply cultural. Keep that in mind as we zoom out.</p>
  </div>
</section>

<section class="reveal">
  <div class="sh">Explore all 35</div>
  <h2>Where people spend their time</h2>
  <p class="sub">So, how's the world out there? Each dot is a country we mapped, <span class="aha">colored from yellow (fewer work hours) to red (more) across the year</span>. Spin it and a pattern shows up: the busy red dots cluster where incomes are lower, while the calmer yellow ones sit among the wealthy. Find the country you're curious about and dive deep: click it to open its 24-hour day. (It's a little sad, but you'll spot a gap over South America. The honest limit of our data.)</p>
  <div class="mapwrap">
    <div id="globe"></div>
    <div class="mappanel" id="mapPanel">
      <div class="hint">👆 Click a country on the map to reveal its day.</div>
    </div>
  </div>
  <div class="maplegend">
    <span>Fewer work hours/yr</span><span class="bar"></span><span>More work hours/yr</span>
  </div>
</section>

<section class="reveal">
  <div class="sh">Screen 1</div>
  <h2>Who works the most?</h2>
  <p class="sub">Here's the first surprise: the countries that work the most aren't the richest. Over a full year, people in India, China and South Africa put in around 2,300 hours, while Germany and the Nordics stop near 1,350, almost half as much. <span class="aha">The richer a country gets, the fewer hours it works.</span> Wealth is what lets a nation ease off the clock.</p>
  <div class="panel"><div class="bubbles" id="workBubbles"></div></div>
</section>

<section class="reveal">
  <div class="sh">Screen 2 &middot; the heart of the story</div>
  <h2>The double shift</h2>
  <p class="sub">The double shift, and one stubborn question: why is it almost always women? There's a second shift, the invisible one: cooking, cleaning, raising children, caring for elders. It never shows on a payslip, it sits outside policy indicators, and it stays out of the conversation. Around the world it lands overwhelmingly on women. <span class="aha">In India, women do about five more hours of unpaid work every single day than men.</span> Turkey, Portugal and Mexico aren't far behind, while only the Nordics come close to sharing it evenly. And the penalty is double: those same women also get less time to rest. In Portugal and Italy, men enjoy almost an hour and a half more leisure every single day. Calling women strong and empowered doesn't erase those extra hours. This is the part of the day the economy never counts, the part that shapes millions of lives most, and it's long past time we talked about it as a society.</p>
  <div class="twinwrap">
    <div class="panel"><div class="tcap">🏠 Unpaid work / day <span>women do more</span></div><div class="chartbox twin"><canvas id="genderChart"></canvas></div></div>
    <div class="panel"><div class="tcap">🛋️ Leisure / day <span>men get more</span></div><div class="chartbox twin"><canvas id="leisureChart"></canvas></div></div>
  </div>
</section>

<section class="reveal">
  <div class="sh">Screen 3</div>
  <h2>Work vs. free time</h2>
  <p class="sub">Remember our five friends? Here's where each of them lands when we weigh a whole year of work against their daily free time. <span class="aha">The more a country works across the year, the less it plays each day.</span> Camille takes it slow, Sofía barely catches a break, and the others fall somewhere in between. Same 24 hours, very different lives.</p>
  <div class="panel"><div class="chartbox"><canvas id="scatterChart"></canvas></div></div>
</section>

<section class="reveal">
  <div class="sh">Screen 4</div>
  <h2>Working until when?</h2>
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

<section class="reveal">
  <div class="sh">Predictive model</div>
  <h2>🤖 The day of 2050</h2>
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
    <div class="predclocks">
      <div><div class="clab">Today</div><div class="clockbox2"><canvas id="clockToday"></canvas></div></div>
      <div class="arrow">&rarr;</div>
      <div><div class="clab">Projected 2050</div><div class="clockbox2"><canvas id="clock2050"></canvas></div></div>
    </div>
    <div class="predtext" id="predText"></div>
  </div>
</section>

<section class="reveal">
  <div class="sh">The takeaway</div>
  <h2>At the end of the day, how do you feel?</h2>
  <p class="sub" style="font-size:16px;max-width:780px">When your day ends, is it a feeling of a job well done, or of pure exhaustion? Your gender, your culture, and the country you live in can tip that balance, for better or worse. A single day is such a short thing next to a whole life. For the life you want now, and the one you want later, have you ever stopped to think about what really matters? <b>How do you live your day?</b></p>
  <div class="poll" id="poll">
    <div class="pollq">When your day ends, how do you usually feel?</div>
    <button class="pollopt" data-k="acc"><span class="fill"></span><span class="lbl">😌 Accomplished</span><span class="pct"></span></button>
    <button class="pollopt" data-k="exh"><span class="fill"></span><span class="lbl">😮‍💨 Exhausted</span><span class="pct"></span></button>
    <button class="pollopt" data-k="both"><span class="fill"></span><span class="lbl">🤷 A bit of both</span><span class="pct"></span></button>
    <button class="pollopt" data-k="busy"><span class="fill"></span><span class="lbl">⏳ Too busy to notice</span><span class="pct"></span></button>
    <div class="pollnote">Tap to cast your vote. Results are tallied on this device.</div>
  </div>
</section>

<section class="reveal">
  <div class="sh">Behind the scenes</div>
  <h2>How we used AI</h2>
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

</div>
<script>
const D = __DATA__;
const CATS=['Personal care','Paid work','Unpaid work','Leisure','Other'];
const COL=['#5a67d8','#e05265','#ed8936','#9b5de5','#a0aec0'];
const TX='#5a6285',TXD='#1e2749',GRID='rgba(30,39,73,.09)';
const hm=h=>`${Math.floor(h)}h${String(Math.round((h-Math.floor(h))*60)).padStart(2,'0')}`;
const personaISO=D.personas.map(p=>p.iso3);

const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('in');}),{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));

// sun rises as you scroll down the page
const sunfx=document.querySelector('.sunfx');
function sunScroll(){
  const max=(document.documentElement.scrollHeight-window.innerHeight)||1;
  const p=Math.min(1,Math.max(0,window.scrollY/max));
  sunfx.style.setProperty('--sunY',(-14+p*70)+'%');
  sunfx.style.setProperty('--sunO',(0.45+p*0.45).toFixed(2));
  sunfx.style.setProperty('--rayO',(0.10+p*0.55).toFixed(2));
}
window.addEventListener('scroll',sunScroll,{passive:true});
window.addEventListener('resize',sunScroll);sunScroll();

// pause the spinning clock for users who prefer reduced motion
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if(reduce){const ck=document.querySelector('.clock');if(ck && ck.pauseAnimations) ck.pauseAnimations();}

// KPI count-up animation
document.querySelectorAll('.kpi .n').forEach(el=>{
  const t=+el.dataset.target;
  if(reduce){el.textContent=t.toLocaleString('en-US');return;}
  const dur=1300,st=performance.now();
  (function step(now){const p=Math.min(1,(now-st)/dur);
    const v=Math.round(t*(1-Math.pow(1-p,3)));
    el.textContent=v.toLocaleString('en-US');
    if(p<1)requestAnimationFrame(step);})(st);
});

// ---- end-of-day poll (tallied per device via localStorage) ----
const POLL_KEY='tfhh_poll_v1', POLL_MINE='tfhh_poll_mine';
function pollData(){try{return JSON.parse(localStorage.getItem(POLL_KEY))||{};}catch(e){return {};}}
function renderPoll(show){
  const d=pollData(), total=Object.values(d).reduce((a,b)=>a+b,0), mine=localStorage.getItem(POLL_MINE);
  document.querySelectorAll('.pollopt').forEach(b=>{
    const k=b.dataset.k, v=d[k]||0, pct=total?Math.round(v/total*100):0;
    b.querySelector('.fill').style.width=(show?pct:0)+'%';
    b.querySelector('.pct').textContent=pct+'%';
    b.classList.toggle('mine', mine===k);
  });
  if(show) document.getElementById('poll').classList.add('voted');
}
document.querySelectorAll('.pollopt').forEach(b=>b.addEventListener('click',()=>{
  const poll=document.getElementById('poll');
  if(poll.classList.contains('voted')) return;
  const d=pollData(), k=b.dataset.k; d[k]=(d[k]||0)+1;
  localStorage.setItem(POLL_KEY,JSON.stringify(d)); localStorage.setItem(POLL_MINE,k);
  renderPoll(true);
}));
if(localStorage.getItem(POLL_MINE)) renderPoll(true);

// personas
const grid=document.getElementById('personaGrid');
D.personas.forEach((p,i)=>{
  const el=document.createElement('div');el.className='pcard';
  el.innerHTML=`<div class="cont">${p.continent}</div>
    <img class="avatar" src="${p.avatar}" alt="Illustrated portrait of ${p.name} from ${p.continent}">
    <div class="pname">${p.name} <span class="pflag">${p.emoji}</span></div>
    <div class="sig">${p.sig}</div>
    <div class="bio">${p.bio}</div>
    <div class="clockbox"><canvas id="clk${i}"></canvas>
      <div class="clabel"><div class="b">24h</div><div class="s">one day</div></div></div>
    <div class="pstats"><div>Retires<b>${p.ret.toFixed(0)}</b></div>
      <div>Work/yr<b>${Math.round(p.wh)}h</b></div></div>`;
  grid.appendChild(el);
  new Chart(document.getElementById('clk'+i),{type:'doughnut',
    data:{labels:CATS,datasets:[{data:p.clock,backgroundColor:COL,borderColor:'#fff',borderWidth:2}]},
    options:{cutout:'60%',plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c=>` ${c.label}: ${hm(c.parsed)}`}}}}});
});

// quiz
const ids=['pca','paw','upw','lei'];
function readQuiz(){const o={};ids.forEach(k=>o[k]=parseFloat(document.getElementById('q_'+k).value));return o;}
function updTotals(){
  const q=readQuiz();ids.forEach(k=>document.getElementById('v_'+k).textContent=hm(q[k]));
  const sum=q.pca+q.paw+q.upw+q.lei;const oth=Math.max(0,24-sum);
  document.getElementById('qtotal').innerHTML=`Accounted: <b>${hm(Math.min(24,sum))}</b> &middot; Other/leftover: <b>${hm(oth)}</b>`+(sum>24?` &middot; <span style="color:#c96a1b">over 24h, we'll rescale</span>`:``);
}
ids.forEach(k=>document.getElementById('q_'+k).addEventListener('input',updTotals));
updTotals();
let qc=null;
document.getElementById('qbtn').addEventListener('click',()=>{
  const q=readQuiz();let v=[q.pca,q.paw,q.upw,q.lei];let sum=v.reduce((a,b)=>a+b,0);
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
  if(qc)qc.destroy();
  qc=new Chart(document.getElementById('qclock'),{type:'doughnut',
    data:{labels:CATS,datasets:[{data:[best.pca,best.paw,best.upw,best.lei,best.oth],
      backgroundColor:COL,borderColor:'#fff',borderWidth:2}]},
    options:{cutout:'58%',plugins:{legend:{display:false},
      tooltip:{callbacks:{label:c=>` ${c.label}: ${hm(c.parsed)}`}}}}});
});

// Screen 1: top 10 hardest-working countries as flag bubbles (sized by hours/year)
const whAll=D.countries.map(c=>c.wh),whLo=Math.min(...whAll),whHi=Math.max(...whAll);
const top10=[...D.countries].sort((a,b)=>b.wh-a.wh).slice(0,10);
document.getElementById('workBubbles').innerHTML=top10.map(c=>{
  const dia=Math.round(64+(c.wh-whLo)/(whHi-whLo)*92);
  return `<div class="bub"><div class="circ" style="width:${dia}px;height:${dia}px">
    <img src="assets/flags/${c.iso2}.png" alt="${c.country} flag" loading="lazy"></div>
    <div class="bnm">${c.country}</div><div class="bvl">${Math.round(c.wh)}h/yr</div></div>`;
}).join('');

// Screen 2
const g=D.gender;
new Chart(document.getElementById('genderChart'),{type:'bar',
  data:{labels:g.map(x=>x.country),datasets:[
    {label:'Women',data:g.map(x=>x.f),backgroundColor:'#e05292',borderRadius:4},
    {label:'Men',data:g.map(x=>x.m),backgroundColor:'#5a67d8',borderRadius:4}]},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:TXD}},
    tooltip:{callbacks:{label:c=>` ${c.dataset.label}: ${hm(c.parsed.x)}`}}},
    scales:{x:{ticks:{color:TX,callback:v=>v+'h'},grid:{color:GRID},
      title:{display:true,text:'Unpaid work per day',color:TX}},
      y:{ticks:{color:TXD},grid:{display:false}}}}});
new Chart(document.getElementById('leisureChart'),{type:'bar',
  data:{labels:g.map(x=>x.country),datasets:[
    {label:'Women',data:g.map(x=>x.leiF),backgroundColor:'#e05292',borderRadius:4},
    {label:'Men',data:g.map(x=>x.leiM),backgroundColor:'#5a67d8',borderRadius:4}]},
  options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:TXD}},
    tooltip:{callbacks:{label:c=>` ${c.dataset.label}: ${hm(c.parsed.x)}`}}},
    scales:{x:{ticks:{color:TX,callback:v=>v+'h'},grid:{color:GRID},
      title:{display:true,text:'Leisure per day',color:TX}},
      y:{ticks:{color:TXD},grid:{display:false}}}}});

// Screen 3: retirement road with WORK/RETIRE signs and flags
const rMIN=59.5,rMAX=73;
const rField=document.getElementById('retireField');
const rW=rField.clientWidth,rSize=46;
const rXpos=a=>((a-rMIN)/(rMAX-rMIN))*(rW-rSize)+rSize/2;
const rLanes=[];
[...D.countries].sort((a,b)=>a.ret-b.ret).forEach(c=>{
  const rx=rXpos(c.ret);let rlane=0;
  while(rLanes[rlane]!==undefined && rx-rLanes[rlane]<rSize*0.86) rlane++;
  rLanes[rlane]=rx;
  const el=document.createElement('div');el.className='rmk'+(personaISO.includes(c.iso3)?' p':'');
  el.style.left=rx+'px';el.style.bottom=(rlane*46)+'px';el.title=c.country+' — retires at '+c.ret.toFixed(1);
  el.innerHTML=`<img src="assets/flags/${c.iso2}.png" alt="${c.country} flag" loading="lazy">`;
  rField.appendChild(el);
});
const rRoad=document.getElementById('retireRoad');
for(let a=60;a<=72;a+=2){const t=document.createElement('div');t.className='rtick';t.style.left=rXpos(a)+'px';t.textContent=a;rRoad.appendChild(t);}

// Screen 4
const pts=D.countries.map(c=>({x:c.wh,y:c.lei,c:c.country,iso:c.iso3}));
new Chart(document.getElementById('scatterChart'),{type:'scatter',
  data:{datasets:[
    {label:'Countries',data:pts.filter(p=>!personaISO.includes(p.iso)),
      backgroundColor:'rgba(90,103,216,.55)',pointRadius:6},
    {label:'Our five humans',data:pts.filter(p=>personaISO.includes(p.iso)),
      backgroundColor:'#ed8936',pointRadius:9,pointStyle:'triangle'}]},
  options:{plugins:{legend:{labels:{color:TXD}},
    tooltip:{callbacks:{label:c=>` ${c.raw.c}: ${Math.round(c.raw.x)}h/yr, ${hm(c.raw.y)} leisure`}}},
    scales:{x:{ticks:{color:TX},grid:{color:GRID},title:{display:true,text:'Hours worked per year',color:TX}},
      y:{ticks:{color:TX,callback:v=>v+'h'},grid:{color:GRID},title:{display:true,text:'Leisure per day',color:TX}}}}});

// ---- Predictive model: the day of 2050 ----
const M=D.model;
const selC=document.getElementById('predCountry');
D.countries.slice().sort((a,b)=>a.country.localeCompare(b.country)).forEach(c=>{
  const o=document.createElement('option');o.value=c.iso3;o.textContent=`${c.flag} ${c.country}`;selC.appendChild(o);});
selC.value='MEX';
function findC(iso){return D.countries.find(c=>c.iso3===iso);}
function project(c,growth){
  // convergência: o país caminha em direção ao que a tendência de renda prevê
  // para o seu NOVO nível de GDP; a fração de convergência cresce com o crescimento.
  const conv=Math.min(1,growth/100);
  const ng=Math.log(c.gdp*(1+growth/100));
  const tgt=m=>m.a+m.b*ng;
  const paw=Math.max(0,c.paw+(tgt(M.paw_h)-c.paw)*conv);
  const lei=Math.max(0,c.lei+(tgt(M.lei_h)-c.lei)*conv);
  const upw=Math.max(0,c.upw+(tgt(M.upw_h)-c.upw)*conv);
  let v=[c.pca,paw,upw,lei,c.oth];const s=v.reduce((a,b)=>a+b,0);return v.map(x=>x*24/s);
}
const refT={c:null},refF={c:null};
function drawClock(id,data,ref){
  if(ref.c)ref.c.destroy();
  ref.c=new Chart(document.getElementById(id),{type:'doughnut',
    data:{labels:CATS,datasets:[{data,backgroundColor:COL,borderColor:'#fff',borderWidth:2}]},
    options:{cutout:'58%',plugins:{legend:{display:false},
      tooltip:{callbacks:{label:x=>` ${x.label}: ${hm(x.parsed)}`}}}}});
}
function renderPred(){
  const c=findC(selC.value);const g=parseInt(document.getElementById('predGrowth').value);
  document.getElementById('predGrowthLbl').textContent='+'+g+'%';
  const now=[c.pca,c.paw,c.upw,c.lei,c.oth],fut=project(c,g);
  drawClock('clockToday',now,refT);drawClock('clock2050',fut,refF);
  const dLei=Math.round((fut[3]-c.lei)*60),dPaw=Math.round((fut[1]-c.paw)*60);
  const sg=v=>(v>=0?'+':'')+v;
  document.getElementById('predKpis').innerHTML=`
    <div class="k"><div class="n" style="color:#9b5de5">${hm(fut[3])}</div><div class="l">Leisure/day (${sg(dLei)} min)</div></div>
    <div class="k"><div class="n" style="color:#e05265">${hm(fut[1])}</div><div class="l">Paid work/day (${sg(dPaw)} min)</div></div>
    <div class="k"><div class="n" style="color:#5a67d8">$${Math.round(c.gdp*(1+g/100)/1000)}k</div><div class="l">Projected GDP/capita (PPP)</div></div>
    <div class="k"><div class="n" style="color:#ed8936">+${g}%</div><div class="l">Growth scenario</div></div>`;
  // narrative: bright side + pain points (specific to the country)
  const yearH=Math.round(Math.abs(dLei)*365/60);
  const avgLei=D.countries.reduce((s,x)=>s+x.lei,0)/D.countries.length;
  const restPos = c.lei>=avgLei ? `already one of the more rested nations` : `below the 35-country average for free time`;
  let up;
  if(g<=0){
    up=`Today ${c.country} enjoys <b>${hm(c.lei)}</b> of leisure a day (${restPos}). Slide the growth up to see how prosperity could reshape the day.`;
  }else if(dLei>=1){
    up=`From <b>${hm(c.lei)}</b> today, leisure climbs <b>+${dLei} min/day</b> (~${yearH}h a year) as paid work eases by <b>${Math.abs(dPaw)} min</b>, and ${c.country} drifts toward the rhythm of wealthier nations.`;
  }else if(dLei<=-1){
    up=`${c.country} already rests <b>${hm(c.lei)}</b> a day, more than its income alone would predict. Growth won't add free time here; that leisure springs from other forces, not wealth.`;
  }else{
    up=`${c.country} already sits right where its income predicts (<b>${hm(c.lei)}</b> of leisure), so growth alone barely shifts the day.`;
  }
  // gap de gênero real do país
  const gapMin=Math.round((c.upwF-c.upwM)*60);
  const genderLine = gapMin>0
    ? `In ${c.country}, women already do about <b>${gapMin} min more unpaid work a day</b> than men, and income barely moves that gap in our data.`
    : `Even where the gender gap is small, income alone doesn't close it in our data.`;
  const catchTxt = `${genderLine} <b>Prosperity won't split the second shift</b>: that needs policy, not just a bigger economy. And this is a <b>pattern, not a promise</b>: freed-up hours can quietly become screen time, and shorter workdays usually take deliberate choices (4-day weeks, paid leave).`;
  document.getElementById('predText').innerHTML=`
    <div class="ptcard up"><h4>🌱 The bright side</h4><p>${up}</p></div>
    <div class="ptcard catch"><h4>⚠️ The catch</h4><p>${catchTxt}</p></div>`;
}
selC.addEventListener('change',renderPred);
document.getElementById('predGrowth').addEventListener('input',renderPred);
document.querySelectorAll('.predquick button').forEach(b=>b.addEventListener('click',()=>{
  document.getElementById('predGrowth').value=b.dataset.g;renderPred();}));
renderPred();

// ---- Interactive globe ----
const whs=D.countries.map(c=>c.wh);const whMin=Math.min(...whs),whMax=Math.max(...whs);
function whColor(v){const t=Math.max(0,Math.min(1,(v-whMin)/(whMax-whMin)));
  const a=[255,214,10],b=[214,20,64];   // yellow -> red (contrasts with ocean/land)
  return `rgb(${a.map((x,i)=>Math.round(x+(b[i]-x)*t)).join(',')})`;}
let mapClock=null;
function selectCountry(c){
  const p=document.getElementById('mapPanel');
  p.innerHTML=`<div class="mpflag">${c.flag}</div><div class="mpname">${c.country}</div>
    <div class="mpclock"><canvas id="mpClock"></canvas></div>
    <div class="mpstats">
      <div><span>Paid work</span><b>${hm(c.paw)}/day</b></div>
      <div><span>Unpaid work</span><b>${hm(c.upw)}/day</b></div>
      <div><span>Leisure</span><b>${hm(c.lei)}/day</b></div>
      <div><span>Personal care</span><b>${hm(c.pca)}/day</b></div>
      <div><span>Work per year</span><b>${Math.round(c.wh)}h</b></div>
      <div><span>Retires (men)</span><b>${c.ret.toFixed(0)} yrs</b></div>
    </div>`;
  if(mapClock)mapClock.destroy();
  mapClock=new Chart(document.getElementById('mpClock'),{type:'doughnut',
    data:{labels:CATS,datasets:[{data:[c.pca,c.paw,c.upw,c.lei,c.oth],
      backgroundColor:COL,borderColor:'#fff',borderWidth:2}]},
    options:{cutout:'58%',plugins:{legend:{display:false},
      tooltip:{callbacks:{label:x=>` ${x.label}: ${hm(x.parsed)}`}}}}});
}
const gEl=document.getElementById('globe');
if(typeof Globe==='undefined'){
  gEl.innerHTML='<div style="color:#5a6285;padding:30px;text-align:center">Globe library failed to load. Check that assets/lib/globe.gl.min.js exists.</div>';
}else{
  const globe=Globe()(gEl)
    .globeImageUrl('assets/img/earth-day.jpg')
    .backgroundColor('rgba(0,0,0,0)')
    .showAtmosphere(true).atmosphereColor('#cfe3ff').atmosphereAltitude(0.22)
    .pointsData(D.countries).pointLat('lat').pointLng('lng')
    .pointColor(d=>whColor(d.wh)).pointAltitude(0.012).pointRadius(0.9)
    .pointResolution(24)
    .pointLabel(d=>`${d.flag} ${d.country} · ${Math.round(d.wh)}h/yr`)
    .onPointClick(d=>selectCountry(d));
  // clarear o globo com luz ambiente extra
  try{const sc=globe.scene();sc.children.filter(o=>o.isLight).forEach(l=>l.intensity*=1.35);
    const THREEg=globe.scene().constructor;}catch(e){}
  const sizeGlobe=()=>globe.width(gEl.clientWidth).height(gEl.clientHeight);
  requestAnimationFrame(sizeGlobe);
  window.addEventListener('resize',sizeGlobe);
  globe.pointOfView({lat:15,lng:-20,altitude:2.3});
  const ctr=globe.controls();ctr.autoRotate=true;ctr.autoRotateSpeed=0.7;ctr.enableZoom=true;
}
</script>
</body></html>
"""

OUT.write_text(HTML.replace("__DATA__", DATA), encoding="utf-8")
print(f"OK -> {OUT}  ({len(countries)} countries, {len(gender)} gender bars, {len(personas)} personas)")
