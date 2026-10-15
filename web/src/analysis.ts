import definitions from './dimensions.json';
import type {Message,Snapshot} from './state';
import type {Case} from './api';
export const dimensionDefinitions=definitions;
export type Fact={id:string;area:string;facet:string;quote:string;turn:number;source:'initial'|'answer';kind:'reported'|'uncertain';status:'active'|'superseded';basis:string;replaces:string[];replaced_by?:string};
export type DecisionBrief={conflict:string;stakeholders:string;options:{action:string;tradeoff:string}[];recommendation:string;uncertainties:string[];basis:string[];language:string;stale:boolean;as_of_turn:number};
export type Analysis={schema:1;facts:Fact[];ready:boolean;brief:DecisionBrief|null;language:string;origin:string};
export const blankAnalysis=():Analysis=>({schema:1,facts:[],ready:false,brief:null,language:'English',origin:'semantic'});
export function dimensionView(snapshot:Snapshot,area:string){
 const def=definitions[area as keyof typeof definitions],facts=(snapshot.session.analysis?.facts||[]).filter(f=>f.area===area&&f.status==='active');
 const covered=new Set(facts.filter(f=>f.kind==='reported').map(f=>f.facet));
 const missing=Object.keys(def.facets).filter(k=>!covered.has(k));
 return {facts,known:facts.filter(f=>f.kind==='reported'),uncertain:facts.filter(f=>f.kind==='uncertain'),missing,coverage:covered.size,status:covered.size===3?'substantial':facts.length?'partial':'unexplored'};
}
export function isReady(snapshot:Snapshot){return Object.keys(definitions).every(id=>dimensionView(snapshot,id).status==='substantial')}
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
  if(!Object.hasOwn(def.facets,f.facet)||!str(f.quote,600)||f.quote.length<4||!Number.isInteger(f.turn)||f.turn<1||!users[f.turn-1]?.content.includes(f.quote)||!['reported','uncertain'].includes(f.kind)||!['active','superseded'].includes(f.status))continue;
  safe.facts.push({id:f.id,area:f.area,facet:f.facet,quote:f.quote,turn:f.turn,source:f.turn===1?'initial':'answer',kind:f.kind,status:f.status,basis:str(f.basis,220)?f.basis:'',replaces:Array.isArray(f.replaces)?f.replaces.filter((s:unknown)=>str(s,50)).slice(0,5):[],...(str(f.replaced_by,50)?{replaced_by:f.replaced_by}:{})});
 }
 safe.language=a.language==='中文'?'中文':'English';safe.origin=a.origin==='curated'?'curated':'semantic';
 const stub={session:{analysis:safe}} as Snapshot;safe.ready=isReady(stub);
 const b=a.brief;
 if(b&&['conflict','stakeholders','recommendation'].every(k=>str(b[k as keyof DecisionBrief],500))&&Array.isArray(b.options)&&b.options.length>=2&&b.options.length<=3&&b.options.every(o=>o&&str(o.action,220)&&str(o.tradeoff,300))&&Array.isArray(b.uncertainties)&&b.uncertainties.length<=4&&b.uncertainties.every(u=>str(u,250))&&Array.isArray(b.basis)&&b.basis.length>0&&b.basis.every(id=>safe.facts.some(f=>f.id===id))&&Number.isInteger(b.as_of_turn)&&b.as_of_turn<=users.length){
  safe.brief={conflict:b.conflict,stakeholders:b.stakeholders,recommendation:b.recommendation,options:b.options.map(o=>({action:o.action,tradeoff:o.tradeoff})),uncertainties:b.uncertainties,basis:b.basis,language:b.language==='中文'?'中文':'English',as_of_turn:b.as_of_turn,stale:b.stale===true||b.basis.some(id=>safe.facts.find(f=>f.id===id)?.status!=='active')};
 }
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
 const lines=[zh?'## 五维信息与初步建议':'## Five-dimensional context and guidance',zh?'信息覆盖不是事实核实或风险评分。':'Context coverage is not independent verification or a risk score.'];
 for(const [area,d] of Object.entries(definitions)){
  const state=dimensionView(snapshot,area);lines.push(`### ${zh?d.zh:d.en} (${state.coverage}/3)`);
  for(const f of a.facts.filter(f=>f.area===area))lines.push(`[${f.id}] ${f.source==='initial'?(zh?'初始情境':'Initial situation'):(zh?'轮次 ':'Turn ')+f.turn} · ${f.kind==='uncertain'?(zh?'不确定':'Uncertain'):(zh?'用户陈述':'Reported')} ${f.status==='superseded'?(zh?'· 已被更正':'· Superseded'):''}\n> ${f.quote.replace(/\n/g,'\n> ')}`);
  if(state.missing.length)lines.push((zh?'仍值得探索：':'Still worth exploring: ')+state.missing.map(f=>facetLabel(area,f,zh)).join('; '));
 }
 const b=a.brief;if(b){lines.push(zh?'### 有条件的初步建议':'### Conditional preliminary guidance');if(b.stale)lines.push(zh?'本轮尚待重新评估。':'Awaiting reassessment.');lines.push(b.conflict,b.stakeholders,...b.options.map(o=>o.action+' — '+o.tradeoff),b.recommendation,(zh?'尚未解决：':'Unresolved: ')+b.uncertainties.join('; '),(zh?'依据：':'Sources: ')+b.basis.join(', '));}
 return lines.join('\n\n');
}
