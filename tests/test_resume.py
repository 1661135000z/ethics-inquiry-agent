import unittest

from inquiry.resume import ResumeStore
from inquiry.ui_state import Workspace


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.store = ResumeStore(ttl=10, max_entries=2, clock=lambda: self.now)

    def test_expiration_and_read_refresh(self):
        token = self.store.issue(Workspace(draft='Unsent response.'))
        self.now = 9
        self.assertEqual(self.store.get(token).draft, 'Unsent response.')
        self.now = 18
        self.assertIsNotNone(self.store.get(token))
        self.now = 28
        self.assertIsNone(self.store.get(token))
        self.assertFalse(self.store.save(token, Workspace()))

    def test_tokens_and_copies_are_isolated(self):
        original = Workspace(draft='First inquiry.')
        a = self.store.issue(original)
        b = self.store.issue(Workspace(draft='Second inquiry.'))
        self.assertNotEqual(a, b)
        original.draft = 'Changed original.'
        recovered = self.store.get(a)
        recovered.draft = 'Changed recovered.'
        recovered.conversation.messages.append({'role':'user', 'content':'changed'})
        self.assertEqual(self.store.get(a).draft, 'First inquiry.')
        self.assertEqual(self.store.get(a).conversation.messages, [])
        self.assertEqual(self.store.get(b).draft, 'Second inquiry.')
        self.assertIsNone(self.store.get('unknown'))

    def test_capacity_evicts_least_recently_used(self):
        a = self.store.issue(Workspace())
        b = self.store.issue(Workspace())
        self.store.get(a)
        c = self.store.issue(Workspace())
        self.assertIsNone(self.store.get(b))
        self.assertIsNotNone(self.store.get(a))
        self.assertIsNotNone(self.store.get(c))

    def test_save_preserves_product_state_without_connection_or_credentials(self):
        token = self.store.issue(Workspace())
        w = Workspace(draft='Draft answer.', onboarded=True, phase='chat')
        w.confirmed_model = 'connection-signature'
        w.api_key = 'must-not-copy'
        w.conversation.api_key = 'must-not-copy'
        self.assertTrue(self.store.save(token, w))
        recovered = self.store.get(token)
        self.assertTrue(recovered.onboarded)
        self.assertEqual(recovered.phase, 'chat')
        self.assertEqual(recovered.draft, 'Draft answer.')
        self.assertEqual(recovered.confirmed_model, '')
        self.assertFalse(hasattr(recovered, 'api_key'))
        self.assertFalse(hasattr(recovered.conversation, 'api_key'))


    def test_older_schema_is_upgraded_without_copying_attached_key(self):
        from dataclasses import make_dataclass, field
        from inquiry.core import Session
        legacy = make_dataclass('Workspace', [('conversation',Session,field(default_factory=Session)),('draft',str,'Older draft.')])
        legacy.__module__ = Workspace.__module__
        original = legacy()
        original.api_key = 'must-not-copy'
        token = self.store.issue(original)
        recovered = self.store.get(token)
        self.assertEqual(recovered.draft,'Older draft.')
        self.assertEqual(recovered.provider_id,'')
        self.assertFalse(hasattr(recovered,'api_key'))

if __name__ == '__main__':
    unittest.main()
