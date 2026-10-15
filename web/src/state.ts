import {cleanAnalysis,type Analysis} from './analysis';
export type Message={role:'user'|'assistant';content:string};
export type Snapshot={version:number;attempts:number;initial_text:string;case_id:string;backup_until?:number;session:{analysis?:Analysis;messages:Message[];observations:{area:string;quote:string}[];records:{turn:number;provider:string;model:string;tokens?:number;focus:string;time:string;regenerations?:number}[];focus:string}};
export type State={screen:'welcome'|'cases'|'chat';onboarded:boolean;archived:boolean;provider:string;model:string;verified:boolean;draft:string;savedDraft:string;selecting:boolean;caseId:string;initialText:string;snapshot:Snapshot;activeRequest:string|null;pendingText:string|null;pendingOperation:string|null;stage:string;error:string;view:'chat'|'notes'|'review';language:'中文'|'English';theme:'dark'|'light'};
export const emptySnapshot=():Snapshot=>({version:0,attempts:0,initial_text:'',case_id:'blank',session:{messages:[],observations:[],records:[],focus:'scope'}});
export const initialState=():State=>({screen:'welcome',onboarded:false,archived:false,provider:'gemini',model:'gemini-3.5-flash-lite',verified:false,draft:'',savedDraft:'',selecting:false,caseId:'blank',initialText:'',snapshot:emptySnapshot(),activeRequest:null,pendingText:null,pendingOperation:null,stage:'idle',error:'',view:'chat',language:'English',theme:'dark'});
export type Action= {type:'HOME'}|{type:'RESUME'}|{type:'MODEL';provider:string;model:string}|{type:'CONFIRM'}|{type:'DRAFT';text:string}|{type:'CASE';id:string;text:string}|{type:'SELECT_AGAIN'}|{type:'CANCEL_SELECT'}|{type:'REQUEST';id:string;text?:string;operation?:string}|{type:'STAGE';id:string;stage:string}|{type:'COMPLETE';id:string;snapshot:Snapshot;preserveDraft?:boolean}|{type:'FAIL';id:string;message:string}|{type:'RESTORE';snapshot:Snapshot}|{type:'VIEW';view:State['view']}|{type:'THEME';theme:State['theme']}|{type:'LANGUAGE';language:State['language']}|{type:'NEW';snapshot:Snapshot};
export function reducer(s:State,a:Action):State {
 switch(a.type){
 case 'HOME':return s.activeRequest?s:{...s,screen:'welcome'};
 case 'RESUME':return s.activeRequest?s:{...s,screen:s.selecting?'cases':s.snapshot.session.messages.length?'chat':'cases'};
 case 'MODEL':return {...s,provider:a.provider,model:a.model,verified:false,error:''};
 case 'CONFIRM':return {...s,onboarded:true,verified:true,screen:s.snapshot.session.messages.length&&!s.selecting?'chat':'cases',error:''};
 case 'DRAFT':return {...s,draft:a.text,error:''};
 case 'CASE':return {...s,caseId:a.id,draft:a.text,error:''};
 case 'SELECT_AGAIN':return s.selecting||s.activeRequest?s:{...s,screen:'cases',selecting:true,savedDraft:s.draft,draft:s.snapshot.initial_text,caseId:s.snapshot.case_id,view:'chat',error:''};
 case 'CANCEL_SELECT':return s.activeRequest?s:{...s,screen:'chat',selecting:false,draft:s.savedDraft,savedDraft:'',caseId:s.snapshot.case_id,error:''};
 case 'REQUEST':return {...s,activeRequest:a.id,pendingText:a.operation==='regenerate'?null:a.text||s.draft,pendingOperation:a.operation||'submit',stage:'input',error:''};
 case 'STAGE':return a.id===s.activeRequest?{...s,stage:a.stage}:s;
 case 'COMPLETE':return a.id===s.activeRequest?{...s,snapshot:a.snapshot,archived:false,screen:'chat',selecting:false,savedDraft:'',draft:a.preserveDraft?s.draft:'',initialText:a.snapshot.initial_text,caseId:a.snapshot.case_id,activeRequest:null,pendingText:null,pendingOperation:null,stage:'done',error:'',view:'chat'}:s;
 case 'FAIL':return a.id===s.activeRequest?{...s,activeRequest:null,pendingText:null,pendingOperation:null,stage:'error',error:a.message}:s;
 case 'RESTORE':
  if(!a.snapshot.session.messages.length&&s.snapshot.session.messages.length)return {...s,archived:true,activeRequest:null,pendingText:null,pendingOperation:null,screen:s.screen==='welcome'?'welcome':'chat',selecting:false,error:'后台会话已过期或不可用，旧记录已保留为只读。请先导出，再开始新对话。'};
  return {...s,snapshot:a.snapshot,archived:false,error:'',screen:s.screen==='welcome'?'welcome':a.snapshot.session.messages.length&&!s.selecting?'chat':s.screen==='chat'?'cases':s.screen};
 case 'VIEW':return {...s,view:a.view};
 case 'THEME':return {...s,theme:a.theme};
 case 'LANGUAGE':return {...s,language:a.language};
 case 'NEW':return {...s,snapshot:a.snapshot,archived:false,activeRequest:null,pendingText:null,pendingOperation:null,screen:'cases',draft:s.snapshot.initial_text,caseId:s.snapshot.case_id,selecting:false,savedDraft:'',stage:'idle',error:'',view:'chat'};
 }
}
export function publicSnapshot(s:State){
 return {screen:s.screen,onboarded:s.onboarded,archived:s.archived,provider:s.provider,model:s.model,draft:s.draft,savedDraft:s.savedDraft,selecting:s.selecting,caseId:s.caseId,initialText:s.initialText,snapshot:s.snapshot,view:s.view,language:s.language,theme:s.theme};
}
export function restoreState(raw:string|null):State{
 const fallback=initialState();
 try{
  if(!raw||raw.length>200000)return fallback;
  const v=JSON.parse(raw); if(!v||!['welcome','cases','chat'].includes(v.screen)||!Array.isArray(v.snapshot?.session?.messages))return fallback;
  const text=(x:unknown,max=24000)=>typeof x==='string'&&x.length<=max;
  const n=(x:unknown)=>typeof x==='number'&&Number.isSafeInteger(x)&&x>=0;
  if(!['gemini','zhipu','openrouter','deepseek'].includes(v.provider)||!text(v.model,120)||
    !['draft','savedDraft','initialText','caseId'].every(k=>text(v[k]))||
    typeof v.onboarded!=='boolean'||typeof v.selecting!=='boolean'||
    !['chat','notes','review'].includes(v.view)||!['中文','English'].includes(v.language)||!['dark','light'].includes(v.theme))return fallback;
  const s=v.snapshot,session=s.session;
  if(!n(s.version)||!n(s.attempts)||!text(s.initial_text)||!text(s.case_id,120)||!text(session.focus,40)||
    session.messages.length>30||!session.messages.every((m:Message)=>m&&['user','assistant'].includes(m.role)&&text(m.content))||
    !Array.isArray(session.observations)||session.observations.length>30||!session.observations.every((o:{area:string;quote:string})=>o&&text(o.area,80)&&text(o.quote))||
    !Array.isArray(session.records)||session.records.length>15||!session.records.every((r:Snapshot['session']['records'][number])=>r&&n(r.turn)&&text(r.provider,40)&&text(r.model,120)&&text(r.focus,40)&&text(r.time,80)))return fallback;
  if(v.archived!==undefined&&typeof v.archived!=='boolean')return fallback;
  v.snapshot={version:s.version,attempts:s.attempts,initial_text:s.initial_text,case_id:s.case_id,session:{
   ...(cleanAnalysis(session.analysis,session.messages)?{analysis:cleanAnalysis(session.analysis,session.messages)}:{}),
   focus:session.focus,messages:session.messages.map((m:Message)=>({role:m.role,content:m.content})),
   observations:session.observations.map((o:{area:string;quote:string})=>({area:o.area,quote:o.quote})),
   records:session.records.map((r:Snapshot['session']['records'][number])=>({turn:r.turn,provider:r.provider,model:r.model,focus:r.focus,time:r.time,...(n(r.tokens)?{tokens:r.tokens}:{}),...(n(r.regenerations)?{regenerations:r.regenerations}:{})}))}};
  // Copy only the declared non-secret fields, never arbitrary persisted properties.
  const base=publicSnapshot(fallback);
  for(const k of Object.keys(base) as (keyof typeof base)[]) if(k in v)(base as Record<string,unknown>)[k]=v[k];
  return {...fallback,...base,verified:false,activeRequest:null,pendingText:null,pendingOperation:null,stage:'idle',error:''};
 }catch{return fallback}
}
