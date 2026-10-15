# Architecture

React renders immediately as static assets. Python is called only for configuration, session restoration, connection testing, submitted inquiries and exports. GSAP handles UI transitions; it does not implement reasoning or make API requests.

```text
Browser: React + TypeScript + GSAP
             │ same-origin /api
             ▼
Cloudflare Python Worker ── Gemini / GLM / gated DeepSeek
             │
             ▼
        D1 snapshots and atomic request reservations

Mainland browser → identical EdgeOne static app → fixed-origin API relay → same Worker
Local browser    → Vite / built assets → FastAPI → process-memory store
```

## Inquiry contract

`inquiry/core.py` supplies an objectivity-focused prompt and parses the provider's JSON. Each accepted response contains one context-specific question, a focus area and optional exact user quotations. Uncertain statements stay uncertain. Validation checks structure, bounded length and quotation provenance; these are useful safeguards, not proof that every model question is correct.

`edge/service.py` orchestrates input checks → atomic reservation → provider request → response validation → transactional commit. A duplicate request ID cannot silently call the provider again. Only a valid response updates the snapshot. Request attempts count even when a provider fails.

`edge/transport.py` calls fixed vendor endpoints. `edge/policy.py` controls allowed models, credentials, free eligibility and errors. The DeepSeek route requires server-granted eligibility after a genuine GLM failure and a manual user switch; it is never an automatic paid retry.

## State and security

The React reducer in `web/src/state.ts` manages selection, pending drafts, cancellation, regeneration and recovery. Its storage whitelist excludes credentials. Python's cookie is HttpOnly, same-site and secure on HTTPS; D1 stores accepted records and request reservations, not provider keys. Secrets come from the Worker environment or the native server's `.env`.

The mirror relay permits only known routes, bounded bodies and matching POST origins. It is neither a redirect nor an open proxy; secrets remain in Cloudflare. The mirror's backend availability and limits are shared with the primary site.

## Deliberate limits

There is no custom model training, standards lookup, autonomous audit decision, external audit-tool execution or raw token streaming. SSE streams observable processing events and the final validated response. Human-review packets are assembled from accepted records without another model call. Developer-funded access is a bounded demonstration, not an unrestricted production API. Free hosting and provider capacity are separate limits; mainland access requires testing on the actual network.

## Experience layer

`experience.ts` derives counts, categories and source turns from accepted snapshots. `ExperiencePanels.tsx` renders the lens motif, observable stages, clue notebook, dossier and help. It does not request additional reasoning or infer a risk score. Pending input is ephemeral reducer state and is removed on failure; accepted records are unchanged until the backend commit.

`history.ts` sanitises explicit local archives using the public snapshot whitelist, excluding drafts, credentials and backup authorisation. `HistoryPanel.tsx` displays them independently in a native dialog. localStorage is origin-specific, capped at twenty records and two megabytes of parsed input. It is not an encrypted vault or a server synchronisation feature. Printing a selected archive hides the live workbench so the two dossiers cannot be combined inadvertently.

The shared-element transition commits state exactly once and measures its destination after rendering. Animation preparation, timeline or cleanup failures fall back to the accepted state rather than blocking a validated reply. Reduced-motion bypasses the cinematic timeline. Processing animations correspond to events received from the backend; no hidden reasoning or fictitious tools are shown.


## Evidence-led five-dimensional inquiry

`inquiry/analysis.py` defines three information needs for each of the five existing area IDs. Active facts retain a stable ID, exact user quotation, user-turn number, initial/answer provenance, semantic facet, reported/uncertain kind and short classification explanation. A valid current correction can supersede an earlier source-linked claim. Covered facets are a set, so repeated and paraphrased statements within one facet cannot inflate coverage. Unknowns do not complete a need; no area is a default label.

`system_prompt` receives this shared state, definitions, gaps and the full retained conversation. A **single** provider response contains the concise conversational response, one core question, focus, incremental semantic updates and an optional conditional decision brief. Python validates source turns and quotations, derives coverage and commits analysis with the dialogue atomically. A failed request commits neither new facts nor advice. This is model-assisted semantic classification with bounded validation, not a proof of factual truth or universal classification accuracy.

Preset previews use reviewed, literal scenario excerpts, supplied by `/api/config`. `scripts/sync_analysis_assets.py` keeps the bundled fallback presets and bilingual definitions aligned with Python; a regression checks equality. Custom/edited scenarios are analysed only on their first explicit submission, without a separate classification call. Neither hover, language switching nor radar navigation calls a model.

The optional brief is accepted only when all areas have substantial reported context or the latest user asks for advice, and must cite active exact quotations. Accepted new user context conservatively marks any unreassessed brief stale, even if extraction returns no usable updates. Guidance remains tentative and human-reviewed. Free-provider output is bounded to 3,000 tokens for structured state; DeepSeek retains its 1,600-token paid output cap, with unchanged session/request/paid-backup gates; no automatic retries. Actual costs still depend on tokens and provider pricing.

React uses the same IDs and facet definitions for coverage, missing information, source navigation and highlight state. Restoring cached analysis copies only declared, source-checked fields; earlier archives retain their quotations without inventing semantic completeness. Markdown and HTML review exports include analysis sources and conditional guidance where available. Native Python and Workers use the same parser/state functions.

### Repeatable semantic smoke checks

When a configured free provider is available, run `python scripts/evaluate_semantics.py --url https://inquire-experience.inquire-ethics-lab.workers.dev --provider zhipu --max-cases 6`. This deliberately sends up to six fictional inputs and consumes normal request allowance. It stops at the first service error, does not retry and does not use paid backup. Its small varied sample is separate from the offline state suite; manually inspect whether the next question respects context and known facts. Provider availability failures are not classification results.
