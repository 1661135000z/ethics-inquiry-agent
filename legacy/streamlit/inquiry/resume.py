"""Bounded, process-local inquiry recovery; never writes browser text or files."""
from collections import OrderedDict
from copy import deepcopy
from dataclasses import fields
import secrets
from threading import RLock
import time

from .core import Session
from .ui_state import Workspace


class ResumeStore:
    """Opaque capabilities identify isolated workspace snapshots for two hours.

    The caller keeps the token in tab session storage, never in a URL. Recovery
    ends when this process stops, the entry expires, or capacity evicts it.
    Provider credentials/settings must remain outside Workspace.
    """

    def __init__(self, ttl=7200, max_entries=128, clock=None):
        if ttl <= 0 or max_entries < 1:
            raise ValueError("Recovery TTL and capacity must be positive.")
        self.ttl = ttl
        self.max_entries = max_entries
        self._clock = clock or time.monotonic
        self._entries = OrderedDict()
        self._lock = RLock()

    @staticmethod
    def _snapshot(workspace):
        # Streamlit can retain a cached store while reloading imported classes.
        # Resolve the current declared schema instead of relying on class identity.
        from .ui_state import Workspace as CurrentWorkspace
        from .core import Session as CurrentSession
        if not (isinstance(workspace, CurrentWorkspace) or
                (type(workspace).__name__ == "Workspace" and
                 type(workspace).__module__ == CurrentWorkspace.__module__)):
            raise TypeError("Only Workspace snapshots can be recovered.")
        # Copy declared product fields only; exclude attached runtime objects,
        # credentials and the connection signature, which must be reconfirmed.
        defaults = CurrentWorkspace()
        values = {f.name: deepcopy(getattr(workspace, f.name, getattr(defaults, f.name)))
                  for f in fields(CurrentWorkspace) if f.name not in {"conversation", "confirmed_model"}}
        values["conversation"] = CurrentSession(**{
            f.name: deepcopy(getattr(workspace.conversation, f.name)) for f in fields(CurrentSession)
        })
        return CurrentWorkspace(**values)

    def _prune(self, now):
        for token, (deadline, _) in list(self._entries.items()):
            if deadline <= now:
                del self._entries[token]

    def issue(self, workspace):
        snapshot = self._snapshot(workspace)
        with self._lock:
            now = self._clock()
            self._prune(now)
            token = secrets.token_urlsafe(32)
            while token in self._entries:
                token = secrets.token_urlsafe(32)
            self._entries[token] = (now + self.ttl, snapshot)
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
            return token

    def get(self, token):
        if not isinstance(token, str):
            return None
        with self._lock:
            now = self._clock()
            self._prune(now)
            entry = self._entries.get(token)
            if entry is None:
                return None
            snapshot = deepcopy(entry[1])
            self._entries[token] = (now + self.ttl, entry[1])
            self._entries.move_to_end(token)
            return snapshot

    def save(self, token, workspace):
        if not isinstance(token, str):
            return False
        snapshot = self._snapshot(workspace)
        with self._lock:
            now = self._clock()
            self._prune(now)
            if token not in self._entries:
                return False
            self._entries[token] = (now + self.ttl, snapshot)
            self._entries.move_to_end(token)
            return True
