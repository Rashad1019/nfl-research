"""Template A model (game bets). Implements Step 4 + Step 5 of the nfl-bet-research skill exactly.

Usage:
    python3 scripts/template_a.py runs/<run-folder>

Reads  runs/<run>/config.json + runs/<run>/data/*   (see fetch_data.py)
Writes runs/<run>/result.json and prints an audit trail of every number.

Data choices (documented in CLAUDE.md):
  * Team points / half points come from ESPN game-by-game line scores (OT excluded from 2H).
    They are printed next to StatRankings so disagreements are visible. ESPN is used because
    bets grade on actual points; StatRankings' defense-by-half pages drop non-offensive scores.
  * Schedule adjustment uses StatRankings ppg / opponent-points-per-game for all 32 teams.
"""
import json
import math
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from teams import name, nflverse  # noqa: E402

PHI = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
HFA = 1.5
SD = {"ml": 13.3, "total": 13.5, "h1": 10.0, "h2": 10.5}


def pct(p):  # whole-percent rounding, half up
    return int(p * 100 + 0.5)


def implied(o):
    return abs(o) / (abs(o) + 100) if o < 0 else 100 / (o + 100)


def fair(a, b):
    ia, ib = implied(a), implied(b)
    return ia / (ia + ib), ib / (ia + ib)


def need_price(p):
    return round(-100 * p / (1 - p)) if p >= 0.5 else round(100 * (1 - p) / p)


def fmt_odds(o):
    return f"+{o}" if o > 0 else str(o)


def price_ok(book, final):
    """Book price at or better than need <=> the book's implied chance is no higher than ours."""
    return implied(book) <= final + 1e-12


def load(run):
    cfg = json.load(open(f"{run}/config.json"))
    sr = json.load(open(f"{run}/data/sr_data.json"))
    epa = json.load(open(f"{run}/data/epa.json"))["teams"]
    games = []
    for w in range(1, cfg["week"] + 1):
        for e in json.load(open(f"{run}/data/espn/wk{w}.json"))["events"]:
            c = e["competitions"][0]
            if c["status"]["type"]["name"] != "STATUS_FINAL":
                continue
            side = {t["homeAway"]: (t["team"]["abbreviation"], [v["value"] for v in t["linescores"]], int(t["score"]))
                    for t in c["competitors"]}
            games.append((w, side["away"], side["home"]))
    return cfg, sr, epa, games


def team_log(games, team):
    rows = []
    for w, a, h in games:
        for me, op in ((a, h), (h, a)):
            if me[0] == team:
                q, o = me[1], op[1]
                rows.append({"wk": w, "opp": op[0], "home": me is h, "pf": me[2], "pa": op[2],
                             "h1f": q[0] + q[1], "h1a": o[0] + o[1], "h2f": q[2] + q[3], "h2a": o[2] + o[3],
                             "ot": len(q) > 4})
    return rows


def avg(rows, k):
    return sum(r[k] for r in rows) / len(rows)


