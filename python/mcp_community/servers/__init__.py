"""Pre-Built MCP Servers."""

from contextlib import suppress

from .calculator import CalculatorMCP

with suppress(ImportError):
    from .duckduckgo import DuckDuckGoMCP as DuckDuckGoMCP
    from .slack import SlackMCP as SlackMCP


__all__ = ["CalculatorMCP", "DuckDuckGoMCP", "SlackMCP"]
