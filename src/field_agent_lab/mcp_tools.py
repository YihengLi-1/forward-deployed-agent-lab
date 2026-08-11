from __future__ import annotations

from .engine import FieldAgentEngine
from .models import AgentRequest


def search_service_knowledge(engine: FieldAgentEngine, query: str, locale: str = "en-US") -> dict[str, object]:
    response = engine.respond(AgentRequest(message=query, locale=locale, channel="mcp"))
    return response.model_dump(mode="json")


def collect_intake(
    name: str,
    callback_number: str,
    service: str,
    preferred_time: str,
) -> dict[str, object]:
    return {
        "status": "pending_confirmation",
        "name": name,
        "callback_number": callback_number,
        "service": service,
        "preferred_time": preferred_time,
        "message": "A staff member must confirm availability before an appointment is created.",
    }


def escalate_to_human(summary: str, priority: str = "normal") -> dict[str, str]:
    normalized_priority = "urgent" if priority.lower() == "urgent" else "normal"
    return {
        "status": "queued",
        "priority": normalized_priority,
        "summary": summary[:500],
    }

