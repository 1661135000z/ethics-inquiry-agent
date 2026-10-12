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

**Visitor setup:** open **AI Model Settings → Use your own API key**, select a service/model, enter the key in the password field and confirm free eligibility. A nonempty visitor key takes priority for that service; an empty field uses the developer configuration. Keys remain only in that Streamlit session's memory, survive service switching and are removed by **Clear session keys** or session expiry. This app does not write keys to files, logs, exports, GitHub, URLs or shared caches. Browser password masking is visual protection; enter keys only on a trusted HTTPS deployment. A fresh browser session does not inherit another visitor's credentials.

**Test Connection** sends one small fictional audit-ethics case through the actual `Session.submit` workflow, including the objectivity prompt, JSON parsing, question-only and quote checks. It consumes one request, does not use the user's case, does not append to the formal conversation, and never automatically falls back to another service. A success badge applies to the current service/key/model configuration; changing it invalidates the badge. A successful test does not establish the quality of all future questions.

中文：在侧栏选择 Gemini 或智谱 GLM，展开“使用自己的 API Key”，输入密钥并勾选免费档确认，点击“测试连接”。不输入自己的密钥时使用开发者配置。请勿把密钥放入聊天内容；无需把密钥发给项目维护者。Gemini 连接失败时可手动切换智谱，原有对话保留。服务提供方仍按自身政策处理请求，应用不能核实账户计费状态。

## Model choices and costs

| Service | Default | Setup / limits |
|---|---|---|
| Google Gemini | `gemini-2.5-flash-lite` | Eligible free-tier project; set `GEMINI_FREE_TIER_CONFIRMED = "true"` only after checking the account. Regional restrictions apply. |
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

## Interface and execution states

- **Riffle-inspired case selection:** native Streamlit buttons are styled as folder cards; hovering lifts one and slightly shifts neighbors. Selected cards have a checkmark and accent border. Keyboard and touch activation use the same Python callback; selecting a case fills an editable draft without sending it. Choosing your own case restores a blank starting point.
- **Exploded-inspired details:** expand Case details to view context, inquiry and human review in layers. Hover or keyboard focus on the expander separates them. All information stays readable without motion.
- **Relay-inspired execution:** real backend events drive Input check → Model request → Output validation → Save result. Earlier stages are complete only when execution has advanced past them. Errors mark the current stage and preserve the draft; no fake tool calls or timers imply progress. Save means commit to current session memory, not disk. The provider records still show the actual model used.
- A short settling header graphic and subtle active-stage pulse provide restrained feedback. There are no autoplay background loops, external fonts/CDNs, Node build or front-end framework. Reduced-motion preferences disable transitions; mobile layouts wrap cards. See [motion attribution](THIRD_PARTY_NOTICES.md).

The stylesheet uses Streamlit's container keys and DOM test identifiers. Dependencies are pinned; check visual behavior before upgrading Streamlit. Core functionality remains native Python callbacks even if CSS is unavailable.

## Use and scope

1. Choose English or 中文 and a configured service.
2. Type your own fictional/anonymized situation, or load and edit an optional example. Loading a case never submits it.
3. Confirm sharing with the selected service(s); send and answer the follow-up. Unknown facts can remain unknown.
4. After one follow-up answer, prepare a human-review briefing or download the conversation. The notebook quotes user statements, not verified audit evidence.

The prompt focuses on objectivity, relevant facts, pressures, conflicting information and independent review. A small state manager retains context, validates the response and records provider/model provenance. It is not a fixed branching quiz or a trained custom model. It cannot certify compliance, replace professional judgment or give an audit opinion. Validation rejects malformed answers and some premature verdicts, but cannot prove that every valid-looking question is neutral, accurate or free of bias. Exact quote matching cannot prove completeness or preserve every contextual nuance; read the full transcript and check original evidence.

The app does not intentionally persist conversations to disk. Provider policies still apply. Download before resetting/leaving. Exported user/model text is untrusted; read it as text and do not follow embedded links/instructions automatically.

## Development

```sh
python -m unittest discover -s tests -v
```

`inquiry/core.py`: state, prompt and response checks. `inquiry/providers.py`: HTTP adapters and cost guards. `inquiry/examples.py`: optional scenarios. `inquiry/presentation.py`: local motion/style and escaped details. `app.py`: UI and session-only credentials. Tests use fake responses; passing them is **not** evidence of live provider quality or mainland reachability.

## Official references

Pricing and access should be rechecked before deployment:

- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [regional availability](https://ai.google.dev/gemini-api/docs/available-regions)
- [OpenRouter free variants](https://openrouter.ai/docs/guides/routing/model-variants/free), [free router](https://openrouter.ai/openrouter/free)
- [GLM-4.7-Flash API](https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash)
- [智谱 model overview](https://docs.bigmodel.cn/cn/guide/start/model-overview)
- [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
