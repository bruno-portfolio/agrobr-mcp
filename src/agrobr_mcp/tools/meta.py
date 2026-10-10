from mcp.server import MCPServer

from agrobr_mcp.config import logger
from agrobr_mcp.tools.utils import DATASET_BY_TOOL, products


def register(mcp: MCPServer) -> None:
    @mcp.tool()
    async def listar_produtos(tool: str = "") -> str:
        """List valid products/parameters for each agrobr-mcp tool.

        Useful to discover which values to pass before calling another tool.
        If no tool is specified, lists all.

        Args:
            tool: Tool name (e.g. "preco_diario"). Empty = all tools.
        """
        if tool:
            if tool not in DATASET_BY_TOOL:
                valid_tools = ", ".join(sorted(DATASET_BY_TOOL))
                return f"Tool '{tool}' não encontrada. Tools com produtos: {valid_tools}"
            return f"## Produtos — {tool}\n\n{products(tool)}"

        lines = ["## Produtos válidos por tool\n"]
        for tool_name in DATASET_BY_TOOL:
            lines.append(f"**{tool_name}:** {products(tool_name)}")
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
