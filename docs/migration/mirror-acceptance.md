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

## External blockers / not passed

- A subsequent GLM request returned provider HTTP 429. The owner identifies current GLM server capacity as the cause. No quota-exhaustion diagnosis is asserted and no paid fallback is enabled.
- Live Gemini inquiry through the custom mirror returned the provider's unsupported-source-region HTTP 400 classification. It did not commit an empty or invalid answer. No region bypass was introduced.
- Sustained multi-turn mainland dialogue is therefore not yet accepted, despite working page/API transport. Repeat live acceptance after provider capacity recovers or after a separately configured eligible domestic provider is added.
- English interface checks covered welcome, configuration, error rendering, live language switching, execution stages, statement headings, empty states and review. This browser check used an explicitly marked local fixture, not a live model. User quotations were preserved without translation.
- Automated duplicate GLM testing was stopped after approval review rejected unnecessary repeated requests under the observed capacity limitation.

