import {initialState,publicSnapshot,restoreState,type State,type Snapshot} from './state';
export const HISTORY_KEY='inquire.history.v1';
export type Archive={id:string;name:string;savedAt:number;provider:string;model:string;language:State['language'];snapshot:Snapshot};
export function createArchive(state:State,name:string,id:string,savedAt:number):Archive{
 const clean=restoreState(JSON.stringify(publicSnapshot({...state,draft:'',savedDraft:'',selecting:false})));
 const messages=clean.snapshot.session.messages;
 if(!messages.length||messages.length%2||!messages.every((m,i)=>m.role===(i%2?'assistant':'user')))throw new Error('No complete accepted inquiry to save.');
 if(!/^[a-zA-Z0-9-]{1,100}$/.test(id)||!Number.isFinite(savedAt)||savedAt<0)throw new Error('Invalid archive identity.');
 return {id,name:name.trim().slice(0,80)||'Inquire',savedAt,provider:clean.provider,model:clean.model,language:clean.language,snapshot:clean.snapshot};
}
export function readHistory(raw:string|null):Archive[]{
 if(!raw||raw.length>2000000)return [];
 try{const value=JSON.parse(raw);if(!Array.isArray(value))return [];const result:Archive[]=[];
 for(const item of value.slice(0,20)){try{
  if(!item||typeof item.name!=='string'||typeof item.id!=='string'||typeof item.savedAt!=='number')continue;
  const base=initialState();const state=restoreState(JSON.stringify({...publicSnapshot(base),screen:'chat',onboarded:true,provider:item.provider,model:item.model,language:item.language,snapshot:item.snapshot}));
  const archive=createArchive(state,item.name,item.id,item.savedAt);
  if(!result.some(r=>r.id===archive.id))result.push(archive);
 }catch{/* Skip one malformed entry without losing the rest. */}}
 return result;
 }catch{return []}
}
export function saveArchive(items:Archive[],archive:Archive){return [archive,...items.filter(i=>i.id!==archive.id)].slice(0,20);}
export function renameArchive(items:Archive[],id:string,name:string){return items.map(i=>i.id===id?{...i,name:name.trim().slice(0,80)||i.name}:i);}

export function archiveMarkdown(item:Archive,language:State['language']):string{
 const zh=language==='中文';
 const heading=zh?'本机探究档案':'Saved inquiry';
 const note=zh?'已接受对话的只读存档。用户陈述仍需核对，本记录不构成伦理结论。':'Read-only archive of accepted dialogue. User statements require verification; this record is not an ethical conclusion.';
 const turns=item.snapshot.session.messages.map(m=>`## ${m.role==='user'?(zh?'用户陈述':'User statement'):'Inquire'}\n\n${m.content}`).join('\n\n');
 return `# Inquire — ${heading}\n\n${item.name}\n\n${note}\n\n${turns}\n\n## ${zh?'模型来源':'Model provenance'}\n\n${JSON.stringify(item.snapshot.session.records,null,2)}`;
}
