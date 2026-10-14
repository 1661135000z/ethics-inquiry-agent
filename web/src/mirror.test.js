import {describe,it,expect,vi,afterEach} from 'vitest';
import proxy from '../../edge-functions/api/[[default]].js';
const host='https://mirror.example';
afterEach(()=>vi.unstubAllGlobals());
describe('fixed upstream mirror',()=>{
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
 it('rejects arbitrary targets, foreign origins and oversized bodies without forwarding',async()=>{
  const fetcher=vi.fn();vi.stubGlobal('fetch',fetcher);
  expect((await proxy({request:new Request(host+'/api/arbitrary')})).status).toBe(404);
  expect((await proxy({request:new Request(host+'/api/session',{method:'POST',headers:{Origin:'https://foreign.example'},body:'{}'})})).status).toBe(403);
  expect((await proxy({request:new Request(host+'/api/inquiry',{method:'POST',headers:{Origin:host},body:'x'.repeat(20001)})})).status).toBe(413);
  expect(fetcher).not.toHaveBeenCalled();
 });
});
