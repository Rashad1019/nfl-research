# NFL Bet Research: instructions for any AI session

Read this whole file before doing anything in this repo. It is the hand-off document: a new
Claude/LLM session (or a human) should be able to continue the work from here with no other context.

## What this repo is

Rashad runs the **`nfl-bet-research` skill** (Claude skill; Template A = game bets, Template B = player
props). Every time a Template A run is done, its data, model output and a colorful HTML report are
committed here and **pushed to `main`**. Repo: https://github.com/Rashad1019/nfl-research (public).

- `index.html` (root): list of every run, newest first. Regenerated automatically.
- `runs/<season>-w<WW>-<away>-at-<home>/report.html`: the visual report for one run.

The skill is the source of truth for the **method** (rules, formulas, cutoffs). This repo is the
source of truth for the **code that implements it** and the **history of runs**.
If the skill and `scripts/template_a.py` ever disagree, follow the skill and fix the script.

## Standard workflow for a new Template A run

Rashad gives: the game(s) and the book lines (ML both sides, spread, total; sometimes juice,
sometimes 1H/2H under prices). Then:

1. **Create the run folder**: `runs/<season>-w<WW>-<away>-at-<home>/` (ESPN abbreviations, lowercase
   in the folder name, e.g. `2026-w05-buf-at-lar`). For a multi-game slate use
   `runs/<season>-w<WW>-slate-<date>/` and list every game in `config.json`.
2. **Write `config.json`.** Copy the previous run's config as a template. Fill in:
   - `ml`, `spread` (home line + both prices), `total` (line + both prices). If Rashad didn't give
     juice, use DraftKings from the ESPN summary (`pickcenter`) and say so in `lines_source`.
   - `h1_under_price` / `h2_under_price`: `null` if not given (report then says "price not given").
   - `skip_full_game`: `null`, or a reason string if a skill ❌ rule applies (QB questionable, or
     a different QB starting than usual; strong wind not in the line).
   - Hand-researched text: `injuries`, `qbs`, `weather`, `opening`, `line_move`, `situation`,
     `kills_it`, `not_checked`, `sources`. These come from web search (official injury reports,
     odds articles) and are rendered as-is.
3. **Fetch data**: `python3 scripts/fetch_data.py runs/<run>`. It prints any source that failed.
   Put every failure in `not_checked` (skill rule 8: never skip silently).
4. **Model**: `python3 scripts/template_a.py runs/<run>`. It prints an audit trail and writes `result.json`.
   Check the ESPN-vs-StatRankings lines it prints and note any disagreement in `not_checked`.
5. **Report**: `python3 scripts/build_report.py runs/<run>`. It writes `report.html` and rebuilds `index.html`.
6. **Visually check** the report (see "Screenshots" below), at phone width especially.
7. **Answer Rashad in chat** with the skill's exact Table 1/2/3 output (the HTML is extra, not a
   replacement), then **commit and push**:
   ```
   git add -A && git commit -m "Week N: AWAY @ HOME Template A run" && git push origin main
   ```
8. **Grading**: when Rashad sends final scores ("grade it"), record W/L/Push per market in
   `runs/<run>/grades.json` (not built yet; see Roadmap) and push.

## Report audience and layout (Rashad's requirement, 2026-10-11)

Write the report for **someone who has never placed a sports bet**. They should know instantly what
to do and why. `build_report.py` renders, in this order:
1. Team banner, then a big **"What to do"** box: "Don't bet this game", or "Bet N of the 5" listing
   each bet and the worst price to accept.
