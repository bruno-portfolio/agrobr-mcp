import pytest
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_clima_mt(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["clima"].fn(uf="MT", ano=2023, agregacao="mensal")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_clima_invalid_uf(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["clima"].fn(uf="XX", ano=2023, agregacao="mensal")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_desmatamento_deter(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["desmatamento"].fn(bioma="amazonia", sistema="deter")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_desmatamento_prodes(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["desmatamento"].fn(bioma="cerrado", sistema="prodes")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_desmatamento_invalid(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["desmatamento"].fn(bioma="invalido", sistema="deter")
    assert isinstance(result, str)
    assert len(result) > 0
