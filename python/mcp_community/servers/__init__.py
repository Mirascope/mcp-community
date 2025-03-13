"""Pre-Built MCP Servers."""

from contextlib import suppress

from .calculator import CalculatorMCP
from .filesystem import FileSystemMCP

with suppress(ImportError):
    from .duckduckgo import DuckDuckGoMCP as DuckDuckGoMCP


__all__ = ["CalculatorMCP", "DuckDuckGoMCP", "FileSystemMCP"]
