import asyncio
import logging
import signal
import sys
import os
from typing import Optional

from .http_server import create_app
from .mcp_server import main as run_mcp_stdio
from .sync_service import sync_service
from .database import create_tables
from .config import settings


# Configure logging
def setup_logging():
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

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

    async def run_http_server(
        self, host: Optional[str] = None, port: Optional[int] = None
    ):
        """Run the HTTP MCP server"""
        import uvicorn

        # Use config defaults if not provided
        host = host or settings.host
        port = port or int(os.getenv("PORT", settings.port))

        logger.info(f"Starting HTTP MCP server on {host}:{port}")
        await self.start_sync_service()

        try:
            # Set up signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)

            config = uvicorn.Config(
                create_app(), host=host, port=port, log_level=settings.log_level.lower()
            )
            server = uvicorn.Server(config)

            # Run server until shutdown signal
            await server.serve()

        except Exception as e:
            logger.error(f"HTTP server error: {e}")
        finally:
            await self.stop_sync_service()

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
    mode: str = "stdio", host: Optional[str] = None, port: Optional[int] = None
):
    """Run the MCP server in the specified mode"""
    manager = ServerManager()

    if mode == "http":
        await manager.run_http_server(host, port)
    elif mode == "stdio":
        await manager.run_stdio_server()
    else:
        raise ValueError(f"Unknown server mode: {mode}")


if __name__ == "__main__":
    # Setup logging first
    setup_logging()

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="WaniKani MCP Server")
    parser.add_argument(
        "--mode",
        choices=["http", "stdio"],
        default="stdio",
        help="Server mode (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"HTTP server host (default: {settings.host})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"HTTP server port (default: {settings.port})",
    )

    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.mode, args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)
