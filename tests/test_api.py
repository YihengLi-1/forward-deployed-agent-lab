from fastapi.testclient import TestClient

from field_agent_lab.api import app


client = TestClient(app)


def test_health_and_readiness() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    readiness = client.get("/readyz").json()
    assert readiness["status"] == "ready"
    assert readiness["knowledge_documents"] >= 8


def test_agent_endpoint() -> None:
    response = client.post(
        "/v1/agent/respond",
        json={"message": "Do you accept HSA cards?", "locale": "en-US"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["route"] == "knowledge"
    assert payload["citations"]


def test_voice_endpoint_returns_ssml_without_external_call() -> None:
    response = client.post(
        "/v1/voice/respond",
        json={"message": "When are you open?", "generate_audio": False},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ssml"].startswith("<speak")
    assert payload["audio_base64"] is None


def test_evaluation_endpoint() -> None:
    response = client.post("/v1/evaluations/run")
    assert response.status_code == 200
    assert response.json()["cases"] == 16

