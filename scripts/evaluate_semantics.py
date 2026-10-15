"""Opt-in, bounded live semantic smoke checks through normal public APIs. Never paid fallback."""
import argparse,asyncio,json,uuid
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
async def run(args):
 cases=json.loads((ROOT/'tests/semantic_cases.json').read_text())[:args.max_cases]
 async with httpx.AsyncClient(base_url=args.url.rstrip('/'),timeout=90) as client:
  config=(await client.get('/api/config')).json()
  provider=next(p for p in config['providers'] if p['id']==args.provider)
  if not provider['configured']:raise SystemExit('The server-side demonstration model is not configured. No key is read or requested by this script.')
  results=[]
  for case in cases:
   r=await client.post('/api/session',json={'new':True});r.raise_for_status();state=r.json()
   body=dict(provider=args.provider,model=provider['default_model'],language=case['language'],text=case['text'],consent=True,version=state['version'],request_id=uuid.uuid4().hex,case_id='blank',operation='submit')
   r=await client.post('/api/inquiry',json=body);r.raise_for_status();result=None;error=None
   for frame in r.text.split('\n\n'):
    event=next((l[7:] for l in frame.splitlines() if l.startswith('event: ')),None)
    data=next((l[6:] for l in frame.splitlines() if l.startswith('data: ')),None)
    if data and event=='complete':result=json.loads(data)
    if data and event=='error':error=json.loads(data)
   if error or not result:
    print(case['id']+': STOP '+json.dumps(error or {'code':'no_complete_event'},ensure_ascii=False));break
   a=result['session'].get('analysis',{});facts=a.get('facts',[])
   reported={f['area'] for f in facts if f['kind']=='reported' and f['status']=='active'}
   found={f['area'] for f in facts if f['status']=='active'}
   passed=set(case['required'])<=found and not (set(case['forbidden_reported'])&reported)
   results.append({'case':case['id'],'passed':passed,'analysis':a,'reply':result['session']['messages'][-1]['content']})
   print(case['id']+': '+('PASS' if passed else 'CHECK')+' '+','.join(sorted(found)),flush=True)
  if args.output:Path(args.output).write_text(json.dumps(results,ensure_ascii=False,indent=2))
  print(f'{len(results)} accepted cases. This is a small smoke sample, not an accuracy benchmark. No automatic retries or paid fallback.')
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--url',default='http://127.0.0.1:8788')
 parser.add_argument('--provider',choices=['gemini','zhipu'],default='gemini')
 parser.add_argument('--max-cases',type=int,choices=range(1,7),default=6)
 parser.add_argument('--output',help='Optional local fictional-result JSON; do not commit private histories.')
 asyncio.run(run(parser.parse_args()))
