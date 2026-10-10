# Changelog

## [0.2.0] - 2026-10-10

### Added

- `desmatamento` accepts optional `ano` (PRODES mapping year, used as given without falling back;
  DETER calendar year) and `uf` filters.
- `serie_historica_safra`: CONAB historical series by season, last 10 years by default; without `uf`,
  area and production summed over the states.
- `rebanho`: IBGE PPM herds and animal products by state, latest published year by default.
- `exportacao`: exports summed by month (and state, with `uf`), current year by default; states the
  source used and its license class (Comex Stat, or the ABIOVE fallback, `zona_cinza`).
- In the `exportacao` and `serie_historica_safra` sums, missing values do not become zero: a measure
  with no published value is shown as missing ("sem dado" in the total), and a sum with missing parts
  is flagged with how many are missing (`faltam N de M`).
- `queimadas`: one day of INPE fire hotspots (yesterday by default) counted by biome and top 10
  municipalities, from the reference satellite AQUA_M-T.

### Changed

- Require agrobr >=2.0.0,<3 and MCP Python SDK >=2.0.0,<3; use MCPServer.
- Products in tool descriptions, `listar_produtos` and error messages come from agrobr's
  `datasets.list_products()`, with agrobr's names (e.g. `boi`, `cana`, `milho_1`). Products agrobr does
  not serve are no longer listed, such as `arroz`, `leite` and `suino` in `preco_diario`, `cafe` in
  `estimativa_safra` and `balanco`, and `sorgo` in `producao_anual`.
- `futuros_b3` without a date returns the latest published B3 session instead of today's.
- `estimativa_safra` without a season returns the latest season with data instead of the calendar's
  current season.
- `desmatamento` reads PRODES for the previous calendar year, falling back one more year when empty,
  and DETER for the last 15 days, at most 2,000 records, and states in the response when the
  selection was cut.

### Fixed

- Forward crop progress filters using agrobr 2.0's `produto` and `uf` parameters.
- `futuros_b3` with `boi_gordo` returns the live cattle contract (BGI); agrobr 2.0 rejected the name
  and agrobr 1.1 returned it empty.
- Project links on PyPI (homepage, repository, issues) point to github.com/bruno-portfolio/agrobr-mcp.
- Dependencies have upper bounds: 0.1.2 had none on agrobr or the MCP Python SDK, so a fresh install
  could pull agrobr 2 or SDK 2 and fail to start.
