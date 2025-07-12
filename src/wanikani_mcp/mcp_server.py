import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from mcp.types import AnyUrl
from sqlmodel import Session, select

from .database import get_engine
from .models import (
    User,
    Assignment,
    Subject,
    ReviewStatistic,
    SyncLog,
    SyncType,
    SyncStatus,
)
from .wanikani_client import WaniKaniClient
from .auth import create_user_with_api_keys, verify_mcp_api_key
from .sync_service import sync_service

# Create MCP server
server = Server("wanikani-mcp")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="register_user",
            description="Register a new user with their WaniKani API key to get an MCP API key",
            inputSchema={
                "type": "object",
                "properties": {
                    "wanikani_api_key": {
                        "type": "string",
                        "description": "Your WaniKani API key (get it from https://www.wanikani.com/settings/personal_access_tokens)",
                    }
                },
                "required": ["wanikani_api_key"],
            },
        ),
        types.Tool(
            name="get_status",
            description="Get current WaniKani status including lessons, reviews, and level",
            inputSchema={
                "type": "object",
                "properties": {
                    "mcp_api_key": {
                        "type": "string",
                        "description": "Your MCP API key from registration",
                    }
                },
                "required": ["mcp_api_key"],
            },
        ),
        types.Tool(
            name="get_leeches",
            description="Get problematic items that need extra practice",
            inputSchema={
                "type": "object",
                "properties": {
                    "mcp_api_key": {
                        "type": "string",
                        "description": "Your MCP API key from registration",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of leeches to return",
                        "default": 10,
                    },
                },
                "required": ["mcp_api_key"],
            },
        ),
        types.Tool(
            name="sync_data",
            description="Manually trigger synchronization with WaniKani API",
            inputSchema={
                "type": "object",
                "properties": {
                    "mcp_api_key": {
                        "type": "string",
                        "description": "Your MCP API key from registration",
                    }
                },
                "required": ["mcp_api_key"],
            },
        ),
    ]


async def _get_user_from_mcp_key(mcp_api_key: str) -> User:
    engine = get_engine()
    with Session(engine) as session:
        user = await verify_mcp_api_key(mcp_api_key, session)
        if not user:
            raise ValueError("Invalid MCP API key")
        return user


