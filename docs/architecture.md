# AuraAssist Architecture

```
User / Web MCP Client (React + TS)
        |
        |  Streamable HTTP (MCP 2025-11-25+)
        v
AuraAssist MCP Server (Python + MCPServer SDK, Streamable HTTP)
        |
        |-- Home State Service      (home_state.py / devices.py)
        |-- Event Store / Memory    (event_store.py, SQLite)
        |-- Vision Service          (vision.py -> Bedrock VLM)
        |-- Routine Orchestrator    (routines.py)
        |-- Reasoning / Briefing    (bedrock_client.py)
        v
Alexa+ / Web Simulator response
```

## Layers

| Layer | Responsibility | Technology |
| --- | --- | --- |
| Client | Chat, dashboard, event timeline, visible MCP tool log | React + TypeScript + Vite |
| MCP | Tools + resources over Streamable HTTP | Python `mcp.server.MCPServer`, Starlette |
| Vision | Image -> structured scene JSON | Amazon Bedrock Converse (Nova / Claude) |
| Reasoning | Briefings and summaries | Amazon Bedrock (text) |
| Home state | Devices, rooms, locks, thermostat | In-memory registry |
| Memory | Events, object sightings, routines | SQLite |
| Routines | Deterministic multi-step workflows with confirmation | routines.py |

## MCP Tools

| Tool | Purpose |
| --- | --- |
| `get_home_snapshot` | Current device/room state |
| `describe_scene` | VLM scene description from a camera frame |
| `find_object` | Search object-sighting history |
| `get_recent_events` | Filtered event list |
| `run_routine` | Plan (confirm=false) or execute (confirm=true) a routine |
| `control_device` | Control one device (on/off/lock/unlock) |
| `generate_daily_briefing` | Human-readable user/caregiver summary |
| `set_user_preference` | Accessibility and privacy preferences |

## MCP Resources

- `aura://home/state`
- `aura://events/recent`
- `aura://routines`
- `aura://privacy-policy`
- `aura://user/preferences`

## Confirmation Flow

1. Client calls `run_routine(routine_name, confirm=false)`.
2. Server returns the plan and a spoken confirmation prompt.
3. User approves.
4. Client calls `run_routine(routine_name, confirm=true)`.
5. Server executes steps, logs events, and summarizes results.
