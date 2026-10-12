import os
from pathlib import Path
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


class AppTests(unittest.TestCase):
    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-only", "GEMINI_API_KEY": "", "ZHIPU_API_KEY": "", "OPENROUTER_MODEL":"openrouter/free"})
    def test_free_model_picker_defaults_to_fixed_model(self):
        at = AppTest.from_file(str(APP)).run()
        self.assertEqual(at.selectbox(key="free_model").value, "nvidia/nemotron-3-super-120b-a12b:free")
        at.selectbox(key="free_model").select("openrouter/free").run()
        self.assertFalse(at.exception)
        self.assertEqual(at.selectbox(key="free_model").value, "openrouter/free")

    def test_clean_start_has_no_prefilled_case_or_api_calls(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY":"", "OPENROUTER_API_KEY":"", "ZHIPU_API_KEY":""}):
            at = AppTest.from_file(str(APP)).run()
            self.assertFalse(at.exception)
            self.assertEqual(at.text_area(key="draft").value, "")
            self.assertEqual(at.session_state["conversation"].messages, [])
            self.assertTrue(at.button(key="submit_inquiry").disabled)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-only", "GEMINI_API_KEY": "", "ZHIPU_API_KEY": ""})
    def test_optional_example_is_editable_and_not_submitted(self):
        at = AppTest.from_file(str(APP)).run()
        at.button(key="case_dashboard").click().run()
        self.assertIn("year-end", at.text_area(key="draft").value)
        self.assertFalse(at.session_state["conversation"].messages)
        at.text_area(key="draft").input("My own revised situation.")
        at.button(key="submit_inquiry").click().run()
        self.assertEqual(at.text_area(key="draft").value, "My own revised situation.")

    def test_return_to_own_scenario_clears_example_without_submitting(self):
        at=AppTest.from_file(str(APP)).run()
        at.button(key="case_dashboard").click().run()
        self.assertTrue(at.text_area(key="draft").value)
        at.button(key="case_blank").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.text_area(key="draft").value, "")
        self.assertEqual(at.session_state["example"], "blank")
        self.assertEqual(at.session_state["conversation"].messages, [])

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-only", "GEMINI_API_KEY": "", "ZHIPU_API_KEY": ""})
    def test_submit_and_transport_failure_preserve_user_work(self):
        import json
        from inquiry.providers import ProviderError
        at = AppTest.from_file(str(APP)).run()
        at.text_area(key="draft").input("I face pressure to accept an unsupported estimate.")
        at.checkbox(key="consent").check()
        reply = json.dumps({"question":"Who is asking you to accept the estimate?", "focus":"pressure", "observations":[]})
        with patch("inquiry.providers.Client.complete", return_value=(reply, {"provider":"openrouter", "model":"test/free"})):
            at.button(key="submit_inquiry").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["conversation"].turns, 1)
        self.assertEqual(at.text_area(key="draft").value, "")
        at.text_area(key="draft").input("My manager asked me.")
        with patch("inquiry.providers.Client.complete", side_effect=ProviderError("Network unavailable", "network")):
            at.button(key="submit_inquiry").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["conversation"].turns, 1)
        self.assertEqual(at.text_area(key="draft").value, "My manager asked me.")
        self.assertEqual(at.session_state["workflow"], ("request", True))

    @patch.dict(os.environ, {"GEMINI_API_KEY":"owner-only", "GEMINI_FREE_TIER_CONFIRMED":"true", "OPENROUTER_API_KEY":"", "ZHIPU_API_KEY":""})
    def test_connection_uses_visitor_key_without_changing_conversation(self):
        import json
        at=AppTest.from_file(str(APP)).run()
        self.assertIn("api_key_gemini", [w.key for w in at.text_input])
        at.text_input(key="api_key_gemini").input("visitor-only").run()
        at.checkbox(key="free_confirm_gemini").check().run()
        captured=[]
        def complete(client, messages):
            captured.append((client.settings['GEMINI_API_KEY'],messages))
            return json.dumps({'question':'Who can independently review the disputed estimate?', 'focus':'review','observations':[]}), {'provider':'gemini','model':'gemini-2.5-flash-lite'}
        with patch("inquiry.providers.Client.complete",complete), patch("inquiry.providers.Client.available_models", return_value=["gemini-3.5-flash-lite"]):
            at.button(key="test_connection").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(captured[0][0],'visitor-only')
        self.assertIn('OBJECTIVITY',captured[0][1][0]['content'])
        self.assertFalse(at.session_state['conversation'].messages)
        self.assertNotIn('visitor-only', ''.join(x.value for x in at.success))
        at.text_input(key="api_key_gemini").input("new-key").run()
        self.assertFalse(any('Connection verified' in x.value for x in at.success))
        at.selectbox(key="provider").select("zhipu").run()
        at.selectbox(key="provider").select("gemini").run()
        self.assertEqual(at.text_input(key="api_key_gemini").value, "new-key")
        at.button(key="clear_api_keys").click().run()
        self.assertEqual(at.text_input(key="api_key_gemini").value,'')

    @patch.dict(os.environ, {"OPENROUTER_API_KEY":"test-only", "GEMINI_API_KEY":"", "ZHIPU_API_KEY":""})
    def test_main_navigation_can_restart_after_conversation(self):
        import json
        at=AppTest.from_file(str(APP)).run()
        at.button(key="case_dashboard").click().run()
        at.checkbox(key="consent").check()
        reply=json.dumps({"question":"Who can review the missing entries?", "focus":"review", "observations":[]})
        with patch("inquiry.providers.Client.complete", return_value=(reply,{"provider":"openrouter","model":"test/free"})):
            at.button(key="submit_inquiry").click().run()
        self.assertEqual(at.session_state["conversation"].turns,1)
        at.session_state["attempts"]=5
        at.button(key="choose_scenario").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["conversation"].messages,[])
        self.assertEqual(at.session_state["conversation"].records,[])
        self.assertEqual(at.session_state["workflow"],("idle",False))
        self.assertFalse(at.checkbox(key="consent").value)
        self.assertEqual(at.session_state["attempts"],5)
        at.button(key="case_vendor").click().run()
        self.assertIn("referral",at.text_area(key="draft").value)
        at.button(key="main_new_inquiry").click().run()
        self.assertEqual(at.text_area(key="draft").value,"")
        self.assertEqual(at.session_state["example"],"blank")

    def test_chinese_ui_and_reset_keep_request_counter(self):
        at = AppTest.from_file(str(APP)).run()
        at.selectbox(key="language").select("中文").run()
        at.session_state["attempts"] = 7
        at.text_area(key="draft").input("测试情境").run()
        at.button(key="new_inquiry").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.text_area(key="draft").value, "")
        self.assertEqual(at.session_state["attempts"], 7)


if __name__ == "__main__": unittest.main()
