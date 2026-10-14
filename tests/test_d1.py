"""Exercise production D1 SQL against SQLite, with the binding interface only."""
import sqlite3
import unittest
from unittest.mock import patch
from pathlib import Path
from edge.d1 import D1Store
from edge.service import Service
from edge.policy import APIError
from test_api import Transport

class Statement:
    def __init__(self,db,sql,args=()):self.db,self.sql,self.args=db,sql,args
    def bind(self,*args):return Statement(self.db,self.sql,args)
    async def first(self):
        row=self.db.connection.execute(self.sql,self.args).fetchone()
        return dict(row) if row else None
    async def run(self):
        before=self.db.connection.total_changes
        self.db.connection.execute(self.sql,self.args)
        return {'meta':{'changes':self.db.connection.total_changes-before}}
class Binding:
    def __init__(self):
        self.connection=sqlite3.connect(':memory:')
        self.connection.row_factory=sqlite3.Row
        self.connection.executescript((Path(__file__).parent.parent/'edge/schema.sql').read_text())
    def prepare(self,sql):return Statement(self,sql)
    async def batch(self,statements):
        with self.connection:return [await s.run() for s in statements]

class D1Tests(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):self.binding.connection.close()
    async def asyncSetUp(self):
        self.binding=Binding();self.store=D1Store(self.binding);self.transport=Transport()
        self.service=Service(self.store,self.transport,{'GEMINI_API_KEY':'placeholder','GEMINI_FREE_TIER_CONFIRMED':'true','ACCESS_CODE':'test'})
        self.token,_=await self.service.create()
        self.body={'provider':'gemini','model':'gemini-2.5-flash','consent':True,'access_code':'test','version':0,'request_id':'d1-request-0001','text':'This is a fictional audit concern.'}
    async def test_d1_commit_and_idempotent_replay(self):
        a=[e async for e in self.service.inquire(self.token,self.body)]
        b=[e async for e in self.service.inquire(self.token,self.body)]
        self.assertEqual(a[-1],b[-1]);self.assertEqual(len(self.transport.calls),1)
        self.assertEqual((await self.store.get(self.token))['version'],1)
    async def test_failed_output_releases_lease_but_counts_attempt(self):
        self.transport.raw='{}'
        with self.assertRaises(APIError):[e async for e in self.service.inquire(self.token,self.body)]
        self.assertEqual((await self.store.get(self.token))['attempts'],1)
        self.transport.raw='{"question":"Who can independently verify the audit evidence?","focus":"evidence","observations":[]}'
        result=[e async for e in self.service.inquire(self.token,{**self.body,'request_id':'d1-request-0002'})]
        self.assertEqual(result[-1]['data']['attempts'],2)
    async def test_new_session_keeps_attempt_budget(self):
        t,s=await self.service.create(attempts=24)
        with self.assertRaises(APIError):[e async for e in self.service.inquire(t,self.body)]
        self.assertEqual(len(self.transport.calls),0)
    async def test_stale_response_cannot_overwrite_newer_lease(self):
        await self.store.reserve(self.token,0,'request-0001','x')
        self.binding.connection.execute('UPDATE sessions SET busy=?',('new-request',))
        snapshot=await self.store.get(self.token);snapshot['version']=1
        with self.assertRaises(APIError):await self.store.finish(self.token,'request-0001',snapshot)
        self.assertEqual((await self.store.get(self.token))['version'],0)
    async def test_transport_deadline_has_commit_margin(self):
        with patch('edge.d1.time.time',return_value=1000):
            await self.store.reserve(self.token,0,'request-margin','x')
        with patch('edge.d1.time.time',return_value=1061):
            snapshot=await self.store.get(self.token);snapshot['version']=1
            await self.store.finish(self.token,'request-margin',snapshot)
            self.assertEqual((await self.store.get(self.token))['version'],1)

if __name__=='__main__':unittest.main()
