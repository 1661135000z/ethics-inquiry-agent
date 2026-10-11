import json
import unittest
import httpx
from inquiry.providers import Client, ProviderError, settings_from, Limits


class ProviderTests(unittest.TestCase):
    def settings(self, **extra):
        return settings_from({"OPENROUTER_API_KEY": "test-secret", **extra})

    def test_paid_model_blocked_before_transport(self):
        c = Client("openrouter", self.settings(OPENROUTER_MODEL="vendor/paid"))
        with self.assertRaises(ProviderError): c.complete([{"role": "user", "content": "hi"}])

    def test_secrets_fallback_and_environment_precedence(self):
        result = settings_from({"OPENROUTER_API_KEY": "env"}, {"OPENROUTER_API_KEY": "secret", "ZHIPU_API_KEY": "local"})
        self.assertEqual(result["OPENROUTER_API_KEY"], "env")
        self.assertEqual(result["ZHIPU_API_KEY"], "local")

    def test_openrouter_wire_format_and_actual_model(self):
        def handle(req):
            self.assertEqual(req.url.host, "openrouter.ai")
            body = json.loads(req.content)
            self.assertEqual(body["model"], "openrouter/free")
            self.assertLessEqual(body["max_tokens"], 1600)
            return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}], "model": "actual/free", "usage": {"total_tokens": 80}})
        c = Client("openrouter", self.settings(), transport=httpx.MockTransport(handle))
        text, meta = c.complete([{"role": "user", "content": "hi"}])
        self.assertEqual(text, "{}")
        self.assertEqual(meta["model"], "actual/free")

    def test_gemini_requires_owner_free_tier_confirmation(self):
        c = Client("gemini", settings_from({"GEMINI_API_KEY": "secret"}))
        with self.assertRaises(ProviderError): c.complete([])

    def test_gemini_native_payload(self):
        def handle(req):
            self.assertEqual(req.url.host, "generativelanguage.googleapis.com")
            self.assertNotIn("secret", str(req.url))
            body=json.loads(req.content)
            self.assertEqual(body["systemInstruction"]["parts"][0]["text"], "rules")
            self.assertEqual(body["contents"][0]["role"], "user")
            return httpx.Response(200, json={"candidates":[{"content":{"parts":[{"text":"{}"}]}}], "modelVersion":"gemini-test"})
        c=Client("gemini", settings_from({"GEMINI_API_KEY":"secret", "GEMINI_FREE_TIER_CONFIRMED":"true"}), transport=httpx.MockTransport(handle))
        self.assertEqual(c.complete([{"role":"system","content":"rules"},{"role":"user","content":"hi"}])[0], "{}")

    def test_errors_do_not_expose_secrets_or_server_body(self):
        def handle(req): return httpx.Response(429, text="secret credential and private scenario")
        c=Client("openrouter", self.settings(), transport=httpx.MockTransport(handle))
        with self.assertRaises(ProviderError) as caught: c.complete([])
        self.assertNotIn("private", str(caught.exception))
        self.assertNotIn("secret", str(caught.exception))
        self.assertEqual(caught.exception.code, "quota")

    def test_limits_apply_to_attempts_and_expire(self):
        clock=[0.0]
        limits=Limits(2, 60, clock=lambda:clock[0])
        self.assertTrue(limits.take()); self.assertTrue(limits.take())
        self.assertFalse(limits.take())
        clock[0]=61
        self.assertTrue(limits.take())


if __name__ == "__main__": unittest.main()
