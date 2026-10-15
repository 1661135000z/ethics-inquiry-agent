"""Evidence-derived discussion, information and readiness. No model calls or moral scoring."""
from copy import deepcopy
import hashlib,re
POLICY={'weights':{'role':2,'interests':1,'pressure':1,'evidence':3,'review':3},'breadth_weight':2,'conflict_weight':20,'stance_weight':10,'stakeholder_weight':10,'consequence_weight':10,'action_weight':10,'unknown_penalty':7,'max_penalty':21,'threshold':60,'ceiling':95}
def defs():
 from inquiry.analysis import DEFINITIONS
 return DEFINITIONS

def dimension_states(a):
 result={};eng=a.get('engagements',[])
 for area,d in defs().items():
  allfacts=[f for f in a.get('facts',[]) if f['area']==area];facts=[f for f in allfacts if f['status']=='active'];touches=[e for e in eng if e['area']==area]
  explored={f['facet'] for f in allfacts}|{e['facet'] for e in touches if e.get('facet') in d['facets']}
  info=set();declined=[]
  for facet in d['facets']:
   known=max((f['turn'] for f in facts if f['facet']==facet and f['kind']=='reported'),default=0)
   unknown=max([0]+[f['turn'] for f in facts if f['facet']==facet and f['kind']=='uncertain']+[e['turn'] for e in touches if e.get('facet')==facet and e['state']=='unknown'])
   if known>unknown:info.add(facet)
   latest=max((e for e in touches if e.get('facet')==facet),key=lambda e:e['turn'],default=None)
   if latest and latest['state']=='declined' and latest['turn']>=known:declined.append(facet)
  coverage=max(len(explored),1 if touches else 0)
  result[area]={'coverage':coverage,'information':len(info),'status':'substantial' if len(info)==3 else 'partial' if facts or touches else 'unexplored','explored':list(f for f in d['facets'] if f in explored),'unexplored':[f for f in d['facets'] if f not in explored],'supported':[f for f in d['facets'] if f in info],'known':[f['id'] for f in facts if f['kind']=='reported'],'uncertain':[f['id'] for f in facts if f['kind']=='uncertain'],'missing':[f for f in d['facets'] if f not in info],'declined':declined}
 return result

def short_response_state(text):
 normal=re.sub(r'[^\w\u3400-\u9fff]','',text.casefold())
 if normal in {'不知道','我不知道','我不确定','不确定','不清楚','我不清楚','不能确认','无法确认','idontknow','idonotknow','imnotsure','iamnotsure','icannotconfirm'}:return 'unknown'
 if normal in {'我不想回答','我不想讨论这个问题','不想回答','我不打算解决这个问题','不愿回答','idontwanttoanswer','idonotwanttoanswer','idontwanttodiscussthis','iprefertopass'}:return 'declined'
 return None

def record_engagements(a,updates,user_texts,previous_target=None):
 a=deepcopy(a);items=a.setdefault('engagements',[]);candidates=updates[:12] if isinstance(updates,list) else []
 if user_texts and isinstance(previous_target,dict) and previous_target.get('area') in defs():
  text=user_texts[-1];state=short_response_state(text)
  if state:candidates=[e for e in candidates if isinstance(e,dict) and e.get('turn')!=len(user_texts) and not (isinstance(e.get('quote'),str) and short_response_state(e['quote']))]+[dict(previous_target,quote=text,turn=len(user_texts),state=state)]
 for e in candidates:
  if not isinstance(e,dict):continue
  area,facet,quote,turn,state=(e.get(k) for k in ['area','facet','quote','turn','state'])
  if not isinstance(area,str) or area not in defs() or (facet is not None and (not isinstance(facet,str) or facet not in defs()[area]['facets'])) or (not isinstance(state,str) or state not in {'discussed','unknown','declined','position'}):continue
  if type(turn) is not int or not 1<=turn<=len(user_texts) or not isinstance(quote,str) or not 1<=len(quote)<=600 or quote not in user_texts[turn-1]:continue
  # Stable source identity and facet credit. Repeating a stance never fills more facets.
  canonical=re.sub(r'\W+','',quote.casefold())
  same=next((v for v in reversed(items) if v['area']==area and v.get('facet')==facet),None)
  if same and same['state']==state and re.sub(r'\W+','',same['quote'].casefold())==canonical and not any(f['area']==area and f['facet']==facet and f['turn']>same['turn'] and f['kind']=='reported' for f in a.get('facts',[])):continue
  eid='E'+hashlib.sha256(f'{area}|{facet}|{turn}|{state}|{canonical}'.encode()).hexdigest()[:12]
  if any(v['id']==eid for v in items):continue
  items.append(dict(id=eid,area=area,facet=facet,quote=quote,turn=turn,state=state))
 a['engagements']=items[-80:]
 return a

