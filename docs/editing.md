# Editing the product

Run the Python API on port 8788 and `pnpm dev` in a second terminal. Open Vite's displayed local URL. React updates as you save; change one component or rule at a time and check both Chinese/English and 390px/desktop views before building.

| Change | File |
|---|---|
| Page sections, buttons, inline model settings, backup offer | `web/src/App.tsx` |
| Situation examples and previews | `web/src/SituationStudio.tsx`, `inquiry/examples.py` |
| Colours, type size, spacing, responsive layout | `web/src/style.css`, `web/src/experience.css` |
| Clue compass, notebook, dossier, help and status | `web/src/ExperiencePanels.tsx`, `web/src/experience.ts` |
| Explicit local history and its privacy whitelist | `web/src/HistoryPanel.tsx`, `web/src/history.ts` |
| Entry and shared-element transitions | `web/src/motion.ts` |
| Errors translated between interface languages | `web/src/i18n.ts` |
| Navigation, drafts, reset and recovery rules | `web/src/state.ts` |
| Browser-to-backend calls and SSE handling | `web/src/api.ts` |
| Agent instructions and reply validation | `inquiry/core.py` |
| Model allowlist, API endpoints and errors | `edge/policy.py`, `edge/transport.py` |
| Turn/request limits and transaction flow | `edge/service.py`, `edge/store.py`, `edge/d1.py` |
| Human-review output | `inquiry/review_packet.py` |

For a text change, update both branches of `t('中文','English')`. For CSS, edit the existing component rule and inspect mobile overrides rather than stacking conflicting fixes. Do not change state or API logic just to move a button. Keep passwords out of JSX defaults, Vite configuration and checked-in files.

Changing the Python example list changes `/api/config`; the browser uses the server's list. `web/src/cases.json` is a bundled fallback, so keep it consistent if editing examples. UI-only edits still need `pnpm test` and `pnpm build`. Backend edits need `python -m unittest discover -s tests -v`. Do not use live paid API calls for tests that mocked responses can cover.