2. "How to read this page": 4 short steps (chance → 60/65% bar → extra checks → green/red).
3. "The 5 bets at a glance": the chat's Table 1 as a simple list (bet, chance, need, ✓ BET / ✕ SKIP).
4. One card per bet: **what the bet means** in plain words (incl. "risk $X to win $Y"), a chance
   meter with the cutoff line, **why we're not betting it** (one plain sentence per failed rule,
   with the actual numbers), **the numbers behind it** (for halves: each team's half points
   scored/allowed → expected points → projected total, plus every game's half total ✓/✕), and
   "how we got X%".
5. Odds explained, injuries/QB/line movement, then collapsed "More detail", glossary, sources.

Keep jargon (EPA, de-vig, DISAGREE, RAW/ADJ) out of the main view, or explain it inline.
Numbers on the page round half up (`r1()`, `pct()`) so they match the chat tables.

## Repo layout

```
CLAUDE.md                 this file (AGENTS.md points here)
README.md                 human overview
index.html                generated: list of all runs
scripts/
  teams.py                ESPN abbr -> StatRankings name, nflverse code, team colors (all 32)
  fetch_data.py           downloads StatRankings (26 stat pages + 3 trend pages), ESPN scoreboards/
                          summaries/box scores, nflverse play-by-play -> EPA
  template_a.py           the Template A model (skill Step 4 + Step 5), writes result.json
  build_report.py         result.json -> report.html (+ index.html)
runs/<run>/
  config.json             inputs: lines, prices, hand-researched notes
  data/                   raw snapshot used for that run (committed so results are reproducible)
    sr_data.json          StatRankings tables, all 32 teams, all columns
    espn/wk<N>.json       ESPN scoreboards (quarter line scores) weeks 1..N
    espn/summary_A-H.json ESPN game summary: DraftKings odds, injuries, venue, weather
    espn/g_<id>.json      ESPN box scores for both teams' completed games (QB starters)
    epa.json              EPA/play + success rate per team (derived)
  result.json             every computed number
  report.html             the visual report
```

Re-running `template_a.py` on a committed `data/` snapshot must reproduce the same numbers.
**Don't re-fetch into an old run's `data/`**, because that overwrites the snapshot the picks were made on.

## Model (what template_a.py does)

Exactly the skill's Step 4/5:
- RAW team points = (team PF + opp PA)/2; margin = home − away + 1.5 (0 if `neutral`); total = sum.
- ADJ: adj off = PF − (avg PA of opponents played − league avg ppg); adj def = PA − (avg PF of opponents − league avg).
- Halves (RAW only): half total = (away half F + home half A)/2 + (home half F + away half A)/2.
- Model chance = average of RAW and ADJ via normal CDF: σ 13.3 (ML/spread), 13.5 (total), 10 (1H), 10.5 (2H).
- Fair = de-vigged book probability. Final = Fair + 0.25·(Model − Fair). ⚠ DISAGREE if |Model − Fair| > 10 pts.
- Halves: Final = (model + league under-26.5 rate)/2; team count = both teams' games under 26.5 in that half.
- Need price: −100·F/(1−F) if F ≥ 50%, else +100·(1−F)/F.
- Bet only if: Final ≥ 60% (halves ≥ 65% **and** team count ≥ 75%), not DISAGREE, no underdog ML,
  book price at or better than Need, and no `skip_full_game` reason.
- Parlays: 2 legs, each ≥ 65% and qualifying, different games, no leg reused, max 3.
- Percentages rounded half-up to whole numbers.

### Data choices (deliberate; keep them unless Rashad changes them)
- **Team points and half points come from ESPN game-by-game line scores** (OT excluded from 2H).
  StatRankings is the cross-check, and the script prints both. Reason: bets grade on actual points, but
  StatRankings' "opponent half points" pages and its "opponent-offensive-points-per-game-estimated"
  page leave out defensive/special-teams scores (e.g. LAR 2H allowed: StatRankings 11.0 vs actual 12.5 in 2026 Wk 5).
- **Schedule adjustment** uses StatRankings `ppg` and `opp_ppg` (actual points allowed) for all 32 teams.
- **League half rates** = every FINAL game this season in ESPN scoreboards, weeks 1..`week`.
  Games in progress at fetch time are excluded.

## Source fallbacks (verified 2026-10-11)

| Skill source | Status | What we use instead |
|---|---|---|
| statrankings.com | ✅ works with plain `curl`/urllib + browser UA | (primary) |
| footballdb.com | ❌ HTTP 403 (curl and WebFetch) | ESPN scoreboard API line scores |
| pro-football-reference.com | ❌ HTTP 403 (curl and WebFetch) | ESPN summary/box score API |
| rbsdm.com | ❌ JS-only app, no data in HTML | nflverse play-by-play → EPA (`epa.json`) |
| Injuries | ESPN summary `injuries` + team sites via web search | |
| Odds/juice | ESPN summary `pickcenter` (DraftKings) | opening line via web search |

ESPN endpoints (no key needed):
- Scoreboard: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=<season>&seasontype=2&week=<N>`
- Game summary: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=<id>`

## Gotchas
- ESPN abbreviations are the canonical keys (`LAR`, `WSH`). nflverse uses `LA` and `WAS`;
  `teams.py` maps them. StatRankings rows are keyed by full team name (in a `data-tooltip` attribute).
- A Monday game appears in that week's ESPN scoreboard (UTC date may be Tuesday).
- StatRankings rate-limits (HTTP 429). `fetch_data.py` waits 3 s between pages and backs off on 429, so a full fetch takes ~2 min.
- StatRankings shows "-" in Last 5 when a team has played < 5 games. That's normal.
- **Screenshots:** headless Chrome won't render narrower than 500px, so a 400px `--window-size`
  screenshot looks clipped even when the page is fine. To check phone width, load the report in a
  390px-wide `<iframe>` and screenshot that (`--allow-file-access-from-files`).
- In CSS, don't append alpha hex to a `var(--x)` color (`var(--warn)66` is invalid). Bar fills use literal hex.

## Conventions
- Current-season stats only. Every number has a source; anything calculated is "derived".
- Rashad reads results on his phone, so keep the report phone-first and the chat tables narrow.
- Commit messages: `Week N: AWAY @ HOME Template A run` (or a short description for code changes).
- Push straight to `main`. Rashad asked for every run to be pushed here.

## Roadmap / not built yet
- Template B (player props) pipeline + report.
- `grades.json` + a running record by bet type on `index.html` (skill "Results log").
- GitHub Pages (would make `index.html` viewable as a website; not enabled yet).

## Run history
| Run | Date | Result |
|---|---|---|
| `2026-w05-buf-at-lar` | 2026-10-11 | No bets. ML/O-U ⚠ DISAGREE; closest 2H U26.5 64% (cutoff 65%), BUF +3.5 54% |