def target_for_question(value,focus,a):
 if focus not in defs():return None
 target=value.get('question_target')
 if isinstance(target,dict) and target.get('area')==focus and isinstance(target.get('facet'),str) and target['facet'] in defs()[focus]['facets']:return {'area':focus,'facet':target['facet']}
 # An old/free-text response has only an area, not an invented precise facet.
 return {'area':focus,'facet':None}

def update_context(a,value,user_texts):
 a=deepcopy(a);active=[f for f in a.get('facts',[]) if f['status']=='active'];context=deepcopy(a.get('context',{'signals':{},'critical_unknowns':[]}))
 if not isinstance(value,dict):a['context']=context;return a
 def source(item,reported=False):
  if not isinstance(item,dict) or not isinstance(item.get('summary'),str) or not 1<=len(item['summary'])<=250:return None
  q=item.get('basis_quotes',[])
  if not isinstance(q,list):return None
  ids=list(dict.fromkeys(f['id'] for quote in q if isinstance(quote,str) and quote.strip() and any(quote in t for t in user_texts) for f in active if (not reported or f['kind']=='reported') and (f['quote'] in quote or quote in f['quote'])))
  return {'summary':item['summary'],'basis':ids[:12]} if ids else None
 for k in ['conflict','stance','stakeholders','consequences']:
  if k in value:
   item=source(value[k],reported=True);context.setdefault('signals',{}).pop(k,None)
   if item:context['signals'][k]=item
 if 'critical_unknowns' in value and isinstance(value['critical_unknowns'],list):context['critical_unknowns']=[v for x in value['critical_unknowns'][:3] if (v:=source(x))]
 context['as_of_turn']=len(user_texts);a['context']=context;return a

