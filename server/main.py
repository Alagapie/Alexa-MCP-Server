"""AuraAssist entry point.

Exposes the MCP server over Streamable HTTP (MCP 2025-11-25+).
Run with:  uvicorn server.main:app --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .mcp_tools import mcp

load_dotenv()

MCP_PATH = os.getenv("MCP_PATH", "/mcp")


@mcp.custom_route("/", methods=["GET"])
async def root(_request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "AuraAssist MCP Server",
            "status": "ok",
            "mcp_endpoint": MCP_PATH,
            "spec": "MCP 2025-11-25+ (Streamable HTTP)",
        }
    )


@mcp.custom_route("/health", methods=["GET"])
async def health(_request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


# Build the Streamable HTTP ASGI app. Must be called AFTER custom routes are
# registered so they are included.
app = mcp.streamable_http_app(streamable_http_path=MCP_PATH)

# Allow the web simulator (served from a different origin) to call the server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)
