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

## Interactive clue radar — 2026-10-15

The decorative ellipse is replaced by five axes derived from accepted statement counts. The common count scale is labelled and expands in multiples of three; zero remains zero. This is neither a risk score nor a completeness measure. Category and axis hover/focus are linked, and activation opens the corresponding clue section without a model request. Count changes animate locally and respect reduced-motion preferences. Two geometry/count regression tests bring the frontend suite to 38 tests. Local fictional browser checks cover count updates and axis-to-notebook navigation; no live model call is required for this change.

## Guided experience and author credit — 2026-10-15

- 44 frontend tests, 30 Python API tests and TypeScript checking passed. No provider, billing, session-limit or core objectivity logic changed.
- The existing Inside Inquire sheet introduces the guide once after the first eligible successful model transition. Editing, settings, accepted conversations and prior viewing suppress automatic opening. Explicit guide completion focuses the composer; ordinary dismissal restores its invoking control.
- A fresh-context review identified focus stealing during settings edits and unconditional mobile keyboard activation. Both were repaired; the eligibility regression was checked failing before the fix and passing afterwards.
- Local browser checks use an explicitly marked simulated provider, with real request/validation/commit flow. They verify two accepted turns, bounded composer height, contextual question reference, home/resume preserving drafts and counts, no repeated guide, source-to-radar linkage and printable S01/S02 source references. These are not new live-provider acceptance claims.
- The read-only example reproduces the original two-turn export from 12 October 2026, with fictional input, original English wording and actual model provenance. It is clearly historical, costs no model request and leaves the current inquiry untouched.
- About and the footer include the owner's authorised name. About includes the authorised contact email, ACC305 course-design origin and third-party licence acknowledgement. This does not authorise publishing visitor identities or original teaching files.
- Desktop 1366px and mobile 390px layouts were checked, including the Chinese light-mode About sheet, with no horizontal page overflow. The separately delivered English Word guide retains its original five pages and adds a sixth page; all six rendered pages were visually checked.

## Evidence-led five-dimensional inquiry — 2026-10-15

This release changes the inquiry state and response contract, while keeping the existing visual identity, objectivity scope, provider credentials, paid backup gates and request limits.

- 54 frontend tests, 51 Python tests and TypeScript checking passed. State tests cover exact initial quotes, missing relationship information, separately supported pressure, multi-area updates, duplicate/nested quotations, uncertain reports, reopened coverage when newer uncertainty challenges an old claim, corrections and A→B→A restoration, malformed classifications, source turns, advice gating/staleness, legacy regeneration and safe persistence/export. These deterministic tests validate state handling; they do not establish general semantic classification accuracy.
- Each dimension has three distinct information needs. Source-supported reported facets drive coverage; uncertain reports remain visible but unresolved. A model performs contextual classification in the same request that chooses the follow-up. No separate call is made for typing, hover, language, source navigation, historical examples or brief display.
- Curated, exact-quote preset previews initialise the panel without an LLM call. A regression compares the bundled definitions and case data against the Python source. Custom/edited situations are semantically analysed on their first submission.
- Local browser verification uses an explicitly labelled simulated provider and the real service/state/validation/commit path. Selecting the friendship/fees example immediately showed the university relationship as partial; activating that dimension showed its source and missing stake/influence information before submission. A valid initial reply preserved those facts and highlighted its actual focus. Refresh preserved accepted records and required renewed connection verification.
- The historical example now has labelled Chinese translations and expandable original English. The existing modal has its own language switch; changing language on its second recorded turn retained that turn. Earlier live conversation messages remain in their original language. The modal close label now follows the current React language rather than a previous document-language effect.
- Independent review found five P2 issues: correction-cycle identity, sync regeneration of old observations, paid output cap, archived analysis export and unreassessed advice freshness. Each had a failing regression before repair; all passed afterwards. DeepSeek retains the original 1,600-output-token cap; Gemini/GLM permit up to 3,000 for structured state. No additional paid-model request or automatic retry was made.
- Live acceptance attempted one normal Gemini request, which returned the provider's unsupported-source-region HTTP 400 classification, and one normal GLM request, which returned recognised capacity HTTP 429. Both were stopped without repeated requests or region bypass. **No accepted live semantic transcript or classification-accuracy result is claimed for this release.** The previous live acceptances above remain historical, not evidence for the new prompt.
- `tests/semantic_cases.json` contains varied English/Chinese, indirect, ambiguous and multi-area expressions. The opt-in `scripts/evaluate_semantics.py` can run at most six normal free-provider cases, stops on a provider error and never enables DeepSeek. Run it after service availability recovers; inspect replies as well as labels. It is a smoke sample, not an accuracy benchmark.
- The separate Word user guide was updated to seven pages and rendered for page-by-page inspection. Public source contains no real client documents, visitor histories or credentials.

