#!/usr/bin/env python3
"""MCP server: mcp-midband-retainer - Mid-Band Success Retainer.

The productized invisible tier: a $120/mo named-relationship retainer with quarterly
service reviews, upgrade-path orchestration, priority artifact access, and price-lock
in the billing token. $120/mo is the dominant anchor of the V3 run (133 price mentions,
~2x the next band). Annual ~10x with ~17% discount.
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from tools import TOOLS
from handlers import HANDLERS

SERVICE_NAME = "mcp-midband-retainer"
VERSION = "1.0.0"

app = Server(SERVICE_NAME)


@app.list_tools()
async def list_tools():
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    handler = HANDLERS.get(name)
    if handler is None:
        return [TextContent(type="text", text='{"status": "error", "error": "unknown tool ' + name + '"}')]
    try:
        result = handler(arguments or {})
    except Exception as exc:
        return [TextContent(type="text", text='{"status": "error", "error": "' + str(exc).replace('"', '\\"') + '"}')]
    result.setdefault("status", "ok")
    result.setdefault("tool", name)
    result.setdefault("service", SERVICE_NAME)
    result.setdefault("version", VERSION)
    return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]


async def _main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(_main())