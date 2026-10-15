import {it,expect} from 'vitest';
import {quoteSource,stageState,stats,clueGroups,radarData} from './experience';
import {initialState,reducer} from './state';
it('links exact quotations only to user turns and preserves missing sources',()=>{
 const s=initialState().snapshot;s.session.messages=[{role:'user',content:'I do not know who checked the source.'},{role:'assistant',content:'Who checked the source?'}];
 expect(quoteSource(s,'do not know')).toBe(1);expect(quoteSource(s,'Who checked')).toBeNull();
});
it('counts only accepted turns and treats backup cap as total inquiry turns',()=>{
 const s=initialState().snapshot;s.session.messages=[{role:'user',content:'a'},{role:'assistant',content:'b'}];
 expect(stats(s,'deepseek').remaining).toBe(9);expect(stats(s,'zhipu').remaining).toBe(19);
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

it('derives radar axes only from recorded statement counts, leaving empty axes at zero',()=>{
 const s=initialState().snapshot;s.session.observations=[{area:'evidence',quote:'First'},{area:'evidence',quote:'Second'},{area:'review',quote:'Unknown reviewer'}];
 const radar=radarData(s);expect(radar.scale).toBe(3);expect(radar.axes.map(a=>a.count)).toEqual([0,0,0,2,1]);
 expect(radar.axes[0].point).toEqual([120,85]);expect(radar.axes[3].ratio).toBeCloseTo(2/3);expect(radar.axes[4].ratio).toBeCloseTo(1/3);
});
it('uses a labelled shared count scale without manufacturing a full empty radar',()=>{
 const s=initialState().snapshot;expect(radarData(s).axes.every(a=>a.ratio===0)).toBe(true);
 s.session.observations=Array.from({length:7},(_,i)=>({area:'role',quote:`Statement ${i}`}));
 const data=radarData(s);expect(data.scale).toBe(9);expect(data.axes[0].count).toBe(7);expect(data.axes.every(a=>a.ratio>=0&&a.ratio<=1)).toBe(true);
});
