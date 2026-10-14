"""D1-backed atomic attempts, leases and transactional conversation snapshots."""
import hashlib
import json
import time
from .policy import APIError

def plain(value):
    return value.to_py() if hasattr(value,'to_py') else value

class D1Store:
    def __init__(self, db): self.db=db
    def stmt(self,sql,*args): return self.db.prepare(sql).bind(*args)
    def token(self,t): return hashlib.sha256(t.encode()).hexdigest()
    async def grant_backup(self,token):
        await self.get(token)
        await self.stmt("UPDATE sessions SET payload=json_set(payload,'$.backup_until',?) WHERE token=? AND expires>?",int(time.time())+1800,self.token(token),int(time.time())).run()
    async def create(self,token,snapshot):
        now=int(time.time())
        await self.db.batch([
            self.stmt('DELETE FROM sessions WHERE expires<?',now),
            self.stmt('DELETE FROM requests WHERE created<?',now-86400),
            self.stmt('INSERT INTO sessions(token,payload,expires) SELECT ?,?,? WHERE (SELECT count(*) FROM sessions)<128',self.token(token),json.dumps(snapshot,ensure_ascii=False),now+7200)])
        try: await self.get(token)
        except APIError: raise APIError('capacity','当前会话容量已满，请稍后再试。',429) from None
    async def get(self,token):
        row=plain(await self.stmt('SELECT payload FROM sessions WHERE token=? AND expires>?',self.token(token),int(time.time())).first())
        if not row: raise APIError('expired','会话已过期，请开始新的探究。',410)
        return json.loads(row['payload'])
    async def reserve(self,token,version,rid,fingerprint):
        paid=fingerprint.startswith('paid:');token=self.token(token);now=int(time.time())
        old=plain(await self.stmt('SELECT fingerprint,result FROM requests WHERE token=? AND request_id=?',token,rid).first())
        if old:
            if old['fingerprint']!=fingerprint: raise APIError('duplicate','重复请求的内容不一致。',409)
            if old['result']: return json.loads(old['result'])
            raise APIError('duplicate','请求已尝试或处理中，请恢复会话后继续。',409)
        if paid:
            row=plain(await self.stmt("SELECT json_extract(payload,'$.backup_until') AS allowed FROM sessions WHERE token=? AND expires>?",token,now).first())
            if not row or not row['allowed'] or row['allowed']<=now:raise APIError('backup_gate','请先在GLM失败后选择备用模型。',403)
        results=plain(await self.db.batch([
            self.stmt("INSERT OR IGNORE INTO requests(token,request_id,fingerprint,created) SELECT ?,?,?,? WHERE EXISTS(SELECT 1 FROM sessions WHERE token=? AND expires>? AND busy_until<? AND json_extract(payload,'$.version')=? AND json_extract(payload,'$.attempts')<24 AND (?=0 OR json_extract(payload,'$.backup_until')>?)) AND (SELECT count(*) FROM requests WHERE created>?)<40 AND (SELECT count(*) FROM requests WHERE created>?)<150 AND (?=0 OR ((SELECT count(*) FROM requests WHERE token=? AND fingerprint LIKE 'paid:%')<10 AND (SELECT count(*) FROM requests WHERE fingerprint LIKE 'paid:%' AND created>?)<60))",token,rid,fingerprint,now,token,now,now,version,int(paid),now,now-3600,now-86400,int(paid),token,now-86400),
            self.stmt("UPDATE sessions SET busy=?,busy_until=?,payload=json_set(payload,'$.attempts',json_extract(payload,'$.attempts')+1) WHERE token=? AND busy_until<? AND json_extract(payload,'$.version')=? AND EXISTS(SELECT 1 FROM requests WHERE token=? AND request_id=? AND created=? AND result IS NULL)",rid,now+90,token,now,version,token,rid,now)
        ]))
        results=[plain(r) for r in results]
        if not plain(results[0]['meta'])['changes'] or not plain(results[1]['meta'])['changes']:
            if paid:
                counts=plain(await self.stmt("SELECT (SELECT count(*) FROM requests WHERE token=? AND fingerprint LIKE 'paid:%') AS session_paid,(SELECT count(*) FROM requests WHERE fingerprint LIKE 'paid:%' AND created>?) AS day_paid",token,now-86400).first())
                if counts['session_paid']>=10 or counts['day_paid']>=60:raise APIError('backup_limit','备用模型请求额度已达到限制，请返回GLM或稍后再试。',429)
            raise APIError('conflict_or_limit','会话正在更新、已过期或达到请求限制。请恢复后继续。',409)
        return None
    async def finish(self,token,rid,snapshot=None):
        token=self.token(token);now=int(time.time())
        if snapshot is None:
            await self.stmt("UPDATE sessions SET busy='',busy_until=0 WHERE token=? AND busy=?",token,rid).run()
            return
        payload=json.dumps(snapshot,ensure_ascii=False)
        result=plain(await self.db.batch([
            self.stmt("UPDATE sessions SET payload=?,expires=? WHERE token=? AND busy=? AND busy_until>? AND json_extract(payload,'$.version')=?",payload,now+7200,token,rid,now,snapshot['version']-1),
            self.stmt("UPDATE requests SET result=? WHERE token=? AND request_id=? AND EXISTS(SELECT 1 FROM sessions WHERE token=? AND busy=? AND payload=?)",payload,token,rid,token,rid,payload),
            self.stmt("UPDATE sessions SET busy='',busy_until=0 WHERE token=? AND busy=?",token,rid)
        ]))
        if not plain(plain(result[0])['meta'])['changes']:
            raise APIError('conflict','会话版本已变化，已保留先前记录。',409)
