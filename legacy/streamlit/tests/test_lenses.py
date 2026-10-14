import unittest
from inquiry.core import Session
from inquiry.lenses import reported_quotes, area_counts, focus_html

class LensTests(unittest.TestCase):
    def test_only_literal_user_statements_are_counted(self):
        s=Session(messages=[{'role':'user','content':'I have not verified the upload records.'},{'role':'assistant','content':'Who can check the records?'},{'role':'user','content':'I have not verified the upload records.'}],observations=[{'area':'evidence','quote':'I have not verified the upload records.'},{'area':'evidence','quote':'I have not verified the upload records.'},{'area':'review','quote':'Who can check the records?'},{'area':'role','quote':'Invented claim.'},{'area':'invalid','quote':'upload records'}])
        quotes=reported_quotes(s)
        self.assertEqual(len(quotes),1)
        self.assertEqual(quotes[0]['turns'],[1,2])
        self.assertEqual(area_counts(s)['evidence'],1)
        self.assertEqual(sum(area_counts(s).values()),1)
        self.assertEqual(reported_quotes(s,'role'),[])
    def test_banner_uses_whitelisted_topic_not_model_markup(self):
        html=focus_html(Session(focus='<script>unsafe</script>'),'中文')
        self.assertIn('情境边界',html)
        self.assertNotIn('<script>',html)
        self.assertNotIn('完成',html)
        self.assertIn('Evidence and alternatives',focus_html(Session(focus='evidence')))
