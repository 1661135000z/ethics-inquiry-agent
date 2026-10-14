import {it,expect} from 'vitest';
import {createArchive,readHistory,saveArchive,renameArchive,archiveMarkdown} from './history';
import {initialState} from './state';
function sample(){const s=initialState();s.snapshot.session.messages=[{role:'user',content:'Fictional situation'},{role:'assistant',content:'Who could check it?'}];s.snapshot.initial_text='Fictional situation';s.snapshot.session.records=[{turn:1,provider:'gemini',model:s.model,time:'2026-10-15T00:00:00Z',focus:'review'}];return s;}
it('only saves accepted records and drops credentials, unsent drafts and backup access',()=>{
 const s={...sample(),draft:'UNSENT',api_key:'PRIVATE-KEY',access_code:'PRIVATE-CODE',verified:true};s.snapshot.backup_until=9999999999;
 const item=createArchive(s,'Saved inquiry','archive-one',123);
 const raw=JSON.stringify(item);expect(raw).not.toContain('PRIVATE');expect(raw).not.toContain('UNSENT');expect(raw).not.toContain('backup_until');
 expect(readHistory(JSON.stringify([item]))[0].snapshot.session.messages).toHaveLength(2);
});
it('rejects corrupt, oversized and odd-turn archives without breaking usable entries',()=>{
 const item=createArchive(sample(),'Okay','one',123);
 expect(readHistory('broken')).toEqual([]);expect(readHistory('x'.repeat(2000001))).toEqual([]);
 expect(readHistory(JSON.stringify([{...item,snapshot:{session:{messages:[null]}}},item]))).toHaveLength(1);
 const odd=structuredClone(item);odd.snapshot.session.messages.pop();expect(readHistory(JSON.stringify([odd]))).toEqual([]);
});
it('upserts named snapshots and caps local history at twenty without mutating input',()=>{
 const item=createArchive(sample(),'One','one',123);const original=[item];
 const saved=saveArchive(original,{...item,name:'New name'});expect(saved).toHaveLength(1);expect(original[0].name).toBe('One');
 let all=original;for(let i=0;i<25;i++)all=saveArchive(all,{...item,id:`item-${i}`});expect(all).toHaveLength(20);
 expect(renameArchive(all,all[0].id,'  Renamed  ')[0].name).toBe('Renamed');
});
it('refuses saving an empty conversation',()=>{expect(()=>createArchive(initialState(),'Empty','e',123)).toThrow()});

it('exports an archive without an invented backend failure or unsent draft',()=>{
 const item=createArchive({...sample(),draft:'DO-NOT-EXPORT'},'Named inquiry','one',123);
 const text=archiveMarkdown(item,'English');expect(text).toContain('Named inquiry');expect(text).toContain('Model provenance');expect(text).not.toContain('unavailable');expect(text).not.toContain('Unsent draft');expect(text).not.toContain('DO-NOT-EXPORT');
});
