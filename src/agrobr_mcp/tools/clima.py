from datetime import date, timedelta

from mcp.server import MCPServer

from agrobr_mcp.config import (
    DESMATAMENTO_MAX_REGISTROS,
    DETER_JANELA_DIAS,
    QUEIMADAS_SATELITE,
    QUEIMADAS_TOP_MUNICIPIOS,
    logger,
)
from agrobr_mcp.tools.utils import VALID_UFS, df_to_text, resolve_biome


def register(mcp: MCPServer) -> None:
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
    async def desmatamento(
        bioma: str = "amazonia", sistema: str = "deter", ano: int = 0, uf: str = ""
    ) -> str:
        """Deforestation polygons and alerts by biome.

        Biomes: amazonia, cerrado, mata_atlantica, caatinga, pampa, pantanal.
        Systems: prodes (polygons for the previous calendar year, falling back
        one more year when empty), deter (alerts of the last 15 days).
        At most 2000 records are read; the response reports any cut.

        Args:
            bioma: Biome name (e.g. "amazonia", "cerrado")
            sistema: "prodes" (annual) or "deter" (alerts)
            ano: Year (PRODES mapping year, used as given without falling back;
                DETER calendar year). Default: see above.
            uf: State abbreviation filter (e.g. "PA", "MT"). Empty = whole biome.
        """
        try:
            from agrobr import desmatamento as desmat

            bioma_resolved = resolve_biome(bioma)
            uf_ref = uf.strip().upper() or None
            filtro = {
                "uf": uf_ref,
                "max_registros": DESMATAMENTO_MAX_REGISTROS,
                "tamanho_pagina": DESMATAMENTO_MAX_REGISTROS,
                "return_meta": True,
            }
            if sistema == "prodes":
                ano_atual = date.today().year
                for ano_ref in (ano,) if ano else (ano_atual - 1, ano_atual - 2):
                    df, meta = await desmat.prodes(bioma=bioma_resolved, ano=ano_ref, **filtro)
                    if not df.empty:
                        break
                recorte = str(ano_ref)
            else:
                if ano:
                    inicio, fim = date(ano, 1, 1), min(date(ano, 12, 31), date.today())
                else:
                    fim = date.today()
                    inicio = fim - timedelta(days=DETER_JANELA_DIAS)
                df, meta = await desmat.deter(
                    bioma=bioma_resolved, inicio=inicio.isoformat(), fim=fim.isoformat(), **filtro
                )
                if "data" in df.columns:
                    df = df.sort_values("data", ascending=True)
                recorte = f"{inicio.isoformat()} a {fim.isoformat()}"
            if uf_ref:
                recorte += f", {uf_ref}"
            cobertura = meta.source_details.get("coverage", {})
            nota = (
                f"Corte: lidas {cobertura['returned_rows']} de {cobertura['expected_rows']} "
                "ocorrências do recorte, as primeiras pelo identificador da fonte "
                "(não as mais recentes)."
                if cobertura.get("truncated")
                else ""
            )
            return df_to_text(
                df,
                title=f"Desmatamento {sistema.upper()} {recorte} — {bioma_resolved}",
                source="INPE/TerraBrasilis",
                note=nota,
            )
        except ValueError:
            return (
                f"Bioma '{bioma}', sistema '{sistema}', ano {ano} ou UF '{uf}' inválido. "
                "Biomas: amazonia, cerrado, mata_atlantica, caatinga, pampa, pantanal. "
                "Sistemas: prodes, deter."
            )
        except Exception as e:
            logger.exception("desmatamento(%s, %s) failed", bioma, sistema)
            return f"Erro ao buscar desmatamento: {type(e).__name__}: {e}"

    @mcp.tool()
    async def queimadas(uf: str, data: str = "") -> str:
        """Fire hotspots of one day by municipality and biome (INPE Queimadas).

        Counts the reference satellite (AQUA_M-T), the basis of INPE's official
        statistics; other satellites repeat detections of the same fire.

        Args:
            uf: State abbreviation (e.g. "MT", "PA")
            data: Date in "YYYY-MM-DD" format (default: yesterday)
        """
        try:
            from agrobr import datasets

            uf_upper = uf.strip().upper()
            if uf_upper not in VALID_UFS:
                return f"UF '{uf}' inválida. Use: {', '.join(sorted(VALID_UFS))}"
            dia = date.fromisoformat(data) if data else date.today() - timedelta(days=1)
            df = await datasets.queimadas(
                ano=dia.year, mes=dia.month, dia=dia.day, uf=uf_upper, satelite=QUEIMADAS_SATELITE
            )
            titulo = f"Focos de calor — {uf_upper} ({dia.isoformat()})"
            fonte = f"INPE Queimadas, satélite de referência {QUEIMADAS_SATELITE}"
            if df.empty:
                return df_to_text(df, title=titulo, source=fonte)
            focos = df[["municipio", "bioma"]].fillna("não informado")
            por_bioma = (
                focos["bioma"].value_counts().rename_axis("bioma").reset_index(name="focos")
            )
            por_municipio = (
                focos.groupby("municipio")
                .size()
                .reset_index(name="focos")
                .sort_values(["focos", "municipio"], ascending=[False, True])
            )
            mostrados = min(QUEIMADAS_TOP_MUNICIPIOS, len(por_municipio))
            return "\n".join(
                [
                    f"## {titulo}",
                    f"Fonte: {fonte}",
                    f"Total: {len(df)} focos",
                    "",
                    por_bioma.to_string(index=False),
                    "",
                    f"Municípios com mais focos ({mostrados} de {len(por_municipio)}):",
                    por_municipio.head(QUEIMADAS_TOP_MUNICIPIOS).to_string(index=False),
                ]
            )
        except ValueError as e:
            return f"Parâmetro inválido (data YYYY-MM-DD, UF): {e}"
        except Exception as e:
            logger.exception("queimadas(%s, %s) failed", uf, data)
            return f"Erro ao buscar queimadas de '{uf}': {type(e).__name__}: {e}"
