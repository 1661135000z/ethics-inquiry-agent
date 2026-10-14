# Inquire · Ethics Inquiry Agent

An interactive audit-ethics assistant that asks a better question before judgment. Built with **React, TypeScript, GSAP and Python**; focused on **objectivity**, contextual follow-up questions and human review.

**[Open the live app](https://inquire-experience.inquire-ethics-lab.workers.dev/) · [Open the mainland mirror](https://app.inquire-ethics.dynv6.net/) · [User guide](docs/user-guide.md) · [Architecture](docs/architecture.md)**

The mirror runs the same interface and relays API requests to the same backend. The public demonstration uses server-side credentials: visitors do not need an account, API key or access code. Network availability and model capacity can vary.

## What it does

- A progressive welcome → model selection → situation → conversation journey, with GSAP transitions, light/dark themes, bilingual controls and locally bundled Chinese fonts.
- Your own situation, or four optional editable examples. Hover/focus previews stay in the browser; only explicit submissions call the agent.
- One contextual question per turn about roles, interests, pressure, evidence or independent review. The agent preserves uncertainty and avoids immediate ethical verdicts.
- Gemini and GLM model selection; optional personal keys held only in page memory. **DeepSeek appears only after a genuine GLM service failure**, requires a manual switch and is funded by the developer.
- Transactional conversations: invalid replies or failed requests do not overwrite accepted records. Switching situations, cancelling, restarting and regenerating retain the appropriate drafts and settings.
- Exact user quotations, provider provenance, observable execution stages, Markdown export and an HTML human-review packet after at least two accepted turns.
- Refresh recovery, keyboard/touch support and reduced-motion support. Expired server sessions retain a read-only browser copy when available.

The assistant is an inquiry aid, not an auditor or a source of verified facts. It does not train a model, browse standards, make audit opinions or show hidden model reasoning. Execution events stream over SSE; model text is displayed **after complete JSON validation**, rather than raw token streaming.

## Run locally

Use **Node 22.22+**, **pnpm 11.25** and **Python 3.12+** for the native server. Python Workers deployment separately requires Python 3.13+.

```sh
pnpm install --frozen-lockfile
pnpm build
python -m venv .api-venv
# macOS / Linux:
source .api-venv/bin/activate
# Windows PowerShell: .api-venv\Scripts\Activate.ps1
python -m pip install -r requirements-api.txt
cp .env.example .env
# Fill .env privately, then:
python -m uvicorn edge.local:app --host 127.0.0.1 --port 8788
```

Open **http://127.0.0.1:8788**. For live UI editing, leave the Python server running and run `pnpm dev` in a second terminal; Vite proxies `/api` to port 8788. The native server uses process memory; restarting it loses server snapshots. Cloudflare uses D1.

## Credentials and demonstration limits

Put developer credentials in `.env` locally or **Cloudflare Workers Secrets** online. Never put them in Vite variables, React code, GitHub, exports or a filled example file. `.env.example` documents the variables. Enable free-tier flags only after checking your account's eligibility; provider pricing and quota are external to this app.

- `GEMINI_API_KEY`, `ZHIPU_API_KEY`: developer model credentials.
- `GEMINI_FREE_TIER_CONFIRMED`, `ZHIPU_FREE_TIER_CONFIRMED`: eligibility flags.
- `DEMO_ACCESS_ENABLED=true`: explicitly allows the bounded public demo without an access code. Set false and configure `ACCESS_CODE` for private access.
- `DEEPSEEK_API_KEY`: optional **paid** backup credential. It is not a free API; visitors are not charged by the app.

A visitor's personal key overrides the developer key for that request and is not persisted. Changing provider does not silently send content to a second service.

Gemini/GLM inquiries allow up to **12 accepted turns**. DeepSeek mode allows up to **10 accepted turns total in the current inquiry**, including earlier turns. DeepSeek also has a **10-request session allowance** and a **60-request shared daily allowance**; failed calls and regeneration consume request attempts. Starting a new inquiry resets its conversation counter, preserves the 24-attempt lineage counter, returns DeepSeek users to GLM, and requires a fresh GLM failure to offer the backup again. Shared limits remain **40 attempts/hour and 150/day**. These request caps are not a monetary spending guarantee. See [limits and troubleshooting](docs/user-guide.md).

## Source layout

```text
web/                Current React UI, styles, motion, state and frontend tests
edge/               Python API, provider calls, policy and transactional storage
inquiry/            Shared objectivity prompt, validation and review/export logic
edge-functions/     Fixed-origin EdgeOne API relay
tests/              Current Python API tests
scripts/            Worker preparation and portable source packaging
docs/               Current usage, architecture, deployment and verification
legacy/             Archived Streamlit release and historical design notes
```

See [editing the product](docs/editing.md) for exactly which files control the page and agent behavior. The former Streamlit app is self-contained in [`legacy/streamlit/`](legacy/streamlit/README.md); it is not the default entrypoint. No teaching materials, identities or filled credentials belong in this repository.

## Check and deploy

```sh
python -m unittest discover -s tests -v
pnpm test
pnpm build
python scripts/package_react.py
```

The ZIP at `dist/inquire-react-source.zip` includes the built UI and native Python server, excluding private configuration, dependencies and the archive. GitHub Actions checks the current application on `main` and the development branch. [Deployment instructions](docs/deployment.md) cover Cloudflare and the identical-interface EdgeOne mirror. Deployments do not automatically upgrade a paid plan.

## Licenses and attribution

Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Local Noto Sans SC subsets retain the SIL Open Font License. GSAP follows its own Standard License. No Base44 template source or assets were copied.
