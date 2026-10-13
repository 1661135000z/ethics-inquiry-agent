import json
from unittest.mock import patch
import streamlit as st
from tests.test_app import AppTests,REPLY

def palette_harness(commands,zh,on_action):
    def act(action):
        st.session_state['command_v2']={'action':action}
        on_action()
    for command in commands:
        st.button(command['title'],key='command_'+command['id'],disabled=not command['enabled'],on_click=act,args=(command['id'],))

class PolishAppTests(AppTests):
    # Run only the new tests here; base tests remain in their existing module.
    def setUp(self):
        super().setUp()
        p=patch('inquiry.components.render_palette',palette_harness);p.start();self.addCleanup(p.stop)
    def two_turns(self,at):
        self.first_turn(at,'I am an audit senior facing a deadline.')
        at.text_area(key='draft').input('I have not checked the source records.').run()
        response=json.dumps({'question':'Who could verify the source records independently?', 'focus':'evidence','observations':[{'area':'evidence','quote':'I have not checked the source records.'}]})
        with patch('inquiry.providers.Client.complete',return_value=(response,{'provider':'openrouter','model':'test/free'})):
            at.button(key='submit_inquiry').click().run()
    def test_palette_navigation_and_view_cancel_preserve_unsent_draft(self):
        at=self.app();self.first_turn(at)
        at.text_area(key='draft').input('An unsent answer.').run()
        with patch('inquiry.providers.Client.complete') as complete:
            at.button(key='command_notebook').click().run()
            self.assertEqual(at.session_state['workspace'].view,'notebook')
            self.assertEqual(at.session_state['workspace_tab'],'Inquiry notebook')
            at.button(key='command_scenario').click().run()
            self.assertEqual(at.session_state['workspace'].view,'conversation')
            at.button(key='cancel_selection').click().run()
            self.assertEqual(at.session_state['workspace'].view,'notebook')
            self.assertEqual(at.text_area(key='draft').value,'An unsent answer.')
            complete.assert_not_called()
    def test_palette_uses_only_owned_scroll_destinations_and_new_reset_view(self):
        at=self.app();self.first_turn(at)
        at.button(key='command_write').click().run()
        self.assertEqual(at.session_state['scroll_request'][0],'composer')
        at.button(key='command_model').click().run()
        self.assertEqual(at.session_state['scroll_request'][0],'model')
        at.button(key='command_notebook').click().run()
        at.button(key='main_new_inquiry').click().run()
        self.assertEqual(at.session_state['workspace'].view,'conversation')
        self.assertEqual(at.session_state['workspace'].note_filter,'all')
    def test_logical_tab_survives_language_change(self):
        at=self.app();self.first_turn(at)
        at.button(key='command_notebook').click().run()
        at.selectbox(key='language').select('中文').run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['workspace'].view,'notebook')
        self.assertEqual(at.session_state['workspace_tab'],'探究记录')
    def test_review_packet_is_gated_and_navigation_uses_no_model_request(self):
        at=self.app();self.first_turn(at)
        self.assertTrue(at.button(key='command_briefing').disabled)
        self.two_turns_fixture(at)
        with patch('inquiry.providers.Client.complete') as complete:
            at.button(key='command_briefing').click().run()
            self.assertEqual(at.session_state['workspace'].view,'briefing')
            self.assertFalse(at.exception)
            at.button(key='briefing').click().run()
            complete.assert_not_called()
        self.assertIn('download_review_packet',[d.key for d in at.get('download_button')])
    def two_turns_fixture(self,at):
        at.text_area(key='draft').input('I have not checked the source records.').run()
        with patch('inquiry.providers.Client.complete',return_value=(REPLY,{'provider':'openrouter','model':'test/free'})):
            at.button(key='submit_inquiry').click().run()

# Do not rediscover inherited base methods in this companion suite.
for _name in list(vars(AppTests)):
    if _name.startswith('test_'):
        setattr(PolishAppTests,_name,None)

# The shared base must not be collected a second time.
del AppTests
