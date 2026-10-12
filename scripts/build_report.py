"""Render runs/<run>/result.json -> runs/<run>/report.html, then rebuild the root index.html.

Usage:
    python3 scripts/build_report.py runs/<run-folder>

Pure static HTML + inline CSS/SVG (only external asset: Google Fonts). Phone-first, light/dark.
"""
import glob
import html
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from teams import colors, name  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc = html.escape


def pct(p):
    return int(p * 100 + 0.5)


def odds(o):
    return "—" if o is None else (f"+{o}" if o > 0 else str(o))


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def lum(h):
    return sum(w * v / 255 for w, v in zip((0.299, 0.587, 0.114), _rgb(h)))


def chart_color(h):
    """Lift very dark team colors so they read on both light and dark backgrounds."""
    c = _rgb(h)
    while lum(_hex(c)) < 0.38:
        c = [v + (255 - v) * 0.18 for v in c]
    return _hex(c)


def team_accents(a, h):
    ca, cb = colors(a), colors(h)
    acc_a, acc_h = chart_color(ca[0]), chart_color(cb[0])
    if sum(abs(x - y) for x, y in zip(_rgb(acc_a), _rgb(acc_h))) < 120:  # too alike -> use home secondary
        acc_h = chart_color(cb[1])
    return acc_a, acc_h


