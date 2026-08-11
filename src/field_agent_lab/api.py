from __future__ import annotations

import os

from fastapi import FastAPI

from .engine import DEFAULT_KNOWLEDGE_PATH, FieldAgentEngine
from .evaluation import load_jsonl, run_evaluation
from .models import AgentRequest, AgentResponse, VoiceRequest, VoiceResponse
from .tts import MacOSSayProvider, to_ssml


engine = FieldAgentEngine.from_path(
    os.environ.get("FIELD_AGENT_KNOWLEDGE_PATH", str(DEFAULT_KNOWLEDGE_PATH))
)
app = FastAPI(
    title="Forward-Deployed Agent Lab",
    version="0.1.0",
    description="Synthetic service-business agent with grounded answers and explicit handoffs.",
)


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
def readiness() -> dict[str, object]:
    return {"status": "ready", "knowledge_documents": len(engine.knowledge_base.documents)}


@app.post("/v1/agent/respond", response_model=AgentResponse)
def agent_respond(request: AgentRequest) -> AgentResponse:
    return engine.respond(request)


@app.post("/v1/voice/respond", response_model=VoiceResponse)
def voice_respond(request: VoiceRequest) -> VoiceResponse:
    response = engine.respond(request)
    audio_base64 = None
    audio_format = None
    if request.generate_audio:
        provider = MacOSSayProvider()
        audio_base64 = provider.synthesize_base64(response.answer)
        audio_format = provider.audio_format
    return VoiceResponse(
        **response.model_dump(),
        ssml=to_ssml(response.answer, locale=request.locale),
        audio_base64=audio_base64,
        audio_format=audio_format,
    )


@app.post("/v1/evaluations/run")
def evaluate() -> dict[str, object]:
    cases = load_jsonl(DEFAULT_KNOWLEDGE_PATH.parent / "eval_cases.jsonl")
    return run_evaluation(engine, cases).to_dict()


def run() -> None:
    import uvicorn

    uvicorn.run("field_agent_lab.api:app", host="0.0.0.0", port=8000)

