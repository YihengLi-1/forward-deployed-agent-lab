"""Vercel entrypoint: serves the existing FastAPI app plus a one-page demo UI at /."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.responses import HTMLResponse  # noqa: E402

from field_agent_lab.api import app  # noqa: E402

DEMO_HTML = (ROOT / "api" / "demo.html").read_text(encoding="utf-8")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def demo() -> str:
    return DEMO_HTML
