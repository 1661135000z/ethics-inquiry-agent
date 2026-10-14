import unittest
from edge.transport import parse_response, request_payload
from edge.policy import APIError

class TransportTests(unittest.TestCase):
    def test_gemini_400_reasons_are_classified_without_echoing_body(self):
        cases=[
            ('User location is not supported for the API use.','FAILED_PRECONDITION','region'),
            ('Gemini API free tier is not available in your country. Please enable billing.','FAILED_PRECONDITION','free_tier_region'),
            ('API key not valid. Please pass a valid API key.','INVALID_ARGUMENT','auth'),
            ('Unknown name generationConfig.','INVALID_ARGUMENT','parameters'),
        ]
        for message,status,code in cases:
            with self.subTest(code=code), self.assertRaises(APIError) as caught:
                parse_response('gemini','gemini-3.5-flash-lite',400,{'error':{'message':message+' private-key-must-not-appear','status':status}})
            self.assertEqual(caught.exception.code,code)
            self.assertNotIn('private-key-must-not-appear',str(caught.exception))
    def test_unknown_error_does_not_echo_provider_content(self):
        with self.assertRaises(APIError) as caught:
            parse_response('gemini','gemini-3.5-flash-lite',400,{'error':{'message':'private-key-must-not-appear'}})
        self.assertNotIn('private-key-must-not-appear',str(caught.exception))
    def test_gemini_uses_header_key_and_supported_thinking_configuration(self):
        for model in ['gemini-3.5-flash-lite','gemini-2.5-flash']:
            url,headers,payload=request_payload('gemini',model,'private-test-key',[{'role':'system','content':'Ask one question.'},{'role':'user','content':'A fictional concern.'}])
            self.assertNotIn('private-test-key',url)
            self.assertEqual(headers['x-goog-api-key'],'private-test-key')
            self.assertEqual('thinkingConfig' in payload['generationConfig'],model.startswith('gemini-2.5-'))
