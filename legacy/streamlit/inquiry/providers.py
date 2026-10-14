"""Small HTTP adapters with free-model allowlists and sanitized failures."""
from collections import deque
from threading import Lock
import time
import re
import httpx

GEMINI_MODELS = ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash")

PROVIDERS = {
    "gemini": {"name": "Google Gemini", "key": "GEMINI_API_KEY", "model": GEMINI_MODELS[0], "setting": "GEMINI_MODEL"},
    "openrouter": {"name": "OpenRouter · free", "key": "OPENROUTER_API_KEY", "model": "openrouter/free", "setting": "OPENROUTER_MODEL"},
    "zhipu": {"name": "智谱 GLM · 国内备选", "key": "ZHIPU_API_KEY", "model": "glm-4.7-flash", "setting": "ZHIPU_MODEL"},
}


class ProviderError(RuntimeError):
    def __init__(self, message, code="configuration"):
        super().__init__(message)
        self.code = code


def settings_from(env, secrets=None, dotenv=None):
    keys = {"GEMINI_FREE_TIER_CONFIRMED", "ZHIPU_FREE_TIER_CONFIRMED", "ACCESS_CODE"}
    for p in PROVIDERS.values(): keys.update([p["key"], p["setting"]])
    secrets = secrets or {}
    dotenv = dotenv or {}
    return {key: str(env.get(key) or secrets.get(key) or dotenv.get(key) or "").strip() for key in keys}


def session_settings(owner, provider, key, model, free_confirmed=False):
    """Copy settings; never mutate shared configuration or persist visitor credentials."""
    result = dict(owner)
    p = PROVIDERS[provider]
    result[p['setting']] = model
    if key.strip():
        result[p['key']] = key.strip()
        result[f'{provider.upper()}_FREE_TIER_CONFIRMED'] = str(bool(free_confirmed)).lower()
    return result


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
            allowed = model in GEMINI_MODELS
        else:
            allowed = model == "glm-4.7-flash"
        if not allowed: raise ProviderError("Model blocked by the free-tier allowlist; no request was sent.")
        if self.provider in {"gemini", "zhipu"} and self.settings.get(f"{self.provider.upper()}_FREE_TIER_CONFIRMED", "").lower() != "true":
            raise ProviderError("Confirm the account's free-tier eligibility / 请先确认当前密钥的免费档资格。")
        return key, model

    def response_error(self, response, model):
        """Expose only status and a bounded machine code, never the upstream message."""
        if response.status_code == 200: return
        status = response.status_code
        code = "quota" if status in {402, 429} else "auth" if status in {401, 403} else "unavailable"
        diagnostic = ""
        try:
            error = response.json().get("error", {})
            number = str(error.get("code", ""))
            if re.fullmatch(r"\d{3,6}", number): diagnostic = f" · platform code {number}"
        except (ValueError, AttributeError, TypeError):
            pass
        if status == 404:
            notice = "Model/resource not found / 模型或接口资源不可用。Gemini请检查当前密钥的可用模型；2.5系列可能限制新项目访问。"
        elif status == 401:
            notice = "Authentication rejected / 平台未接受密钥认证。智谱国内平台请复制完整API Key，不要包含Bearer前缀、引号或换行；模型更名不能解决认证失败。"
        elif code == "quota":
            notice = "Free quota/capacity unavailable / 免费额度或容量不足，请稍后重试或切换免费服务，不要开启付费计费。"
        elif code == "auth":
            notice = "Access denied / 请检查账号权限、免费档资格及地区限制。"
        else:
            notice = "Provider/model unavailable / 服务或模型暂不可用，请检查模型选择或切换服务。"
        raise ProviderError(f"{self.provider} · {model} · {notice} (HTTP {status}{diagnostic})", code)

    def available_models(self):
        """Read Gemini model metadata for this key; return only vetted free-model names."""
        if self.provider != "gemini": raise ProviderError("Model discovery is supported for Gemini only.")
        key, model = self.validate()
        if self.budget is not None and not self.budget():
            raise ProviderError("Local request limit reached / 已达到本应用的请求限制。", "local_limit")
        try:
            with httpx.Client(timeout=30.0, follow_redirects=False, transport=self.transport) as http:
                response = http.get("https://generativelanguage.googleapis.com/v1beta/models", params={"pageSize": 1000}, headers={"x-goog-api-key": key})
        except (httpx.HTTPError, OSError):
            raise ProviderError("Model list unavailable / 无法连接Google模型列表，请检查网络或地区限制。", "network") from None
        self.response_error(response, model)
        try:
            entries = response.json()["models"]
            if not isinstance(entries, list): raise ValueError()
            names = {item.get("name", "").removeprefix("models/") for item in entries if isinstance(item, dict) and isinstance(item.get("name"), str) and "generateContent" in (item.get("supportedGenerationMethods") or [])}
        except (ValueError, KeyError, TypeError, AttributeError):
            raise ProviderError("Invalid model metadata / 模型列表格式无法识别。", "format") from None
        return [name for name in GEMINI_MODELS if name in names]

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
            if not model.startswith("gemini-2.5-"):
                # New Flash-Lite models default to minimal thinking; do not send 2.5's budget option.
                payload["generationConfig"].pop("thinkingConfig")
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
            if self.provider == "zhipu":
                payload["thinking"] = {"type": "disabled"}
                payload["response_format"] = {"type": "json_object"}
        try:
            with httpx.Client(timeout=45.0, follow_redirects=False, transport=self.transport) as http:
                response = http.post(url, headers=headers, json=payload)
        except (httpx.HTTPError, OSError):
            raise ProviderError("Connection failed or timed out / 连接失败或超时。Gemini可能受网络或地区限制，请手动切换智谱GLM。", "network") from None
        self.response_error(response, model)
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
