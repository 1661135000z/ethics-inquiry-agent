"""Configured-card entry and persistent inline setup regressions."""
from unittest.mock import patch
import os
from tests.test_app import AppTests

class EntryFlowTests(AppTests):
    def test_ready_card_enters_workspace_without_a_request_or_reopening_setup(self):
        with patch.dict(os.environ,{'GEMINI_API_KEY':'fixture','GEMINI_FREE_TIER_CONFIRMED':'true'}):
            at=self.app()
            self.assertNotIn('confirm_model',[button.key for button in at.button])
            with patch('inquiry.providers.Client.complete') as complete:
                at.button(key='welcome_gemini').click().run()
                self.assertTrue(at.session_state['workspace'].onboarded)
                self.assertFalse(at.session_state['model_panel'])
                self.assertNotIn('scroll_request', at.session_state)
                at.text_area(key='draft').input('An unsent fictional concern.').run()
                self.assertFalse(at.session_state['model_panel'])
                complete.assert_not_called()
    def test_unconfigured_card_opens_inline_setup_and_confirmation_closes_it(self):
        at=self.app();at.button(key='welcome_zhipu').click().run()
        self.assertTrue(at.session_state['model_panel'])
        self.assertFalse(at.session_state['workspace'].onboarded)
        at.selectbox(key='provider').select('openrouter').run()
        self.confirm(at)
        self.assertFalse(at.session_state['model_panel'])
        self.assertTrue(at.session_state['workspace'].onboarded)
        at.button(key='open_model_settings').click().run()
        self.assertTrue(at.session_state['model_panel'])
        at.text_area(key='draft').input('Unsent context.').run()
        self.assertEqual(at.text_area(key='draft').value,'Unsent context.')
    def test_new_conversation_retains_visual_preference(self):
        at=self.app();self.first_turn(at)
        at.session_state['workspace'].theme='dark'
        at.button(key='main_new_inquiry').click().run()
        self.assertEqual(at.session_state['workspace'].theme,'dark')

for name in vars(AppTests):
    if name.startswith('test_'):setattr(EntryFlowTests,name,None)
del AppTests
