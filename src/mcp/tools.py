import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient


async def load_mcp_tools():
    client = MultiServerMCPClient(
        {
            "news": {
                "transport": "stdio",
                "command": "python",
                "args": ["-m", "src.mcp.server"],
            }
        }
    )

    tools = await client.get_tools()
    return tools


def get_mcp_tools():
    return asyncio.run(load_mcp_tools())