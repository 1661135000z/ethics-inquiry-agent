"""Runtime-independent free-model and credential policy."""
import re
MODELS = {
    'gemini': ('gemini-3.5-flash-lite','gemini-3.1-flash-lite','gemini-2.5-flash-lite','gemini-2.5-flash'),
    'zhipu': ('glm-4.7-flash',),
    'openrouter': ('openrouter/free',),
}
KEYS = {'gemini':'GEMINI_API_KEY','zhipu':'ZHIPU_API_KEY','openrouter':'OPENROUTER_API_KEY'}

class APIError(Exception):
    def __init__(self, code, message, status=400):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)

def credentials(body, env):
    provider, model = body.get('provider'), body.get('model')
    if not isinstance(provider,str) or not isinstance(model,str) or provider not in MODELS:
        raise APIError('model','请选择允许的免费模型。')
    allowed=model in MODELS[provider] or (provider=='openrouter' and bool(re.fullmatch(r'[\w.-]+/[\w.-]+:free',model)))
    if not allowed:
        raise APIError('model','请选择允许的免费模型。')
    supplied = body.get('api_key','')
    if not isinstance(supplied,str) or len(supplied)>512:
        raise APIError('configuration','密钥格式无法识别。')
    key = supplied.strip()
    if key:
        free = body.get('free_confirmed') is True
    else:
        access = env.get('ACCESS_CODE','')
        if not access or body.get('access_code') != access:
            raise APIError('access','请输入开发者访问码，或使用自己的 API Key。',403)
        key = env.get(KEYS[provider],'')
        free = env.get(provider.upper()+'_FREE_TIER_CONFIRMED','').lower() == 'true'
    if not key: raise APIError('configuration','尚未配置此服务的 API Key。')
    if provider != 'openrouter' and not free:
        raise APIError('free_tier','请先确认当前账户和模型具备免费档资格。')
    if any(c in key for c in '\r\n'): raise APIError('configuration','密钥不能包含换行。')
    return provider, model, key

