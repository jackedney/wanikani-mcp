import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from mcp.types import AnyUrl

# Create MCP server
server = Server("wanikani-mcp")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_status",
            description="Get current WaniKani status including lessons, reviews, and level",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="get_leeches",
            description="Get problematic items that need extra practice",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of leeches to return",
                        "default": 10,
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="sync_data",
            description="Manually trigger synchronization with WaniKani API",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    if name == "get_status":
        return [
            types.TextContent(
                type="text",
                text="Status: Level 5, 12 lessons, 23 reviews available. Next review in 2 hours.",
            )
        ]
    elif name == "get_leeches":
        limit = arguments.get("limit", 10)
        return [
            types.TextContent(
                type="text",
                text=f"Top {limit} leeches: 人 (person), 水 (water), 火 (fire) - these need practice!",
            )
        ]
    elif name == "sync_data":
        return [
            types.TextContent(
                type="text",
                text="Data sync initiated. This may take a few minutes to complete.",
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=AnyUrl("wanikani://user_progress"),
            name="User Progress",
            description="Current user progress and statistics",
            mimeType="application/json",
        ),
        types.Resource(
            uri=AnyUrl("wanikani://review_forecast"),
            name="Review Forecast",
            description="Timeline of upcoming reviews",
            mimeType="application/json",
        ),
        types.Resource(
            uri=AnyUrl("wanikani://item_database"),
            name="Item Database",
            description="Searchable collection of user's WaniKani items",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "wanikani://user_progress":
        return '{"level": 5, "lessons_available": 12, "reviews_available": 23, "next_review_time": "2024-01-15T14:00:00Z"}'
    elif uri == "wanikani://review_forecast":
        return '{"forecast": [{"time": "2024-01-15T14:00:00Z", "count": 23}, {"time": "2024-01-15T20:00:00Z", "count": 15}]}'
    elif uri == "wanikani://item_database":
        return '{"items": [{"id": 1, "characters": "人", "meaning": "person", "level": 1}, {"id": 2, "characters": "水", "meaning": "water", "level": 1}]}'
    else:
        raise ValueError("Resource not found")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
