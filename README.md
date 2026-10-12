# 🏈 NFL Bet Research

Game-bet research reports for NFL matchups, built with the `nfl-bet-research` method:
current-season stats only, the sportsbook line as the anchor, and research that nudges it a quarter
of the way toward our model. Bets are made only when strict cutoffs are met.

**Open `index.html`** to see every run, or go straight to a report in `runs/<run>/report.html`
(download the file, or view it via GitHub Pages if it's enabled).

## What's in a report
- Matchup banner, the book lines, and a one-line verdict (bet / no bet, and why)
- Projected score: raw and schedule-adjusted
- All 5 bets (moneyline, spread, over/under, 1st-half and 2nd-half under 26.5), each with a chance bar
  showing our model, the book's fair chance, the final number and the cutoff
- Half-scoring charts per team vs. the 26.5 line
- Tale of the tape (EPA, scoring, efficiency), game logs, injuries, line movement
- Bets we'd make, parlays, what wasn't checked, sources

## Run it
```bash
python3 scripts/fetch_data.py   runs/<run>   # needs runs/<run>/config.json
python3 scripts/template_a.py   runs/<run>   # -> result.json (+ audit trail)
python3 scripts/build_report.py runs/<run>   # -> report.html + index.html
```
Python 3 standard library only. No packages to install.

See **[CLAUDE.md](CLAUDE.md)** for the full workflow, model details, data sources, fallbacks and gotchas.

*No model guarantees a win. Track every bet against the closing line.*
