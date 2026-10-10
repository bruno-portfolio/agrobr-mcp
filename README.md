# agrobr-mcp

[![PyPI](https://img.shields.io/pypi/v/agrobr-mcp)](https://pypi.org/project/agrobr-mcp/)
[![Tests](https://github.com/bruno-portfolio/agrobr-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/bruno-portfolio/agrobr-mcp/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**MCP server that gives LLMs access to real-time Brazilian agricultural data** — prices, crop estimates, climate, deforestation and more from 10 public sources from agrobr.

![Demo](https://github.com/user-attachments/assets/76b6c45d-055e-4b36-aa10-02ae3f917aa8)

---

## Install

Version 0.2.0 requires agrobr >=2.0.0,<3 and MCP Python SDK >=2.0.0,<3.

```bash
pip install agrobr-mcp
```

## Setup

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agrobr": {
      "command": "python",
      "args": ["-m", "agrobr_mcp"]
    }
  }
}
```

### Cursor

Settings > MCP Servers > Add:

```json
{
  "agrobr": {
    "command": "python",
    "args": ["-m", "agrobr_mcp"]
  }
}
```

### Claude Code

```bash
claude mcp add agrobr python -- -m agrobr_mcp
```

> If the above fails due to `-m` flag parsing, create a wrapper script:
>
> **Linux/macOS:** `echo 'python -m agrobr_mcp' > run.sh && chmod +x run.sh && claude mcp add agrobr ./run.sh`
>
> **Windows:** `echo python -m agrobr_mcp > run.bat && claude mcp add agrobr run.bat`

### Docker

```bash
docker build -t agrobr-mcp .
docker run --rm -i agrobr-mcp
```

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agrobr": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "agrobr-mcp"]
    }
  }
}
```

---

## Tools

14 tools available out of the box:

### Prices & Market

| Tool | Description |
|------|-------------|
| `preco_diario` | Daily spot prices for agricultural commodities (CEPEA/ESALQ) |
| `futuros_b3` | Daily settlement prices for agricultural futures on B3 exchange (latest published session by default) |
| `exportacao` | Agricultural exports summed by month, by product and state of origin (Comex Stat; ABIOVE fallback) |

### Production & Crop

| Tool | Description |
|------|-------------|
| `estimativa_safra` | Crop estimate by state, latest season with data by default (CONAB/IBGE) |
| `producao_anual` | Historical annual production by state (IBGE PAM) |
| `balanco` | Supply and demand balance — stock, consumption, exports (CONAB) |
| `progresso_safra` | Weekly planting and harvesting progress by state (CONAB) |
| `serie_historica_safra` | Historical crop series by season — area, production, yield; last 10 years by default (CONAB) |
| `rebanho` | Livestock herds and animal products by state, latest published year by default (IBGE PPM) |

### Climate & Environment

| Tool | Description |
|------|-------------|
| `clima` | Climate data by state — temperature, precipitation, radiation (NASA POWER) |
| `desmatamento` | Deforestation polygons (PRODES for the previous calendar year, falling back one more year when empty) and alerts (DETER, last 15 days) by biome, with optional year and state filters, up to 2,000 records (INPE) |
| `queimadas` | Fire hotspots of one day by municipality and biome, reference satellite (INPE) |

### Meta

| Tool | Description |
|------|-------------|
| `listar_produtos` | List valid products for each tool |
| `health_check` | Check status of all data sources |

---

## Example queries

```
"Qual o preço da soja nos últimos 5 dias?"
"Estimativa de safra de milho por estado"
"Progresso da colheita de soja"
"Dados de desmatamento na Amazônia"
"Quais produtos estão disponíveis?"
```

---

## How it works

```
User (natural language)
    │
MCP Client (Claude Desktop / Cursor / Claude Code)
    │
agrobr-mcp (this server — thin layer, text formatting)
    │
agrobr library (data collection, parsing, caching)
    │
19 public APIs (CEPEA, CONAB, IBGE, INPE, B3, NASA POWER…)
```

agrobr-mcp is a thin wrapper. All data logic lives in the [agrobr](https://github.com/bruno-portfolio/agrobr) library.

---

## Development

```bash
git clone https://github.com/bruno-portfolio/agrobr-mcp.git
cd agrobr-mcp
pip install -e ".[dev]"

# Run tests
pytest tests/ -m "not integration" -v

# Lint
ruff check src/ tests/
ruff format src/ tests/
```

---

## License

MIT

---

## PT-BR

### O que é o agrobr-mcp?

Servidor MCP que dá acesso a dados agrícolas brasileiros em tempo real para LLMs. Preços, safras, clima, desmatamento e mais — tudo de fontes públicas como CEPEA, CONAB, IBGE, INPE e B3.

### Instalação

A versão 0.2.0 requer agrobr >=2.0.0,<3 e MCP Python SDK >=2.0.0,<3.

```bash
pip install agrobr-mcp
```

### Configuração

Adicione ao seu client MCP (Claude Desktop, Cursor ou Claude Code) conforme as instruções acima.

### Docker

```bash
docker build -t agrobr-mcp .
docker run --rm -i agrobr-mcp
```

### 14 tools disponíveis

- **preco_diario** — Preço spot de commodities agrícolas (CEPEA/ESALQ)
- **futuros_b3** — Ajustes diários de futuros agrícolas na B3 (por padrão, o último pregão publicado)
- **exportacao** — Exportações agrícolas somadas por mês, por produto e UF de origem (Comex Stat; ABIOVE como reserva)
- **estimativa_safra** — Estimativa de safra por UF, por padrão a safra mais recente com dado (CONAB/IBGE)
- **producao_anual** — Produção histórica por UF (IBGE PAM)
- **balanco** — Balanço de oferta e demanda (CONAB)
- **progresso_safra** — Progresso semanal de plantio e colheita (CONAB)
- **serie_historica_safra** — Série histórica por safra: área, produção e produtividade; por padrão os últimos 10 anos (CONAB)
- **rebanho** — Rebanhos e produção animal por UF, por padrão o ano mais recente publicado (IBGE PPM)
- **clima** — Dados climáticos por UF (NASA POWER)
- **desmatamento** — Polígonos de desmatamento (PRODES do ano anterior ao corrente, recuando mais um ano se vier vazio) e alertas (DETER, últimos 15 dias) por bioma, com filtros opcionais de ano e UF, até 2.000 registros (INPE)
- **queimadas** — Focos de calor de um dia por município e bioma, satélite de referência (INPE)
- **listar_produtos** — Lista produtos válidos por tool
- **health_check** — Status das fontes de dados

### Links

- [agrobr library](https://github.com/bruno-portfolio/agrobr) — biblioteca de dados agrícolas
- [MCP Protocol](https://modelcontextprotocol.io) — Model Context Protocol

mcp-name: io.github.bruno-portfolio/agrobr
