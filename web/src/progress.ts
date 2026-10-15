import definitions from './dimensions.json';
import policy from './readiness-policy.json';
import type {Analysis} from './analysis';
export type Engagement={id:string;area:string;facet:string|null;quote:string;turn:number;state:'discussed'|'unknown'|'declined'|'position'};
export type ContextSignal={summary:string;basis:string[]};
export type ReadinessContext={signals:Partial<Record<'conflict'|'stance'|'stakeholders'|'consequences',ContextSignal>>;critical_unknowns:ContextSignal[];as_of_turn?:number};
export function dimensionState(a:Analysis,area:string){
 const d=definitions[area as keyof typeof definitions],facets=Object.keys(d.facets),allfacts=a.facts.filter(f=>f.area===area),facts=allfacts.filter(f=>f.status==='active'),engagements=(a.engagements||[]).filter(e=>e.area===area);
 const explored=new Set([...allfacts.map(f=>f.facet),...engagements.flatMap(e=>e.facet&&facets.includes(e.facet)?[e.facet]:[])]),supported:string[]=[],declined:string[]=[];
 for(const facet of facets){const known=Math.max(0,...facts.filter(f=>f.facet===facet&&f.kind==='reported').map(f=>f.turn));const unknown=Math.max(0,...facts.filter(f=>f.facet===facet&&f.kind==='uncertain').map(f=>f.turn),...engagements.filter(e=>e.facet===facet&&e.state==='unknown').map(e=>e.turn));if(known>unknown)supported.push(facet);
 const latest=engagements.filter(e=>e.facet===facet).reduce<Engagement|undefined>((old,e)=>!old||e.turn>old.turn?e:old,undefined);if(latest?.state==='declined'&&latest.turn>=known)declined.push(facet);
 }
 return {facts,known:facts.filter(f=>f.kind==='reported'),uncertain:facts.filter(f=>f.kind==='uncertain'),engagements,coverage:Math.max(explored.size,engagements.length?1:0),information:supported.length,supported,explored:facets.filter(f=>explored.has(f)),unexplored:facets.filter(f=>!explored.has(f)),missing:facets.filter(f=>!supported.includes(f)),declined,status:supported.length===3?'substantial':facts.length||engagements.length?'partial':'unexplored'};
}
export function readinessForAnalysis(a:Analysis){
 const d=Object.fromEntries(Object.keys(definitions).map(k=>[k,dimensionState(a,k)])),facts=a.facts.filter(f=>f.status==='active'),byid=new Map(facts.map(f=>[f.id,f])),signals=a.context?.signals||{};
 const anchored=(v:ContextSignal|undefined,sufficient=false)=>!!v?.basis?.length&&v.basis.every(id=>{const f=byid.get(id);return !!f&&(!sufficient||d[f.area].supported.includes(f.facet))});
 const has=(area:string,facet:string)=>d[area].supported.includes(facet);
 const conflict=anchored(signals.conflict,true)||(has('role','decision')&&(has('interests','influence')||has('pressure','incentive')));
 const stance=anchored(signals.stance,true)||(a.engagements||[]).some(e=>e.state==='position'&&!(a.engagements||[]).some(v=>v.area===e.area&&v.facet===e.facet&&v.turn>e.turn&&['unknown','declined'].includes(v.state)));
 const stakeholders=anchored(signals.stakeholders,true)||has('role','decision'),consequences=anchored(signals.consequences,true)||has('role','responsibility')||has('evidence','alternatives'),action=has('evidence','basis')||has('review','route')||has('review','reviewer');
 const info=Object.entries(policy.weights).reduce((n,[k,w])=>n+d[k].information*w,0),breadth=Object.values(d).filter(v=>v.coverage>0).length*policy.breadth_weight;
 const critical=(a.context?.critical_unknowns||[]).filter(v=>anchored(v)),unknown=new Set([...facts.filter(f=>f.kind==='uncertain'&&['evidence','review'].includes(f.area)&&d[f.area].missing.includes(f.facet)).map(f=>f.area+':'+f.facet),...(a.engagements||[]).filter(e=>e.state==='unknown'&&['evidence','review'].includes(e.area)&&!!e.facet&&d[e.area].missing.includes(e.facet)).map(e=>e.area+':'+e.facet)]);
 const unknown_count=Math.max(critical.length,unknown.size),penalty=Math.min(policy.max_penalty,unknown_count*policy.unknown_penalty);
 let score=Math.max(0,Math.min(policy.ceiling,info+breadth+20*Number(conflict)+10*Number(stance)+10*Number(stakeholders)+10*Number(consequences)+10*Number(action)-penalty));
 const eligible=score>=policy.threshold&&conflict&&(stakeholders||consequences)&&Object.values(d).filter(v=>v.information>0).length>=2;if(!eligible)score=Math.min(score,policy.threshold-1);
 return {score,eligible,stage:a.brief&&!a.brief.stale?'refining':eligible?'initial':'exploring',criteria:{conflict,stance,stakeholders,consequences,action_basis:action},critical_unknowns:critical,unknown_count,information_points:info,exploration_points:breadth,penalty};
}
export type AdviceReadiness=ReturnType<typeof readinessForAnalysis>;
