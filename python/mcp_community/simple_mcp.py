"""The SimpleMCP class."""

import inspect
from collections.abc import Callable
from typing import ParamSpec, cast

import mcp.server.stdio
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool
from pydantic import BaseModel
from rich import print

from mirascope.core import BaseTool
from mirascope.core.base._utils import (
    convert_base_model_to_base_tool,
    convert_function_to_base_tool,
    fn_is_async,
)
from mirascope.mcp.tools import MCPTool, ToolUseBlock

_P = ParamSpec("_P")


class SimpleMCP:
    """SimpleMCP Server Implementation."""

    def __init__(
        self,
        name: str,
        version: str = "0.1.0",
        tools: list[Callable | type[BaseTool]] | None = None,
    ) -> None:
        """Initializes an instance of `SimpleMCP`."""
        self.name: str = name
        self.version: str = version
        self.server: Server = Server(name)
        self._tools: dict[str, tuple[Tool, type[MCPTool]]] = {}
        if tools:
            for tool in tools:
                self.tool()(tool)

    def tool(
        self,
    ) -> Callable[[Callable | type[BaseTool]], type[BaseTool]]:
        """Decorator to register tools."""

        def decorator(
            tool: Callable | type[BaseTool],
        ) -> type[BaseTool]:
            if inspect.isclass(tool):
                if issubclass(tool, MCPTool):
                    converted_tool = tool
                else:
                    converted_tool = convert_base_model_to_base_tool(
                        cast(type[BaseModel], tool), MCPTool
                    )
            else:
                converted_tool = convert_function_to_base_tool(tool, MCPTool)
            tool_schema = converted_tool.tool_schema()
            name = tool_schema["name"]
            if name in self._tools:
                # Raise KeyError if tool name already exists
                raise KeyError(f"Tool {name} already exists.")

            self._tools[name] = (
                Tool(
                    name=name,
                    description=tool_schema.get("description"),
                    inputSchema=tool_schema["input_schema"],
                ),
                converted_tool,
            )
            return converted_tool

        return decorator

    async def run(self) -> None:
        """Run the MCP server."""
        print(f"Starting {self.name} server...")

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [tool for tool, _ in self._tools.values()]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name not in self._tools:
                raise KeyError(f"Tool {name} not found.")
            _, tool_type = self._tools[name]

            tool = tool_type.from_tool_call(
                tool_call=ToolUseBlock(id=name, name=name, input=arguments)
            )
            if fn_is_async(tool.call):
                result = await tool.call()
            else:
                result = tool.call()
            return [TextContent(type="text", text=result)]

        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.name,
                    server_version=self.version,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
