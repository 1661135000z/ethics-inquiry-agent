import {dimensionState,readinessForAnalysis,type Engagement,type ReadinessContext,type AdviceReadiness} from './progress';
import definitions from './dimensions.json';
import type {Message,Snapshot} from './state';
import type {Case} from './api';
export const dimensionDefinitions=definitions;
export type Fact={id:string;area:string;facet:string;quote:string;turn:number;source:'initial'|'answer';kind:'reported'|'uncertain';status:'active'|'superseded';basis:string;replaces:string[];replaced_by?:string};
export type DecisionBrief={conflict:string;stakeholders:string;options:{action:string;tradeoff:string}[];recommendation:string;uncertainties:string[];basis:string[];language:string;stale:boolean;as_of_turn:number};
export type Analysis={schema:1;facts:Fact[];ready:boolean;brief:DecisionBrief|null;language:string;origin:string;engagements?:Engagement[];context?:ReadinessContext;question_target?:{area:string;facet:string|null}|null;readiness?:AdviceReadiness};
export const blankAnalysis=():Analysis=>({schema:1,facts:[],ready:false,brief:null,language:'English',origin:'semantic',engagements:[],context:{signals:{},critical_unknowns:[]}});
export function dimensionView(snapshot:Snapshot,area:string){return dimensionState(snapshot.session.analysis||blankAnalysis(),area)}
export function isReady(snapshot:Snapshot){return Object.keys(definitions).every(id=>dimensionView(snapshot,id).information===3)}
export function facetLabel(area:string,facet:string,zh:boolean){const d=definitions[area as keyof typeof definitions];const labels=d.facets[facet as keyof typeof d.facets] as [string,string]|undefined;return labels?.[zh?1:0]||facet}
/** Copy only declared, source-checked fields. Never treat cached completion flags as authority. */
export function cleanAnalysis(raw:unknown,messages:Message[]):Analysis|undefined{
 if(!raw||typeof raw!=='object')return;
 const a=raw as Analysis;if(a.schema!==1||!Array.isArray(a.facts)||a.facts.length>60)return;
 const users=messages.filter(m=>m.role==='user');const safe=blankAnalysis();
 const str=(v:unknown,n:number):v is string=>typeof v==='string'&&v.length<=n;
 for(const f of a.facts){
  if(!f||!str(f.id,50)||safe.facts.some(v=>v.id===f.id)||!Object.hasOwn(definitions,f.area))continue;
  const def=definitions[f.area as keyof typeof definitions];
  if(!Object.hasOwn(def.facets,f.facet)||!str(f.quote,600)||f.quote.length<1||!Number.isInteger(f.turn)||f.turn<1||!users[f.turn-1]?.content.includes(f.quote)||!['reported','uncertain'].includes(f.kind)||!['active','superseded'].includes(f.status))continue;
  safe.facts.push({id:f.id,area:f.area,facet:f.facet,quote:f.quote,turn:f.turn,source:f.turn===1?'initial':'answer',kind:f.kind,status:f.status,basis:str(f.basis,220)?f.basis:'',replaces:Array.isArray(f.replaces)?f.replaces.filter((s:unknown)=>str(s,50)).slice(0,5):[],...(str(f.replaced_by,50)?{replaced_by:f.replaced_by}:{})});
 }
 safe.engagements=[];
 for(const e of Array.isArray(a.engagements)?a.engagements.slice(-80):[]){
  if(!e||!str(e.id,50)||safe.engagements.some(v=>v.id===e.id)||!Object.hasOwn(definitions,e.area)||e.facet!==null&&(!str(e.facet,50)||!Object.hasOwn(definitions[e.area as keyof typeof definitions].facets,e.facet))||!str(e.quote,600)||!e.quote.length||!Number.isInteger(e.turn)||e.turn<1||!users[e.turn-1]?.content.includes(e.quote)||!['discussed','unknown','declined','position'].includes(e.state))continue;
  safe.engagements.push({id:e.id,area:e.area,facet:e.facet,quote:e.quote,turn:e.turn,state:e.state});
 }
 const signal=(v:unknown)=>{if(!v||typeof v!=='object')return;const s=v as {summary:unknown;basis:unknown};if(str(s.summary,250)&&s.summary.length&&Array.isArray(s.basis)&&s.basis.length>0&&s.basis.length<=12&&s.basis.every(id=>typeof id==='string'&&safe.facts.some(f=>f.id===id)))return {summary:s.summary,basis:s.basis as string[]}};
 safe.context={signals:{},critical_unknowns:[]};
 if(a.context&&typeof a.context==='object'){
  for(const k of ['conflict','stance','stakeholders','consequences'] as const){const v=signal(a.context.signals?.[k]);if(v)safe.context.signals[k]=v}
  safe.context.critical_unknowns=(Array.isArray(a.context.critical_unknowns)?a.context.critical_unknowns:[]).slice(0,3).flatMap(v=>{const s=signal(v);return s?[s]:[]});
  if(Number.isInteger(a.context.as_of_turn)&&a.context.as_of_turn!>0&&a.context.as_of_turn!<=users.length)safe.context.as_of_turn=a.context.as_of_turn;
 }
 const target=a.question_target;
 if(target&&typeof target.area==='string'&&Object.hasOwn(definitions,target.area)&&(target.facet===null||typeof target.facet==='string'&&Object.hasOwn(definitions[target.area as keyof typeof definitions].facets,target.facet)))safe.question_target={area:target.area,facet:target.facet};
 safe.language=a.language==='中文'?'中文':'English';safe.origin=a.origin==='curated'?'curated':'semantic';
 const stub={session:{analysis:safe}} as Snapshot;safe.ready=isReady(stub);
 const b=a.brief;
 if(b&&['conflict','stakeholders','recommendation'].every(k=>str(b[k as keyof DecisionBrief],500))&&Array.isArray(b.options)&&b.options.length>=1&&b.options.length<=3&&b.options.every(o=>o&&str(o.action,220)&&str(o.tradeoff,300))&&Array.isArray(b.uncertainties)&&b.uncertainties.length<=4&&b.uncertainties.every(u=>str(u,250))&&Array.isArray(b.basis)&&b.basis.length>0&&b.basis.every(id=>safe.facts.some(f=>f.id===id))&&Number.isInteger(b.as_of_turn)&&b.as_of_turn<=users.length){
  safe.brief={conflict:b.conflict,stakeholders:b.stakeholders,recommendation:b.recommendation,options:b.options.map(o=>({action:o.action,tradeoff:o.tradeoff})),uncertainties:b.uncertainties,basis:b.basis,language:b.language==='中文'?'中文':'English',as_of_turn:b.as_of_turn,stale:b.stale===true||b.basis.some(id=>safe.facts.find(f=>f.id===id)?.status!=='active')};
 }
 safe.readiness=readinessForAnalysis(safe);
 return safe;
}
export function scenarioSnapshot(c:Case|undefined,text:string,zh:boolean):Snapshot{
 const en=c&&text.trim()===c.text_en.trim(),cn=c&&text.trim()===c.text_zh.trim();
 const raw=text.trim()?(cn?c?.analysis_zh:en?c?.analysis_en:undefined):undefined;
 const messages:Message[]=text?[{role:'user',content:text}]:[];
 const analysis=cleanAnalysis(raw,messages)||blankAnalysis();
 if(!raw)analysis.origin='pending';
 return {version:0,attempts:0,initial_text:text,case_id:c?.id||'blank',session:{messages:[],records:[],focus:'scope',observations:analysis.facts.filter(f=>f.status==='active').map(f=>({area:f.area,quote:f.quote})),analysis}};
}

