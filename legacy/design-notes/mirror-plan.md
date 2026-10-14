# Identical frontend mirror and bounded public demo

Goal: preserve the visual experience and Python inquiry engine, update portfolio links, and remove the need to share private developer access credentials.

1. Publish README and repository homepage linking to the current React release. Preserve legacy code and deployment.
2. Add opt-in DEMO_ACCESS_ENABLED=false default. When enabled, server-owned keys may be used without ACCESS_CODE, still requiring free eligibility and global atomic quotas. The private code remains server-only; no prefilled browser secret. Test the opt-in boundary and visitor-key precedence.
3. Host the exact production static bundle on EdgeOne with a fixed upstream /api proxy. Same-origin browser routes and cookies remain valid. Verify request origin before rewriting to the fixed upstream; forward only the known API routes, bounded body, no caching, no logging, no arbitrary URL target.
4. Proxy does not move LLM calls or change Agent validation. It depends on the existing Cloudflare backend, so verify server-to-server availability and CPU budget. This addresses browser domain reachability, not a fully independent backend outage.
5. Deploy only a free registered account project. Confirm static assets, session creation, model test, inquiry SSE, cookies/export and mainland no-VPN access. If proxy runtime streaming/upstream constraints fail, use a full Python mirror adapter without changing the frontend.

No private credential is copied into the mirror, frontend source or public repository. Mainland reachability requires user network evidence. No paid plan, purchased domain or guessed mirror URL.
