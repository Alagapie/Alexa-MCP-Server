"""Routine orchestrator with confirmation guardrails."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .devices import registry
from .event_store import event_store


ROUTINES: Dict[str, Dict[str, Any]] = {
    "bedtime": {
        "description": "Secure the home and prepare it for sleep",
        "requires_confirmation": True,
        "steps": [
            {"action": "check_doors", "description": "Check door locks"},
            {"action": "lock_device", "target": "back_door", "description": "Lock back door if unlocked"},
            {"action": "control_device", "target": "living_room_light", "value": "off", "description": "Turn off living room light"},
            {"action": "control_device", "target": "kitchen_light", "value": "off", "description": "Turn off kitchen light"},
            {"action": "set_thermostat", "value": 22, "description": "Set thermostat to 22°C"},
        ],
    },
    "leaving_home": {
        "description": "Prepare the home for absence",
        "requires_confirmation": True,
        "steps": [
            {"action": "check_doors", "description": "Check door locks"},
            {"action": "lock_device", "target": "front_door", "description": "Lock front door"},
            {"action": "control_device", "target": "living_room_light", "value": "off"},
            {"action": "control_device", "target": "kitchen_light", "value": "off"},
            {"action": "control_device", "target": "coffee_plug", "value": "off"},
            {"action": "set_thermostat", "value": 18, "description": "Set thermostat to 18°C"},
        ],
    },
    "morning": {
        "description": "Support calm start to day",
        "requires_confirmation": True,
        "steps": [
            {"action": "control_device", "target": "bedroom_light", "value": "on"},
            {"action": "control_device", "target": "kitchen_light", "value": "on"},
        ],
    },
}


class RoutineOrchestrator:
    def __init__(self):
        pass

    def list_routines(self) -> List[Dict[str, Any]]:
        return [
            {"name": k, "description": v.get("description"), "requires_confirmation": v.get("requires_confirmation", True)}
            for k, v in ROUTINES.items()
        ]

    def run_routine(self, routine_name: str, confirm: bool = False) -> Dict[str, Any]:
        if routine_name not in ROUTINES:
            return {"error": f"Unknown routine: {routine_name}"}
        routine = ROUTINES[routine_name]
        if not confirm and routine.get("requires_confirmation", True):
            plan = self._plan(routine_name, routine)
            return {
                "status": "needs_confirmation",
                "routine": routine_name,
                "description": routine.get("description"),
                "plan": plan,
                "message": self._format_plan_message(plan, routine_name),
            }
        # Execute
        results = []
        for step in routine.get("steps", []):
            res = self._execute_step(step)
            results.append(res)
        summary = self._summarize(results)
        try:
            event_store.add_event(
                event_type="routine_execution",
                action=routine_name,
                details=f"executed with {len(results)} steps",
            )
        except Exception:
            pass
        return {"status": "executed", "routine": routine_name, "results": results, "summary": summary}

    def _plan(self, name: str, routine: Dict[str, Any]) -> List[Dict[str, Any]]:
        planned = []
        for step in routine.get("steps", []):
            planned.append({"step": step.get("action"), "description": step.get("description") or step, "target": step.get("target")})
        return planned

    def _format_plan_message(self, plan: List[Dict[str, Any]], name: str) -> str:
        if name == "bedtime":
            return "The back door may be unlocked and lights may be on. Should I lock the back door, turn off the living-room and kitchen lights, and set the thermostat to 22°C?"
        if name == "leaving_home":
            return "I'll secure the front door, turn off unnecessary devices, and set thermostat to 18°C. Proceed?"
        return f"Ready to run {name} with {len(plan)} steps. Proceed?"

    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        action = step.get("action")
        if action == "check_doors":
            doors = [d for d in registry.get_all() if d["type"] == "door"]
            return {"action": action, "doors": doors}
        if action == "lock_device":
            target = step.get("target")
            d = registry.update(target, {"locked": True, "open": False}) if target else None
            return {"action": action, "target": target, "result": d}
        if action == "control_device":
            target = step.get("target")
            value = step.get("value")
            updates = {"on": value == "on"} if value in ("on", "off") else {}
            d = registry.update(target, updates) if target else None
            return {"action": action, "target": target, "value": value, "result": d}
        if action == "set_thermostat":
            value = step.get("value")
            d = registry.update("thermostat", {"temperature": value})
            return {"action": action, "value": value, "result": d}
        return {"action": action, "status": "skipped"}

    def _summarize(self, results: List[Dict[str, Any]]) -> str:
        return f"Completed {len(results)} steps."


orchestrator = RoutineOrchestrator()
