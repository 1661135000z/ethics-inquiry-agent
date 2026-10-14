# Using Inquire

The interface opens in English for first-time visitors. Use **中文** to switch to Chinese; the current tab retains your chosen language.

## Start an inquiry

1. Open the [mainland mirror](https://app.inquire-ethics.dynv6.net/) or the [primary app](https://inquire-experience.inquire-ethics-lab.workers.dev/).
2. Choose GLM or Gemini. The public demo uses saved server credentials; you do not need a personal key or access code. If needed, use the inline model settings to test the connection or supply your own key.
3. Type a fictional or anonymised situation. Optional examples can be previewed and edited; they are not assumptions the agent makes about you.
4. Confirm permission to send the text to the selected provider, then submit. Answer the agent's follow-up question with what you know; state what remains unknown.
5. Use **Inquiry clues** to inspect recorded statements and jump back to their source turn. **Human review** previews the dossier; after two accepted turns, print/save it as PDF or download the HTML packet.

A turn is one accepted user message plus the agent's validated question. Questions explore objectivity through your role, relationships, incentives, competing explanations, evidence and independent review. They do not certify ethical compliance.

## If GLM is busy

A recognised capacity error means the provider is crowded; retrying later may work. Other rate-limit, quota, authentication and network errors have different causes. The app offers a visible DeepSeek backup after an eligible GLM failure. Expand it and choose **Switch to DeepSeek** to continue without discarding the accepted conversation or unsent input. The developer funds this service; you do not pay or provide a key.

DeepSeek mode permits at most **10 accepted turns in the current inquiry**, not ten additional turns after switching. There are also ten paid request attempts per server session and sixty across the deployment per day. Failures and regeneration consume attempts; reaching ten displayed turns is therefore not guaranteed. Backup eligibility lasts 30 minutes after a recognised GLM failure.

## Return to the welcome screen

Click the top-left Inquire logo to return home. Your conversation, unsent draft, model settings and request counts remain intact. Choose **Continue your inquiry** to return to the same view, including a pending situation selection. Home navigation makes no model call. It is temporarily unavailable while a request, connection or transition is running. Choosing a model card still tests or configures that service.

## Change or restart

**Choose another situation** opens selection without deleting the accepted conversation. Submit the replacement to commit it only after a valid first reply; cancel restores the old draft. **New inquiry** clears the transcript, observations and execution records, retains the original situation and model preference, and clears sending consent. When using DeepSeek, it returns to GLM.

The conversation turn counter resets for a new inquiry. The inherited **24 request-attempt limit does not reset**, and global hourly/daily limits remain. A new server session has a fresh ten-attempt DeepSeek allowance only if a new real GLM failure enables it; this is not unlimited free access. Normal Gemini/GLM inquiries allow twelve accepted turns. Connection tests also consume the shared deployment allowance.

**Regenerate** replaces only the latest agent question and preserves the unsent answer; it does not add a user turn but consumes an API attempt. Changing models retains the conversation and requires renewed sending consent.

## Records, privacy and recovery

Reported statements are exact quotations from the user, not independently verified audit evidence. Empty categories do not prove the absence of a threat. The review packet organises statements, missing information and model provenance for human review; it is not a final ethical recommendation.

The browser retains non-secret drafts and accepted records in tab sessionStorage. Personal keys and sending consent clear on refresh. Server sessions expire after two hours; availability may end earlier if the native server restarts. An available cached transcript is then read-only and can be exported. Closing the tab can discard its local cache. Do not enter client-identifiable, confidential or sensitive information.

Execution details show actual input checks, provider requests, output validation and commit status. They do not display hidden chain-of-thought or invented tool calls. A validation failure leaves the previous accepted conversation intact; rephrase or switch provider rather than accepting an invalid answer.

## A demonstration you can reproduce

This is an illustrative test script, not a claimed live model transcript:

- Situation: “I am an audit junior. An AI tool marked a revenue adjustment as low risk. My manager wants me to accept it before a deadline, but I do not know who checked the source data.”
- Answer a question about independent review: “I have the tool output and source-data extract. I do not know whether anyone independently compared them.”
- Answer the next contextual question using the records or people available to resolve uncertainty.
- Check that the agent preserves “I do not know”, asks a relevant follow-up, and does not declare the judgment acceptable or unethical. After two turns, export the conversation and review packet.

Model wording varies. Keep an actual exported transcript if demonstrating the agent in a submission; do not replace it with this sample script.

## Workspace controls

**Inquiry clues** organises exact user quotations into five areas. Click a source-turn link to return to the original message. The five-axis radar plots recorded statement counts, with a shared labelled scale that expands when needed. Empty axes remain at zero. Hover/focus an axis or category to highlight its counterpart; click to open that area. It does not measure risk or prove that enough evidence has been gathered. Counts describe statements, not ethical risk, evidence completeness or verified facts.

A submitted message remains visibly pending until validation and commit succeed. The processing ribbon uses real backend stage events. Use **Back to latest** after reading an earlier message; a long initial situation can be expanded without resending it.

The model status distinguishes **Configured · not tested** from a successful connection test or accepted response. An expired or changed configuration can require testing again without removing accepted records. Conversation turns and request attempts are separate counters.

## Save and revisit a local archive

Open **History**, give the inquiry a name and choose **Save on this device**. Saving is optional and stores only accepted conversation, observations and provenance in this browser's localStorage. It excludes API keys, access codes, sending consent, unsent drafts and DeepSeek eligibility. At most the twenty most recently saved records are kept.

Choose a record to read its conversation, clues and review preview. Rename it, export Markdown, or delete it and use **Undo** while the panel remains open. Historical viewing does not call a model or replace the current online inquiry. A historical dossier may be printed; its server download link is disabled because the current server session may represent a different conversation.

These saved archives survive tab closure until you delete them or clear site storage. They are not synchronised: the primary and mirror domains have separate local archives. Avoid confidential data, including on shared devices. Browser storage restrictions may prevent saving; the active inquiry still works. Download an export before clearing site data.

Use **Help** for the short guide, privacy details and product scope. Theme and language changes do not translate user quotations or discard the live conversation.
