"""Example demonstrating a bot using Anthropic with DuckDuckGoMCP.

This script creates a simple bot that:
1. Connects to a local DuckDuckGoMCP server
2. Takes user input from the console
3. Sends the query to Anthropic's Claude
4. Executes tools as requested by Claude in a loop until completion
5. Returns Claude's final response
"""

import asyncio
import multiprocessing
import time

from anthropic import AsyncAnthropic
from anthropic.types import (
    Message,
    ToolParam,
    ToolUseBlock,
    ToolResultBlockParam,
    MessageParam,
)
from mcp_community import mcp_client, run_mcp
from mcp_community.servers.duckduckgo import DuckDuckGoMCP
from rich import print
from mcp import ClientSession


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
        result = await session.call_tool(tool_call.name, tool_call.input)
        tool_results.append(
            ToolResultBlockParam(
                type="tool_result", tool_use_id=tool_call.id, content=result.content
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


def server_process_target(host, port):
    """Target function for the server process."""
    run_mcp(DuckDuckGoMCP, host=host, port=port)


def run_server_in_process(
    host: str = "localhost", port: int = 8000
) -> multiprocessing.Process:
    """Run the DuckDuckGoMCP server in a separate process."""
    print(f"[bold blue]Starting DuckDuckGoMCP server on {host}:{port}...[/bold blue]")

    # Start the server in a new process
    process = multiprocessing.Process(
        target=server_process_target, args=(host, port), daemon=True
    )
    process.start()

    # Wait for the server to start
    print("[bold yellow]Waiting for server to start...[/bold yellow]")
    time.sleep(2)

    return process


async def main() -> None:
    """Run the main application loop."""
    server_process = run_server_in_process()
    url = f"http://localhost:{8000}/sse"
    try:
        async with mcp_client(url) as session:
            print(f"[bold green]Connected to MCP server at {url}[/bold green]")
            list_tools_result = await session.list_tools()
            tools = [
                ToolParam(
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema,
                )
                for tool in list_tools_result.tools
            ]
            while True:
                query = input("\nEnter your query (or 'exit'/'quit' to end): ").strip()
                if query.lower() in ("exit", "quit"):
                    break
                if not query:
                    continue
                print("[bold cyan]Processing query...[/bold cyan]")
                response = await loop(session, query, tools)
                print("\n[bold green](Bot):[/bold green]")
                print(response)

    except Exception as e:
        print(f"[bold red]Error: {str(e)}[/bold red]")
        raise

    finally:
        # Clean up the server process
        print("\n[bold blue]Shutting down server...[/bold blue]")

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
    asyncio.run(main())
