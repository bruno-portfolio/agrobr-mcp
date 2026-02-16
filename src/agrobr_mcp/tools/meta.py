from mcp.server.fastmcp import FastMCP

from agrobr_mcp.config import logger

PRODUCTS_BY_TOOL: dict[str, list[str]] = {
    "preco_diario": [
        "soja",
        "milho",
        "boi_gordo",
        "cafe_arabica",
        "cafe_robusta",
        "algodao",
        "trigo",
        "arroz",
        "acucar",
        "etanol_hidratado",
        "etanol_anidro",
        "frango_congelado",
        "suino",
        "leite",
        "laranja_industria",
    ],
    "futuros_b3": [
        "boi_gordo",
        "milho",
        "cafe_arabica",
        "cafe_conillon",
        "etanol",
        "soja_cross",
        "soja_fob",
    ],
    "estimativa_safra": ["soja", "milho", "arroz", "feijao", "algodao", "trigo", "cafe"],
    "producao_anual": [
        "soja",
        "milho",
        "arroz",
        "feijao",
        "algodao",
        "trigo",
        "cafe",
        "cana_de_acucar",
        "mandioca",
        "laranja",
        "cacau",
        "sorgo",
    ],
    "balanco": ["soja", "milho", "arroz", "feijao", "algodao", "trigo", "cafe"],
    "progresso_safra": ["soja", "milho", "arroz", "feijao", "algodao", "trigo"],
}


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def listar_produtos(tool: str = "") -> str:
        """List valid products/parameters for each agrobr-mcp tool.

        Useful to discover which values to pass before calling another tool.
        If no tool is specified, lists all.

        Args:
            tool: Tool name (e.g. "preco_diario"). Empty = all tools.
        """
        if tool:
            products = PRODUCTS_BY_TOOL.get(tool)
            if not products:
                valid_tools = ", ".join(sorted(PRODUCTS_BY_TOOL))
                return f"Tool '{tool}' não encontrada. Tools com produtos: {valid_tools}"
            return f"## Produtos — {tool}\n\n{', '.join(products)}"

        lines = ["## Produtos válidos por tool\n"]
        for tool_name, products in PRODUCTS_BY_TOOL.items():
            lines.append(f"**{tool_name}:** {', '.join(products)}")
        return "\n".join(lines)

    @mcp.tool()
    async def health_check() -> str:
        """Check the status of agrobr data sources.

        Returns which APIs are responding and which have issues.
        Useful to diagnose when a tool returns an error.
        """
        try:
            from agrobr import health

            results = await health.run_all_checks()
            lines = ["## Status das Fontes de Dados\n"]
            for check in results:
                status_label = "OK" if check.status.value == "ok" else "FALHA"
                latency = f" ({check.latency_ms}ms)" if check.latency_ms else ""
                lines.append(f"- {check.source}: {status_label}{latency}")
            return "\n".join(lines)
        except Exception as e:
            logger.exception("health_check failed")
            return f"Erro ao verificar status: {type(e).__name__}: {e}"
