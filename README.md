# Inquire — Audit ethics agent

[Open the live app](https://ethics-inquiry-agent.streamlit.app/)

A bilingual Python + Streamlit learning tool focused on **objectivity**. Describe any audit situation; the agent asks one contextual follow-up question at a time. No scenario is assumed. Optional editable examples include relationships, self-review and two fictional AI-audit situations.

## Run locally / 本地运行

Use Python 3.11 or 3.12 (tested on 3.12). From this folder:

```sh
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`. Fill in **one** API key privately. Never commit the real file. Environment variables with the same names also work and take precedence. Alternatively, copy `.env.example` to `.env`; it is loaded from the project directory without modifying process environment. Developer configuration priority is environment variables → Streamlit Secrets → `.env`. No API key is bundled, and the app does not simulate a live model when unconfigured.

中文：先安装 Python，再按上面步骤安装依赖。把配置模板复制为 `.streamlit/secrets.toml`，只填写你要用的服务。使用者打开已经配置好的在线版无需安装；本地版仍需 Python、依赖、有效密钥和访问模型服务的网络。

## AI Model Settings / 模型设置

**Developer setup:** fill `.env` locally or `.streamlit/secrets.toml`; on Community Cloud, use the Secrets panel. Templates contain empty keys. For Gemini or GLM, set the corresponding `*_FREE_TIER_CONFIRMED` flag to `true` only after confirming your account's current free-model eligibility. API keys are never bundled or displayed from this configuration.

Both developer services can be configured together in Community Cloud **Settings → Secrets**:

```toml
GEMINI_API_KEY = "replace-with-your-key"
GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_FREE_TIER_CONFIRMED = "false"

ZHIPU_API_KEY = "replace-with-your-key"
ZHIPU_MODEL = "glm-4.7-flash"
ZHIPU_FREE_TIER_CONFIRMED = "false"
```

Set each confirmation flag to `"true"` only after checking that account's free-tier eligibility. Replace existing entries rather than creating duplicate TOML fields. Retain any OpenRouter settings. Select the service in the main Model settings panel; clear session keys to use developer keys. Developer keys never appear in the browser input fields. Do not put this filled configuration in the repository.

**Visitor setup:** open **Model settings → Use your own API key**, select a service/model, enter the key in the password field and confirm free eligibility. A nonempty visitor key takes priority for that service; an empty field uses the developer configuration. Keys remain only in that Streamlit session's memory, survive service switching and are removed by **Clear session keys** or session expiry. This app does not write keys to files, logs, exports, GitHub, URLs or shared caches. Browser password masking is visual protection; enter keys only on a trusted HTTPS deployment. A fresh browser session does not inherit another visitor's credentials.

**Test Connection** first checks the account-specific model list for Gemini, then sends one small fictional audit-ethics case through the actual `Session.submit` workflow, including the objectivity prompt, JSON parsing, question-only and quote checks. It consumes one generation request (plus a metadata request for Gemini), does not use the user's case, does not append to the formal conversation, and never automatically falls back to another service. A success badge applies to the current service/key/model configuration; changing it invalidates the badge. A successful test does not establish the quality of all future questions.

中文：在侧栏选择 Gemini 或智谱 GLM，展开“使用自己的 API Key”，输入密钥并勾选免费档确认，点击“测试连接”。不输入自己的密钥时使用开发者配置。请勿把密钥放入聊天内容；无需把密钥发给项目维护者。Gemini 连接失败时可手动切换智谱，原有对话保留。服务提供方仍按自身政策处理请求，应用不能核实账户计费状态。

## Model choices and costs

| Service | Default | Setup / limits |
|---|---|---|
| Google Gemini | `gemini-3.5-flash-lite` | Eligible free-tier project; set `GEMINI_FREE_TIER_CONFIRMED = "true"` only after checking the account. Regional restrictions apply. |
| OpenRouter | `openrouter/free` | The sidebar defaults to the tested `nvidia/nemotron-3-super-120b-a12b:free` model. Select `openrouter/free` for variable routing, or configure another `vendor/model:free` ID. Actual model is recorded. |
| 智谱 GLM | `glm-4.7-flash` | Domestic alternative. Confirm current free eligibility, then set `ZHIPU_FREE_TIER_CONFIRMED = "true"`. |

Only these Gemini/GLM models and OpenRouter free routes are allowed. No paid-model fallback, automatic retry loop, training, or server purchase is needed. **Zero cost cannot be guaranteed by code:** provider terms, account billing, quotas and availability can change. Do not enable paid billing to bypass a limit. Free services may process data for product improvement; use fictional or anonymized scenarios only.

Optional fallback is off by default. Enabling it sends the conversation to the explicitly selected second service after a network/quota/service failure. It does not retry authentication failures or malformed model output. Requests are capped at 24 per browser session, 40/hour and 150/day per running server process, 12 dialogue turns, 4,000 characters per input and 1,600 output tokens per call. Restarting a process resets its counters: these are shared-demo safeguards, not provider billing controls. Set `ACCESS_CODE` for a shared-demo deployment; it is a simple gate, not full user authentication.

## Deploy to Streamlit Community Cloud

1. Put this project's contents in a public GitHub repository. Do not upload private documents, personal information, `.venv`, `.env`, or real Secrets.
2. Sign into [Streamlit Community Cloud](https://share.streamlit.io/), create an app from the repository, select `main` and `app.py`, and use Python 3.12 in advanced settings.
3. Paste the settings into the platform's **Secrets** panel, not into a GitHub file. Configure at least one service and optionally a shared-demo access code.
4. Deploy, then test the public link in a separate browser. Complete the checks in [evaluation.md](docs/evaluation.md) using a real model before sharing the app.
5. Share the app link and retain a source ZIP for reproducibility.

## Mainland access / 中国大陆备用方案

Streamlit Cloud, GitHub and overseas model services are not guaranteed accessible on a mainland local network. Test from the reviewer's actual network before submission. An overseas-hosted app can call its provider server-side, but this does not solve inability to open the webpage or account eligibility restrictions.

准备在线链接、源码 ZIP 和真实测试的演示录像。源码可直接发送给使用者，避免依赖 GitHub 下载。使用者也可安装本地版并选择智谱；国内模型仍需有效密钥、免费额度和可用网络。录像只能展示结果，不能替代交互使用。

Build a source-only ZIP with `python scripts/package.py`. It uses an explicit file allowlist, excluding keys, environments and course PDFs.

## Connection diagnosis

Gemini 2.5 names are valid, but Google restricts access for projects that have not used them previously. New projects default to `gemini-3.5-flash-lite`; `gemini-3.1-flash-lite` is another vetted free-tier choice. Legacy 2.5 options remain selectable for eligible projects. Use **Check available models** to query the model list with your current key; only the project's vetted text-generation models are displayed. Model-list access does not prove generation quota or billing eligibility. See [Google's current access notice](https://ai.google.dev/gemini-api/docs/deprecations).

A Gemini HTTP 404 can indicate unavailable model/resource; the connection test checks model availability before generation. A GLM HTTP 401 means authentication was rejected and is not fixed by renaming the model. This adapter uses the domestic `open.bigmodel.cn` endpoint and keys issued at `bigmodel.cn`, not international `z.ai` or a separate coding-plan endpoint. Paste the complete API key without `Bearer`, surrounding quotes or line breaks. Errors display provider/model, HTTP status and a bounded numeric diagnostic code where supplied, never the upstream error message or your key. Do not publish account identifiers or raw provider error bodies.

## Progressive welcome and compact workbench

First visit shows only an immersive provider selection and setup area. Gemini and GLM cards select the provider and open configuration; OpenRouter remains an optional alternative. Confirming a configured model unlocks the workbench through a skippable 1.05-second local card-to-status transition. The welcome never repeats on ordinary reruns or starting another inquiry.

The main-page **Model settings** panel contains the service, model, visitor key and connection test. On first visit, confirm **Use Gemini / GLM / OpenRouter** to continue with configured developer keys. This confirmation sends no API request. A successful connection test also confirms the current configuration; changing service, model or key invalidates confirmation. Sidebar contains language and scope information.

A 260px interactive right-hand journey tracks **Choose model → Choose situation → Start conversation**. It is driven by confirmed configuration, selected/typed situation and valid conversation responses. It stays in progress during inquiry; a single answer does not certify completion. On narrow screens, the journey becomes an in-flow horizontal strip. Clicking a step focuses its region; returning to situations preserves the current conversation.

Folder cards use local Streamlit Custom Components v2. Hover or keyboard focus previews details without a Python rerun or model request; moving into the details keeps the preview open, and leaving closes it after 120ms. Click/Enter selects an editable draft. Touch users have a separate Preview control. Details use safe text nodes; component payloads contain no API keys. One-shot triggers prevent replayed selections.

**Choose another situation** and **New conversation** appear only after a valid conversation starts:
- Choose another situation opens a pending selection while preserving the current conversation and unsent reply. Cancel restores them. A valid first reply for the new situation commits the replacement; network or output errors preserve both the old conversation and new draft.
- New conversation clears messages, notebook, briefing, consent and execution state, while retaining the initial situation and model configuration. Custom situations retain their original first user message. Download records before restarting.
- Model switches preserve conversation and request counters. Changing service/model resets sending consent.

Conversation, notebook and review briefing share tabs. **Execution details**, initially collapsed, retains real Input check → Model request → Output validation → Save result events. Failed requests expand it automatically and preserve the input. Save means current-session memory, not disk. Provider records show the actual model and fallback used.

Each assistant question has a browser-only **Copy** action. **Regenerate last question** consumes a model request and validates a replacement before updating the latest question and provenance; it preserves earlier turns, the latest user answer and your unsent draft. Failure preserves the original response. A narrow validation guard rejects observed “unknown reviewer → nobody reviewed” presuppositions; it is not a comprehensive factuality check. **Help me respond** fills editable response starters without sending them or inventing facts. Revoking sending consent or changing fallback services blocks further calls until consent is renewed.

Refresh recovery uses an opaque capability in tab `sessionStorage`, with inquiry snapshots in a bounded server-memory cache (two-hour inactivity timeout, at most 128 workspaces). The snapshot contains inquiry data, public provider/model/language preferences and request count; **no API keys, consent or connection signature**. A recovered workbench requires model confirmation again; visitor keys must be re-entered. No inquiry text is stored in the browser, on disk or in a URL. Process restarts, expiry and capacity eviction can erase recovery; download is the durable backup. Closing the tab ends access to its token.

Animations are original local CSS/Web Animations inspired by Hairline, GSAP timeline sequencing, Motion, Anime.js and AutoAnimate; no React, Node build, external scripts or background animation is required. `prefers-reduced-motion` removes motion. Component focus and local preview state survive unrelated reruns. See [notices](THIRD_PARTY_NOTICES.md).

## Local typography

Noto Sans SC variable-font WOFF2 subsets are bundled under `static/fonts/` with the SIL Open Font License. Unicode-range loading retrieves only needed subsets; `font-display: swap` and system fallbacks keep text readable while loading. English and Chinese use one font family, with no Google Fonts/CDN requests. Streamlit static serving is enabled in the checked-in configuration. Keep static files and license files in deployments and portable ZIPs.

Font preparation is a development-only step: `scripts/build_fonts.py` records the official source and produces the committed subsets. Running the app needs neither fontTools nor Brotli. See the font manifest for provenance and artifact sizes.

## Use and scope

1. Choose English or 中文, open Model settings if needed, and confirm the configured service.
2. Type your own fictional/anonymized situation, or load and edit an optional example. Hover previews; click selects. Loading a case never submits it.
3. Confirm sharing with the selected service(s); send and answer the follow-up. Unknown facts can remain unknown.
4. After one follow-up answer, prepare a human-review briefing or download the conversation. The notebook quotes user statements, not verified audit evidence.

The prompt focuses on objectivity, relevant facts, pressures, conflicting information and independent review. A small state manager retains context, validates the response and records provider/model provenance. It is not a fixed branching quiz or a trained custom model. It cannot certify compliance, replace professional judgment or give an audit opinion. Validation rejects malformed answers and some premature verdicts, but cannot prove that every valid-looking question is neutral, accurate or free of bias. Exact quote matching cannot prove completeness or preserve every contextual nuance; read the full transcript and check original evidence.

The app does not intentionally persist conversations to disk. Provider policies still apply. Download before resetting/leaving. Exported user/model text is untrusted; read it as text and do not follow embedded links/instructions automatically.

## Development

```sh
python -m unittest discover -s tests -v
```

`inquiry/core.py`: state, prompt and response checks. `inquiry/providers.py`: HTTP adapters and cost guards. `inquiry/examples.py`: optional scenarios. `inquiry/ui_state.py`: navigation and transactional scenario switching. `inquiry/resume.py`: bounded process-memory refresh recovery. `inquiry/components.py` and `frontend/`: local v2 components. `inquiry/presentation.py`: compact local style. `app.py`: UI and session-only credentials. Tests use fake responses; passing them is **not** evidence of live provider quality or mainland reachability.

## Official references

Pricing and access should be rechecked before deployment:

- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [regional availability](https://ai.google.dev/gemini-api/docs/available-regions)
- [OpenRouter free variants](https://openrouter.ai/docs/guides/routing/model-variants/free), [free router](https://openrouter.ai/openrouter/free)
- [GLM-4.7-Flash API](https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash)
- [智谱 model overview](https://docs.bigmodel.cn/cn/guide/start/model-overview)
- [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
