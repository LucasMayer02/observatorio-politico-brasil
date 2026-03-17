import json
from pathlib import Path
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP

from src.config import PROCESSED_DATA_DIR


mcp = FastMCP("mcp-news")


def load_processed_docs() -> List[Dict[str, Any]]:
    processed_dir = Path(PROCESSED_DATA_DIR)

    docs = []
    for file_path in processed_dir.glob("*.json"):
        if file_path.name == "chunks.json":
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, dict):
                docs.append(data)

    return docs


@mcp.tool()
def list_articles(topic: str = "politica") -> List[Dict[str, Any]]:
    docs = load_processed_docs()

    results = []
    for doc in docs:
        if doc.get("topic", "").lower() == topic.lower():
            results.append(
                {
                    "doc_id": doc.get("doc_id", ""),
                    "title": doc.get("title", ""),
                    "source": doc.get("source", ""),
                    "published_at": doc.get("published_at", ""),
                    "url": doc.get("url", ""),
                }
            )

    return results


@mcp.tool()
def get_article(doc_id: str) -> Dict[str, Any]:
    docs = load_processed_docs()

    for doc in docs:
        if doc.get("doc_id") == doc_id:
            return doc

    return {"error": f"Artigo não encontrado para doc_id={doc_id}"}


@mcp.tool()
def build_timeline(keyword: str) -> List[Dict[str, Any]]:
    docs = load_processed_docs()

    results = []
    keyword_lower = keyword.lower()

    for doc in docs:
        title = doc.get("title", "").lower()
        content = doc.get("content_clean", "").lower()

        if keyword_lower in title or keyword_lower in content:
            results.append(
                {
                    "doc_id": doc.get("doc_id", ""),
                    "title": doc.get("title", ""),
                    "published_at": doc.get("published_at", ""),
                    "source": doc.get("source", ""),
                    "url": doc.get("url", ""),
                }
            )

    results.sort(key=lambda x: x.get("published_at", ""))
    return results


if __name__ == "__main__":
    print("MCP server iniciado...")
    mcp.run()