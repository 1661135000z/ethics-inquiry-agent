from copy import deepcopy
import json
import unittest

from inquiry.core import Session, InputError, ModelOutputError
from inquiry.providers import ProviderError


class Client:
    def __init__(self, question='Who can review the underlying evidence?', observations=None):
        self.question = question
        self.observations = observations or []
        self.calls = 0

    def complete(self, messages):
        self.calls += 1
        self.messages = messages
        return json.dumps({'question': self.question, 'focus': 'review',
                           'observations': self.observations}), {
            'provider': 'test', 'model': 'replacement', 'tokens': 42,
            'fallback_from': 'primary'}


class RegenerationTests(unittest.TestCase):
    def test_replaces_question_without_new_turn_and_keeps_prior_context(self):
        s = Session()
        s.submit('I am a junior auditor.', Client('What evidence supports this estimate?'))
        s.submit('The manager refuses additional testing.', Client('Who prepared this estimate?'))
        first_record = deepcopy(s.records[0])
        client = Client()
        stages = []
        s.regenerate(client, progress=stages.append)
        self.assertEqual(client.calls, 1)
        self.assertEqual(client.messages[1:], s.messages[:-1])
        self.assertNotIn('Who prepared this estimate?', str(client.messages))
        self.assertIn('What evidence supports this estimate?', str(client.messages))
        self.assertEqual(s.turns, 2)
        self.assertEqual(len(s.messages), 4)
        self.assertEqual(len(s.records), 2)
        self.assertEqual(s.records[0], first_record)
        self.assertEqual(s.records[-1]['regenerations'], 1)
        self.assertEqual(s.records[-1]['tokens'], 42)
        self.assertEqual(stages, ['input', 'request', 'validate', 'save', 'done'])
        s.regenerate(Client())
        self.assertEqual(s.records[-1]['regenerations'], 2)

    def test_transport_and_validation_failure_are_transactional(self):
        class Offline:
            def complete(self, messages):
                raise ProviderError('offline', 'network')
        for client, error in [(Offline(), ProviderError), (Client('Approved.'), ModelOutputError)]:
            s = Session()
            s.submit('The manager refuses additional testing.', Client())
            original = deepcopy(s)
            with self.assertRaises(error):
                s.regenerate(client)
            self.assertEqual(s, original)

    def test_only_valid_user_quotes_are_merged(self):
        text = 'The manager refuses additional testing.'
        s = Session()
        s.submit(text, Client(observations=[{'area':'pressure', 'quote':text}]))
        s.regenerate(Client(observations=[{'area':'review', 'quote':'Who can review the underlying evidence?'}]))
        self.assertEqual(s.observations, [{'area':'pressure', 'quote':text}])

    def test_rejects_missing_question_before_request(self):
        c = Client()
        for s in [Session(), Session(messages=[{'role':'user', 'content':'Audit concern.'}])]:
            with self.assertRaises(InputError):
                s.regenerate(c)
        self.assertEqual(c.calls, 0)

    def test_regeneration_allowed_after_turn_limit(self):
        s = Session(messages=[{'role':'user', 'content':'Audit concern.'},
                              {'role':'assistant', 'content':'Who can verify this concern?'}] * 12)
        s.regenerate(Client())
        self.assertEqual(s.turns, 12)


if __name__ == '__main__':
    unittest.main()
