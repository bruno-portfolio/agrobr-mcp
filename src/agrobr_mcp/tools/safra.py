from datetime import date

from mcp.server import MCPServer

from agrobr_mcp.config import SERIE_HISTORICA_ANOS, logger
from agrobr_mcp.tools.utils import (
    VALID_UFS,
    df_to_text,
    products,
    somar_publicado,
    with_products,
)


def register(mcp: MCPServer) -> None:
    @mcp.tool()
    @with_products("estimativa_safra")
    async def estimativa_safra(produto: str, safra: str = "") -> str:
        """Current crop season estimate by state (area, production, yield).

        Products: {products}.

        Args:
            produto: Crop name (e.g. "soja", "milho")
            safra: Crop season in "YYYY/YY" format (default: latest season with data)
        """
        try:
            from agrobr import datasets

            df = await datasets.estimativa_safra(produto, safra=safra or None)
            safra_ref = safra or (df["safra"].iloc[0] if not df.empty else "mais recente")
            return df_to_text(
                df,
                title=f"Estimativa Safra {safra_ref} — {produto.title()}",
                source="CONAB / IBGE LSPA",
            )
        except ValueError:
            return f"Produto '{produto}' não encontrado. Use: {products('estimativa_safra')}."
        except Exception as e:
            logger.exception("estimativa_safra(%s) failed", produto)
            return f"Erro ao buscar estimativa de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    @with_products("producao_anual")
    async def producao_anual(produto: str, ano: int = 0) -> str:
        """Historical annual crop production by state (IBGE PAM).

        Products: {products}.

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
                f"Produtos: {products('producao_anual')}."
            )
        except Exception as e:
            logger.exception("producao_anual(%s, %s) failed", produto, ano)
            return f"Erro ao buscar produção de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    @with_products("balanco")
    async def balanco(produto: str) -> str:
        """Supply and demand balance (stock, consumption, exports).

        Products: {products}.

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
            return f"Produto '{produto}' não encontrado. Use: {products('balanco')}."
        except Exception as e:
            logger.exception("balanco(%s) failed", produto)
            return f"Erro ao buscar balanço de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    @with_products("progresso_safra")
    async def progresso_safra(produto: str, uf: str = "") -> str:
        """Weekly planting and harvesting progress by state.

        Products: {products}.

        Args:
            produto: Crop name (e.g. "soja", "milho_1")
            uf: State abbreviation filter (e.g. "MT", "PR"). Empty = all states.
        """
        try:
            from agrobr import conab

            cultura = produto.replace("_", " ").title()
            df = await conab.progresso_safra(produto=produto, uf=uf.strip().upper() or None)
            title_suffix = f" — {uf.upper()}" if uf else ""
            return df_to_text(
                df,
                title=f"Progresso Safra — {cultura}{title_suffix}",
                source="CONAB",
            )
        except ValueError:
            return f"Produto '{produto}' não encontrado. Use: {products('progresso_safra')}."
        except Exception as e:
            logger.exception("progresso_safra(%s) failed", produto)
            return f"Erro ao buscar progresso de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    @with_products("serie_historica_safra")
    async def serie_historica_safra(produto: str, uf: str = "", ano_inicio: int = 0) -> str:
        """Historical crop series by season (CONAB): area, production and yield.

        Products: {products}.

        Args:
            produto: Crop name (e.g. "soja", "milho_2")
            uf: State abbreviation (e.g. "PR"). Empty = Brazil, summed over the states.
            ano_inicio: Start year of the first season (default: 10 years ago)
        """
        try:
            from agrobr import datasets

            uf_ref = uf.strip().upper() or None
            inicio = ano_inicio or date.today().year - SERIE_HISTORICA_ANOS
            df = await datasets.serie_historica_safra(produto, ano_inicio=inicio, uf=uf_ref)
            if uf_ref is None:
                df = somar_publicado(df, ["safra"], ["area_plantada_mil_ha", "producao_mil_ton"])
            return df_to_text(
                df,
                title=f"Série histórica desde {inicio} — {produto.title()} ({uf_ref or 'Brasil'})",
                source="CONAB",
                note="" if uf_ref else "Brasil: soma das UFs publicadas; produtividade só por UF.",
            )
        except ValueError:
            return (
                f"Produto '{produto}' ou UF '{uf}' inválido. "
                f"Use: {products('serie_historica_safra')}."
            )
        except Exception as e:
            logger.exception("serie_historica_safra(%s, %s) failed", produto, uf)
            return f"Erro ao buscar a série de '{produto}': {type(e).__name__}: {e}"

    @mcp.tool()
    @with_products("rebanho")
    async def rebanho(produto: str, ano: int = 0) -> str:
        """Livestock herds and animal products by state (IBGE PPM).

        Products: {products}.

        Args:
            produto: Herd or product (e.g. "bovino", "leite")
            ano: Reference year (default: latest published)
        """
        try:
            from agrobr import datasets

            df = await datasets.pecuaria_municipal(produto, ano=ano or None, nivel="uf")
            ano_ref = ano or (df["ano"].iloc[0] if not df.empty else "mais recente")
            return df_to_text(
                df.sort_values("valor", ascending=False),
                title=f"Pecuária {ano_ref} — {produto.title()} (por UF)",
                source="IBGE PPM",
                max_rows=len(VALID_UFS),
            )
        except ValueError:
            return f"Produto '{produto}' ou ano {ano} inválido. Use: {products('rebanho')}."
        except Exception as e:
            logger.exception("rebanho(%s, %s) failed", produto, ano)
            return f"Erro ao buscar o rebanho de '{produto}': {type(e).__name__}: {e}"
