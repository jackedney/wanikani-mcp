from wanikani_mcp.http_server import mcp


def test_mcp_server_instance():
    """Test that MCP server instance is created correctly"""
    assert mcp is not None
    assert mcp.name == "wanikani-mcp"


def test_mcp_tools_registered():
    """Test that our core MCP tools are registered"""
    # This is a basic test that the server has tools
    # The actual tools will be tested when we have real data
    assert hasattr(mcp, "tool")
    assert hasattr(mcp, "resource")


def test_server_startup():
    """Test that server can initialize without errors"""
    from wanikani_mcp.http_server import create_app

    # Should not raise any exceptions
    app = create_app()
    assert app is not None
