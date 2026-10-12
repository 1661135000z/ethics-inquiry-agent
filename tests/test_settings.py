import unittest
from inquiry import providers

class SettingsTests(unittest.TestCase):
    def test_session_key_overrides_owner_only_for_that_service(self):
        self.assertTrue(hasattr(providers, 'session_settings'), 'session credential resolution is missing')
        owner = {'GEMINI_API_KEY':'owner', 'ZHIPU_API_KEY':'domestic', 'GEMINI_FREE_TIER_CONFIRMED':'true'}
        result = providers.session_settings(owner, 'gemini', 'visitor', 'gemini-2.5-flash-lite', False)
        self.assertEqual(result['GEMINI_API_KEY'], 'visitor')
        self.assertEqual(result['ZHIPU_API_KEY'], 'domestic')
        self.assertEqual(result['GEMINI_FREE_TIER_CONFIRMED'], 'false')
        self.assertEqual(owner['GEMINI_API_KEY'], 'owner')

    def test_empty_session_key_uses_owner_and_dotenv_is_lowest_priority(self):
        self.assertTrue(hasattr(providers, 'session_settings'))
        result = providers.settings_from({'GEMINI_API_KEY':'env'}, {'GEMINI_API_KEY':'secret','ZHIPU_API_KEY':'secret-glm'}, {'GEMINI_API_KEY':'file','ZHIPU_API_KEY':'file-glm'})
        self.assertEqual(result['GEMINI_API_KEY'], 'env')
        self.assertEqual(result['ZHIPU_API_KEY'], 'secret-glm')
        self.assertEqual(providers.session_settings(result,'gemini','', 'gemini-2.5-flash-lite',False)['GEMINI_API_KEY'],'env')
