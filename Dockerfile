FROM python:3.11-slim

LABEL maintainer="Bruno Escalhão"
LABEL description="MCP server for Brazilian agricultural data"
LABEL org.opencontainers.image.source="https://github.com/bruno-portfolio/agrobr-mcp"

WORKDIR /app

RUN pip install --no-cache-dir agrobr-mcp

ENTRYPOINT ["python", "-m", "agrobr_mcp"]
