# agrobr-mcp

[![PyPI](https://img.shields.io/pypi/v/agrobr-mcp)](https://pypi.org/project/agrobr-mcp/)
[![Tests](https://github.com/bruno-portfolio/agrobr-mcp/actions/workflows/tests.yml/badge.svg)](https://github.com/bruno-portfolio/agrobr-mcp/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**MCP server that gives LLMs access to real-time Brazilian agricultural data** — prices, crop estimates, climate, deforestation and more from 10 public sources from agrobr.

![Demo](https://github.com/user-attachments/assets/76b6c45d-055e-4b36-aa10-02ae3f917aa8)

---

## Install

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

## Hosted deployment

A hosted deployment is available on [Fronteir AI](https://fronteir.ai/mcp/bruno-portfolio-agrobr-mcp).

## Tools

10 tools available out of the box:

### Prices & Market

| Tool | Description |
|------|-------------|
| `preco_diario` | Daily spot prices for agricultural commodities (CEPEA/ESALQ) |
| `futuros_b3` | Daily settlement prices for agricultural futures on B3 exchange |

### Production & Crop

| Tool | Description |
|------|-------------|
| `estimativa_safra` | Current crop season estimate by state (CONAB/IBGE) |
| `producao_anual` | Historical annual production by state (IBGE PAM) |
| `balanco` | Supply and demand balance — stock, consumption, exports (CONAB) |
| `progresso_safra` | Weekly planting and harvesting progress by state (CONAB) |

### Climate & Environment

| Tool | Description |
|------|-------------|
| `clima` | Climate data by state — temperature, precipitation, radiation (NASA POWER) |
| `desmatamento` | Deforestation rates and real-time alerts by biome (INPE) |

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

### 10 tools disponíveis

- **preco_diario** — Preço spot de commodities agrícolas (CEPEA/ESALQ)
- **futuros_b3** — Ajustes diários de futuros agrícolas na B3
- **estimativa_safra** — Estimativa da safra corrente por UF (CONAB/IBGE)
- **producao_anual** — Produção histórica por UF (IBGE PAM)
- **balanco** — Balanço de oferta e demanda (CONAB)
- **progresso_safra** — Progresso semanal de plantio e colheita (CONAB)
- **clima** — Dados climáticos por UF (NASA POWER)
- **desmatamento** — Taxa de desmatamento e alertas por bioma (INPE)
- **listar_produtos** — Lista produtos válidos por tool
- **health_check** — Status das fontes de dados

### Links

- [agrobr library](https://github.com/bruno-portfolio/agrobr) — biblioteca de dados agrícolas
- [MCP Protocol](https://modelcontextprotocol.io) — Model Context Protocol

mcp-name: io.github.bruno-portfolio/agrobr
