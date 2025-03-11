"""A simple calculator MCP server."""

from mcp.server import FastMCP

# Create a FastMCP server with calculator tools
CalculatorMCP = FastMCP("Calculator")


@CalculatorMCP.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@CalculatorMCP.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


@CalculatorMCP.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@CalculatorMCP.tool()
def divide(a: int, b: int) -> float | None:
    """Divide two numbers."""
    if b == 0:
        return None
    return a / b


__all__ = ["CalculatorMCP"]


if __name__ == "__main__":
    from mcp_community import run_mcp

    run_mcp(CalculatorMCP)
