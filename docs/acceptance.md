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


## Delivery organisation and current backup limit

The React application is the default root implementation; Streamlit and superseded planning notes are archived under `legacy/`. Current Python tests are under `tests/`. The owner reduced the DeepSeek limit from fifteen to **ten** accepted turns and ten paid attempts per session; the earlier live two-turn acceptance remains historical evidence, not a fresh ten-turn test. Cached older fifteen-turn histories remain readable.

## Lens experience verification — 2026-10-15

This UI release preserves provider endpoints, objectivity instructions and existing cost limits. A local browser fixture uses clearly labelled fictional model replies; these UI checks are not new live-provider claims.

- 36 frontend tests, 30 Python API tests and TypeScript checking passed. Regression coverage includes safe archive sanitisation/export, exact source matching, pending failure, real-stage progress and animation exceptions that must still commit accepted state once.
- Browser workflow passed: configured model connection, welcome-to-situation transition cleanup, two accepted turns, visible pending input and stage updates, source navigation, unread/back-to-latest, dossier preview and HTML download.
- Explicit archive save, read-only inspection, rename, delete/undo and Markdown export passed. Opening/closing history retained the unsent draft and request count. No extra model requests were made by archive or dossier operations.
- Cancelling situation selection restored the previous unsent draft. New inquiry cleared accepted turns and retained initial context and the inherited request-attempt count.
- Desktop dark and 390px mobile light/English layouts were visually checked, including dossier and history sheet. English controls/privacy text remain English; original Chinese quotations remain unchanged.
- Independent review identified animation-failure recovery, archive-print isolation and printable source references; all three were repaired. Print CSS and static references are checked structurally; physical printing and all browser print engines are not claimed as tested.
- No API credentials, user histories, original teaching materials or private Word manual are included in the public source. The Word user guide is updated separately with a five-page visual check.

### Published release checks

GitHub commit `dae1689` passed the React and Python checks workflow. Cloudflare published Worker version `78956eec-7d6a-4b5b-bce6-cb0615f7c2f5`. The primary browser loaded the new assets, verified the developer Gemini configuration and accepted one real fictional inquiry with source-linked statements. No paid backup call was made in this release check.

The EdgeOne console shows the same commit Running and the account plan Free. The custom mirror returns the new page; JavaScript, CSS and font CSS match the local release by SHA-256. Its `/api/health` returns HTTP 200 with the Python inquiry API ready. Browser navigation to the mirror temporarily encountered a connection closure in this test environment, while normal TLS command-line checks succeeded. The owner previously confirmed mainland page access; this release does not claim a new no-VPN mainland model transcript.
