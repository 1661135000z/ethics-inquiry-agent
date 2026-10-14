import {it,expect} from 'vitest';
import {quoteSource,stageState,stats,clueGroups} from './experience';
import {initialState,reducer} from './state';
it('links exact quotations only to user turns and preserves missing sources',()=>{
 const s=initialState().snapshot;s.session.messages=[{role:'user',content:'I do not know who checked the source.'},{role:'assistant',content:'Who checked the source?'}];
 expect(quoteSource(s,'do not know')).toBe(1);expect(quoteSource(s,'Who checked')).toBeNull();
});
it('counts only accepted turns and treats backup cap as total inquiry turns',()=>{
 const s=initialState().snapshot;s.session.messages=[{role:'user',content:'a'},{role:'assistant',content:'b'}];
 expect(stats(s,'deepseek').remaining).toBe(9);expect(stats(s,'zhipu').remaining).toBe(11);
});
it('stages never invent completed checks before server progress',()=>{
 expect(stageState('request','input')).toBe('complete');expect(stageState('request','commit')).toBe('waiting');expect(stageState('error','commit')).toBe('waiting');
});
it('missing clue categories remain empty, not verified or cleared',()=>{
 const s=initialState().snapshot;s.session.observations=[{area:'evidence',quote:'I do not know whether the data are complete.'}];
 expect(clueGroups(s).find(g=>g.id==='review')?.quotes).toEqual([]);
 expect(clueGroups(s).find(g=>g.id==='evidence')?.quotes[0].quote).toContain('do not know');
});
it('pending messages are cleared on failure without altering the draft or accepted record',()=>{
 const original={...initialState(),draft:'Unsent fictional reply'};
 const pending=reducer(original,{type:'REQUEST',id:'r',text:original.draft,operation:'submit'});
 expect(pending.pendingText).toBe(original.draft);
 const failed=reducer(pending,{type:'FAIL',id:'r',message:'busy'});
 expect(failed.pendingText).toBeNull();expect(failed.draft).toBe(original.draft);expect(failed.snapshot).toEqual(original.snapshot);
});
