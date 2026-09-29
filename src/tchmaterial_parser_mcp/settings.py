"""Runtime settings for the local MCP server."""

from __future__ import annotations

import os
from pathlib import Path


DOWNLOAD_DIR_ENV = "TCHMATERIAL_MCP_DOWNLOAD_DIR"


def download_directory() -> Path:
    """Return the server-controlled download root."""

    configured = os.getenv(DOWNLOAD_DIR_ENV)
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / "Downloads" / "tchMaterial-parser").resolve()

