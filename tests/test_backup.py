import unittest
from unittest.mock import patch
import httpx
from edge.local import create_app
from edge.policy import APIError
from edge.service import Service
from edge.store import MemoryStore
from edge.d1 import D1Store
from edge.transport import parse_response,request_payload
from test_d1 import Binding
from test_api import Transport

class BackupTransport(Transport):
    async def complete(self,provider,model,key,messages):
        if provider=='zhipu':
            self.calls.append((provider,model,key,messages))
            return parse_response(provider,model,429,{'error':{'code':'1312','message':'该模型当前访问量过大 private-value'}})
        return await super().complete(provider,model,key,messages)

class BackupTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.env={'ZHIPU_API_KEY':'glm-placeholder','ZHIPU_FREE_TIER_CONFIRMED':'true','DEEPSEEK_API_KEY':'backup-placeholder','DEMO_ACCESS_ENABLED':'true'}
        self.transport=BackupTransport();self.store=MemoryStore();self.service=Service(self.store,self.transport,self.env)
        self.token,_=await self.service.create()
        self.body={'provider':'zhipu','model':'glm-4.7-flash','consent':True,'version':0,'request_id':'glm-failure-0001','text':'The dashboard is missing entries.'}
    async def fail_glm(self):
        with self.assertRaises(APIError) as error:
            [e async for e in self.service.inquire(self.token,self.body)]
        self.assertTrue(getattr(error.exception,'backup_available',False))
        self.assertEqual(error.exception.code,'glm_capacity')
        self.assertNotIn('private-value',str(error.exception))
    async def test_no_paid_request_before_glm_failure(self):
        with self.assertRaises(APIError) as error:
            [e async for e in self.service.inquire(self.token,{**self.body,'provider':'deepseek','model':'deepseek-flash','paid_confirmed':True})]
        self.assertEqual(error.exception.code,'backup_gate');self.assertEqual(self.transport.calls,[])
    async def test_glm_failure_offers_backup_but_never_automatically_calls_it(self):
        await self.fail_glm()
        self.assertEqual([c[0] for c in self.transport.calls],['zhipu'])
        self.assertEqual((await self.service.restore(self.token))['session']['messages'],[])
    async def test_manual_backup_runs_the_same_inquiry_checks_and_provenance(self):
        await self.fail_glm()
        result=[e async for e in self.service.inquire(self.token,{**self.body,'provider':'deepseek','model':'deepseek-flash','paid_confirmed':True,'request_id':'backup-request-0001'})]
        self.assertEqual(result[-1]['data']['session']['records'][-1]['provider'],'deepseek')
        self.assertEqual(len(result[-1]['data']['session']['messages']),2)
    async def test_paid_request_requires_explicit_backup_selection_flag(self):
        await self.fail_glm()
        with self.assertRaises(APIError):
            [e async for e in self.service.inquire(self.token,{**self.body,'provider':'deepseek','model':'deepseek-flash','request_id':'backup-request-0001'})]
        self.assertEqual(len(self.transport.calls),1)
    async def test_memory_and_d1_enforce_ten_paid_attempts(self):
        for store in (MemoryStore(),D1Store(Binding())):
            if isinstance(store,D1Store):self.addCleanup(store.db.connection.close)
            service=Service(store,BackupTransport(),self.env);token,_=await service.create()
            with self.assertRaises(APIError):[e async for e in service.inquire(token,self.body)]
            for index in range(10):
                body={**self.body,'provider':'deepseek','model':'deepseek-flash','paid_confirmed':True,'request_id':f'backup-request-{index:04d}','version':index}
                [e async for e in service.inquire(token,body)]
            with self.assertRaises(APIError):
                [e async for e in service.inquire(token,{**body,'request_id':'backup-request-over','version':10})]
            self.assertEqual(len(service.transport.calls),11)
    def test_deepseek_payload_is_fixed_and_non_thinking(self):
        url,headers,payload=request_payload('deepseek','deepseek-flash','backup-placeholder',[{'role':'user','content':'A fictional question'}])
        self.assertEqual(url,'https://api.deepseek.com/chat/completions')
        self.assertEqual(payload['thinking'],{'type':'disabled'})
        self.assertNotIn('provider',payload);self.assertNotIn('reasoning',payload)
    async def test_backup_grant_is_bound_to_session_and_expires(self):
        await self.fail_glm()
        other,_=await self.service.create()
        body={**self.body,'provider':'deepseek','model':'deepseek-flash','paid_confirmed':True,'request_id':'backup-expiry-0001'}
        with self.assertRaises(APIError):[e async for e in self.service.inquire(other,body)]
        self.store.items[self.token]['snapshot']['backup_until']=0
        with self.assertRaises(APIError):[e async for e in self.service.inquire(self.token,body)]
        self.assertEqual(len(self.transport.calls),1)
    async def test_successful_glm_clears_backup_eligibility(self):
        await self.fail_glm();self.service.transport=Transport()
        [e async for e in self.service.inquire(self.token,{**self.body,'request_id':'glm-recovered-0001'})]
        with self.assertRaises(APIError):
            [e async for e in self.service.inquire(self.token,{**self.body,'provider':'deepseek','model':'deepseek-flash','paid_confirmed':True,'request_id':'backup-invalid-0001','version':1})]
        self.assertEqual(len(self.service.transport.calls),1)
    async def test_connection_failure_grants_actual_browser_session_without_paid_probe(self):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(self.service)),base_url='https://fixture.test') as client:
            await client.post('/api/session',json={})
            failure=await client.post('/api/connect',json=self.body)
            self.assertTrue(failure.json()['error']['backup_available'])
            paid={**self.body,'provider':'deepseek','model':'deepseek-flash','paid_confirmed':True,'request_id':'backup-http-0001'}
            probe=await client.post('/api/connect',json=paid)
            self.assertEqual(probe.status_code,403)
            response=await client.post('/api/inquiry',json=paid)
            self.assertIn('event: complete',response.text)
            self.assertEqual([c[0] for c in self.transport.calls],['zhipu','deepseek'])