def run_game(g, cfg, sr, epa, games, league):
    A, H = g["away"], g["home"]
    srv = lambda key, t: float(sr[key][name(t)][str(cfg["season"])].rstrip("%"))
    out = {"away": A, "home": H, "meta": {k: v for k, v in g.items() if k not in ("away", "home")}, "teams": {}}
    logs = {t: team_log(games, t) for t in (A, H)}
    for t in (A, H):
        L = logs[t]
        out["teams"][t] = {
            "games": len(L), "low_confidence": len(L) < 4, "log": L,
            "espn": {k: avg(L, k) for k in ("pf", "pa", "h1f", "h1a", "h2f", "h2a")},
            "statrankings": {"pf": srv("ppg", t), "pa": srv("opp_ppg", t), "pa_est_off": srv("papg", t),
                             "h1f": srv("h1_off", t), "h1a": srv("h1_def", t), "h2f": srv("h2_off", t), "h2a": srv("h2_def", t)},
            "h1_under": sum(r["h1f"] + r["h1a"] < 26.5 for r in L),
            "h2_under": sum(r["h2f"] + r["h2a"] < 26.5 for r in L),
            "epa": epa.get(nflverse(t)),
            "stats": {k: sr[k][name(t)].get(str(cfg["season"])) for k in
                      ("ypp", "opp_ypp", "plays", "spp", "top", "third", "opp_third", "opp_rztd", "opp_ypa",
                       "pressure", "to_margin", "pen", "h1_top")},
            "trends": {k: sr[k][name(t)] for k in ("tr_moneyline", "tr_ats", "tr_totals")},
        }
    T = out["teams"]
    E = {t: T[t]["espn"] for t in T}
    hfa = 0 if g.get("neutral") else HFA

    # 4b RAW
    a_raw, h_raw = (E[A]["pf"] + E[H]["pa"]) / 2, (E[H]["pf"] + E[A]["pa"]) / 2
    # 4c ADJ
    lg = sum(float(v[str(cfg["season"])]) for v in sr["ppg"].values()) / 32
    adj = {}
    for t in (A, H):
        opps = [r["opp"] for r in logs[t]]
        opp_pa = sum(srv("opp_ppg", o) for o in opps) / len(opps)
        opp_pf = sum(srv("ppg", o) for o in opps) / len(opps)
        adj[t] = {"opps": opps, "opp_avg_pa": opp_pa, "opp_avg_pf": opp_pf,
                  "adj_off": E[t]["pf"] - (opp_pa - lg), "adj_def": E[t]["pa"] - (opp_pf - lg)}
    a_adj, h_adj = (adj[A]["adj_off"] + adj[H]["adj_def"]) / 2, (adj[H]["adj_off"] + adj[A]["adj_def"]) / 2
    proj = {
        "league_avg_ppg": lg,
        "raw": {"away": a_raw, "home": h_raw, "margin_home": h_raw - a_raw + hfa, "total": a_raw + h_raw},
        "adj": {"away": a_adj, "home": h_adj, "margin_home": h_adj - a_adj + hfa, "total": a_adj + h_adj},
        "schedule": adj,
    }
    # 4d halves
    proj["h1"] = (E[A]["h1f"] + E[H]["h1a"]) / 2 + (E[H]["h1f"] + E[A]["h1a"]) / 2
    proj["h2"] = (E[A]["h2f"] + E[H]["h2a"]) / 2 + (E[H]["h2f"] + E[A]["h2a"]) / 2
    out["proj"] = proj
    mr, ma = proj["raw"]["margin_home"], proj["adj"]["margin_home"]
    tr, ta = proj["raw"]["total"], proj["adj"]["total"]

    # 4e-4g full-game markets: compute both sides, pick the higher Final
    mk = []

    def market(bet, sides):
        best = max(sides, key=lambda s: s["final"])
        for s in sides:
            s["disagree"] = abs(s["model"] - s["fair"]) > 0.10
        best["bet"] = bet
        best["need"] = need_price(best["final"])
        best["other"] = [s for s in sides if s is not best][0]
        mk.append(best)

    ml = g["ml"]
    f_h, f_a = fair(ml["home"], ml["away"])
    m_h = (PHI(mr / SD["ml"]) + PHI(ma / SD["ml"])) / 2
    market("ML", [
        {"pick": f"{H} {fmt_odds(ml['home'])}", "team": H, "price": ml["home"], "model": m_h, "fair": f_h,
         "final": f_h + 0.25 * (m_h - f_h), "dog": ml["home"] > 0},
        {"pick": f"{A} {fmt_odds(ml['away'])}", "team": A, "price": ml["away"], "model": 1 - m_h, "fair": f_a,
         "final": f_a + 0.25 * ((1 - m_h) - f_a), "dog": ml["away"] > 0}])

    sp = g["spread"]
    hl = sp["home_line"]
    fs_h, fs_a = fair(sp["home_price"], sp["away_price"])
    s_h = (PHI((mr + hl) / SD["ml"]) + PHI((ma + hl) / SD["ml"])) / 2
    s_a = (PHI((-mr - hl) / SD["ml"]) + PHI((-ma - hl) / SD["ml"])) / 2
    market("Spread", [
        {"pick": f"{H} {hl:+g}", "team": H, "price": sp["home_price"], "model": s_h, "fair": fs_h, "final": fs_h + 0.25 * (s_h - fs_h)},
        {"pick": f"{A} {-hl:+g}", "team": A, "price": sp["away_price"], "model": s_a, "fair": fs_a, "final": fs_a + 0.25 * (s_a - fs_a)}])

    to = g["total"]
    fo, fu = fair(to["over_price"], to["under_price"])
    ov = ((1 - PHI((to["line"] - tr) / SD["total"])) + (1 - PHI((to["line"] - ta) / SD["total"]))) / 2
    market("O/U", [
        {"pick": f"Over {to['line']}", "price": to["over_price"], "model": ov, "fair": fo, "final": fo + 0.25 * (ov - fo)},
        {"pick": f"Under {to['line']}", "price": to["under_price"], "model": 1 - ov, "fair": fu, "final": fu + 0.25 * ((1 - ov) - fu)}])

    # 4h halves
    n_team = len(logs[A]) + len(logs[H])
    for half, key, sd, lr in (("1H U26.5", "h1", SD["h1"], league["h1_rate"]), ("2H U26.5", "h2", SD["h2"], league["h2_rate"])):
        m = PHI((26.5 - proj[key]) / sd)
        fin = (m + lr) / 2
        cnt = T[A][f"{key}_under"] + T[H][f"{key}_under"]
        mk.append({"bet": half, "pick": "Under 26.5", "model": m, "league": lr, "final": fin, "need": need_price(fin),
                   "team_count": cnt, "team_games": n_team, "price": g.get(f"{key}_under_price"), "disagree": False})

    # Step 5: qualification
    skip_fg = g.get("skip_full_game")
    for m in mk:
        why = []
        half = m["bet"].startswith(("1H", "2H"))
        if half:
            if m["final"] < 0.65: why.append("below 65%")
            if m["team_count"] < 0.75 * m["team_games"]: why.append(f"team count {m['team_count']}/{m['team_games']} < 75%")
        else:
            if m["final"] < 0.60: why.append("below 60%")
            if m["disagree"]: why.append("DISAGREE")
            if m["bet"] == "ML" and m.get("dog"): why.append("underdog ML")
            if skip_fg: why.append(skip_fg)
        if m["price"] is None:
            if not why: why.append("price not given")
        elif not price_ok(m["price"], m["final"]):
            why.append("overpriced")
        m["qualifies"] = not why
        m["blocked_by"] = why
    out["markets"] = mk
    return out


