"""A simple calculator MCP server."""

from mcp.server import FastMCP

mcp = FastMCP("Calculator")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def divide(a: int, b: int) -> float | None:
    """Divide two numbers."""
    if b == 0:
        return None
    return a / b


CalculatorMCP = mcp

__all__ = ["CalculatorMCP"]


if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(CalculatorMCP)
