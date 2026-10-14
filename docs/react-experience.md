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

By default create a private access code to protect developer-funded calls. The live demonstration explicitly opts into `DEMO_ACCESS_ENABLED=true`: configured eligible provider keys can be used without a visitor key or access code, while all atomic request budgets remain active. Set this flag to false to restore private-code access. The private code is never prefilled in a browser. Only set a free-confirmation flag to `true` after checking that account's current free eligibility. The API refuses unapproved models, but does not control changes in provider pricing; do not enable paid billing for this demo.

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

Static loading, Python initialization and model inference are different delays. Deployment reported 1,151ms Worker startup; this is not CPU/request measurement. Both configured providers have completed live inquiries, including continuing one conversation across providers. The 2026-10-14 dashboard sample across mixed API routes showed CPU P50 25.38ms, P90 54.4ms and P99 55.99ms, with zero reported CPU/memory-limit errors; memory P99 was 58.66MB. This small, delayed aggregate is not per-inquiry profiling. It exceeds the published 10ms free CPU baseline, so long-term free-tier reliability is **not established**. Do not upgrade billing automatically; use the included native Python backup if resource errors occur. See https://developers.cloudflare.com/workers/platform/limits/. Global Cloudflare access is not guaranteed from mainland networks; test with the actual viewer's network. Local native Python and the preserved Streamlit release remain alternatives.

## Interaction and inquiry contract

Welcome shows only model selection. An explicit saved-configuration/personal-key choice separates developer credentials from provider keys. When bounded public demo mode is enabled, selecting a configured model connects automatically without displaying a private access-code field. Inline credentials lead to an inquiry studio through a GSAP shared-element transition. The studio shares the welcome page’s centered typography, ambient contours and nested surfaces. The primary editable context sits beside optional expandable examples; local hover/focus previews do not call Python, and touch has a separate preview action. Light/dark themes, Chinese font subsets and animation assets are bundled locally. Reduced motion removes transitions; there is no search palette or skip button.

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

Gemini HTTP400 is classified from recognized error categories without echoing provider bodies: unsupported request location, free-tier region, rejected key, invalid parameters or unmet prerequisites. Do not automatically enable billing or retry a client error. Switch to GLM when the source region is unsupported.

Local simulated browser QA is explicitly labelled; it is not proof of live model connectivity. Keep endpoint and CPU checks distinct from mock transport tests.

## Release acceptance — 2026-10-14

- Live Gemini: two contextual follow-up turns accepted and persisted in D1. Live GLM: connection and continuation of the same conversation accepted. No private credential was read or included in evidence.
- Live cancellation and refresh: accepted transcript and unsent draft retained; refresh clears credential verification and consent without replaying welcome. A two-turn human review HTML downloaded successfully.
- Local simulated 390px touch QA: preview does not select a scenario, selection populates the editable draft, regeneration retains unsent input, cancellation restores it, and light-theme dialogue has no horizontal overflow. Pointer hover was inspected in code; no automated pointer-hover claim is made.
- Fixed narrow-screen journey connectors crossing step labels; lines now occupy dedicated gaps. The final CSS repair and configuration loading/error retry are deployed. An approval-service outage delayed publication temporarily; the normal approval flow recovered before deployment.
- Mainland access without VPN remains unmeasured. SSE shows real execution stages and only validated complete replies, not token streaming. GitHub checks package the native backup; automatic Cloudflare deployment is not configured.

- Expired backend recovery now preserves cached accepted dialogue as a read-only archive, retains the unsent draft, and offers a local Markdown download. Starting a new inquiry releases archive mode. A restarted native fixture proved this in the browser and produced a complete cached export. Closing the tab still discards its sessionStorage.
- Current frontend state suite: 14 tests, including the expired-session regression observed failing before the fix.

## Same-interface mirror

`edgeone.json` builds the exact React frontend. `edge-functions/api/[[default]].js` relays only known API routes to the fixed existing Python Worker; no developer key or private code is copied. It rejects foreign POST origins and bodies over 20,000 bytes, preserves host-local session cookies, passes SSE without buffering, and disables API caching. The mirror shares the backend quota and depends on its availability. A redirect would not solve blocked browser access; this relay does not redirect the visitor.

Deployment requires a registered free EdgeOne project and verification of server-to-server upstream reachability, response streaming and mainland no-VPN access. A mirror is not considered live until these checks pass; no invented hostname is listed. Existing Cloudflare CPU/free-tier limits remain.

Mirror deployment acceptance (2026-10-14): EdgeOne project `inquire-mirror`, source branch `feat/react-experience`, confirmed **Free** in the service dashboard. The default `edgeone.dev` hostname is rejected with HTTP 401 on mainland networks by the platform's region policy, so it is not a mainland delivery link. The free custom hostname https://app.inquire-ethics.dynv6.net/ has passed ownership verification and its CNAME is active. Free HTTPS passed normal certificate validation and the health endpoint returned HTTP 200. The owner confirmed mainland page access without a VPN, but GLM returned provider HTTP 429; sustained mainland dialogue is not yet verified.

The platform preinstalls Node 22.11; install/build commands use official npm Node 22.22 and pnpm 11.25 packages without changing application dependencies. Health/config/session forwarding and a real GLM connection plus first inquiry passed on the default hostname. A second inquiry returned provider HTTP 429; the accepted conversation and unsent draft remained intact. Request streams can contain ArrayBuffer chunks in EdgeOne, normalized before forwarding. SSE is passed through without buffering. On the custom hostname, normal TLS, local font CSS, API health/config, session creation and an identical frontend script SHA-256 passed; an inquiry error event was correctly preserved without committing an empty answer. No repeated automatic retries or paid fallback were introduced.

Cost boundary: no paid Tencent plan, certificate, purchased domain, storage add-on or extra agent service is enabled by this deployment. The proxy shares existing Cloudflare and model free quotas. A Free dashboard label is not a guarantee of unlimited availability; do not enable pay-as-you-go upgrades to address a 429. Review the provider console's rate/concurrency limits before accepting classroom traffic.

Final live check: Gemini through the custom mirror returned a sanitized unsupported-source-region error (HTTP 400); this is not a successful Gemini dialogue acceptance. The owner attributes GLM 429 to server capacity. See [full acceptance](migration/mirror-acceptance.md) for passed checks and external blockers.
