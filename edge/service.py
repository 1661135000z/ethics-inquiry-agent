"""Portable async orchestration. No vendor SDK, UI, sockets or thread locks."""
from dataclasses import asdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import secrets
import re
from inquiry.core import Session, system_prompt, parse_reply, ModelOutputError
from inquiry.examples import EXAMPLES
from .policy import APIError, credentials, MODELS, KEYS

class Service:
    def __init__(self, store, transport, env):
        self.store, self.transport, self.env=store, transport, env

    def configuration(self):
        return {'providers':[{'id':p,'models':list(dict.fromkeys([self.default_model(p),*models])), 'default_model':self.default_model(p),
                 'configured':bool(self.env.get(KEYS[p])) and (bool(self.env.get('ACCESS_CODE')) or self.env.get('DEMO_ACCESS_ENABLED','').lower()=='true'),
                 'free_confirmed':self.env.get(p.upper()+'_FREE_TIER_CONFIRMED','').lower()=='true'} for p,models in MODELS.items() if p!='deepseek'],
                 'cases':EXAMPLES,'principle':'objectivity','demo_access':self.env.get('DEMO_ACCESS_ENABLED','').lower()=='true',
                 'paid_backup':{'id':'deepseek','models':['deepseek-flash'],'configured':bool(self.env.get('DEEPSEEK_API_KEY')),'free_confirmed':False}}

    def default_model(self,provider):
        configured=self.env.get({'gemini':'GEMINI_MODEL','zhipu':'ZHIPU_MODEL','openrouter':'OPENROUTER_MODEL','deepseek':'DEEPSEEK_MODEL'}[provider],'')
        if configured in MODELS[provider] or (provider=='openrouter' and re.fullmatch(r'[\w.-]+/[\w.-]+:free',configured)):
            return configured
        return MODELS[provider][0]

    async def create(self, attempts=0):
        token=secrets.token_urlsafe(32)
        snapshot={'version':0,'attempts':attempts,'session':asdict(Session()),'initial_text':'','case_id':'blank'}
        await self.store.create(token,snapshot)
        return token,snapshot

    async def restore(self, token): return await self.store.get(token)

    async def inquire(self, token, body, fallback_token=None):
        if not isinstance(body,dict): raise APIError('input','请求格式无法识别。')
        provider,model,key=credentials(body,self.env)
        if body.get('consent') is not True: raise APIError('consent','请确认仅发送虚构或匿名内容。')
        operation=body.get('operation','submit')
        if operation not in {'submit','switch','regenerate'}: raise APIError('input','未知操作。')
        text=body.get('text','')
        if not isinstance(text,str) or (operation!='regenerate' and not 1<=len(text.strip())<=4000):
            raise APIError('input','请输入1–4,000个字符。')
        language=body.get('language','中文')
        if language not in {'中文','English'}: raise APIError('input','未知语言。')
        rid=body.get('request_id','')
        if not isinstance(rid,str) or not re.fullmatch(r'[A-Za-z0-9-]{8,80}',rid): raise APIError('input','请求标识无法识别。')
        version=body.get('version')
        if type(version) is not int: raise APIError('input','缺少会话版本。')
        fingerprint=hashlib.sha256(json.dumps([provider,model,operation,text,language,version,body.get('case_id','blank')],ensure_ascii=False).encode()).hexdigest()
        if provider=='deepseek':fingerprint='paid:'+fingerprint
        prior=await self.store.reserve(token,version,rid,fingerprint)
        if prior is not None:
            yield {'event':'complete','data':prior}
            return
        try:
            state=await self.store.get(token)
            session=Session() if operation=='switch' else Session(**deepcopy(state['session']))
            if operation=='regenerate':
                if not session.messages or session.messages[-1]['role']!='assistant': raise APIError('input','暂无可重新生成的追问。')
                candidate=session.messages[:-1]
            else:
                if session.turns>=(15 if provider=='deepseek' else 12): raise APIError('limit','已达到15轮，请导出并开始新对话。' if provider=='deepseek' else '已达到12轮，请导出并开始新对话。')
                if sum(len(m['content']) for m in session.messages)+len(text.strip())>24000: raise APIError('limit','已达到上下文长度限制。')
                candidate=session.messages+[{'role':'user','content':text.strip()}]
            yield {'event':'stage','data':{'stage':'input'}}
            yield {'event':'stage','data':{'stage':'request'}}
            raw,meta=await self.transport.complete(provider,model,key,[{'role':'system','content':system_prompt(language,session.observations)},*candidate])
            yield {'event':'stage','data':{'stage':'validate'}}
            question,focus,quotes=parse_reply(raw,[m['content'] for m in candidate if m['role']=='user'])
            session.messages=candidate+[{'role':'assistant','content':question}]
            for quote in quotes:
                if quote not in session.observations: session.observations.append(quote)
            session.observations=session.observations[-30:]; session.focus=focus
            record={'turn':session.turns,'time':datetime.now(timezone.utc).isoformat(),
                    'provider':provider,'model':str(meta.get('model',model))[:120],
                    'tokens':meta.get('tokens') if type(meta.get('tokens')) is int else None,'focus':focus}
            if operation=='regenerate':
                record['regenerations']=(session.records[-1].get('regenerations',0) if session.records else 0)+1
                session.records=session.records[:-1]+[record]
            else: session.records.append(record)
            state['session']=asdict(session); state['version']+=1
            if provider=='zhipu':state.pop('backup_until',None)
            if session.turns==1 and operation!='regenerate':
                state['initial_text']=text.strip()
                case=body.get('case_id','blank')
                state['case_id']=case if case in {c['id'] for c in EXAMPLES} else 'blank'
            yield {'event':'stage','data':{'stage':'commit'}}
            await self.store.finish(token,rid,state)
            yield {'event':'complete','data':state}
        except ModelOutputError:
            await self.store.finish(token,rid)
            raise APIError('validation','回复未通过伦理追问检查，原对话和输入已保留。请重试或切换模型。',422) from None
        except APIError as error:
            await self.store.finish(token,rid)
            if provider=='zhipu' and error.code in {'glm_capacity','glm_rate_limit','glm_busy','network','unavailable','quota'}:
                await self.store.grant_backup(fallback_token or token)
                error.backup_available=True
            raise
        except BaseException:
            await self.store.finish(token,rid)
            raise

