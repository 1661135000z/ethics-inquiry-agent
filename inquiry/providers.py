"""Small HTTP adapters with free-model allowlists and sanitized failures."""
from collections import deque
from threading import Lock
import time
import re
import httpx

PROVIDERS = {
    "gemini": {"name": "Google Gemini", "key": "GEMINI_API_KEY", "model": "gemini-2.5-flash-lite", "setting": "GEMINI_MODEL"},
    "openrouter": {"name": "OpenRouter · free", "key": "OPENROUTER_API_KEY", "model": "openrouter/free", "setting": "OPENROUTER_MODEL"},
    "zhipu": {"name": "智谱 GLM · 国内备选", "key": "ZHIPU_API_KEY", "model": "glm-4.7-flash", "setting": "ZHIPU_MODEL"},
}


class ProviderError(RuntimeError):
    def __init__(self, message, code="configuration"):
        super().__init__(message)
        self.code = code


def settings_from(env, secrets=None):
    keys = {"GEMINI_FREE_TIER_CONFIRMED", "ZHIPU_FREE_TIER_CONFIRMED", "ACCESS_CODE"}
    for p in PROVIDERS.values(): keys.update([p["key"], p["setting"]])
    secrets = secrets or {}
    return {key: str(env.get(key) or secrets.get(key) or "").strip() for key in keys}


class Limits:
    """Process-wide attempt limiter; not a replacement for provider billing controls."""
    def __init__(self, count=40, seconds=3600, clock=time.monotonic):
        self.count, self.seconds, self.clock = count, seconds, clock
        self.events, self.lock = deque(), Lock()

    def take(self):
        with self.lock:
            now = self.clock()
            while self.events and now - self.events[0] >= self.seconds:
                self.events.popleft()
            if len(self.events) >= self.count: return False
            self.events.append(now)
            return True


class Client:
    def __init__(self, provider, settings, transport=None, budget=None):
        self.provider, self.settings, self.transport, self.budget = provider, settings, transport, budget

    def validate(self):
        if self.provider not in PROVIDERS: raise ProviderError("Unknown provider.")
        p = PROVIDERS[self.provider]
        key = self.settings.get(p["key"], "")
        if not key: raise ProviderError("No API key configured / 尚未配置API密钥。")
        model = self.settings.get(p["setting"]) or p["model"]
        if self.provider == "openrouter":
            allowed = model == "openrouter/free" or bool(re.fullmatch(r"[\w.-]+/[\w.-]+:free", model))
        elif self.provider == "gemini":
            allowed = model in {"gemini-2.5-flash-lite", "gemini-2.5-flash"}
        else:
            allowed = model == "glm-4.7-flash"
        if not allowed: raise ProviderError("Model blocked by the free-tier allowlist; no request was sent.")
        if self.provider in {"gemini", "zhipu"} and self.settings.get(f"{self.provider.upper()}_FREE_TIER_CONFIRMED", "").lower() != "true":
            raise ProviderError("Owner must confirm the account's current free-tier eligibility in Secrets before use.")
        return key, model

    def complete(self, messages):
        key, model = self.validate()
        if self.budget is not None and not self.budget():
            raise ProviderError("Local request limit reached / 已达到本应用的请求限制。", "local_limit")
        headers = {"Content-Type": "application/json"}
        if self.provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            headers["x-goog-api-key"] = key
            payload = {
                "systemInstruction": {"parts": [{"text": "\n".join(m["content"] for m in messages if m["role"] == "system")}]},
                "contents": [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in messages if m["role"] != "system"],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1600, "responseMimeType": "application/json", "thinkingConfig": {"thinkingBudget": 0}},
            }
        else:
            url = "https://openrouter.ai/api/v1/chat/completions" if self.provider == "openrouter" else "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers["Authorization"] = "Bearer " + key
            payload = {"model": model, "messages": messages, "temperature": 0.3, "max_tokens": 1600, "stream": False}
            if self.provider == "openrouter":
                topics = ["role", "interests", "pressure", "evidence", "review"]
                payload["response_format"] = {"type": "json_schema", "json_schema": {
                    "name": "inquiry_response", "strict": True, "schema": {
                        "type": "object", "additionalProperties": False,
                        "properties": {
                            "question": {"type": "string"},
                            "focus": {"type": "string", "enum": topics + ["scope"]},
                            "observations": {"type": "array", "items": {
                                "type": "object", "additionalProperties": False,
                                "properties": {"area": {"type": "string", "enum": topics}, "quote": {"type": "string"}},
                                "required": ["area", "quote"]}},
                        }, "required": ["question", "focus", "observations"],
                    }}}
                payload["provider"] = {"require_parameters": True}
                payload["reasoning"] = {"enabled": False}
            if self.provider == "zhipu": payload["thinking"] = {"type": "disabled"}
        try:
            with httpx.Client(timeout=45.0, follow_redirects=False, transport=self.transport) as http:
                response = http.post(url, headers=headers, json=payload)
        except (httpx.HTTPError, OSError):
            raise ProviderError("Connection failed or timed out. Try another configured provider / 连接失败或超时。", "network") from None
        if response.status_code != 200:
            code = "quota" if response.status_code in {402, 429} else "auth" if response.status_code in {401, 403} else "unavailable"
            notices = {"quota": "Free quota/capacity unavailable. Wait or select another free provider; do not enable paid billing.",
                       "auth": "Access denied. Check the API key, free-tier eligibility and regional availability.",
                       "unavailable": "Provider/model unavailable. Check configuration or switch provider."}
            raise ProviderError(notices[code], code)
        try:
            data = response.json()
            if self.provider == "gemini":
                text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"] if not p.get("thought"))
                actual = data.get("modelVersion", model)
                tokens = data.get("usageMetadata", {}).get("totalTokenCount")
            else:
                text = data["choices"][0]["message"]["content"]
                actual, tokens = data.get("model", model), data.get("usage", {}).get("total_tokens")
            if not isinstance(text, str) or not text.strip() or len(text) > 16000: raise ValueError()
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):
            raise ProviderError("Provider returned an empty, blocked or invalid response. Your input was kept.", "format") from None
        return text, {"provider": self.provider, "model": str(actual), "tokens": tokens if isinstance(tokens, int) else None}


class FallbackClient:
    """Caller constructs this only after explicit consent to share context with BOTH services."""
    def __init__(self, primary, secondary=None):
        self.primary, self.secondary = primary, secondary

    def complete(self, messages):
        try:
            return self.primary.complete(messages)
        except ProviderError as error:
            if self.secondary is None or error.code not in {"quota", "network", "unavailable"}: raise
            text, meta = self.secondary.complete(messages)
            meta["fallback_from"] = self.primary.provider
            return text, meta
