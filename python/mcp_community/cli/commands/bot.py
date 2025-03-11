"""CLI tool for interacting with MCP servers using Anthropic.

This tool creates a simple bot that:
1. Connects to multiple local MCP servers (e.g., calculator, duckduckgo)
2. Takes user input from the console
3. Sends the query to Anthropic's Claude
4. Executes tools as requested by Claude in a loop until completion
5. Returns Claude's final response
"""

import asyncio
import importlib
import multiprocessing
import time
from contextlib import AsyncExitStack
from typing import Annotated

import typer
from anthropic import AsyncAnthropic
from anthropic.types import (
    Message,
    MessageParam,
    ToolParam,
    ToolResultBlockParam,
    ToolUseBlock,
)
from mcp import ClientSession, Tool
from mcp.types import CallToolResult, TextContent
from rich import print

from mcp_community import mcp_client, run_mcp


class CombinedSession(ClientSession):
    """A session that combines multiple MCP sessions and routes tool calls appropriately."""

    def __init__(self, sessions: list[ClientSession]) -> None:
        self.sessions = sessions
        # Build a mapping of tool names to sessions
        self.tool_map: dict[str, ClientSession] = {}

    async def list_all_tools(self) -> list[Tool]:
        """Combine tools from all sessions."""
        all_tools: list[Tool] = []
        for session in self.sessions:
            result = await session.list_tools()
            all_tools.extend(result.tools)

            # Map each tool to its session
            for tool in result.tools:
                self.tool_map[tool.name] = session
        return all_tools

    async def call_tool(
        self, name: str, arguments: dict | None = None
    ) -> CallToolResult:
        """Route the tool call to the appropriate session."""
        if not (session := self.tool_map.get(name)):
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Error: Tool '{name}' not found in any connected server",
                    )
                ]
            )
        return await session.call_tool(name, arguments)

    async def __aenter__(self) -> "CombinedSession":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        """Async context manager exit."""
        # We don't close the sessions here since they'll be closed separately
        pass


client = AsyncAnthropic()


async def call(messages: list, tools: list[ToolParam]) -> Message:
    """Returns the `Message` response from Claude."""
    return await client.messages.create(
        max_tokens=1024,
        model="claude-3-5-sonnet-latest",
        system="You are a helpful web assistant.",
        messages=messages,
        tools=tools,
    )


def collect_content_and_tool_calls(response: Message) -> tuple[str, list[ToolUseBlock]]:
    """Return the content and tool calls from the response."""
    content = ""
    tool_calls = []
    for block in response.content:
        if block.type == "text":
            content += block.text
        elif block.type == "tool_use":
            tool_calls.append(block)
    return content, tool_calls


async def call_tools(
    session: ClientSession, tool_calls: list[ToolUseBlock]
) -> list[ToolResultBlockParam]:
    """Return the tool results from the session."""
    tool_results = []
    for tool_call in tool_calls:
        result = await session.call_tool(tool_call.name, tool_call.input)  # pyright: ignore [reportArgumentType]
        tool_results.append(
            ToolResultBlockParam(
                type="tool_result",
                tool_use_id=tool_call.id,
                content=result.content,  # pyright: ignore [reportArgumentType]
            )
        )
    return tool_results


async def loop(session: ClientSession, query: str, tools: list[ToolParam]) -> str:
    """Return the final response once Claude is done calling tools."""
    messages: list[MessageParam] = [{"role": "user", "content": query}]
    response = await call(messages, tools)
    if isinstance(response.content, str):
        return response.content
    messages.append({"role": "assistant", "content": response.content})
    content = ""
    tool_calls: list[ToolUseBlock] = []
    content, tool_calls = collect_content_and_tool_calls(response)
    if not tool_calls:
        return content
    tool_results = await call_tools(session, tool_calls)
    messages.append({"role": "user", "content": tool_results})
    while tool_calls:
        response = await call(messages, tools)
        messages.append({"role": "assistant", "content": response.content})
        content, tool_calls = collect_content_and_tool_calls(response)
        if not tool_calls:
            return content
        tool_results = await call_tools(session, tool_calls)
        messages.append({"role": "user", "content": tool_results})
    return content


def server_process_target(server: str, port: int) -> None:
    """Target function for the server process."""
    module_path = "mcp_community.servers"
    try:
        server_module = importlib.import_module(f"{module_path}.{server}")
    except ImportError:
        raise ImportError(f"Server {server} not found in {module_path}")
    try:
        server_class = server_module.mcp
    except AttributeError:
        raise AttributeError(f"Server {server} does not have a 'mcp' class")
    run_mcp(server_class, host="localhost", port=port)


def run_server_in_process(server: str, port: int) -> multiprocessing.Process:
    """Run an MCP server in a separate process."""
    print(f"[bold blue]Starting {server} MCP server on localhost:{port}...[/bold blue]")

    # Start the server in a new process
    process = multiprocessing.Process(
        target=server_process_target, args=(server, port), daemon=True
    )
    process.start()

    # Wait for the server to start
    print(f"[bold yellow]Waiting for {server} server to start...[/bold yellow]")
    time.sleep(2)

    return process


async def run_bot(servers: list[str], port: int) -> None:
    """Run the main application loop with multiple servers."""
    server_processes: list[multiprocessing.Process] = []
    sessions: list[ClientSession] = []

    for i, server in enumerate(servers):
        process = run_server_in_process(server, port + i)
        server_processes.append(process)

    try:
        async with AsyncExitStack() as stack:
            connections: list[ClientSession] = []
            for i in range(len(servers)):
                connection = await stack.enter_async_context(
                    mcp_client(f"http://localhost:{port + i}/sse")
                )
                connections.append(connection)

            combined_session = CombinedSession(connections)
            async with combined_session:
                all_tools = await combined_session.list_all_tools()
                converted_tools = [
                    ToolParam(
                        name=tool.name,
                        description=tool.description or "",
                        input_schema=tool.inputSchema,
                    )
                    for tool in all_tools
                ]
                while True:
                    query = input(
                        "\nEnter your query (or 'exit'/'quit' to end): "
                    ).strip()
                    if query.lower() in ("exit", "quit"):
                        break
                    if not query:
                        continue
                    print("[bold cyan]Processing query...[/bold cyan]")
                    response = await loop(combined_session, query, converted_tools)
                    print("\n[bold green](Bot):[/bold green]")
                    print(response)

    except Exception as e:
        print(f"[bold red]Error: {str(e)}[/bold red]")
        raise

    finally:
        # Clean up all sessions
        for session in sessions:
            await session.__aexit__(None, None, None)

        # Clean up all server processes
        print("\n[bold blue]Shutting down servers...[/bold blue]")
        for process in server_processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)

                if process.is_alive():
                    print(
                        "[bold yellow]Server process still running, killing...[/bold yellow]"
                    )
                    process.kill()
                    process.join(timeout=1)

        print("[bold green]All servers shutdown complete[/bold green]")


app = typer.Typer()


@app.command()
def bot_command(
    servers: Annotated[
        str,
        typer.Option(
            help="Comma-separated list of servers to run (e.g., 'calculator,duckduckgo')"
        ),
    ] = "calculator",
    port: Annotated[
        int, typer.Option(help="Starting port number (each server will use port+n)")
    ] = 8000,
) -> None:
    """Run MCP servers and start a chat session with a bot with access to them."""
    server_list = [s.strip() for s in servers.split(",")]
    asyncio.run(run_bot(servers=server_list, port=port))


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
