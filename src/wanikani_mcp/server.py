import asyncio
import logging
import sys

from .config import settings
from .database import create_tables

# from .http_server import create_app
from .mcp_server import main as run_mcp_stdio
from .sync_service import sync_service


# Configure logging
def setup_logging():
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler for stdio mode (avoid console output)
    import os

    log_file = os.path.join(os.getcwd(), "server.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)


logger = logging.getLogger(__name__)


class ServerManager:
    def __init__(self):
        self.running = False
        self.shutdown_event = asyncio.Event()

    async def start_sync_service(self):
        """Start the background sync service"""
        create_tables()
        await sync_service.start()
        logger.info("Background sync service started")

    async def stop_sync_service(self):
        """Stop the background sync service"""
        await sync_service.stop()
        logger.info("Background sync service stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown_event.set()

    async def run_http_server(self, host: str | None = None, port: int | None = None):
        """Run the HTTP MCP server"""
        logger.error("HTTP server mode not available - http_server.py was removed")
        raise NotImplementedError("HTTP server mode is not implemented")

    async def run_stdio_server(self):
        """Run the stdio MCP server"""
        logger.info("Starting stdio MCP server")
        await self.start_sync_service()

        try:
            # Run the stdio MCP server
            await run_mcp_stdio()
        except Exception as e:
            logger.error(f"Stdio server error: {e}")
        finally:
            await self.stop_sync_service()


async def run_server(
    mode: str = "stdio", host: str | None = None, port: int | None = None
):
    """Run the MCP server in the specified mode"""
    manager = ServerManager()

    if mode == "http":
        await manager.run_http_server(host, port)
    elif mode == "stdio":
        await manager.run_stdio_server()
    else:
        raise ValueError(f"Unknown server mode: {mode}")


def main():
    """Main entry point for the server"""
    # Setup logging first
    setup_logging()

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="WaniKani MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio"],
        default="stdio",
        help="Server mode (only stdio supported)",
    )

    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.mode))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
