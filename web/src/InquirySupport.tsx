import {useEffect,useState} from 'react';
import {dimensionDefinitions,type DecisionBrief} from './analysis';
import {briefChange,gapSuggestions,turnChanges} from './inquiryUX';
import {Icon} from './Icon';
import type {Snapshot} from './state';
export function GapGuide({snapshot,zh,locked,draft,onDraft,onArea}:{snapshot:Snapshot;zh:boolean;locked:boolean;draft:string;onDraft:(text:string)=>void;onArea:(id:string)=>void}){
 const gaps=gapSuggestions(snapshot,zh),[chosen,setChosen]=useState('');
 const signature=gaps.map(g=>g.area+':'+g.facet).join('|');
 useEffect(()=>setChosen(''),[snapshot.version]);
 const selected=gaps.find(g=>g.area===chosen)||gaps[0],t=(cn:string,en:string)=>zh?cn:en;
 if(!snapshot.session.analysis)return null;
 if(!selected)return <div className="gap-guide gap-ready"><Icon name="check" size={16}/><div><strong>{t('已有初步分析基础','A preliminary basis is available')}</strong><p>{t('可以继续比较方案、质疑建议，或补充会改变判断的新信息。','Compare options, challenge the guidance, or add facts that could change it.')}</p><button className="text-button" disabled={locked} onClick={()=>onDraft(t('根据目前的信息，你建议如何行动？还有哪些前提需要核实？','Based on the current information, what action would you suggest, and what assumptions need checking?'))}>{t(draft?'将讨论问题补充到草稿':'讨论初步建议',draft?'Add discussion prompt to draft':'Discuss preliminary guidance')}<Icon name="arrow" size={14}/></button></div></div>;
 return <section className="gap-guide" aria-label={t('接下来可以补充','Context you can add next')}>
  <header><span className="micro">{t('接下来可以补充','Context you can add next')}</span><span>{t('按实际信息缺口生成 · 可自由跳过','Based on recorded gaps · optional')}</span></header>
  <div className="gap-tabs" role="group" aria-label={t('尚待探索的维度','Areas with open context needs')}>{gaps.map(g=><button key={g.area} type="button" aria-pressed={selected.area===g.area} onClick={()=>{setChosen(g.area);onArea(g.area)}} disabled={locked}><span className={`gap-dot ${g.uncertain?'uncertain':''}`}/>{g.label}<small title={t('尚缺的信息类别','Open information needs')}>{g.remaining}{zh?'项':' open'}</small></button>)}</div>
  <div className="gap-question" key={selected.area+selected.facet}><div>{selected.source&&<blockquote className="gap-source"><span>{t('你已提到','Already reported')}</span><q title={selected.source.quote}>{selected.source.quote}</q></blockquote>}<strong>{selected.question}</strong><p>{selected.hint}</p></div><button className="secondary" type="button" disabled={locked||draft.length+selected.starter.length+2>4000} onClick={()=>{onArea(selected.area);onDraft(selected.starter)}}>{t(draft?'补充到草稿':'从这里回答',draft?'Add to draft':'Start here')}<Icon name="arrow" size={14}/></button></div>
  <details className="gap-explanation" key={signature}><summary>{t('为什么提示这个？','Why this prompt?')}</summary><p>{t(`“${selected.label}”目前有 ${selected.coverage}/3 类信息获得陈述支持。这是尚缺的一类，不代表已存在相关风险；回答后仍由模型结合上下文评估。`,`Reported context supports ${selected.coverage}/3 needs in ${selected.label.toLowerCase()}. This is an open need, not evidence of risk; the model reassesses your answer in context.`)}</p></details>
 </section>;
}
export function TurnUpdate({snapshot,turn,zh,onLocate}:{snapshot:Snapshot;turn:number;zh:boolean;onLocate:(turn:number,area?:string)=>void}){
 const engagements=(snapshot.session.analysis?.engagements||[]).filter(e=>e.turn===turn);const change=turnChanges(snapshot,turn),t=(a:string,b:string)=>zh?a:b;
 if(!snapshot.session.analysis)return null;
 const labels=(ids:string[])=>[...new Set(ids)].map(id=>dimensionDefinitions[id as keyof typeof dimensionDefinitions]?.[zh?'zh':'en']).filter(Boolean).join(zh?'、':', ');
 return <details className={`turn-update ${change.corrected.length?'has-correction':''}`} open={change.corrected.length>0}>
  <summary><Icon name={change.corrected.length?'refresh':'note'} size={13}/><span>{change.corrected.length?t('本轮修正了先前信息','Earlier information revised'):change.added.length?t(`本轮补充：${labels(change.added.map(f=>f.area))}`,`Context added: ${labels(change.added.map(f=>f.area))}`):engagements.length?t(`本轮探索：${labels(engagements.map(e=>e.area))}`,`Explored: ${labels(engagements.map(e=>e.area))}`):t('本轮未记录新的维度信息','No new dimensional context recorded this turn')}</span><Icon name="plus" size={12}/></summary>
  <p>{t('以下来自已接受记录；是用户陈述，不是独立核实的事实。','From accepted records: reported statements, not independently verified facts.')}</p>
  {change.corrected.map(c=><div className="correction-pair" key={c.after.id}><span>{t('先前陈述','Earlier statement')}</span>{c.before.map(f=><blockquote key={f.id}>{f.quote}<button className="text-button" onClick={()=>onLocate(f.turn,f.area)}>{t(`第${f.turn}轮`,`Turn ${f.turn}`)}<Icon name="arrow" size={12}/></button></blockquote>)}<span>{t('本轮修正为','Revised this turn')}</span><blockquote>{c.after.quote}</blockquote></div>)}
  {change.added.length>0&&<ul>{change.added.map(f=><li key={f.id}><span>{labels([f.area])}{f.kind==='uncertain'?t(' · 尚不确定',' · uncertain'):''}{f.status==='superseded'?t(' · 后续已修正',' · revised later'):''}</span><q>{f.quote}</q></li>)}</ul>}
  {engagements.map(e=><blockquote key={e.id}>{e.quote}<small>{e.state==='unknown'?t('已探索 · 仍不确定','Explored · still uncertain'):e.state==='declined'?t('已探索 · 暂不继续追问','Explored · not pursued further'):t('已记录讨论或立场','Discussion or position recorded')}</small></blockquote>)}
  {!engagements.length&&!change.added.length&&!change.corrected.length&&<p>{t('重复、模糊或暂时无法分类的回答不会被强行算作进展；仍可以继续讨论。','Repeated, ambiguous or unclassified answers are not forced into progress. The inquiry can still continue.')}</p>}
 </details>;
}
export function BriefRevision({brief,previous,zh}:{brief:DecisionBrief;previous?:DecisionBrief|null;zh:boolean}){
 const kind=briefChange(previous,brief),t=(a:string,b:string)=>zh?a:b;
 const before=kind==='revised'?previous?.recommendation:undefined;
 return <div className={`brief-revision ${brief.stale?'is-stale':''}`}><span className="status-dot"/><div><strong>{brief.stale?t('已有新信息，建议尚待重新评估','New context: guidance awaits reassessment'):kind==='revised'?t('本轮已更新分析与建议','Analysis and guidance updated'):kind==='reassessed'?t('本轮已重新评估建议','Guidance reassessed this turn'):t('已形成有条件的初步建议','Conditional preliminary guidance available')}</strong><p>{t(`依据截至第 ${brief.as_of_turn} 轮的陈述；新增信息可能改变建议。`,`Based on reported context through turn ${brief.as_of_turn}; new information may change it.`)}</p>{before&&before!==brief.recommendation&&<details><summary>{t('对比先前建议','Compare the previous suggestion')}</summary><p>{before}</p><strong>{t('当前建议','Current suggestion')}</strong><p>{brief.recommendation}</p><small>{t('具体信息修正见相应轮次的记录；这不表示新陈述已被核实。','See the corresponding turn for recorded revisions; new statements remain unverified.')}</small></details>}</div></div>;
}
export function OptionComparison({brief,zh,onDiscuss,locked=false}:{brief:DecisionBrief;zh:boolean;onDiscuss?:(text:string)=>void;locked?:boolean}){
 const t=(a:string,b:string)=>zh?a:b;
 return <section className="option-comparison" aria-label={t('行动方案比较','Compare possible actions')}><header><h4>{t('把可选方案放在一起看','Compare the possible actions')}</h4><span>{t('模型提出的备选 · 可继续质疑','Model-proposed options · open to challenge')}</span></header><div className="option-grid" style={{'--option-count':brief.options.length} as React.CSSProperties}>{brief.options.map((o,i)=><article key={i}><span className="option-number">{t('方案','OPTION')} {String(i+1).padStart(2,'0')}</span><strong>{o.action}</strong><div><span className="micro">{t('前提、后果与权衡','Conditions, consequences & trade-offs')}</span><p>{o.tradeoff}</p></div>{onDiscuss&&<button className="text-button" disabled={locked} onClick={()=>onDiscuss(t(`我想进一步讨论这个方案：“${o.action}”。它在当前情境下需要哪些前提，有什么风险？`,`I would like to examine this option: “${o.action}”. What conditions and risks matter in this situation?`))}>{t('深入讨论此方案','Examine this option')}<Icon name="arrow" size={14}/></button>}</article>)}</div></section>;
}
