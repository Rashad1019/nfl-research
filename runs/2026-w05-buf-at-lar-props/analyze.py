"""Reproduce Template B from frozen 2026 weeks 1–4 sources; stdlib only."""
import json,csv,gzip,math,statistics as S
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parent;D=ROOT/'data'
def norm(n):
 return ''.join(c for c in n.lower().replace('iii','').replace('jr.','').replace('sr.','') if c.isalpha()).replace('jamescook','jcook').replace('raydavis','rdavis').replace('rem ahn','')
def n(x):
 try:return float(x)
 except:return 0.
def canon(t):return {'LA':'LAR','WAS':'WSH','OAK':'LV','SD':'LAC','STL':'LAR'}.get(t,t)
positions={};names={}
for f in D.glob('roster_*.json'):
 for grp in json.loads(f.read_text())['athletes']:
  for a in grp['items']:
   positions[a['id']]=a['position']['abbreviation'];names[a['id']]=a['displayName']
snaps=defaultdict(dict)
for r in csv.DictReader((D/'snaps.csv').open()):
 if r['game_type']=='REG' and 1<=int(r['week'])<=4:
  snaps[canon(r['team']),norm(r['player'])][int(r['week'])]=r
# Fill absent historical roster positions with snap data.
namepos={norm(r['player']):r['position'] for r in csv.DictReader((D/'snaps.csv').open()) if r['game_type']=='REG'}
logs=defaultdict(list);teamgames=defaultdict(list);audit=[];allrows=[]
for f in sorted(D.glob('g_*.json')):
 d=json.loads(f.read_text());w=int(d['header']['week']);id=d['header']['id']
 ts=d['boxscore']['players'];teams=[x['team']['abbreviation'] for x in ts]
 for t in ts:
  tm=t['team']['abbreviation'];opp=next(x for x in teams if x!=tm);rows={}
  for s in t['statistics']:
   if s['name'] not in ['passing','rushing','receiving','kicking']:continue
   for a in s['athletes']:
    at=a['athlete'];pid=at['id'];name=at['displayName'];pos=positions.get(pid,namepos.get(norm(name),'?'))
    r=rows.setdefault(pid,dict(id=pid,name=name,pos=pos,team=tm,opp=opp,week=w,event=id))
    for k,v in zip(s['keys'],a['stats']):
     if k=='completions/passingAttempts':r['cmp'],r['att']=map(n,v.split('/'))
     elif k=='fieldGoalsMade/fieldGoalAttempts':r['fgm'],r['fga']=map(n,v.split('/'))
     elif k=='extraPointsMade/extraPointAttempts':r['xpm'],r['xpa']=map(n,v.split('/'))
     else:r[k]=n(v)
  # Normalize alternate kicker keys by label.
  for s in t['statistics']:
   if s['name']=='kicking':
    for a in s['athletes']:
     r=rows[a['athlete']['id']];r['fgm'],r['fga']=map(n,a['stats'][0].split('/'));r['xpm'],r['xpa']=map(n,a['stats'][3].split('/'));r['pos']='K'
  for r in rows.values():
   r['combined']=r.get('rushingYards',0)+r.get('receivingYards',0)
   r['td']=r.get('rushingTouchdowns',0)+r.get('receivingTouchdowns',0)
   logs[tm,r['name']].append(r);allrows.append(r)
  # Same-game slot ranks: WR/TE targets, RB carries, all ties by yards then name.
  slots={}
  for pos,k,yk in [('WR','receivingTargets','receivingYards'),('TE','receivingTargets','receivingYards'),('RB','rushingAttempts','rushingYards'),('QB','att','passingYards'),('K','fga','fgm')]:
   rs=sorted([r for r in rows.values() if r['pos']==pos],key=lambda r:(-r.get(k,0),-r.get(yk,0),r['name']))
   for ix,r in enumerate(rs):slots[f'{pos}{ix+1}']=r
  stats=next(x['statistics'] for x in d['boxscore']['teams'] if x['team']['abbreviation']==tm)
  teamstat={x['name']:x['displayValue'] for x in stats}
  teamgames[tm].append(dict(week=w,opp=opp,event=id,rows=list(rows.values()),slots=slots,stats=teamstat))
  for cat,key in [('passing','passingYards'),('rushing','rushingYards'),('receiving','receivingYards')]:
   s=next(x for x in t['statistics'] if x['name']==cat)
   ix=s['keys'].index(key);su=sum(n(a['stats'][ix]) for a in s['athletes']);tot=n(s['totals'][ix])
   if su!=tot:audit.append(dict(team=tm,week=w,stat=key,player_sum=su,team_total=tot))
