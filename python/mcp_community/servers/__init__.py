"""Pre-Built MCP Servers."""

from contextlib import suppress

from .calculator import CalculatorMCP

with suppress(ImportError):
    from .docker_sandbox import DockerSandboxMCP as DockerSandboxMCP
    from .duckduckgo import DuckDuckGoMCP as DuckDuckGoMCP

__all__ = ["CalculatorMCP", "DockerSandboxMCP", "DuckDuckGoMCP"]
