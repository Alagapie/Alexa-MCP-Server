"""Vision service for scene description."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .bedrock_client import bedrock
from .event_store import event_store


class VisionService:
    def __init__(self):
        pass

    def describe_scene(self, camera_id: str = "kitchen", image_data: Optional[bytes] = None) -> Dict[str, Any]:
        res = bedrock.describe_scene(camera_id, image_data)
        # Store object sightings
        try:
            details = json.dumps(
                {
                    "objects": res.get("objects", []),
                    "hazards": res.get("hazards", []),
                    "summary": res.get("summary"),
                }
            )
            event_store.add_event(
                event_type="object_sighting",
                room=res.get("room") or camera_id,
                details=details,
                confidence=None,
            )
        except Exception:
            pass
        return res


vision = VisionService()
