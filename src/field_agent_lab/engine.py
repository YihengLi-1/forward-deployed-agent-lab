from __future__ import annotations

import re
import uuid
from pathlib import Path

from .knowledge import KnowledgeBase
from .models import AgentRequest, AgentResponse, Route, ToolCall


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_PATH = PROJECT_ROOT / "data" / "knowledge.json"

URGENT_PATTERNS = (
    r"\b(chest pain|cannot breathe|can't breathe|severe bleeding|unconscious|suicid(?:e|al))\b",
    r"胸痛|无法呼吸|大量出血|失去意识|自杀",
)
SCHEDULING_TERMS = {
    "appointment",
    "book",
    "schedule",
    "reschedule",
    "cancel",
    "availability",
    "预约",
    "改期",
    "取消",
}
RESTRICTED_ADVICE_TERMS = {
    "diagnose",
    "diagnosis",
    "prescribe",
    "dosage",
    "legal advice",
    "guarantee coverage",
    "诊断",
    "开药",
    "剂量",
    "法律意见",
}


class FieldAgentEngine:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base

    @classmethod
    def from_path(cls, path: str | Path = DEFAULT_KNOWLEDGE_PATH) -> "FieldAgentEngine":
        return cls(KnowledgeBase.from_json(path))

    def respond(self, request: AgentRequest) -> AgentResponse:
        message = request.message.strip()
        lowered = message.lower()
        request_id = f"req_{uuid.uuid4().hex[:12]}"

        if any(re.search(pattern, lowered, flags=re.IGNORECASE) for pattern in URGENT_PATTERNS):
            return AgentResponse(
                request_id=request_id,
                route=Route.URGENT_HANDOFF,
                answer=(
                    "This may be urgent. Please call emergency services now. "
                    "I am also routing this conversation to a human staff member."
                ),
                tool_calls=[
                    ToolCall(
                        name="escalate_to_human",
                        arguments={"priority": "urgent", "summary": message[:240]},
                    )
                ],
                handoff_required=True,
                handoff_reason="Potential emergency detected",
            )

        if any(term in lowered for term in RESTRICTED_ADVICE_TERMS):
            return AgentResponse(
                request_id=request_id,
                route=Route.GENERAL_HANDOFF,
                answer=(
                    "I cannot provide a diagnosis, prescription, or legal determination. "
                    "I can collect your question and route it to the appropriate professional."
                ),
                tool_calls=[
                    ToolCall(
                        name="escalate_to_human",
                        arguments={"priority": "normal", "summary": message[:240]},
                    )
                ],
                handoff_required=True,
                handoff_reason="Professional judgment required",
            )

        cancellation_policy_question = (
            "cancel" in lowered
            and any(phrase in lowered for phrase in ("policy", "how early", "how much notice", "what is"))
        )
        if not cancellation_policy_question and any(term in lowered for term in SCHEDULING_TERMS):
            return AgentResponse(
                request_id=request_id,
                route=Route.SCHEDULING,
                answer=(
                    "I can help with that. Please share your preferred date, time window, "
                    "service, and callback number; a staff member will confirm availability."
                ),
                tool_calls=[
                    ToolCall(
                        name="collect_intake",
                        arguments={
                            "customer_id": request.customer_id,
                            "requested_action": "schedule_follow_up",
                            "source_channel": request.channel,
                        },
                    )
                ],
            )

        citations = self.knowledge_base.search(message, locale=request.locale)
        if citations:
            top = citations[0]
            return AgentResponse(
                request_id=request_id,
                route=Route.KNOWLEDGE,
                answer=f"According to the service guide: {top.excerpt}",
                citations=citations,
            )

        return AgentResponse(
            request_id=request_id,
            route=Route.GENERAL_HANDOFF,
            answer=(
                "I do not have enough verified information to answer safely. "
                "I will route this question to a staff member."
            ),
            tool_calls=[
                ToolCall(
                    name="escalate_to_human",
                    arguments={"priority": "normal", "summary": message[:240]},
                )
            ],
            handoff_required=True,
            handoff_reason="No grounded answer found",
        )