async def _sync_user_data(user: User) -> int:
    """Sync data for a user and return number of records updated"""
    engine = get_engine()

    # Create sync log
    with Session(engine) as session:
        sync_log = SyncLog(
            user_id=user.id,
            sync_type=SyncType.MANUAL,
            status=SyncStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
        )
        session.add(sync_log)
        session.commit()
        session.refresh(sync_log)

    try:
        client = WaniKaniClient(user.wanikani_api_key)
        records_updated = 0

        # Get user info and update profile
        user_data = await client.get_user()
        with Session(engine) as session:
            db_user = session.get(User, user.id)
            if db_user:
                db_user.username = user_data["data"]["username"]
                db_user.level = user_data["data"]["level"]
                db_user.last_sync = datetime.now(timezone.utc)
                session.add(db_user)
                session.commit()
                records_updated += 1

        # For now, just update user info
        # TODO: Implement full sync of subjects, assignments, reviews, etc.

        await client.close()

        # Update sync log
        with Session(engine) as session:
            db_sync_log = session.get(SyncLog, sync_log.id)
            if db_sync_log:
                db_sync_log.status = SyncStatus.SUCCESS
                db_sync_log.records_updated = records_updated
                db_sync_log.completed_at = datetime.now(timezone.utc)
                session.add(db_sync_log)
                session.commit()

        return records_updated

    except Exception as e:
        # Update sync log with error
        with Session(engine) as session:
            db_sync_log = session.get(SyncLog, sync_log.id)
            if db_sync_log:
                db_sync_log.status = SyncStatus.ERROR
                db_sync_log.error_message = str(e)
                db_sync_log.completed_at = datetime.now(timezone.utc)
                session.add(db_sync_log)
                session.commit()
        raise


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    try:
        if name == "register_user":
            wanikani_api_key = arguments["wanikani_api_key"]

            # Test the API key first
            client = WaniKaniClient(wanikani_api_key)
            try:
                user_data = await client.get_user()
                username = user_data["data"]["username"]
                level = user_data["data"]["level"]
            except Exception as e:
                await client.close()
                return [
                    types.TextContent(
                        type="text",
                        text=f"Invalid WaniKani API key: {str(e)}",
                    )
                ]
            finally:
                await client.close()

            # Create user
            engine = get_engine()
            with Session(engine) as session:
                # Check if user already exists
                existing_user = session.exec(
                    select(User).where(User.wanikani_api_key == wanikani_api_key)
                ).first()

                if existing_user:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"User already registered. Your MCP API key is: {existing_user.mcp_api_key}",
                        )
                    ]

                user, mcp_api_key = await create_user_with_api_keys(
                    wanikani_api_key, username, level, session
                )

                return [
                    types.TextContent(
                        type="text",
                        text=f"Registration successful! Your MCP API key is: {mcp_api_key}\n\nSave this key securely - you'll need it for all other operations.",
                    )
                ]

        elif name == "get_status":
            mcp_api_key = arguments["mcp_api_key"]
            user = await _get_user_from_mcp_key(mcp_api_key)

            engine = get_engine()
            with Session(engine) as session:
                now = datetime.now(timezone.utc)

                # Count available lessons (srs_stage = 0, available now or no available_at)
                lessons_count = session.exec(
                    select(Assignment).where(
                        Assignment.user_id == user.id,
                        Assignment.srs_stage == 0,
                        not Assignment.hidden,
                        (Assignment.available_at <= now)
                        | Assignment.available_at.is_(None),
                    )
                ).all()

                # Count available reviews (srs_stage > 0, available now or no available_at)
                reviews_count = session.exec(
                    select(Assignment).where(
                        Assignment.user_id == user.id,
                        Assignment.srs_stage > 0,
                        not Assignment.hidden,
                        (Assignment.available_at <= now)
                        | Assignment.available_at.is_(None),
                    )
                ).all()

                # Find next review time
                next_review = session.exec(
                    select(Assignment)
                    .where(
                        Assignment.user_id == user.id,
                        Assignment.srs_stage > 0,
                        not Assignment.hidden,
                        Assignment.available_at > now,
                    )
                    .order_by(Assignment.available_at)
                ).first()

                next_review_text = (
                    "No upcoming reviews"
                    if not next_review
                    else f"Next review at {next_review.available_at}"
                )

                return [
                    types.TextContent(
                        type="text",
                        text=f"WaniKani Status for {user.username}:\nLevel: {user.level}\nLessons available: {len(lessons_count)}\nReviews available: {len(reviews_count)}\n{next_review_text}",
                    )
                ]

        elif name == "get_leeches":
            mcp_api_key = arguments["mcp_api_key"]
            limit = arguments.get("limit", 10)
            user = await _get_user_from_mcp_key(mcp_api_key)

            engine = get_engine()
            with Session(engine) as session:
                # Find items with low accuracy rates (leeches)
                leeches = session.exec(
                    select(ReviewStatistic, Subject)
                    .join(Subject)
                    .where(
                        ReviewStatistic.user_id == user.id,
                        ReviewStatistic.percentage_correct < 70,
                        ReviewStatistic.meaning_incorrect
                        + ReviewStatistic.reading_incorrect
                        > 3,
                    )
                    .order_by(ReviewStatistic.percentage_correct)
                    .limit(limit)
                ).all()

                if not leeches:
                    return [
                        types.TextContent(
                            type="text",
                            text="No leeches found! You're doing great!",
                        )
                    ]

                leech_text = f"Top {len(leeches)} leeches (items needing practice):\n\n"
                for stat, subject in leeches:
                    accuracy = stat.percentage_correct
                    total_errors = stat.meaning_incorrect + stat.reading_incorrect
                    meanings = [
                        m["meaning"] for m in subject.meanings if m.get("primary")
                    ]
                    meaning_text = meanings[0] if meanings else "Unknown"

                    leech_text += f"• {subject.characters or subject.slug} ({meaning_text}) - {accuracy}% accuracy, {total_errors} errors\n"

                return [
                    types.TextContent(
                        type="text",
                        text=leech_text,
                    )
                ]

        elif name == "sync_data":
            mcp_api_key = arguments["mcp_api_key"]
            user = await _get_user_from_mcp_key(mcp_api_key)

            # Use the enhanced sync service
            records_updated = await sync_service._sync_user_data(user)

            return [
                types.TextContent(
                    type="text",
                    text=f"Data sync completed! Updated {records_updated} records including subjects, assignments, and review statistics.",
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except ValueError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"Unexpected error: {str(e)}",
            )
        ]


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
    try:
        # Parse the URI to extract the resource type and MCP API key
        # Expected format: wanikani://resource_type?mcp_api_key=key
        if not uri.startswith("wanikani://"):
            raise ValueError("Invalid resource URI")

        parts = uri.replace("wanikani://", "").split("?")
        resource_type = parts[0]

        # Extract MCP API key from query parameters
        mcp_api_key = None
        if len(parts) > 1:
            query_params = dict(
                param.split("=") for param in parts[1].split("&") if "=" in param
            )
            mcp_api_key = query_params.get("mcp_api_key")

        if not mcp_api_key:
            return '{"error": "MCP API key required in query parameters"}'

        # Validate user
        try:
            user = await _get_user_from_mcp_key(mcp_api_key)
        except ValueError:
            return '{"error": "Invalid MCP API key"}'

        engine = get_engine()

        if resource_type == "user_progress":
            with Session(engine) as session:
                # Get current lesson and review counts
                lessons_count = len(
                    session.exec(
                        select(Assignment).where(
                            Assignment.user_id == user.id,
                            Assignment.srs_stage == 0,
                            Assignment.available_at <= datetime.now(timezone.utc),
                        )
                    ).all()
                )

                reviews_count = len(
                    session.exec(
                        select(Assignment).where(
                            Assignment.user_id == user.id,
                            Assignment.srs_stage > 0,
                            Assignment.available_at <= datetime.now(timezone.utc),
                        )
                    ).all()
                )

                next_review = session.exec(
                    select(Assignment)
                    .where(
                        Assignment.user_id == user.id,
                        Assignment.srs_stage > 0,
                        Assignment.available_at > datetime.now(timezone.utc),
                    )
                    .order_by(Assignment.available_at)
                ).first()

                return json.dumps(
                    {
                        "user_id": user.id,
                        "username": user.username,
                        "level": user.level,
                        "lessons_available": lessons_count,
                        "reviews_available": reviews_count,
                        "next_review_time": next_review.available_at.isoformat()
                        if next_review
                        else None,
                        "last_sync": user.last_sync.isoformat()
                        if user.last_sync
                        else None,
                        "subscription_active": user.subscription_active,
                    }
                )

        elif resource_type == "review_forecast":
            with Session(engine) as session:
                # Get upcoming reviews grouped by hour
                upcoming_assignments = session.exec(
                    select(Assignment)
                    .where(
                        Assignment.user_id == user.id,
                        Assignment.srs_stage > 0,
                        Assignment.available_at > datetime.now(timezone.utc),
                    )
                    .order_by(Assignment.available_at)
                ).all()

                # Group by hour
                forecast = {}
                for assignment in upcoming_assignments:
                    hour_key = assignment.available_at.replace(
                        minute=0, second=0, microsecond=0
                    )
                    hour_str = hour_key.isoformat()
                    forecast[hour_str] = forecast.get(hour_str, 0) + 1

                forecast_list = [
                    {"time": time, "count": count}
                    for time, count in sorted(forecast.items())
                ]

                return json.dumps(
                    {
                        "user_id": user.id,
                        "forecast": forecast_list[:24],  # Next 24 hours
                    }
                )

        elif resource_type == "item_database":
            with Session(engine) as session:
                # Get user's subjects with assignment info
                subjects_with_assignments = session.exec(
                    select(Subject, Assignment)
                    .join(Assignment)
                    .where(Assignment.user_id == user.id)
                    .order_by(Subject.level, Subject.id)
                ).all()

                items = []
                for subject, assignment in subjects_with_assignments:
                    primary_meaning = next(
                        (m["meaning"] for m in subject.meanings if m.get("primary")),
                        "Unknown",
                    )
                    items.append(
                        {
                            "id": subject.id,
                            "characters": subject.characters,
                            "slug": subject.slug,
                            "meaning": primary_meaning,
                            "level": subject.level,
                            "type": subject.object_type,
                            "srs_stage": assignment.srs_stage,
                            "available_at": assignment.available_at.isoformat()
                            if assignment.available_at
                            else None,
                        }
                    )

                return json.dumps(
                    {
                        "user_id": user.id,
                        "total_items": len(items),
                        "items": items,
                    }
                )

        else:
            return '{"error": "Unknown resource type"}'

    except Exception as e:
        return json.dumps({"error": f"Resource error: {str(e)}"})


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