CSS = """
:root{--bg:#0b1020;--panel:#131a2e;--panel2:#1a2340;--ink:#eef2ff;--mute:#9aa6c8;--line:#2a3558;
--go:#22c55e;--no:#f43f5e;--warn:#f59e0b;--info:#38bdf8;--vio:#a78bfa;--track:#222c4a;
--shadow:0 10px 30px rgba(0,0,0,.35)}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--bg:#f4f6fb;--panel:#ffffff;--panel2:#eef2fb;
--ink:#0f172a;--mute:#5b6787;--line:#dfe5f2;--track:#e6ebf5;--shadow:0 8px 24px rgba(15,23,42,.08)}}
:root[data-theme="light"]{--bg:#f4f6fb;--panel:#ffffff;--panel2:#eef2fb;--ink:#0f172a;--mute:#5b6787;--line:#dfe5f2;--track:#e6ebf5;--shadow:0 8px 24px rgba(15,23,42,.08)}
:root[data-theme="dark"]{--bg:#0b1020;--panel:#131a2e;--panel2:#1a2340;--ink:#eef2ff;--mute:#9aa6c8;--line:#2a3558;--track:#222c4a}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:16px}
h1,h2,h3,.num{font-family:Oswald,Inter,sans-serif;letter-spacing:.3px}
h2{font-size:20px;margin:28px 0 12px;display:flex;align-items:center;gap:10px}
h2:before{content:"";width:6px;height:22px;border-radius:3px;background:linear-gradient(var(--a),var(--h))}
a{color:var(--info)}
.hero{border-radius:22px;overflow:hidden;box-shadow:var(--shadow);position:relative;color:#fff;
background:linear-gradient(115deg,var(--a1) 0%,var(--a1) 42%,var(--h1) 58%,var(--h1) 100%)}
.hero:after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 20% 0%,rgba(255,255,255,.18),transparent 55%),
linear-gradient(115deg,transparent 46%,rgba(255,255,255,.25) 50%,transparent 54%)}
.hero-in{position:relative;z-index:1;padding:22px 20px 18px}
.stripe{position:relative;z-index:1;display:grid;grid-template-columns:1fr 1fr;height:8px}
.kick{font-size:12px;text-transform:uppercase;letter-spacing:2px;opacity:.85}
.vs{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;margin:14px 0 6px}
.tm{text-align:center}.tm .ab{font:700 46px/1 Oswald,sans-serif}.tm .nm{font-size:12px;opacity:.85}
.tm .rec{display:inline-block;margin-top:6px;font-size:11px;padding:2px 8px;border-radius:99px;background:rgba(0,0,0,.28)}
.at{font:600 18px Oswald,sans-serif;opacity:.8}
.chips{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-top:12px}
.chip{font-size:12px;padding:5px 10px;border-radius:99px;background:rgba(0,0,0,.32);backdrop-filter:blur(4px)}
.verdict{margin:16px 0 0;border-radius:16px;padding:14px 16px;display:flex;gap:12px;align-items:center;
background:var(--panel);border:1px solid var(--line);box-shadow:var(--shadow)}
.verdict .big{font:700 22px Oswald,sans-serif}.verdict .ic{font-size:28px}
.grid{display:grid;gap:12px}.g2{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:14px 14px 12px;box-shadow:var(--shadow)}
.mk-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.mk-bet{font-size:11px;text-transform:uppercase;letter-spacing:1.5px;color:var(--mute)}
.mk-pick{font:600 20px Oswald,sans-serif}
.mk-ch{font:700 34px/1 Oswald,sans-serif;text-align:right}
.badge{display:inline-block;font-size:11px;font-weight:700;padding:3px 8px;border-radius:99px;letter-spacing:.5px}
.b-go{background:rgba(34,197,94,.16);color:var(--go)}.b-no{background:rgba(244,63,94,.14);color:var(--no)}
.b-warn{background:rgba(245,158,11,.16);color:var(--warn)}
.bar{position:relative;height:14px;border-radius:99px;background:var(--track);margin:14px 0 6px;overflow:visible}
.fill{position:absolute;left:0;top:0;bottom:0;border-radius:99px}
.cut{position:absolute;top:-5px;bottom:-5px;width:0;border-left:2px dashed var(--ink);opacity:.55}
.dot{position:absolute;top:50%;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;border:2px solid var(--panel)}
.dia{position:absolute;top:50%;width:12px;height:12px;margin:-6px 0 0 -6px;transform:rotate(45deg);border:2px solid var(--panel)}
.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:11px;color:var(--mute)}
.legend i{display:inline-block;width:9px;height:9px;margin-right:4px;vertical-align:-1px}
.kv{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px}
.kv div{background:var(--panel2);border-radius:10px;padding:6px 8px}.kv b{display:block;font:600 16px Oswald,sans-serif}
.kv span{font-size:10px;color:var(--mute);text-transform:uppercase;letter-spacing:1px}
.why{font-size:13px;color:var(--mute);margin-top:8px}
.score{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.sc{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:14px;box-shadow:var(--shadow)}
.sc h3{margin:0 0 8px;font-size:13px;color:var(--mute);text-transform:uppercase;letter-spacing:1.5px}
.sline{display:flex;align-items:center;justify-content:space-between;margin:4px 0}
.sline .num{font-size:30px;font-weight:700}
.pill{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px}
.cmp{font-size:12px;color:var(--mute);border-top:1px solid var(--line);padding-top:8px;margin-top:8px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:7px 6px;text-align:right;border-bottom:1px solid var(--line)}th:first-child,td:first-child{text-align:left}
th{color:var(--mute);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:1px}
.scroll{overflow-x:auto}
.tape-row{display:grid;grid-template-columns:1fr 92px 1fr;align-items:center;gap:8px;margin:7px 0;font-size:13px}
.tape-l,.tape-r{display:flex;align-items:center;gap:6px}.tape-l{justify-content:flex-end}
.tape-c{text-align:center;font-size:11px;color:var(--mute);text-transform:uppercase;letter-spacing:.8px;line-height:1.2}
.tb{height:10px;border-radius:99px}
.best{font-weight:700}
ul.clean{margin:0;padding-left:18px}ul.clean li{margin:4px 0}
.inj{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.tag{font-size:10px;font-weight:700;padding:2px 6px;border-radius:6px;margin-right:6px}
.t-out{background:rgba(244,63,94,.15);color:var(--no)}.t-q{background:rgba(245,158,11,.16);color:var(--warn)}
.t-ok{background:rgba(34,197,94,.15);color:var(--go)}
.foot{color:var(--mute);font-size:12px;margin:28px 0 10px;text-align:center}
svg text{fill:var(--mute);font:10px Inter,sans-serif}
@media (max-width:520px){.tm .ab{font-size:38px}.mk-ch{font-size:30px}.score{grid-template-columns:1fr}.kv b{font-size:15px}}
"""


