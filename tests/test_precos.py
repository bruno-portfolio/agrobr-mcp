import pytest
from mcp.server.fastmcp import FastMCP


@pytest.mark.asyncio
async def test_preco_diario_soja(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["preco_diario"].fn(produto="soja", dias=3)
    assert isinstance(result, str)
    assert len(result) > 0
    if "Erro" not in result:
        assert "Soja" in result or "soja" in result
        assert "CEPEA" in result


@pytest.mark.asyncio
async def test_preco_diario_invalid_product(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["preco_diario"].fn(produto="inexistente", dias=3)
    assert "não encontrado" in result


@pytest.mark.asyncio
async def test_futuros_b3_milho(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["futuros_b3"].fn(contrato="milho", data="")
    assert isinstance(result, str)
    assert len(result) > 0
    if "Erro" not in result:
        assert "B3" in result


@pytest.mark.asyncio
async def test_futuros_b3_invalid_contract(mcp_server: FastMCP):
    tools = mcp_server._tool_manager._tools
    result = await tools["futuros_b3"].fn(contrato="inexistente", data="")
    assert "inválido" in result or "Erro" in result or "Nenhum dado" in result
