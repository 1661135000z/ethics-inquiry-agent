import {describe,it,expect,vi,afterEach} from 'vitest';
import proxy from '../../edge-functions/api/[[default]].js';
const host='https://mirror.example';
afterEach(()=>vi.unstubAllGlobals());
describe('fixed upstream mirror',()=>{
 it('accepts ArrayBuffer chunks from the edge runtime without corrupting JSON',async()=>{
  const bytes=new TextEncoder().encode('{"text":"虚构情境"}');
  let forwarded;
  vi.stubGlobal('fetch',async request=>{forwarded=await request.json();return new Response('{}')});
  const request={url:host+'/api/session',method:'POST',headers:new Headers({Origin:host}),body:new ReadableStream({start(controller){controller.enqueue(bytes.buffer);controller.close()}})};
  const response=await proxy({request});
  expect(response.status).toBe(200);expect(forwarded).toEqual({text:'虚构情境'});
 });
 it('preserves streaming response and host-local session cookie',async()=>{
  let received;
  vi.stubGlobal('fetch',async request=>{received=request;return new Response('event: stage\ndata: {"stage":"request"}\n\n',{headers:{'Content-Type':'text/event-stream','Set-Cookie':'inquire_session=opaque; HttpOnly; Secure; SameSite=Strict; Path=/api'}})});
  const result=await proxy({request:new Request(host+'/api/inquiry',{method:'POST',headers:{Origin:host,Cookie:'unrelated=private; inquire_session=opaque'},body:'{"consent":true}'})});
  expect(received.url).toBe('https://inquire-experience.inquire-ethics-lab.workers.dev/api/inquiry');
  expect(received.headers.get('origin')).toBe('https://inquire-experience.inquire-ethics-lab.workers.dev');
  expect(received.headers.get('cookie')).toBe('inquire_session=opaque');
  expect(result.headers.get('cache-control')).toBe('no-store');
  expect(result.headers.get('set-cookie')).toContain('inquire_session=opaque');
  expect(await result.text()).toContain('event: stage');
 });
 it('forwards Unicode JSON using the documented edge Request body types',async()=>{
  const NativeRequest=Request;
  vi.stubGlobal('Request',class extends NativeRequest{
   constructor(url,init){if(init?.body instanceof Uint8Array)throw new TypeError('Unsupported edge body type');super(url,init)}
  });
  let forwarded;
  vi.stubGlobal('fetch',async request=>{forwarded=await request.json();return new Response('{}')});
  const response=await proxy({request:new NativeRequest(host+'/api/session',{method:'POST',headers:{Origin:host},body:JSON.stringify({text:'虚构情境'})})});
  expect(response.status).toBe(200);expect(forwarded).toEqual({text:'虚构情境'});
 });
 it('rejects arbitrary targets, foreign origins and oversized bodies without forwarding',async()=>{
  const fetcher=vi.fn();vi.stubGlobal('fetch',fetcher);
  expect((await proxy({request:new Request(host+'/api/arbitrary')})).status).toBe(404);
  expect((await proxy({request:new Request(host+'/api/session',{method:'POST',headers:{Origin:'https://foreign.example'},body:'{}'})})).status).toBe(403);
  expect((await proxy({request:new Request(host+'/api/inquiry',{method:'POST',headers:{Origin:host},body:'x'.repeat(20001)})})).status).toBe(413);
  expect(fetcher).not.toHaveBeenCalled();
 });
});