# ESPN game sum 176 matches PFR; preserve nflverse discrepancy in audit.
corrections=[]
for tm,gs in teamgames.items():gs.sort(key=lambda g:g['week'])
# Participation supplies zero-stat active games, never fills missed games with zero.
players={}
for (tm,name),rs in logs.items():
 if tm not in ['BUF','LAR']:continue
 rs.sort(key=lambda r:r['week']);sp=snaps.get((tm,norm(name)),{})
 weeks=set(sp)|{r['week'] for r in rs}
 for w in weeks:
  if not any(r['week']==w for r in rs):
   g=next(x for x in teamgames[tm] if x['week']==w)
   rs.append(dict(id=rs[0]['id'],name=name,pos=rs[0]['pos'],team=tm,opp=g['opp'],week=w,event=g['event']))
 rs.sort(key=lambda r:r['week'])
 players[tm,name]=dict(name=name,pos=rs[0]['pos'],games=len(rs),logs=rs,snaps=sp)
# Rank only active candidates; questionable Moore included conditionally.
selected={}
for tm in ['BUF','LAR']:
 ps=[v for (t,name),v in players.items() if t==tm and name not in ['Joshua Palmer','Terrance Ferguson','Ronnie Rivers','Frank Gore Jr.']]
 group={}
 for pos,key in [('WR','receivingTargets'),('TE','receivingTargets'),('RB','rushingAttempts'),('QB','att'),('K','fga')]:
  ss=sorted([p for p in ps if p['pos']==pos],key=lambda p:(-sum(r.get(key,0) for r in p['logs'])/p['games'],-sum(r.get(key,0) for r in p['logs']),-sum(r.get('receivingYards',0) for r in p['logs']),p['name']))
  for i,p in enumerate(ss):p['slot']=f'{pos}{i+1}'
  group[pos]=ss[:{'WR':3,'TE':1,'RB':2,'QB':1,'K':1}[pos]]
 selected[tm]=group
# League same-slot baselines; absent slots contribute zero to all 128 team-games.
keys=['passingYards','att','cmp','passingTouchdowns','rushingYards','rushingAttempts','combined','receptions','receivingYards','fgm']
league={}
for sl in ['QB1','RB1','RB2','WR1','WR2','WR3','TE1','K1']:
 league[sl]={k:S.mean(g['slots'].get(sl,{}).get(k,0) for gs in teamgames.values() for g in gs) for k in keys}
def defense(opp,slot,key):return [g['slots'].get(slot,{}).get(key,0) for gs in teamgames.values() for g in gs if g['opp']==opp]
categories=[('Passing yards','passingYards','QB'),('Pass attempts','att','QB'),('Completions','cmp','QB'),('TDs thrown','passingTouchdowns','QB'),('Rushing yards','rushingYards','rush'),('Rush attempts','rushingAttempts','rush'),('Rush + rec yards','combined','RB'),('Receptions','receptions','rec'),('Receiving yards','receivingYards','rec'),('Field goals (K)','fgm','K')]
results={}
for tm,group in selected.items():
 opp='LAR' if tm=='BUF' else 'BUF';cats={}
 for title,key,pool in categories:
  if pool=='rush':ps=group['RB']+([group['QB'][0]] if sum(r.get('rushingAttempts',0)>0 for r in group['QB'][0]['logs'])>group['QB'][0]['games']/2 else [])
  elif pool=='rec':
   rb=max([v for (t,_),v in players.items() if t==tm and v['pos']=='RB'],key=lambda p:sum(r.get('receivingTargets',0) for r in p['logs']))
   ps=group['WR']+group['TE']+[rb]
  else:ps=group[pool]
  out=[]
  for p in ps:
   slot=p['slot'];vs=[r.get(key,0) for r in p['logs']];median=S.median(vs);sd=S.stdev(vs) if len(vs)>1 else 0
   allowed=defense(opp,slot,key);baseline=league[slot][key];factor=S.mean(allowed)/baseline if baseline else None
   proj=median*factor if factor is not None else None
   chance=.5*(1+math.erf((proj-median)/sd/math.sqrt(2))) if sd and proj is not None else None
   out.append(dict(player=p['name'],slot=slot,games=p['games'],median=median,projection=proj,chance=chance,matchup=factor,sd=sd,log=vs,defense_log=allowed,league=baseline))
  cats[title]=dict(top_number=max(out,key=lambda r:r['projection'] if r['projection'] is not None else -1),best_chance=max(out,key=lambda r:r['chance'] if r['chance'] is not None else -1),all=out)
 results[tm]=cats
