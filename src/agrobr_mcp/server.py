from mcp.server.fastmcp import FastMCP

from agrobr_mcp.tools import clima, meta, precos, safra

mcp = FastMCP(
    "agrobr",
    instructions="Real-time Brazilian agricultural data: prices, crop estimates, "
    "climate, deforestation and more. 19 public sources unified via agrobr.",
)

precos.register(mcp)
safra.register(mcp)
clima.register(mcp)
meta.register(mcp)


def run() -> None:
    mcp.run()
