import json
import unittest
from inquiry.ui_state import Workspace
from inquiry.providers import ProviderError

class GoodClient:
    def complete(self, messages):
        return json.dumps({'question':'Who can independently review this judgment?', 'focus':'review','observations':[]}), {'provider':'gemini','model':'test'}

class BadClient:
    def complete(self, messages):
        raise ProviderError('offline','network')

class WorkspaceTests(unittest.TestCase):
    def test_onboarding_requires_explicit_model_choice(self):
        w=Workspace()
        self.assertEqual(w.current_step('config-a',True),'model')
        w.confirm_model('config-a')
        self.assertTrue(w.onboarded)
        self.assertEqual(w.current_step('config-a',True),'scenario')
        w.draft='My own concern about an audit judgment.'
        self.assertEqual(w.current_step('config-a',True),'conversation')
        self.assertEqual(w.current_step('config-b',True),'model')
        self.assertEqual(w.current_step('config-a',False),'model')

    def test_success_stores_custom_initial_scenario_and_restart_retains_it(self):
        w=Workspace();w.confirm_model('a');w.draft='I face pressure over an audit estimate.'
        w.submit(w.draft,GoodClient())
        w.draft='Unsent follow-up.'
        w.new_conversation()
        self.assertFalse(w.conversation.messages)
        self.assertEqual(w.draft,'I face pressure over an audit estimate.')
        self.assertEqual(w.confirmed_model,'a')
        self.assertEqual(w.workflow,('idle',False))
        self.assertFalse(w.show_briefing)

    def test_switch_failure_keeps_old_conversation_and_cancel_restores_draft(self):
        w=Workspace();w.choose('dashboard','Old situation about audit estimates.')
        w.submit(w.draft,GoodClient());old=w.conversation
        w.draft='My unsent response.';w.enter_selection()
        w.choose('vendor','New situation about a vendor incentive.')
        with self.assertRaises(ProviderError):w.submit(w.pending_text,BadClient())
        self.assertIs(w.conversation,old)
        self.assertEqual(w.conversation.turns,1)
        self.assertEqual(w.pending_text,'New situation about a vendor incentive.')
        self.assertEqual(w.workflow,('request',True))
        w.cancel_selection()
        self.assertEqual(w.draft,'My unsent response.')
        self.assertEqual(w.case_id,'dashboard')

    def test_switch_commits_only_after_valid_reply(self):
        w=Workspace();w.choose('dashboard','Old situation.');w.submit(w.draft,GoodClient())
        w.enter_selection();w.choose('vendor','New vendor situation.')
        w.submit(w.pending_text,GoodClient())
        self.assertEqual(w.case_id,'vendor')
        self.assertEqual(w.initial_text,'New vendor situation.')
        self.assertEqual(w.conversation.turns,1)
        self.assertNotIn('Old situation.',w.conversation.export())
        self.assertEqual(w.phase,'chat')

    def test_navigation_preserves_conversation_and_unsent_text(self):
        w=Workspace();w.draft='Audit concern.';w.submit(w.draft,GoodClient())
        w.draft='Unsent answer.';w.enter_selection();w.enter_selection()
        w.cancel_selection()
        self.assertEqual(w.draft,'Unsent answer.')
        self.assertEqual(w.conversation.turns,1)

    def test_regenerate_preserves_draft_and_transactional_failure(self):
        from copy import deepcopy
        w=Workspace();w.confirm_model('a');w.submit('Audit concern.',GoodClient())
        w.draft='My unsent response.'
        old=deepcopy(w.conversation)
        with self.assertRaises(ProviderError):w.regenerate(BadClient())
        self.assertEqual(w.conversation,old)
        self.assertEqual(w.draft,'My unsent response.')
        self.assertEqual(w.workflow,('request',True))
        w.regenerate(GoodClient())
        self.assertEqual(w.draft,'My unsent response.')
        self.assertEqual(w.conversation.turns,1)
        self.assertEqual(w.workflow,('done',False))
        self.assertEqual(w.phase,'chat')

if __name__=='__main__':unittest.main()
