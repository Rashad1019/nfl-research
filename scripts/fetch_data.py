"""Download and parse every input Template A needs into runs/<run>/data/.

Usage:
    python3 scripts/fetch_data.py runs/<run-folder>

Reads runs/<run>/config.json (season, week, games) and writes:
    data/sr_data.json            StatRankings team tables (all 32 teams, every column)
    data/espn/wk<N>.json         ESPN scoreboards, weeks 1..week (quarter line scores)
    data/espn/summary_<A>-<H>.json  ESPN game summary: DraftKings odds, injuries, venue, weather
    data/espn/g_<id>.json        ESPN box scores for both teams' completed games (QB starters)
    data/epa.json                EPA/play + success rate, all teams (derived from nflverse pbp)

Why ESPN/nflverse: footballdb.com and pro-football-reference.com return HTTP 403 to
scripts and WebFetch; rbsdm.com is a JS-only app. See CLAUDE.md "Source fallbacks".
"""
import csv
import gzip
import html as H
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# key -> StatRankings path under /nfl/teams/  (the exact links from the skill)
SR_PAGES = {
    "h1_off": "offense-by-quarter/1st-half-points-per-game",
    "h1_def": "defense-by-quarter/opponent-1st-half-points-per-game",
    "h2_off": "offense-by-quarter/2nd-half-points-per-game",
    "h2_def": "defense-by-quarter/opponent-2nd-half-points-per-game",
    "h1_top": "offense-by-quarter/1st-half-time-of-possession-percent",
    "ppg": "scoring-offense/points-per-game",
    "papg": "scoring-defense/opponent-offensive-points-per-game-estimated",
    "opp_ppg": "scoring-defense/opponent-points-per-game",
    "margin": "scoring-offense/average-scoring-margin",
    "ppp": "scoring-offense/points-per-play",
    "opp_ppp": "scoring-defense/opponent-points-per-play",
    "plays": "offense/plays-per-game",
    "opp_plays": "defense/opponent-plays-per-game",
    "spp": "offense/seconds-per-play",
    "top": "offense/average-time-of-possession-excluding-ot",
    "ypp": "offense/yards-per-play",
    "opp_ypp": "defense/opponent-yards-per-play",
    "third": "offense/third-down-conversion-percentage",
    "opp_third": "defense/opponent-third-down-conversion-percentage",
    "opp_rztd": "scoring-defense/opponent-red-zone-scoring-percentage-td-only",
    "opp_rztrips": "scoring-defense/opponent-red-zone-scoring-attempts-per-game",
    "fga": "special-teams-offense/field-goal-attempts-per-game",
    "opp_ypa": "passing-defense/opponent-yards-per-pass-attempt",
    "pressure": "passing-defense/pressure-rate",
    "to_margin": "turnovers/turnover-margin-per-game",
    "pen": "penalties/penalties-per-game",
}
SR_TRENDS = {"tr_moneyline": "moneyline", "tr_ats": "ats", "tr_totals": "totals"}


def get(url, tries=5):
    """GET with backoff. StatRankings returns 429 if pages are requested back-to-back."""
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 0) or 15 * (i + 1))


def parse_sr(page):
    """StatRankings table -> {full team name: {column header: cell text}}.
    Team names live only in the logo's data-tooltip attribute."""
    i = page.find("<tbody")
    head = page[page.find("<thead"):i]
    body = page[i:page.find("</table>", i)]
    clean = lambda s: re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
    hdr = [clean(x).split(">")[-1].strip() for x in re.findall(r"<th[^>]*>(.*?)</th>", head, re.S)]
    out = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        m = re.search(r'data-tooltip="([^"]+)"', row)
        if m:
            out[m.group(1)] = dict(zip(hdr, [clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]))
    return out


def fetch_statrankings(data):
    sr, failed = {}, []
    pages = {k: f"https://www.statrankings.com/nfl/teams/{p}" for k, p in SR_PAGES.items()}
    pages.update({k: f"https://www.statrankings.com/nfl/trends/{p}" for k, p in SR_TRENDS.items()})
    for k, url in pages.items():
        time.sleep(3)  # be polite; avoids 429s
        try:
            sr[k] = parse_sr(get(url).decode())
            assert len(sr[k]) == 32, f"{len(sr[k])} teams"
        except Exception as e:  # rule 8: never skip silently
            failed.append(f"{k}: {url} -> {e}")
    json.dump(sr, open(f"{data}/sr_data.json", "w"), indent=1)
    return failed


def fetch_espn(data, season, week, games):
    os.makedirs(f"{data}/espn", exist_ok=True)
    base = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    events = []
    for w in range(1, week + 1):
        sb = json.loads(get(f"{base}/scoreboard?dates={season}&seasontype=2&week={w}"))
        json.dump(sb, open(f"{data}/espn/wk{w}.json", "w"))
        events += sb["events"]
    wanted = {t for g in games for t in (g["away"], g["home"])}
    for e in events:
        c = e["competitions"][0]
        teams = {t["homeAway"]: t["team"]["abbreviation"] for t in c["competitors"]}
        if not wanted & set(teams.values()):
            continue
        if c["status"]["type"]["name"] == "STATUS_FINAL":
            json.dump(json.loads(get(f"{base}/summary?event={e['id']}")), open(f"{data}/espn/g_{e['id']}.json", "w"))
        for g in games:
            if teams == {"away": g["away"], "home": g["home"]} and c["status"]["type"]["name"] != "STATUS_FINAL":
                json.dump(json.loads(get(f"{base}/summary?event={e['id']}")),
                          open(f"{data}/espn/summary_{g['away']}-{g['home']}.json", "w"))


def fetch_epa(data, season):
    """EPA/play and success rate on offense and defense (pass + run plays, regular season)."""
    url = f"https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.csv.gz"
    rows = csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(get(url)))))
    acc = {"off": defaultdict(lambda: [0, 0.0, 0]), "def": defaultdict(lambda: [0, 0.0, 0])}
    for x in rows:
        if x["season_type"] != "REG" or x["play_type"] not in ("pass", "run") or x["epa"] in ("", "NA"):
            continue
        e = float(x["epa"])
        for side, team in (("off", x["posteam"]), ("def", x["defteam"])):
            a = acc[side][team]
            a[0] += 1; a[1] += e; a[2] += e > 0
    out = {}
    for side, d in acc.items():
        order = sorted(d, key=lambda t: d[t][1] / d[t][0], reverse=(side == "off"))  # rank 1 = best
        for t, (n, s, w) in d.items():
            out.setdefault(t, {})[side] = {"plays": n, "epa": s / n, "sr": w / n, "rank": order.index(t) + 1}
    json.dump({"source": url, "teams": out}, open(f"{data}/epa.json", "w"), indent=1)


if __name__ == "__main__":
    run = sys.argv[1].rstrip("/")
    cfg = json.load(open(f"{run}/config.json"))
    data = f"{run}/data"
    os.makedirs(data, exist_ok=True)
    failed = fetch_statrankings(data)
    fetch_espn(data, cfg["season"], cfg["week"], cfg["games"])
    try:
        fetch_epa(data, cfg["season"])
    except Exception as e:
        failed.append(f"nflverse pbp -> {e}")
    print("FAILED:\n  " + "\n  ".join(failed) if failed else "All sources loaded.")
