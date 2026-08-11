from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .engine import FieldAgentEngine
from .mcp_tools import collect_intake as collect_intake_impl
from .mcp_tools import escalate_to_human as escalate_to_human_impl
from .mcp_tools import search_service_knowledge as search_service_knowledge_impl


engine = FieldAgentEngine.from_path()
mcp = FastMCP("forward-deployed-agent-lab")


@mcp.tool()
def search_service_knowledge(query: str, locale: str = "en-US") -> dict[str, object]:
    """Search approved service-business knowledge and return citations."""
    return search_service_knowledge_impl(engine, query, locale)


@mcp.tool()
def collect_intake(
    name: str,
    callback_number: str,
    service: str,
    preferred_time: str,
) -> dict[str, object]:
    """Collect scheduling details without claiming that an appointment is confirmed."""
    return collect_intake_impl(name, callback_number, service, preferred_time)


@mcp.tool()
def escalate_to_human(summary: str, priority: str = "normal") -> dict[str, str]:
    """Queue a request for a human staff member."""
    return escalate_to_human_impl(summary, priority)


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()

