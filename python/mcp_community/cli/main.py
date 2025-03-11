"""Main CLI entrypoint for `mcp-community`."""

import importlib.metadata

from rich import print
from typer import Typer

from .commands import bot_command

app = Typer()

app.command(name="version", help="Show the MCP Community `mc` CLI tool version.")(
    lambda: print(importlib.metadata.version("mcp_community"))
)
app.command(name="bot", help="Run an AI bot with MCP servers")(bot_command)
