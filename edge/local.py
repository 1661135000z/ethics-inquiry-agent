"""Native Python API and production-build static server."""
import json
import os
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from dotenv import load_dotenv
from .service import Service, APIError
from .store import MemoryStore
from .transport import NativeTransport
from inquiry.core import Session
from inquiry.review_packet import build_review_packet

async def request_body(request):
    parts=[];size=0
    async for part in request.stream():
        size+=len(part)
        if size>20000:raise APIError('input','请求过长。',413)
        parts.append(part)
    try:
        value=json.loads(b''.join(parts))
        if not isinstance(value,dict):raise ValueError()
        return value
    except (ValueError,TypeError):raise APIError('input','请求格式无法识别。') from None

def create_app(service=None):
    load_dotenv()
    service=service or Service(MemoryStore(),NativeTransport(),dict(os.environ))
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    @app.middleware('http')
    async def guard(request,call_next):
        origin=request.headers.get('origin')
        if request.url.path.startswith('/api/') and request.method=='POST':
            if origin and urlparse(origin).hostname!=request.url.hostname:
                return JSONResponse({'error':{'code':'origin','message':'请求来源不允许。'}},status_code=403)
            try:
                size=int(request.headers.get('content-length','0'))
                if size>20000: return JSONResponse({'error':{'code':'input','message':'请求过长。'}},status_code=413)
            except ValueError:
                return JSONResponse({'error':{'code':'input','message':'请求长度无法识别。'}},status_code=400)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        if request.url.path.startswith('/api/'): response.headers['Cache-Control']='no-store'
        return response

    @app.exception_handler(APIError)
    async def api_error(request,error): return JSONResponse({'error':{'code':error.code,'message':error.message}},status_code=error.status)

    @app.get('/api/health')
    async def health(): return {'ok':True,'runtime':'native-python'}
    @app.get('/api/config')
    async def config(): return service.configuration()
    def token(request):
        t=request.cookies.get('inquire_session')
        if not t: raise APIError('expired','会话不可用，请重新开始。',410)
        return t
    @app.post('/api/session')
    async def session(request:Request):
        body=await request_body(request)
        old=request.cookies.get('inquire_session')
        if old and not body.get('new'):
            try: return JSONResponse(await service.restore(old))
            except APIError as e:
                if e.code!='expired': raise
        attempts=0
        if old and body.get('new'):
            try:
                prior=await service.restore(old)
                attempts=prior['attempts']
            except APIError: pass
        t,snapshot=await service.create(attempts=attempts)
        response=JSONResponse(snapshot)
        response.set_cookie('inquire_session',t,max_age=7200,httponly=True,samesite='strict',secure=request.url.scheme=='https',path='/api')
        return response
    @app.post('/api/connect')
    async def connect(request:Request):
        body=await request_body(request);t,_=await service.create()
        body.update({'request_id':__import__('secrets').token_hex(16),'version':0,'operation':'submit','consent':True,
                     'text':'I am reviewing an AI audit screening result and do not know who independently checked it.'})
        result=None
        async for event in service.inquire(t,body):
            if event['event']=='complete': result=event['data']
        return {'ok':True,'model':result['session']['records'][-1]['model']}
    @app.post('/api/inquiry')
    async def inquiry(request:Request):
        body=await request_body(request); t=token(request)
        async def stream():
            try:
                async for event in service.inquire(t,body):
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'],ensure_ascii=False)}\n\n"
            except APIError as e:
                yield f"event: error\ndata: {json.dumps({'code':e.code,'message':e.message},ensure_ascii=False)}\n\n"
            except Exception:
                yield 'event: error\ndata: {"code":"internal","message":"请求未完成，原对话和输入已保留。"}\n\n'
        return StreamingResponse(stream(),media_type='text/event-stream',headers={'Cache-Control':'no-store'})
    @app.get('/api/export')
    async def export(request:Request):
        snapshot=await service.restore(token(request));session=Session(**snapshot['session'])
        language=request.query_params.get('language','中文')
        return StreamingResponse(iter([session.export(language)]),media_type='text/markdown',headers={'Content-Disposition':'attachment; filename="inquire-conversation.md"'})
    @app.get('/api/review')
    async def review(request:Request):
        snapshot=await service.restore(token(request)); session=Session(**snapshot['session'])
        if session.turns<2: raise APIError('input','至少完成两轮对话后生成复核简报。')
        html=build_review_packet(session,language=request.query_params.get('language','中文'))
        return StreamingResponse(iter([html]),media_type='text/html',headers={'Content-Disposition':'attachment; filename="inquire-review.html"'})
    @app.get('/{path:path}')
    async def assets(path:str):
        root=(Path(__file__).parent.parent/'web'/'dist').resolve()
        candidate=(root/path).resolve()
        if root not in candidate.parents or not candidate.is_file(): candidate=root/'index.html'
        if not candidate.exists(): return JSONResponse({'message':'Build the React frontend first.'},status_code=503)
        return FileResponse(candidate)
    return app

app=create_app()
