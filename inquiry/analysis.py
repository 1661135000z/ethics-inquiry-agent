"""Evidence-linked inquiry state. Coverage describes reported information, never truth/risk."""
from copy import deepcopy
import hashlib
import json
import re

# Three distinct information needs per existing area; no default classification.
DEFINITIONS = {
 'role': {'en':'Role & responsibility','zh':'角色与责任','facets':{
  'position':('Role and decision authority','角色及决策权限'),
  'decision':('The decision and affected stakeholders','待作判断及受影响者'),
  'responsibility':('Professional responsibilities and consequences','职业责任及可能后果')},
  'boundary':'Professional position, decision, duties and affected people. Friendship alone belongs to interests, not pressure.'},
 'interests': {'en':'Relationships & interests','zh':'关系与利益','facets':{
  'relationship':('Relevant personal or business ties, including explicit absence','相关私人或业务关系，包括明确不存在的关系'),
  'stake':('Who stands to gain or lose','谁可能得益或受损'),
  'influence':('How ties or interests could affect judgment','关系或利益怎样影响判断')},
  'boundary':'Friendship, kinship, commercial ties, stakes and bias. A university classmate is a relationship; it is not by itself a threat, incentive or promotion pressure.'},
 'pressure': {'en':'Pressure & incentives','zh':'压力与激励','facets':{
  'request':('A demand, deadline or explicit absence of pressure','要求、期限或明确没有压力'),
  'incentive':('Consequences, rewards or threats attached to the decision','与决定挂钩的后果、奖励或威胁'),
  'response':('How the person can respond to the pressure','当事人如何应对压力')},
  'boundary':'An actual demand/deadline or linked reward/threat (e.g. promotion tied to silence), and its effect. Mentioning a manager, responsibility, friendship or uncertainty alone is not pressure.'},
 'evidence': {'en':'Evidence & alternatives','zh':'证据与其他解释','facets':{
  'basis':('Available records and their reliability','已有资料及可靠性'),
  'uncertainty':('Known limits, competing explanations and how to verify them','已知局限、其他解释及核实方法'),
  'alternatives':('Possible actions, consequences and contrary evidence','可选行动、可能后果及相反证据')},
  'boundary':'Information quality, contrary evidence, uncertainty, options and consequences. Unknown is not proof of absence; acknowledging a limit can cover uncertainty only if the checking approach is also stated.'},
 'review': {'en':'Independent review','zh':'独立复核','facets':{
  'reviewer':('An independent person and their authority','独立复核人员及权限'),
  'route':('A usable reporting or escalation route','可用的报告或升级渠道'),
  'safeguard':('Feasible safeguards and their limits','可行应对措施及局限')},
  'boundary':'Independent checks, reporting routes, safeguards and their feasibility. Do not infer that a reviewer exists, is independent or has checked anything.'},
}

def empty_analysis():
 return {'schema':1,'facts':[],'dimensions':{},'ready':False,'brief':None,'language':'English','origin':'semantic'}

def fact_id(area,facet,quote,turn):
 return 'F'+hashlib.sha256((area+'|'+facet+'|'+normalise(quote)+'|'+str(turn)).encode()).hexdigest()[:12]

def normalise(text):
 return re.sub(r'\W+','',text.casefold())

def dimension_states(analysis):
 states={}
 for area,d in DEFINITIONS.items():
  facts=[f for f in analysis.get('facts',[]) if f['area']==area and f.get('status')=='active']
  covered={f['facet'] for f in facts if f['kind']=='reported'}
  missing=[f for f in d['facets'] if f not in covered]
  states[area]={'coverage':len(covered),'status':'substantial' if len(covered)==3 else 'partial' if facts else 'unexplored',
                'known':[f['id'] for f in facts if f['kind']=='reported'],
                'uncertain':[f['id'] for f in facts if f['kind']=='uncertain'],'missing':missing}
 return states

def finish(analysis):
 analysis['dimensions']=dimension_states(analysis)
 analysis['ready']=all(d['status']=='substantial' for d in analysis['dimensions'].values())
 return analysis

