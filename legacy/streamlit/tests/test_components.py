"""Component data and one-shot callback contracts independent of a browser."""
import unittest
from unittest.mock import Mock, patch

from inquiry.components import render_cases, render_journey, render_scroll, render_message_motion, render_welcome, render_transition, render_resume, render_copy, _ASSETS


class ComponentContracts(unittest.TestCase):
    def test_selection_payload_preserves_literal_text_and_registers_one_callback(self):
        renderer=Mock(return_value=object())
        callback=Mock()
        case={"id":"audit", "title":"<script>not html</script>", "text":"A & B", "source":"Teaching case"}
        with patch("inquiry.components._component", return_value=renderer):
            result=render_cases([case], "audit", 3, callback)
        self.assertIs(result, renderer.return_value)
        kwargs=renderer.call_args.kwargs
        self.assertEqual(kwargs["key"], "case_picker_v2")
        self.assertEqual(kwargs["data"]["cases"][0]["title"], case["title"])
        self.assertEqual(kwargs["data"]["epoch"], 3)
        self.assertIs(kwargs["on_choose_change"], callback)
        callback.assert_not_called()

    def test_journey_current_and_navigation_callback(self):
        renderer=Mock()
        callback=Mock()
        steps=[{"id":"model","title":"Model","detail":"Ready","state":"complete"},
               {"id":"scenario","title":"Scenario","detail":"Pick","state":"current"}]
        with patch("inquiry.components._component", return_value=renderer):
            render_journey(steps, callback)
        kwargs=renderer.call_args.kwargs
        self.assertEqual(kwargs["data"]["current"], "scenario")
        self.assertEqual(kwargs["key"], "journey_v2")
        self.assertIs(kwargs["on_navigate_change"], callback)

    def test_scroll_accepts_only_owned_targets_and_has_no_callback(self):
        renderer=Mock()
        with patch("inquiry.components._component", return_value=renderer):
            render_scroll("conversation", 9)
            with self.assertRaises(ValueError): render_scroll("input[name=api_key]", 10)
        self.assertEqual(renderer.call_count, 1)
        self.assertEqual(renderer.call_args.kwargs, {
            "data":{"target":"conversation","nonce":9}, "key":"scroll_bridge_v2", "height":0})

    def test_app_active_alias_and_motion_have_minimal_payloads(self):
        renderer=Mock()
        with patch("inquiry.components._component", return_value=renderer):
            render_journey([{"id":"model", "state":"active"}], Mock())
            self.assertEqual(renderer.call_args.kwargs["data"]["current"], "model")
            render_message_motion(2, 4)
        self.assertEqual(renderer.call_args.kwargs, {
            "data":{"epoch":2,"count":4}, "key":"message_motion_v2", "height":0})

    def test_welcome_filters_readiness_to_known_boolean_flags(self):
        renderer = Mock()
        callback = Mock()
        with patch("inquiry.components._component", return_value=renderer):
            render_welcome("zhipu", {"zhipu": True, "gemini": "secret", "api_key": "secret"}, True, callback, 7)
        kwargs = renderer.call_args.kwargs
        self.assertEqual(kwargs["data"], {"selected": "zhipu", "ready": {"gemini": False, "zhipu": True, "openrouter": False}, "zh": True, "nonce": 7})
        self.assertEqual(kwargs["key"], "welcome_v2")
        self.assertIs(kwargs["on_choose_change"], callback)
        callback.assert_not_called()
        with patch("inquiry.components._component", return_value=renderer):
            render_welcome("gemini", True, False, callback)
            self.assertEqual(renderer.call_args.kwargs["data"]["ready"], {"gemini": True, "zhipu": False, "openrouter": False})
            with self.assertRaises(ValueError):
                render_welcome("unknown", False, False, callback)

    def test_transition_has_no_callback_and_rejects_arbitrary_selector(self):
        renderer = Mock()
        with patch("inquiry.components._component", return_value=renderer):
            render_transition("scenario", 8, "<script>literal</script>")
            with self.assertRaises(ValueError):
                render_transition("input", 9, "bad")
        self.assertEqual(renderer.call_count, 1)
        self.assertEqual(renderer.call_args.kwargs, {"data": {"kind": "scenario", "nonce": 8, "title": "<script>literal</script>"}, "key": "transition_v2", "height": 0})

    def test_resume_and_copy_contracts(self):
        renderer = Mock()
        restore, ready = Mock(), Mock()
        with patch("inquiry.components._component", return_value=renderer):
            render_resume("opaque-token", restore, ready)
            self.assertEqual(renderer.call_args.kwargs, {"data": {"token": "opaque-token"}, "key": "resume_v2", "height": 0, "on_restore_change": restore, "on_ready_change": ready})
            render_copy("<b>Literal question?</b>", "copy-question")
            self.assertEqual(renderer.call_args.kwargs, {"data": {"text": "<b>Literal question?</b>", "zh": False}, "key": "copy-question"})
        restore.assert_not_called()
        ready.assert_not_called()

    def test_new_browser_assets_are_local_and_use_only_explicit_actions(self):
        welcome = (_ASSETS / "welcome.js").read_text()
        transition = (_ASSETS / "transition_bridge.js").read_text() + (_ASSETS / "motion_runtime.js").read_text()
        copy = (_ASSETS / "copy_reply.js").read_text()
        self.assertNotIn("innerHTML", welcome + transition + copy)
        self.assertEqual(welcome.count("setTriggerValue('choose'"), 1)
        self.assertNotIn("setTriggerValue", transition + copy)
        self.assertNotIn("fetch(", welcome + transition + copy)
        self.assertIn("state.seen.has(nonce)", transition)
        self.assertIn("prefers-reduced-motion", welcome + transition)
        self.assertIn("skip.onclick=()=>finish('skip')", transition)
        self.assertIn("duration:720", transition)
        self.assertNotIn("querySelector('input", transition)

    def test_assets_do_not_send_preview_events_or_render_data_as_html(self):
        picker=(_ASSETS / "case_picker.js").read_text()
        journey=(_ASSETS / "journey.js").read_text()
        self.assertNotIn("innerHTML", picker+journey)
        self.assertNotIn("setStateValue", picker)
        self.assertEqual(picker.count("setTriggerValue('choose'"), 1)
        self.assertEqual(journey.count("setTriggerValue('navigate'"), 1)


if __name__=="__main__": unittest.main()
