# AuraAssist Demo Script (under 3 minutes)

Target: show a complete accessibility journey with visible MCP tool calls.

| Time | Section | On screen | Voiceover |
| --- | --- | --- | --- |
| 0:00–0:20 | Problem | Home simulator idle | "Smart homes are powerful, but for a blind user 'turn on the light' doesn't answer the real questions: what's on the counter? where are my keys? is the house secure?" |
| 0:20–0:45 | Intro | AuraAssist UI + MCP connection banner | "AuraAssist is a context-aware Alexa+ companion built on a self-hosted MCP server over Streamable HTTP." |
| 0:45–1:30 | Scene understanding | Ask "What is on the kitchen counter?" — show `describe_scene` tool call | "AuraAssist sends the kitchen frame to a vision model on Amazon Bedrock and returns a spoken, safety-first description." |
| 1:30–2:10 | Routine orchestration | Ask "Prepare the house for bed" → plan → "yes" → show `run_routine` ×2 and device changes | "AuraAssist plans first, asks for confirmation, then executes the bedtime routine across doors, lights, and the thermostat." |
| 2:10–2:35 | Memory & briefing | Ask "What changed today?" — show event timeline | "Everything is remembered so users and caregivers can get a calm summary." |
| 2:35–2:55 | Close | MCP tool log + privacy resource | "AuraAssist: privacy-first, context-aware, and built to help people understand their home, not just command it." |

## Checklist before recording

- MCP server running (`uvicorn server.main:app --port 8000`).
- Web simulator running (`npm run dev`).
- Zoom the browser so MCP tool calls and device state are readable.
- Keep the tool-call log visible — it proves real MCP usage.
- No copyrighted music or third-party trademarks.
