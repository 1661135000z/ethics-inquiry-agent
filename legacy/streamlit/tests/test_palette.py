"""Command-palette payload, validation, keyboard and lifecycle contracts."""
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import Mock, patch

from inquiry.components import _ASSETS, render_palette


class PaletteContracts(unittest.TestCase):
    def test_only_public_whitelisted_fields_leave_python(self):
        renderer, callback = Mock(), Mock()
        commands = [
            {"id": "model", "title": "<script>literal</script>", "hint": "Configure", "enabled": True,
             "api_key": "private", "conversation": "private transcript"},
            {"id": "write", "title": "Write", "hint": "Start", "enabled": "secret"},
            {"id": "reset", "title": "Reset", "enabled": True},
            {"id": ["model"], "title": "Invalid", "enabled": True},
            {"id": "model", "title": "Duplicate", "enabled": True},
        ]
        with patch("inquiry.components._component", return_value=renderer) as factory:
            result = render_palette(commands, True, callback)
        factory.assert_called_once_with("command_palette")
        self.assertIs(result, renderer.return_value)
        args = renderer.call_args.kwargs
        self.assertEqual(args["key"], "command_v2")
        self.assertEqual(args["data"], {"zh": True, "commands": [
            {"id": "model", "title": "<script>literal</script>", "hint": "Configure", "enabled": True},
            {"id": "write", "title": "Write", "hint": "Start", "enabled": False},
        ]})
        callback.assert_not_called()
        self.assertEqual(set(args), {"key", "data", "on_action_change"})

    def test_callback_revalidates_action_id_and_enabled_status(self):
        renderer, callback = Mock(), Mock()
        with patch("inquiry.components._component", return_value=renderer):
            render_palette([{"id": "write", "enabled": True}, {"id": "briefing", "enabled": False}], False, callback)
        dispatch = renderer.call_args.kwargs["on_action_change"]
        for action in (None, "reset", "briefing", "model", ["write"], {"id": "write"}):
            with patch("inquiry.components.st.session_state", {"command_v2": {"action": action}}):
                dispatch()
        callback.assert_not_called()
        with patch("inquiry.components.st.session_state", {"command_v2": {"action": "write"}}):
            dispatch()
        callback.assert_called_once_with()

    def test_missing_state_and_empty_commands_do_not_dispatch(self):
        renderer, callback = Mock(), Mock()
        with patch("inquiry.components._component", return_value=renderer):
            render_palette([], False, callback)
        dispatch = renderer.call_args.kwargs["on_action_change"]
        for state in ({}, {"command_v2": None}, {"command_v2": {"action": "write"}}):
            with patch("inquiry.components.st.session_state", state):
                dispatch()
        callback.assert_not_called()

    def test_registration_uses_style_isolation_and_local_assets(self):
        renderer = Mock()
        with patch("inquiry.components.st.components.v2.component", return_value=renderer) as factory:
            render_palette([], False, Mock())
        args = factory.call_args.kwargs
        self.assertTrue(args["isolate_styles"])
        self.assertEqual(args["html"], '<div class="command-palette"></div>')
        self.assertEqual(args["js"], (_ASSETS / "command_palette.js").read_text())
        self.assertEqual(args["css"], (_ASSETS / "command_palette.css").read_text())

    def test_assets_have_no_external_actions_and_one_trigger_site(self):
        js = (_ASSETS / "command_palette.js").read_text()
        css = (_ASSETS / "command_palette.css").read_text()
        for forbidden in ("innerHTML", "fetch(", "XMLHttpRequest", "clipboard", "globalThis", "setStateValue", "document.querySelector"):
            self.assertNotIn(forbidden, js)
        self.assertEqual(js.count("setTriggerValue('action'"), 1)
        self.assertIn("return () => ui.dispose()", js)
        self.assertIn("removeEventListener('keydown', keyboard)", js)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("max-width:560px", css)
        self.assertIn("max-height:min(432px,calc(100dvh - 210px))", css)
        self.assertIn("createElementNS", js)
        self.assertIn("glyph.setAttribute('aria-hidden', 'true')", js)
        self.assertNotIn("https:", css)

    def test_browser_logic_filters_navigates_and_cleans_up_without_reruns(self):
        node = shutil.which("node")
        bundled = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
        if not node and bundled.is_file():
            node = str(bundled)
        if not node:
            self.skipTest("Node.js is required for the local DOM interaction contract")
        # A minimal DOM host lets us execute the actual asset, not a duplicate
        # implementation. Foreign input values throw if accidentally inspected.
        script = r"""
import assert from 'node:assert/strict';
import fs from 'node:fs';
class Element {
  constructor(tag) { this.tagName = tag.toUpperCase(); this.children = []; this.attrs = {}; this.isConnected = true; this.value = ''; this.classList = {add: name => { this.className = name; }}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(key, value) { this.attrs[key] = value; }
  removeAttribute(key) { delete this.attrs[key]; }
  focus() { document.activeElement = this; }
  scrollIntoView() {}
  showModal() { this.open = true; }
  close() { this.open = false; this.onclose?.(); }
  getBoundingClientRect() { return {left: 10, top: 10, right: 500, bottom: 500}; }
}
const listeners = new Set();
global.document = {
  activeElement: new Element('button'),
  createElement: tag => new Element(tag),
  createElementNS: (namespace, tag) => { assert.equal(namespace, 'http://www.w3.org/2000/svg'); return new Element(tag); },
  addEventListener: (name, fn) => { assert.equal(name, 'keydown'); listeners.add(fn); },
  removeEventListener: (name, fn) => { assert.equal(name, 'keydown'); listeners.delete(fn); },
};
const source = fs.readFileSync(process.env.PALETTE_ASSET, 'utf8');
const render = (await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'))).default;
const actions = [];
const commands = [
  {id: 'model', title: 'Model', hint: 'Provider', enabled: true},
  {id: 'scenario', title: 'Scenario', hint: 'Choose', enabled: false},
  {id: 'notebook', title: 'Notebook', hint: 'Evidence', enabled: true},
  {id: 'write', title: 'Write', hint: 'Question', enabled: true},
];
const host = root => ({querySelector: selector => { assert.equal(selector, '.command-palette'); return root; }});
const key = (value, options = {}, focus = document.activeElement) => {
  const event = {key: value, composedPath: () => [focus], preventDefault() { this.defaultPrevented = true; }, ...options};
  [...listeners].forEach(fn => fn(event));
  return event;
};
let root = new Element('div');
let cleanup = render({parentElement: host(root), data: {commands}, setTriggerValue: (event, id) => { assert.equal(event, 'action'); actions.push(id); }});
assert.equal(listeners.size, 1);
const prior = document.activeElement;
key('k', {ctrlKey: true});
assert.equal(root._palette.open, true);
assert.equal(document.activeElement, root._palette.search);
key('ArrowDown');
assert.equal(root._palette.active, 'notebook'); // Disabled scenario is skipped.
assert.deepEqual(actions, []);
root._palette.search.value = 'evidence';
root._palette.search.oninput();
assert.equal(root._palette.rows.length, 1);
root._palette.rows[0].button.onpointerenter();
assert.deepEqual(actions, []);
key('Enter');
key('Enter', {repeat: true});
assert.deepEqual(actions, ['notebook']);
assert.equal(document.activeElement, prior);
key('/', {}, prior);
assert.deepEqual(actions, ['notebook', 'write']);
const foreign = new Element('input');
Object.defineProperty(foreign, 'value', {get() { throw Error('Foreign value was read'); }});
key('/', {}, foreign);
assert.equal(actions.length, 2);
key('k', {metaKey: true}, foreign); // Normal typing focus still allows Cmd K.
assert.equal(root._palette.open, true);
key('Escape');
assert.equal(document.activeElement, foreign);
foreign.type = 'password';
key('k', {ctrlKey: true}, foreign);
assert.equal(root._palette.open, false);
key('k', {ctrlKey: true, isComposing: true}, prior);
key('k', {ctrlKey: true, keyCode: 229}, prior);
key('/', {isComposing: true}, prior);
assert.equal(root._palette.open, false);
assert.equal(actions.length, 2);
const editable = new Element('div'); editable.isContentEditable = true;
key('/', {}, editable);
assert.equal(actions.length, 2);
// Data changes must update the existing listener, including write readiness.
cleanup = render({parentElement: host(root), data: {commands: commands.map(command => ({...command, enabled: false})), zh: true}, setTriggerValue: () => { throw Error('Stale enabled action'); }});
assert.equal(listeners.size, 1);
key('/', {}, prior);
key('k', {ctrlKey: true}, prior);
key('Enter');
assert.equal(root._palette.open, true);
root._palette.search.value = 'no-match'; root._palette.search.oninput();
assert.equal(root._palette.rows.length, 0);
assert.equal(root._palette.empty.hidden, false);
key('ArrowUp'); key('Enter'); key('Escape');
assert.equal(root._palette.label.textContent, '快捷导航');
// A remount disposes the previous instance before adding its own listener.
const oldCleanup = cleanup;
const oldRoot = root;
root = new Element('div');
cleanup = render({parentElement: host(root), data: {commands}, setTriggerValue: (event, id) => actions.push(id)});
assert.equal(oldRoot._palette.disposed, true);
assert.equal(listeners.size, 1);
oldCleanup();
assert.equal(listeners.size, 1);
root._palette.launcher.onclick();
root._palette.rows[0].button.onclick();
root._palette.rows[0].button.onclick();
assert.deepEqual(actions, ['notebook', 'write', 'model']);
cleanup(); cleanup();
assert.equal(listeners.size, 0);
key('/', {}, prior);
assert.equal(actions.length, 3);
"""
        result = subprocess.run([node, "--input-type=module", "-e", script],
                                env={**os.environ, "PALETTE_ASSET": str(_ASSETS / "command_palette.js")},
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
