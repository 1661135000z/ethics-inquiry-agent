import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
import streamlit as st
from streamlit.testing.v1 import AppTest
from inquiry.providers import ProviderError

APP=Path(__file__).resolve().parents[1]/'app.py'
REPLY=json.dumps({'question':'Who can independently review this audit estimate?', 'focus':'review','observations':[]})

# AppTest does not drive JavaScript. A native test harness exercises the same callbacks;
# the actual v2 bridge and hover/touch behavior are tested in the browser separately.
def cases_harness(cases,selected,epoch,on_choose,zh=False):
    def choose(case_id):
        st.session_state['case_picker_v2']={'choose':case_id}
        on_choose()
    for case in cases:
        st.button(case['title'],key='case_'+case['id'],on_click=choose,args=(case['id'],))

def journey_harness(steps,on_navigate,key='journey_v2'):
    st.session_state['test_journey_steps']=steps
    def navigate(target):
        st.session_state['journey_v2']={'navigate':target}
        on_navigate()
    for step in steps:
        st.button(step['title'],key='navigate_'+step['id'],on_click=navigate,args=(step['id'],))

def resume_harness(token,on_restore,on_ready):
    if not st.session_state.get('resume_ready'): on_ready()

def welcome_harness(selected,ready,zh,on_choose,nonce=0):
    def choose(service):
        st.session_state['welcome_v2']={'choose':service}
        on_choose()
    for service in ['gemini','zhipu','openrouter']:
        st.button(service,key='welcome_'+service,on_click=choose,args=(service,))

