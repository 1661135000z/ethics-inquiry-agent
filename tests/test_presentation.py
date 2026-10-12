import unittest
from inquiry.presentation import relay_html
class PresentationTests(unittest.TestCase):
    def test_flow_is_panel_with_real_stage_descriptions(self):
        idle=relay_html('idle',True)
        self.assertIn('workflow-panel',idle)
        self.assertIn('等待输入',idle)
        active=relay_html('request',True)
        self.assertEqual(active.count('flow-step active'),1)
        self.assertEqual(active.count('flow-step complete'),1)
        self.assertIn('读取情境与上下文',active)
        failed=relay_html('validate',True,True)
        self.assertEqual(failed.count('flow-step failed'),1)
        self.assertNotIn('flow-step active',failed)
        done=relay_html('done')
        self.assertEqual(done.count('flow-step complete'),4)
