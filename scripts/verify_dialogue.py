"""Opt-in public-demo multi-turn check. Stops on first failure; never invokes paid backup."""
import argparse,asyncio,json,uuid
from pathlib import Path
import httpx
INPUTS=[
'I am the audit manager. The CFO is a university friend and wants me to accept a revenue judgment before Friday. He linked next quarter’s advisory renewal to a smooth audit. I must decide whether to seek independent review; investors could rely on this report.',
'I do not know',
'I think my own career matters more. Losing the client could hurt my promotion, but I do not know whether that is an explicit threat.',
'I do not want to discuss my friendship further.',
'I can compare signed contracts with the ledger. The audit committee can review concerns without the CFO. Please give conditional initial advice.',
'I prefer a documented independent review because investors could be harmed. I have not checked whether the committee is independent.',
'The committee chair may also be involved. That is a concern, not a confirmed fact. How would this change your advice?',
'I am willing to accept personal career risk, but I cannot accept inventing evidence.',
'I can request signed delivery records. I cannot yet establish whether all records are complete.',
'Could you compare requesting more time with escalating now?',
'I can ask for two more days. The CFO has not agreed to that extension.',
'I am not sure',
'I could document the disagreement and consult an independent partner who has not worked on this client.',
'The partner may have authority to pause sign-off; I need to confirm that authority.',
'Please update the preliminary guidance and make the most important remaining uncertainty explicit.',
'I now learned that the ledger extract excludes the last two days. My earlier statement about available records was incomplete.',
'I would seek the missing extract before relying on it. If it cannot be obtained, I would record that limitation.',
'If the deadline stays unchanged, what is the most cautious feasible next step?',
'I will compare the complete records, document the concern, and ask the independent partner to review. This is my plan, not a completed action.',
'Please summarise one or two conditional actions, the main trade-off and the unresolved point, then ask one useful follow-up.'
]
async def run(args):
 async with httpx.AsyncClient(base_url=args.url.rstrip('/'),timeout=90,headers={'User-Agent':'Inquire acceptance check'}) as client:
  config=(await client.get('/api/config')).json();p=next(v for v in config['providers'] if v['id']==args.provider)
  if not p['configured']:raise SystemExit('Server demo not configured; no credentials are read by this check.')
  state=(await client.post('/api/session',json={})).json();results=[];failure=None
  for i,text in enumerate(INPUTS[:args.turns],1):
   response=await client.post('/api/inquiry',json=dict(provider=args.provider,model=p['default_model'],language='English',consent=True,version=state['version'],request_id=uuid.uuid4().hex,text=text,case_id='blank'))
   complete=None
   for frame in response.text.replace('\r\n','\n').split('\n\n'):
    lines=frame.splitlines();event=next((v[7:] for v in lines if v.startswith('event: ')),None);data=next((v[6:] for v in lines if v.startswith('data: ')),None)
    if data and event=='complete':complete=json.loads(data)
    if data and event=='error':failure=json.loads(data)
   if not complete:
    if not failure:
     try:failure=response.json().get('error',{'code':'http','status':response.status_code})
     except ValueError:failure={'code':'no_complete','status':response.status_code}
    print(f'{args.provider} turn {i}: STOP '+json.dumps(failure,ensure_ascii=False),flush=True);break
   state=complete;a=state['session']['analysis'];r=a.get('readiness',{})
   results.append(dict(turn=i,input=text,reply=state['session']['messages'][-1]['content'],analysis=a))
   print(f"{args.provider} turn {i}: accepted; readiness={r.get('score')} eligible={r.get('eligible')} brief={bool(a.get('brief'))}",flush=True)
  # Save fictional results only: never session token, cookie, access code or key.
  report=dict(provider=args.provider,accepted=len(results),requested=args.turns,failure=failure,turns=results)
  if args.output:Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2))
  print('No automatic retries or paid fallback. Provider and deployment quotas still apply.')
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url',required=True);parser.add_argument('--provider',choices=['gemini','zhipu'],required=True);parser.add_argument('--turns',type=int,choices=range(1,21),default=20);parser.add_argument('--output');asyncio.run(run(parser.parse_args()))
