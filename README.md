# WaniKani MCP Server

This is a WaniKani MCP (Model Context Protocol) server that provides WaniKani data and functionality to AI assistants. It implements the MCP specification using JSON-RPC over HTTP, allowing AI assistants to access user progress, trigger data synchronization, and get learning assistance through defined tools and resources.

## Features

The WaniKani MCP server exposes the following core features programmatically through its API:

*   **Automated Data Synchronization**: Background workers periodically sync with the WaniKani v2 API to keep user data fresh.
*   **Progress and Status Analysis**: Provides real-time data about user progress, current level, and upcoming lessons/reviews.
*   **Leech Identification Algorithm**: Analyzes review history to identify consistently problematic items for targeted learning assistance.
*   **Multi-User Support**: Secure API key-based authentication allows multiple users to access their personal WaniKani data through the same MCP server instance.

### Core MCP Tools:

*   **`get_status`**: Get a real-time snapshot of the user's current WaniKani status (current level, lessons available, upcoming review count, and next review time).
*   **`get_leeches`**: Identify items the user struggles with most ("leeches") with parameters for `threshold` and `limit`.
*   **`sync_data`**: Manually trigger synchronization with WaniKani servers, returning sync status and timestamp.

### MCP Resources:

*   **`user_progress`**: Current user progress and statistics.
*   **`review_forecast`**: Timeline of upcoming reviews.
*   **`item_database`**: Searchable collection of user's WaniKani items.

## Development Stack

*   **Language**: Python with type hints
*   **Linter/Formatter**: Ruff
*   **Typing**: Built-in Python type hints
*   **MCP Framework**: Python MCP SDK
*   **Web Framework**: FastAPI (for HTTP transport)
*   **Database**: PostgreSQL with SQLModel ORM
*   **Migration Tool**: Alembic
*   **Background Jobs**: APScheduler + FastAPI BackgroundTasks
*   **Package Manager**: uv
*   **Task Runner**: Taskfile
*   **Testing**: pytest
*   **Containerization**: Podman
*   **CI/CD**: GitHub Actions
*   **Deployment**: Render
*   **Configuration**: pydantic-settings
*   **WaniKani API Client**: httpx

## Common Development Commands

All Python functionality should be run via `uv run python` to ensure the correct environment.

*   **Install dependencies**: `uv install`
*   **Run linter/formatter**: `uv run ruff check .` and `uv run ruff format .`
*   **Run type checker**: `uvx ty check .`
*   **Run tests**: `uv run pytest`
*   **Run development server**: `task dev` (when implemented)
*   **Build for deployment**: `task build` (when implemented)
*   **Run database migrations**: `uv run alembic upgrade head` (when implemented)

## Code Style Guidelines

*   Use `snake_case` for tool names, parameters, and Python code.
*   Type hints are required; docstrings are not recommended.
*   Focus on clarity over cleverness.
*   Follow TDD with relevant tests (aim for 70% coverage).
*   Authentication via Bearer Token with MCP API keys.
*   MCP-compliant error responses with proper error codes.
*   All tools must be properly registered with clear documentation.
*   Consistent JSON structure for all tool responses.
*   Input validation using Pydantic models for tool parameters.
*   Good naming, logic patterns > lots of comments.

## Deployment & Testing

*   **Deployment**: The application is containerized with Podman and deployed to Render using GitHub Actions for CI/CD.
*   **Testing**: `pytest` is used for unit and integration tests, aiming for 70% test coverage.
