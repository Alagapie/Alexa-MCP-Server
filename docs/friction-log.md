# Friction Log — Amazon Developer Hackathon (Alexa+ track)

Notes recorded while building AuraAssist with MCP and Amazon Bedrock.

## 1. MCP SDK major version rename (FastMCP → MCPServer)

- **Used it for:** Building the self-hosted MCP server (Streamable HTTP).
- **What happened:** Guides and most tutorials use `from mcp.server.fastmcp import FastMCP`.
  The installed SDK (2.x) renamed it to `MCPServer` and importing the old path
  raises a `ModuleNotFoundError` with a pointer to the migration guide.
- **Impact:** Medium. Cost time to discover the new entry point.
- **Workaround:** Imported `from mcp.server import MCPServer` and used
  `streamable_http_app()` + `custom_route()`.
- **Suggestion:** Show the current API front-and-center in the Alexa+ onboarding
  docs with a minimal Streamable HTTP server example, and pin a known-good version.

## 2. Mounting the Streamable HTTP app

- **What happened:** Mounting `streamable_http_app()` under a FastAPI sub-path
  can lead to double paths and lifespan issues.
- **Workaround:** Used the Streamable HTTP app directly as the ASGI app and added
  extra routes with `@mcp.custom_route`.
- **Suggestion:** Document the exact "add a health route + serve MCP" pattern.

## 3. CORS for a browser MCP client

- **What happened:** A browser-based MCP client needs `Mcp-Session-Id` in
  `expose_headers` and an SSE-capable `Accept` header.
- **Workaround:** Added `CORSMiddleware` with `expose_headers=["Mcp-Session-Id"]`
  and `Accept: application/json, text/event-stream`.
- **Suggestion:** Mention browser-client setup explicitly in Track docs.

## 4. Bedrock model IDs / onboarding

- **What happened:** Model IDs and regions differ (e.g. `amazon.nova-lite-v1:0`
  vs `us.amazon.nova-lite-v1:0`) and access must be granted before first call.
- **Workaround:** Made the client configurable via env vars with a mock fallback
  so the demo always runs.
- **Suggestion:** Provide a per-track list of enable-able models and their IDs.

## Overall

- **What worked well:** The MCP tool/resource model maps cleanly onto a home
  assistant; Streamable HTTP is easy to test with the SDK client; the protocol
  version negotiation (2025-11-25) worked first try.
- **Would I build with it again?** Yes — MCP is a strong fit for agent-facing APIs.
