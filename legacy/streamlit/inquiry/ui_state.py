"""Product state, independent of widgets and provider credentials."""
from dataclasses import dataclass, field
from .core import Session

@dataclass
class Workspace:
    conversation: Session = field(default_factory=Session)
    case_id: str = 'blank'
    initial_text: str = ''
    draft: str = ''
    phase: str = 'compose'
    pending_case: str = 'blank'
    pending_text: str = ''
    confirmed_model: str = ''
    workflow: tuple = ('idle', False)
    saved_workflow: tuple = ('idle', False)
    show_briefing: bool = False
    epoch: int = 0
    provider_id: str = ''
    model_id: str = ''
    language_id: str = 'English'
    request_count: int = 0
    onboarded: bool = False
    view: str = 'conversation'
    saved_view: str = 'conversation'
    note_filter: str = 'all'
    theme: str = ''

    def confirm_model(self, signature):
        self.confirmed_model = signature
        self.onboarded = True

    def current_step(self, signature, configured):
        if not configured or signature != self.confirmed_model:
            return 'model'
        text = self.pending_text if self.phase == 'select' else self.draft
        case = self.pending_case if self.phase == 'select' else self.case_id
        if not self.conversation.messages and case == 'blank' and not text.strip():
            return 'scenario'
        if self.phase == 'select' and case == 'blank' and not text.strip():
            return 'scenario'
        return 'conversation'

    def choose(self, case_id, text):
        if self.conversation.messages:
            self.enter_selection()
            self.pending_case, self.pending_text = case_id, text
        else:
            self.case_id, self.draft = case_id, text

    def enter_selection(self):
        if not self.conversation.messages:
            return
        if self.phase != 'select':
            self.pending_case, self.pending_text = self.case_id, self.initial_text
            self.saved_view = self.view
            self.view = 'conversation'
            self.saved_workflow = self.workflow
            self.phase = 'select'
            self.workflow = ('idle', False)
            self.epoch += 1

    def cancel_selection(self):
        if self.phase == 'select':
            self.phase = 'chat'
            self.pending_case, self.pending_text = 'blank', ''
            self.workflow = self.saved_workflow
            self.view = self.saved_view
            self.epoch += 1

    def new_conversation(self):
        self.conversation = Session()
        self.draft = self.initial_text
        self.phase = 'compose'
        self.pending_case, self.pending_text = 'blank', ''
        self.workflow = self.saved_workflow = ('idle', False)
        self.show_briefing = False
        self.view = self.saved_view = 'conversation'
        self.note_filter = 'all'
        self.epoch += 1

    def submit(self, text, client, language='English', progress=None):
        switching = self.phase == 'select'
        candidate = Session() if switching else self.conversation
        first = not candidate.messages
        def emit(stage):
            self.workflow = (stage, False)
            if progress:
                progress(stage)
        try:
            reply = candidate.submit(text, client, language, progress=emit)
        except Exception:
            self.workflow = (self.workflow[0], True)
            raise
        # A pending switch replaces the old inquiry only after a valid first reply.
        if switching:
            self.conversation = candidate
            self.case_id = self.pending_case
        if first:
            self.initial_text = text.strip()
        self.phase = 'chat'
        self.view = 'conversation'
        if switching: self.note_filter = 'all'
        self.draft = ''
        self.pending_case, self.pending_text = 'blank', ''
        self.show_briefing = False
        return reply

    def regenerate(self, client, language='English', progress=None):
        def emit(stage):
            self.workflow = (stage, False)
            if progress:
                progress(stage)
        try:
            reply = self.conversation.regenerate(client, language, progress=emit)
        except Exception:
            self.workflow = (self.workflow[0], True)
            raise
        self.show_briefing = False
        return reply
