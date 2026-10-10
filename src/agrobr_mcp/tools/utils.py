from collections.abc import Callable
from typing import TypeVar

import pandas as pd

from agrobr_mcp.config import MAX_ROWS_DEFAULT

Tool = TypeVar("Tool", bound=Callable[..., object])

DATASET_BY_TOOL = {
    "preco_diario": "preco_diario",
    "futuros_b3": "futuros_agricolas",
    "estimativa_safra": "estimativa_safra",
    "producao_anual": "producao_anual",
    "balanco": "balanco",
    "progresso_safra": "progresso_safra",
    "serie_historica_safra": "serie_historica_safra",
    "rebanho": "pecuaria_municipal",
    "exportacao": "exportacao",
}


def products(tool: str) -> str:
    from agrobr import datasets

    return ", ".join(datasets.list_products(DATASET_BY_TOOL[tool]))


def with_products(tool: str) -> Callable[[Tool], Tool]:
    def fill(fn: Tool) -> Tool:
        fn.__doc__ = (fn.__doc__ or "").replace("{products}", products(tool))
        return fn

    return fill


BIOME_MAP = {
    "amazonia": "Amazônia",
    "cerrado": "Cerrado",
    "mata_atlantica": "Mata Atlântica",
    "caatinga": "Caatinga",
    "pampa": "Pampa",
    "pantanal": "Pantanal",
}

VALID_UFS = {
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
}


def resolve_biome(name: str) -> str:
    normalized = name.strip().lower().replace(" ", "_")
    return BIOME_MAP.get(normalized, name)


def somar_publicado(df: pd.DataFrame, chaves: list[str], medidas: list[str]) -> pd.DataFrame:
    """Soma ``medidas`` por ``chaves`` sem transformar ausência em zero.

    Grupo sem parcela publicada sai nulo; com parte ausente, sai a soma das publicadas, e a coluna
    ``faltam`` diz quantas faltam por medida (``medida: N de M``). Sem ausência, não há ``faltam``.
    """
    somas = df.groupby(chaves)[medidas].sum(min_count=1)
    ausentes = df[medidas].isna().groupby([df[chave] for chave in chaves]).sum()
    tamanhos = df.groupby(chaves).size()
    if ausentes.to_numpy().any():
        somas["faltam"] = [
            "; ".join(
                f"{medida}: {int(ausentes.loc[grupo, medida])} de {int(tamanhos.loc[grupo])}"
                for medida in medidas
                if ausentes.loc[grupo, medida]
            )
            for grupo in somas.index
        ]
    return somas.reset_index()


def total_publicado(serie: pd.Series, formato: str, rotulo: str) -> str:
    faltam = int(serie.isna().sum())
    if faltam == len(serie):
        return f"{rotulo} sem dado"
    texto = formato.format(serie.sum())
    if faltam:
        texto += f" (soma das parcelas publicadas; faltam {faltam} de {len(serie)})"
    return texto


def df_to_text(
    df: pd.DataFrame,
    title: str = "",
    source: str = "",
    max_rows: int = MAX_ROWS_DEFAULT,
    note: str = "",
) -> str:
    lines: list[str] = []

    if title:
        lines.append(f"## {title}")
    if source:
        lines.append(f"Fonte: {source}")
    if note:
        lines.append(note)
    lines.append("")

    if df.empty:
        lines.append("Nenhum dado disponível para os parâmetros informados.")
        return "\n".join(lines)

    if len(df) > max_rows:
        lines.append(f"(mostrando {max_rows} de {len(df)} registros)")
        df = df.tail(max_rows)

    lines.append(df.to_string(index=False))
    return "\n".join(lines)