def chance_bar(m, acc):
    cut = 0.65 if m["bet"].startswith(("1H", "2H")) else 0.60
    f = m["final"]
    col = "#22c55e" if m["qualifies"] else ("#f59e0b" if f >= cut - 0.05 else acc)  # hex: gets an alpha suffix below
    marks = f'<div class="fill" style="width:{f*100:.1f}%;background:linear-gradient(90deg,{col}66,{col})"></div>'
    marks += f'<div class="cut" style="left:{cut*100}%" title="cutoff {pct(cut)}%"></div>'
    ref = m.get("fair", m.get("league"))
    marks += f'<div class="dia" style="left:{ref*100:.1f}%;background:var(--info)" title="{"book fair" if "fair" in m else "league rate"} {pct(ref)}%"></div>'
    marks += f'<div class="dot" style="left:{m["model"]*100:.1f}%;background:var(--vio)" title="model {pct(m["model"])}%"></div>'
    return f'<div class="bar">{marks}</div>'


def market_card(m, acc, why):
    half = m["bet"].startswith(("1H", "2H"))
    if m["qualifies"]:
        badge = '<span class="badge b-go">✓ BET</span>'
    else:
        badge = '<span class="badge b-no">PASS</span>'
    if m["disagree"]:
        badge += ' <span class="badge b-warn">⚠ DISAGREE</span>'
    ref_lbl = "League" if half else "Book fair"
    ref = m["league"] if half else m["fair"]
    third = (f'<div><span>Team count</span><b>{m["team_count"]}/{m["team_games"]}</b></div>' if half
             else f'<div><span>Book price</span><b>{odds(m["price"])}</b></div>')
    blocked = "" if m["qualifies"] else f'<div class="why"><b>Blocked by:</b> {esc(", ".join(m["blocked_by"]))}</div>'
    return f"""<div class="card">
 <div class="mk-top"><div><div class="mk-bet">{esc(m['bet'])}</div><div class="mk-pick">{esc(m['pick'])}</div>{badge}</div>
 <div class="mk-ch num">{pct(m['final'])}%</div></div>
 {chance_bar(m, acc)}
 <div class="legend"><span><i style="background:var(--vio);border-radius:50%"></i>Model {pct(m['model'])}%</span>
 <span><i style="background:var(--info);transform:rotate(45deg)"></i>{ref_lbl} {pct(ref)}%</span>
 <span><i style="border-left:2px dashed var(--ink);width:2px"></i>Cutoff {65 if half else 60}%</span></div>
 <div class="kv"><div><span>Final</span><b>{pct(m['final'])}%</b></div><div><span>Need</span><b>{odds(m['need'])}</b></div>{third}</div>
 <div class="why">{esc(why)}</div>{blocked}
</div>"""