# PBP: second-feed audit, red-zone touches, distance kicking, passing role context.
pbp=[]
with gzip.open(D/'pbp.csv.gz','rt') as f:
 for r in csv.DictReader(f):
  if r['season_type']=='REG' and 1<=n(r['week'])<=4 and canon(r['posteam']) in ['BUF','LAR'] and r['play_type']!='no_play' and not n(r.get('two_point_attempt')):pbp.append(r)
rz=defaultdict(lambda:defaultdict(lambda:defaultdict(int)));pbplayers=defaultdict(lambda:defaultdict(float));kicks=defaultdict(list)
for r in pbp:
 tm=canon(r['posteam']);w=int(r['week']);yd=n(r['yardline_100'])
 for pkey in ['rusher','receiver','passer']:
  pn=r.get(pkey+'_player_name','')
  if not pn:continue
  vals=pbplayers[tm,w,pn]
  if pkey=='rusher' and n(r['rush_attempt']):
   vals['rushingAttempts']+=1;vals['rushingYards']+=n(r['rushing_yards']);vals['rushingTouchdowns']+=n(r['rush_touchdown'])
   for cutoff in [10,20]:
    if r['yardline_100'] and yd<=cutoff:rz[tm][pn][str(cutoff)]+=1
  elif pkey=='receiver' and n(r['pass_attempt']) and not n(r['sack']):
   vals['receivingTargets']+=1;vals['receptions']+=n(r['complete_pass']);vals['receivingYards']+=n(r['receiving_yards']);vals['receivingTouchdowns']+=n(r['pass_touchdown'])
   vals['air_yards']+=n(r['air_yards']);vals['yac']+=n(r['yards_after_catch'])
   for cutoff in [10,20]:
    if r['yardline_100'] and yd<=cutoff and n(r['complete_pass']):rz[tm][pn][str(cutoff)]+=1
  elif pkey=='passer' and n(r['pass_attempt']) and not n(r['sack']):
   vals['att']+=1;vals['cmp']+=n(r['complete_pass']);vals['passingYards']+=n(r['passing_yards']);vals['passingTouchdowns']+=n(r['pass_touchdown'])
 if n(r['field_goal_attempt']):kicks[tm].append(dict(week=w,distance=n(r['kick_distance']),made=r['field_goal_result']=='made'))
def short(name):
 parts=name.replace(' III','').replace(' Jr.','').split();return parts[0][0]+'.'+parts[-1]
# Match short names against full names; Cook and Davis use nflverse short spelling.
def findpb(tm,name):
 candidates={pn for t,w,pn in pbplayers if t==tm};expected=short(name)
 return next((pn for pn in candidates if norm(pn)==norm(expected)),None)
pbpcheck=[]
for (tm,name),p in players.items():
 pn=findpb(tm,name)
 if pn is None:continue
 for r in p['logs']:
  for key in ['passingYards','att','cmp','passingTouchdowns','rushingYards','rushingAttempts','rushingTouchdowns','receptions','receivingYards','receivingTouchdowns']:
   a=r.get(key,0);b=pbplayers[tm,r['week'],pn].get(key,0)
   if a!=b:pbpcheck.append(dict(team=tm,player=name,week=r['week'],stat=key,espn=a,nflverse=b))
