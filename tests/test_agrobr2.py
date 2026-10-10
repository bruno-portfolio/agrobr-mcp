import re
from datetime import date, timedelta
from types import SimpleNamespace
from unittest import mock

import pandas as pd
import pytest
from agrobr import datasets
from agrobr.exceptions import InvalidParameterError
from mcp.server import mcpserver

TETO_DESMATAMENTO = 2000

DATASET_DA_TOOL = {
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

CHAMADA_COM_PRODUTO_INVALIDO = [
    ("preco_diario", "agrobr.datasets.preco_diario", {"produto": "inexistente"}),
    ("futuros_b3", "agrobr.datasets.futuros_agricolas", {"contrato": "inexistente"}),
    ("estimativa_safra", "agrobr.datasets.estimativa_safra", {"produto": "inexistente"}),
    ("producao_anual", "agrobr.datasets.producao_anual", {"produto": "inexistente"}),
    ("balanco", "agrobr.datasets.balanco", {"produto": "inexistente"}),
    ("progresso_safra", "agrobr.conab.progresso_safra", {"produto": "inexistente"}),
    (
        "serie_historica_safra",
        "agrobr.datasets.serie_historica_safra",
        {"produto": "inexistente"},
    ),
    ("rebanho", "agrobr.datasets.pecuaria_municipal", {"produto": "inexistente"}),
    ("exportacao", "agrobr.datasets.exportacao", {"produto": "inexistente"}),
]


def _meta_desmatamento(expected_rows: int, returned_rows: int) -> SimpleNamespace:
    return SimpleNamespace(
        source_details={
            "coverage": {
                "expected_rows": expected_rows,
                "returned_rows": returned_rows,
                "truncated": expected_rows > returned_rows,
            }
        }
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("uf,expected_uf", [("", None), (" mt ", "MT")])
async def test_progresso_safra_parametros_agrobr2(
    mcp_server: mcpserver.MCPServer, uf: str, expected_uf: str | None
) -> None:
    with mock.patch(
        "agrobr.conab.progresso_safra", autospec=True, return_value=pd.DataFrame()
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["progresso_safra"].fn(
            produto="soja", uf=uf
        )

    fetcher.assert_awaited_once_with(produto="soja", uf=expected_uf)
    assert "Nenhum dado disponível" in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,dataset", DATASET_DA_TOOL.items())
async def test_produtos_anunciados_sao_os_da_lib(
    mcp_server: mcpserver.MCPServer, tool: str, dataset: str
) -> None:
    tools = mcp_server._tool_manager._tools
    listados = await tools["listar_produtos"].fn(tool=tool)
    descricao = re.search(r"^\s*(?:Products|Contracts): (.+)\.$", tools[tool].description, re.M)

    produtos_da_lib = datasets.list_products(dataset)
    assert listados.splitlines()[-1].split(", ") == produtos_da_lib
    assert descricao is not None
    assert descricao.group(1).split(", ") == produtos_da_lib


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,alvo,argumentos", CHAMADA_COM_PRODUTO_INVALIDO)
async def test_produto_invalido_lista_os_produtos_da_lib(
    mcp_server: mcpserver.MCPServer, tool: str, alvo: str, argumentos: dict[str, str]
) -> None:
    with mock.patch(alvo, autospec=True, side_effect=InvalidParameterError("inexistente")):
        response = await mcp_server._tool_manager._tools[tool].fn(**argumentos)

    assert ", ".join(datasets.list_products(DATASET_DA_TOOL[tool])) in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_futuros_b3_sem_data_usa_pregao_recente(mcp_server: mcpserver.MCPServer) -> None:
    pregao = pd.DataFrame(
        {"data": pd.to_datetime(["2026-10-08"]), "ticker": ["BGI"], "vencimento_codigo": ["V26"]}
    )
    with mock.patch(
        "agrobr.datasets.futuros_agricolas", autospec=True, return_value=pregao
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["futuros_b3"].fn(
            contrato="boi_gordo", data=""
        )

    fetcher.assert_awaited_once_with("boi_gordo", data=None)
    assert "(2026-10-08)" in response
    assert "BGI" in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_estimativa_safra_sem_safra_usa_mais_recente(
    mcp_server: mcpserver.MCPServer,
) -> None:
    estimativa = pd.DataFrame({"safra": ["2025/26"], "uf": ["MT"], "producao": [51000.0]})
    with mock.patch(
        "agrobr.datasets.estimativa_safra", autospec=True, return_value=estimativa
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["estimativa_safra"].fn(
            produto="soja", safra=""
        )

    fetcher.assert_awaited_once_with("soja", safra=None)
    assert "Estimativa Safra 2025/26" in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_desmatamento_deter_ultimos_15_dias_com_teto(
    mcp_server: mcpserver.MCPServer,
) -> None:
    alertas = pd.DataFrame(
        {"data": pd.to_datetime(["2026-10-02", "2026-09-30"]), "uf": ["PA", "MT"]}
    )
    with mock.patch(
        "agrobr.desmatamento.deter",
        autospec=True,
        return_value=(alertas, _meta_desmatamento(3556, TETO_DESMATAMENTO)),
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["desmatamento"].fn(
            bioma="amazonia", sistema="deter"
        )

    fim = date.today()
    inicio = fim - timedelta(days=15)
    fetcher.assert_awaited_once_with(
        bioma="Amazônia",
        uf=None,
        inicio=inicio.isoformat(),
        fim=fim.isoformat(),
        max_registros=TETO_DESMATAMENTO,
        tamanho_pagina=TETO_DESMATAMENTO,
        return_meta=True,
    )
    assert f"{inicio.isoformat()} a {fim.isoformat()}" in response
    assert "2000 de 3556" in response
    assert response.index("2026-09-30") < response.index("2026-10-02")
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_desmatamento_deter_ano_e_uf(mcp_server: mcpserver.MCPServer) -> None:
    with mock.patch(
        "agrobr.desmatamento.deter",
        autospec=True,
        return_value=(pd.DataFrame(), _meta_desmatamento(0, 0)),
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["desmatamento"].fn(
            bioma="cerrado", sistema="deter", ano=2024, uf=" mt "
        )

    fetcher.assert_awaited_once_with(
        bioma="Cerrado",
        uf="MT",
        inicio="2024-01-01",
        fim="2024-12-31",
        max_registros=TETO_DESMATAMENTO,
        tamanho_pagina=TETO_DESMATAMENTO,
        return_meta=True,
    )
    assert "DETER 2024-01-01 a 2024-12-31, MT" in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_desmatamento_prodes_ano_anterior_com_teto(
    mcp_server: mcpserver.MCPServer,
) -> None:
    ano = date.today().year - 1
    poligonos = pd.DataFrame({"ano": [ano], "uf": ["TO"], "area_km2": [0.0118]})
    with mock.patch(
        "agrobr.desmatamento.prodes",
        autospec=True,
        return_value=(poligonos, _meta_desmatamento(58784, TETO_DESMATAMENTO)),
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["desmatamento"].fn(
            bioma="cerrado", sistema="prodes"
        )

    fetcher.assert_awaited_once_with(
        bioma="Cerrado",
        ano=ano,
        uf=None,
        max_registros=TETO_DESMATAMENTO,
        tamanho_pagina=TETO_DESMATAMENTO,
        return_meta=True,
    )
    assert f"PRODES {ano}" in response
    assert "2000 de 58784" in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_desmatamento_prodes_sem_feicao_recua_um_ano(
    mcp_server: mcpserver.MCPServer,
) -> None:
    ano = date.today().year - 1
    poligonos = pd.DataFrame({"ano": [ano - 1], "uf": ["RS"], "area_km2": [0.02]})
    with mock.patch(
        "agrobr.desmatamento.prodes",
        autospec=True,
        side_effect=[
            (poligonos.iloc[:0], _meta_desmatamento(0, 0)),
            (poligonos, _meta_desmatamento(1, 1)),
        ],
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["desmatamento"].fn(
            bioma="pampa", sistema="prodes"
        )

    assert [chamada.kwargs["ano"] for chamada in fetcher.await_args_list] == [ano, ano - 1]
    assert f"PRODES {ano - 1}" in response
    assert "Corte" not in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_desmatamento_prodes_ano_e_uf_sem_recuo(mcp_server: mcpserver.MCPServer) -> None:
    with mock.patch(
        "agrobr.desmatamento.prodes",
        autospec=True,
        return_value=(pd.DataFrame(), _meta_desmatamento(0, 0)),
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["desmatamento"].fn(
            bioma="amazonia", sistema="prodes", ano=2020, uf="pa"
        )

    fetcher.assert_awaited_once_with(
        bioma="Amazônia",
        ano=2020,
        uf="PA",
        max_registros=TETO_DESMATAMENTO,
        tamanho_pagina=TETO_DESMATAMENTO,
        return_meta=True,
    )
    assert "PRODES 2020, PA" in response
    assert "Nenhum dado disponível" in response


@pytest.mark.asyncio
async def test_serie_historica_brasil_soma_as_ufs(mcp_server: mcpserver.MCPServer) -> None:
    serie = pd.DataFrame(
        {
            "produto": ["milho"] * 4,
            "safra": ["2023/24", "2023/24", "2024/25", "2024/25"],
            "regiao": ["SUL", "CENTRO-OESTE", "SUL", "CENTRO-OESTE"],
            "uf": ["PR", "MT", "PR", "MT"],
            "area_plantada_mil_ha": [100.25, 200.50, 110.25, 220.50],
            "producao_mil_ton": [500.25, 1000.50, 600.25, 1200.50],
            "produtividade_kg_ha": [4990.0, 4991.0, 5444.0, 5445.0],
        }
    )
    with mock.patch(
        "agrobr.datasets.serie_historica_safra", autospec=True, return_value=serie
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["serie_historica_safra"].fn(
            produto="milho"
        )

    fetcher.assert_awaited_once_with("milho", ano_inicio=date.today().year - 10, uf=None)
    somas = serie.groupby("safra")[["area_plantada_mil_ha", "producao_mil_ton"]].sum()
    for valor in somas.to_numpy().ravel():
        assert f"{valor:.2f}" in response
    assert "4990" not in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_serie_historica_uf_e_ano_inicio(mcp_server: mcpserver.MCPServer) -> None:
    serie = pd.DataFrame(
        {"produto": ["milho"], "safra": ["2015/16"], "uf": ["PR"], "producao_mil_ton": [1.0]}
    )
    with mock.patch(
        "agrobr.datasets.serie_historica_safra", autospec=True, return_value=serie
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["serie_historica_safra"].fn(
            produto="milho", uf=" pr ", ano_inicio=2015
        )

    fetcher.assert_awaited_once_with("milho", ano_inicio=2015, uf="PR")
    assert "2015/16" in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_rebanho_ano_mais_recente_todas_as_ufs(mcp_server: mcpserver.MCPServer) -> None:
    rebanho = pd.DataFrame(
        {
            "ano": [2024] * 27,
            "localidade": [f"Estado {i:02d}" for i in range(27)],
            "especie": ["bovino"] * 27,
            "valor": [float(i * 1000) for i in range(27)],
            "unidade": ["cabeças"] * 27,
        }
    )
    with mock.patch(
        "agrobr.datasets.pecuaria_municipal", autospec=True, return_value=rebanho
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["rebanho"].fn(produto="bovino")

    fetcher.assert_awaited_once_with("bovino", ano=None, nivel="uf")
    assert "2024" in response
    assert "mostrando" not in response
    assert response.index("Estado 26") < response.index("Estado 00")
    assert not response.startswith("Erro")


@pytest.mark.asyncio
@pytest.mark.parametrize("fonte,licenca", [("comexstat", "livre"), ("abiove", "zona_cinza")])
async def test_exportacao_soma_por_mes_e_declara_a_fonte(
    mcp_server: mcpserver.MCPServer, fonte: str, licenca: str
) -> None:
    exportado = pd.DataFrame(
        {
            "ano": [2026] * 4,
            "mes": [1, 1, 2, 2],
            "produto": ["soja"] * 4,
            "uf": ["MT", "PR", "MT", "PR"],
            "kg_liquido": [10250.0, 20500.0, 30250.0, 40500.0],
            "valor_fob_usd": [1000.25, 2000.50, 3000.25, 4000.50],
            "volume_ton": [10.25, 20.50, 30.25, 40.50],
        }
    )
    with mock.patch(
        "agrobr.datasets.exportacao",
        autospec=True,
        return_value=(exportado, SimpleNamespace(selected_source=fonte)),
    ) as fetcher:
        response = await mcp_server._tool_manager._tools["exportacao"].fn(produto="soja")

    fetcher.assert_awaited_once_with("soja", ano=date.today().year, uf=None, return_meta=True)
    por_mes = exportado.groupby("mes")[["volume_ton", "valor_fob_usd"]].sum()
    for valor in por_mes.to_numpy().ravel():
        assert f"{valor:.2f}" in response
    total_ton = exportado["volume_ton"].sum()
    total_usd = exportado["valor_fob_usd"].sum()
    assert f"Total: {total_ton:,.2f} t; US$ {total_usd:,.2f} FOB" in response
    assert f"{fonte} (licença {licenca}" in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_queimadas_conta_por_municipio_e_bioma(mcp_server: mcpserver.MCPServer) -> None:
    focos = pd.DataFrame(
        {
            "municipio": ["M01", "M01"] + [f"M{i:02d}" for i in range(2, 13)],
            "bioma": ["Amazônia"] * 7 + ["Cerrado"] * 5 + [None],
            "uf": ["MT"] * 13,
        }
    )
    with mock.patch("agrobr.datasets.queimadas", autospec=True, return_value=focos) as fetcher:
        response = await mcp_server._tool_manager._tools["queimadas"].fn(uf=" mt ")

    ontem = date.today() - timedelta(days=1)
    fetcher.assert_awaited_once_with(
        ano=ontem.year, mes=ontem.month, dia=ontem.day, uf="MT", satelite="AQUA_M-T"
    )
    assert f"({ontem.isoformat()})" in response
    assert "Total: 13 focos" in response
    assert re.search(r"Amazônia\s+7\b", response)
    assert re.search(r"Cerrado\s+5\b", response)
    assert re.search(r"não informado\s+1\b", response)
    assert re.search(r"M01\s+2\b", response)
    assert "M10" in response
    assert "M11" not in response
    assert "M12" not in response
    assert not response.startswith("Erro")


@pytest.mark.asyncio
async def test_queimadas_uf_invalida_nao_consulta(mcp_server: mcpserver.MCPServer) -> None:
    with mock.patch("agrobr.datasets.queimadas", autospec=True) as fetcher:
        response = await mcp_server._tool_manager._tools["queimadas"].fn(uf="XX")

    fetcher.assert_not_awaited()
    assert "UF 'XX' inválida" in response


NULO = float("nan")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fob,volume,total,linhas",
    [
        (
            [NULO] * 4,
            [10.25, 20.50, 30.25, 40.50],
            "Total: 101.50 t; valor FOB sem dado",
            [
                r"2026\s+1\s+30\.75\s+NaN\s+valor_fob_usd: 2 de 2",
                r"2026\s+2\s+70\.75\s+NaN\s+valor_fob_usd: 2 de 2",
            ],
        ),
        (
            [1000.25, 2000.50, 3000.25, 4000.50],
            [NULO] * 4,
            "Total: volume sem dado; US$ 10,001.50 FOB",
            [
                r"2026\s+1\s+NaN\s+3000\.75\s+volume_ton: 2 de 2",
                r"2026\s+2\s+NaN\s+7000\.75\s+volume_ton: 2 de 2",
            ],
        ),
        (
            [1000.25, NULO, 3000.25, 4000.50],
            [10.25, 20.50, 30.25, 40.50],
            "Total: 101.50 t; US$ 8,001.00 FOB (soma das parcelas publicadas; faltam 1 de 4)",
            [
                r"2026\s+1\s+30\.75\s+1000\.25\s+valor_fob_usd: 1 de 2",
                r"2026\s+2\s+70\.75\s+7000\.75\s*$",
            ],
        ),
    ],
)
async def test_exportacao_ausencia_nao_vira_zero(
    mcp_server: mcpserver.MCPServer,
    fob: list[float],
    volume: list[float],
    total: str,
    linhas: list[str],
) -> None:
    exportado = pd.DataFrame(
        {
            "ano": [2026] * 4,
            "mes": [1, 1, 2, 2],
            "produto": ["soja"] * 4,
            "uf": ["MT", "PR", "MT", "PR"],
            "valor_fob_usd": fob,
            "volume_ton": volume,
        }
    )
    with mock.patch(
        "agrobr.datasets.exportacao",
        autospec=True,
        return_value=(exportado, SimpleNamespace(selected_source="comexstat")),
    ):
        response = await mcp_server._tool_manager._tools["exportacao"].fn(produto="soja")

    assert total in response
    for linha in linhas:
        assert re.search(linha, response, re.M), linha
    assert "0.00 t" not in response
    assert "US$ 0.00" not in response


@pytest.mark.asyncio
async def test_serie_historica_brasil_marca_soma_parcial(mcp_server: mcpserver.MCPServer) -> None:
    serie = pd.DataFrame(
        {
            "safra": ["2023/24", "2023/24", "2024/25", "2024/25"],
            "uf": ["PR", "MT", "PR", "MT"],
            "area_plantada_mil_ha": [100.25, 200.50, 110.25, 220.50],
            "producao_mil_ton": [500.25, NULO, 600.25, 1200.50],
        }
    )
    with mock.patch("agrobr.datasets.serie_historica_safra", autospec=True, return_value=serie):
        response = await mcp_server._tool_manager._tools["serie_historica_safra"].fn(
            produto="milho"
        )

    assert re.search(r"2023/24\s+300\.75\s+500\.25\s+producao_mil_ton: 1 de 2", response)
    assert re.search(r"2024/25\s+330\.75\s+1800\.75\s*$", response, re.M)


@pytest.mark.asyncio
async def test_exportacao_fallback_aponta_a_pagina_de_licencas(
    mcp_server: mcpserver.MCPServer,
) -> None:
    exportado = pd.DataFrame(
        {"ano": [2026], "mes": [1], "uf": [None], "volume_ton": [1.0], "valor_fob_usd": [2.0]}
    )
    with mock.patch(
        "agrobr.datasets.exportacao",
        autospec=True,
        return_value=(exportado, SimpleNamespace(selected_source="abiove")),
    ):
        response = await mcp_server._tool_manager._tools["exportacao"].fn(produto="soja")

    assert "confira o uso em https://www.agrobr.dev/docs/licenses/)" in response
