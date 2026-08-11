from field_agent_lab.engine import FieldAgentEngine
from field_agent_lab.models import AgentRequest, Route


def make_engine() -> FieldAgentEngine:
    return FieldAgentEngine.from_path()


def test_urgent_message_escalates() -> None:
    response = make_engine().respond(AgentRequest(message="I have chest pain and cannot breathe"))
    assert response.route is Route.URGENT_HANDOFF
    assert response.handoff_required is True
    assert response.tool_calls[0].name == "escalate_to_human"


def test_scheduling_collects_intake_without_false_confirmation() -> None:
    response = make_engine().respond(AgentRequest(message="I want to book an appointment"))
    assert response.route is Route.SCHEDULING
    assert response.handoff_required is False
    assert response.tool_calls[0].name == "collect_intake"
    assert "confirm" in response.answer.lower()


def test_knowledge_response_has_citation() -> None:
    response = make_engine().respond(AgentRequest(message="What are your Saturday business hours?"))
    assert response.route is Route.KNOWLEDGE
    assert response.citations
    assert response.citations[0].document_id == "ops-001"


def test_out_of_scope_question_hands_off() -> None:
    response = make_engine().respond(AgentRequest(message="What is the weather in Chicago?"))
    assert response.route is Route.GENERAL_HANDOFF
    assert response.handoff_required is True

