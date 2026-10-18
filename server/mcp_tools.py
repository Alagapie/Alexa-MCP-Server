"""MCP tools and resources for AuraAssist (MCP 2025-11-25+ / Streamable HTTP)."""
from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Optional

from mcp.server import MCPServer

from .bedrock_client import bedrock
from .devices import registry
from .event_store import event_store
from .home_state import home_state
from .routines import orchestrator
from .vision import vision

# The MCP server instance. Renamed from FastMCP -> MCPServer in MCP SDK 2.x.
mcp = MCPServer("AuraAssist")


@mcp.tool()
def get_home_snapshot(room_filter: Optional[str] = None) -> Dict[str, Any]:
    """Return the current home-state snapshot (devices, rooms, alerts)."""
    return home_state.snapshot(room_filter=room_filter)


@mcp.tool()
def describe_scene(camera_id: str = "kitchen", image_base64: Optional[str] = None) -> Dict[str, Any]:
    """Describe a camera frame using a vision-language model.

    Returns structured JSON: room, objects, hazards, people_count, summary.
    Images are processed transiently and are not retained.
    """
    image_bytes: Optional[bytes] = None
    if image_base64:
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            image_bytes = None
    return vision.describe_scene(camera_id=camera_id, image_data=image_bytes)


@mcp.tool()
def find_object(object_name: str, time_range: Optional[str] = None) -> Dict[str, Any]:
    """Search recent object sightings for a named object (e.g. 'keys')."""
    results = event_store.find_object(object_name=object_name, time_range=time_range)
    return {"object": object_name, "count": len(results), "results": results}


@mcp.tool()
def get_recent_events(
    since: Optional[str] = None,
    room: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Return recent device, camera, and routine events."""
    events = event_store.get_recent(since=since, room=room, event_type=event_type, limit=limit)
    return {"count": len(events), "events": events}


@mcp.tool()
def run_routine(routine_name: str, confirm: bool = False) -> Dict[str, Any]:
    """Plan or execute a multi-step routine.

    Call with confirm=false first to receive a plan, then confirm=true to execute.
    """
    return orchestrator.run_routine(routine_name=routine_name, confirm=confirm)


@mcp.tool()
def control_device(device_id: str, action: str, confirm: bool = True) -> Dict[str, Any]:
    """Control one device. action is one of: on, off, lock, unlock."""
    if not confirm:
        return {"status": "needs_confirmation", "device_id": device_id, "action": action}
    action_lower = action.lower()
    if action_lower == "on":
        res = registry.update(device_id, {"on": True})
    elif action_lower == "off":
        res = registry.update(device_id, {"on": False})
    elif action_lower == "lock":
        res = registry.update(device_id, {"locked": True, "open": False})
    elif action_lower == "unlock":
        res = registry.update(device_id, {"locked": False})
    else:
        return {"status": "error", "message": f"Unsupported action: {action}"}
    if res is None:
        return {"status": "error", "message": f"Unknown device: {device_id}"}
    try:
        event_store.add_event(
            event_type="device_action",
            device_id=device_id,
            room=res.get("room"),
            action=action_lower,
            details=json.dumps(res.get("state", {})),
        )
    except Exception:
        pass
    return {"status": "ok", "device_id": device_id, "action": action_lower, "device": res}


@mcp.tool()
def generate_daily_briefing(date: Optional[str] = None, audience: str = "user") -> Dict[str, Any]:
    """Generate a calm, human-readable briefing from recent events."""
    events = event_store.get_recent(since=date, limit=200)
    text = bedrock.generate_briefing(events, audience=audience)
    return {"date": date or "recent", "audience": audience, "event_count": len(events), "briefing": text}


_PREFS: Dict[str, Any] = {}


@mcp.tool()
def set_user_preference(key: str, value: str) -> Dict[str, Any]:
    """Store an accessibility or privacy preference (key/value)."""
    _PREFS[key] = value
    event_store.add_event(event_type="preference_set", action=key, details=value)
    return {"status": "ok", "key": key, "value": value, "preferences": _PREFS}


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------

@mcp.resource("aura://home/state", name="Home State", description="Current home-state snapshot")
def resource_home_state() -> str:
    return json.dumps(home_state.snapshot(), indent=2)


@mcp.resource("aura://events/recent", name="Recent Events", description="Recent device and camera events")
def resource_recent_events() -> str:
    return json.dumps(event_store.get_recent(limit=50), indent=2)


@mcp.resource("aura://routines", name="Routines", description="Available routines")
def resource_routines() -> str:
    return json.dumps(orchestrator.list_routines(), indent=2)


@mcp.resource("aura://privacy-policy", name="Privacy Policy", description="Data-retention and privacy rules")
def resource_privacy() -> str:
    return json.dumps(
        {
            "retention": "Camera frames are processed transiently and not retained.",
            "no_face_identification": True,
            "no_person_identification": True,
            "event_memory": "Stored locally; user can clear at any time.",
            "security_actions_require_confirmation": True,
        },
        indent=2,
    )


@mcp.resource("aura://user/preferences", name="User Preferences", description="Accessibility and privacy preferences")
def resource_prefs() -> str:
    return json.dumps(_PREFS, indent=2)
