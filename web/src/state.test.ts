import {describe,it,expect} from 'vitest';
import {initialState,reducer,publicSnapshot,restoreState} from './state';
describe('workspace transitions',()=>{
 it('starts with only model entry',()=>{expect(initialState().screen).toBe('welcome')});
 it('model selection does not erase accepted messages',()=>{
  const state={...initialState(),screen:'chat' as const,snapshot:{version:1,attempts:1,initial_text:'Original',case_id:'blank',session:{messages:[{role:'user' as const,content:'Original'}],observations:[],records:[],focus:'scope'}}};
  expect(reducer(state,{type:'MODEL',provider:'zhipu',model:'glm-4.7-flash'}).snapshot).toEqual(state.snapshot);
 });
 it('cancel restores both conversation and unsent answer',()=>{
  const state={...initialState(),screen:'chat' as const,draft:'Unsent answer'};
  const choosing=reducer(state,{type:'SELECT_AGAIN'});
  const changed=reducer(choosing,{type:'DRAFT',text:'New situation'});
  expect(reducer(changed,{type:'CANCEL_SELECT'}).draft).toBe('Unsent answer');
 });
 it('opening selection twice preserves the original unsent answer',()=>{
  const first=reducer({...initialState(),screen:'chat' as const,draft:'Original answer'},{type:'SELECT_AGAIN'});
  const changed=reducer(first,{type:'DRAFT',text:'Pending case'});
  const repeated=reducer(changed,{type:'SELECT_AGAIN'});
  expect(reducer(repeated,{type:'CANCEL_SELECT'}).draft).toBe('Original answer');
 });
 it('failed request retains case draft and previous transcript',()=>{
  const state=reducer({...initialState(),draft:'New situation'},{type:'REQUEST',id:'r1'});
  const failed=reducer(state,{type:'FAIL',id:'r1',message:'Unavailable'});
  expect(failed.draft).toBe('New situation'); expect(failed.snapshot).toEqual(state.snapshot);
 });
 it('stale response cannot replace the current workspace',()=>{
  const state=reducer(initialState(),{type:'REQUEST',id:'new'});
  expect(reducer(state,{type:'COMPLETE',id:'old',snapshot:state.snapshot})).toEqual(state);
 });
 it('restore stays onboarded and preserves unsent draft',()=>{
  const state={...initialState(),screen:'chat' as const,onboarded:true,draft:'Waiting',verified:true};
  const restored=restoreState(JSON.stringify(publicSnapshot(state)));
  expect(restored.screen).toBe('chat'); expect(restored.draft).toBe('Waiting'); expect(restored.verified).toBe(false);
 });
 it('public snapshot excludes unknown secret fields',()=>{
  expect(JSON.stringify(publicSnapshot({...initialState(),api_key:'DO-NOT-SAVE'} as never))).not.toContain('DO-NOT-SAVE');
 });
 it('recovery clears connection error without erasing the draft',()=>{
  const state={...initialState(),draft:'Still unsent',error:'Session expired'};
  const restored=reducer(state,{type:'RESTORE',snapshot:state.snapshot});
  expect(restored.error).toBe('');expect(restored.draft).toBe('Still unsent');
 });
 it('rejects corrupted cached field types instead of breaking the interface',()=>{
  const raw={...publicSnapshot(initialState()),draft:{api_key:'secret'},provider:[],snapshot:{session:{messages:[null]}}};
  expect(restoreState(JSON.stringify(raw))).toEqual(initialState());
 });
 it('regenerating a question preserves the unsent answer',()=>{
  const state=reducer({...initialState(),draft:'Unsent answer'},{type:'REQUEST',id:'regen'});
  expect(reducer(state,{type:'COMPLETE',id:'regen',snapshot:state.snapshot,preserveDraft:true}).draft).toBe('Unsent answer');
 });
 it('new session invalidates completion from an older request',()=>{
  const pending=reducer(initialState(),{type:'REQUEST',id:'old'});
  const reset=reducer(pending,{type:'NEW',snapshot:initialState().snapshot});
  const late={...pending.snapshot,version:1};
  expect(reducer(reset,{type:'COMPLETE',id:'old',snapshot:late})).toEqual(reset);
 });
 it('cannot cancel a submitted scenario switch while it is in flight',()=>{
  const selected=reducer(initialState(),{type:'SELECT_AGAIN'});
  const pending=reducer(selected,{type:'REQUEST',id:'switch'});
  expect(reducer(pending,{type:'CANCEL_SELECT'})).toEqual(pending);
 });
});
