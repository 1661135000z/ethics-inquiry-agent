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
        at.selectbox(key="example").select("dashboard").run()
        at.button(key="load_example").click().run()
        self.assertIn("year-end", at.text_area(key="draft").value)
        self.assertFalse(at.session_state["conversation"].messages)
        at.text_area(key="draft").input("My own revised situation.")
        at.button(key="submit_inquiry").click().run()
        self.assertEqual(at.text_area(key="draft").value, "My own revised situation.")

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
