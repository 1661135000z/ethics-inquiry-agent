/** Fixed same-origin API relay. No keys, private access code, arbitrary target or logs. */
const UPSTREAM='https://inquire-experience.inquire-ethics-lab.workers.dev';
const routes={health:'GET',config:'GET',session:'POST',connect:'POST',inquiry:'POST',export:'GET',review:'GET'};
function error(status,message){return Response.json({error:{code:'mirror',message}},{status,headers:{'Cache-Control':'no-store'}})}
export default async function onRequest({request}){
 const url=new URL(request.url),name=url.pathname.slice('/api/'.length);
 if(!(name in routes))return error(404,'接口不存在。');
 if(request.method!==routes[name])return error(405,'请求方法不支持。');
 let body;
 if(request.method==='POST'){
  let sameOrigin=false;try{sameOrigin=new URL(request.headers.get('origin')).origin===url.origin}catch{}
  if(!sameOrigin)return error(403,'请求来源不允许。');
  const reader=request.body?.getReader(),chunks=[];let size=0;
  try{if(reader)while(true){const part=await reader.read();if(part.done)break;const chunk=part.value instanceof ArrayBuffer?new Uint8Array(part.value):new Uint8Array(part.value.buffer,part.value.byteOffset,part.value.byteLength);size+=chunk.byteLength;if(size>20000){await reader.cancel();return error(413,'请求过长。')}chunks.push(chunk)}}finally{reader?.releaseLock()}
  body=new Uint8Array(size);let offset=0;for(const chunk of chunks){body.set(chunk,offset);offset+=chunk.length}
 }
 const headers=new Headers({'Accept':request.headers.get('accept')||'application/json'});
 if(request.method==='POST'){headers.set('Origin',UPSTREAM);headers.set('Content-Type','application/json')}
 const cookie=request.headers.get('cookie')?.match(/(?:^|;\s*)inquire_session=([A-Za-z0-9_-]{1,128})(?:;|$)/)?.[1];
 if(cookie)headers.set('Cookie','inquire_session='+cookie);
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),90000);
 try{
  const upstream=await fetch(new Request(UPSTREAM+url.pathname+url.search,{method:request.method,headers,body:body?.buffer,signal:controller.signal,redirect:'manual'}));
  if(upstream.status>=300&&upstream.status<400)return error(502,'后端返回了意外跳转。');
  const outgoing=new Headers({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'});
  for(const name of ['Content-Type','Content-Disposition']){const value=upstream.headers.get(name);if(value)outgoing.set(name,value)}
  const session=upstream.headers.get('set-cookie');
  if(session?.startsWith('inquire_session='))outgoing.set('Set-Cookie',session.replace(/;\s*Domain=[^;]+/ig,''));
  // Preserve SSE as a stream; never buffer/parse/log conversations or credentials.
  return new Response(upstream.body,{status:upstream.status,headers:outgoing});
 }catch{return error(502,'镜像暂时无法连接后端，请稍后重试。')}finally{clearTimeout(timeout)}
}
