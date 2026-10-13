# React experience

The independent React/Vite/GSAP interface shares the existing pure Python inquiry engine. The original Streamlit entrypoint remains available. No original teaching documents or personal identifiers are included.

## Local run

Use Node 22+ and Python 3.12. Install pnpm through its official instructions, then:

```sh
pnpm install --frozen-lockfile
pnpm build
python -m venv .api-venv
source .api-venv/bin/activate
# Windows: .api-venv\Scripts\Activate.ps1
python -m pip install -r requirements-api.txt
python -m uvicorn edge.local:app --host 127.0.0.1 --port 8788
```

Open `http://127.0.0.1:8788`. For frontend development, `pnpm dev` proxies `/api` to this Python server. The downloadable React backup includes `web/dist`, so running the Python server from that ZIP needs no Node build.

Native recovery is process memory: restarting the server loses its snapshots. Cloud recovery uses D1. Both expire access after two hours of inactivity. The browser keeps non-secret workspace drafts and transcripts in **tab sessionStorage**, not keys or consent. Close the tab to discard that local cache; exports are the durable backup.

## Private configuration

Copy `.env.example` to `.env` for the native server. For Cloudflare use Worker **Settings → Variables and Secrets**; never add filled files to GitHub. Streamlit Secrets are separate and are not automatically transferred.

```dotenv
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FREE_TIER_CONFIRMED=false
ZHIPU_API_KEY=
ZHIPU_MODEL=glm-4.7-flash
ZHIPU_FREE_TIER_CONFIRMED=false
ACCESS_CODE=
```

Create a private access code to protect developer-funded calls. Only set a free-confirmation flag to `true` after checking that account's current free eligibility. The API refuses unapproved models, but does not control changes in provider pricing; do not enable paid billing for this demo.

Visitor keys override the developer key for that request only. Password fields stay in page memory and clear on refresh; they are sent over HTTPS to the Python backend, then to the selected provider. They are not written to D1, exports, browser storage, bundles or application logs. Provider switching never sends data automatically to a second service. A new selection requires fresh sending consent. Connection testing sends only a fictional audit example and does not modify the user's dialogue.

## Cloudflare deployment

Python Worker tooling requires Python 3.13+ and `uv`; install official `workers-py`. Authenticate Wrangler through its official browser flow. Use a dedicated free D1 database and replace the `database_id` in `wrangler.jsonc` with **your own** ID.

```sh
pnpm build
python scripts/prepare_worker.py
pnpm exec wrangler d1 execute inquire-sessions --remote --file edge/schema.sql
cd .inquire-ethics-lab
pywrangler deploy
```

The generated isolated project excludes Streamlit dependencies and development environments. API routes run Python; static React assets use the asset binding. Set private secrets after deployment. This branch does not replace the existing Community Cloud release.

No automatic paid upgrade. The service caps 12 accepted turns, 24 attempts per conversation lineage, 40 attempts/hour and 150/day per deployment. Connection checks count too. Failed requests count toward budgets. At most 128 active sessions. D1 atomically reserves attempts and commits only validated responses; duplicate request IDs cannot call a model again. Free platform limits still apply independently. This is a small demonstration, not an abuse-resistant public production service.

Static loading, Python initialization and model inference are different delays. Deployment reported 1,151ms Worker startup; this is not CPU/request measurement. Complete Gemini/GLM calls and real CPU metrics must pass before asserting free-tier suitability. Global Cloudflare access is not guaranteed from mainland networks; test with the actual viewer's network. Local native Python and the preserved Streamlit release remain alternatives.

## Interaction and inquiry contract

Welcome shows only model selection. Inline credentials lead to the folder workspace through a GSAP shared-element transition. Local hover/focus previews do not call Python; touch has a separate preview action. Light/dark themes, Chinese font subsets and animation assets are bundled locally. Reduced motion removes transitions; there is no search palette or skip button.

The journey derives from real UI state. Switching situations preserves the accepted conversation and unsent answer until a validated first reply commits the replacement. Cancel restores the draft. New conversation keeps the original situation and model preferences while clearing consent and records. Regeneration replaces only the latest validated question and preserves the unsent answer.

The agent asks one contextual question per turn about objectivity, preserves uncertainty and accepts only exact user quotations. It does not make an ethical verdict or audit opinion. Notebook entries are **user statements**, not independently verified evidence. Review packets require at least two turns and support human review.

SSE streams real input/request/validation/commit stage events, followed by one **fully validated** reply. It intentionally does not display raw provider token streams, hidden reasoning or unvalidated partial JSON. No invented tool calls are shown.

## Verification

```sh
python -m unittest discover -s tests_next -v
pnpm test
pnpm build
# Original UI tests require the original requirements.txt dependencies:
python -m unittest discover -s tests
```

Local simulated browser QA is explicitly labelled; it is not proof of live model connectivity. Keep endpoint and CPU checks distinct from mock transport tests.