a=json.loads((D/'template_a_result.json').read_text())['games'][0];tds={};context={}
for tm,side in [('BUF','away'),('LAR','home')]:
 projected=(a['proj']['raw'][side]+a['proj']['adj'][side])/2;ppg=a['teams'][tm]['espn']['pf']
 totaltd=sum(r.get('td',0) for g in teamgames[tm] for r in g['rows']);teamproj=totaltd/len(teamgames[tm])*projected/ppg
 touches=sum(v['10'] for v in rz[tm].values());tdout=[]
 eligible={p['name']:p for cat in results[tm].values() for r in cat['all'] for p in [players[tm,r['player']]] if p['pos']!='K'}
 for name,p in eligible.items():
  pn=findpb(tm,name);touch=rz[tm].get(pn,{}).get('10',0);td=sum(r.get('td',0) for r in p['logs']);share=(td/totaltd+touch/touches)/2;exp=teamproj*share
  tdout.append(dict(player=name,td=td,touches10=touch,touches20=rz[tm].get(pn,{}).get('20',0),expected=exp,chance=1-math.exp(-exp),games=p['games']))
 tds[tm]=sorted(tdout,key=lambda r:-r['chance']);context[tm]=dict(projected_points=projected,ppg=ppg,team_td=totaltd,projected_td=teamproj,touches10=touches,kicks=kicks[tm])
usage={}
for (tm,name),p in players.items():
 if p['pos'] not in ['QB','RB','WR','TE']:continue
 gs=teamgames[tm];targets=sum(x.get('receivingTargets',0) for x in p['logs']);rec=sum(x.get('receptions',0) for x in p['logs']);carries=sum(x.get('rushingAttempts',0) for x in p['logs']);pn=findpb(tm,name)
 total_targets=sum(x.get('receivingTargets',0) for g in gs for x in g['rows']);total_carries=sum(x.get('rushingAttempts',0) for g in gs for x in g['rows'])
 usage[tm+' '+name]=dict(targets=targets,targets_per_game=targets/p['games'],catch_rate=rec/targets if targets else None,target_share=targets/total_targets if total_targets else None,carry_share=carries/total_carries,mean_offense_snap_pct=S.mean(n(x['offense_pct']) for x in p['snaps'].values()) if p['snaps'] else None,air_yards=sum(v.get('air_yards',0) for (t,w,pp),v in pbplayers.items() if t==tm and pp==pn),yac=sum(v.get('yac',0) for (t,w,pp),v in pbplayers.items() if t==tm and pp==pn))
output=dict(usage=usage,method='Weeks 1–4 only. Same-slot ESPN league denominators; sample SD; neutral script multiplier 1.00 because Template A projects a close game. Model chances are chances to beat own median, not a sportsbook line. TD touches = rushes plus completed receptions at or inside 10; no pass attempts. Participation from nflverse/PFR snaps.',league_games=sum(map(len,teamgames.values()))/2,results=results,tds=tds,context=context,league=league,boxscore_disagreements=audit,corrections=corrections,pbp_disagreements=pbpcheck,players={tm:{name:p for (t,name),p in players.items() if t==tm} for tm in ['BUF','LAR']},defense={tm:[g for gs in teamgames.values() for g in gs if g['opp']==tm] for tm in ['BUF','LAR']})
(ROOT/'result.json').write_text(json.dumps(output,indent=2));print('games',output['league_games'],'box disagreements',len(audit),'PBP disagreements',len(pbpcheck));print('PBP differences',pbpcheck[:25]);print('TD',tds)
for tm,cats in results.items():
 print(tm)
 for title,cat in cats.items():
  print(title,[(lab,r['player'],r['games'],r['median'],round(r['projection'],2),round(r['chance']*100) if r['chance'] is not None else None) for lab,r in cat.items() if lab!='all'])
