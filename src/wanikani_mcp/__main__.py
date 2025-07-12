from .http_server import mcp


def main():
    # Use FastMCP's built-in run method instead of uvicorn directly
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