export function analysisMarkdown(snapshot:Snapshot,zh:boolean):string{
 const a=snapshot.session.analysis;if(!a)return '';
 const lines=[zh?'## 五维信息与初步建议':'## Five-dimensional context and guidance',zh?'探索覆盖记录讨论，信息充分度记录有据内容；均非核实或伦理评分。':'Exploration records discussion; information records supported context. Neither is verification or a moral score.'];
 for(const [area,d] of Object.entries(definitions)){
  const state=dimensionView(snapshot,area);lines.push(`### ${zh?d.zh:d.en} — ${zh?'探索':'Exploration'} ${Math.round(state.coverage/3*100)}%; ${zh?'信息':'Information'} ${state.information}/3`);
  for(const f of a.facts.filter(f=>f.area===area))lines.push(`[${f.id}] ${f.source==='initial'?(zh?'初始情境':'Initial situation'):(zh?'轮次 ':'Turn ')+f.turn} · ${f.kind==='uncertain'?(zh?'不确定':'Uncertain'):(zh?'用户陈述':'Reported')} ${f.status==='superseded'?(zh?'· 已被更正':'· Superseded'):''}\n> ${f.quote.replace(/\n/g,'\n> ')}`);
  if(state.missing.length)lines.push((zh?'仍值得探索：':'Still worth exploring: ')+state.missing.map(f=>facetLabel(area,f,zh)).join('; '));
 }
 const b=a.brief;if(b){lines.push(zh?'### 有条件的初步建议':'### Conditional preliminary guidance');if(b.stale)lines.push(zh?'本轮尚待重新评估。':'Awaiting reassessment.');lines.push(b.conflict,b.stakeholders,...b.options.map(o=>o.action+' — '+o.tradeoff),b.recommendation,(zh?'尚未解决：':'Unresolved: ')+b.uncertainties.join('; '),(zh?'依据：':'Sources: ')+b.basis.join(', '));}
 return lines.join('\n\n');
}
