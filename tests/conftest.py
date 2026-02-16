import pytest
from mcp.server.fastmcp import FastMCP

from agrobr_mcp.tools import clima, meta, precos, safra


@pytest.fixture
def mcp_server() -> FastMCP:
    server = FastMCP("test")
    precos.register(server)
    safra.register(server)
    clima.register(server)
    meta.register(server)
    return server
