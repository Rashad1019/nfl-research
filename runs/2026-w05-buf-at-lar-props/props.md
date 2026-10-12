# Template B — BUF at LAR

Monday, October 12, 2026, 8:15 p.m. ET · SoFi Stadium. Research cutoff: October 11 ET. Current-season weeks 1–4 only.

**Research shortlist: Stafford passing, Coleman receiving (conditional on Moore playing), and Allen/Cook/Kyren touchdown roles. No confirmed bets: live prices and full source verification are incomplete, and the TD model materially disagrees with the published market.**

**Read the percentages correctly:** chance means beating that player’s own season median, not clearing a sportsbook line. T = TOP NUMBER; C = BEST CHANCE; T/C = both. WR1/2/3 are target rankings, not field alignment. All medians, projections, percentages and matchup factors below are **derived** from the linked game logs. These are uncalibrated small-sample model outputs.

**Method:** projection = median × opponent same-slot average / league same-slot average; chance = Φ((projection − median)/sample SD). League baseline uses 64 completed games / 128 team-games through Week 4, not the older skill’s stated 65. Missing participation games are excluded; active zero-stat games are included using nflverse/PFR snap records. PFR position tables were blocked, so same-slot ESPN league baselines are the disclosed fallback. QB1 means most pass attempts; RB1/2 use carries; WR/TE use targets, ties by yards. A missing slot counts zero in the league denominator. Zero SD yields N/A, never an invented percentage.

**Game script:** average the saved Template A raw and adjusted team points; apply no extra numerical script adjustment because the projected game is close (multiplier 1.00). Injuries are qualitative flags, not arbitrary boosts. [Template A source](../2026-w05-buf-at-lar/result.json).

Derived score context: BUF 26.2, LAR 24.5.

## BUF

| Category | Player | Slot | Games | Median | Projection | Chance | Matchup |
|---|---|---|---|---|---|---|---|
| Passing yards T/C | Josh Allen | QB1 | 4 | 250.5 | 161.3 | 5% | 0.64 |
| Pass attempts T/C | Josh Allen | QB1 | 4 | 30.0 | 28.4 | 29% | 0.95 |
| Completions T/C | Josh Allen | QB1 | 4 | 20.0 | 15.6 | 6% | 0.78 |
| TDs thrown T/C | Josh Allen | QB1 | 4 | 1.5 | 1.7 | 56% | 1.12 |
| Rushing yards T | James Cook | RB1 | 4 | 105.0 | 80.4 | 30% | 0.77 |
| Rushing yards C | Ray Davis | RB2 | 4 | 1.5 | 1.8 | 58% | 1.22 |
| Rush attempts T | James Cook | RB1 | 4 | 17.0 | 15.4 | 39% | 0.91 |
| Rush attempts C | Josh Allen | QB1 | 4 | 7.0 | 7.5 | 55% | 1.07 |
| Rush + rec yards T | James Cook | RB1 | 4 | 111.0 | 75.3 | 20% | 0.68 |
| Rush + rec yards C | Ray Davis | RB2 | 4 | 1.5 | 2.1 | 57% | 1.41 |
| Receptions T/C | Keon Coleman | WR3 | 4 | 3.5 | 4.4 | 63% | 1.27 |
| Receiving yards T/C | Keon Coleman | WR3 | 4 | 50.0 | 82.1 | 75% | 1.64 |
| Field goals (K) T/C | Tyler Bass | K1 | 4 | 1.5 | 1.3 | 44% | 0.86 |

**TOP 3 TD SCORERS — derived Poisson estimates**

| Player | Expected TDs | Chance | Why |
|---|---|---|---|
| Josh Allen | 1.38 | 75% | 7 TDs; 6 touches inside 10 |
| James Cook III | 1.19 | 70% | 3 TDs; 8 touches inside 10 |
| Keon Coleman | 0.10 | 10% | 1 TDs; 0 touches inside 10 |

Third place is tied: Coleman, Kincaid and Moore have identical model estimates. Coleman is shown because Moore is questionable; this is not a statistical advantage over Kincaid.

