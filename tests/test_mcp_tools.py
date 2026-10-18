from server.home_state import home_state
from server.routines import orchestrator


def test_home_snapshot():
    snap = home_state.snapshot()
    assert "devices" in snap
    assert len(snap["devices"]) > 0


def test_routine_needs_confirm():
    res = orchestrator.run_routine("bedtime", confirm=False)
    assert res["status"] == "needs_confirmation"


def test_routine_execute():
    res = orchestrator.run_routine("bedtime", confirm=True)
    assert res["status"] == "executed"
