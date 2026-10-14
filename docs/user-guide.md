# Using Inquire

## Start an inquiry

1. Open the [mainland mirror](https://app.inquire-ethics.dynv6.net/) or the [primary app](https://inquire-experience.inquire-ethics-lab.workers.dev/).
2. Choose GLM or Gemini. The public demo uses saved server credentials; you do not need a personal key or access code. If needed, use the inline model settings to test the connection or supply your own key.
3. Type a fictional or anonymised situation. Optional examples can be previewed and edited; they are not assumptions the agent makes about you.
4. Confirm permission to send the text to the selected provider, then submit. Answer the agent's follow-up question with what you know; state what remains unknown.
5. Inspect reported statements and execution details. After two accepted turns, download the human-review packet; export the conversation before leaving.

A turn is one accepted user message plus the agent's validated question. Questions explore objectivity through your role, relationships, incentives, competing explanations, evidence and independent review. They do not certify ethical compliance.

## If GLM is busy

A recognised capacity error means the provider is crowded; retrying later may work. Other rate-limit, quota, authentication and network errors have different causes. The app offers a visible DeepSeek backup after an eligible GLM failure. Expand it and choose **Switch to DeepSeek** to continue without discarding the accepted conversation or unsent input. The developer funds this service; you do not pay or provide a key.

DeepSeek mode permits at most **10 accepted turns in the current inquiry**, not ten additional turns after switching. There are also ten paid request attempts per server session and sixty across the deployment per day. Failures and regeneration consume attempts; reaching ten displayed turns is therefore not guaranteed. Backup eligibility lasts 30 minutes after a recognised GLM failure.

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
