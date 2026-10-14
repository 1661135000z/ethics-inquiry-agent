import type {ReactNode} from 'react';
import type {Case} from './api';
import {Icon} from './Icon';

export function ContextGlyph({kind}:{kind:string}){
 return <svg viewBox="0 0 100 100" fill="none" aria-hidden="true" className="context-glyph">
  <circle cx="50" cy="50" r="43" className="glyph-orbit"/>
  {kind==='relationships'?<><circle cx="34" cy="41" r="10"/><circle cx="66" cy="41" r="10"/><path d="M19 68c0-18 30-18 30 0m2 0c0-18 30-18 30 0M44 41h12"/></>:
   kind==='controls'?<><rect x="29" y="27" width="42" height="34" rx="5"/><path d="m24 43-7 9 33 25 33-25-7-9M36 40h28m-28 9h19"/></>:
   kind==='dashboard'?<><path d="M24 72V28h52M33 61l13-15 12 7 14-21"/><circle cx="46" cy="46" r="4"/><path d="M55 71h21" strokeDasharray="2 5"/></>:
   <><rect x="24" y="29" width="52" height="42" rx="8"/><path d="m35 44 7 7-7 7m15 0h14M62 20v9"/><circle cx="62" cy="17" r="3"/></>}
 </svg>
}

type Props={cases:Case[];zh:boolean;selected:string;preview:string|null;locked:boolean;onSelect:(c:Case)=>void;onCustom:()=>void;reveal:(id:string)=>void;hide:()=>void;toggle:(id:string)=>void;children:ReactNode};
export function SituationStudio({cases,zh,selected,preview,locked,onSelect,onCustom,reveal,hide,toggle,children}:Props){
 const t=(cn:string,en:string)=>zh?cn:en;
 const current=cases.find(c=>c.id===selected);
 return <div className="studio-grid">
  <div className="entry-bezel" data-enter><div className="entry-core">
   <div className="entry-intro"><div className="entry-caption"><span className="status-dot"/>{t('由你提供情境','The context is yours')}</div>
    <h3>{t('写下你正在思考的事。','What is on your mind?')}</h3>
    <p>{t('一个决定，一些线索，或还说不清的疑虑。','A decision, a few clues, or an unresolved concern.')}</p>
    <svg viewBox="0 0 420 110" fill="none" className="entry-contours" aria-hidden="true"><path d="M-30 140C90 140 70 18 230 18s140 120 240 120M-30 155C100 155 80 37 230 37s140 120 240 120M-30 170C110 170 90 56 230 56s140 120 240 120"/></svg>
   </div>
   {children}
   <div className="entry-source"><span>{current&&selected!=='blank'?t('已选示例，可自由修改','Selected example · freely editable'):t('自定义情境 · 不预设任何事实','Your own situation · no facts assumed')}</span>
    {selected!=='blank'&&<button className="text-button" disabled={locked} onClick={onCustom}>{t('改写自己的情境','Write my own')}<Icon name="arrow" size={13}/></button>}
   </div>
  </div></div>
  <section className="inspiration-bezel" aria-label={t('情境灵感','Situation inspiration')} data-enter><div className="inspiration-core">
   <header className="inspiration-heading"><div><span className="subtle-line"/><h3>{t('也可以，从这里开始。','Or start with a situation.')}</h3></div><span className="inspiration-count">{String(cases.length).padStart(2,'0')}</span></header>
   <div className="situation-options" onMouseLeave={hide} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget))hide()}}>
    {cases.map(c=>{const expanded=preview===c.id, chosen=selected===c.id;return <article key={c.id} data-case={c.id} className={`situation-option ${chosen?'selected':''} ${expanded?'expanded':''}`} onMouseEnter={()=>{if(matchMedia('(hover:hover) and (min-width:761px)').matches)reveal(c.id)}} onFocus={e=>{if(!(e.target as HTMLElement).closest('.situation-peek'))reveal(c.id)}}>
     <div className="situation-row"><button className="situation-select" onClick={()=>onSelect(c)} disabled={locked} aria-pressed={chosen}>
      <div className="glyph-bezel"><ContextGlyph kind={c.id}/></div><div className="situation-label"><strong>{(zh?c.zh:c.en).replace(/^(Example · |Fictional · |示例 · |新编虚构 · )/,'')}</strong><small>{['dashboard','vendor'].includes(c.id)?t('AI 与专业判断','AI and professional judgment'):t('关系与独立判断','Relationships and independent judgment')}</small></div><span className="situation-arrow">{chosen?<Icon name="check" size={16}/>:<Icon name="arrow" size={16}/>}</span>
     </button><button className="situation-peek" aria-expanded={expanded} disabled={locked} onClick={()=>toggle(c.id)}>{t('预览','Preview')}</button></div>
     <div className="situation-reveal" aria-hidden={!expanded} inert={!expanded}><div><p>{zh?c.text_zh:c.text_en}</p><button className="text-button" disabled={locked} onClick={()=>onSelect(c)}>{t('以此为起点','Use this as a starting point')}<span className="arrow-island"><Icon name="arrow" size={14}/></span></button></div></div>
    </article>})}
   </div>
   <footer className="inspiration-footer"><span className="status-dot"/>{t('所有示例均为假设或虚构，可编辑。','Hypothetical or fictional examples. Always editable.')}</footer>
  </div></section>
 </div>
}
