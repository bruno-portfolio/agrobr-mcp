import pytest
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_listar_produtos_all(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["listar_produtos"].fn(tool="")
    assert "preco_diario" in result
    assert "soja" in result


@pytest.mark.asyncio
async def test_listar_produtos_specific(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["listar_produtos"].fn(tool="preco_diario")
    assert "soja" in result
    assert "milho" in result


@pytest.mark.asyncio
async def test_listar_produtos_invalid_tool(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["listar_produtos"].fn(tool="inexistente")
    assert "não encontrada" in result


@pytest.mark.asyncio
async def test_health_check(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["health_check"].fn()
    assert "Status" in result or "Erro" in result