def apply_updates(previous,updates,user_texts):
 a=deepcopy(previous) if isinstance(previous,dict) and previous.get('schema')==1 else empty_analysis()
 facts=a['facts'];changed=False
 for u in updates[:18] if isinstance(updates,list) else []:
  if not isinstance(u,dict):continue
  area,facet,quote,turn,kind=(u.get(k) for k in ('area','facet','quote','turn','kind'))
  if not isinstance(area,str) or area not in DEFINITIONS or not isinstance(facet,str) or facet not in DEFINITIONS[area]['facets'] or not isinstance(kind,str) or kind not in {'reported','uncertain'}:continue
  if type(turn) is not int or not 1<=turn<=len(user_texts):continue
  if not isinstance(quote,str) or not 4<=len(quote)<=600 or quote not in user_texts[turn-1]:continue
  # Preserve explicit unknowns even if the model assigns the wrong epistemic kind.
  if re.search(r"(?:I |we )?(?:do not|don't|cannot|can't) (?:know|confirm)|not sure|不知道|不清楚|不能确认|无法确认|尚不确定",quote,re.I):kind='uncertain'
  # Only a current-message correction can displace the same area's earlier claim.
  replaced=[]
  for fid in u.get('replaces',[])[:5] if isinstance(u.get('replaces'),list) else []:
   old=next((f for f in facts if f['id']==fid),None)
   if old and turn==len(user_texts) and old['turn']<turn and old['area']==area and old['facet']==facet and old['status']=='active':
    replaced.append(old)
  canonical=normalise(quote)
  existing=next((f for f in facts if f['area']==area and f['facet']==facet and f['kind']==kind and f['status']=='active' and (canonical in normalise(f['quote']) or normalise(f['quote']) in canonical)),None)
  if existing and not replaced:continue
  fid=fact_id(area,facet,quote,turn)
  if any(f['id']==fid for f in facts):continue
  for old in replaced:old['status']='superseded';old['replaced_by']=fid
  basis=u.get('basis','')
  facts.append({'id':fid,'area':area,'facet':facet,'quote':quote,'turn':turn,'source':'initial' if turn==1 else 'answer',
                'kind':kind,'status':'active','basis':basis[:220] if isinstance(basis,str) else '', 'replaces':[f['id'] for f in replaced]})
  changed=True
 # Bound retained facts while prioritising active information. Keep stable IDs.
 if len(facts)>60:
  a['facts']=[f for f in facts if f['status']=='superseded'][-10:]+[f for f in facts if f['status']=='active'][-50:]
 if changed and a.get('brief'):a['brief']['stale']=True
 return finish(a)

def analysis_context(analysis,language):
 a=finish(deepcopy(analysis or empty_analysis()))
 definitions={k:{'definition':d['boundary'],'facets':{f:labels[0] for f,labels in d['facets'].items()}} for k,d in DEFINITIONS.items()}
 return ('Shared evidence state and information gaps (not a risk score; not a checklist). '
         'Use the full conversation to update this state BEFORE choosing the most useful follow-up. '
         'Personal ties do not establish pressure; a promotion threat does. Do not repeat answered facts. '
         'Unknowns need a verification path, not the same question again. Each area may progress differently. '
         'Respect the user\'s relevant new direction or request for advice. '
         +json.dumps({'definitions':definitions,'state':a,'response_language':language},ensure_ascii=False))

# Manually reviewed seed quotes, used only when present verbatim in the selected text.
SEEDS={
 'relationships':[
  ('role','position','I manage the audit of a listed company.','我是一家上市公司客户的审计经理。'),
  ('interests','relationship','Its CFO is a close friend from university.','CFO是我的大学好友。'),
  ('evidence','uncertainty','an aggressive revenue recognition judgment that may be defensible under the standard','一项激进、但可能有准则依据的收入确认判断'),
  ('pressure','incentive',"has hinted that next quarter's tax advisory renewal depends on a smooth audit",'暗示下季度税务咨询合同续约取决于审计是否顺利')],
 'controls':[
  ('role','decision','design a new internal-control system and subsequently audit it','设计新的内部控制系统，并在之后审计该系统'),
  ('interests','relationship','the same partner to lead both engagements','同一位合伙人领导两项业务'),
  ('pressure','request','The client asks for the same partner to lead both engagements to save time and fees.','为节省时间和费用，客户要求同一位合伙人领导两项业务。')],
 'dashboard':[
  ('role','position','I am an audit senior.','我是一名高级审计员。'),
  ('evidence','basis','a batch of manually uploaded entries is not visible in the dashboard','一批手工上传的分录没有显示在仪表盘里'),
  ('evidence','uncertainty','I do not know whether it was screened elsewhere.','不知道是否已在其他地方筛查'),
  ('pressure','request','The manager asks us to close the testing section today.','经理要求今天完成该部分测试')],
 'vendor':[
  ('role','decision','Our audit team is considering an AI tool recommended by a partner.','审计团队正在考虑合伙人推荐的一款AI工具。'),
  ('interests','stake','The vendor offers a referral reward to the firm if a client adopts it.','如果客户采用，供应商会向事务所提供推荐奖励。'),
  ('evidence','basis',"I have only seen the vendor's demonstration.",'我只看过供应商的演示')]
}

