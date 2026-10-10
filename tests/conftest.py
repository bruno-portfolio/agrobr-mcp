import pytest
from mcp.server import MCPServer

from agrobr_mcp.tools import clima, meta, precos, safra


@pytest.fixture
def mcp_server() -> MCPServer:
    server = MCPServer("test")
    precos.register(server)
    safra.register(server)
    clima.register(server)
    meta.register(server)
    return server
