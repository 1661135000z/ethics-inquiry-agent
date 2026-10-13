import asyncio
import json
import unittest

from edge.service import Service, APIError
from edge.store import MemoryStore


class Transport:
    def __init__(self, raw=None):
        self.raw = raw or '{"question":"Who can independently verify the missing entries?","focus":"evidence","observations":[]}'
        self.calls = []

    async def complete(self, provider, model, key, messages):
        self.calls.append((provider, model, key, messages))
        return self.raw, {"provider": provider, "model": model, "tokens": 40}


class APITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.transport = Transport()
        self.service = Service(MemoryStore(), self.transport, {
            'GEMINI_API_KEY': 'owner-placeholder', 'GEMINI_FREE_TIER_CONFIRMED':'true',
            'ACCESS_CODE':'test-access'})
        self.token, self.snapshot = await self.service.create()
        self.body = {'request_id':'request-0001','version':0,'provider':'gemini',
                     'model':'gemini-2.5-flash','text':'The AI dashboard has missing entries.',
                     'consent':True,'access_code':'test-access','language':'English'}

    async def events(self, body):
        return [e async for e in self.service.inquire(self.token, body)]

    async def test_commit_and_idempotency(self):
        events = await self.events(self.body)
        result = events[-1]['data']
        self.assertEqual(result['version'], 1)
        self.assertEqual(len(result['session']['messages']), 2)
        repeated = await self.events(self.body)
        self.assertEqual(repeated[-1]['data'], result)
        self.assertEqual(len(self.transport.calls), 1)

    async def test_invalid_model_output_keeps_session(self):
        self.transport.raw = '{"question":"You should sign this audit.","focus":"review"}'
        with self.assertRaises(APIError): await self.events(self.body)
        state = await self.service.restore(self.token)
        self.assertEqual(state['version'], 0)
        self.assertEqual(state['session']['messages'], [])
        self.assertEqual(state['attempts'], 1)

    async def test_key_is_request_scoped_and_visitor_wins(self):
        body = {**self.body,'api_key':'visitor-placeholder','free_confirmed':True}
        result = (await self.events(body))[-1]['data']
        self.assertEqual(self.transport.calls[0][2], 'visitor-placeholder')
        self.assertNotIn('placeholder', json.dumps(result))
        self.assertNotIn('placeholder', json.dumps(await self.service.restore(self.token)))

    async def test_consent_and_free_allowlist(self):
        for update in [{'consent':False},{'model':'paid-model'},{'access_code':'wrong'}]:
            with self.assertRaises(APIError): await self.events({**self.body,**update})
        self.assertEqual(len(self.transport.calls),0)

    async def test_version_conflict_does_not_call_model(self):
        await self.events(self.body)
        with self.assertRaises(APIError): await self.events({**self.body,'request_id':'request-0002'})
        self.assertEqual(len(self.transport.calls),1)

    async def test_switch_failure_and_regeneration_are_transactional(self):
        await self.events(self.body)
        self.transport.raw = '{}'
        with self.assertRaises(APIError):
            await self.events({**self.body,'request_id':'request-0002','version':1,'operation':'switch','text':'An entirely different audit concern.'})
        self.assertEqual(len((await self.service.restore(self.token))['session']['messages']),2)
        self.transport.raw = '{"question":"Which original record could help verify the entries?","focus":"evidence","observations":[]}'
        result = (await self.events({**self.body,'request_id':'request-0003','version':1,'operation':'regenerate'}))[-1]['data']
        self.assertEqual(len(result['session']['messages']),2)
        self.assertEqual(result['session']['records'][0]['regenerations'],1)

    async def test_configuration_never_returns_credentials(self):
        self.assertNotIn('placeholder',json.dumps(self.service.configuration()))

    async def test_expired_session_fails(self):
        self.service.store.items[self.token]['expires'] = 0
        with self.assertRaises(APIError): await self.service.restore(self.token)

    async def test_duplicate_id_with_different_input_is_rejected(self):
        await self.events(self.body)
        with self.assertRaises(APIError): await self.events({**self.body,'text':'Another scenario with the same request ID.'})

if __name__ == '__main__': unittest.main()
