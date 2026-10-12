import json,math,statistics as S
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
P=Path(__file__).resolve().parent;r=json.loads((P/'result.json').read_text())
def f(x,d=1):return str(Decimal(str(x)).quantize(Decimal('1').scaleb(-d),rounding=ROUND_HALF_UP))
def pct(x):return f(x*100,0)+'%' if x is not None else 'N/A'
def ls(xs):return ', '.join(f(x,0) for x in xs)
def link(g):return f"https://www.espn.com/nfl/boxscore/_/gameId/{g['event']}"
book={'Josh Allen':-118,'James Cook III':-118,'DJ Moore':185,'Keon Coleman':260,'Dalton Kincaid':165,'Kyren Williams':-185,'Puka Nacua':-125,'Davante Adams':-105}
notes={
'Josh Allen':'Rams suppress passing yardage; rushing and goal-line work are the better fit. Both starting QBs are cleared. KILLS IT: sacks and stalled drives prevent red-zone visits.',
'James Cook III':'Leads Buffalo carries, but every Rams lead back stayed below his rushing median. Palmer is out; Moore questionable. KILLS IT: Buffalo trails and abandons the run; Allen takes goal-line scores.',
'Ray Davis':'Wins a chance ranking only against a tiny personal median; Ty Johnson is ahead on the depth chart. KILLS IT: no offensive touches. This is not a recommended prop.',
'Keon Coleman':'Highest BUF receiving projection comes from the WR3 comparison; Palmer is out. Moore playing is an assumption. KILLS IT: Moore sits, Coleman moves to WR2, and the favorable comparison disappears.',
'Khalil Shakir':'Ranks WR1 by targets per appearance, although he lines up in the slot. Rams WR1 yardage has been low. KILLS IT: short catches with little yardage after the catch.',
'DJ Moore':'Questionable shoulder; ranks WR2 only if active without a new restriction. KILLS IT: limited snaps or inactive. No bet before status confirmation.',
'Dalton Kincaid':'Rams have limited their opponents’ most-targeted TEs; early production inflates Buffalo’s season baseline. KILLS IT: extra protection duties and targets shared with Knox.',
'Tyler Bass':'A close game supports late kicks, but the model does not project two makes. KILLS IT: touchdowns or fourth-down attempts replace field goals.',
'Matthew Stafford':'Buffalo has consistently allowed passing volume; a close game keeps both offenses involved. No QB injury designation. KILLS IT: Rams establish a lead and run, cutting attempts.',
'Kyren Williams':'Top Rams back by carries and receiving workload; Oliver is out for Buffalo. Run-yard matchup is less favorable than the TD role. KILLS IT: Corum gets the carries or Stafford throws the scores.',
'Blake Corum':'BUF RB2 production lifts the formula, but Corum’s recent workload is falling. No injury-based promotion. KILLS IT: Williams retains nearly all meaningful touches.',
'Puka Nacua':'Highest targets per appearance and favorable BUF WR1 catches; active after missing two games. LOW CONFIDENCE: two games. KILLS IT: reduced workload or Adams commands targets.',
'Davante Adams':'WR2 comparison reflects Nacua’s return; the two games without Nacua overstate his current opportunity. KILLS IT: Nacua dominates and Williams finishes drives.',
'Konata Mumpfield':'WR3 by target rate; may encounter Buffalo’s questionable nickel position. No verified individual coverage weakness. KILLS IT: low target volume behind the stars.',
'Tyler Higbee':'Ferguson’s absence helps opportunity, but Parkinson is cleared and BUF TE production is inconsistent. KILLS IT: split routes or blocking assignments.',
'Harrison Mevis':'Buffalo has rarely forced multiple field-goal attempts; recent four-make game is an outlier. KILLS IT: touchdowns replace kicks.'}
lines=['# Template B — BUF at LAR', '', 'Monday, October 12, 2026, 8:15 p.m. ET · SoFi Stadium. Research cutoff: October 11 ET. Current-season weeks 1–4 only.', '', '**Research shortlist: Stafford passing, Coleman receiving (conditional on Moore playing), and Allen/Cook/Kyren touchdown roles. No confirmed bets: live prices and full source verification are incomplete, and the TD model materially disagrees with the published market.**','',
'**Read the percentages correctly:** chance means beating that player’s own season median, not clearing a sportsbook line. T = TOP NUMBER; C = BEST CHANCE; T/C = both. WR1/2/3 are target rankings, not field alignment. All medians, projections, percentages and matchup factors below are **derived** from the linked game logs. These are uncalibrated small-sample model outputs.', '',
'**Method:** projection = median × opponent same-slot average / league same-slot average; chance = Φ((projection − median)/sample SD). League baseline uses 64 completed games / 128 team-games through Week 4, not the older skill’s stated 65. Missing participation games are excluded; active zero-stat games are included using nflverse/PFR snap records. PFR position tables were blocked, so same-slot ESPN league baselines are the disclosed fallback. QB1 means most pass attempts; RB1/2 use carries; WR/TE use targets, ties by yards. A missing slot counts zero in the league denominator. Zero SD yields N/A, never an invented percentage.', '',
'**Game script:** average the saved Template A raw and adjusted team points; apply no extra numerical script adjustment because the projected game is close (multiplier 1.00). Injuries are qualitative flags, not arbitrary boosts. [Template A source](../2026-w05-buf-at-lar/result.json).', '']
lines.append('Derived score context: '+', '.join(t+' '+f(r['context'][t]['projected_points']) for t in ['BUF','LAR'])+'.')
for tm in ['BUF','LAR']:
 lines+=['',f'## {tm}', '', '| Category | Player | Slot | Games | Median | Projection | Chance | Matchup |','|---|---|---|---|---|---|---|---|']
 for title,c in r['results'][tm].items():
  picks=[('T/C',c['top_number'])] if c['top_number']['player']==c['best_chance']['player'] else [('T',c['top_number']),('C',c['best_chance'])]
  for lab,x in picks:
   name=x['player'].replace(' III','');lines.append(f"| {title} {lab} | {name} | {x['slot']} | {x['games']} | {f(x['median'])} | {f(x['projection'])} | {pct(x['chance'])} | {f(x['matchup'],2)} |")
 lines+=['','**TOP 3 TD SCORERS — derived Poisson estimates**','', '| Player | Expected TDs | Chance | Why |','|---|---|---|---|']
 top=r['tds'][tm][:3]
 if tm=='BUF':top=[next(x for x in r['tds'][tm] if x['player']==name) for name in ['Josh Allen','James Cook III','Keon Coleman']]
 for x in top:lines.append(f"| {x['player']} | {f(x['expected'],2)} | {pct(x['chance'])} | {f(x['td'],0)} TDs; {x['touches10']} touches inside 10 |")
 if tm=='BUF':lines+=['','Third place is tied: Coleman, Kincaid and Moore have identical model estimates. Coleman is shown because Moore is questionable; this is not a statistical advantage over Kincaid.']
 c=r['context'][tm];lines+=['',f"**TD math (derived):** team TDs = ({f(c['team_td'],0)} ÷ 4) × ({f(c['projected_points'],5)} ÷ {f(c['ppg'],2)}) = {f(c['projected_td'],4)}. Player share = ½ × (player TDs / {f(c['team_td'],0)} + player inside-10 touches / {c['touches10']}). Expected TDs = team TDs × player share; chance = 1 − exp(−expected TDs). Touches are rushes plus completed receptions, not targets; passing TDs do not count for the passer’s anytime TD. No redistribution of injured players’ TD shares. Puka’s missed games can depress his share.", '', '**WHY / KILLS IT**', '']
 names=sorted({x['player'] for c in r['results'][tm].values() for x in [c['top_number'],c['best_chance']]}|{x['player'] for x in top})
 for name in names:lines.append('- **'+name+':** '+notes[name])
 opp='LAR' if tm=='BUF' else 'BUF';gs=sorted(r['defense'][opp],key=lambda g:g['week'])
 lines+=['',f'**DEFENSE — {opp}, opponent by opponent.** C/A = completions/attempts. RB = most carries; WR = most targets, ties by yards. Each row links to its ESPN box score.', '', '| Opponent | QB: C/A, yards, TD | Lead RB: carries/yards | WR1: catches/yards | TE1: catches/yards |','|---|---|---|---|---|']
 for g in gs:
  q=g['slots']['QB1'];rb=g['slots']['RB1'];wr=g['slots']['WR1'];te=g['slots']['TE1'];lines.append(f"| [{q['team']}]({link(g)}) | {q['name']}: {f(q['cmp'],0)}/{f(q['att'],0)}, {f(q['passingYards'],0)}, {f(q['passingTouchdowns'],0)} | {rb['name']}: {f(rb.get('rushingAttempts',0),0)}/{f(rb.get('rushingYards',0),0)} | {wr['name']}: {f(wr.get('receptions',0),0)}/{f(wr.get('receivingYards',0),0)} | {te['name']}: {f(te.get('receptions',0),0)}/{f(te.get('receivingYards',0),0)} |")
 lines+=['','**Defense counts (derived):**']
 for slot,key,mark,label in [('QB1','passingYards',225.5,'QB passing yards >225.5'),('QB1','cmp',19.5,'QB completions >19.5'),('QB1','passingTouchdowns',1.5,'QB pass TDs >1.5'),('RB1','rushingYards',59.5,'lead-RB rush yards >59.5'),('RB2','rushingYards',29.5,'RB2 rush yards >29.5'),('WR1','receptions',5.5,'WR1 catches >5.5'),('WR3','receivingYards',39.5,'WR3 receiving yards >39.5')]:
  vs=[g['slots'].get(slot,{}).get(key,0) for g in gs];lines.append(f'- {label}: {sum(v>mark for v in vs)}/{len(vs)}; log {ls(vs)}. These are screening marks, not quoted book lines.')
 k=r['results'][tm]['Field goals (K)']['top_number']['player'];p=r['players'][tm][k];ks=c['kicks'];attempts=[x.get('fga',0) for x in p['logs']];makes=[x.get('fgm',0) for x in p['logs']];oppatt=[g['slots']['K1'].get('fga',0) for g in gs]
 lines+=['',f"**KICKER — {k}:** FG makes {ls(makes)}; attempts {ls(attempts)}. Median attempts {f(S.median(attempts))}; XP {f(sum(x.get('xpm',0) for x in p['logs']),0)}/{f(sum(x.get('xpa',0) for x in p['logs']),0)}. Opponent allowed 2+ FGA in {sum(v>=2 for v in oppatt)}/4 games ({ls(oppatt)}), {f(S.mean(oppatt))} FGA/game."]
 for lo,hi,label in [(0,40,'under 40'),(40,50,'40–49'),(50,100,'50+')]:
  kk=[x for x in ks if lo<=x['distance']<hi];lines.append(f'- {label} yards: {sum(x["made"] for x in kk)}/{len(kk)} made; '+(pct(sum(x['made'] for x in kk)/len(kk)) if kk else 'no attempts')+'.')
 # Team games are the opposing-defense records stored under the other team.
 own=[g for gs2 in r['defense'].values() for g in gs2 if g['slots']['QB1']['team']==tm]
 # Those lists contain opponents, not BUF/LAR; use original eight boxscore team stats instead.
 ownstats=[]
 for fpath in (P/'data').glob('g_*.json'):
  dd=json.loads(fpath.read_text())
  for tt in dd['boxscore']['teams']:
   if tt['team']['abbreviation']==tm:ownstats.append({a['name']:a['displayValue'] for a in tt['statistics']})
 def rzstats(ss):
  vals=[list(map(float,s['redZoneAttempts'].split('-'))) for s in ss];return sum(v[0] for v in vals),sum(v[1] for v in vals)
 made,att=rzstats(ownstats);oppmade,opptrips=rzstats([g['stats'] for g in gs]);trips=(att/4+opptrips/4)/2;rate=(made/att+oppmade/opptrips)/2;stalls=trips*(1-rate)
 lines+=['',f"**Kicker stress test (derived):** offense RZ TDs {f(made,0)}/{f(att,0)} ({pct(made/att)}), {f(att/4)} trips/game; opponent allows {f(oppmade,0)}/{f(opptrips,0)} ({pct(oppmade/opptrips)}). Averaged trip expectation {f(trips,2)} × (1 − averaged TD rate {pct(rate)}) = {f(stalls,2)} non-TD red-zone possessions. This is an opportunity proxy, not guaranteed FG attempts: turnovers and fourth-down tries consume some. Longer kicks cannot be forecast reliably from this sample. Roof limits direct rain; field-level wind was not verified. No kicker over recommended."]