def advice_readiness(a,dimensions=None):
 d=dimensions or dimension_states(a);facts=[f for f in a.get('facts',[]) if f['status']=='active'];byid={f['id']:f for f in facts};c=a.get('context',{});signals=c.get('signals',{})
 def anchored(v,sufficient=False):
  if not isinstance(v,dict) or not v.get('basis'):return False
  return all(fid in byid and (not sufficient or byid[fid]['facet'] in d[byid[fid]['area']]['supported']) for fid in v['basis'])
 def has(area,facet):return facet in d[area]['supported']
 conflict=anchored(signals.get('conflict'),True) or (has('role','decision') and (has('interests','influence') or has('pressure','incentive')))
 stance=anchored(signals.get('stance'),True) or any(e['state']=='position' and not any(v['area']==e['area'] and v.get('facet')==e.get('facet') and v['turn']>e['turn'] and v['state'] in {'unknown','declined'} for v in a.get('engagements',[])) for e in a.get('engagements',[]))
 stakeholders=anchored(signals.get('stakeholders'),True) or has('role','decision')
 consequences=anchored(signals.get('consequences'),True) or has('role','responsibility') or has('evidence','alternatives')
 action=has('evidence','basis') or has('review','route') or has('review','reviewer')
 info=sum(d[k]['information']*w for k,w in POLICY['weights'].items());breadth=sum(v['coverage']>0 for v in d.values())*POLICY['breadth_weight']
 critical=[v for v in c.get('critical_unknowns',[]) if anchored(v)]
 unknown_facets={(f['area'],f['facet']) for f in facts if f['kind']=='uncertain' and f['area'] in {'evidence','review'} and f['facet'] in d[f['area']]['missing']}|{(e['area'],e['facet']) for e in a.get('engagements',[]) if e['state']=='unknown' and e['area'] in {'evidence','review'} and e.get('facet') in d[e['area']]['missing']}
 penalty=min(POLICY['max_penalty'],max(len(critical),len(unknown_facets))*POLICY['unknown_penalty'])
 score=max(0,min(POLICY['ceiling'],info+breadth+20*conflict+10*stance+10*stakeholders+10*consequences+10*action-penalty))
 supported_areas=sum(v['information']>0 for v in d.values());eligible=bool(score>=POLICY['threshold'] and conflict and (stakeholders or consequences) and supported_areas>=2)
 # High discussion alone cannot masquerade as readiness.
 if not eligible:score=min(score,POLICY['threshold']-1)
 b=a.get('brief');stage='refining' if b and not b.get('stale') else 'initial' if eligible else 'exploring'
 return {'score':int(score),'eligible':eligible,'stage':stage,'criteria':{'conflict':bool(conflict),'stance':bool(stance),'stakeholders':bool(stakeholders),'consequences':bool(consequences),'action_basis':bool(action)},'critical_unknowns':critical,'unknown_count':max(len(critical),len(unknown_facets)),'information_points':info,'exploration_points':breadth,'penalty':penalty}


def source_turns(updates,user_texts):
 """Correct only uniquely provable source-turn labels; never guess ambiguous quotations."""
 if not isinstance(updates,list):return []
 clean=[]
 for u in updates[:12]:
  if not isinstance(u,dict):continue
  v=dict(u);quote=v.get('quote');turn=v.get('turn')
  if isinstance(quote,str) and quote.strip() and len(quote)<=600:
   valid=type(turn) is int and 1<=turn<=len(user_texts) and quote in user_texts[turn-1]
   if not valid:
    matches=[i+1 for i,text in enumerate(user_texts) if quote in text]
    if len(matches)==1:v['turn']=matches[0]
  clean.append(v)
 return clean

def respect_boundary(reply,focus,a,user_texts,prior_target):
 """One-call fallback when a model repeats the exact topic just declined/left unknown."""
 if not user_texts or not short_response_state(user_texts[-1]) or not isinstance(prior_target,dict) or a.get('question_target')!=prior_target or not any(c in reply for c in '?？'):return reply,focus,a
 questions={
 'role':('position','What decision is within your own authority?','哪些决定属于你的权限范围？'),
 'interests':('stake','Whose interests could be affected by this decision?','这个决定可能影响谁的利益？'),
 'pressure':('response','If anyone has made a request, what room do you have to respond?','如果有人提出了要求，你有哪些应对空间？'),
 'evidence':('basis','Which records or sources might help check the concern?','哪些资料或来源可以帮助核实这个疑虑？'),
 'review':('route','What independent reporting route could you explore?','你可以尝试什么独立的报告渠道？')}
 d=dimension_states(a)
 candidates=[area for area in ['evidence','review','role','interests','pressure'] if area!=prior_target.get('area') and questions[area][0] in d[area]['missing'] and questions[area][0] not in d[area]['declined']]
 if not candidates:return reply,focus,a
 area=candidates[0];facet,en,zh=questions[area];cn=a.get('language')=='中文'
 a['question_target']={'area':area,'facet':facet}
 # Acknowledge the boundary, replacing the repetitive question rather than adding a second.
 intro=('可以保留未知，先换一个角度。' if short_response_state(user_texts[-1])=='unknown' else '可以暂不讨论这一点，换一个角度。') if cn else ('We can leave that unknown and consider another angle. ' if short_response_state(user_texts[-1])=='unknown' else 'We can leave that topic aside and consider another angle. ')
 return intro+(zh if cn else en),area,a