## Mobile radar layout repair — 2026-10-15

- Mobile navigation now stretches to the workspace width rather than shrinking with translated text. At 390px, Chinese previously measured 269px; both languages now measure 350px. At 320px both measure 280px, without horizontal page overflow.
- The panel is hidden during mobile situation selection and visible after the first accepted reply. Desktop selection at 1366px retains the panel. Browser checks used the labelled local simulated-provider flow, without live model requests. All 54 frontend and 51 Python tests and TypeScript checking passed.

## Help action refinement — 2026-10-15

The guide and recorded-example actions use unframed SVG arrows instead of dark circular inserts. Browser checks covered Chinese dark desktop and light mobile at 390px, including advancing the recorded example. Buttons retain their existing actions; reduced-motion preferences disable arrow movement. TypeScript, production build and all 54 frontend tests passed.

## Guided context and revisable advice — 2026-10-15

- Added optional, bilingual information-gap prompts beside the composer. Priority uses the accepted model focus, then explicit uncertainty and remaining coverage; it does not change classification or scores. Each prompt can show a recorded quote and explain the gap. Fully supported facets are excluded, and unknown information gets a verification route instead of a repeated demand for the fact.
- Accepted-turn additions and validated replacement links drive the change display. Corrections show exact old/new quotations and source navigation; a later revision does not erase its historical source. Brief comparison uses model-provided options only. Previous-suggestion comparison retains one prior accepted brief in the safely restored workspace, across view/home navigation and refresh. New inquiries clear it; this is not a full version archive. The prompt now asks the mentor to make missing information actionable and acknowledge explicit corrections. No extra LLM request was added.
- Labelled local-provider browser flow: initial preset → prompt fills draft with attempts unchanged → second accepted answer and advice request → two model-provided options → discussion button fills draft with attempts unchanged → third answer explicitly corrects the earlier record → old/new source panel and updated recommendation with previous suggestion available. Refresh retained accepted statements and corrections while requiring renewed connection verification. This deterministic fixture tests integration, not live semantic accuracy.
- Mobile uses document scrolling and a return-to-latest control. A focused input plus a simulated visual-viewport reduction from 844px to 460px activated the compact composer; guidance hid and input/sending controls stayed available. This is browser viewport simulation, not a physical iOS/Android keyboard test. Chinese at 390px had no horizontal page overflow. Language changes retained the three accepted rounds and draft.

- Final verification: 64 frontend tests, 51 Python tests, TypeScript and production build passed. At 320px and 390px, the new guide and comparison layout did not create horizontal page overflow. Clicking a gap with an existing draft preserved it and appended the starter. The English Word guide adds an eighth page; all earlier seven rendered pages are byte-identical to the prior render, and the new page was visually inspected. No real provider acceptance or physical-keyboard compatibility result is claimed.

- Independent review caught comparison loss when the brief unmounted on navigation. The prior accepted brief now lives in the workspace reducer and is source-validated on restore. A failing-then-passing regression covers navigation, refresh, secret-field stripping, failed switch preservation and clearing after a successful switch/new inquiry.
