import {dimensionView,dimensionDefinitions} from './analysis';
import type {Snapshot} from './state';
export const areas=Object.entries(dimensionDefinitions).map(([id,d])=>({id,zh:d.zh,en:d.en}));
export function quoteSource(snapshot:Snapshot,quote:string){let turn=0;for(const message of snapshot.session.messages){if(message.role==='user'){turn++;if(quote&&message.content.includes(quote))return turn}}return null;}
export function clueGroups(snapshot:Snapshot){return areas.map(area=>{
 const facts=snapshot.session.analysis?.facts.filter(f=>f.area===area.id&&f.status==='active');
 return {...area,quotes:facts?facts.map(f=>({...f,sourceId:f.id,turn:f.turn})):
 snapshot.session.observations.filter(o=>o.area===area.id).map(o=>({...o,sourceId:`S${String(snapshot.session.observations.indexOf(o)+1).padStart(2,'0')}`,turn:quoteSource(snapshot,o.quote),kind:'reported',basis:'',facet:'',source:'answer'}))};
});}

export function stats(snapshot:Snapshot,provider:string){const accepted=snapshot.session.messages.filter(m=>m.role==='user').length,cap=provider==='deepseek'?10:20;return {accepted,cap,remaining:Math.max(0,cap-accepted),attempts:snapshot.attempts,statements:snapshot.session.observations.length};}
export function stageState(current:string,stage:string):'active'|'complete'|'waiting'{const stages=['input','request','validate','commit'];if(current==='done')return 'complete';if(current===stage)return 'active';return stages.indexOf(current)>stages.indexOf(stage)?'complete':'waiting';}

export function radarData(snapshot:Snapshot){
 const semantic=!!snapshot.session.analysis;
 const groups=clueGroups(snapshot),scale=semantic?3:Math.max(3,Math.ceil(Math.max(0,...groups.map(g=>g.quotes.length))/3)*3);
 const axes=groups.map((g,i)=>{
  const dimension=dimensionView(snapshot,g.id);
  const angle=-Math.PI/2+i*Math.PI*2/5,count=g.quotes.length,ratio=(semantic?dimension.coverage:count)/scale;
  const at=(r:number):[number,number]=>[120+Math.cos(angle)*r,85+Math.sin(angle)*r];
  return {...g,...dimension,count,ratio,point:at(58*ratio),end:at(58),label:at(76)};
 });
 const grid=[1/3,2/3,1].map(r=>axes.map((_,i)=>{const angle=-Math.PI/2+i*Math.PI*2/5;return `${120+Math.cos(angle)*58*r},${85+Math.sin(angle)*58*r}`}).join(' '));
 return {axes,scale,grid,points:axes.map(a=>a.point.join(',')).join(' ')};
}