def seed_case(case,language):
 text=case.get('text_zh' if language=='中文' else 'text_en','')
 updates=[]
 for area,facet,en,zh in SEEDS.get(case.get('id'),[]):
  quote=zh if language=='中文' else en
  if quote in text:
   updates.append(dict(area=area,facet=facet,quote=quote,turn=1,kind='uncertain' if area=='evidence' and facet=='uncertainty' else 'reported',basis='情境原文明确提供此信息；尚未经独立核实。' if language=='中文' else 'Explicit initial scenario wording; not independently verified.'))
 a=apply_updates(empty_analysis(),updates,[text]);a['origin']='curated';a['language']=language
 return a

def wants_advice(text):
 return bool(re.search(r'建议|怎么办|怎么做|该如何|你会怎么|选哪个|recommend|advice|suggest|what should|what would you|which option|what can i do',text,re.I))

def validate_brief(value,analysis,user_texts,language):
 if not isinstance(value,dict) or not (analysis['ready'] or (user_texts and wants_advice(user_texts[-1]))):return None
 active=[f for f in analysis['facts'] if f['status']=='active']
 basis=value.get('basis_quotes',[])
 if not isinstance(basis,list):return None
 ids=list(dict.fromkeys(f['id'] for quote in basis if isinstance(quote,str) for f in active if quote==f['quote']))
 if not ids:return None
 def txt(x,n):return isinstance(x,str) and 1<=len(x)<=n and not re.search(r'https?://|<|>|(?:definitely|clearly) (?:ethical|unethical)|可以签字|已违反|构成违规',x,re.I)
 fields=('conflict','stakeholders','recommendation')
 if not all(txt(value.get(k),500) for k in fields):return None
 options=value.get('options',[]);unknowns=value.get('uncertainties',[])
 if not isinstance(options,list) or not 2<=len(options)<=3 or not all(isinstance(o,dict) and txt(o.get('action'),220) and txt(o.get('tradeoff'),300) for o in options):return None
 if not isinstance(unknowns,list) or not 1<=len(unknowns)<=4 or not all(txt(u,250) for u in unknowns):return None
 return {**{k:value[k] for k in fields},'options':[{'action':o['action'],'tradeoff':o['tradeoff']} for o in options],
         'uncertainties':unknowns,'basis':ids,'language':language,'stale':False,'as_of_turn':len(user_texts)}

def analysis_markdown(analysis,language='English'):
 zh=language=='中文';a=finish(deepcopy(analysis or empty_analysis()))
 lines=['# 五维信息与初步建议' if zh else '# Five-dimensional context and preliminary guidance',
        '信息覆盖不是事实核实或风险评分，仍需人工判断。' if zh else 'Context coverage is not verification and not a risk score. Human judgment remains necessary.']
 for area,d in DEFINITIONS.items():
  state=a['dimensions'][area];lines.append('\n## '+d['zh' if zh else 'en']+f" ({state['coverage']}/3)")
  for f in a['facts']:
   if f['area']==area and f['status']=='active':
    lines.append(f"[{f['id']}] "+('初始情境' if zh and f['turn']==1 else '第'+str(f['turn'])+'轮' if zh else 'Initial situation' if f['turn']==1 else 'Turn '+str(f['turn']))+' · '+('不确定' if zh and f['kind']=='uncertain' else f['kind'])+'\n> '+f['quote'].replace('\n','\n> '))
  missing=[d['facets'][f][int(zh)] for f in state['missing']]
  if missing:lines.append(('仍值得探索：' if zh else 'Still worth exploring: ')+'; '.join(missing))
 b=a.get('brief')
 if b:
  lines.append('\n## '+('有条件的初步建议' if zh else 'Conditional preliminary guidance'))
  if b['stale']:lines.append('新信息尚未重新评估。' if zh else 'New information has not yet been reassessed.')
  lines.extend([b['conflict'],b['stakeholders']])
  lines.extend(o['action']+' — '+o['tradeoff'] for o in b['options'])
  lines.extend([b['recommendation'],('未解决：' if zh else 'Unresolved: ')+'; '.join(b['uncertainties']),('依据：' if zh else 'Sources: ')+', '.join(b['basis'])])
 return '\n\n'.join(lines)
