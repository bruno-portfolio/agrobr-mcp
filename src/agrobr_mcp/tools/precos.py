from datetime import date

from mcp.server import MCPServer

from agrobr_mcp.config import logger
from agrobr_mcp.tools.utils import (
    df_to_text,
    products,
    somar_publicado,
    total_publicado,
    with_products,
)


def register(mcp: MCPServer) -> None:
    @mcp.tool()
    @with_products("preco_diario")
    async def preco_diario(produto: str, dias: int = 5) -> str:
        """Daily spot prices for Brazilian agricultural commodities (CEPEA/ESALQ).

        Products: {products}.

        Args:
            produto: Commodity name (e.g. "soja", "milho", "boi")
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
            return f"Produto '{produto}' não encontrado. Use: {products('preco_diario')}."
        except Exception as e:
            logger.exception("preco_diario(%s) failed", produto)
            return f"Erro ao buscar preço de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    @with_products("futuros_b3")
    async def futuros_b3(contrato: str, data: str = "") -> str:
        """Daily settlement prices for agricultural futures on B3 exchange.

        Contracts: {products}.

        Args:
            contrato: Futures contract name (e.g. "milho", "boi")
            data: Date in "YYYY-MM-DD" format (default: latest published session)
        """
        try:
            from agrobr import datasets

            df = await datasets.futuros_agricolas(contrato, data=data or None)
            pregao = df["data"].max().date().isoformat() if not df.empty else data or "recente"
            return df_to_text(
                df,
                title=f"Futuros B3 — {contrato.replace('_', ' ').title()} ({pregao})",
                source="B3",
            )
        except ValueError:
            return (
                f"Contrato '{contrato}' ou data '{data}' inválido. "
                f"Contratos: {products('futuros_b3')}. Data: YYYY-MM-DD."
            )
        except Exception as e:
            logger.exception("futuros_b3(%s, %s) failed", contrato, data)
            return f"Erro ao buscar futuros de '{contrato}': {type(e).__name__}: {e}"

    @mcp.tool()
    @with_products("exportacao")
    async def exportacao(produto: str, ano: int = 0, uf: str = "") -> str:
        """Brazilian agricultural exports summed by month (Comex Stat; ABIOVE fallback).

        Products: {products}.
        The Comex Stat query can take about a minute.

        Args:
            produto: Product (e.g. "soja", "farelo_soja")
            ano: Year (default: current year)
            uf: State of origin (e.g. "MT"). Empty = Brazil.
        """
        try:
            from agrobr import datasets

            ano_ref = ano or date.today().year
            uf_ref = uf.strip().upper() or None
            df, meta = await datasets.exportacao(produto, ano=ano_ref, uf=uf_ref, return_meta=True)
            chaves = ["ano", "mes", "uf"] if uf_ref else ["ano", "mes"]
            por_mes = somar_publicado(df, chaves, ["volume_ton", "valor_fob_usd"])
            fonte = meta.selected_source
            licenca = datasets.info("exportacao")["licenses"].get(fonte, "?")
            aviso = (
                ""
                if licenca == "livre"
                else "; confira o uso em https://www.agrobr.dev/docs/licenses/"
            )
            total = "Total: " + "; ".join(
                [
                    total_publicado(df["volume_ton"], "{:,.2f} t", "volume"),
                    total_publicado(df["valor_fob_usd"], "US$ {:,.2f} FOB", "valor FOB"),
                ]
            )
            return df_to_text(
                por_mes,
                title=f"Exportação {ano_ref} — {produto.title()} ({uf_ref or 'Brasil'}, por mês)",
                source=f"{fonte} (licença {licenca}{aviso})",
                note="" if df.empty else total,
            )
        except ValueError:
            return (
                f"Produto '{produto}', ano {ano} ou UF '{uf}' inválido. "
                f"Use: {products('exportacao')}."
            )
        except Exception as e:
            logger.exception("exportacao(%s, %s, %s) failed", produto, ano, uf)
            return f"Erro ao buscar exportação de '{produto}': {type(e).__name__}: {e}"