lines+=['','## WATCH, market check and stress tests','',
'- **Stafford:** favorable defense does not validate the extreme yardage projection. BetMGM’s October 7 article lists 282.5 yards, 36.5 attempts, 23.5 completions and 2.5 passing TDs; the article has an incorrect ET kickoff label, and its lines are not a live quote. No over/under prices were available in that article. [Book source](https://sports.betmgm.com/en/blog/nfl/matthew-stafford-props-odds-gaa/).',
'- **Coleman:** Moore active is essential to the WR3 comparison. If Moore is out, Coleman moves to WR2 and the model must be rerun; Bell is next behind Moore on the depth chart but lacks a verified four-game receiving sample. Palmer’s absence can add Coleman routes, but no fixed target boost is invented.',
'- **Puka: LOW CONFIDENCE.** Only two appearances. Corum’s early split differs from the current workload. Ray Davis’s small median can produce a good chance ranking without meaningful projected yardage.',
'- **Injuries:** BUF Oliver and Palmer out; Moore, Alford and Landon Jackson questionable. LAR Donald, Parkinson and Watson cleared; Lake questionable. Ferguson unavailable. Official updates override older injury labels on Ourlads. [Bills](https://www.buffalobills.com/news/buffalo-bills-injury-report-vs-rams-week-5), [Rams](https://www.therams.com/news/rams-injury-report-week-5-2026-vs-bills-aaron-donald-colby-parkinson-and-jaylen-watson-good-to-go-for-monday-night-football).',
'- **Coverage:** Ourlads lists Shakir in the slot, Coleman left and Moore right; Rams McDuffie right CB, Watson left CB, Wallace nickel. BUF Benford left CB, Hairston right CB, Alford nickel; Rams Mumpfield in the slot. These are alignment starting points, not shadow assignments. Individual current-season targets/catches/yards/TDs/rating allowed were not verified, so no weak-defender claim or numerical boost is made. [BUF depth](https://www.ourlads.com/nfldepthcharts/depthchart/BUF), [LAR depth](https://www.ourlads.com/nfldepthcharts/depthchart/LAR).','']
# Scripted conservative sensitivity, labeled analyst assumptions.
stress={'Stafford completions':(60*.60-3,.60),'Coleman catches':(4,.60),'Puka catches':(8,.60),'Corum rush yards':(5,3.5),'Cook rush yards':(12,4.)}
for name,(a,b) in stress.items():lines.append(f'- **Stress scenario, analyst assumptions — {name}:** {f(a)} × {f(b,2)} = {f(a*b)}. '+('First term = 60 plays × 60% dropbacks − 3 sacks/scrambles.' if name.startswith('Stafford') else 'Targets × catch rate, or carries × yards/carry.')+' The optimistic projection does not survive every realistic script.')
lines+=['','**Published anytime TD prices (October 11 article; not verified live).** Implied probabilities calculated from prices, with vig still included. They are not fair probabilities. Large disagreement blocks a confident recommendation under the skill’s book-first rule.', '', '| Player | Model | Book | Implied | Gap |','|---|---|---|---|---|']
for tm in ['BUF','LAR']:
 for x in r['tds'][tm]:
  if x['player'] not in book:continue
  od=book[x['player']];im=abs(od)/(abs(od)+100) if od<0 else 100/(od+100)
  lines.append(f"| {x['player']} | {pct(x['chance'])} | {od:+} | {pct(im)} | {f((x['chance']-im)*100)} pts |")
