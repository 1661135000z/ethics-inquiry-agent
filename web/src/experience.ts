import type {Snapshot} from './state';
export const areas=[{id:'role',zh:'角色与判断',en:'Role & judgment'},{id:'interests',zh:'关系与利益',en:'Interests & relationships'},{id:'pressure',zh:'压力与激励',en:'Pressure & incentives'},{id:'evidence',zh:'证据与解释',en:'Evidence & explanations'},{id:'review',zh:'独立复核',en:'Independent review'}];
export function quoteSource(snapshot:Snapshot,quote:string){let turn=0;for(const message of snapshot.session.messages){if(message.role==='user'){turn++;if(quote&&message.content.includes(quote))return turn}}return null;}
export function clueGroups(snapshot:Snapshot){return areas.map(area=>({...area,quotes:snapshot.session.observations.filter(o=>o.area===area.id).map(o=>({...o,turn:quoteSource(snapshot,o.quote)}))}));}
export function stats(snapshot:Snapshot,provider:string){const accepted=snapshot.session.messages.filter(m=>m.role==='user').length,cap=provider==='deepseek'?10:12;return {accepted,cap,remaining:Math.max(0,cap-accepted),attempts:snapshot.attempts,statements:snapshot.session.observations.length};}
export function stageState(current:string,stage:string):'active'|'complete'|'waiting'{const stages=['input','request','validate','commit'];if(current==='done')return 'complete';if(current===stage)return 'active';return stages.indexOf(current)>stages.indexOf(stage)?'complete':'waiting';}

export function radarData(snapshot:Snapshot){
 const groups=clueGroups(snapshot),scale=Math.max(3,Math.ceil(Math.max(0,...groups.map(g=>g.quotes.length))/3)*3);
 const axes=groups.map((g,i)=>{
  const angle=-Math.PI/2+i*Math.PI*2/5,count=g.quotes.length,ratio=count/scale;
  const at=(r:number):[number,number]=>[120+Math.cos(angle)*r,85+Math.sin(angle)*r];
  return {...g,count,ratio,point:at(58*ratio),end:at(58),label:at(76)};
 });
 const grid=[1/3,2/3,1].map(r=>axes.map((_,i)=>{const angle=-Math.PI/2+i*Math.PI*2/5;return `${120+Math.cos(angle)*58*r},${85+Math.sin(angle)*58*r}`}).join(' '));
 return {axes,scale,grid,points:axes.map(a=>a.point.join(',')).join(' ')};
}
