"""Home state model and snapshot logic."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .devices import registry


class HomeStateService:
    def __init__(self):
        self._alerts: List[Dict[str, Any]] = []

    def snapshot(self, room_filter: Optional[str] = None) -> Dict[str, Any]:
        devices = registry.get_all()
        if room_filter:
            room_filter = room_filter.lower()
            devices = [d for d in devices if d["room"].lower() == room_filter]
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "devices": devices,
            "alerts": list(self._alerts),
            "summary": self._build_summary(devices),
        }

    def _build_summary(self, devices: List[Dict[str, Any]]) -> str:
        on_lights = sum(1 for d in devices if d["type"] == "light" and d["state"].get("on"))
        locked_doors = sum(1 for d in devices if d["type"] == "door" and d["state"].get("locked"))
        total_doors = sum(1 for d in devices if d["type"] == "door")
        parts = [
            f"{on_lights} light(s) on",
            f"{locked_doors}/{total_doors} door(s) locked",
        ]
        return "; ".join(parts)

    def add_alert(self, alert: Dict[str, Any]) -> None:
        alert = {**alert, "timestamp": datetime.now(timezone.utc).isoformat()}
        self._alerts.append(alert)

    def clear_alerts(self) -> None:
        self._alerts.clear()


home_state = HomeStateService()
