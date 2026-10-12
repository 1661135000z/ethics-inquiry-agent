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
    if target not in {"model", "scenario", "conversation"}:
        raise ValueError("Unknown navigation target")
    return _component("scroll_bridge")(
        data={"target": target, "nonce": nonce}, key="scroll_bridge_v2", height=0,
    )


def render_message_motion(epoch: int, count: int):
    """Animate only newly appended transcript messages."""
    return _component("message_motion")(data={"epoch": epoch, "count": count}, key="message_motion_v2", height=0)
