from __future__ import annotations

import base64
import html
import subprocess
import tempfile
from pathlib import Path


def to_ssml(text: str, *, locale: str = "en-US") -> str:
    safe_text = html.escape(text, quote=False)
    return f'<speak xml:lang="{locale}"><prosody rate="95%">{safe_text}</prosody></speak>'


class MacOSSayProvider:
    """Local TTS adapter. It sends no text to an external service."""

    audio_format = "aiff"

    def synthesize_base64(self, text: str) -> str:
        executable = Path("/usr/bin/say")
        if not executable.exists():
            raise RuntimeError("macOS say is unavailable")
        with tempfile.TemporaryDirectory(prefix="field-agent-tts-") as temp_dir:
            output_path = Path(temp_dir) / "response.aiff"
            subprocess.run(
                [str(executable), "-o", str(output_path), text],
                check=True,
                capture_output=True,
            )
            return base64.b64encode(output_path.read_bytes()).decode("ascii")

