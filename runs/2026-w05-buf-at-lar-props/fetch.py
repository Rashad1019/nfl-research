import concurrent.futures,json,urllib.request,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=ROOT/'data';D.mkdir(exist_ok=True)
OLD=ROOT.parent/'2026-w05-buf-at-lar'
UA={'User-Agent':'Mozilla/5.0'}
jobs=[]
for w in range(1,5):
 p=OLD/f'data/espn/wk{w}.json';shutil.copy2(p,D/p.name)
 for e in json.loads(p.read_text())['events']:
  if e['status']['type']['completed']:
   id=e['id'];dest=D/f'g_{id}.json'
   old=OLD/f'data/espn/g_{id}.json'
   if old.exists():shutil.copy2(old,dest)
   else:jobs.append((f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={id}',dest))
teams={}
for p in D.glob('wk*.json'):
 for e in json.loads(p.read_text())['events']:
  for c in e['competitions'][0]['competitors']:teams[c['team']['id']]=c['team']['abbreviation']
for id,t in teams.items():jobs.append((f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{id}/roster?season=2026',D/f'roster_{t}.json'))
jobs += [('https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2026.csv.gz',D/'pbp.csv.gz')]
shutil.copy2(OLD/'result.json',D/'template_a_result.json')
shutil.copy2(OLD/'data/sr_data.json',D/'sr_data.json')
def fetch(x):
 u,p=x
 try:
  if not p.exists():p.write_bytes(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=50).read())
  return {'url':u,'file':p.name,'bytes':p.stat().st_size}
 except Exception as e:return {'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:res=list(pool.map(fetch,jobs))
(D/'fetch_log.json').write_text(json.dumps(res,indent=2))
print('Fetched',sum('error' not in r for r in res),'of',len(res));print([r for r in res if 'error' in r])