def parlays(results):
    legs = sorted([(m["final"], r["away"] + "@" + r["home"], m) for r in results for m in r["markets"]
                   if m["qualifies"] and m["final"] >= 0.65], key=lambda x: -x[0])
    used, out = set(), []
    for i, a in enumerate(legs):
        for b in legs[i + 1:]:
            if len(out) == 3: break
            if a[1] == b[1] or id(a[2]) in used or id(b[2]) in used: continue
            used |= {id(a[2]), id(b[2])}
            out.append({"legs": [f"{a[1]} {a[2]['bet']} {a[2]['pick']}", f"{b[1]} {b[2]['bet']} {b[2]['pick']}"],
                        "combined": a[0] * b[0]})
    return out


def main(run):
    cfg, sr, epa, games = load(run)
    h1 = [a[1][0] + a[1][1] + h[1][0] + h[1][1] for _, a, h in games]
    h2 = [a[1][2] + a[1][3] + h[1][2] + h[1][3] for _, a, h in games]
    n = len(games)
    league = {"games": n, "h1_avg": sum(h1) / n, "h2_avg": sum(h2) / n,
              "h1_under": sum(v < 26.5 for v in h1), "h2_under": sum(v < 26.5 for v in h2)}
    league["h1_rate"], league["h2_rate"] = league["h1_under"] / n, league["h2_under"] / n
    results = [run_game(g, cfg, sr, epa, games, league) for g in cfg["games"]]
    res = {"config": cfg, "league": league, "games": results, "parlays": parlays(results)}
    json.dump(res, open(f"{run}/result.json", "w"), indent=1)

    # audit trail
    print(f"League: {n} final games | 1H avg {league['h1_avg']:.2f} U26.5 {league['h1_under']}/{n} | "
          f"2H avg {league['h2_avg']:.2f} U26.5 {league['h2_under']}/{n}")
    for r in results:
        print(f"\n== {r['away']} @ {r['home']}")
        for t, d in r["teams"].items():
            e, s = d["espn"], d["statrankings"]
            print(f" {t} ({d['games']} g) ESPN pf {e['pf']:.2f} pa {e['pa']:.2f} 1H {e['h1f']:.2f}/{e['h1a']:.2f} 2H {e['h2f']:.2f}/{e['h2a']:.2f}"
                  f" | SR pf {s['pf']} pa {s['pa']} 1H {s['h1f']}/{s['h1a']} 2H {s['h2f']}/{s['h2a']}")
        p = r["proj"]
        for k in ("raw", "adj"):
            print(f" {k.upper()}: {r['away']} {p[k]['away']:.2f} {r['home']} {p[k]['home']:.2f} margin(home) {p[k]['margin_home']:+.2f} total {p[k]['total']:.2f}")
        print(f" 1H proj {p['h1']:.2f} | 2H proj {p['h2']:.2f}")
        for m in r["markets"]:
            extra = f"fair {m['fair']:.3f}" if "fair" in m else f"league {m['league']:.3f} count {m['team_count']}/{m['team_games']}"
            print(f"  {m['bet']:9s} {m['pick']:12s} model {m['model']:.3f} {extra} final {m['final']:.3f} ({pct(m['final'])}%)"
                  f" need {fmt_odds(m['need'])} {'DISAGREE ' if m['disagree'] else ''}-> {'BET' if m['qualifies'] else 'no: ' + ', '.join(m['blocked_by'])}")
    print("\nParlays:", res["parlays"] or "none")


if __name__ == "__main__":
    main(sys.argv[1].rstrip("/"))
