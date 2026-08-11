from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Route(str, Enum):
    URGENT_HANDOFF = "urgent_handoff"
    SCHEDULING = "scheduling"
    KNOWLEDGE = "knowledge"
    GENERAL_HANDOFF = "general_handoff"


class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    customer_id: str | None = Field(default=None, max_length=128)
    locale: str = Field(default="en-US", pattern=r"^[a-z]{2}(?:-[A-Z]{2})?$")
    channel: str = Field(default="web", pattern=r"^(web|voice|sms|mcp)$")


class Citation(BaseModel):
    document_id: str
    title: str
    excerpt: str
    score: float


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]


class AgentResponse(BaseModel):
    request_id: str
    route: Route
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    handoff_required: bool = False
    handoff_reason: str | None = None


class VoiceRequest(AgentRequest):
    channel: str = "voice"
    generate_audio: bool = False


class VoiceResponse(AgentResponse):
    ssml: str
    audio_base64: str | None = None
    audio_format: str | None = None

