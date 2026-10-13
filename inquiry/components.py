"""Small local Streamlit v2 components with one-shot action callbacks.

Callbacks take no arguments (the Streamlit contract). Read the event from
``st.session_state[key].get('choose')`` or ``.get('navigate')`` inside the callback. Do not
also consume the returned trigger in the render pass.
"""
from pathlib import Path
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import streamlit as st

_ASSETS = Path(__file__).resolve().parent.parent / "frontend"


def _component(name: str):
    return st.components.v2.component(
        name,
        html=f'<div class="{name.replace("_", "-")}"></div>',
        css=(_ASSETS / f"{name}.css").read_text(encoding="utf-8"),
        js=(_ASSETS / f"{name}.js").read_text(encoding="utf-8"),
        isolate_styles=True,
    )


def render_cases(
    cases: Sequence[Mapping[str, Any]], selected: str | None, epoch: int,
    on_choose: Callable[[], None], zh: bool = False,
):
    """Render supplied cases; hover stays in the browser and selection fires once."""
    payload = [{field: str(case.get(field, ""))
                for field in ("id", "title", "subtitle", "text", "source")}
               for case in cases]
    return _component("case_picker")(
        data={"cases": payload, "selected": selected, "epoch": epoch, "zh": zh},
        key="case_picker_v2", on_choose_change=on_choose,
    )


def render_journey(
    steps: Sequence[Mapping[str, Any]], on_navigate: Callable[[], None],
    key: str = "journey_v2",
):
    """Render fixed journey text and states; navigation is a one-shot event."""
    payload = [{field: str(step.get(field, ""))
                for field in ("id", "title", "detail", "state")}
               for step in steps]
    current = next((step["id"] for step in payload if step["state"] in {"current", "active"}), None)
    return _component("journey")(
        data={"steps": payload, "current": current}, key=key,
        on_navigate_change=on_navigate,
    )


def render_scroll(target: str, nonce: int):
    """Perform a single scoped navigation action on an app-owned anchor."""
    if target not in {"model", "scenario", "conversation", "composer"}:
        raise ValueError("Unknown navigation target")
    return _component("scroll_bridge")(
        data={"target": target, "nonce": nonce}, key="scroll_bridge_v2", height=0,
    )


def render_message_motion(epoch: int, count: int):
    """Animate only newly appended transcript messages."""
    return _component("message_motion")(data={"epoch": epoch, "count": count}, key="message_motion_v2", height=0)


def render_welcome(
    selected: str, ready: bool | Mapping[str, bool], zh: bool,
    on_choose: Callable[[], None], nonce: int = 0,
):
    """Render public provider selection; all configuration stays in Python.

    Read the chosen ID from st.session_state["welcome_v2"]["choose"] in the
    callback. Readiness accepts a bool for the selected model or an ID mapping.
    """
    providers = ("gemini", "zhipu", "openrouter")
    if selected not in providers:
        raise ValueError("Unknown model provider")
    statuses = ({provider: ready.get(provider) is True for provider in providers}
                if isinstance(ready, Mapping)
                else {provider: bool(ready) and provider == selected for provider in providers})
    return _component("welcome")(
        data={"selected": selected, "ready": statuses, "zh": bool(zh), "nonce": int(nonce)},
        key="welcome_v2", on_choose_change=on_choose,
    )


def render_transition(kind: str, nonce: int, title: str):
    """Run a cancellable confirmation once per nonce at an owned anchor."""
    if kind not in {"model", "scenario", "conversation"}:
        raise ValueError("Unknown transition target")
    return _component("transition_bridge")(
        data={"kind": kind, "nonce": int(nonce), "title": str(title)},
        key="transition_v2", height=0,
    )


def render_resume(token: str, on_restore: Callable[[], None], on_ready: Callable[[], None]):
    """Send an opaque session token only; restoration is a one-shot callback."""
    return _component("resume_bridge")(
        data={"token": str(token)}, key="resume_v2", height=0,
        on_restore_change=on_restore, on_ready_change=on_ready,
    )


def render_copy(text: str, key: str, zh: bool = False):
    """Copy an assistant question on an explicit browser click."""
    return _component("copy_reply")(data={"text": str(text), "zh": bool(zh)}, key=key)


_PALETTE_ACTIONS = frozenset({"model", "scenario", "conversation", "notebook", "briefing", "write"})


def render_palette(
    commands: Sequence[Mapping[str, Any]], zh: bool, on_action: Callable[[], None],
):
    """Render public navigation commands and validate each one-shot action.

    The zero-argument callback reads ``st.session_state['command_v2']['action']``.
    Only known, currently enabled command IDs reach it. Search and highlight
    changes stay local; no conversation or model configuration is sent here.
    """
    payload = []
    seen = set()
    for command in commands:
        action = command.get("id")
        if not isinstance(action, str) or action not in _PALETTE_ACTIONS or action in seen:
            continue
        seen.add(action)
        payload.append({"id": action, "title": str(command.get("title", "")),
                        "hint": str(command.get("hint", "")), "enabled": command.get("enabled") is True})
    enabled = {command["id"] for command in payload if command["enabled"]}

    def dispatch():
        event = st.session_state.get("command_v2", {})
        action = event.get("action") if hasattr(event, "get") else None
        if isinstance(action, str) and action in _PALETTE_ACTIONS and action in enabled:
            on_action()

    return _component("command_palette")(
        data={"commands": payload, "zh": bool(zh)}, key="command_v2", on_action_change=dispatch,
    )
