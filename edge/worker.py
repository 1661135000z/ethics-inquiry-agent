"""Python Worker: scoped credentials, transactional inquiry and real SSE stages."""
from workers import WorkerEntrypoint, Response, fetch
from urllib.parse import urlparse, parse_qs
from http.cookies import SimpleCookie
import asyncio
import json
import secrets
from edge.service import Service, APIError
from edge.policy import KEYS
from edge.d1 import D1Store
from edge.transport import request_payload, parse_response
from inquiry.core import Session
from inquiry.review_packet import build_review_packet

class WorkerTransport:
    async def complete(self, provider, model, key, messages):
        url,headers,payload=request_payload(provider,model,key,messages)
        try:
            response=await asyncio.wait_for(fetch(url,method='POST',headers=headers,body=json.dumps(payload)),45)
            raw=await asyncio.wait_for(response.text(),15)
            if len(raw)>131072:raise APIError('format','模型返回超过安全长度。',502)
            try:data=json.loads(raw)
            except ValueError:data={}
            return parse_response(provider,model,response.status,data)
        except APIError:raise
        except Exception:raise APIError('network','无法连接模型服务，请检查网络、地区或切换模型。',502) from None

async def request_body(request):
    length=request.headers.get('content-length')
    if length:
        try:
            if int(length)>20000:raise APIError('input','请求过长。',413)
        except ValueError:raise APIError('input','请求长度无法识别。') from None
    reader=request.body.getReader()
    parts=[];size=0
    try:
        while True:
            item=await reader.read()
            if item.done:break
            part=bytes(item.value.to_py());size+=len(part)
            if size>20000:raise APIError('input','请求过长。',413)
            parts.append(part)
        value=json.loads(b''.join(parts))
        if not isinstance(value,dict):raise ValueError()
        return value
    except (ValueError,TypeError):raise APIError('input','请求格式无法识别。') from None
    finally:reader.releaseLock()

def token(request):
    c=SimpleCookie();c.load(request.headers.get('cookie') or '')
    value=c.get('inquire_session')
    if not value:raise APIError('expired','会话不可用，请重新开始。',410)
    return value.value

def stream_events(service,t,body):
    from js import ReadableStream,TextEncoder
    from pyodide.ffi import create_proxy,to_js
    enc=TextEncoder.new()
    async def start(controller):
        try:
            async for event in service.inquire(t,body):
                controller.enqueue(enc.encode(f"event: {event['event']}\ndata: {json.dumps(event['data'],ensure_ascii=False)}\n\n"))
        except APIError as e:
            controller.enqueue(enc.encode(f"event: error\ndata: {json.dumps({'code':e.code,'message':e.message},ensure_ascii=False)}\n\n"))
        except Exception:
            controller.enqueue(enc.encode('event: error\ndata: {"code":"internal","message":"请求未完成，原记录已保留。"}\n\n'))
        finally:
            controller.close();proxy.destroy()
    proxy=create_proxy(start)
    return ReadableStream.new(to_js({'start':proxy}))

class Default(WorkerEntrypoint):
    async def fetch(self,request):
        path=urlparse(request.url).path
        headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'}
        try:
            if path=='/api/health':return Response.json({'ok':True,'runtime':'python-worker','inquiry_api_ready':hasattr(self.env,'DB')},headers=headers)
            if not hasattr(self.env,'DB'):raise APIError('configuration','数据库尚未配置。',503)
            env={k:str(getattr(self.env,k,'')) for k in [*KEYS.values(),'GEMINI_FREE_TIER_CONFIRMED','ZHIPU_FREE_TIER_CONFIRMED','GEMINI_MODEL','ZHIPU_MODEL','OPENROUTER_MODEL','ACCESS_CODE','DEMO_ACCESS_ENABLED']}
            service=Service(D1Store(self.env.DB),WorkerTransport(),env)
            if request.method=='POST':
                origin=request.headers.get('origin')
                if origin and origin.rstrip('/')!=f'{urlparse(request.url).scheme}://{urlparse(request.url).netloc}':raise APIError('origin','请求来源不允许。',403)
                body=await request_body(request)
            else:body={}
            if path=='/api/config' and request.method=='GET':return Response.json(service.configuration(),headers=headers)
            if path=='/api/session' and request.method=='POST':
                old=None
                try:old=token(request)
                except APIError:pass
                if old and not body.get('new'):
                    try:return Response.json(await service.restore(old),headers=headers)
                    except APIError as e:
                        if e.code!='expired':raise
                attempts=0
                if old:
                    try:attempts=(await service.restore(old))['attempts']
                    except APIError:pass
                t,snapshot=await service.create(attempts)
                headers['Set-Cookie']=f'inquire_session={t}; HttpOnly; SameSite=Strict; Path=/api; Max-Age=7200'+('; Secure' if request.url.startswith('https:') else '')
                return Response.json(snapshot,headers=headers)
            if path=='/api/connect' and request.method=='POST':
                t,_=await service.create()
                body.update({'request_id':secrets.token_hex(16),'version':0,'operation':'submit','consent':True,'text':'I am reviewing an AI audit screening result and do not know who independently checked it.'})
                result=None
                async for event in service.inquire(t,body):
                    if event['event']=='complete':result=event['data']
                return Response.json({'ok':True,'model':result['session']['records'][-1]['model']},headers=headers)
            if path=='/api/inquiry' and request.method=='POST':
                headers['Content-Type']='text/event-stream'
                return Response(stream_events(service,token(request),body),headers=headers)
            if path in {'/api/export','/api/review'} and request.method=='GET':
                language=parse_qs(urlparse(request.url).query).get('language',['中文'])[0]
                snapshot=await service.restore(token(request));s=Session(**snapshot['session'])
                if path=='/api/review':
                    if s.turns<2:raise APIError('input','至少完成两轮后生成复核简报。')
                    headers.update({'Content-Type':'text/html; charset=utf-8','Content-Disposition':'attachment; filename="inquire-review.html"'})
                    return Response(build_review_packet(s,language),headers=headers)
                headers.update({'Content-Type':'text/markdown; charset=utf-8','Content-Disposition':'attachment; filename="inquire-conversation.md"'})
                return Response(s.export(language),headers=headers)
            return Response('Not found',status=404,headers=headers)
        except APIError as e:return Response.json({'error':{'code':e.code,'message':e.message}},status=e.status,headers=headers)
        except Exception:return Response.json({'error':{'code':'internal','message':'请求未完成，请稍后重试。'}},status=500,headers=headers)
