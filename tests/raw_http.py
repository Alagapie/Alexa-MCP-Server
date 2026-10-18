import httpx, json

URL = "http://127.0.0.1:8000/mcp"
headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

init = {
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "raw", "version": "1.0"}},
}
r = httpx.post(URL, json=init, headers=headers)
print("STATUS", r.status_code)
print("CT:", r.headers.get("content-type"))
print("SESSION:", r.headers.get("mcp-session-id"))
print("BODY:", r.text[:300])
