import {dimensionDefinitions,dimensionView,type Fact,type DecisionBrief} from './analysis';
import type {Snapshot} from './state';
// Editorial prompts describe a missing information need, never an assumed case fact.
const prompts:Record<string,Record<string,[string,string,string,string]>>={
 role:{position:['What decision can you actually make in your role?','你的职责范围内，哪些决定可以由你作出？','My decision authority is…','我的决策权限是……'],decision:['Who could be affected by the decision you need to make?','你要作出的判断会影响哪些人？','The decision and people affected are…','待作判断及受影响的人是……'],responsibility:['What professional responsibility would be at stake if this judgment were wrong?','如果判断有误，会涉及你的哪项职业责任？','The responsibility and possible consequences are…','相关职业责任及可能后果是……']},
 interests:{relationship:['What personal or business ties are relevant, if any?','是否存在与判断相关的私人或业务关系？','The relevant ties, or their absence, are…','相关关系，或明确不存在的关系是……'],stake:['Who might gain or lose from this decision?','谁可能因这个决定得益或受损？','What I know about who gains or loses is…','关于谁会得益或受损，我知道的是……'],influence:['How could the relationship or interest change your judgment?','这段关系或相关利益可能怎样影响你的判断？','The possible influence on my judgment is…','它可能对判断产生的影响是……']},
 pressure:{request:['Has anyone made a specific request or set a deadline?','有没有人提出具体要求或设定期限？','The request or deadline, if any, is…','具体要求或期限（如有）是……'],incentive:['Is any reward or adverse consequence explicitly tied to the decision?','是否有明确与决定挂钩的奖励或不利后果？','What is actually tied to the decision is…','明确与决定挂钩的后果是……'],response:['What room do you have to respond to the pressure, if there is any?','如果确有压力，你有什么应对空间？','My room to respond, and its limits, is…','我可以采取的应对及局限是……']},
 evidence:{basis:['Which original records could support or challenge your understanding?','哪些原始资料可以支持或反驳你的理解？','The records I can check, and their limits, are…','我可以核对的原始资料及其局限是……'],uncertainty:['What remains uncertain, and how could you check it?','目前哪些内容还不确定，可以怎样核实？','What remains uncertain and how I could check it is…','尚不确定的内容及可核实的途径是……'],alternatives:['What other action could you take, and what might follow?','除了目前的做法，还有什么可选行动及可能后果？','Another possible action and its consequences are…','另一种可选行动及可能后果是……']},
 review:{reviewer:['Who could independently review this issue, and with what authority?','谁可以独立复核此事，拥有什么权限？','What I know about an independent reviewer is…','关于独立复核人员，我知道的是……'],route:['What reporting route could you actually use?','你实际可以使用什么报告或升级渠道？','An available reporting route, or how I could find one, is…','可用的报告渠道，或寻找渠道的方法是……'],safeguard:['Which safeguard is feasible here, and what would it fail to address?','什么应对措施在这里可行，它有什么局限？','A feasible safeguard and its limits would be…','可行的应对措施及其局限是……']}
};
export function gapSuggestions(snapshot:Snapshot,zh:boolean){
 if(!snapshot.session.analysis||snapshot.session.analysis.origin==='pending')return [];
 return Object.entries(dimensionDefinitions).flatMap(([area,d],order)=>{
  const v=dimensionView(snapshot,area),available=v.missing.filter(f=>!v.declined.includes(f));if(!available.length)return [];
  // An explicit uncertainty deserves a checking path before unrelated missing details.
  const facet=available.find(f=>v.uncertain.some(u=>u.facet===f)&&!v.engagements.some(e=>e.facet===f&&e.state==='unknown'))||available.find(f=>v.unexplored.includes(f))||available[0];
  const uncertain=v.uncertain.some(f=>f.facet===facet),p=prompts[area][facet];
  return [{area,facet,label:zh?d.zh:d.en,question:uncertain?(zh?'可以通过哪些资料或人员核实这部分不确定的信息？':'Which available records or people could help check this uncertainty?'):p[zh?1:0],starter:uncertain?(zh?'关于这部分不确定的信息，我可以尝试核实的途径是……':'A way I could try to check this uncertainty is…'):p[zh?3:2],uncertain,source:v.uncertain.filter(f=>f.facet===facet).at(-1)||v.facts.at(-1),
   hint:uncertain?(zh?'这部分尚不能确认；可以补充核实途径，也可以说明暂时无法核实。':'This is uncertain. Describe a checking route, or say that none is currently known.'):(zh?'只填写你知道的；不知道、暂不适用也可以说明。':'Share only what you know; unknown or not applicable is a useful answer.'),
   coverage:v.information,remaining:available.length,priority:area===snapshot.session.focus?0:uncertain?1:2,order}];
 }).sort((a,b)=>a.priority-b.priority||a.coverage-b.coverage||a.order-b.order);
}
export function turnChanges(snapshot:Snapshot,turn:number){
 const facts=snapshot.session.analysis?.facts||[],current=facts.filter(f=>f.turn===turn);
 const corrected=current.flatMap(after=>{const before=after.replaces.map(id=>facts.find(f=>f.id===id)).filter((f):f is Fact=>!!f&&f.status==='superseded'&&f.replaced_by===after.id);return before.length?[{after,before}]:[]});
 return {added:current.filter(f=>!corrected.some(c=>c.after.id===f.id)),corrected};
}
export function briefChange(previous:DecisionBrief|null|undefined,next:DecisionBrief|null|undefined){
 if(!next)return 'none';if(next.stale)return 'stale';if(!previous)return 'created';
 const content=(b:DecisionBrief)=>JSON.stringify([b.conflict,b.stakeholders,b.options,b.recommendation,b.uncertainties]);
 return content(previous)!==content(next)?'revised':previous.as_of_turn!==next.as_of_turn||previous.stale?'reassessed':'unchanged';
}
export function nearLatest(scrollTop:number,scrollHeight:number,clientHeight:number){return scrollHeight-scrollTop-clientHeight<100}
