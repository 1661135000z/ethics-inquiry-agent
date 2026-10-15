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
                 'generationConfig':{'temperature':0.3,'maxOutputTokens':3000,'responseMimeType':'application/json'}}
        if model.startswith('gemini-2.5-'): payload['generationConfig']['thinkingConfig']={'thinkingBudget':0}
    else:
        headers['Authorization']='Bearer '+key
        url={'zhipu':'https://open.bigmodel.cn/api/paas/v4/chat/completions','deepseek':'https://api.deepseek.com/chat/completions','openrouter':'https://openrouter.ai/api/v1/chat/completions'}[provider]
        payload={'model':model,'messages':messages,'temperature':0.3,'max_tokens':1600 if provider=='deepseek' else 3000,'stream':False,'response_format':{'type':'json_object'}}
        if provider in {'zhipu','deepseek'}: payload['thinking']={'type':'disabled'}
        else:
            payload['reasoning']={'enabled':False}
            payload['provider']={'require_parameters':True}
    return url,headers,payload

def parse_response(provider, model, status, data):
    if status!=200:
        if provider=='zhipu' and status==429:
            error=data.get('error',{}) if isinstance(data,dict) else {}
            error=error if isinstance(error,dict) else {}
            vendor_code=str(error.get('code',''));detail=str(error.get('message',''))[:8192]
            if vendor_code=='1312' or '访问量过大' in detail or '服务器拥挤' in detail:
                code,message='glm_capacity','GLM服务器当前拥挤，通常等待片刻再试即可恢复。原对话和输入已保留，也可以选择备用模型。'
            elif vendor_code in {'1302','1303'}:
                code,message='glm_rate_limit','GLM当前请求过于集中或并发受限。请等待片刻再试，也可以选择备用模型；这不表示余额不足。'
            else:
                code,message='glm_busy','GLM当前繁忙或限流。请等待片刻再试，也可以选择备用模型；不能仅凭429认定额度用完。'
            raise APIError(code,message+'（HTTP 429）',502)
        if provider=='deepseek' and status==402:
            raise APIError('backup_balance','备用模型余额不足，请返回GLM或联系管理员。',502)
        if provider=='gemini' and status==400:
            error=data.get('error',{}) if isinstance(data,dict) else {}
            error=error if isinstance(error,dict) else {}
            detail=str(error.get('message',''))[:8192].lower()
            reason=str(error.get('status','')).upper()
            # Match only known categories. Never echo vendor text or credentials.
            if 'free tier' in detail and ('country' in detail or 'billing' in detail):
                code,message='free_tier_region','Gemini 判定当前请求地区不支持免费档，请切换 GLM。'
            elif 'location' in detail and ('not supported' in detail or 'unsupported' in detail):
                code,message='region','Gemini 不接受当前请求来源的地区，请切换 GLM；这不是访问码错误。'
            elif ('api key' in detail and ('not valid' in detail or 'invalid' in detail)) or 'api_key_invalid' in detail:
                code,message='auth','Gemini 未接受 API Key，请核对 AI Studio 的密钥，或切换 GLM。'
            elif reason=='INVALID_ARGUMENT':
                code,message='parameters','Gemini 未接受当前模型或请求参数，请更换允许的模型，或切换 GLM。'
            elif reason=='FAILED_PRECONDITION':
                code,message='precondition','Gemini 的账号或地区条件未满足，请检查免费资格，或切换 GLM。'
            else:
                code,message='request','Gemini 拒绝了当前请求，请更换模型或切换 GLM。'
            raise APIError(code,f'{message}（HTTP 400）',502)
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
                    try:data=json.loads(buffer)
                    except ValueError:data={}
                    return parse_response(provider,model,response.status_code,data)
        except (httpx.HTTPError,ValueError):
            raise APIError('network','连接失败或超时。Gemini 不可用时请手动切换 GLM。',502) from None

