# Anonymized field implementation case study

## Situation

Small service businesses often run critical workflows through phone calls, messaging, staff memory, and disconnected documents. That makes automation less about writing a chatbot and more about learning the operation: who owns each decision, which facts are approved, what must be escalated, and how staff verify that the system is helping.

The author has supported real clinics, wellness businesses, and professional-service teams with agent and workflow implementation. Those engagements produced bilingual role playbooks, front-desk and practitioner training materials, workflow scorecards, and KPI trackers. Client identities, data, code, and operating details are intentionally excluded from this repository.

## What this repository demonstrates

This lab reconstructs the transferable engineering pattern using a fictional organization and synthetic data:

1. Map user requests into knowledge lookup, intake, or human escalation.
2. Ground operational answers in an approved knowledge source and return citations.
3. Prevent the agent from diagnosing, prescribing, making legal determinations, or falsely confirming an appointment.
4. Expose the same workflow through HTTP, voice-ready output, and MCP tools.
5. Evaluate routing, handoff, tool selection, and grounding before deployment.
6. Package the service with health probes, resource constraints, autoscaling, and network policy.

## Product decisions

- **Human confirmation is a feature.** The scheduling tool collects structured intake but never claims that a booking exists.
- **Unknown questions fail closed.** If retrieval cannot find an approved answer, the request is routed to staff.
- **Safety rules remain deterministic.** The compact classifier is an experiment, not the sole safety boundary.
- **Evaluation is separated from anecdotes.** Synthetic benchmark results are published with the dataset and limitations.
- **Adapters keep channels replaceable.** The API, local TTS provider, and MCP server all call the same core engine.

## How this maps to forward-deployed engineering

| Field responsibility | Evidence in this lab |
|---|---|
| Discover the real workflow | Route and handoff model mirrors front-desk operations |
| Translate ambiguity into a product | Structured requests, responses, tool calls, and citations |
| Integrate with customer systems | FastAPI endpoints and MCP tools form replaceable integration boundaries |
| Operate safely | Deterministic escalation, health probes, tests, and evaluation gates |
| Enable nontechnical users | Responses explain the next step instead of exposing internal implementation |
| Prepare for production | Container image and Kubernetes Deployment, Service, HPA, and NetworkPolicy |

## Limitations

This is a technical portfolio project, not a deployed clinical system. It does not store protected health information, create real appointments, or provide medical or legal advice. The evaluation dataset is synthetic and small; its scores show reproducibility on committed cases, not general production performance.

