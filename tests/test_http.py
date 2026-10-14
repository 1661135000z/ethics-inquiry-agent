import unittest
import httpx
from edge.local import create_app
from edge.service import Service
from edge.store import MemoryStore
from test_api import Transport

class HTTPTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.transport=Transport()
        service=Service(MemoryStore(),self.transport,{'GEMINI_API_KEY':'owner-placeholder','GEMINI_FREE_TIER_CONFIRMED':'true','ACCESS_CODE':'test-access'})
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(service)),base_url='https://inquire.test')
        self.body={'request_id':'http-test-0001','version':0,'provider':'gemini','model':'gemini-2.5-flash','text':'The screening report is missing entries.','consent':True,'access_code':'test-access','language':'English'}
    async def asyncTearDown(self): await self.client.aclose()
    async def test_cookie_sse_and_recovery(self):
        r=await self.client.post('/api/session',json={})
        self.assertIn('HttpOnly',r.headers['set-cookie'])
        self.assertIn('Secure',r.headers['set-cookie'])
        r=await self.client.post('/api/inquiry',json=self.body)
        self.assertIn('event: complete',r.text)
        self.assertNotIn('owner-placeholder',r.text)
        snapshot=(await self.client.post('/api/session',json={})).json()
        self.assertEqual(snapshot['version'],1)
        new=(await self.client.post('/api/session',json={'new':True})).json()
        self.assertEqual(new['attempts'],1)
        self.assertEqual(new['session']['messages'],[])
    async def test_malformed_and_oversized_body_are_safe_errors(self):
        for raw in ['not-json','[]','"text"']:
            r=await self.client.post('/api/session',content=raw)
            self.assertEqual(r.status_code,400)
            self.assertEqual(r.json()['error']['code'],'input')
        r=await self.client.post('/api/session',content='x'*20001)
        self.assertEqual(r.status_code,413)
    async def test_cross_origin_and_unaccepted_export(self):
        r=await self.client.post('/api/session',json={},headers={'Origin':'https://attacker.test'})
        self.assertEqual(r.status_code,403)
        r=await self.client.get('/api/export')
        self.assertEqual(r.status_code,410)
        self.assertEqual(self.transport.calls,[])

