import pytest
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_estimativa_safra_soja(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["estimativa_safra"].fn(produto="soja", safra="")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_estimativa_safra_invalid(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["estimativa_safra"].fn(produto="inexistente", safra="")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_producao_anual_soja(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["producao_anual"].fn(produto="soja", ano=2022)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_producao_anual_invalid(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["producao_anual"].fn(produto="inexistente", ano=2022)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_balanco_soja(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["balanco"].fn(produto="soja")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_balanco_invalid(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["balanco"].fn(produto="inexistente")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_progresso_safra_soja(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["progresso_safra"].fn(produto="soja", uf="")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_progresso_safra_invalid(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["progresso_safra"].fn(produto="inexistente", uf="")
    assert isinstance(result, str)
    assert len(result) > 0
