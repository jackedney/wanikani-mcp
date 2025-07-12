# WaniKani MCP Server

## Empowering AI Assistants with WaniKani Data

The WaniKani MCP (Model Context Protocol) Server acts as a bridge, providing AI assistants with seamless access to WaniKani user data and functionality. By implementing the MCP specification over JSON-RPC via HTTP, this server enables AI assistants to retrieve user progress, trigger data synchronization, and offer personalized learning assistance.

## Key Features

This server exposes powerful capabilities designed to enhance the WaniKani learning experience through AI:

*   **Automated Data Synchronization**: Keeps user data fresh and up-to-date by periodically syncing with the official WaniKani v2 API.
*   **Real-time Progress & Status**: Provides AI assistants with instant access to a user's current WaniKani level, available lessons, upcoming reviews, and next review times.
*   **Intelligent Leech Identification**: Utilizes an advanced algorithm to analyze review history and pinpoint consistently problematic items ("leeches"), enabling targeted learning strategies.
*   **Multi-User Support**: Securely manages data for multiple users through API key-based authentication, ensuring personalized and private access.

### Core MCP Tools for AI Assistants:

AI assistants can leverage the following tools to interact with the WaniKani data:

*   **`get_status`**: Obtain a snapshot of the user's current WaniKani learning status.
*   **`get_leeches`**: Identify and retrieve a list of the user's most challenging items.
*   **`sync_data`**: Manually initiate a data synchronization with WaniKani servers.

### Available MCP Resources:

Beyond direct tools, the server also exposes structured data resources:

*   **`user_progress`**: Comprehensive statistics and progress details for a user.
*   **`review_forecast`**: A timeline of upcoming reviews.
*   **`item_database`**: A searchable collection of all WaniKani items relevant to the user.

## Technology Stack

Built with modern and robust technologies to ensure performance and scalability:

*   **Backend**: Python with FastAPI
*   **Database**: PostgreSQL with SQLModel ORM
*   **Background Tasks**: APScheduler
*   **Containerization**: Podman
*   **Deployment**: Render

## Getting Started (For Developers)

To set up the project locally, ensure you have `uv` installed, then:

1.  **Install dependencies**: `uv install`
2.  **Run tests**: `uv run pytest`

For more detailed development information, please refer to the project's internal documentation.

## Contribution

We welcome contributions! Please refer to our contribution guidelines (link to be added) for more information.