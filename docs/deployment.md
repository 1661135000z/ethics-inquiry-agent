# Deployment

## Cloudflare primary

Use your own Cloudflare account and free-plan resources; deployment tooling needs Python 3.13+, uv, workers-py and authenticated Wrangler. Replace the database ID in `wrangler.jsonc` when deploying to a different account.

```sh
pnpm build
pnpm exec wrangler d1 create inquire-sessions
# Put the returned ID in wrangler.jsonc, then initialize your database:
pnpm exec wrangler d1 execute inquire-sessions --remote --file edge/schema.sql
python scripts/prepare_worker.py
cd .inquire-ethics-lab
pywrangler deploy
```

For an existing deployment, reuse its database and secrets; do not create a replacement database on every release. The preparation script copies only runtime Python files into an isolated project and uses `web/dist` for assets. Add credentials privately under Workers → Settings → Variables and Secrets. Do not copy Streamlit Secrets; they belong to the archived app.

`DEMO_ACCESS_ENABLED=true` is an explicit public-demo choice; use false plus a secret `ACCESS_CODE` for private installations. Store API keys as Secrets. Free eligibility flags are account-specific. DeepSeek is optional and paid, protected by its backend failure gate and request limits.

## Same-interface EdgeOne mirror

`edgeone.json` builds the same `web/` source. `edge-functions/api/[[default]].js` relays known API paths to the fixed Cloudflare origin without revealing keys. Set its fixed upstream when deploying your own backend. Preserve POST-origin checks, bounded bodies, cookies and SSE handling.

The official npm runtime wrapper in the build commands supplies a Node version compatible with pnpm; the platform's older bundled Node is insufficient. Keep the project on its free plan. The source branch must contain the same root configuration and frontend as `main`.

The default `edgeone.dev` domain can reject mainland requests. The current mirror uses a verified custom subdomain and a free HTTPS certificate. A custom domain does not guarantee all networks will work. Test asset loading, backend connectivity and a complete fictional inquiry on the target network; a successful static page alone is insufficient.

## Checks and portable copy

GitHub Actions verifies the frontend, Python API and portable package; it is not automatic Cloudflare deployment. EdgeOne's linked source branch builds automatically. Local `python scripts/package_react.py` creates a source ZIP with built frontend assets; run it only after `pnpm build`. It excludes secrets, installed dependencies and legacy files.

The Cloudflare free CPU baseline remains a practical risk for Python Workers: an earlier small aggregate sample exceeded the baseline, despite no recorded resource-limit errors at that time. No paid upgrade is automatic or authorised by these instructions. Provider inference latency, static asset loading and Worker startup are different measurements. The native Python server remains a portable fallback; the old Streamlit release is archived separately.
