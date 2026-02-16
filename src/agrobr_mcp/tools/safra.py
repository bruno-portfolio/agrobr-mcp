from datetime import date

from mcp.server.fastmcp import FastMCP

from agrobr_mcp.config import logger
from agrobr_mcp.tools.utils import current_crop_season, df_to_text


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def estimativa_safra(produto: str, safra: str = "") -> str:
        """Current crop season estimate by state (area, production, yield).

        Products: soja, milho, arroz, feijao, algodao, trigo, cafe.

        Args:
            produto: Crop name (e.g. "soja", "milho")
            safra: Crop season in "YYYY/YY" format (default: current season)
        """
        try:
            from agrobr import datasets

            safra_ref = safra or current_crop_season()
            df = await datasets.estimativa_safra(produto, safra=safra_ref)
            return df_to_text(
                df,
                title=f"Estimativa Safra {safra_ref} — {produto.title()}",
                source="CONAB / IBGE LSPA",
            )
        except ValueError:
            return (
                f"Produto '{produto}' não encontrado. "
                "Use: soja, milho, arroz, feijao, algodao, trigo, cafe."
            )
        except Exception as e:
            logger.exception("estimativa_safra(%s) failed", produto)
            return f"Erro ao buscar estimativa de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    async def producao_anual(produto: str, ano: int = 0) -> str:
        """Historical annual crop production by state (IBGE PAM).

        Products: soja, milho, arroz, feijao, algodao, trigo, cafe,
        cana_de_acucar, mandioca, laranja, cacau, sorgo.

        Args:
            produto: Crop name (e.g. "soja", "milho")
            ano: Reference year (default: previous year)
        """
        try:
            from agrobr import datasets

            ano_ref = ano or (date.today().year - 1)
            df = await datasets.producao_anual(produto, ano=ano_ref)
            return df_to_text(
                df,
                title=f"Produção {ano_ref} — {produto.title()} (por UF)",
                source="IBGE PAM",
            )
        except ValueError:
            return (
                f"Produto '{produto}' ou ano {ano} inválido. "
                "Produtos: soja, milho, arroz, feijao, algodao, trigo, cafe, "
                "cana_de_acucar, mandioca, laranja, cacau, sorgo."
            )
        except Exception as e:
            logger.exception("producao_anual(%s, %s) failed", produto, ano)
            return f"Erro ao buscar produção de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    async def balanco(produto: str) -> str:
        """Supply and demand balance (stock, consumption, exports).

        Products: soja, milho, arroz, feijao, algodao, trigo, cafe.

        Args:
            produto: Crop name (e.g. "soja", "milho")
        """
        try:
            from agrobr import datasets

            df = await datasets.balanco(produto)
            return df_to_text(
                df,
                title=f"Balanço Oferta/Demanda — {produto.title()}",
                source="CONAB",
            )
        except ValueError:
            return (
                f"Produto '{produto}' não encontrado. "
                "Use: soja, milho, arroz, feijao, algodao, trigo, cafe."
            )
        except Exception as e:
            logger.exception("balanco(%s) failed", produto)
            return f"Erro ao buscar balanço de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    async def progresso_safra(produto: str, uf: str = "") -> str:
        """Weekly planting and harvesting progress by state.

        Products: soja, milho, arroz, feijao, algodao, trigo.

        Args:
            produto: Crop name (e.g. "soja", "milho")
            uf: State abbreviation filter (e.g. "MT", "PR"). Empty = all states.
        """
        try:
            from agrobr import conab

            cultura = produto.replace("_", " ").title()
            kwargs: dict[str, str] = {"cultura": cultura}
            if uf:
                kwargs["estado"] = uf.strip().upper()
            df = await conab.progresso_safra(**kwargs)
            title_suffix = f" — {uf.upper()}" if uf else ""
            return df_to_text(
                df,
                title=f"Progresso Safra — {cultura}{title_suffix}",
                source="CONAB",
            )
        except ValueError:
            return (
                f"Produto '{produto}' não encontrado. "
                "Use: soja, milho, arroz, feijao, algodao, trigo."
            )
        except Exception as e:
            logger.exception("progresso_safra(%s) failed", produto)
            return f"Erro ao buscar progresso de '{produto}': {type(e).__name__}: {e}"
