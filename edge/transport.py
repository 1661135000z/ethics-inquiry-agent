"""Fixed provider URLs and bounded, sanitized HTTP handling."""
import json
from .policy import APIError

def request_payload(provider, model, key, messages):
    headers={'Content-Type':'application/json'}
    if provider=='gemini':
        headers['x-goog-api-key']=key
        url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
        payload={'systemInstruction':{'parts':[{'text':'\n'.join(m['content'] for m in messages if m['role']=='system')}]},
                 'contents':[{'role':'model' if m['role']=='assistant' else 'user','parts':[{'text':m['content']}]} for m in messages if m['role']!='system'],
                 'generationConfig':{'temperature':0.3,'maxOutputTokens':1600,'responseMimeType':'application/json'}}
        if model.startswith('gemini-2.5-'): payload['generationConfig']['thinkingConfig']={'thinkingBudget':0}
    else:
        headers['Authorization']='Bearer '+key
        url='https://open.bigmodel.cn/api/paas/v4/chat/completions' if provider=='zhipu' else 'https://openrouter.ai/api/v1/chat/completions'
        payload={'model':model,'messages':messages,'temperature':0.3,'max_tokens':1600,'stream':False,'response_format':{'type':'json_object'}}
        if provider=='zhipu': payload['thinking']={'type':'disabled'}
        else:
            payload['reasoning']={'enabled':False}
            payload['provider']={'require_parameters':True}
    return url,headers,payload

def parse_response(provider, model, status, data):
    if status!=200:
        code='auth' if status in {401,403} else 'quota' if status in {402,429} else 'unavailable'
        message={401:'服务未接受密钥，请检查密钥及申请平台。',403:'访问受限，请检查账号、地区和权限。',404:'模型或资源不可用，请更换允许的模型。',429:'免费额度或服务容量不足，请稍后再试或手动切换。'}.get(status,'模型服务暂不可用，请稍后重试。')
        raise APIError(code,f'{message}（HTTP {status}）',502)
    try:
        if provider=='gemini':
            raw=''.join(p.get('text','') for p in data['candidates'][0]['content']['parts'] if not p.get('thought'))
            actual=data.get('modelVersion',model); tokens=data.get('usageMetadata',{}).get('totalTokenCount')
        else:
            raw=data['choices'][0]['message']['content']; actual=data.get('model',model); tokens=data.get('usage',{}).get('total_tokens')
        if not isinstance(raw,str) or not 1<=len(raw)<=16000: raise ValueError()
    except (KeyError,TypeError,ValueError,IndexError):
        raise APIError('format','服务返回空白或无法识别的回复。',502) from None
    return raw,{'model':actual,'tokens':tokens}

class NativeTransport:
    async def complete(self, provider, model, key, messages):
        import httpx
        url,headers,payload=request_payload(provider,model,key,messages)
        try:
            async with httpx.AsyncClient(timeout=45,follow_redirects=False) as http:
                async with http.stream('POST',url,headers=headers,json=payload) as response:
                    buffer=bytearray()
                    async for chunk in response.aiter_bytes():
                        buffer.extend(chunk)
                        if len(buffer)>131072: raise APIError('format','模型返回内容超过安全长度。',502)
                    data=json.loads(buffer) if response.status_code==200 else {}
                    return parse_response(provider,model,response.status_code,data)
        except (httpx.HTTPError,ValueError):
            raise APIError('network','连接失败或超时。Gemini 不可用时请手动切换 GLM。',502) from None

