import unittest, inspect, json
from inquiry.core import Session, InputError, ModelOutputError
from inquiry.providers import Client, settings_from, ProviderError
import httpx

class WorkflowTests(unittest.TestCase):
    def test_progress_tracks_actual_commit_and_failure(self):
        self.assertIn('progress', inspect.signature(Session.submit).parameters)
        class Fake:
            def complete(self, messages):
                return json.dumps({'question':'What evidence can independently verify the estimate?', 'focus':'evidence','observations':[]}), {'provider':'test','model':'test'}
        stages=[]; session=Session()
        session.submit('My manager pressures me to accept an estimate.', Fake(), progress=stages.append)
        self.assertEqual(stages,['input','request','validate','save','done'])
        stages=[]
        with self.assertRaises(InputError): session.submit('',Fake(),progress=stages.append)
        self.assertEqual(stages,['input'])

    def test_gemini_and_glm_run_full_inquiry_protocol(self):
        def handle(req):
            body=json.loads(req.content)
            if req.url.host=='generativelanguage.googleapis.com':
                self.assertIn('OBJECTIVITY',body['systemInstruction']['parts'][0]['text'])
                reply=json.dumps({'question':'What evidence would help you evaluate this pressure?', 'focus':'pressure','observations':[]})
                return httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':reply}]}}]})
            self.assertEqual(req.url.host,'open.bigmodel.cn')
            self.assertIn('OBJECTIVITY', body['messages'][0]['content'])
            self.assertEqual(body['response_format'],{'type':'json_object'})
            return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps({'question':'Who can review the estimate independently?', 'focus':'review','observations':[]})}}]})
        for service,key in [('gemini','GEMINI_API_KEY'),('zhipu','ZHIPU_API_KEY')]:
            session=Session()
            client=Client(service,settings_from({key:'test-only',service.upper()+'_FREE_TIER_CONFIRMED':'true'}),transport=httpx.MockTransport(handle))
            session.submit('My manager pressures me to accept an estimate.',client)
            self.assertEqual(session.turns,1)
            self.assertEqual(session.records[0]['provider'],service)