lines+=['','[BetMGM TD source](https://sports.betmgm.com/en/blog/nfl/bills-rams-first-anytime-td-odds-picks-week-5-gaa/). Prices only; the article’s historical trends were not used.', '',
'## Data checks and missing research','',
'- ESPN game-by-game sums agree with FootballDB’s season totals for Allen passing (1,039 yards, 79/119, six TDs), Stafford passing (1,189 yards, 99/162, six TDs), Cook rushing (421), and Puka receiving (14/199 on 21 targets). These are partial independent checks, not completion of the strict PFR + FootballDB every-game requirement.',
'- Shakir discrepancy: ESPN game log sums to 176 yards, matching PFR/NFL season totals; nflverse play sums give 166, including 40 rather than 50 in Week 1. Use ESPN’s game sum and flag it. All other tested BUF/LAR player passing/rushing/receiving yardage, attempts, completions and TD logs agree across ESPN and nflverse. Feeds may share the same upstream NFL scorer, so this is not a substitute for full independent verification.',
'- ESPN passing total rows sometimes use net yards while individual rows use gross yards. Those differences are retained in result.json; the player props use gross individual passing yards. Receiving and rushing rows matched their own total rows before the audit. PFR’s BUF QB allowed totals match the four-game ESPN sum; LAR PFR lists 615 QB yards, which includes the backup Dart’s 20; starter-only comparator is explicitly separate.',
'- PFR team pages, red-zone and advanced-defense direct requests returned 403; FootballDB direct team-stat requests returned 403. Some player totals and snap pages were available through indexed web results. NFLverse player_stats_2026.csv returned 404; ESPN boxes, nflverse play-by-play and snap-count CSV were used instead.',
'- Not verified: every player’s PFR/FootballDB box-score cross-check, all defensive-position season totals, individual coverage metrics, ESPN block/run-stop win rates, Next Gen separation and yards before contact (page failed), Sharp explosive/directional metrics, confirmed coordinator game-plan quotes, live multi-book lines/movement, final inactives and field-level wind. No old-season data filled these gaps.',
'- Categories are modeled independently and are not an internally reconciled stat line: Cook’s combined-yard projection is below his rush-yard projection. That inconsistency is another reason to treat this as a screening run, not a betting forecast.',
'- The normal approximation is only the requested ranking formula. It is not calibrated for low discrete counts, and the TD share formula can assign zero to players who still have a real scoring chance. Model outputs should not be used as certainty or automatically converted into bets.', '',
'## Sources and reproducibility','',
'- [Allen second source](https://www.footballdb.com/players/josh-allen-allenjo06); [Stafford second source](https://www.footballdb.com/players/matthew-stafford-staffma01); [Cook/team totals](https://www.footballdb.com/teams/nfl/buffalo-bills); [Puka games](https://www.footballdb.com/players/puka-nacua-nacuapu01); [Shakir PFR](https://www.pro-football-reference.com/players/S/ShakKh00.htm).',
'- [nflverse play-by-play](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz); [nflverse/PFR participation](https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_2026.csv).',
'- ESPN per-game source links are in both defense tables; all 64 league snapshots and 32 rosters are frozen under data/. StatRankings and Template A frozen inputs are also retained.',
'- Reproduce: python3 runs/2026-w05-buf-at-lar-props/analyze.py then python3 runs/2026-w05-buf-at-lar-props/build.py. Fetch script is provenance only; do not refetch over this frozen run.', '',
'## Appendix: every checked player and calculation','']
for tm,cats in r['results'].items():
 for cat,c in cats.items():
  lines+=['',f'**{tm} — {cat}**','', '| Player | Games log | Median | Opp slot log | League avg | Factor | Projection | Chance |','|---|---|---|---|---|---|---|---|']
  for x in c['all']:lines.append(f"| {x['player']} | {ls(x['log'])} | {f(x['median'])} | {ls(x['defense_log'])} | {f(x['league'],3)} | {f(x['matchup'],3)} | {f(x['projection'])} | {pct(x['chance'])} |")
lines+=['', '## Usage checks (derived)', '', '| Player | Targets/game | Catch % | Target share | Carry share | Mean off. snap % | Air yards | YAC |', '|---|---|---|---|---|---|---|---|']
for name,u in r['usage'].items():
 lines.append(f"| {name} | {f(u['targets_per_game'])} | {pct(u['catch_rate'])} | {pct(u['target_share'])} | {pct(u['carry_share'])} | {pct(u['mean_offense_snap_pct'])} | {f(u['air_yards'],0)} | {f(u['yac'],0)} |")
(P/'props.md').write_text('\n'.join(lines)+'\n')
print('Wrote props.md',len(lines),'lines')
