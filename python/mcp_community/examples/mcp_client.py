"""Example demonstrating how to use the mcp_client utility to connect to an MCP SSE server,
running the CalculatorMCP in a separate process and then terminating it."""

import asyncio
import multiprocessing
import time

from mcp_community import mcp_client, run_mcp
from mcp_community.servers.calculator import CalculatorMCP
from rich import print


async def run_client(host: str = "localhost", port: int = 8765) -> None:
    """Connect to an MCP server and use the calculator tools."""
    url = f"http://{host}:{port}/sse"
    print(f"[bold cyan]Connecting to MCP server at {url}...[/bold cyan]")

    try:
        async with mcp_client(url) as session:
            # List available tools
            list_tools_result = await session.list_tools()
            print("\n[bold green]Available tools:[/bold green]")
            for tool in list_tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            # Test calculator operations
            args = {"a": 5, "b": 7}
            print(
                f"\n[bold yellow]Testing calculator operations with a={args['a']}, b={args['b']}[/bold yellow]"
            )

            # add
            added = await session.call_tool("add", arguments=args)
            assert added.content[0].type == "text"
            print(f"  {args['a']} + {args['b']} = {added.content[0].text}")

            # subtract
            subtracted = await session.call_tool("subtract", arguments=args)
            assert subtracted.content[0].type == "text"
            print(f"  {args['a']} - {args['b']} = {subtracted.content[0].text}")

            # multiply
            multiplied = await session.call_tool("multiply", arguments=args)
            assert multiplied.content[0].type == "text"
            print(f"  {args['a']} * {args['b']} = {multiplied.content[0].text}")

            # divide
            divided = await session.call_tool("divide", arguments=args)
            assert divided.content[0].type == "text"
            print(f"  {args['a']} / {args['b']} = {divided.content[0].text}")

            print(
                "\n[bold green]All calculator operations completed successfully![/bold green]"
            )
    except Exception as e:
        print(f"[bold red]Error connecting to server: {str(e)}[/bold red]")
        raise


# This function needs to be at module level for multiprocessing to work
def server_process_target(host, port):
    """Target function for the server process."""
    run_mcp(CalculatorMCP, host=host, port=port)


def run_server_in_process(
    host: str = "localhost", port: int = 8765
) -> multiprocessing.Process:
    """Run the CalculatorMCP server in a separate process."""
    print(f"[bold blue]Starting CalculatorMCP server on {host}:{port}...[/bold blue]")

    # Start the server in a new process with the module-level function
    process = multiprocessing.Process(
        target=server_process_target, args=(host, port), daemon=True
    )
    process.start()

    # Wait a moment for the server to start
    print("[bold yellow]Waiting for server to start...[/bold yellow]")
    time.sleep(2)

    return process


def main() -> None:
    """Run the client example with the CalculatorMCP server in a separate process."""
    host = "localhost"
    port = 8765

    # Start the CalculatorMCP server in a separate process
    server_process = run_server_in_process(host, port)

    try:
        # Run the client
        asyncio.run(run_client(host, port))
    finally:
        # Clean up the server process
        print("\n[bold blue]Shutting down server...[/bold blue]")

        # Terminate the server process
        if server_process.is_alive():
            server_process.terminate()
            server_process.join(timeout=5)

            if server_process.is_alive():
                print(
                    "[bold yellow]Server process still running, killing...[/bold yellow]"
                )
                server_process.kill()
                server_process.join(timeout=1)

        print("[bold green]Server shutdown complete[/bold green]")


if __name__ == "__main__":
    main()
