import type {Snapshot} from './state';
export type Provider={id:string;models:string[];default_model?:string;configured:boolean;free_confirmed:boolean};
export type Case={id:string;en:string;zh:string;text_en:string;text_zh:string;source:string};
export type Config={providers:Provider[];cases:Case[];principle:string;test_mode?:boolean;demo_access?:boolean};
export class APIError extends Error{constructor(public code:string,message:string,public status=400){super(message)}}
export async function json<T>(path:string,body?:unknown):Promise<T>{
 let r:Response;try{r=await fetch(path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},credentials:'same-origin',body:body?JSON.stringify(body):undefined})}catch{throw new APIError('network','无法连接后端，请检查网络。')}
 const data=await r.json();if(!r.ok)throw new APIError(data.error?.code||'network',data.error?.message||'请求未完成。',r.status);return data;
}
export async function inquiry(body:unknown,signal:AbortSignal,event:(stage:string)=>void):Promise<Snapshot>{
 const response=await fetch('/api/inquiry',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify(body),signal});
 if(!response.ok){const data=await response.json();throw new APIError(data.error?.code||'request',data.error?.message||'请求未完成。',response.status)}
 if(!response.body)throw new APIError('network','响应连接不可用。');
 const reader=response.body.getReader(),decoder=new TextDecoder();let buffer='',result:Snapshot|undefined;
 while(true){const {done,value}=await reader.read();buffer+=decoder.decode(value,{stream:!done});let end;
  while((end=buffer.indexOf('\n\n'))>=0){const frame=buffer.slice(0,end);buffer=buffer.slice(end+2);const type=frame.match(/^event: (.*)$/m)?.[1];const raw=frame.match(/^data: (.*)$/m)?.[1];if(!raw)continue;const data=JSON.parse(raw);
   if(type==='stage')event(data.stage);if(type==='complete')result=data;if(type==='error')throw new APIError(data.code,data.message);
  }
  if(buffer.length>250000)throw new APIError('format','响应超过长度限制。');if(done)break;
 }
 if(!result)throw new APIError('interrupted','连接中断，输入已保留。请先恢复会话，避免重复发送。');return result;
}
