from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .engine import FieldAgentEngine
from .models import AgentRequest


@dataclass(frozen=True)
class EvaluationResult:
    cases: int
    route_accuracy: float
    handoff_accuracy: float
    tool_accuracy: float
    grounded_answer_rate: float
    failures: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "cases": self.cases,
            "route_accuracy": self.route_accuracy,
            "handoff_accuracy": self.handoff_accuracy,
            "tool_accuracy": self.tool_accuracy,
            "grounded_answer_rate": self.grounded_answer_rate,
            "failures": self.failures,
        }


def load_jsonl(path: str | Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_evaluation(engine: FieldAgentEngine, cases: list[dict[str, object]]) -> EvaluationResult:
    route_matches = 0
    handoff_matches = 0
    tool_matches = 0
    knowledge_cases = 0
    grounded_knowledge_answers = 0
    failures: list[dict[str, object]] = []

    for index, case in enumerate(cases):
        response = engine.respond(
            AgentRequest(
                message=str(case["message"]),
                locale=str(case.get("locale", "en-US")),
                channel=str(case.get("channel", "web")),
            )
        )
        actual_tool = response.tool_calls[0].name if response.tool_calls else None
        expected_tool = case.get("expected_tool")
        route_ok = response.route.value == case["expected_route"]
        handoff_ok = response.handoff_required == case["expected_handoff"]
        tool_ok = actual_tool == expected_tool
        route_matches += int(route_ok)
        handoff_matches += int(handoff_ok)
        tool_matches += int(tool_ok)

        if case["expected_route"] == "knowledge":
            knowledge_cases += 1
            grounded_knowledge_answers += int(bool(response.citations))

        if not (route_ok and handoff_ok and tool_ok):
            failures.append(
                {
                    "case": index,
                    "message": case["message"],
                    "expected_route": case["expected_route"],
                    "actual_route": response.route.value,
                    "expected_handoff": case["expected_handoff"],
                    "actual_handoff": response.handoff_required,
                    "expected_tool": expected_tool,
                    "actual_tool": actual_tool,
                }
            )

    total = len(cases)
    return EvaluationResult(
        cases=total,
        route_accuracy=round(route_matches / total, 4),
        handoff_accuracy=round(handoff_matches / total, 4),
        tool_accuracy=round(tool_matches / total, 4),
        grounded_answer_rate=round(
            grounded_knowledge_answers / knowledge_cases if knowledge_cases else 0.0,
            4,
        ),
        failures=failures,
    )

