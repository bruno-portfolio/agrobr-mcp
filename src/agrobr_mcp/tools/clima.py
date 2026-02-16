from datetime import date

from mcp.server.fastmcp import FastMCP

from agrobr_mcp.config import logger
from agrobr_mcp.tools.utils import VALID_UFS, df_to_text, resolve_biome


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def clima(uf: str, ano: int = 0, agregacao: str = "mensal") -> str:
        """Recent climate data by state (temperature, precipitation, radiation,
        humidity, wind).

        Valid states: AC, AL, AM, AP, BA, CE, DF, ES, GO, MA, MG, MS,
        MT, PA, PB, PE, PI, PR, RJ, RN, RO, RR, RS, SC, SE, SP, TO.

        Args:
            uf: State abbreviation (e.g. "MT", "PR", "RS")
            ano: Year (default: current year)
            agregacao: "diario" or "mensal" (default: "mensal")
        """
        try:
            from agrobr import nasa_power

            uf_upper = uf.strip().upper()
            if uf_upper not in VALID_UFS:
                return f"UF '{uf}' inválida. Use: {', '.join(sorted(VALID_UFS))}"
            ano_ref = ano or date.today().year
            df = await nasa_power.clima_uf(uf_upper, ano_ref, agregacao=agregacao)
            return df_to_text(
                df,
                title=f"Clima {ano_ref} — {uf_upper} ({agregacao})",
                source="NASA POWER",
            )
        except Exception as e:
            logger.exception("clima(%s, %s) failed", uf, ano)
            return f"Erro ao buscar clima de '{uf}': {type(e).__name__}: {e}"

    @mcp.tool()
    async def desmatamento(bioma: str = "amazonia", sistema: str = "deter") -> str:
        """Deforestation rates and alerts by biome.

        Biomes: amazonia, cerrado, mata_atlantica, caatinga, pampa, pantanal.
        Systems: prodes (annual rate), deter (real-time alerts).

        Args:
            bioma: Biome name (e.g. "amazonia", "cerrado")
            sistema: "prodes" (annual) or "deter" (alerts)
        """
        try:
            from agrobr import desmatamento as desmat

            bioma_resolved = resolve_biome(bioma)
            if sistema == "prodes":
                df = await desmat.prodes(bioma=bioma_resolved)
                if "ano" in df.columns:
                    df = df.sort_values("ano", ascending=True)
            else:
                df = await desmat.deter(bioma=bioma_resolved)
                if "data" in df.columns:
                    df = df.sort_values("data", ascending=True)
            return df_to_text(
                df,
                title=f"Desmatamento {sistema.upper()} — {bioma_resolved}",
                source="INPE/TerraBrasilis",
            )
        except ValueError:
            return (
                f"Bioma '{bioma}' ou sistema '{sistema}' inválido. "
                "Biomas: amazonia, cerrado, mata_atlantica, caatinga, pampa, pantanal. "
                "Sistemas: prodes, deter."
            )
        except Exception as e:
            logger.exception("desmatamento(%s, %s) failed", bioma, sistema)
            return f"Erro ao buscar desmatamento: {type(e).__name__}: {e}"