def half_chart(rows, key, acc_t, label):
    """Per-game half totals (both teams) vs the 26.5 line."""
    W, Hh, pad = 300, 130, 22
    vals = [r[f"{key}f"] + r[f"{key}a"] for r in rows]
    top = max(max(vals), 30) + 4
    bw = (W - pad * 2) / len(vals)
    y = lambda v: Hh - 18 - (v / top) * (Hh - 30)
    s = [f'<svg viewBox="0 0 {W} {Hh}" width="100%" role="img" aria-label="{esc(label)}">']
    for i, (r, v) in enumerate(zip(rows, vals)):
        x = pad + i * bw + bw * 0.18
        w = bw * 0.64
        under = v < 26.5
        c = "var(--go)" if under else "var(--no)"
        own = r[f"{key}f"]
        s.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{w:.1f}" height="{y(0)-y(v):.1f}" rx="5" fill="{c}" opacity=".25"/>')
        s.append(f'<rect x="{x:.1f}" y="{y(own):.1f}" width="{w:.1f}" height="{y(0)-y(own):.1f}" rx="5" fill="{acc_t}"/>')
        s.append(f'<text x="{x+w/2:.1f}" y="{y(v)-4:.1f}" text-anchor="middle" style="fill:{c};font-weight:700">{v:g}</text>')
        s.append(f'<text x="{x+w/2:.1f}" y="{Hh-4}" text-anchor="middle">W{r["wk"]} {"vs" if r["home"] else "@"} {r["opp"]}</text>')
    s.append(f'<line x1="{pad-6}" x2="{W-pad+6}" y1="{y(26.5):.1f}" y2="{y(26.5):.1f}" stroke="var(--warn)" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(f'<text x="{W-pad+4}" y="{y(26.5)-4:.1f}" text-anchor="end" style="fill:var(--warn)">26.5</text></svg>')
    return "".join(s)


def tape(r, acc_a, acc_h):
    A, H = r["away"], r["home"]
    TA, TH = r["teams"][A], r["teams"][H]
    num = lambda s: float(str(s).rstrip("%")) if s not in (None, "-", "") else None
    rows = [  # label, away value, home value, higher_is_better, fmt
        ("Off EPA/play", TA["epa"]["off"]["epa"], TH["epa"]["off"]["epa"], True, lambda v: f"{v:+.3f}"),
        ("Def EPA/play", TA["epa"]["def"]["epa"], TH["epa"]["def"]["epa"], False, lambda v: f"{v:+.3f}"),
        ("Pts scored", TA["espn"]["pf"], TH["espn"]["pf"], True, lambda v: f"{v:.1f}"),
        ("Pts allowed", TA["espn"]["pa"], TH["espn"]["pa"], False, lambda v: f"{v:.1f}"),
        ("Yds/play", num(TA["stats"]["ypp"]), num(TH["stats"]["ypp"]), True, lambda v: f"{v:.1f}"),
        ("Opp yds/play", num(TA["stats"]["opp_ypp"]), num(TH["stats"]["opp_ypp"]), False, lambda v: f"{v:.1f}"),
        ("Opp yds/att", num(TA["stats"]["opp_ypa"]), num(TH["stats"]["opp_ypa"]), False, lambda v: f"{v:.1f}"),
        ("3rd down %", num(TA["stats"]["third"]), num(TH["stats"]["third"]), True, lambda v: f"{v:.0f}%"),
        ("Pressure %", num(TA["stats"]["pressure"]), num(TH["stats"]["pressure"]), True, lambda v: f"{v:.0f}%"),
        ("Plays/game", num(TA["stats"]["plays"]), num(TH["stats"]["plays"]), None, lambda v: f"{v:.1f}"),
        ("TO margin/g", num(TA["stats"]["to_margin"]), num(TH["stats"]["to_margin"]), True, lambda v: f"{v:+.2f}"),
    ]
    out = []
    for lbl, a, h, hib, f in rows:
        if a is None or h is None:
            continue
        lo = min(a, h, 0)
        span = (max(abs(a - lo), abs(h - lo)) or 1)
        wa, wh = 18 + 82 * abs(a - lo) / span, 18 + 82 * abs(h - lo) / span
        ba = "best" if hib is not None and ((a > h) == hib) and a != h else ""
        bh = "best" if hib is not None and ((h > a) == hib) and a != h else ""
        out.append(f'<div class="tape-row"><div class="tape-l"><span class="{ba}">{f(a)}</span><div class="tb" style="width:{wa:.0f}%;max-width:120px;background:{acc_a}"></div></div>'
                   f'<div class="tape-c">{lbl}</div>'
                   f'<div class="tape-r"><div class="tb" style="width:{wh:.0f}%;max-width:120px;background:{acc_h}"></div><span class="{bh}">{f(h)}</span></div></div>')
    ranks = (f'<div class="cmp">EPA ranks (1 = best): {A} offense #{TA["epa"]["off"]["rank"]}, defense #{TA["epa"]["def"]["rank"]} · '
             f'{H} offense #{TH["epa"]["off"]["rank"]}, defense #{TH["epa"]["def"]["rank"]}. Bold = better side. EPA derived from nflverse play-by-play.</div>')
    return "".join(out) + ranks


def inj_list(items):
    li = []
    for x in items:
        t = x.split(":")[0].strip().upper()
        cls = "t-out" if t in ("OUT", "IR") else ("t-ok" if t.startswith("CLEAR") else "t-q")
        li.append(f'<li><span class="tag {cls}">{esc(t)}</span>{esc(x.split(":", 1)[1].strip() if ":" in x else x)}</li>')
    return '<ul class="clean" style="list-style:none;padding:0">' + "".join(li) + "</ul>"


def why_line(m, r):
    p, A, H = r["proj"], r["away"], r["home"]
    lead = lambda mm: f"{H} by {mm:.1f}" if mm >= 0 else f"{A} by {-mm:.1f}"
    if m["bet"] == "ML":
        return f"Model margin {lead(p['raw']['margin_home'])} (raw) / {lead(p['adj']['margin_home'])} (adj): near a coin flip; book says {pct(m['fair'])}%."
    if m["bet"] == "Spread":
        return f"Projected margin {lead(p['raw']['margin_home'])} to {lead(p['adj']['margin_home'])} vs the {r['meta']['spread']['home_line']:+g} line."
    if m["bet"] == "O/U":
        return f"Model total {p['raw']['total']:.1f}–{p['adj']['total']:.1f} vs {r['meta']['total']['line']}."
    key = "h1" if m["bet"].startswith("1H") else "h2"
    return f"Projected {key.upper()} total {p[key]:.1f}; {m['team_count']} of {m['team_games']} team games stayed under; league {pct(m['league'])}%."


def game_section(r, league):
    A, H = r["away"], r["home"]
    acc_a, acc_h = team_accents(A, H)
    pa_, ph_ = colors(A)[0], colors(H)[0]
    meta, p = r["meta"], r["proj"]
    T = r["teams"]
    rec = lambda t: T[t]["trends"]["tr_moneyline"].get("Win/Loss", "")
    bets = [m for m in r["markets"] if m["qualifies"]]
    if bets:
        verdict = f'<div class="ic">✅</div><div><div class="big">{len(bets)} bet{"s" if len(bets) > 1 else ""} qualify</div><div class="why">{esc(" · ".join(m["bet"] + " " + m["pick"] for m in bets))}</div></div>'
    else:
        near = max(r["markets"], key=lambda m: m["final"] - (0.65 if m["bet"].startswith(("1H", "2H")) else 0.60))
        verdict = (f'<div class="ic">🛑</div><div><div class="big">No bets: every market fails a rule</div>'
                   f'<div class="why">Closest: {esc(near["bet"])} {esc(near["pick"])} at {pct(near["final"])}% ({esc(", ".join(near["blocked_by"]))}).</div></div>')
    sp, to = meta["spread"], meta["total"]
    chips = [meta.get("kickoff", ""), meta.get("venue", ""), f"{H} {sp['home_line']:+g}", f"ML {A} {odds(meta['ml']['away'])} / {H} {odds(meta['ml']['home'])}", f"O/U {to['line']}"]
    lead = lambda mm: f"{H} by {mm:.1f}" if mm >= 0 else f"{A} by {-mm:.1f}"

    cards = "".join(market_card(m, acc_h, why_line(m, r)) for m in r["markets"])
    logs_tbl = ""
    for t in (A, H):
        rows = "".join(f'<tr><td>W{g["wk"]} {"vs" if g["home"] else "@"} {g["opp"]}</td><td>{g["pf"]}-{g["pa"]}</td>'
                       f'<td>{g["h1f"]:g}-{g["h1a"]:g}</td><td>{g["h2f"]:g}-{g["h2a"]:g}</td></tr>' for g in T[t]["log"])
        e, s = T[t]["espn"], T[t]["statrankings"]
        logs_tbl += (f'<div class="card"><h3 style="margin:0 0 6px;color:{acc_a if t == A else acc_h}">{t} game log</h3><div class="scroll"><table>'
                     f'<tr><th>Game</th><th>Final</th><th>1H</th><th>2H</th></tr>{rows}'
                     f'<tr><td><b>Avg (ESPN)</b></td><td>{e["pf"]:.1f}-{e["pa"]:.1f}</td><td>{e["h1f"]:.1f}-{e["h1a"]:.1f}</td><td>{e["h2f"]:.1f}-{e["h2a"]:.1f}</td></tr>'
                     f'<tr><td>StatRankings</td><td>{s["pf"]}-{s["pa"]}</td><td>{s["h1f"]}-{s["h1a"]}</td><td>{s["h2f"]}-{s["h2a"]}</td></tr></table></div></div>')
    halves = "".join(
        f'<div class="card"><h3 style="margin:0 0 4px">{t}: {lbl}</h3>{half_chart(T[t]["log"], k, acc_a if t == A else acc_h, t + " " + lbl)}'
        f'<div class="why">Solid bar = {t} points; faint bar = game total (green under, red over).</div></div>'
        for k, lbl in (("h1", "1st-half totals"), ("h2", "2nd-half totals")) for t in (A, H))
    kills = "".join(f"<li><b>{esc(k)}:</b> {esc(v)}</li>" for k, v in meta.get("kills_it", {}).items())
    sched = p["schedule"]
    return f"""
<section class="hero" style="--a1:{pa_};--h1:{ph_}"><div class="hero-in">
 <div class="kick">{esc(meta.get('kickoff', ''))}</div>
 <div class="vs"><div class="tm"><div class="ab">{A}</div><div class="nm">{esc(name(A))}</div><div class="rec">{esc(rec(A))}</div></div>
 <div class="at">@</div>
 <div class="tm"><div class="ab">{H}</div><div class="nm">{esc(name(H))}</div><div class="rec">{esc(rec(H))}</div></div></div>
 <div class="chips">{''.join(f'<span class="chip">{esc(c)}</span>' for c in chips[2:])}</div>
</div><div class="stripe"><span style="background:{colors(A)[1]}"></span><span style="background:{colors(H)[1]}"></span></div></section>
<div class="verdict">{verdict}</div>

<h2>Projected score</h2>
<div class="score">
 <div class="sc"><h3>Raw</h3>
  <div class="sline"><span><i class="pill" style="background:{acc_a}"></i>{A}</span><span class="num">{p['raw']['away']:.1f}</span></div>
  <div class="sline"><span><i class="pill" style="background:{acc_h}"></i>{H}</span><span class="num">{p['raw']['home']:.1f}</span></div>
  <div class="cmp">Margin {lead(p['raw']['margin_home'])} (incl. +1.5 home) · Total {p['raw']['total']:.1f}</div></div>
 <div class="sc"><h3>Schedule-adjusted</h3>
  <div class="sline"><span><i class="pill" style="background:{acc_a}"></i>{A}</span><span class="num">{p['adj']['away']:.1f}</span></div>
  <div class="sline"><span><i class="pill" style="background:{acc_h}"></i>{H}</span><span class="num">{p['adj']['home']:.1f}</span></div>
  <div class="cmp">Margin {lead(p['adj']['margin_home'])} · Total {p['adj']['total']:.1f}</div></div>
</div>
<div class="card" style="margin-top:12px"><div class="why" style="margin:0">
 <b>Book says:</b> {H} by {-sp['home_line']:g}, total {to['line']}. <b>Model says:</b> {lead(p['raw']['margin_home'])} to {lead(p['adj']['margin_home'])}, total {p['raw']['total']:.1f}–{p['adj']['total']:.1f}.
 Schedule: {A} opponents allowed {sched[A]['opp_avg_pa']:.1f} / scored {sched[A]['opp_avg_pf']:.1f}; {H} opponents allowed {sched[H]['opp_avg_pa']:.1f} / scored {sched[H]['opp_avg_pf']:.1f} (league avg {p['league_avg_ppg']:.1f}).
 <br><b>Line move:</b> {esc(meta.get('line_move', '—'))}</div></div>

<h2>All 5 bets</h2>
<div class="grid g2">{cards}</div>

<h2>Half scoring vs 26.5</h2>
<div class="grid g2">{halves}</div>
<div class="card" style="margin-top:12px"><div class="why" style="margin:0">League this season: 1H avg {league['h1_avg']:.1f}, under 26.5 in {league['h1_under']}/{league['games']} ({pct(league['h1_rate'])}%) ·
 2H avg {league['h2_avg']:.1f}, under 26.5 in {league['h2_under']}/{league['games']} ({pct(league['h2_rate'])}%). OT excluded.</div></div>

<h2>Tale of the tape</h2>
<div class="card"><div class="tape-row" style="font-weight:700"><div style="text-align:right;color:{acc_a}">{A}</div><div></div><div style="color:{acc_h}">{H}</div></div>{tape(r, acc_a, acc_h)}</div>

<h2>Game logs</h2>
<div class="grid g2">{logs_tbl}</div>

<h2>Injuries &amp; situation</h2>
<div class="inj">
 <div class="card"><h3 style="margin:0 0 6px;color:{acc_a}">{A}</h3>{inj_list(meta.get('injuries', {}).get(A, []))}</div>
 <div class="card"><h3 style="margin:0 0 6px;color:{acc_h}">{H}</h3>{inj_list(meta.get('injuries', {}).get(H, []))}</div>
</div>
<div class="card" style="margin-top:12px"><ul class="clean">
 <li><b>QBs:</b> {esc(meta.get('qbs', '—'))}</li><li><b>Weather:</b> {esc(meta.get('weather', '—'))}</li>
 <li><b>Opening line:</b> {esc(meta.get('opening', '—'))}</li>
 {''.join(f'<li>{esc(x)}</li>' for x in meta.get('situation', []))}
 <li><b>Lines source:</b> {esc(meta.get('lines_source', '—'))}</li></ul></div>
{f'<h2>Kills it</h2><div class="card"><ul class="clean">{kills}</ul></div>' if kills else ''}
"""


def page(title, body, accents=("#38bdf8", "#a78bfa"), back=True):
    nav = '<a href="../../index.html" style="font-size:13px">← All runs</a>' if back else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body style="--a:{accents[0]};--h:{accents[1]}"><div class="wrap">{nav}{body}</div></body></html>"""


def build_run(run):
    res = json.load(open(f"{run}/result.json"))
    cfg, league = res["config"], res["league"]
    body = f'<h1 style="font-size:26px;margin:10px 0 14px">NFL Bet Research <span style="color:var(--mute);font-weight:500">· {esc(cfg.get("title", ""))}</span></h1>'
    for r in res["games"]:
        body += game_section(r, league)
    # Tables 2/3 across all games
    bets = sorted([(m, r) for r in res["games"] for m in r["markets"] if m["qualifies"]], key=lambda x: -x[0]["final"])
    t2 = "".join(f'<tr><td>{i}</td><td>{x["away"]}@{x["home"]} {esc(m["bet"])} {esc(m["pick"])}</td><td>{pct(m["final"])}%</td><td>{odds(m["need"])}</td></tr>'
                 for i, (m, x) in enumerate(bets, 1)) or '<tr><td colspan="4" style="text-align:center;color:var(--mute)">None qualify.</td></tr>'
    t3 = "".join(f'<tr><td>{esc(" + ".join(p["legs"]))}</td><td>{pct(p["combined"])}%</td></tr>' for p in res["parlays"]) \
        or '<tr><td colspan="2" style="text-align:center;color:var(--mute)">None. No legs at 65%+ that qualify.</td></tr>'
    body += f"""<h2>Bets we'd make</h2><div class="card scroll"><table><tr><th>#</th><th>Bet</th><th>Chance</th><th>Need</th></tr>{t2}</table></div>
<h2>Parlays</h2><div class="card scroll"><table><tr><th>Parlay</th><th>Combined</th></tr>{t3}</table></div>
<h2>Not checked</h2><div class="card"><ul class="clean">{''.join(f'<li>{esc(x)}</li>' for x in cfg.get('not_checked', []))}</ul></div>
<h2>Sources</h2><div class="card"><ul class="clean">{''.join(f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for t, u in cfg.get('sources', []))}</ul></div>
<h2>How the chance is computed</h2><div class="card"><div class="why" style="margin:0">
Model = average of RAW and schedule-adjusted normal-CDF chances (σ 13.3 margin, 13.5 total, 10 / 10.5 halves).
Final = book fair + 25% × (model − fair). Halves: Final = (model + league rate) / 2.
Bet only if Final ≥ 60% (≥ 65% halves, plus team count ≥ 75%), no ⚠ DISAGREE (|model − fair| &gt; 10 pts), and price at or better than Need. All numbers derived by <code>scripts/template_a.py</code>; see <code>result.json</code>.</div></div>
<div class="foot">Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · Run date {esc(cfg.get('run_date', ''))} · No template guarantees a win. Track every bet against the closing line.</div>"""
    g0 = res["games"][0]
    acc = team_accents(g0["away"], g0["home"])
    title = " · ".join(f'{r["away"]} @ {r["home"]}' for r in res["games"])
    open(f"{run}/report.html", "w").write(page(f"{title} Bet Research", body, acc))


def build_index():
    cards = []
    for rj in sorted(glob.glob(f"{ROOT}/runs/*/result.json"), reverse=True):
        run = os.path.basename(os.path.dirname(rj))
        res = json.load(open(rj))
        cfg = res["config"]
        for r in res["games"]:
            A, H = r["away"], r["home"]
            q = [m for m in r["markets"] if m["qualifies"]]
            badge = f'<span class="badge b-go">✓ {len(q)} bet{"s" if len(q) != 1 else ""}</span>' if q else '<span class="badge b-no">No bets</span>'
            mk = " · ".join(f'{m["bet"]} {pct(m["final"])}%' for m in r["markets"])
            cards.append(f'<a href="runs/{run}/report.html" style="text-decoration:none;color:inherit"><div class="card" style="border-left:6px solid {colors(H)[0]}">'
                         f'<div class="mk-top"><div><div class="mk-bet">{esc(cfg.get("title", ""))} · {esc(cfg.get("run_date", ""))}</div>'
                         f'<div class="mk-pick">{A} @ {H}</div></div>{badge}</div><div class="why">{esc(mk)}</div></div></a>')
    body = ('<h1 style="font-size:30px;margin:8px 0 2px">🏈 NFL Bet Research</h1>'
            '<div class="why" style="margin:0 0 16px">Template A game-bet reports. Newest first. Current-season stats only; the book line is the anchor.</div>'
            f'<div class="grid">{"".join(cards) or "<div class=card>No runs yet.</div>"}</div>'
            f'<div class="foot">Updated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</div>')
    open(f"{ROOT}/index.html", "w").write(page("NFL Bet Research", body, back=False))


if __name__ == "__main__":
    run = sys.argv[1].rstrip("/")
    build_run(run)
    build_index()
    print(f"Wrote {run}/report.html and index.html")
