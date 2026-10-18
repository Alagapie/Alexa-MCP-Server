# AuraAssist Privacy & Data Retention

AuraAssist is designed to be privacy-first. It helps an assistant understand a
home without turning that home into a surveillance system.

## Principles

- **No facial recognition or person identification.** The vision model never
  identifies people by name, face, gender, race, ethnicity, or health condition.
  It reports only an anonymous `people_count`.
- **Limited image retention.** Camera frames are processed transiently to produce
  structured facts. Frames are not stored by default. Only derived text
  (object labels, locations, confidence, summary) is written to the event store.
- **Local event memory.** Event history is stored in a local SQLite database for
  the demo. In a deployed configuration it is stored in DynamoDB under the
  user's account with a configurable retention window.
- **Explicit consent for sensitive actions.** Locking/unlocking doors and
  disabling alarms require a two-step confirmation and are never silent.
- **Communicated uncertainty.** Low-confidence results are reported with
  "possibly" or "unclear" rather than stated as fact.
- **Caregiver summaries are derived, not raw.** Briefings summarize events and
  avoid raw video and person identification.

## Data Retention

| Data | Where | Retention |
| --- | --- | --- |
| Camera frames | In memory only | Transient (processing only) |
| Object sightings | Event store | Configurable, default 30 days |
| Device actions | Event store | Configurable, default 30 days |
| Preferences | Event store / config | Until deleted |

## User Controls

- `set_user_preference` stores accessibility and privacy preferences.
- `aura://privacy-policy` exposes the current retention rules as an MCP resource.
- Users can request their event history be deleted (clear the event store).

## Non-Goals

AuraAssist does not provide medical diagnosis, fall detection, emergency
dispatch, continuous video streaming, or person identification.
