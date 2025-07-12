from mcp.server.fastmcp import FastMCP
from typing import Any
import json
import logging

from .database import create_tables
from .sync_service import sync_service

logger = logging.getLogger(__name__)

mcp: FastMCP = FastMCP("wanikani-mcp")


@mcp.tool()
async def get_status() -> dict[str, Any]:
    """Get current WaniKani status including lessons, reviews, and level"""
    return {
        "level": 5,
        "lessons_available": 12,
        "reviews_available": 23,
        "next_review_time": "2024-01-15T14:00:00Z",
        "username": "demo_user",
    }


@mcp.tool()
async def get_leeches(limit: int = 10) -> dict[str, Any]:
    """Get problematic items that need extra practice"""
    return {
        "leeches": [
            {"characters": "人", "meaning": "person", "incorrect_count": 5},
            {"characters": "水", "meaning": "water", "incorrect_count": 4},
            {"characters": "火", "meaning": "fire", "incorrect_count": 3},
        ][:limit],
        "total_leeches": 15,
    }


@mcp.tool()
async def sync_data() -> dict[str, str]:
    """Manually trigger synchronization with WaniKani API"""
    return {
        "status": "success",
        "message": "Data sync initiated. This may take a few minutes to complete.",
    }


@mcp.resource("wanikani://user_progress/{user_id}")
async def user_progress(user_id: str) -> str:
    """Current user progress and statistics"""
    return json.dumps(
        {
            "user_id": user_id,
            "username": "demo_user",
            "level": 5,
            "lessons_available": 12,
            "reviews_available": 23,
            "next_review_time": "2024-01-15T14:00:00Z",
            "last_sync": None,
        }
    )


@mcp.resource("wanikani://review_forecast/{user_id}")
async def review_forecast(user_id: str) -> str:
    """Timeline of upcoming reviews"""
    return json.dumps(
        {
            "user_id": user_id,
            "forecast": [
                {"time": "2024-01-15T14:00:00Z", "count": 23},
                {"time": "2024-01-15T20:00:00Z", "count": 15},
                {"time": "2024-01-16T08:00:00Z", "count": 31},
            ],
        }
    )


@mcp.resource("wanikani://item_database/{user_id}")
async def item_database(user_id: str) -> str:
    """Searchable collection of user's WaniKani items"""
    return json.dumps(
        {
            "user_id": user_id,
            "items": [
                {"id": 1, "characters": "人", "meaning": "person", "level": 1},
                {"id": 2, "characters": "水", "meaning": "water", "level": 1},
                {"id": 3, "characters": "火", "meaning": "fire", "level": 2},
            ],
        }
    )


async def startup_event():
    """Initialize the application"""
    create_tables()
    await sync_service.start()
    logger.info("WaniKani MCP server started with background sync")


async def shutdown_event():
    """Clean up on shutdown"""
    await sync_service.stop()
    logger.info("WaniKani MCP server stopped")


def create_app():
    """Create and configure the FastMCP application"""
    # FastMCP doesn't support lifecycle events in the same way
    # We'll handle startup/shutdown in the server manager
    return mcp


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="sse")
