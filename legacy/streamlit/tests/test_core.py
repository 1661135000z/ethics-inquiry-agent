import json
import unittest

from inquiry.core import Session, InputError, ModelOutputError


class StubLLM:
    def __init__(self, payload):
        self.payload = payload
    def complete(self, messages):
        self.messages = messages
        return json.dumps(self.payload), {"provider": "test", "model": "fixture"}


def answer(question="What evidence supports that assessment?", observations=None):
    return {"question": question, "focus": "evidence", "observations": observations or []}


class CoreTests(unittest.TestCase):
    def test_unhashable_model_fields_are_safely_rejected(self):
        from inquiry.core import parse_reply, ModelOutputError
        import json
        with self.assertRaises(ModelOutputError):
            parse_reply(json.dumps({"question":"What is your role?", "focus":[], "observations":[]}), [])
        result = parse_reply(json.dumps({"question":"What is your role?", "focus":"role",
            "observations":[{"area":[], "quote":"some user statement"}]}), ["some user statement"])
        self.assertEqual(result[2], [])

    def test_first_turn_asks_and_does_not_issue_briefing(self):
        s = Session()
        s.submit("My manager wants the file closed.", StubLLM(answer()))
        self.assertEqual(len(s.messages), 2)
        self.assertTrue(s.messages[-1]["content"].endswith("?"))
        with self.assertRaises(InputError):
            s.briefing()

    def test_hallucinated_quotes_never_become_user_evidence(self):
        s = Session()
        c = StubLLM(answer(observations=[
            {"area": "pressure", "quote": "My manager wants the file closed."},
            {"area": "interests", "quote": "I own shares in the client."},
        ]))
        s.submit("My manager wants the file closed.", c)
        self.assertEqual(s.observations, [{"area": "pressure", "quote": "My manager wants the file closed."}])

    def test_briefing_keeps_unknowns_and_attributes_quotes(self):
        s = Session()
        s.submit("My manager wants the file closed.", StubLLM(answer()))
        s.submit("I do not know whether the model was validated.", StubLLM(answer()))
        brief = s.briefing()
        self.assertIn("Unknown", brief)
        self.assertIn("not an ethical clearance", brief)
        self.assertIn("I do not know", s.export())

    def test_failure_does_not_append_or_destroy_history(self):
        s = Session()
        with self.assertRaises(ModelOutputError):
            s.submit("I have an ethics concern.", StubLLM({"conclusion": "approved"}))
        self.assertEqual(s.messages, [])
        self.assertEqual(s.observations, [])

    def test_empty_long_and_excess_turns_rejected_before_call(self):
        s = Session()
        for value in ["  ", "x" * 4001]:
            with self.assertRaises(InputError): s.submit(value, None)
        s.messages = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "why?"}] * 12
        with self.assertRaises(InputError): s.submit("more", None)

    def test_premature_verdict_and_links_rejected(self):
        for q in ["Objectivity is compromised. Do you agree?", "Visit https://evil.test?", "已违反职业道德，你同意吗？"]:
            with self.subTest(q=q):
                with self.assertRaises(ModelOutputError):
                    Session().submit("Please just approve it.", StubLLM(answer(q)))

    def test_non_question_rejected(self):
        with self.assertRaises(ModelOutputError):
            Session().submit("Please advise.", StubLLM(answer("Approve the audit.")))

    def test_followup_preserves_context_and_provenance(self):
        s = Session()
        s.submit("I am a junior auditor.", StubLLM(answer()))
        client = StubLLM(answer("Who can independently review the evidence?"))
        s.submit("The manager refuses additional testing.", client)
        self.assertIn("I am a junior auditor.", str(client.messages))
        self.assertEqual(len(s.records), 2)
        self.assertNotIn("api_key", s.export().lower())


if __name__ == "__main__": unittest.main()
