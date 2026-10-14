import json
import unittest
from inquiry.core import parse_reply, ModelOutputError

class UncertaintyTests(unittest.TestCase):
    def response(self,q):
        return json.dumps({'question':q,'focus':'evidence','observations':[]})
    def test_unknown_reviewer_cannot_become_absent_reviewer(self):
        with self.assertRaises(ModelOutputError):
            parse_reply(self.response('既然这些分录未被仪表盘覆盖且无人检查，您可以独立复核吗？'),['我不知道由谁检查这些分录。'])
    def test_explicit_user_statement_may_be_queried(self):
        q='既然这些分录无人检查，您可以请谁独立复核？'
        self.assertEqual(parse_reply(self.response(q),['我确认这些分录无人检查。'])[0],q)
    def test_english_unknown_does_not_become_absence(self):
        with self.assertRaises(ModelOutputError):
            parse_reply(self.response('Since nobody reviewed these entries, who could review them independently?'),['I do not know who reviewed these entries.'])
