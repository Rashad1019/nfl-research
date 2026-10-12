# 🏈 NFL Bet Research

Game-bet research reports for NFL matchups, built with the `nfl-bet-research` method:
current-season stats only, the sportsbook line as the anchor, and research that nudges it a quarter
of the way toward our model. Bets are made only when strict cutoffs are met.

**Live site:** deployed on Vercel from this repo. Every push to `main` redeploys automatically.
Locally: `python3 -m http.server` in the repo root, then open http://localhost:8000.

### Deploy on Vercel (one time)
1. Go to https://vercel.com/new and import `Rashad1019/nfl-research`.
2. Framework Preset: **Other**. Leave build and output settings empty (`vercel.json` handles it).
3. Click **Deploy**. Your site URL is the list of games; tap a game for its report.

## What's in a report
Written for someone who has never placed a bet:
- A big **"What to do"** box at the top: bet these (and the worst price to accept), or "Don't bet this game"
- How to read the page in 4 steps, then all 5 bets at a glance (chance, what's needed, ✓ bet / ✕ skip)
- One card per bet (moneyline, spread, total, 1st-half and 2nd-half under 26.5): what the bet means in
  plain words, a chance meter, why we're skipping it (with numbers), and the math behind it
- Odds explained, injuries and line movement, plus tap-to-open detail, glossary and sources

## Run it
```bash
python3 scripts/fetch_data.py   runs/<run>   # needs runs/<run>/config.json
python3 scripts/template_a.py   runs/<run>   # -> result.json (+ audit trail)
python3 scripts/build_report.py runs/<run>   # -> report.html + index.html
```
Python 3 standard library only. No packages to install.

See **[CLAUDE.md](CLAUDE.md)** for the full workflow, model details, data sources, fallbacks and gotchas.

*No model guarantees a win. Track every bet against the closing line.*
