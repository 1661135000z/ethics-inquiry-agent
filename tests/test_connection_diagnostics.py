import json,unittest,httpx
from inquiry.providers import Client,settings_from,ProviderError,PROVIDERS

class DiagnosticsTests(unittest.TestCase):
    def test_new_gemini_default_and_payload(self):
        self.assertEqual(PROVIDERS['gemini']['model'],'gemini-3.5-flash-lite')
        def handle(req):
            self.assertIn('gemini-3.5-flash-lite:generateContent',str(req.url))
            body=json.loads(req.content)
            self.assertNotIn('thinkingBudget',body['generationConfig'].get('thinkingConfig',{}))
            return httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':'{}'}]}}]})
        Client('gemini',settings_from({'GEMINI_API_KEY':'test-only','GEMINI_FREE_TIER_CONFIRMED':'true'}),transport=httpx.MockTransport(handle)).complete([{'role':'user','content':'test'}])

    def test_available_models_excludes_paid_and_wrong_methods(self):
        self.assertTrue(hasattr(Client,'available_models'))
        def handle(req):
            self.assertEqual(req.method,'GET')
            self.assertNotIn('test-only',str(req.url))
            return httpx.Response(200,json={'models':[
                {'name':'models/gemini-3.5-flash-lite','supportedGenerationMethods':['generateContent']},
                {'name':'models/gemini-paid-pro','supportedGenerationMethods':['generateContent']},
                {'name':'models/gemini-2.5-flash','supportedGenerationMethods':['embedContent']} ]})
        client=Client('gemini',settings_from({'GEMINI_API_KEY':'test-only','GEMINI_FREE_TIER_CONFIRMED':'true'}),transport=httpx.MockTransport(handle))
        self.assertEqual(client.available_models(),['gemini-3.5-flash-lite'])

    def test_glm_auth_error_reports_safe_diagnostic_code_only(self):
        def handle(req):return httpx.Response(401,json={'error':{'code':'1002','message':'private key test-only and scenario'}})
        client=Client('zhipu',settings_from({'ZHIPU_API_KEY':'test-only','ZHIPU_FREE_TIER_CONFIRMED':'true'}),transport=httpx.MockTransport(handle))
        with self.assertRaises(ProviderError) as caught: client.complete([{'role':'user','content':'fictional case'}])
        self.assertIn('1002',str(caught.exception))
        self.assertIn('zhipu',str(caught.exception))
        self.assertNotIn('test-only',str(caught.exception))
        self.assertNotIn('private',str(caught.exception))
