# Mirror acceptance — 2026-10-14

Primary: https://inquire-experience.inquire-ethics-lab.workers.dev/

Alternative: https://app.inquire-ethics.dynv6.net/

## Passed

- EdgeOne Makers service dashboard explicitly shows Free; no paid upgrade or add-on was selected.
- Free dynv6 subdomain, verified TXT ownership, active CNAME and deployed Free Certificate. Automatic certificate renewal and Force HTTPS are enabled.
- Normal TLS validation, API health HTTP 200, local font CSS HTTP 200 and identical React JavaScript SHA-256 compared with the primary deployment.
- Same-origin API relay: valid anonymous sessions, host-local HttpOnly/Secure cookies, streamed stage/error events and sanitized error handling. No frontend keys or private access code.
- Owner reports mainland page access without a VPN. This is one actual network observation, not an all-ISP availability guarantee.
- Default mirror hostname: actual GLM connection and one accepted contextual inquiry. Export downloaded and checked: only accepted user/assistant messages and model provenance, with no failed draft appended.
- Browser scenario switch retained the accepted conversation; cancellation restored the previous unsent draft. New conversation cleared accepted messages and consent while retaining initial fictional situation, selected model and request count.
- 21 Python API tests, 21 frontend/proxy/localization tests and TypeScript type checking passed.

## Earlier provider limitations

- A subsequent GLM request returned provider HTTP 429. The owner identifies current GLM server capacity as the cause. No quota-exhaustion diagnosis is asserted. The original free-only release had no paid fallback; the subsequent developer-funded backup is described below.
- Live Gemini inquiry through the custom mirror returned the provider's unsupported-source-region HTTP 400 classification. It did not commit an empty or invalid answer. No region bypass was introduced.
- The original free-only release did not pass sustained multi-turn dialogue under these provider conditions. A subsequent real backup acceptance passed through the mirror; a mainland no-VPN user transcript test is still distinct from the owner's earlier page-access confirmation.
- English interface checks covered welcome, configuration, error rendering, live language switching, execution stages, statement headings, empty states and review. This browser check used an explicitly marked local fixture, not a live model. User quotations were preserved without translation.
- Automated duplicate GLM testing was stopped after approval review rejected unnecessary repeated requests under the observed capacity limitation.

## Live DeepSeek backup acceptance — 2026-10-14

The developer privately configured `DEEPSEEK_API_KEY` in Cloudflare Secrets. The public configuration reported backup availability without exposing its value. A GLM connection test briefly recovered; an actual fictional inquiry then returned the recognized server-capacity error (HTTP 429) and granted session-bound backup eligibility.

Two intentional DeepSeek requests through https://app.inquire-ethics.dynv6.net/ returned contextual questions and passed the existing question/quotation validation. Both streamed real input/request/validate/commit stages and committed model provenance as DeepSeek. Restoring the session reproduced the accepted transcript. Markdown export included the fictional user text and provider provenance; the two-turn human-review packet returned successfully.

Only two DeepSeek calls were made. No automatic retry, top-up, key inspection or provider-region bypass was used. This verifies the live backend/relay workflow; the fee amount was not retrieved or estimated. The current automated suite contains 30 Python API tests and 23 frontend/state/proxy/localization tests, including 15-turn recovery and backup request limits.