class AppTests(unittest.TestCase):
    def setUp(self):
        self.patches=[patch.dict(os.environ,{'GEMINI_API_KEY':'','OPENROUTER_API_KEY':'test-only','ZHIPU_API_KEY':'','OPENROUTER_MODEL':'openrouter/free'}),
            patch('inquiry.components.render_cases',cases_harness),patch('inquiry.components.render_journey',journey_harness),patch('inquiry.components.render_scroll'),patch('inquiry.components.render_message_motion'),patch('inquiry.components.render_resume',resume_harness),patch('inquiry.components.render_welcome',welcome_harness),patch('inquiry.components.render_transition'),patch('inquiry.components.render_copy')]
        for p in self.patches:p.start();self.addCleanup(p.stop)
    def app(self):
        at=AppTest.from_file(str(APP)).run()
        self.assertFalse(at.exception)
        return at
    def confirm(self,at):
        at.button(key='confirm_model').click().run()
    def first_turn(self,at,text='I face pressure over an audit estimate.'):
        self.confirm(at)
        at.text_area(key='draft').input(text).run()
        at.checkbox(key='consent').check()
        with patch('inquiry.providers.Client.complete',return_value=(REPLY,{'provider':'openrouter','model':'test/free'})):
            at.button(key='submit_inquiry').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['conversation'].turns,1)
        self.assertTrue(at.session_state['connection_check']['signature'])

    def test_first_visit_requires_model_confirmation_and_has_no_reset_actions(self):
        at=self.app()
        self.assertEqual(len(at.text_area),0)
        self.assertNotIn('submit_inquiry',[b.key for b in at.button])
        self.assertNotIn('main_new_inquiry',[b.key for b in at.button])
        self.assertNotIn('choose_scenario',[b.key for b in at.button])
        self.assertFalse(at.session_state['workspace'].onboarded)
        self.confirm(at)
        self.assertEqual(at.session_state['test_journey_steps'][1]['state'],'active')
        at.text_area(key='draft').input('My own audit concern.').run()
        self.assertEqual(at.session_state['test_journey_steps'][2]['state'],'active')

    def test_free_model_picker_and_configuration_change_invalidate_confirmation(self):
        at=self.app();self.confirm(at)
        self.assertEqual(at.selectbox(key='free_model').value,'nvidia/nemotron-3-super-120b-a12b:free')
        at.selectbox(key='free_model').select('openrouter/free').run()
        self.assertFalse(at.exception)
        self.assertTrue(at.button(key='submit_inquiry').disabled)
        self.assertEqual(at.session_state['test_journey_steps'][0]['state'],'active')

    def test_optional_example_editable_and_own_case_does_not_submit(self):
        at=self.app();self.confirm(at)
        with patch('inquiry.providers.Client.complete') as complete:
            at.button(key='case_dashboard').click().run()
            self.assertIn('year-end',at.text_area(key='draft').value)
            at.text_area(key='draft').input('My revised case.').run()
            at.button(key='case_blank').click().run()
            complete.assert_not_called()
        self.assertEqual(at.text_area(key='draft').value,'')
        self.assertFalse(at.session_state['conversation'].messages)

    def test_submit_and_failure_preserve_work_and_open_details(self):
        at=self.app();self.first_turn(at)
        self.assertEqual(at.text_area(key='draft').value,'')
        at.text_area(key='draft').input('My manager asked me.').run()
        with patch('inquiry.providers.Client.complete',side_effect=ProviderError('Network unavailable','network')):
            at.button(key='submit_inquiry').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['conversation'].turns,1)
        self.assertEqual(at.text_area(key='draft').value,'My manager asked me.')
        self.assertEqual(at.session_state['workflow'],('request',True))
        self.assertTrue(any('Network unavailable' in e.value for e in at.error))

    def test_reselect_cancel_and_failed_switch_keep_old_chat(self):
        at=self.app();self.first_turn(at)
        at.text_area(key='draft').input('An unsent answer.').run()
        at.session_state['attempts']=5
        at.button(key='choose_scenario').click().run()
        self.assertEqual(at.session_state['conversation'].turns,1)
        at.button(key='case_vendor').click().run()
        self.assertIn('referral',at.text_area(key='draft').value)
        at.checkbox(key='consent').check()
        with patch('inquiry.providers.Client.complete',side_effect=ProviderError('Offline','network')):
            at.button(key='submit_inquiry').click().run()
        self.assertEqual(at.session_state['conversation'].turns,1)
        self.assertIn('referral',at.text_area(key='draft').value)
        at.button(key='cancel_selection').click().run()
        self.assertEqual(at.text_area(key='draft').value,'An unsent answer.')
        self.assertEqual(at.session_state['attempts'],5)
        self.assertFalse(at.checkbox(key='consent').value)

    def test_new_conversation_keeps_custom_initial_scenario_and_model(self):
        at=self.app();self.first_turn(at)
        confirmation=at.session_state['workspace'].confirmed_model
        at.button(key='main_new_inquiry').click().run()
        self.assertFalse(at.exception)
        self.assertFalse(at.session_state['conversation'].messages)
        self.assertEqual(at.text_area(key='draft').value,'I face pressure over an audit estimate.')
        self.assertEqual(at.session_state['workspace'].confirmed_model,confirmation)
        self.assertFalse(at.checkbox(key='consent').value)
        self.assertNotIn('main_new_inquiry',[b.key for b in at.button])

    def test_step_navigation_preserves_chat_and_unsent_answer(self):
        at=self.app();self.first_turn(at)
        at.text_area(key='draft').input('Still editing my answer.').run()
        at.button(key='navigate_scenario').click().run()
        self.assertEqual(at.session_state['workspace'].phase,'select')
        self.assertEqual(at.session_state['conversation'].turns,1)
        at.button(key='cancel_selection').click().run()
        self.assertEqual(at.text_area(key='draft').value,'Still editing my answer.')

    def test_model_preference_survives_service_switch(self):
        with patch.dict(os.environ,{'GEMINI_API_KEY':'owner-only','GEMINI_FREE_TIER_CONFIRMED':'true','OPENROUTER_API_KEY':''}):
            at=self.app()
            at.selectbox(key='model_gemini_current').select('gemini-3.1-flash-lite').run()
            at.selectbox(key='provider').select('zhipu').run()
            at.selectbox(key='provider').select('gemini').run()
            self.assertEqual(at.selectbox(key='model_gemini_current').value,'gemini-3.1-flash-lite')

    def test_visitor_priority_connection_probe_and_service_switch_preserve_key(self):
        with patch.dict(os.environ,{'GEMINI_API_KEY':'owner-only','GEMINI_FREE_TIER_CONFIRMED':'true','OPENROUTER_API_KEY':''}):
            at=self.app()
            at.text_input(key='api_key_gemini').input('visitor-only').run()
            at.checkbox(key='free_confirm_gemini').check().run()
            captured=[]
            def complete(client,messages):
                captured.append((client.settings['GEMINI_API_KEY'],messages))
                return REPLY,{'provider':'gemini','model':'gemini-3.5-flash-lite'}
            with patch('inquiry.providers.Client.complete',complete),patch('inquiry.providers.Client.available_models',return_value=['gemini-3.5-flash-lite']):
                at.button(key='test_connection').click().run()
            self.assertFalse(at.exception)
            self.assertEqual(captured[0][0],'visitor-only')
            self.assertIn('OBJECTIVITY',captured[0][1][0]['content'])
            self.assertFalse(at.session_state['conversation'].messages)
            self.assertFalse(at.button(key='submit_inquiry').disabled)
            at.text_input(key='api_key_gemini').input('new-key').run()
            self.assertTrue(at.button(key='submit_inquiry').disabled)
            at.selectbox(key='provider').select('zhipu').run()
            at.selectbox(key='provider').select('gemini').run()
            self.assertEqual(at.text_input(key='api_key_gemini').value,'new-key')
            at.button(key='clear_api_keys').click().run()
            self.assertEqual(at.text_input(key='api_key_gemini').value,'')
            self.assertNotIn('visitor-only',''.join(e.value for e in at.success))

    def test_welcome_card_selects_service_without_api_request(self):
        at=self.app()
        with patch('inquiry.providers.Client.complete') as complete:
            at.button(key='welcome_zhipu').click().run()
            complete.assert_not_called()
        self.assertFalse(at.exception)
        self.assertEqual(at.selectbox(key='provider').value,'zhipu')
        self.assertFalse(at.session_state['workspace'].onboarded)
        self.assertNotIn('draft',[a.key for a in at.text_area])

    def test_regeneration_retains_latest_answer_turn_count_and_unsent_draft(self):
        at=self.app();self.first_turn(at)
        at.text_area(key='draft').input('Still drafting.').run()
        replacement=json.dumps({'question':'Which independent records could verify that estimate?', 'focus':'evidence','observations':[]})
        with patch('inquiry.providers.Client.complete',return_value=(replacement,{'provider':'openrouter','model':'test/free'})):
            at.button(key='regenerate').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state['conversation'].turns,1)
        self.assertEqual(at.text_area(key='draft').value,'Still drafting.')
        self.assertIn('independent records',at.session_state['conversation'].messages[-1]['content'])
        self.assertEqual(at.session_state['conversation'].records[-1]['regenerations'],1)

    def test_onboarding_transition_is_not_reissued_on_ordinary_interaction(self):
        at=self.app();self.confirm(at)
        nonce=at.session_state['transition_nonce']
        at.text_area(key='draft').input('An audit concern.').run()
        self.assertEqual(at.session_state['transition_nonce'],nonce)
        self.assertNotIn('welcome_gemini',[b.key for b in at.button])

    def test_regenerate_obeys_revoked_consent(self):
        at=self.app();self.first_turn(at)
        at.checkbox(key='consent').uncheck().run()
        with patch('inquiry.providers.Client.complete') as complete:
            at.button(key='regenerate').click().run()
            complete.assert_not_called()
        self.assertEqual(at.session_state['conversation'].turns,1)
        self.assertTrue(any('Confirm data sharing' in e.value for e in at.warning))

    def test_enabling_new_fallback_requires_new_consent(self):
        with patch.dict(os.environ,{'ZHIPU_API_KEY':'owner-only','ZHIPU_FREE_TIER_CONFIRMED':'true'}):
            at=self.app();self.first_turn(at)
            at.checkbox(key='allow_fallback').check().run()
            self.assertFalse(at.checkbox(key='consent').value)

    def test_refresh_recovers_chat_draft_preferences_without_welcome_or_consent(self):
        at=self.app();self.first_turn(at)
        at.text_area(key='draft').input('An unsent response.').run()
        token=at.session_state['resume_token']
        def restore_harness(_token,on_restore,on_ready):
            if not st.session_state.get('resume_ready'):
                st.session_state['resume_v2']={'restore':token}
                on_restore()
        with patch('inquiry.components.render_resume',restore_harness):
            fresh=self.app()
        self.assertEqual(fresh.session_state['conversation'].turns,1)
        self.assertEqual(fresh.text_area(key='draft').value,'An unsent response.')
        self.assertEqual(fresh.selectbox(key='provider').value,'openrouter')
        self.assertFalse(fresh.checkbox(key='consent').value)
        self.assertFalse(fresh.session_state['workspace'].confirmed_model)
        self.assertNotIn('welcome_gemini',[b.key for b in fresh.button])

    def test_regenerated_unreported_assertion_keeps_prior_question_and_draft(self):
        at=self.app();self.first_turn(at,'I do not know who reviewed these audit entries.')
        prior=at.session_state['conversation'].messages[-1]['content']
        at.text_area(key='draft').input('Still drafting.').run()
        bad=json.dumps({'question':'Since nobody reviewed these entries, who could review them independently?', 'focus':'review','observations':[]})
        with patch('inquiry.providers.Client.complete',return_value=(bad,{'provider':'openrouter','model':'test/free'})):
            at.button(key='regenerate').click().run()
        self.assertEqual(at.session_state['conversation'].messages[-1]['content'],prior)
        self.assertEqual(at.text_area(key='draft').value,'Still drafting.')
        self.assertEqual(at.session_state['workflow'],('validate',True))
        self.assertTrue(any('unreported fact' in e.value for e in at.error))

if __name__=='__main__':unittest.main()
