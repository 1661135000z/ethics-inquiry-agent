import {describe,it,expect} from 'vitest';
import {emptySnapshot,initialState,publicSnapshot,restoreState} from './state';
import {radarData} from './experience';
import {scenarioSnapshot,dimensionView,cleanAnalysis} from './analysis';
import cases from './cases.json';

describe('shared evidence state',()=>{
 it('shows curated initial relationship without a conversation or model call',()=>{
  const c=cases.find(c=>c.id==='relationships')!;
  const preview=scenarioSnapshot(c,c.text_en,false);
  expect(preview.session.messages).toHaveLength(0);
  expect(preview.session.analysis?.facts.some(f=>f.area==='interests'&&f.quote.includes('friend from university'))).toBe(true);
  expect(dimensionView(preview,'interests').status).toBe('partial');
  expect(dimensionView(preview,'review').missing.length).toBe(3);
 });
 it('does not reuse a preset seed after text is edited or invent ties for custom context',()=>{
  const c=cases.find(c=>c.id==='relationships')!;
  const preview=scenarioSnapshot(c,'I need to assess a dashboard. No relationship has been specified.',false);
  expect(preview.session.analysis?.facts).toHaveLength(0);
 });
 it('radar uses distinct facet support, not duplicate quote count',()=>{
  const c=cases.find(c=>c.id==='relationships')!,s=scenarioSnapshot(c,c.text_en,false);
  const a=s.session.analysis!;
  a.facts.push({...a.facts.find(f=>f.area==='interests')!,id:'Fduplicate'});
  const axis=radarData(s).axes.find(a=>a.id==='interests')!;
  expect(axis.coverage).toBe(1);
  expect(axis.ratio).toBe(1/3);
 });
 it('safe persistence retains validated analysis but strips arbitrary secret-shaped fields',()=>{
  const c=cases.find(c=>c.id==='relationships')!,snapshot=scenarioSnapshot(c,c.text_en,false);
  // Preview state is not persisted as accepted; provide the exact initial source.
  snapshot.session.messages=[{role:'user',content:c.text_en},{role:'assistant',content:'Who could independently check this?'}];
  const state={...initialState(),snapshot};
  const raw=JSON.parse(JSON.stringify(publicSnapshot(state)));
  raw.snapshot.session.analysis.api_key='do-not-persist';
  const restored=restoreState(JSON.stringify(raw));
  expect(restored.snapshot.session.analysis?.facts.length).toBeGreaterThan(0);
  expect(JSON.stringify(restored)).not.toContain('do-not-persist');
  const bad=cleanAnalysis({...snapshot.session.analysis,facts:[{...snapshot.session.analysis!.facts[0],quote:'unreported private relationship'}]},snapshot.session.messages);
  expect(bad?.facts).toHaveLength(0);
 });
 it('legacy quote-only snapshots do not gain invented facet completeness',()=>{
  const s=emptySnapshot();s.session.observations=[{area:'pressure',quote:'Someone said something unclear.'}];
  expect(dimensionView(s,'pressure').status).toBe('unexplored');
 });
});
it('archive export includes source-linked analysis and conditional brief',async()=>{
 const {archiveMarkdown,createArchive}=await import('./history');
 const c=cases.find(c=>c.id==='relationships')!;
 const snapshot=scenarioSnapshot(c,c.text_en,false);
 snapshot.session.messages=[{role:'user',content:c.text_en},{role:'assistant',content:'Which records could independently check this?'}];
 const a=snapshot.session.analysis!,f=a.facts[0];
 a.brief={conflict:'A reported concern.',stakeholders:'The audit team.',options:[{action:'Check records',tradeoff:'Takes time'},{action:'Seek review',tradeoff:'Needs availability'}],recommendation:'If the concern is supported, consider independent review.',uncertainties:['The records need checking.'],basis:[f.id],language:'English',stale:true,as_of_turn:1};
 const archive=createArchive({...initialState(),snapshot},'Fictional inquiry','saved-1',1);
 const text=archiveMarkdown(archive,'English');
 expect(text).toContain('Awaiting reassessment');expect(text).toContain(f.id);expect(text).toContain('If the concern is supported');
});
