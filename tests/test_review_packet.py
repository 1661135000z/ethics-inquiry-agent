import copy
from html.parser import HTMLParser
import re
import unittest

from inquiry.core import AREAS, InputError, Session
from inquiry.review_packet import build_review_packet


class DocumentParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.attributes = []
        self.rows = []
        self._row = None
        self._cell = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attributes.extend(attrs)
        if tag == "tr":
            self._row = []
        if tag in ("td", "th"):
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self._row.append("".join(self._cell))
            self._cell = None
        if tag == "tr":
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        self.text.append(data)
        if self._cell is not None:
            self._cell.append(data)

    @property
    def visible_text(self):
        return "\n".join(self.text)


def example_session():
    first = "I review an estimate.\nThe underlying records are incomplete."
    second = "I do not know who reviewed the estimate."
    return Session(
        messages=[
            {"role": "user", "content": first},
            {"role": "assistant", "content": "Who can verify the underlying records?"},
            {"role": "user", "content": second},
            {"role": "assistant", "content": "Which records could identify the reviewer?"},
        ],
        observations=[
            {"area": "role", "quote": "I review an estimate."},
            {"area": "evidence", "quote": "The underlying records are incomplete."},
            {"area": "review", "quote": second},
        ],
        records=[
            {"turn": 1, "time": "2026-01-02T03:04:05+00:00", "provider": "Example provider", "model": "example-alpha"},
            {"turn": 2, "time": "2026-01-02T03:05:06+00:00", "provider": "Example provider", "model": "example-beta", "regenerations": 2},
        ],
        focus="review",
    )


class ReviewPacketTests(unittest.TestCase):
    def test_shared_colors_are_defined_in_a_valid_root_rule(self):
        source = build_review_packet(example_session())
        stylesheet = source.split("<style>", 1)[1].split("</style>", 1)[0]
        root = re.search(r"(?m)^:root\s*\{([^}]+)\}", stylesheet)
        self.assertIsNotNone(root, "Shared color variables require a valid :root selector")
        definitions = set(re.findall(r"(--[a-z-]+)\s*:", root.group(1)))
        references = set(re.findall(r"var\((--[a-z-]+)\)", stylesheet))
        self.assertTrue(references)
        self.assertLessEqual(references, definitions)

    def test_minimum_turns_matches_briefing(self):
        for session in (Session(), Session(messages=[{"role": "user", "content": "An estimate requires review."}])):
            with self.subTest(turns=session.turns):
                with self.assertRaisesRegex(InputError, "answer at least one follow-up"):
                    build_review_packet(session)

    def test_complete_context_quotes_and_provenance_are_preserved(self):
        session = example_session()
        original = copy.deepcopy(session)
        source = build_review_packet(session)
        document = DocumentParser(source)
        content = document.visible_text
        self.assertTrue(source.startswith("<!doctype html>"))
        self.assertEqual(session, original)
        for message in session.messages:
            self.assertIn(message["content"], content)
        transcript = content[content.index("Full conversation transcript"):]
        positions = [transcript.index(message["content"]) for message in session.messages]
        self.assertEqual(positions, sorted(positions))
        for observation in session.observations:
            self.assertIn(observation["quote"], document.text)
        for labels in AREAS.values():
            self.assertIn(labels[0], content)
        for value in ("example-alpha", "example-beta", "2026-01-02T03:05:06+00:00", "Regenerations", "Example provider"):
            self.assertIn(value, content)
        self.assertIn("2", document.text)
        self.assertEqual(document.rows, [
            ["Turn", "Provider", "Model", "Recorded time", "Regenerations"],
            ["1", "Example provider", "example-alpha", "2026-01-02T03:04:05+00:00", "Not recorded"],
            ["2", "Example provider", "example-beta", "2026-01-02T03:05:06+00:00", "2"],
        ])
        self.assertIn("not verified audit evidence", content)
        self.assertIn("not an ethical clearance", content)
        self.assertIn("Unknown / no statement extracted", content)
        self.assertIn("not evidence that the issue is absent", content)
        self.assertIn(session.briefing().split("\n\n")[-1], content)
        self.assertIn("@media print", source)
        self.assertIn("white-space: pre-wrap", source)
        self.assertIn("Ctrl+P", content)

    def test_user_model_and_record_markup_remain_inert_text(self):
        payload = '<script>alert("example")</script><img src="https://example.invalid/x" onerror="alert(1)"> & <b>literal</b>'
        session = example_session()
        session.messages[0]["content"] = payload + "\nOriginal scenario text."
        session.messages[3]["content"] = payload
        session.observations = [{"area": "pressure", "quote": payload}]
        session.records[0].update(provider=payload, model=payload, time=payload, turn=payload, regenerations=payload)
        source = build_review_packet(session)
        document = DocumentParser(source)
        self.assertNotIn("script", document.tags)
        self.assertNotIn("img", document.tags)
        self.assertNotIn("b", document.tags)
        self.assertIn(payload, document.text)
        self.assertEqual(document.rows[1], [payload] * 5)
        self.assertIn("&lt;script&gt;", source)
        for key, value in document.attributes:
            self.assertNotIn(key, ("src", "href", "onerror", "onclick"))
            self.assertNotIn("https://example.invalid", value or "")

    def test_only_literal_user_quotes_are_presented_as_observations(self):
        session = example_session()
        session.observations = [
            {"area": "interests", "quote": "Unsupported invented relationship."},
            {"area": "review", "quote": session.messages[1]["content"]},
            {"area": "pressure", "quote": "I review records are incomplete."},
        ]
        content = DocumentParser(build_review_packet(session)).visible_text
        self.assertNotIn("Unsupported invented relationship.", content)
        self.assertEqual(content.count("Unknown / no statement extracted"), len(AREAS))

    def test_chinese_packet_retains_original_language_and_uncertainty(self):
        session = example_session()
        session.messages[2]["content"] = "我不知道由谁复核，现有资料也未说明。"
        session.observations = [{"area": "review", "quote": session.messages[2]["content"]}]
        source = build_review_packet(session, "中文")
        content = DocumentParser(source).visible_text
        self.assertIn('lang="zh-CN"', source)
        self.assertIn("人工复核简报", content)
        self.assertIn("不是已核实的审计证据", content)
        self.assertIn("不构成伦理许可", content)
        self.assertIn("尚未提取到相关陈述", content)
        self.assertIn("不代表不存在相关事实", content)
        self.assertIn("我不知道由谁复核，现有资料也未说明。", content)
        self.assertIn("I review an estimate.", content)
        for labels in AREAS.values():
            self.assertIn(labels[1], content)

    def test_missing_records_do_not_invent_provenance_or_leak_extra_fields(self):
        session = example_session()
        session.records = [{"turn": 1, "provider": "Example provider", "api_key": "secret-example-value", "workspace": "private-example-value"}]
        content = DocumentParser(build_review_packet(session)).visible_text
        self.assertIn("Not recorded", content)
        self.assertNotIn("secret-example-value", content)
        self.assertNotIn("private-example-value", content)
        session.records = []
        self.assertIn("No model provenance records available", DocumentParser(build_review_packet(session)).visible_text)


if __name__ == "__main__":
    unittest.main()
