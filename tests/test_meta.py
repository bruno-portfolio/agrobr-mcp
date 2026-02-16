import pytest
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_listar_produtos_all(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["listar_produtos"].fn(tool="")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_listar_produtos_specific(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["listar_produtos"].fn(tool="preco_diario")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_listar_produtos_invalid_tool(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["listar_produtos"].fn(tool="inexistente")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_health_check(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["health_check"].fn()
    assert isinstance(result, str)
    assert len(result) > 0
