from datetime import date

from mcp.server.fastmcp import FastMCP

from agrobr_mcp.config import logger
from agrobr_mcp.tools.utils import df_to_text


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def preco_diario(produto: str, dias: int = 5) -> str:
        """Daily spot prices for Brazilian agricultural commodities (CEPEA/ESALQ).

        Products: soja, milho, boi_gordo, cafe_arabica, cafe_robusta,
        algodao, trigo, arroz, acucar, etanol_hidratado, etanol_anidro,
        frango_congelado, suino, leite, laranja_industria.

        Args:
            produto: Commodity name (e.g. "soja", "milho", "boi_gordo")
            dias: Number of recent days to return (default: 5, max: 60)
        """
        try:
            from agrobr import datasets

            df = await datasets.preco_diario(produto)
            df = df.sort_values("data", ascending=True)
            return df_to_text(
                df.tail(dias),
                title=f"Preço diário — {produto.replace('_', ' ').title()}",
                source="CEPEA/ESALQ",
            )
        except ValueError:
            return (
                f"Produto '{produto}' não encontrado. "
                "Use: soja, milho, boi_gordo, cafe_arabica, cafe_robusta, "
                "algodao, trigo, arroz, acucar, etanol_hidratado, etanol_anidro, "
                "frango_congelado, suino, leite, laranja_industria."
            )
        except Exception as e:
            logger.exception("preco_diario(%s) failed", produto)
            return f"Erro ao buscar preço de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    async def futuros_b3(contrato: str, data: str = "") -> str:
        """Daily settlement prices for agricultural futures on B3 exchange.

        Contracts: boi_gordo, milho, cafe_arabica, cafe_conillon,
        etanol, soja_cross, soja_fob.

        Args:
            contrato: Futures contract name (e.g. "milho", "boi_gordo")
            data: Date in "YYYY-MM-DD" format (default: today)
        """
        try:
            from agrobr import b3

            data_ref = date.fromisoformat(data) if data else date.today()
            df = await b3.ajustes(data=data_ref, contrato=contrato)
            return df_to_text(
                df,
                title=f"Futuros B3 — {contrato.replace('_', ' ').title()} ({data_ref})",
                source="B3",
            )
        except ValueError:
            return (
                f"Contrato '{contrato}' ou data '{data}' inválido. "
                "Contratos: boi_gordo, milho, cafe_arabica, cafe_conillon, "
                "etanol, soja_cross, soja_fob. Data: YYYY-MM-DD."
            )
        except Exception as e:
            logger.exception("futuros_b3(%s, %s) failed", contrato, data)
            return f"Erro ao buscar futuros de '{contrato}': {type(e).__name__}: {e}"
