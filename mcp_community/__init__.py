"""Model Context Protocol Community."""

import importlib.metadata

from .simple_mcp import SimpleMCP

__version__ = importlib.metadata.version("mcp-community")


__all__ = ["SimpleMCP"]
