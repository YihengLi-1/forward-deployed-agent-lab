from __future__ import annotations

import json
from pathlib import Path

from field_agent_lab.engine import FieldAgentEngine
from field_agent_lab.evaluation import load_jsonl, run_evaluation


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    engine = FieldAgentEngine.from_path(PROJECT_ROOT / "data" / "knowledge.json")
    cases = load_jsonl(PROJECT_ROOT / "data" / "eval_cases.jsonl")
    report = run_evaluation(engine, cases).to_dict()
    output_path = PROJECT_ROOT / "artifacts" / "eval_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

