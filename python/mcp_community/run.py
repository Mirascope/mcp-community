"""Utilities for running MCP servers and clients."""

import asyncio
import contextlib
from collections.abc import AsyncGenerator, Callable
from typing import Literal, TypeVar

import uvicorn
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.server import FastMCP, Server
from mcp.server.sse import SseServerTransport

T = TypeVar("T")


async def run_mcp_async(
    mcp_server: Server | FastMCP,
    host: str = "0.0.0.0",
    port: int = 8000,
    debug: bool = False,
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> None:
    """Run an MCP server using server-sent events (SSE) over HTTP.

    Args:
        mcp_server: The MCP server instance to run (FastMCP or Server)
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8000)
    """
    if isinstance(mcp_server, FastMCP):
        mcp_server.settings.host = host
        mcp_server.settings.port = port
        mcp_server.settings.debug = debug
        mcp_server.settings.log_level = log_level
        await mcp_server.run_sse_async()
    else:
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request) -> None:  # noqa: ANN001
            """Handle incoming SSE connections."""
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await mcp_server.run(
                    streams[0],
                    streams[1],
                    mcp_server.create_initialization_options(),
                )

        starlette_app = Starlette(
            debug=debug,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        config = uvicorn.Config(
            starlette_app,
            host=host,
            port=port,
            log_level=log_level.lower(),
        )
        server = uvicorn.Server(config)
        await server.serve()


def run_mcp(
    mcp_server: Server | FastMCP,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    """Run an MCP server using server-sent events (SSE) over HTTP.

    This is a synchronous wrapper around run_mcp_server.

    Args:
        mcp_server: The MCP server instance to run (FastMCP or Server)
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8000)
    """
    asyncio.run(run_mcp_async(mcp_server, host, port))


@contextlib.asynccontextmanager
async def mcp_client(
    url: str,
    sampling_callback: Callable | None = None,
) -> AsyncGenerator[ClientSession, None]:
    """Connect to an MCP server over SSE.

    Args:
        url: The URL of the SSE MCP server
        sampling_callback: Optional callback for handling sampling messages

    Yields:
        An initialized MCP client session

    Example:
        ```python
        async with mcp_client("http://localhost:8000") as session:
            tools = await session.list_tools()
            result = await session.call_tool("add", arguments={"a": 1, "b": 2})
        ```
    """
    async with (
        sse_client(url=url) as (read, write),
        ClientSession(read, write, sampling_callback=sampling_callback) as session,
    ):
        # Initialize the connection
        await session.initialize()
        yield session