**TD math (derived):** team TDs = (16 ÷ 4) × (26.20781 ÷ 31.75) = 3.3018. Player share = ½ × (player TDs / 16 + player inside-10 touches / 15). Expected TDs = team TDs × player share; chance = 1 − exp(−expected TDs). Touches are rushes plus completed receptions, not targets; passing TDs do not count for the passer’s anytime TD. No redistribution of injured players’ TD shares. Puka’s missed games can depress his share.

**WHY / KILLS IT**

- **James Cook III:** Leads Buffalo carries, but every Rams lead back stayed below his rushing median. Palmer is out; Moore questionable. KILLS IT: Buffalo trails and abandons the run; Allen takes goal-line scores.
- **Josh Allen:** Rams suppress passing yardage; rushing and goal-line work are the better fit. Both starting QBs are cleared. KILLS IT: sacks and stalled drives prevent red-zone visits.
- **Keon Coleman:** Highest BUF receiving projection comes from the WR3 comparison; Palmer is out. Moore playing is an assumption. KILLS IT: Moore sits, Coleman moves to WR2, and the favorable comparison disappears.
- **Ray Davis:** Wins a chance ranking only against a tiny personal median; Ty Johnson is ahead on the depth chart. KILLS IT: no offensive touches. This is not a recommended prop.
- **Tyler Bass:** A close game supports late kicks, but the model does not project two makes. KILLS IT: touchdowns or fourth-down attempts replace field goals.

**DEFENSE — LAR, opponent by opponent.** C/A = completions/attempts. RB = most carries; WR = most targets, ties by yards. Each row links to its ESPN box score.

