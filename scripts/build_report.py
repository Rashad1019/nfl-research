"""Render runs/<run>/result.json -> runs/<run>/report.html, then rebuild the root index.html.

Usage:
    python3 scripts/build_report.py runs/<run-folder>

AUDIENCE: someone who has never placed a sports bet. The page must say, at the top, exactly what
to do, and every bet must explain in plain English what it is, our chance, the decision, why, and
the numbers behind it (laid out like the chat tables). Jargon goes in the collapsed "details" area.

Pure static HTML + inline CSS/SVG (only external asset: Google Fonts). Phone-first, light/dark.
"""
import glob
import html
import json
import math
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from teams import colors, name  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc = html.escape


def pct(p):
    return int(p * 100 + 0.5)


def r1(x):
    """One decimal, rounded half up (Python's default would show 8.25 as 8.2)."""
    return f"{math.floor(x * 10 + 0.5 + 1e-9) / 10:.1f}"


def odds(o):
    return "—" if o is None else (f"+{o}" if o > 0 else str(o))


def implied(o):
    return abs(o) / (abs(o) + 100) if o < 0 else 100 / (o + 100)


def risk_win(o):
    """Plain-English meaning of an American price."""
    if o is None:
        return ""
    return f"risk ${abs(o)} to win $100" if o < 0 else f"risk $100 to win ${o}"


