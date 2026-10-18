# AuraAssist

A context-aware, hands-free home companion for the Amazon Alexa+ track. Built as a self-hosted MCP server (Streamable HTTP, MCP 2025-11-25+) with a web-based simulator that acts as an MCP client.

## Features
- Streamable HTTP MCP server at `/mcp` with tools: `get_home_snapshot`, `describe_scene`, `find_object`, `get_recent_events`, `run_routine`, `control_device`, `generate_daily_briefing`, `set_user_preference`
- Routine orchestrator with confirmation flow (`bedtime`, `leaving_home`, `morning`)
- Event memory (SQLite) and home-state model with mock devices
- VLM scene description via Amazon Bedrock (mocked by default)
- Privacy-first: no face ID, structured JSON, confirmations for sensitive actions
- Minimal web simulator (Vite + React + TS) to call MCP tools and visualize state

## Quick Start

### 1) Install Python deps
```bash
cd C:/Users/DELL/Desktop/MCP_SERVER/aura-assist
pip install -r requirements.txt
```

### 2) Run MCP server
```bash
uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```
Server: http://127.0.0.1:8000/, MCP endpoint: http://127.0.0.1:8000/mcp

### 3) Run web simulator
```bash
cd web
npm i
npm run dev
```
UI: http://localhost:5173

## MCP Testing
Use MCP Inspector or curl:
- List tools: `POST /mcp` with initialize + tools/list (Streamable HTTP)
- Call `run_routine` with {"routine_name":"bedtime","confirm":false} first, then confirm:true

## Environment
Copy `.env.example` to `.env` and set AWS keys to use real Bedrock (optional).

## License
MIT
