"""Amazon Bedrock client for AuraAssist.

Provides scene understanding (vision) and briefing/reasoning (text) via the
Bedrock Converse API. Falls back to a deterministic mock when AWS credentials
are not configured so the demo always runs offline.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List, Optional

try:
    import boto3
    from botocore.config import Config
except Exception:  # pragma: no cover
    boto3 = None
    Config = None


VISION_PROMPT = """You are the vision module of an accessibility assistant for blind and low-vision users.
Describe the image as structured JSON only. Rules:
- Return ONLY valid JSON, no markdown.
- Do not identify people by name, face, gender, race, ethnicity, or health condition; report only people_count.
- Use "possibly" or "unclear" in labels when confidence is low.
- Do not invent objects or hazards.
- Prioritize safety- and navigation-relevant details.
- Limit to the few most important objects.
- Provide a short summary suitable for text-to-speech.

JSON schema:
{"room": string, "objects": [{"label": string, "location": string, "confidence": number}],
 "hazards": [{"label": string, "confidence": number}], "people_count": number, "summary": string}
"""


class BedrockClient:
    def __init__(self) -> None:
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.vision_model = os.getenv("BEDROCK_VISION_MODEL", "amazon.nova-lite-v1:0")
        self.reasoning_model = os.getenv("BEDROCK_REASONING_MODEL", "us.amazon.nova-lite-v1:0")
        self._client = None
        self.enabled = bool(
            os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE") or os.getenv("AWS_ROLE_ARN")
        )
        if self.enabled and boto3 is not None:
            try:
                cfg = Config(retries={"max_attempts": 3, "mode": "standard"}) if Config else None
                self._client = boto3.client("bedrock-runtime", region_name=self.region, config=cfg)
            except Exception:
                self._client = None
                self.enabled = False

    # -- Vision ------------------------------------------------------------
    def describe_scene(self, camera_id: str = "kitchen", image_data: Optional[bytes] = None) -> Dict[str, Any]:
        if self.enabled and self._client is not None and image_data:
            try:
                return self._describe_scene_bedrock(camera_id, image_data)
            except Exception:
                return self.describe_scene_mock(camera_id)
        return self.describe_scene_mock(camera_id)

    def _describe_scene_bedrock(self, camera_id: str, image_data: bytes) -> Dict[str, Any]:
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"text": VISION_PROMPT + f"\nCamera room hint: {camera_id}."},
                        {"image": {"format": "jpeg", "source": {"bytes": image_data}}},
                    ],
                }
            ],
            "inferenceConfig": {"maxTokens": 600, "temperature": 0.2},
        }
        resp = self._client.invoke_model(modelId=self.vision_model, body=json.dumps(body))
        payload = json.loads(resp["body"].read())
        text = self._extract_text(body=body, response=payload)
        return self._parse_json_safe(text, camera_id)

    def describe_scene_mock(self, camera_id: str = "kitchen", image_data: Optional[bytes] = None) -> Dict[str, Any]:
        return {
            "room": camera_id or "kitchen",
            "objects": [
                {"label": "mug", "location": "left of sink", "confidence": 0.91},
                {"label": "cutting board", "location": "center counter", "confidence": 0.88},
            ],
            "hazards": [{"label": "knife near counter edge", "confidence": 0.74}],
            "people_count": 0,
            "summary": "A mug and cutting board are on the counter. A knife appears close to the counter edge.",
            "source": "mock",
        }

    # -- Reasoning / briefing ---------------------------------------------
    def generate_briefing(self, events: List[Dict[str, Any]], audience: str = "user") -> str:
        if self.enabled and self._client is not None and events:
            try:
                return self._generate_briefing_bedrock(events, audience)
            except Exception:
                return self.generate_briefing_mock(events, audience)
        return self.generate_briefing_mock(events, audience)

    def _generate_briefing_bedrock(self, events: List[Dict[str, Any]], audience: str) -> str:
        audience_note = (
            "The reader is the resident (possibly blind or low-vision). Be calm, concrete, and spoken-friendly."
            if audience == "user"
            else "The reader is a caregiver. Summarize activity without identifying people or inferring health."
        )
        prompt = (
            "Summarize these smart-home events into a short, calm briefing. "
            "Do not identify people or infer sensitive attributes. "
            + audience_note
            + "\n\nEvents (JSON):\n"
            + json.dumps(events[:50], default=str)
        )
        resp = self._client.converse(
            modelId=self.reasoning_model,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 400, "temperature": 0.3},
        )
        return resp["output"]["message"]["content"][0]["text"].strip()

    def generate_briefing_mock(self, events: List[Dict[str, Any]], audience: str = "user") -> str:
        if not events:
            return "No significant changes were recorded today."
        lines: List[str] = []
        for e in events[:10]:
            ts = (e.get("ts") or "")[:16].replace("T", " ")
            line = f"- {ts} {e.get('event_type', 'event')}"
            if e.get("room"):
                line += f" in {e['room']}"
            if e.get("device_id"):
                line += f" ({e['device_id']})"
            if e.get("action"):
                line += f": {e['action']}"
            lines.append(line)
        prefix = "Daily briefing:" if audience == "user" else "Caregiver briefing:"
        return prefix + "\n" + "\n".join(lines)


bedrock = BedrockClient()