| Opponent | QB: C/A, yards, TD | Lead RB: carries/yards | WR1: catches/yards | TE1: catches/yards |
|---|---|---|---|---|
| [SF](https://www.espn.com/nfl/boxscore/_/gameId/401872657) | Brock Purdy: 25/34, 205, 3 | Kaelon Black: 14/65 | Mike Evans: 6/49 | George Kittle: 2/12 |
| [NYG](https://www.espn.com/nfl/boxscore/_/gameId/401872947) | Jameis Winston: 11/27, 111, 0 | Cam Skattebo: 12/36 | Malachi Fields: 2/30 | Isaiah Likely: 5/33 |
| [DEN](https://www.espn.com/nfl/boxscore/_/gameId/401872962) | Bo Nix: 17/34, 186, 2 | J.K. Dobbins: 17/49 | Courtland Sutton: 3/46 | Nate Adkins: 1/8 |
| [PHI](https://www.espn.com/nfl/boxscore/_/gameId/401872970) | Jalen Hurts: 12/27, 93, 2 | Tank Bigsby: 14/55 | Darius Cooper: 3/33 | Zach Ertz: 2/13 |

**Defense counts (derived):**
- QB passing yards >225.5: 0/4; log 205, 111, 186, 93. These are screening marks, not quoted book lines.
- QB completions >19.5: 1/4; log 25, 11, 17, 12. These are screening marks, not quoted book lines.
- QB pass TDs >1.5: 3/4; log 3, 0, 2, 2. These are screening marks, not quoted book lines.
- lead-RB rush yards >59.5: 1/4; log 65, 36, 49, 55. These are screening marks, not quoted book lines.
- RB2 rush yards >29.5: 1/4; log 68, 6, 6, 23. These are screening marks, not quoted book lines.
- WR1 catches >5.5: 1/4; log 6, 2, 3, 3. These are screening marks, not quoted book lines.
- WR3 receiving yards >39.5: 3/4; log 50, 48, 44, 18. These are screening marks, not quoted book lines.

**KICKER — Tyler Bass:** FG makes 3, 0, 1, 2; attempts 3, 0, 1, 2. Median attempts 1.5; XP 13/14. Opponent allowed 2+ FGA in 3/4 games (3, 2, 1, 2), 2.0 FGA/game.
- under 40 yards: 5/5 made; 100%.
- 40–49 yards: 1/1 made; 100%.
- 50+ yards: 0/0 made; no attempts.

**Kicker stress test (derived):** offense RZ TDs 11/16 (69%), 4.0 trips/game; opponent allows 7/12 (58%). Averaged trip expectation 3.50 × (1 − averaged TD rate 64%) = 1.28 non-TD red-zone possessions. This is an opportunity proxy, not guaranteed FG attempts: turnovers and fourth-down tries consume some. Longer kicks cannot be forecast reliably from this sample. Roof limits direct rain; field-level wind was not verified. No kicker over recommended.

## LAR

| Category | Player | Slot | Games | Median | Projection | Chance | Matchup |
|---|---|---|---|---|---|---|---|
| Passing yards T/C | Matthew Stafford | QB1 | 4 | 322.0 | 381.9 | 73% | 1.19 |
| Pass attempts T/C | Matthew Stafford | QB1 | 4 | 41.0 | 46.7 | 65% | 1.14 |
| Completions T/C | Matthew Stafford | QB1 | 4 | 26.0 | 29.4 | 67% | 1.13 |
| TDs thrown T/C | Matthew Stafford | QB1 | 4 | 1.0 | 1.6 | 62% | 1.60 |
| Rushing yards T | Kyren Williams | RB1 | 4 | 82.5 | 64.7 | 21% | 0.78 |
| Rushing yards C | Blake Corum | RB2 | 4 | 34.5 | 60.6 | 79% | 1.76 |
| Rush attempts T | Kyren Williams | RB1 | 4 | 13.5 | 13.9 | 57% | 1.03 |
| Rush attempts C | Blake Corum | RB2 | 4 | 8.0 | 11.5 | 85% | 1.43 |
| Rush + rec yards T | Kyren Williams | RB1 | 4 | 122.0 | 103.1 | 33% | 0.84 |
| Rush + rec yards C | Blake Corum | RB2 | 4 | 37.5 | 58.5 | 72% | 1.56 |
| Receptions T/C | Puka Nacua | WR1 | 2 | 7.0 | 8.6 | 72% | 1.23 |
| Receiving yards T/C | Puka Nacua | WR1 | 2 | 99.5 | 114.6 | 66% | 1.15 |
| Field goals (K) T/C | Harrison Mevis | K1 | 4 | 0.5 | 0.4 | 47% | 0.72 |

**TOP 3 TD SCORERS — derived Poisson estimates**

| Player | Expected TDs | Chance | Why |
|---|---|---|---|
| Kyren Williams | 1.44 | 76% | 4 TDs; 9 touches inside 10 |
| Puka Nacua | 0.34 | 29% | 1 TDs; 2 touches inside 10 |
| Davante Adams | 0.29 | 25% | 2 TDs; 0 touches inside 10 |

**TD math (derived):** team TDs = (10 ÷ 4) × (24.52031 ÷ 21.25) = 2.8847. Player share = ½ × (player TDs / 10 + player inside-10 touches / 15). Expected TDs = team TDs × player share; chance = 1 − exp(−expected TDs). Touches are rushes plus completed receptions, not targets; passing TDs do not count for the passer’s anytime TD. No redistribution of injured players’ TD shares. Puka’s missed games can depress his share.

**WHY / KILLS IT**

- **Blake Corum:** BUF RB2 production lifts the formula, but Corum’s recent workload is falling. No injury-based promotion. KILLS IT: Williams retains nearly all meaningful touches.
- **Davante Adams:** WR2 comparison reflects Nacua’s return; the two games without Nacua overstate his current opportunity. KILLS IT: Nacua dominates and Williams finishes drives.
- **Harrison Mevis:** Buffalo has rarely forced multiple field-goal attempts; recent four-make game is an outlier. KILLS IT: touchdowns replace kicks.
- **Kyren Williams:** Top Rams back by carries and receiving workload; Oliver is out for Buffalo. Run-yard matchup is less favorable than the TD role. KILLS IT: Corum gets the carries or Stafford throws the scores.
- **Matthew Stafford:** Buffalo has consistently allowed passing volume; a close game keeps both offenses involved. No QB injury designation. KILLS IT: Rams establish a lead and run, cutting attempts.
- **Puka Nacua:** Highest targets per appearance and favorable BUF WR1 catches; active after missing two games. LOW CONFIDENCE: two games. KILLS IT: reduced workload or Adams commands targets.

**DEFENSE — BUF, opponent by opponent.** C/A = completions/attempts. RB = most carries; WR = most targets, ties by yards. Each row links to its ESPN box score.

| Opponent | QB: C/A, yards, TD | Lead RB: carries/yards | WR1: catches/yards | TE1: catches/yards |
|---|---|---|---|---|
| [HOU](https://www.espn.com/nfl/boxscore/_/gameId/401872660) | C.J. Stroud: 26/38, 274, 2 | David Montgomery: 20/60 | Nico Collins: 7/75 | Dalton Schultz: 4/35 |
| [DET](https://www.espn.com/nfl/boxscore/_/gameId/401872932) | Jared Goff: 26/38, 327, 4 | Jahmyr Gibbs: 16/52 | Amon-Ra St. Brown: 9/142 | Sam LaPorta: 6/52 |
| [LAC](https://www.espn.com/nfl/boxscore/_/gameId/401872953) | Justin Herbert: 20/34, 226, 1 | Omarion Hampton: 15/56 | Tre' Harris: 6/76 | Oronde Gadsden: 0/0 |
| [NE](https://www.espn.com/nfl/boxscore/_/gameId/401872971) | Drake Maye: 22/37, 269, 3 | TreVeyon Henderson: 14/42 | Romeo Doubs: 6/58 | Hunter Henry: 5/62 |

**Defense counts (derived):**
- QB passing yards >225.5: 4/4; log 274, 327, 226, 269. These are screening marks, not quoted book lines.
- QB completions >19.5: 4/4; log 26, 26, 20, 22. These are screening marks, not quoted book lines.
- QB pass TDs >1.5: 3/4; log 2, 4, 1, 3. These are screening marks, not quoted book lines.
- lead-RB rush yards >59.5: 1/4; log 60, 52, 56, 42. These are screening marks, not quoted book lines.
- RB2 rush yards >29.5: 3/4; log 42, 7, 52, 47. These are screening marks, not quoted book lines.
- WR1 catches >5.5: 4/4; log 7, 9, 6, 6. These are screening marks, not quoted book lines.
- WR3 receiving yards >39.5: 3/4; log 53, 33, 66, 42. These are screening marks, not quoted book lines.

**KICKER — Harrison Mevis:** FG makes 0, 0, 4, 1; attempts 0, 1, 4, 2. Median attempts 1.5; XP 10/10. Opponent allowed 2+ FGA in 1/4 games (1, 1, 4, 0), 1.5 FGA/game.
- under 40 yards: 2/2 made; 100%.
- 40–49 yards: 3/5 made; 60%.
- 50+ yards: 0/0 made; no attempts.

**Kicker stress test (derived):** offense RZ TDs 8/15 (53%), 3.8 trips/game; opponent allows 11/16 (69%). Averaged trip expectation 3.88 × (1 − averaged TD rate 61%) = 1.51 non-TD red-zone possessions. This is an opportunity proxy, not guaranteed FG attempts: turnovers and fourth-down tries consume some. Longer kicks cannot be forecast reliably from this sample. Roof limits direct rain; field-level wind was not verified. No kicker over recommended.

## WATCH, market check and stress tests

- **Stafford:** favorable defense does not validate the extreme yardage projection. BetMGM’s October 7 article lists 282.5 yards, 36.5 attempts, 23.5 completions and 2.5 passing TDs; the article has an incorrect ET kickoff label, and its lines are not a live quote. No over/under prices were available in that article. [Book source](https://sports.betmgm.com/en/blog/nfl/matthew-stafford-props-odds-gaa/).
- **Coleman:** Moore active is essential to the WR3 comparison. If Moore is out, Coleman moves to WR2 and the model must be rerun; Bell is next behind Moore on the depth chart but lacks a verified four-game receiving sample. Palmer’s absence can add Coleman routes, but no fixed target boost is invented.
- **Puka: LOW CONFIDENCE.** Only two appearances. Corum’s early split differs from the current workload. Ray Davis’s small median can produce a good chance ranking without meaningful projected yardage.
- **Injuries:** BUF Oliver and Palmer out; Moore, Alford and Landon Jackson questionable. LAR Donald, Parkinson and Watson cleared; Lake questionable. Ferguson unavailable. Official updates override older injury labels on Ourlads. [Bills](https://www.buffalobills.com/news/buffalo-bills-injury-report-vs-rams-week-5), [Rams](https://www.therams.com/news/rams-injury-report-week-5-2026-vs-bills-aaron-donald-colby-parkinson-and-jaylen-watson-good-to-go-for-monday-night-football).
- **Coverage:** Ourlads lists Shakir in the slot, Coleman left and Moore right; Rams McDuffie right CB, Watson left CB, Wallace nickel. BUF Benford left CB, Hairston right CB, Alford nickel; Rams Mumpfield in the slot. These are alignment starting points, not shadow assignments. Individual current-season targets/catches/yards/TDs/rating allowed were not verified, so no weak-defender claim or numerical boost is made. [BUF depth](https://www.ourlads.com/nfldepthcharts/depthchart/BUF), [LAR depth](https://www.ourlads.com/nfldepthcharts/depthchart/LAR).

- **Stress scenario, analyst assumptions — Stafford completions:** 33.0 × 0.60 = 19.8. First term = 60 plays × 60% dropbacks − 3 sacks/scrambles. The optimistic projection does not survive every realistic script.
- **Stress scenario, analyst assumptions — Coleman catches:** 4.0 × 0.60 = 2.4. Targets × catch rate, or carries × yards/carry. The optimistic projection does not survive every realistic script.
- **Stress scenario, analyst assumptions — Puka catches:** 8.0 × 0.60 = 4.8. Targets × catch rate, or carries × yards/carry. The optimistic projection does not survive every realistic script.
- **Stress scenario, analyst assumptions — Corum rush yards:** 5.0 × 3.50 = 17.5. Targets × catch rate, or carries × yards/carry. The optimistic projection does not survive every realistic script.
- **Stress scenario, analyst assumptions — Cook rush yards:** 12.0 × 4.00 = 48.0. Targets × catch rate, or carries × yards/carry. The optimistic projection does not survive every realistic script.

**Published anytime TD prices (October 11 article; not verified live).** Implied probabilities calculated from prices, with vig still included. They are not fair probabilities. Large disagreement blocks a confident recommendation under the skill’s book-first rule.

| Player | Model | Book | Implied | Gap |
|---|---|---|---|---|
| Josh Allen | 75% | -118 | 54% | 20.8 pts |
| James Cook III | 70% | -118 | 54% | 15.4 pts |
| DJ Moore | 10% | +185 | 35% | -25.3 pts |
| Keon Coleman | 10% | +260 | 28% | -18.0 pts |
| Dalton Kincaid | 10% | +165 | 38% | -27.9 pts |
| Kyren Williams | 76% | -185 | 65% | 11.5 pts |
| Puka Nacua | 29% | -125 | 56% | -27.0 pts |
| Davante Adams | 25% | -105 | 51% | -26.2 pts |

[BetMGM TD source](https://sports.betmgm.com/en/blog/nfl/bills-rams-first-anytime-td-odds-picks-week-5-gaa/). Prices only; the article’s historical trends were not used.

## Data checks and missing research

- ESPN game-by-game sums agree with FootballDB’s season totals for Allen passing (1,039 yards, 79/119, six TDs), Stafford passing (1,189 yards, 99/162, six TDs), Cook rushing (421), and Puka receiving (14/199 on 21 targets). These are partial independent checks, not completion of the strict PFR + FootballDB every-game requirement.
- Shakir discrepancy: ESPN game log sums to 176 yards, matching PFR/NFL season totals; nflverse play sums give 166, including 40 rather than 50 in Week 1. Use ESPN’s game sum and flag it. All other tested BUF/LAR player passing/rushing/receiving yardage, attempts, completions and TD logs agree across ESPN and nflverse. Feeds may share the same upstream NFL scorer, so this is not a substitute for full independent verification.
- ESPN passing total rows sometimes use net yards while individual rows use gross yards. Those differences are retained in result.json; the player props use gross individual passing yards. Receiving and rushing rows matched their own total rows before the audit. PFR’s BUF QB allowed totals match the four-game ESPN sum; LAR PFR lists 615 QB yards, which includes the backup Dart’s 20; starter-only comparator is explicitly separate.
- PFR team pages, red-zone and advanced-defense direct requests returned 403; FootballDB direct team-stat requests returned 403. Some player totals and snap pages were available through indexed web results. NFLverse player_stats_2026.csv returned 404; ESPN boxes, nflverse play-by-play and snap-count CSV were used instead.
- Not verified: every player’s PFR/FootballDB box-score cross-check, all defensive-position season totals, individual coverage metrics, ESPN block/run-stop win rates, Next Gen separation and yards before contact (page failed), Sharp explosive/directional metrics, confirmed coordinator game-plan quotes, live multi-book lines/movement, final inactives and field-level wind. No old-season data filled these gaps.
- Categories are modeled independently and are not an internally reconciled stat line: Cook’s combined-yard projection is below his rush-yard projection. That inconsistency is another reason to treat this as a screening run, not a betting forecast.
- The normal approximation is only the requested ranking formula. It is not calibrated for low discrete counts, and the TD share formula can assign zero to players who still have a real scoring chance. Model outputs should not be used as certainty or automatically converted into bets.

## Sources and reproducibility

- [Allen second source](https://www.footballdb.com/players/josh-allen-allenjo06); [Stafford second source](https://www.footballdb.com/players/matthew-stafford-staffma01); [Cook/team totals](https://www.footballdb.com/teams/nfl/buffalo-bills); [Puka games](https://www.footballdb.com/players/puka-nacua-nacuapu01); [Shakir PFR](https://www.pro-football-reference.com/players/S/ShakKh00.htm).
- [nflverse play-by-play](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz); [nflverse/PFR participation](https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2026.csv).
- ESPN per-game source links are in both defense tables; all 64 league snapshots and 32 rosters are frozen under data/. StatRankings and Template A frozen inputs are also retained.
- Reproduce: python3 runs/2026-w05-buf-at-lar-props/analyze.py then python3 runs/2026-w05-buf-at-lar-props/build.py. Fetch script is provenance only; do not refetch over this frozen run.

## Appendix: every checked player and calculation


**BUF — Passing yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Josh Allen | 334, 248, 204, 253 | 250.5 | 205, 93, 111, 186 | 231.016 | 0.644 | 161.3 | 5% |

**BUF — Pass attempts**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Josh Allen | 29, 31, 26, 33 | 30.0 | 34, 27, 27, 34 | 32.258 | 0.946 | 28.4 | 29% |

**BUF — Completions**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Josh Allen | 20, 20, 16, 23 | 20.0 | 25, 12, 11, 17 | 20.773 | 0.782 | 15.6 | 6% |

**BUF — TDs thrown**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Josh Allen | 2, 3, 0, 1 | 1.5 | 3, 2, 0, 2 | 1.563 | 1.120 | 1.7 | 56% |

**BUF — Rushing yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| James Cook III | 57, 135, 154, 75 | 105.0 | 65, 55, 36, 49 | 66.914 | 0.766 | 80.4 | 30% |
| Ray Davis | 3, 0, 0, 3 | 1.5 | 68, 23, 6, 6 | 21.078 | 1.222 | 1.8 | 58% |
| Josh Allen | 23, 69, 22, 4 | 22.5 | 29, 18, 1, 7 | 15.750 | 0.873 | 19.6 | 46% |

**BUF — Rush attempts**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| James Cook III | 13, 21, 24, 12 | 17.0 | 14, 14, 12, 17 | 15.734 | 0.906 | 15.4 | 39% |
| Ray Davis | 1, 0, 0, 1 | 0.5 | 10, 6, 4, 2 | 5.406 | 1.017 | 0.5 | 51% |
| Josh Allen | 6, 14, 8, 5 | 7.0 | 5, 5, 2, 4 | 3.727 | 1.073 | 7.5 | 55% |

**BUF — Rush + rec yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| James Cook III | 69, 139, 154, 83 | 111.0 | 70, 55, 55, 53 | 85.820 | 0.679 | 75.3 | 20% |
| Ray Davis | 3, 0, 0, 7 | 1.5 | 88, 23, 6, 47 | 29.000 | 1.414 | 2.1 | 57% |

**BUF — Receptions**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Khalil Shakir | 4, 3, 1, 7 | 3.5 | 6, 3, 2, 3 | 5.672 | 0.617 | 2.2 | 30% |
| DJ Moore | 5, 0, 6, 1 | 3.0 | 6, 3, 1, 2 | 3.188 | 0.941 | 2.8 | 48% |
| Keon Coleman | 1, 6, 1, 6 | 3.5 | 2, 3, 2, 2 | 1.773 | 1.269 | 4.4 | 63% |
| Dalton Kincaid | 5, 7, 2, 1 | 3.5 | 2, 2, 5, 1 | 3.914 | 0.639 | 2.2 | 32% |
| James Cook III | 3, 1, 0, 2 | 1.5 | 1, 0, 4, 1 | 2.734 | 0.549 | 0.8 | 30% |

**BUF — Receiving yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Khalil Shakir | 50, 38, 6, 82 | 44.0 | 49, 33, 30, 46 | 76.219 | 0.518 | 22.8 | 25% |
| DJ Moore | 100, 0, 67, 11 | 39.0 | 48, 27, 1, 10 | 42.008 | 0.512 | 20.0 | 34% |
| Keon Coleman | 1, 63, 37, 116 | 50.0 | 50, 18, 48, 44 | 24.352 | 1.643 | 82.1 | 75% |
| Dalton Kincaid | 130, 95, 38, 7 | 66.5 | 12, 13, 33, 8 | 39.352 | 0.419 | 27.9 | 24% |
| James Cook III | 12, 4, 0, 8 | 6.0 | 5, 0, 19, 4 | 18.906 | 0.370 | 2.2 | 23% |

**BUF — Field goals (K)**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Tyler Bass | 3, 0, 1, 2 | 1.5 | 2, 2, 2, 0 | 1.734 | 0.865 | 1.3 | 44% |

**LAR — Passing yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Matthew Stafford | 155, 327, 390, 317 | 322.0 | 269, 274, 327, 226 | 231.016 | 1.186 | 381.9 | 73% |

**LAR — Pass attempts**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Matthew Stafford | 25, 31, 55, 51 | 41.0 | 37, 38, 38, 34 | 32.258 | 1.139 | 46.7 | 65% |

**LAR — Completions**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Matthew Stafford | 15, 22, 30, 32 | 26.0 | 22, 26, 26, 20 | 20.773 | 1.131 | 29.4 | 67% |

**LAR — TDs thrown**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Matthew Stafford | 0, 4, 2, 0 | 1.0 | 3, 2, 4, 1 | 1.563 | 1.600 | 1.6 | 62% |

**LAR — Rushing yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Kyren Williams | 41, 85, 88, 80 | 82.5 | 42, 60, 52, 56 | 66.914 | 0.785 | 64.7 | 21% |
| Blake Corum | 54, 79, 15, 14 | 34.5 | 47, 42, 7, 52 | 21.078 | 1.755 | 60.6 | 79% |
| Matthew Stafford | -1, -1, 13, 10 | 4.5 | 54, 15, 7, 17 | 15.750 | 1.476 | 6.6 | 62% |

**LAR — Rush attempts**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Kyren Williams | 11, 12, 15, 16 | 13.5 | 14, 20, 16, 15 | 15.734 | 1.033 | 13.9 | 57% |
| Blake Corum | 10, 12, 6, 5 | 8.0 | 13, 9, 1, 8 | 5.406 | 1.434 | 11.5 | 85% |
| Matthew Stafford | 2, 4, 2, 3 | 2.5 | 8, 2, 3, 4 | 3.727 | 1.140 | 2.9 | 64% |

**LAR — Rush + rec yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Kyren Williams | 65, 97, 158, 147 | 122.0 | 42, 79, 113, 56 | 85.820 | 0.845 | 103.1 | 33% |
| Blake Corum | 54, 92, 15, 21 | 37.5 | 74, 40, 20, 47 | 29.000 | 1.560 | 58.5 | 72% |

**LAR — Receptions**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Puka Nacua | 5, 9 | 7.0 | 6, 7, 9, 6 | 5.672 | 1.234 | 8.6 | 72% |
| Davante Adams | 3, 8, 7, 4 | 5.5 | 3, 3, 2, 3 | 3.188 | 0.863 | 4.7 | 38% |
| Konata Mumpfield | 0, 1, 4, 1 | 1.0 | 2, 2, 2, 4 | 1.773 | 1.410 | 1.4 | 59% |
| Tyler Higbee | 2, 0, 8, 5 | 3.5 | 5, 4, 6, 0 | 3.914 | 0.958 | 3.4 | 48% |
| Kyren Williams | 3, 2, 6, 10 | 4.5 | 0, 3, 6, 0 | 2.734 | 0.823 | 3.7 | 41% |

**LAR — Receiving yards**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Puka Nacua | 74, 125 | 99.5 | 58, 75, 142, 76 | 76.219 | 1.151 | 114.6 | 66% |
| Davante Adams | 26, 195, 137, 32 | 84.5 | 53, 32, 26, 40 | 42.008 | 0.899 | 75.9 | 46% |
| Konata Mumpfield | 0, 12, 93, 7 | 9.5 | 42, 53, 33, 66 | 24.352 | 1.992 | 18.9 | 59% |
| Tyler Higbee | 12, 0, 62, 67 | 37.0 | 62, 35, 52, 0 | 39.352 | 0.947 | 35.0 | 48% |
| Kyren Williams | 24, 12, 70, 67 | 45.5 | 0, 19, 61, 0 | 18.906 | 1.058 | 48.1 | 54% |

**LAR — Field goals (K)**

| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |
|---|---|---|---|---|---|---|---|
| Harrison Mevis | 0, 0, 4, 1 | 0.5 | 0, 1, 1, 3 | 1.734 | 0.721 | 0.4 | 47% |

## Usage checks (derived)

| Player | Targets/game | Catch % | Target share | Carry share | Mean off. snap % | Air yards | YAC |
|---|---|---|---|---|---|---|---|
| LAR Matthew Stafford | 0.0 | N/A | 0% | 10% | 96% | 0 | 0 |
| LAR Stetson Bennett IV | 0.0 | N/A | 0% | 1% | N/A | 0 | 0 |
| LAR Blake Corum | 1.8 | 57% | 4% | 31% | 28% | -2 | 23 |
| LAR Kyren Williams | 6.3 | 84% | 16% | 51% | 68% | 102 | 95 |
| LAR Ronnie Rivers | 0.5 | 100% | 1% | 5% | 7% | 2 | 3 |
| LAR Puka Nacua | 10.5 | 67% | 13% | 1% | 80% | 251 | 79 |
| LAR Davante Adams | 9.5 | 58% | 24% | 0% | 74% | 636 | 107 |
| LAR Davis Allen | 1.8 | 57% | 4% | 0% | 43% | 32 | 34 |
| LAR Tyler Higbee | 4.8 | 79% | 12% | 0% | 46% | 151 | 34 |
| LAR Jordan Whittington | 1.0 | 67% | 2% | 0% | 38% | 14 | 0 |
| LAR Colby Parkinson | 1.7 | 60% | 3% | 0% | 64% | 9 | 22 |
| LAR Terrance Ferguson | 4.0 | 58% | 8% | 0% | 45% | 79 | 38 |
| LAR Konata Mumpfield | 3.5 | 43% | 9% | 0% | 49% | 231 | 33 |
| BUF Josh Allen | 0.3 | 100% | 1% | 30% | 100% | -8 | 9 |
| BUF James Cook III | 2.5 | 60% | 9% | 64% | 68% | -8 | 27 |
| BUF Ray Davis | 0.3 | 100% | 1% | 2% | 10% | -7 | 11 |
| BUF Frank Gore Jr. | 0.0 | N/A | 0% | 1% | 16% | 0 | 0 |
| BUF Dalton Kincaid | 4.8 | 79% | 17% | 0% | 66% | 239 | 98 |
| BUF DJ Moore | 5.0 | 60% | 18% | 2% | 53% | 303 | 47 |
| BUF Khalil Shakir | 5.8 | 65% | 21% | 0% | 63% | 152 | 93 |
| BUF Joshua Palmer | 3.0 | 33% | 8% | 0% | N/A | 211 | 16 |
| BUF Dawson Knox | 1.5 | 100% | 5% | 1% | 69% | 11 | 19 |
| BUF Keon Coleman | 4.0 | 88% | 14% | 0% | 63% | 205 | 44 |
| LAR Tutu Atwell | 1.5 | 67% | 2% | 0% | 21% | 61 | 5 |
| LAR Xavier Smith | 0.3 | 0% | 1% | 0% | 37% | 0 | 0 |
| BUF Ty Johnson | 3.0 | 100% | 5% | 1% | 28% | 0 | 59 |
| BUF Jackson Hawes | 0.3 | 0% | 1% | 0% | 39% | 36 | 0 |
