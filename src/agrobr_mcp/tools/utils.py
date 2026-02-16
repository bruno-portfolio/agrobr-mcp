from datetime import date

import pandas as pd

from agrobr_mcp.config import MAX_ROWS_DEFAULT

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


def current_crop_season() -> str:
    today = date.today()
    if today.month <= 6:
        start_year = today.year - 1
    else:
        start_year = today.year
    end_year = (start_year + 1) % 100
    return f"{start_year}/{end_year:02d}"


def resolve_biome(name: str) -> str:
    normalized = name.strip().lower().replace(" ", "_")
    return BIOME_MAP.get(normalized, name)


def df_to_text(
    df: pd.DataFrame,
    title: str = "",
    source: str = "",
    max_rows: int = MAX_ROWS_DEFAULT,
) -> str:
    lines: list[str] = []

    if title:
        lines.append(f"## {title}")
    if source:
        lines.append(f"Fonte: {source}")
    lines.append("")

    if df.empty:
        lines.append("Nenhum dado disponível para os parâmetros informados.")
        return "\n".join(lines)

    if len(df) > max_rows:
        lines.append(f"(mostrando {max_rows} de {len(df)} registros)")
        df = df.tail(max_rows)

    lines.append(df.to_string(index=False))
    return "\n".join(lines)
