import {RecordedExample} from './RecordedExample';
import {it,expect} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import {ReviewPreview,ClueCompass} from './ExperiencePanels';
import {initialState} from './state';
it('retains static source attribution when interactive links are hidden for printing',()=>{
 const snapshot=initialState().snapshot;snapshot.initial_text='Fictional input';snapshot.session.messages=[{role:'user',content:'I do not know whether the data are complete.'},{role:'assistant',content:'Who can verify that?'}];snapshot.session.observations=[{area:'evidence',quote:'I do not know whether the data are complete.'}];
 const html=renderToStaticMarkup(<ReviewPreview snapshot={snapshot} zh={false} onLocate={()=>{}}/>);
 expect(html).toContain('<cite>Turn 1</cite>');expect(html).toContain('I do not know whether the data are complete.');
});

it('labels the historical example as read-only and preserves the actual original question',async()=>{
 const {RecordedExample}=await import('./RecordedExample');const html=renderToStaticMarkup(<RecordedExample zh={false}/>);
 expect(html).toContain('Recorded inquiry');expect(html).toContain('read-only');expect(html).toContain('12 October 2026');expect(html).toContain('What steps can you take to verify whether the missing manual entries');expect(html).toContain('Viewing makes no model call');
});
it('translates the read-only historical example without changing original messages',()=>{
 const html=renderToStaticMarkup(<RecordedExample zh={true}/>);
 expect(html).toContain('中文译文');
 expect(html).toContain('一批手工分录');
 expect(html).toContain('查看英文原文');
});
it('keeps language switching available inside the existing modal guide',async()=>{
 const {HelpPanel}=await import('./ExperiencePanels');
 const html=renderToStaticMarkup(<HelpPanel zh={true} onLanguage={()=>{}}/>);
 expect(html).toContain('切换引导语言');
});
it('uses current language for the modal close label instead of the previous document language',async()=>{
 const {vi}=await import('vitest');const {Sheet}=await import('./ExperiencePanels');
 vi.stubGlobal('document',{documentElement:{lang:'zh-CN'}});
 try{const html=renderToStaticMarkup(<Sheet title="Inside Inquire" subtitle="Guide" closeLabel="Close" onClose={()=>{}}>Example</Sheet>);expect(html).toContain('Inside Inquire · Close');}
 finally{vi.unstubAllGlobals()}
});
it('offers source-led gaps as optional draft actions, without invented case details',async()=>{
 const {GapGuide}=await import('./InquirySupport');const {blankAnalysis}=await import('./analysis');
 const s=initialState().snapshot;s.session.analysis=blankAnalysis();s.session.focus='review';
 const html=renderToStaticMarkup(<GapGuide snapshot={s} zh={false} locked={false} draft="" onDraft={()=>{}} onArea={()=>{}}/>);
 expect(html).toContain('Who could independently review');expect(html).toContain('Start here');expect(html).toContain('optional');expect(html).not.toContain('My independent reviewer is');
});
it('renders only model-provided options with discussion actions',async()=>{
 const {OptionComparison}=await import('./InquirySupport');const b={conflict:'Concern',stakeholders:'Team',options:[{action:'Check original records',tradeoff:'Access required'},{action:'Seek independent review',tradeoff:'Reviewer availability unknown'}],recommendation:'Check first',uncertainties:['Access'],basis:['f1'],language:'English',stale:false,as_of_turn:2};
 const html=renderToStaticMarkup(<OptionComparison brief={b} zh={false} onDiscuss={()=>{}}/>);
 expect(html).toContain('Check original records');expect(html).toContain('Reviewer availability unknown');expect(html.match(/Examine this option/g)).toHaveLength(2);expect(html).not.toContain('Recommended option');
});
it('keeps all compass detail panels in a stable stack while exposing only the selected one',()=>{
 const snapshot=initialState().snapshot;
 const render=(activeArea:string)=>renderToStaticMarkup(<ClueCompass snapshot={{...snapshot,session:{...snapshot.session,analysis:{schema:1,facts:[],ready:false,brief:null,language:'English',origin:'semantic'}}}} zh={false} activeArea={activeArea} onArea={()=>{}}/>);
 for(const area of ['role','interests','pressure','evidence','review']){
  const html=render(area);
  expect(html.match(/class="compass-detail-slot/g)).toHaveLength(5);
  expect(html.match(/class="compass-detail-slot is-active"/g)).toHaveLength(1);
  expect(html.match(/aria-hidden="true" inert=""/g)).toHaveLength(4);
 }
});
