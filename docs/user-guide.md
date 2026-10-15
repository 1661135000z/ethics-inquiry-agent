# Using Inquire

The interface opens in English for first-time visitors. Use **中文** to switch to Chinese; the current tab retains your chosen language.

## Start an inquiry

1. Open the [mainland mirror](https://app.inquire-ethics.dynv6.net/) or the [primary app](https://inquire-experience.inquire-ethics-lab.workers.dev/).
2. Choose GLM or Gemini. The public demo uses saved server credentials; you do not need a personal key or access code. If needed, use the inline model settings to test the connection or supply your own key.
3. Type a fictional or anonymised situation. Optional examples can be previewed and edited; they are not assumptions the agent makes about you.
4. Confirm permission to send the text to the selected provider, then submit. Answer the agent's follow-up question with what you know; state what remains unknown.
5. Use **Inquiry clues** to inspect recorded statements and jump back to their source turn. **Human review** previews the dossier; after two accepted turns, print/save it as PDF or download the HTML packet.

A turn is one accepted user message plus the agent's validated question. Questions explore objectivity through your role, relationships, incentives, competing explanations, evidence and independent review. They do not certify ethical compliance.

On phones, the five-dimensional panel appears after the first valid reply and stays hidden during situation selection. Desktop keeps it available during selection too. Language switching preserves its alignment and inquiry state.

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

**Inquiry clues** shows five evidence-linked areas: role/responsibility, relationships/interests, pressure/incentives, evidence/alternatives and independent review. A university friendship belongs primarily to relationships; it is not automatically pressure. A threat linking promotion to silence supplies a separate basis for pressure.

The radar shows three distinct information needs per area, labelled **Unexplored**, **Partly explored** or **Substantial context**. It is not a risk score, independent verification or a requirement to make every area grow equally. Quotation count and turn count do not determine coverage. Unknown reports remain visible but do not count as resolved information. Hover/focus or activate an area to read known statements and remaining gaps. The agent's next focus highlights its corresponding area.

Selecting an unchanged example immediately previews source-checked initial statements, without calling a model. Editing an example or writing your own situation clears that curated preview; the full text is semantically analysed on submission in the **same model request** as the first question. Model updates retain exact quotations, user-turn sources, classification explanations and explicit corrections. A correction can supersede earlier information and reopen a gap; records remain user-reported and may be wrong.

The agent normally responds with a short insight and one concrete follow-up. When the five areas have sufficient reported context, it can compare options and suggest a conditional next step while continuing to ask questions. You can request advice earlier; uncertainty must be made clear. The **Ethical decision brief**, when a valid source-supported brief is generated, shows the conflict, reported stakeholders, options and trade-offs, preliminary advice and unresolved issues. Important new information marks older guidance as needing reassessment until a fresh valid brief replaces it. It never grants ethical clearance or ends the dialogue automatically. If you switch language, saved quotations and earlier advice keep their original wording; subsequent model responses use your selected language.

A submitted message remains visibly pending until validation and commit succeed. The processing ribbon uses real backend stage events. Use **Back to latest** after reading an earlier message; a long initial situation can be expanded without resending it.

The model status distinguishes **Configured · not tested** from a successful connection test or accepted response. An expired or changed configuration can require testing again without removing accepted records. Conversation turns and request attempts are separate counters.

## Save and revisit a local archive

Open **History**, give the inquiry a name and choose **Save on this device**. Saving is optional and stores only accepted conversation, evidence-linked analysis, observations and provenance in this browser's localStorage. It excludes API keys, access codes, sending consent, unsent drafts and DeepSeek eligibility. At most the twenty most recently saved records are kept.

Choose a record to read its conversation, clues and review preview. Rename it, export Markdown, or delete it and use **Undo** while the panel remains open. Historical viewing does not call a model or replace the current online inquiry. A historical dossier may be printed; its server download link is disabled because the current server session may represent a different conversation.

These saved archives survive tab closure until you delete them or clear site storage. They are not synchronised: the primary and mirror domains have separate local archives. Avoid confidential data, including on shared devices. Browser storage restrictions may prevent saving; the active inquiry still works. Download an export before clearing site data.

Use **Help** for the short guide, privacy details and product scope. Theme and language changes do not translate user quotations or discard the live conversation.

## The first-run guide and recorded example

After the first successful model transition, the existing **Inside Inquire** panel opens with a short guide. It opens after the situation page settles and can be dismissed with its close button, Escape or **Explore my situation**. Only that explicit action focuses the input; ordinary dismissal restores the invoking control. Viewing is remembered per browser and domain when storage is available. It does not interrupt an existing dialogue or active editing. Use the help icon beside the language switch to reopen it.

**Real example** contains an actual two-turn test from 12 October 2026 with a fictional situation. English displays the original inputs and model questions. Chinese displays labelled manual translations, with expandable original English for checking. Model provenance remains unchanged; switching language retains the selected example turn. It is a historical record, not a simulated live response. Reading it makes no model requests, does not spend the backup allowance and does not replace your current conversation.

The composer grows with your input within a bounded height. Expand its follow-up reference to see the question you are answering. An explicit **Retry this input** resends a failed draft only when the current connection and sending permission allow it; this uses an API attempt. There are no automatic retries. Changes in distinct information coverage briefly highlight the relevant radar axis; source navigation highlights its category. Printed review previews include statement IDs, source turns and space for human-review notes.

The **About Inquire** tab contains the author's contact details and project origins.