def nick(t):
    return name(t).split()[-1]  # "Bills", "Rams", "49ers"


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
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:860px;margin:0 auto;padding:16px}
h1,h2,h3,.num{font-family:Oswald,Inter,sans-serif;letter-spacing:.3px}
h2{font-size:21px;margin:30px 0 12px;display:flex;align-items:center;gap:10px}
h2:before{content:"";width:6px;height:22px;border-radius:3px;background:linear-gradient(var(--a),var(--h))}
a{color:var(--info)}
.hero{border-radius:22px;overflow:hidden;box-shadow:var(--shadow);position:relative;color:#fff;
background:linear-gradient(115deg,var(--a1) 0%,var(--a1) 42%,var(--h1) 58%,var(--h1) 100%)}
.hero:after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 20% 0%,rgba(255,255,255,.18),transparent 55%),
linear-gradient(115deg,transparent 46%,rgba(255,255,255,.25) 50%,transparent 54%)}
.hero-in{position:relative;z-index:1;padding:22px 20px 18px}
.stripe{position:relative;z-index:1;display:grid;grid-template-columns:1fr 1fr;height:8px}
.kick{font-size:12px;text-transform:uppercase;letter-spacing:2px;opacity:.9}
.vs{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;margin:14px 0 6px}
.tm{text-align:center}.tm .ab{font:700 46px/1 Oswald,sans-serif}.tm .nm{font-size:13px;opacity:.9}
.tm .rec{display:inline-block;margin-top:6px;font-size:12px;padding:2px 9px;border-radius:99px;background:rgba(0,0,0,.28)}
.at{font:600 18px Oswald,sans-serif;opacity:.8}
.card{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:16px;box-shadow:var(--shadow)}
.todo{border-radius:20px;padding:20px;margin-top:16px;border:2px solid}
.todo.no{background:linear-gradient(135deg,rgba(244,63,94,.16),rgba(244,63,94,.04));border-color:rgba(244,63,94,.55)}
.todo.go{background:linear-gradient(135deg,rgba(34,197,94,.18),rgba(34,197,94,.04));border-color:rgba(34,197,94,.6)}
.todo .lbl{font-size:12px;text-transform:uppercase;letter-spacing:2px;color:var(--mute);font-weight:700}
.todo .big{font:700 32px/1.15 Oswald,sans-serif;margin:4px 0 8px}
.todo.no .big{color:var(--no)}.todo.go .big{color:var(--go)}
.todo p{margin:6px 0}
.steps{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.step{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:12px 14px;font-size:14px}
.step .st{display:block;font:600 16px Oswald,sans-serif;margin-bottom:2px}
.sum{width:100%;border-collapse:separate;border-spacing:0 8px;font-size:15px}
.sum td{background:var(--panel);padding:12px 10px;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.sum td:first-child{border-left:1px solid var(--line);border-radius:12px 0 0 12px}
.sum td:last-child{border-right:1px solid var(--line);border-radius:0 12px 12px 0;text-align:right}
.sum th{font-size:11px;color:var(--mute);text-transform:uppercase;letter-spacing:1px;text-align:left;padding:0 10px}
.sum th:last-child{text-align:right}
.sum .ch{font:700 20px Oswald,sans-serif}
.dec{display:inline-block;font-weight:800;font-size:12px;padding:5px 10px;border-radius:99px;letter-spacing:.6px;white-space:nowrap}
.d-no{background:rgba(244,63,94,.15);color:var(--no)}.d-go{background:rgba(34,197,94,.18);color:var(--go)}
.bet{margin-top:16px;border-left:6px solid var(--no)}.bet.ok{border-left-color:var(--go)}
.bet .hd{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.bet .n{font-size:12px;text-transform:uppercase;letter-spacing:1.5px;color:var(--mute);font-weight:700}
.bet .pick{font:700 24px/1.2 Oswald,sans-serif;margin:2px 0}
.what{background:var(--panel2);border-radius:12px;padding:10px 12px;margin:12px 0;font-size:15px}
.what b{color:var(--info)}
.meter{margin:14px 0 4px}
.mrow{display:flex;justify-content:space-between;font-size:14px;margin-bottom:6px}
.mrow .big{font:700 26px/1 Oswald,sans-serif}
.track{position:relative;height:18px;border-radius:99px;background:var(--track)}
.fill{position:absolute;left:0;top:0;bottom:0;border-radius:99px}
.need{position:absolute;top:-6px;bottom:-6px;border-left:3px solid var(--ink)}
.need span{position:absolute;top:-20px;left:-30px;width:60px;text-align:center;font-size:11px;font-weight:700;color:var(--ink)}
.half50{position:absolute;top:0;bottom:0;border-left:1px dashed var(--mute);opacity:.6}
.scale{display:flex;justify-content:space-between;font-size:11px;color:var(--mute);margin-top:4px}
.why h4,.nums h4{margin:16px 0 6px;font:600 15px Oswald,sans-serif;letter-spacing:.5px;text-transform:uppercase}
.why ul{margin:0;padding:0;list-style:none}
.why li{position:relative;padding:8px 10px 8px 36px;margin:6px 0;border-radius:10px;background:rgba(244,63,94,.07);font-size:15px}
.why li:before{content:"✕";position:absolute;left:12px;top:8px;color:var(--no);font-weight:800}
.why li.okk{background:rgba(34,197,94,.08)}.why li.okk:before{content:"✓";color:var(--go)}
.why li.inf{background:rgba(56,189,248,.09)}.why li.inf:before{content:"i";color:var(--info);font-family:Georgia,serif}
.nums table{width:100%;border-collapse:collapse;font-size:14px}
.nums td{padding:7px 4px;border-bottom:1px solid var(--line);vertical-align:top}
.nums td:last-child{text-align:right;font-weight:700;white-space:nowrap}
.nums tr.tot td{border-top:2px solid var(--ink);font-size:15px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.chip{font-size:13px;padding:4px 9px;border-radius:99px;font-weight:600}
.c-u{background:rgba(34,197,94,.15);color:var(--go)}.c-o{background:rgba(244,63,94,.13);color:var(--no)}
.how{font-size:13px;color:var(--mute);margin-top:12px;border-top:1px dashed var(--line);padding-top:10px}
.grid2{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
ul.clean{margin:0;padding-left:18px}ul.clean li{margin:5px 0}
.tag{font-size:10px;font-weight:800;padding:2px 6px;border-radius:6px;margin-right:6px}
.t-out{background:rgba(244,63,94,.15);color:var(--no)}.t-q{background:rgba(245,158,11,.16);color:var(--warn)}
.t-ok{background:rgba(34,197,94,.15);color:var(--go)}
details{margin-top:14px}summary{cursor:pointer;font:600 17px Oswald,sans-serif;padding:12px 16px;background:var(--panel);
border:1px solid var(--line);border-radius:14px;list-style:none}summary::-webkit-details-marker{display:none}
summary:after{content:" ▸";color:var(--mute)}details[open] summary:after{content:" ▾"}
details>div{margin-top:10px}
table.plain{width:100%;border-collapse:collapse;font-size:13px}
table.plain th,table.plain td{padding:7px 6px;text-align:right;border-bottom:1px solid var(--line)}
table.plain th:first-child,table.plain td:first-child{text-align:left}
table.plain th{color:var(--mute);font-size:11px;text-transform:uppercase;letter-spacing:1px}
.gl dt{font-weight:700;margin-top:10px}.gl dd{margin:2px 0 0;color:var(--mute);font-size:14px}
.foot{color:var(--mute);font-size:12px;margin:28px 0 10px;text-align:center}
@media (max-width:520px){.tm .ab{font-size:38px}.todo .big{font-size:27px}.bet .pick{font-size:21px}.sum{font-size:14px}}
"""

BET_TITLES = {"ML": "Moneyline", "Spread": "Point spread", "O/U": "Total points (over/under)",
              "1H U26.5": "1st-half points under 26.5", "2H U26.5": "2nd-half points under 26.5"}


def is_half(m):
    return m["bet"].startswith(("1H", "2H"))


def cutoff(m):
    return 0.65 if is_half(m) else 0.60


# ---------------- plain-English text ----------------

def what_it_is(m, r):
    A, H = r["away"], r["home"]
    if m["bet"] == "ML":
        t = m["team"]
        return f"You're betting the <b>{esc(name(t))}</b> win the game. Score doesn't matter. Price {odds(m['price'])}: {risk_win(m['price'])}."
    if m["bet"] == "Spread":
        t = m["team"]
        line = float(m["pick"].split()[-1])
        if line > 0:
            return (f"The <b>{esc(name(t))}</b> get a {line:g}-point head start. You win if they <b>win the game, or lose by "
                    f"{math.floor(line)} or fewer</b>. Price {odds(m['price'])}: {risk_win(m['price'])}.")
        return (f"The <b>{esc(name(t))}</b> must <b>win by {math.ceil(-line)} or more</b> points. Price {odds(m['price'])}: {risk_win(m['price'])}.")
    if m["bet"] == "O/U":
        line = float(m["pick"].split()[-1])
        if m["pick"].startswith("Under"):
            return f"You win if <b>both teams combined score {math.floor(line)} or fewer</b> points. Price {odds(m['price'])}: {risk_win(m['price'])}."
        return f"You win if <b>both teams combined score {math.ceil(line)} or more</b> points. Price {odds(m['price'])}: {risk_win(m['price'])}."
    if m["bet"].startswith("1H"):
        return "You win if the <b>score at halftime adds up to 26 or fewer</b> points (both teams combined)."
    return "You win if the <b>points scored in the 3rd and 4th quarters only</b> add up to 26 or fewer (both teams; overtime doesn't count)."


def reasons(m, r):
    """List of (passed?, sentence) explaining the decision, with numbers."""
    out = []
    F, cut = pct(m["final"]), pct(cutoff(m))
    if m["final"] >= cutoff(m):
        out.append((True, f"Our chance is {F}%, at or above the {cut}% we require."))
    else:
        coin = " That's close to a coin flip." if F < 56 else ""
        out.append((False, f"We give it a <b>{F}% chance</b> to win. We only bet at <b>{cut}% or higher</b>, so it's {cut - F} point{'s' if cut - F != 1 else ''} short.{coin}"))
    if is_half(m):
        need_n = math.ceil(0.75 * m["team_games"])
        ok = m["team_count"] >= need_n
        out.append((ok, f"Only <b>{m['team_count']} of these two teams' {m['team_games']} games</b> stayed under 26.5 in this half. We want at least {need_n} of {m['team_games']}."
                    if not ok else f"{m['team_count']} of these two teams' {m['team_games']} games stayed under 26.5 in this half (we want {need_n}+)."))
    else:
        if m["disagree"]:
            out.append((False, f"Our stats say <b>{pct(m['model'])}%</b>, but the sportsbook's odds say <b>{pct(m['fair'])}%</b>. That's a "
                               f"{abs(pct(m['model']) - pct(m['fair']))}-point gap. When we disagree with the sportsbook by more than 10 points, "
                               f"the sportsbook is usually right (it prices in injuries, team quality and more than our stats see), so we stay out."))
        else:
            out.append((True, f"Our stats ({pct(m['model'])}%) and the sportsbook ({pct(m['fair'])}%) are within 10 points of each other."))
        if m["bet"] == "ML" and m.get("dog"):
            out.append((False, "This team is the underdog. Our rules never bet an underdog to win outright."))
    if m["price"] is None:
        out.append(("info",
                    f"We don't have the sportsbook's price for this bet. If you find it, only take <b>{odds(m['need'])} or better</b>."))
    elif "overpriced" in m["blocked_by"]:
        out.append((False, f"The price is too expensive. At {odds(m['price'])} you {risk_win(m['price'])}, which only pays off if it wins "
                           f"<b>{pct(implied(m['price']))}%</b> of the time. We think it wins {F}%. The most we'd pay is <b>{odds(m['need'])}</b>."))
    else:
        out.append((True, f"Price {odds(m['price'])} is at or better than the {odds(m['need'])} we'd need."))
    for b in m["blocked_by"]:
        if b not in ("below 60%", "below 65%", "DISAGREE", "overpriced", "underdog ML", "price not given") and not b.startswith("team count"):
            out.append((False, esc(b)))
    return out


def lead(mm, A, H):
    return f"{nick(H)} by {r1(mm)}" if mm >= 0 else f"{nick(A)} by {r1(-mm)}"


def numbers(m, r, league):
    A, H, p, T = r["away"], r["home"], r["proj"], r["teams"]
    E = {t: T[t]["espn"] for t in T}
    rows = []
    if m["bet"] in ("ML", "Spread"):
        rows += [(f"{nick(A)} average points scored / allowed", f"{r1(E[A]['pf'])} / {r1(E[A]['pa'])}"),
                 (f"{nick(H)} average points scored / allowed", f"{r1(E[H]['pf'])} / {r1(E[H]['pa'])}"),
                 ("Our projected score (season averages)", f"{A} {r1(p['raw']['away'])} – {H} {r1(p['raw']['home'])}"),
                 ("Same, adjusted for opponents' strength", f"{A} {r1(p['adj']['away'])} – {H} {r1(p['adj']['home'])}"),
                 ("Our projected winner, both methods (incl. 1.5 pts home edge)", f"{lead(p['raw']['margin_home'], A, H)} / {lead(p['adj']['margin_home'], A, H)}")]
        if m["bet"] == "ML":
            rows.append(("Sportsbook's chance this team wins", f"{pct(m['fair'])}%"))
            rows.append(("Our stats' chance", f"{pct(m['model'])}%"))
        else:
            sp = r["meta"]["spread"]["home_line"]
            rows.append(("Sportsbook expects", lead(-sp, A, H)))
        tot = None
    elif m["bet"] == "O/U":
        rows += [(f"{nick(A)} average points scored / allowed", f"{r1(E[A]['pf'])} / {r1(E[A]['pa'])}"),
                 (f"{nick(H)} average points scored / allowed", f"{r1(E[H]['pf'])} / {r1(E[H]['pa'])}"),
                 ("Our projected total (season averages)", f"{r1(p['raw']['total'])}"),
                 ("Same, adjusted for opponents' strength", f"{r1(p['adj']['total'])}")]
        tot = ("Sportsbook's line", f"{r['meta']['total']['line']}")
    else:
        k = "h1" if m["bet"].startswith("1H") else "h2"
        word = "1st" if k == "h1" else "2nd"
        ea = (E[A][f"{k}f"] + E[H][f"{k}a"]) / 2
        eh = (E[H][f"{k}f"] + E[A][f"{k}a"]) / 2
        rows += [(f"{nick(A)} score {r1(E[A][k+'f'])} in {word} halves; {nick(H)} allow {r1(E[H][k+'a'])}. Average →", f"{nick(A)} {r1(ea)}"),
                 (f"{nick(H)} score {r1(E[H][k+'f'])} in {word} halves; {nick(A)} allow {r1(E[A][k+'a'])}. Average →", f"{nick(H)} {r1(eh)}")]
        tot = (f"Projected {word}-half total (line is 26.5)", f"{r1(p[k])}")
    html_rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in rows)
    if tot:
        html_rows += f'<tr class="tot"><td>{esc(tot[0])}</td><td>{esc(tot[1])}</td></tr>'
    extra = ""
    if is_half(m):
        k = "h1" if m["bet"].startswith("1H") else "h2"
        for t in (A, H):
            chips = "".join(
                f'<span class="chip {"c-u" if g[k+"f"] + g[k+"a"] < 26.5 else "c-o"}">{"vs" if g["home"] else "@"} {g["opp"]}: '
                f'{g[k+"f"] + g[k+"a"]:g} {"✓" if g[k+"f"] + g[k+"a"] < 26.5 else "✕"}</span>' for g in T[t]["log"])
            extra += f'<div style="font-size:14px;margin-top:10px"><b>{nick(t)} games this season</b> ({word_half(k)} total points):</div><div class="chips">{chips}</div>'
        rate, under, n = league[f"{k}_rate"], league[f"{k}_under"], league["games"]
        extra += f'<div style="font-size:14px;color:var(--mute)">Whole NFL this season: {under} of {n} games ({pct(rate)}%) stayed under 26.5 in the {word_half(k)}.</div>'
    return f'<div class="nums"><h4>The numbers behind it</h4><table>{html_rows}</table>{extra}</div>'


def word_half(k):
    return "1st half" if k == "h1" else "2nd half"


def how_we_got(m):
    F = pct(m["final"])
    if is_half(m):
        return (f"How we got {F}%: our stats say {pct(m['model'])}%, and {pct(m['league'])}% of NFL games this season stayed under. "
                f"We average the two.")
    return (f"How we got {F}%: the sportsbook's odds say {pct(m['fair'])}%, our stats say {pct(m['model'])}%. "
            f"We start from the sportsbook and move a quarter of the way toward our stats, because the sportsbook is usually the better estimate.")


def meter(m):
    F, cut = m["final"], cutoff(m)
    col = "#22c55e" if m["qualifies"] else ("#f59e0b" if F >= cut - 0.05 else "#f43f5e")
    return f"""<div class="meter"><div class="mrow"><span>Our chance this bet wins</span><span class="big" style="color:{col}">{pct(F)}%</span></div>
<div class="track"><div class="fill" style="width:{r1(F*100)}%;background:linear-gradient(90deg,{col}55,{col})"></div>
<div class="half50" style="left:50%"></div><div class="need" style="left:{cut*100:.0f}%"><span>need {pct(cut)}%</span></div></div>
<div class="scale"><span>0%</span><span>50% = coin flip</span><span>100%</span></div></div>"""


def bet_card(i, m, r, league):
    ok = m["qualifies"]
    dec = '<span class="dec d-go">✓ BET IT</span>' if ok else '<span class="dec d-no">✕ DON\'T BET</span>'
    rs = reasons(m, r)
    cls = {True: "okk", False: "", "info": "inf"}
    lis = "".join(f'<li class="{cls[good]}">{txt}</li>' for good, txt in rs)
    head = "Why it passes" if ok else "Why we're not betting it"
    action = (f'<div class="what" style="border:1px solid rgba(34,197,94,.5)"><b>What to do:</b> bet it, but only at a price of <b>{odds(m["need"])} or better</b>.</div>' if ok else "")
    return f"""<div class="card bet{' ok' if ok else ''}">
<div class="hd"><div><div class="n">Bet {i} · {esc(BET_TITLES.get(m['bet'], m['bet']))}</div><div class="pick">{esc(m['pick'])}</div></div>{dec}</div>
<div class="what"><b>What this bet means:</b> {what_it_is(m, r)}</div>
{meter(m)}{action}
<div class="why"><h4>{head}</h4><ul>{lis}</ul></div>
{numbers(m, r, league)}
<div class="how">{esc(how_we_got(m))}</div>
</div>"""


def inj_list(items):
    li = []
    for x in items:
        t = x.split(":")[0].strip().upper()
        cls = "t-out" if t in ("OUT", "IR") else ("t-ok" if t.startswith("CLEAR") else "t-q")
        lbl = {"IR": "OUT (IR)", "Q": "MAYBE"}.get(t, t)
        li.append(f'<li><span class="tag {cls}">{esc(lbl)}</span>{esc(x.split(":", 1)[1].strip() if ":" in x else x)}</li>')
    return '<ul class="clean" style="list-style:none;padding:0">' + "".join(li) + "</ul>"


def game_section(r, league):
    A, H = r["away"], r["home"]
    acc_a, acc_h = team_accents(A, H)
    meta, T = r["meta"], r["teams"]
    rec = lambda t: T[t]["trends"]["tr_moneyline"].get("Win/Loss", "")
    mk = r["markets"]
    bets = [m for m in mk if m["qualifies"]]
    if bets:
        todo = (f'<div class="todo go"><div class="lbl">What to do</div><div class="big">Bet {len(bets)} of the 5</div>'
                + "".join(f'<p>✅ <b>{esc(m["pick"])}</b> ({esc(BET_TITLES[m["bet"]])}): only at <b>{odds(m["need"])} or better</b>.</p>' for m in bets)
                + '<p>Skip everything else on this game. Each bet below says why.</p></div>')
    else:
        near = max(mk, key=lambda m: m["final"] - cutoff(m))
        todo = (f'<div class="todo no"><div class="lbl">What to do</div><div class="big">Don\'t bet this game.</div>'
                f'<p>We checked all 5 common bets on {nick(A)} at {nick(H)}. <b>None passed our rules.</b> They\'re all too close to a coin flip, '
                f'or our numbers fight the sportsbook\'s too much to trust.</p>'
                f'<p>The closest was <b>{esc(near["pick"])}</b> ({esc(BET_TITLES[near["bet"]])}) at {pct(near["final"])}%, still short of the {pct(cutoff(near))}% we require.</p>'
                f'<p style="color:var(--mute);font-size:14px">Skipping is a good result: it keeps money off bets that aren\'t clearly in your favor.</p></div>')
    badge = {True: '<span class="dec d-go">✓ BET</span>', False: '<span class="dec d-no">✕ SKIP</span>'}
    rows = "".join(
        f'<tr><td><b>{esc(BET_TITLES[m["bet"]].split(" (")[0])}</b><br><span style="color:var(--mute);font-size:13px">{esc(m["pick"])}</span></td>'
        f'<td class="ch" style="color:{"var(--go)" if m["qualifies"] else "var(--ink)"}">{pct(m["final"])}%</td>'
        f'<td style="color:var(--mute);font-size:13px">need {pct(cutoff(m))}%</td>'
        f'<td>{badge[m["qualifies"]]}</td></tr>' for m in mk)
    cards = "".join(bet_card(i, m, r, league) for i, m in enumerate(mk, 1))
    sp, to = meta["spread"], meta["total"]
    return f"""
<section class="hero" style="--a1:{colors(A)[0]};--h1:{colors(H)[0]}"><div class="hero-in">
 <div class="kick">{esc(meta.get('kickoff', ''))}</div>
 <div class="vs"><div class="tm"><div class="ab">{A}</div><div class="nm">{esc(name(A))}</div><div class="rec">{esc(rec(A))}</div></div>
 <div class="at">@</div>
 <div class="tm"><div class="ab">{H}</div><div class="nm">{esc(name(H))}</div><div class="rec">{esc(rec(H))}</div></div></div>
 <div style="text-align:center;font-size:13px;opacity:.9">{esc(meta.get('venue', ''))}</div>
</div><div class="stripe"><span style="background:{colors(A)[1]}"></span><span style="background:{colors(H)[1]}"></span></div></section>
{todo}

<h2>How to read this page</h2>
<div class="steps">
 <div class="step"><span class="st">1 · Our chance</span>Every bet gets a chance of winning, from 0% to 100%. 50% is a coin flip.</div>
 <div class="step"><span class="st">2 · The bar to clear</span>We only bet at <b>60%+</b> (<b>65%+</b> for half bets). The black line on each meter marks it.</div>
 <div class="step"><span class="st">3 · Extra checks</span>Our stats can't fight the sportsbook by more than 10 points, and the price can't be too expensive.</div>
 <div class="step"><span class="st">4 · Decision</span><span style="color:var(--go);font-weight:700">Green ✓ = bet it.</span> <span style="color:var(--no);font-weight:700">Red ✕ = skip it</span>, and the card says why.</div>
</div>

<h2>The 5 bets at a glance</h2>
<table class="sum"><tr><th>Bet</th><th>Chance</th><th></th><th>Decision</th></tr>{rows}</table>

<h2>Each bet, explained</h2>
{cards}

<h2>Odds in 10 seconds</h2>
<div class="card"><ul class="clean">
 <li><b>A minus number (−176)</b> is the favorite: you risk $176 to win $100 (you get $276 back if it wins).</li>
 <li><b>A plus number (+148)</b> is the underdog: you risk $100 to win $148.</li>
 <li><b>−110 / −115</b> on spreads and totals: risk about $110–115 to win $100. That extra cost is the sportsbook's cut.</li>
 <li><b>Sportsbook's line here:</b> {esc(nick(H))} favored by {-sp['home_line']:g}; total {to['line']}; moneyline {A} {odds(meta['ml']['away'])} / {H} {odds(meta['ml']['home'])}.</li>
</ul></div>

<h2>Things that could change this</h2>
<div class="grid2">
 <div class="card"><h3 style="margin:0 0 8px;color:{acc_a}">{esc(name(A))} injuries</h3>{inj_list(meta.get('injuries', {}).get(A, []))}</div>
 <div class="card"><h3 style="margin:0 0 8px;color:{acc_h}">{esc(name(H))} injuries</h3>{inj_list(meta.get('injuries', {}).get(H, []))}</div>
</div>
<div class="card" style="margin-top:12px"><ul class="clean">
 <li><b>Quarterbacks:</b> {esc(meta.get('qbs', '—'))}</li>
 <li><b>Line movement:</b> {esc(meta.get('line_move', '—'))}</li>
 <li><b>Weather:</b> {esc(meta.get('weather', '—'))}</li>
 <li><b>Final injury news</b> comes out about 90 minutes before kickoff. If a starting QB is suddenly out, everything here is void.</li>
</ul></div>
{details_section(r)}
"""


def details_section(r):
    A, H, T, p, meta = r["away"], r["home"], r["teams"], r["proj"], r["meta"]
    logs = ""
    for t in (A, H):
        rows = "".join(f'<tr><td>Wk {g["wk"]} {"vs" if g["home"] else "@"} {g["opp"]}</td><td>{g["pf"]}–{g["pa"]}</td>'
                       f'<td>{g["h1f"]:g}–{g["h1a"]:g}</td><td>{g["h2f"]:g}–{g["h2a"]:g}</td></tr>' for g in T[t]["log"])
        e, s = T[t]["espn"], T[t]["statrankings"]
        logs += (f'<div class="card"><h3 style="margin:0 0 6px">{esc(name(t))} game by game</h3><table class="plain">'
                 f'<tr><th>Game</th><th>Final</th><th>1st half</th><th>2nd half</th></tr>{rows}'
                 f'<tr><td><b>Average</b></td><td>{r1(e["pf"])}–{r1(e["pa"])}</td><td>{r1(e["h1f"])}–{r1(e["h1a"])}</td><td>{r1(e["h2f"])}–{r1(e["h2a"])}</td></tr>'
                 f'<tr><td style="color:var(--mute)">StatRankings check</td><td>{s["pf"]}–{s["pa"]}</td><td>{s["h1f"]}–{s["h1a"]}</td><td>{s["h2f"]}–{s["h2a"]}</td></tr></table>'
                 f'<div style="font-size:12px;color:var(--mute);margin-top:6px">Scores shown as {t}–opponent.</div></div>')
    ep = lambda t, s: T[t]["epa"][s]
    tape = (f'<table class="plain"><tr><th>Stat</th><th>{A}</th><th>{H}</th></tr>'
            f'<tr><td>Offense EPA/play (higher = better; rank)</td><td>{ep(A,"off")["epa"]:+.3f} (#{ep(A,"off")["rank"]})</td><td>{ep(H,"off")["epa"]:+.3f} (#{ep(H,"off")["rank"]})</td></tr>'
            f'<tr><td>Defense EPA/play (lower = better; rank)</td><td>{ep(A,"def")["epa"]:+.3f} (#{ep(A,"def")["rank"]})</td><td>{ep(H,"def")["epa"]:+.3f} (#{ep(H,"def")["rank"]})</td></tr>'
            + "".join(f'<tr><td>{lbl}</td><td>{esc(str(T[A]["stats"][k]))}</td><td>{esc(str(T[H]["stats"][k]))}</td></tr>' for lbl, k in (
                ("Yards per play", "ypp"), ("Yards per play allowed", "opp_ypp"), ("Pass yards per attempt allowed", "opp_ypa"),
                ("3rd-down conversion %", "third"), ("Pressure rate (defense)", "pressure"), ("Plays per game", "plays"),
                ("Turnover margin per game", "to_margin")))
            + '</table><div style="font-size:12px;color:var(--mute);margin-top:6px">EPA = expected points added per play vs an average team (derived from nflverse play-by-play).</div>')
    situ = "".join(f"<li>{esc(x)}</li>" for x in meta.get("situation", []))
    return f"""
<details><summary>More detail (for the curious)</summary><div>
<div class="grid2">{logs}</div>
<div class="card" style="margin-top:12px"><h3 style="margin:0 0 6px">Team comparison</h3>{tape}</div>
<div class="card" style="margin-top:12px"><h3 style="margin:0 0 6px">Game situation</h3><ul class="clean">{situ}
<li>Opening line: {esc(meta.get('opening', '—'))}</li><li>Where the lines came from: {esc(meta.get('lines_source', '—'))}</li></ul></div>
</div></details>"""


GLOSSARY = [
    ("Moneyline", "Bet on who wins the game. Nothing else matters."),
    ("Point spread", "The favorite has to win by more than the line; the underdog can lose by less than it and still win you the bet."),
    ("Total (over/under)", "Bet on whether both teams' combined points go over or under a number."),
    ("Half bets", "Same idea, counting only the points scored in the 1st half (or only the 2nd half)."),
    ("Sportsbook's chance", "What the odds say the chance is, with the sportsbook's cut removed."),
    ("Our stats' chance", "What this season's scoring numbers alone say."),
    ("Our chance", "The number we decide on: mostly the sportsbook's chance, nudged a quarter of the way toward our stats."),
    ("Need price", "The worst odds still worth taking. Anything more expensive is a bad deal even if you think it wins."),
]


FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
           "%3Ctext y='.9em' font-size='90'%3E%F0%9F%8F%88%3C/text%3E%3C/svg%3E")  # 🏈, inline so no /favicon.ico 404


def page(title, body, accents=("#38bdf8", "#a78bfa"), back=True,
         desc="Plain-English NFL bet checks: whether to bet each game, and why."):
    nav = '<a href="../../index.html" style="font-size:14px">← All games</a>' if back else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta name="theme-color" content="#0b1020"><link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body style="--a:{accents[0]};--h:{accents[1]}"><div class="wrap">{nav}{body}</div></body></html>"""


def build_run(run):
    res = json.load(open(f"{run}/result.json"))
    cfg, league = res["config"], res["league"]
    body = f'<h1 style="font-size:24px;margin:10px 0 14px">NFL Bet Check <span style="color:var(--mute);font-weight:500">· {esc(cfg.get("title", ""))}</span></h1>'
    for r in res["games"]:
        body += game_section(r, league)
    if res["parlays"]:
        body += "<h2>Parlays (two bets combined)</h2><div class='card'><ul class='clean'>" + "".join(
            f'<li>{esc(" + ".join(p["legs"]))}: both win {pct(p["combined"])}% of the time</li>' for p in res["parlays"]) + "</ul></div>"
    gl = "".join(f"<dt>{esc(a)}</dt><dd>{esc(b)}</dd>" for a, b in GLOSSARY)
    body += f"""
<details><summary>Words used on this page</summary><div class="card"><dl class="gl">{gl}</dl></div></details>
<details><summary>What we couldn't check · sources</summary><div class="card">
<ul class="clean">{''.join(f'<li>{esc(x)}</li>' for x in cfg.get('not_checked', []))}</ul>
<h3 style="margin:14px 0 6px">Sources</h3><ul class="clean">{''.join(f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for t, u in cfg.get('sources', []))}</ul></div></details>
<div class="foot">Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · Research date {esc(cfg.get('run_date', ''))}<br>
This is research, not a guarantee. Never bet money you can't afford to lose.</div>"""
    g0 = res["games"][0]
    title = " · ".join(f'{r["away"]} @ {r["home"]}' for r in res["games"])
    open(f"{run}/report.html", "w").write(page(f"{title} Bet Check", body, team_accents(g0["away"], g0["home"])))


INDEX_CSS = """
.top{border-radius:22px;padding:22px 20px;color:#fff;box-shadow:var(--shadow);position:relative;overflow:hidden;
background:linear-gradient(120deg,#1d4ed8 0%,#7c3aed 55%,#db2777 100%)}
.top:after{content:"";position:absolute;right:-40px;top:-40px;width:180px;height:180px;border-radius:50%;background:rgba(255,255,255,.12)}
.top h1{margin:0;font-size:32px;line-height:1.1}.top p{margin:8px 0 0;opacity:.92;max-width:520px}
.gcard{display:block;text-decoration:none;color:inherit;margin-bottom:14px;transition:transform .15s}
.gcard:hover{transform:translateY(-2px)}
.gcard .card{border-left:6px solid var(--tc);padding:0;overflow:hidden}
.gband{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;color:#fff;
background:linear-gradient(110deg,var(--ac) 0%,var(--ac) 45%,var(--hc) 55%,var(--hc) 100%)}
.gband b{font:700 30px/1 Oswald,sans-serif}.gband span{font-size:12px;opacity:.9}
.gbody{padding:14px 16px}
.mini{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin:12px 0 4px}
.mini div{border-radius:10px;padding:6px 4px;text-align:center;font-size:11px;line-height:1.25}
.mini b{display:block;font:700 17px Oswald,sans-serif}
.m-go{background:rgba(34,197,94,.16);color:var(--go)}.m-no{background:var(--panel2);color:var(--mute)}
.cta{display:inline-block;margin-top:10px;font-weight:700;color:var(--info)}
"""

SHORT = {"ML": "Winner", "Spread": "Spread", "O/U": "Total", "1H U26.5": "1st half", "2H U26.5": "2nd half"}


def build_index():
    cards = []
    for rj in sorted(glob.glob(f"{ROOT}/runs/*/result.json"), reverse=True):
        run = os.path.basename(os.path.dirname(rj))
        res = json.load(open(rj))
        cfg = res["config"]
        for r in res["games"]:
            A, H = r["away"], r["home"]
            q = [m for m in r["markets"] if m["qualifies"]]
            if q:
                verdict = f'<div style="color:var(--go);font:700 23px Oswald,sans-serif">✅ Bet {len(q)}: {esc(", ".join(m["pick"] for m in q))}</div>'
            else:
                verdict = '<div style="color:var(--no);font:700 23px Oswald,sans-serif">🛑 Don\'t bet this game</div>'
            mini = "".join(f'<div class="{"m-go" if m["qualifies"] else "m-no"}">{SHORT.get(m["bet"], m["bet"])}<b>{pct(m["final"])}%</b>{"✓ bet" if m["qualifies"] else "✕ skip"}</div>'
                           for m in r["markets"])
            cards.append(
                f'<a class="gcard" href="runs/{run}/report.html" style="--tc:{colors(H)[1]};--ac:{colors(A)[0]};--hc:{colors(H)[0]}"><div class="card">'
                f'<div class="gband"><div><b>{A}</b> <span>at</span> <b>{H}</b></div><span>{esc(r["meta"].get("kickoff", ""))}</span></div>'
                f'<div class="gbody"><div style="font-size:12px;color:var(--mute);text-transform:uppercase;letter-spacing:1.5px">{esc(cfg.get("title", ""))}</div>'
                f'<div style="font:600 19px Oswald,sans-serif;margin:2px 0 6px">{esc(name(A))} at {esc(name(H))}</div>{verdict}'
                f'<div class="mini">{mini}</div>'
                f'<div style="font-size:14px;color:var(--mute)">{len(q)} of 5 bets passed our checks. Percent = our chance the bet wins.</div>'
                f'<span class="cta">See every bet explained →</span></div></div></a>')
    n = len(cards)
    body = (f'<style>{INDEX_CSS}</style>'
            '<div class="top"><h1>🏈 NFL Bet Check</h1>'
            '<p>Before you bet an NFL game, check here. Each game gets a plain answer, <b>bet</b> or <b>don\'t bet</b>, and a page that explains why in everyday words.</p></div>'
            '<h2>How it works</h2><div class="steps">'
            '<div class="step"><span class="st">1 · We crunch the numbers</span>This season\'s scoring for both teams, compared with the sportsbook\'s odds.</div>'
            '<div class="step"><span class="st">2 · Each bet gets a chance</span>From 0% to 100%. 50% is a coin flip.</div>'
            '<div class="step"><span class="st">3 · Strict cutoff</span>We only say "bet" at 60%+ (65%+ for half bets), with a fair price. Otherwise: skip.</div></div>'
            f'<h2>Games ({n})</h2>'
            f'{"".join(cards) or "<div class=card>No games yet.</div>"}'
            f'<div class="foot">Updated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} · Research, not a guarantee. Never bet money you can\'t afford to lose.</div>')
    open(f"{ROOT}/index.html", "w").write(page("NFL Bet Check", body, back=False))


if __name__ == "__main__":
    run = sys.argv[1].rstrip("/")
    build_run(run)
    build_index()
    print(f"Wrote {run}/report.html and index.html")
