"""Pre-Built MCP Servers."""

from contextlib import suppress

from .calculator import CalculatorMCP

with suppress(ImportError):
    from .duckduckgo import DuckDuckGoMCP as DuckDuckGoMCP
    from .google_calendar import GoogleCalendarMCP as GoogleCalendarMCP


__all__ = ["CalculatorMCP", "DuckDuckGoMCP", "GoogleCalendarMCP"]
