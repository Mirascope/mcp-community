"""Model Context Protocol Community."""

import importlib.metadata
from contextlib import suppress

from .run import mcp_client, run_mcp, run_mcp_async

with suppress(ImportError):
    from . import servers as servers

__version__ = importlib.metadata.version("mcp-community")


__all__ = [
    "__version__",
    "mcp_client",
    "run_mcp",
    "run_mcp_async",
    "servers",
]
