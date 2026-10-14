"""Store contract with a bounded native-memory implementation for local use."""
from copy import deepcopy
import time
from .policy import APIError

class MemoryStore:
    def __init__(self):
        self.items = {}
        self.hour = []
        self.day = []
        self.paid_day=[]

    async def grant_backup(self, token):
        await self.get(token)
        self.items[token]['snapshot']['backup_until']=time.time()+1800

    async def create(self, token, snapshot):
        now=time.time()
        self.items={k:v for k,v in self.items.items() if v['expires']>now}
        if len(self.items)>=128: raise APIError('capacity','当前会话容量已满，请稍后重试。',429)
        self.items[token]={'snapshot':deepcopy(snapshot),'expires':now+7200,'busy':False,'requests':{}}

    async def get(self, token):
        item=self.items.get(token)
        if not item or item['expires']<time.time(): raise APIError('expired','会话已过期。请导出已有内容并开始新的探究。',410)
        return deepcopy(item['snapshot'])

    async def reserve(self, token, version, request_id, fingerprint):
        await self.get(token)
        item=self.items[token]
        prior=item['requests'].get(request_id)
        if prior:
            if prior['fingerprint']!=fingerprint: raise APIError('duplicate','重复请求的内容不一致。',409)
            if prior.get('result'): return deepcopy(prior['result'])
            raise APIError('duplicate','请求已尝试或仍在处理中，请恢复会话后再试。',409)
        if item['busy'] or version!=item['snapshot']['version']: raise APIError('conflict','会话已更新，请恢复后继续。',409)
        now=time.time()
        if fingerprint.startswith('paid:'):
            self.paid_day=[t for t in self.paid_day if t>now-86400]
            if item['snapshot'].get('backup_until',0)<=now:
                raise APIError('backup_gate','请先在GLM失败后选择备用模型。',403)
            if sum(r['fingerprint'].startswith('paid:') for r in item['requests'].values())>=15 or len(self.paid_day)>=60:
                raise APIError('backup_limit','备用模型请求额度已达到限制，请返回GLM或稍后再试。',429)
        self.hour=[t for t in self.hour if t>now-3600]
        self.day=[t for t in self.day if t>now-86400]
        if item['snapshot']['attempts']>=24 or len(self.hour)>=40 or len(self.day)>=150:
            raise APIError('limit','已达到请求限制，请稍后继续。',429)
        self.hour.append(now); self.day.append(now)
        if fingerprint.startswith('paid:'):self.paid_day.append(now)
        item['busy']=True
        item['snapshot']['attempts']+=1
        item['requests'][request_id]={'fingerprint':fingerprint}
        return None

    async def finish(self, token, request_id, snapshot=None):
        item=self.items[token]
        if snapshot is not None:
            item['snapshot']=deepcopy(snapshot)
            item['requests'][request_id]['result']=deepcopy(snapshot)
        item['busy']=False
        item['expires']=time.time()+7200

