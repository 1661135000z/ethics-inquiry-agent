import {useLayoutEffect,useRef,useState} from 'react';
import gsap from 'gsap';
import {readinessForAnalysis} from './progress';
import type {Snapshot} from './state';
export function AdviceReadiness({snapshot,zh,processing=false,onAdvice}:{snapshot:Snapshot;zh:boolean;processing?:boolean;onAdvice?:()=>void}){
 const a=snapshot.session.analysis;if(!a)return null;
 return <Readiness snapshot={snapshot} zh={zh} processing={processing} onAdvice={onAdvice}/>;
}
function Readiness({snapshot,zh,processing,onAdvice}:{snapshot:Snapshot;zh:boolean;processing:boolean;onAdvice?:()=>void}){
 const a=snapshot.session.analysis!,r=readinessForAnalysis(a),bar=useRef<HTMLSpanElement>(null),previous=useRef(r.score),wasEligible=useRef(r.eligible),[pulse,setPulse]=useState(false),t=(cn:string,en:string)=>zh?cn:en;
 useLayoutEffect(()=>{const before=previous.current;previous.current=r.score;if(!bar.current||before===r.score||matchMedia('(prefers-reduced-motion: reduce)').matches)return;const tween=gsap.fromTo(bar.current,{width:`${before}%`},{width:`${r.score}%`,duration:.65,ease:'power3.out'});return()=>{tween.kill()}},[r.score]);
 useLayoutEffect(()=>{const changed=r.eligible&&!wasEligible.current;wasEligible.current=r.eligible;if(!changed)return;setPulse(true);const timer=setTimeout(()=>setPulse(false),1100);return()=>clearTimeout(timer)},[r.eligible]);
 const hasBrief=!!a.brief&&!a.brief.stale,updating=processing&&!!a.brief;
 return <section className={`advice-readiness ${r.eligible?'is-ready':''} ${pulse?'just-ready':''}`} aria-label={t('建议准备度','Advice readiness')}>
  <header><strong>{t('建议准备度','Advice readiness')}</strong><b>{r.score}%</b></header>
  <div className="readiness-track" role="progressbar" aria-label={t('形成初步建议的依据','Basis for preliminary guidance')} aria-valuenow={r.score} aria-valuemin={0} aria-valuemax={100}><span ref={bar} style={{width:`${r.score}%`}}/></div>
  <p role="status">{updating?t('正在根据新信息更新','Updating with new information'):hasBrief?t('初步建议已形成 · 持续完善','Preliminary guidance · still evolving'):r.eligible?t('可提供有条件的初步建议','Initial guidance is available'):r.score>=40?t('已具备部分判断依据','A partial basis is available'):t('仍在了解情境','Exploring the situation')}</p>
  <details><summary>{t('依据与关键未知','Basis & open questions')}</summary><p>{t('综合事实充分度、探索范围、核心冲突、立场、相关者和后果；关键未知会降低准备度。不是正确率或伦理评分。','Combines information, exploration, conflict, position, stakeholders and consequences. Important unknowns reduce readiness. This is not confidence or a moral score.')}</p><ul>{Object.entries(r.criteria).map(([key,yes])=><li key={key}>{yes?'✓':'—'} {({conflict:t('核心冲突','Core conflict'),stance:t('基本立场','Basic position'),stakeholders:t('主要相关者','Stakeholders'),consequences:t('可能后果','Consequences'),action_basis:t('可行行动依据','Action basis')} as Record<string,string>)[key]}</li>)}</ul>{r.unknown_count>0&&<p>{t(`仍有 ${r.unknown_count} 类关键未知；建议会保留条件。`,`${r.unknown_count} important open needs remain; guidance stays conditional.`)}</p>}</details>
  {onAdvice&&snapshot.session.messages.length>0&&<button className="text-button" disabled={processing} onClick={onAdvice}>{hasBrief?t('查看初步建议','View preliminary guidance'):t('请求初步建议','Ask for preliminary guidance')}<span aria-hidden="true">↗</span></button>}
 </section>;
}
