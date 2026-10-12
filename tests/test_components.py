"""Component data and one-shot callback contracts independent of a browser."""
import unittest
from unittest.mock import Mock, patch

from inquiry.components import render_cases, render_journey, render_scroll, render_message_motion, _ASSETS


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

    def test_assets_do_not_send_preview_events_or_render_data_as_html(self):
        picker=(_ASSETS / "case_picker.js").read_text()
        journey=(_ASSETS / "journey.js").read_text()
        self.assertNotIn("innerHTML", picker+journey)
        self.assertNotIn("setStateValue", picker)
        self.assertEqual(picker.count("setTriggerValue('choose'"), 1)
        self.assertEqual(journey.count("setTriggerValue('navigate'"), 1)


if __name__=="__main__": unittest.main()
