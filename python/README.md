# Model Context Protocol Community

Goals:

- Community driven
- Implementation details are open-source
- Running, deploying, and connecting to MCP servers is dead simple
- Extremely clear documentation on:
  - How to build an MCP server (fill in the official docs' gaps)
  - How to run/deploy an MCP server
  - How to use an MCP client in your application
- Nice chat UI for using / testing MCP servers

## Available Servers

You can find the list of available servers [here](./mcp_community/servers/README.md)

## Getting Started

First, install the package:

```python
pip install mcp-community
```

Next, try running the `CalculatorMCP` server:

```python
from mcp_community import run_mcp
from mcp_community.servers import CalculatorMCP

run_mcp(CalculatorMCP)
```

By default, this will be running at `http://0.0.0.0:8000/sse`.

Now, connect to the server and run some calculations in a separate process:

```python
import asyncio

from mcp_community import mcp_client


async def run() -> None:
    """Connect to an MCP server and use the calculator tools."""
    async with mcp_client("http://0.0.0.0:8000/sse") as session:
        # List available tools
        list_tools_result = await session.list_tools()
        print("Available Tools:")
        for tool in list_tools_result.tools:
            print(f"- {tool.name}: {tool.description}")

        # Add two numbers together
        args = {"a": 5, "b": 7}
        added = await session.call_tool("add", arguments=args)
        assert added.content[0].type == "text"
        print(f"Addition Result:  {args['a']} + {args['b']} = {added.content[0].text}")


asyncio.run(run())
```

## Usage

MCP Community provides two methods:

- `run_mcp`: runs an MCP server as an SSE application (accepts `Server` or `FastMCP`)
- `mcp_client`: connects to the SSE endpoint for an MCP server

## Hosted Servers

Coming soon...
