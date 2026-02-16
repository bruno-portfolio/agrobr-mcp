import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPECTED_TOOLS = {
    "preco_diario",
    "futuros_b3",
    "estimativa_safra",
    "producao_anual",
    "balanco",
    "progresso_safra",
    "clima",
    "desmatamento",
    "listar_produtos",
    "health_check",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_all_tools_registered():
    server_params = StdioServerParameters(command="python", args=["-m", "agrobr_mcp"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {t.name for t in tools.tools}
            assert EXPECTED_TOOLS.issubset(names), f"Missing tools: {EXPECTED_TOOLS - names}"
