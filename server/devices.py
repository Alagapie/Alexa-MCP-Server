"""Mock smart-home devices for AuraAssist."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Device:
    id: str
    name: str
    type: str  # door, light, plug, thermostat, sensor, camera
    room: str
    state: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class DeviceRegistry:
    def __init__(self):
        now = datetime.now(timezone.utc).isoformat()
        self.devices: Dict[str, Device] = {
            "front_door": Device(
                id="front_door",
                name="Front Door",
                type="door",
                room="entry",
                state={"locked": True, "open": False, "last_updated": now},
            ),
            "back_door": Device(
                id="back_door",
                name="Back Door",
                type="door",
                room="kitchen",
                state={"locked": True, "open": False, "last_updated": now},
            ),
            "living_room_light": Device(
                id="living_room_light",
                name="Living Room Light",
                type="light",
                room="living_room",
                state={"on": False, "brightness": 80, "last_updated": now},
            ),
            "kitchen_light": Device(
                id="kitchen_light",
                name="Kitchen Light",
                type="light",
                room="kitchen",
                state={"on": False, "brightness": 80, "last_updated": now},
            ),
            "bedroom_light": Device(
                id="bedroom_light",
                name="Bedroom Light",
                type="light",
                room="bedroom",
                state={"on": False, "brightness": 60, "last_updated": now},
            ),
            "coffee_plug": Device(
                id="coffee_plug",
                name="Coffee Maker Plug",
                type="plug",
                room="kitchen",
                state={"on": False, "last_updated": now},
            ),
            "thermostat": Device(
                id="thermostat",
                name="Thermostat",
                type="thermostat",
                room="living_room",
                state={"mode": "heat", "temperature": 22, "last_updated": now},
            ),
            "kitchen_camera": Device(
                id="kitchen_camera",
                name="Kitchen Camera",
                type="camera",
                room="kitchen",
                state={"enabled": True, "last_updated": now},
            ),
        }

    def get_all(self) -> List[Dict[str, Any]]:
        return [asdict(d) for d in self.devices.values()]

    def get(self, device_id: str) -> Optional[Dict[str, Any]]:
        d = self.devices.get(device_id)
        return asdict(d) if d else None

    def update(self, device_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        d = self.devices.get(device_id)
        if not d:
            return None
        d.state.update(updates)
        d.state["last_updated"] = datetime.now(timezone.utc).isoformat()
        return asdict(d)


registry = DeviceRegistry()
