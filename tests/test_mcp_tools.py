from field_agent_lab.engine import FieldAgentEngine
from field_agent_lab.mcp_tools import collect_intake, escalate_to_human, search_service_knowledge


def test_mcp_knowledge_tool_returns_structured_result() -> None:
    payload = search_service_knowledge(FieldAgentEngine.from_path(), "What services do you offer?")
    assert payload["route"] == "knowledge"
    assert payload["citations"]


def test_mcp_intake_never_claims_confirmation() -> None:
    payload = collect_intake("Alex", "555-0100", "massage", "Friday afternoon")
    assert payload["status"] == "pending_confirmation"
    assert "confirm" in payload["message"].lower()


def test_mcp_escalation_normalizes_priority() -> None:
    payload = escalate_to_human("Possible emergency", "URGENT")
    assert payload["priority"] == "urgent"

