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

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`. Fill in **one** API key privately. Never commit the real file. Environment variables with the same names also work and take precedence. A `.env` file is not loaded automatically. No API key is bundled, and the app does not simulate a live model when unconfigured.

中文：先安装 Python，再按上面步骤安装依赖。把配置模板复制为 `.streamlit/secrets.toml`，只填写你要用的服务。使用者打开已经配置好的在线版无需安装；本地版仍需 Python、依赖、有效密钥和访问模型服务的网络。

## Model choices and costs

| Service | Default | Setup / limits |
|---|---|---|
| Google Gemini | `gemini-2.5-flash-lite` | Eligible free-tier project; set `GEMINI_FREE_TIER_CONFIRMED = "true"` only after checking the account. Regional restrictions apply. |
| OpenRouter | `openrouter/free` | Free-model router; actual model varies and is recorded. A specific `vendor/model:free` ID can be used for more repeatable evaluation. |
| 智谱 GLM | `glm-4.7-flash` | Domestic alternative. Confirm current free eligibility, then set `ZHIPU_FREE_TIER_CONFIRMED = "true"`. |

Only these Gemini/GLM models and OpenRouter free routes are allowed. No paid-model fallback, automatic retry loop, training, or server purchase is needed. **Zero cost cannot be guaranteed by code:** provider terms, account billing, quotas and availability can change. Do not enable paid billing to bypass a limit. Free services may process data for product improvement; use fictional or anonymized scenarios only.

Optional fallback is off by default. Enabling it sends the conversation to the explicitly selected second service after a network/quota/service failure. It does not retry authentication failures or malformed model output. Requests are capped at 24 per browser session, 40/hour and 150/day per running server process, 12 dialogue turns, 4,000 characters per input and 1,600 output tokens per call. Restarting a process resets its counters: these are shared-demo safeguards, not provider billing controls. Set `ACCESS_CODE` for a shared shared-demo deployment; it is a simple gate, not full user authentication.

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

`inquiry/core.py`: state, prompt and response checks. `inquiry/providers.py`: HTTP adapters and cost guards. `inquiry/examples.py`: optional scenarios. `app.py`: UI. Tests use fake responses; passing them is **not** evidence of live provider quality or mainland reachability.

## Official references

Pricing and access should be rechecked before deployment:

- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [regional availability](https://ai.google.dev/gemini-api/docs/available-regions)
- [OpenRouter free variants](https://openrouter.ai/docs/guides/routing/model-variants/free), [free router](https://openrouter.ai/openrouter/free)
- [智谱 model overview](https://docs.bigmodel.cn/cn/guide/start/model-overview)
- [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
