# React experience implementation plan

Goal: preserve the inquiry engine and running Streamlit release while introducing a continuous React interface and portable Python API.

Architecture: React/Vite/TypeScript with one GSAP motion system. Python core retains question and quotation validation. Native Python API and Python Worker implement the same HTTP contract; choose the free deployment only after runtime verification.

Spec: local architecture assessment dated 2026-10-13; latest preference permits comfortable whitespace. No command search or skip-transition UI. All public content remains anonymous.

## Constraints

- Keys remain request-scoped or backend secrets; never browser persistence or bundles.
- One contextual question, exact user quotations, no verdict; commit only after validation.
- Refresh and navigation preserve accepted dialogue; scenario switching and regeneration are transactional.
- Actual SSE execution events; final question appears only after complete validation, not unsafe partial JSON.
- Reduced motion and touch/keyboard support; no external asset CDN.
- Existing Streamlit entrypoint and tests remain available.

## Tasks

1. API contract and tests: `edge/service.py`, `edge/transport.py`, `edge/store.py`, `tests_next/test_api.py`. Async request execution returns stage events and a validated session snapshot. Test invalid output, repeat request IDs, version conflict, visitor key precedence, free allowlist, no credential serialization.
2. Python Worker adapter: `edge/worker.py`, `wrangler.jsonc`, `pyproject.toml`, SQL schema. Use async runtime fetch and storage binding. Run local runtime probe before considering cloud deployment; record measured and unmeasured limits.
3. React state and tests: `web/src/state.ts`, `web/src/api.ts`, `web/src/state.test.ts`. Restore non-secret state; reject stale requests; preserve draft on cancel/failure; model changes do not delete records.
4. Designed React screens: welcome/model configuration, folder previews, conversation, notebook/review, journey/theme, GSAP shared-element transitions. Test real browser desktop/mobile, reduced-motion guards, rapid navigation and configuration errors.
5. Package/release: build, full old/new suites, security scan, local runnable ZIP, README/CI. Push independent branch; retain current deployment. Complete actual provider/deployment checks when account access and secrets are configured.

## Review focus

- Stale response during case switch must not overwrite current dialogue.
- Interrupted SSE must preserve input and use idempotent recovery.
- Refresh must restore stage without restoring visitor credentials.
- Public developer-key endpoint needs access protection and global quotas.
- Worker runtime/CPU constraints must be measured separately from native tests.

## Execution ledger

- Baseline: independent clone on feat/react-experience from existing public main; old project untouched.
- Authorization: user requested execution of the completed architecture assessment; proceed without another design approval cycle.

- API service: 9 native tests pass; React reducer: 7 tests pass. Real Pyodide core probe returned a validated question. Local Workers cannot establish cloud CPU limits.
- Local fixture preview on port 8789 is labelled simulated, no real provider calls. Native API on port 8788.
- Worker bundling must place source under .worker-build/src to exclude development environments; root requirements.txt kept unchanged.
- Cloudflare scoped OAuth user-approved; callback twice expired. Renew only when ready for immediate user confirmation.
- 2026-10-14: OAuth completed. APAC D1 schema initialized; independent Python Worker + static frontend deployed. Cloud health, empty session creation and invalid-key SSE reached the actual provider HTTP401. Initial domain TLS errors cleared after propagation; user also confirmed model page opens.
- Final review: fixed old-request completion after NEW, locked cancel during submitted switch, unified fresh consent on both selection entry points, increased D1 lease to 90s with transport/commit margin. Regression tests observed failing, then passing.
- Browser QA: cancel restores prior transcript/draft; refresh retains conversation without replaying welcome; 390px phone preview initially toggled shut via focus and was fixed/retested. No horizontal overflow at 390px. Responses in local QA are explicitly simulated.
- Current tests: 98 preserved Streamlit, 17 new Python, 13 React reducer tests pass; TypeScript and production build pass. Runtime bundle JavaScript ~120KB gzip, local font subsets load separately.
- Remaining release gates: privately configure new backend keys/access code, successful real provider calls and Worker CPU measurements, GitHub branch publication/CI, final desktop/phone screenshots.

- Visual continuity revision: preserved the approved welcome; replaced folder cards with a double-bezel context canvas and expandable inspiration list. Credentials now use explicit developer/personal modes. Confirmed both configured services through public boolean metadata, never secret values. Native simulated browser checked independent fields, selection, empty custom context and keyboard preview.
